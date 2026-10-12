"""Core model: platform, backends, artifacts, questions and their registries."""

import functools
import os
import platform as _platform
import re
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, TextIO

# ── Platform ─────────────────────────────────────────────────────────────────

SUPPORTED = ("macos>=14", "ubuntu==22.04", "ubuntu==24.04", "debian==12")


def _version(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v))


def _os_release() -> dict[str, str]:
    try:
        text = Path("/etc/os-release").read_text()
    except OSError:
        return {}
    return {k: v.strip('"') for k, _, v in (line.partition("=") for line in text.splitlines()) if k}


@dataclass(frozen=True)
class Platform:
    os: str  # darwin | linux
    distro: str  # macos | ubuntu | debian | …
    version: str
    arch: str  # arm64 | x86_64

    @classmethod
    def detect(cls) -> Platform:
        machine = _platform.machine().lower()
        arch = {"aarch64": "arm64", "amd64": "x86_64"}.get(machine, machine)
        if sys.platform == "darwin":
            return cls("darwin", "macos", _platform.mac_ver()[0], arch)
        info = _os_release()
        return cls("linux", info.get("ID", "unknown"), info.get("VERSION_ID", ""), arch)

    def matches(self, spec: str) -> bool:
        """`spec` is a distro constraint: `macos`, `ubuntu>=24.04`, `debian==12`."""
        m = re.fullmatch(r"([a-z]+)\s*(>=|<=|==|>|<)?\s*([\d.]*)", spec.strip())
        if not m:
            raise ValueError(f"bad platform constraint {spec!r}")
        name, op, ver = m.groups()
        if name != self.distro:
            return False
        if not op:
            return True
        a, b = _version(self.version), _version(ver)
        return {">=": a >= b, "<=": a <= b, "==": a == b, ">": a > b, "<": a < b}[op]

    @property
    def supported(self) -> bool:
        return any(self.matches(s) for s in SUPPORTED)

    def __str__(self) -> str:
        return f"{self.distro} {self.version} ({self.arch})"


# ── Running commands ─────────────────────────────────────────────────────────

LOG: TextIO | None = None  # set by the runner; every command's output is appended here


def run(
    cmd: str | list[str],
    *,
    check: bool = True,
    sudo: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a command (a string runs through bash), capture output, append it to LOG."""
    argv = ["bash", "-o", "pipefail", "-c", cmd] if isinstance(cmd, str) else list(cmd)
    if sudo and os.geteuid() != 0:
        argv = ["sudo", *(["env", *(f"{k}={v}" for k, v in env.items())] if env else []), *argv]
    full_env = {**os.environ, **(env or {})}
    proc = subprocess.run(argv, capture_output=True, text=True, env=full_env, stdin=subprocess.DEVNULL)
    if LOG:
        LOG.write(f"$ {' '.join(argv)}\n{proc.stdout}{proc.stderr}[exit {proc.returncode}]\n")
        LOG.flush()
    if check and proc.returncode != 0:
        tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-5:])
        raise RuntimeError(f"`{' '.join(argv[-1:] if isinstance(cmd, str) else argv)}` failed: {tail}")
    return proc


def out(cmd: str | list[str]) -> str:
    """stdout of a command, or "" if it fails or doesn't exist."""
    try:
        return run(cmd, check=False).stdout
    except OSError:
        return ""


# ── Backends ─────────────────────────────────────────────────────────────────

BACKENDS: dict[str, type[Backend]] = {}


def backend(name: str):
    def register(cls: type[Backend]) -> type[Backend]:
        cls.name = name
        BACKENDS[name] = cls
        return cls

    return register


@dataclass
class Backend:
    """How a package gets installed. One subclass per package manager."""

    pkg: str
    os: str | None = field(default=None, kw_only=True)
    arch: str | None = field(default=None, kw_only=True)
    distro: str | None = field(default=None, kw_only=True)

    name: ClassVar[str] = ""
    bootstrap: ClassVar[str | None] = None  # artifact id this backend needs installed first

    @property
    def sudo(self) -> bool:
        return False

    @property
    def reversible(self) -> bool:
        return True

    def matches(self, p: Platform) -> bool:
        return self.os in (None, p.os) and self.arch in (None, p.arch) and (not self.distro or p.matches(self.distro))

    def is_installed(self) -> bool:
        raise NotImplementedError

    def install(self) -> None:
        raise NotImplementedError

    def snapshot(self) -> Any:
        """Pre-install state needed for a precise uninstall (e.g. which of several packages existed)."""
        return None

    def uninstall(self, snapshot: Any = None) -> None:
        raise NotImplementedError

    # The same steps as shell commands, for `--script` (shown to humans; rigsmith itself runs the methods above).
    def check_sh(self) -> str:
        return "false"

    def install_sh(self) -> list[str]:
        return [f"# {self}: no shell equivalent, run `rigsmith install`"]

    def uninstall_sh(self, snapshot: Any = None) -> list[str]:
        return [f"# {self}: no shell equivalent, run `rigsmith uninstall`"]

    def __str__(self) -> str:
        return f"{self.name}:{self.pkg}"


def invalidate_caches() -> None:
    """Forget cached package listings (call after installing/uninstalling)."""
    for fn in _CACHED:
        fn.cache_clear()


_CACHED: list[Any] = []


def cached(fn):
    fn = functools.cache(fn)
    _CACHED.append(fn)
    return fn


# ── Artifacts ────────────────────────────────────────────────────────────────

ARTIFACTS: dict[str, Artifact] = {}


@dataclass
class Snippet:
    """A zsh file owned by an artifact, written to shell.d/<phase>-<artifact>.zsh."""

    name: str  # file under library/snippets/
    phase: int


@dataclass
class File:
    """A whole file owned by an artifact."""

    src: str  # file under library/files/
    dest: str  # target path, `~` allowed
    os: str | None = None


@dataclass
class VSCodeSetting:
    key: str
    value: Any


@dataclass
class GitConfig:
    key: str
    value: str
    file: str | None = None  # another git config file (e.g. ~/.gitconfig-work); default: global


type Setting = VSCodeSetting | GitConfig


@dataclass(eq=False)
class Artifact:
    """One installable unit: a package plus the integration config the tool needs."""

    id: str
    help: str
    sources: list[Backend] = field(default_factory=list)
    bin: str | None = None  # presence check: binary on PATH
    check: str | None = None  # presence check: shell command, exit 0 = present
    shell: list[Snippet] | Snippet = field(default_factory=list)
    files: list[File] = field(default_factory=list)
    settings: list[Setting] = field(default_factory=list)
    role: str | None = None
    tags: list[str] = field(default_factory=list)
    prefs: list[str] = field(default_factory=list)  # question ids whose env the snippets read
    requires: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)  # regexes for ~/.zshrc lines that double-load
    register: bool = field(default=True, repr=False)

    def __post_init__(self) -> None:
        if isinstance(self.shell, Snippet):
            self.shell = [self.shell]
        if self.register:
            if self.id in ARTIFACTS:
                raise ValueError(f"duplicate artifact id {self.id!r}")
            ARTIFACTS[self.id] = self

    @property
    def snippets(self) -> list[Snippet]:
        return self.shell if isinstance(self.shell, list) else [self.shell]

    def source(self, p: Platform) -> Backend | None:
        """The one backend used on this platform: first whose constraints match."""
        return next((s for s in self.sources if s.matches(p)), None)

    def available(self, p: Platform) -> bool:
        if self.sources:
            return self.source(p) is not None
        return bool(self.snippets or self.settings or any(f.os in (None, p.os) for f in self.files))

    def present(self, p: Platform) -> bool:
        """Is the package on the system, regardless of which manager installed it?"""
        if self.check:
            return run(self.check, check=False).returncode == 0
        if self.bin:
            return shutil.which(self.bin) is not None
        src = self.source(p)
        return bool(src and src.is_installed())

    post_install_sh: ClassVar[str] = ""  # the post_install step as shell, for `--script`

    def post_install(self) -> None:
        """Override for one-off irreversible setup (e.g. importing history)."""

    def extra_effects(self, p: Platform) -> list[Any]:
        """Override to add effects beyond package, snippets, files and settings (e.g. chsh)."""
        return []

    @property
    def has_post_install(self) -> bool:
        return type(self).post_install is not Artifact.post_install

    def requirements(self, p: Platform) -> list[str]:
        """`requires` plus the bootstrap artifact of the chosen backend."""
        src = self.source(p)
        boot = [src.bootstrap] if src and src.bootstrap and src.bootstrap != self.id else []
        return [*self.requires, *(b for b in boot if b not in self.requires)]


# ── Questions ────────────────────────────────────────────────────────────────

QUESTIONS: dict[str, Question] = {}


@dataclass
class Question:
    """A questionnaire entry. Asked only if an artifact in the menu references it."""

    id: str
    text: str
    choices: dict[str, dict[str, Any]] = field(default_factory=dict)  # answer -> {"env": …, "exclude_tags": …}
    default: str = ""
    help: str = ""
    kind: str = "choice"  # choice | text (free text, e.g. a folder or an email)
    normalize: Callable[[str], str] | None = None  # text answers: clean up what the user typed

    def __post_init__(self) -> None:
        if self.kind == "choice" and self.default not in self.choices:
            raise ValueError(f"question {self.id}: default {self.default!r} is not a choice")
        if self.id in QUESTIONS:
            raise ValueError(f"duplicate question id {self.id!r}")
        QUESTIONS[self.id] = self

    @property
    def tags(self) -> set[str]:
        return {t for c in self.choices.values() for t in c.get("exclude_tags", [])}

    def referenced_by(self, art: Artifact) -> bool:
        return self.id in art.prefs or bool(self.tags & set(art.tags))

    def excluded_tags(self, answer: str) -> set[str]:
        return set(self.choices.get(answer, {}).get("exclude_tags", []))

    def env(self, answer: str) -> dict[str, str]:
        return dict(self.choices.get(answer, {}).get("env", {}))

    def clean(self, answer: str) -> str:
        answer = answer.strip()
        return self.normalize(answer) if self.normalize and answer else answer


def render(text: str, answers: dict[str, str]) -> str:
    """Fill `{{question-id}}` placeholders with answers (unknown ones are left as they are)."""
    return re.sub(r"\{\{([\w-]+)\}\}", lambda m: answers.get(m[1], m[0]), text)


# ── Paths ────────────────────────────────────────────────────────────────────


def sh_path(path: str | Path) -> str:
    """A path for a shell script: `$HOME/...` instead of the absolute home, quoted."""
    text = str(Path(str(path)).expanduser())
    home = str(Path.home())
    if text == home or text.startswith(home + "/"):
        return '"$HOME' + text[len(home) :].replace('"', '\\"') + '"'
    return shlex.quote(text)


def config_home() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "rigsmith"


def state_home() -> Path:
    return Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state") / "rigsmith"


EXTRA_PATH = (
    "/opt/homebrew/bin",
    "/usr/local/bin",
    "/home/linuxbrew/.linuxbrew/bin",
    "~/.local/bin",
    "~/.cargo/bin",
    "~/.krew/bin",
    "~/.local/share/google-cloud-sdk/bin",
)


def ensure_path() -> None:
    """Make tools installed during this run visible to later steps and checks."""
    parts = os.environ.get("PATH", "").split(os.pathsep)
    extra = [str(Path(p).expanduser()) for p in EXTRA_PATH]
    os.environ["PATH"] = os.pathsep.join([*(p for p in extra if p not in parts), *parts])
