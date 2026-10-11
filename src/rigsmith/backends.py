"""Package-manager backends. Each answers is_installed / install / uninstall for one package."""

import io
import os
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rigsmith.model import Backend, backend, cached, out, run

BREW_PATHS = ("/opt/homebrew/bin/brew", "/usr/local/bin/brew", "/home/linuxbrew/.linuxbrew/bin/brew")


def brew_bin() -> str | None:
    return shutil.which("brew") or next((b for b in BREW_PATHS if os.access(b, os.X_OK)), None)


@cached
def _brew_list(kind: str) -> frozenset[str]:
    brew = brew_bin()
    return frozenset(out([brew, "list", f"--{kind}", "-1"]).split()) if brew else frozenset()


@backend("brew")
class Brew(Backend):
    bootstrap = "homebrew"

    @property
    def short(self) -> str:  # "hashicorp/tap/terraform" is listed as "terraform"
        return self.pkg.rsplit("/", 1)[-1]

    def is_installed(self) -> bool:
        return self.short in _brew_list("formula")

    def install(self) -> None:
        run([_need_brew(), "install", self.pkg], env={"HOMEBREW_NO_ENV_HINTS": "1"})

    def uninstall(self, snapshot: Any = None) -> None:
        run([_need_brew(), "uninstall", self.pkg])


@backend("cask")
class Cask(Brew):
    def is_installed(self) -> bool:
        return self.short in _brew_list("cask")

    def install(self) -> None:
        run([_need_brew(), "install", "--cask", self.pkg], env={"HOMEBREW_NO_ENV_HINTS": "1"})

    def uninstall(self, snapshot: Any = None) -> None:
        run([_need_brew(), "uninstall", "--cask", self.pkg])


def _need_brew() -> str:
    brew = brew_bin()
    if not brew:
        raise RuntimeError("Homebrew is not installed")
    return brew


@cached
def _dpkg() -> frozenset[str]:
    lines = out(["dpkg-query", "-W", "-f=${Package} ${Status}\n"]).splitlines()
    return frozenset(line.split()[0] for line in lines if line.endswith(" install ok installed"))


_apt_updated = False


@backend("apt")
class Apt(Backend):
    @property
    def sudo(self) -> bool:
        return True

    def is_installed(self) -> bool:  # `pkg` may list several space-separated packages
        return all(p in _dpkg() for p in self.pkg.split())

    def install(self) -> None:
        global _apt_updated
        env = {"DEBIAN_FRONTEND": "noninteractive"}
        if not _apt_updated:
            run(["apt-get", "update", "-q"], sudo=True, env=env)
            _apt_updated = True
        run(["apt-get", "install", "-y", "-q", *self.pkg.split()], sudo=True, env=env)

    def snapshot(self) -> Any:
        return [p for p in self.pkg.split() if p in _dpkg()]

    def uninstall(self, snapshot: Any = None) -> None:
        mine = [p for p in self.pkg.split() if p not in (snapshot or [])]
        if mine:
            env = {"DEBIAN_FRONTEND": "noninteractive"}
            run(["apt-get", "remove", "-y", "-q", *mine], sudo=True, env=env)


@backend("script")
@dataclass
class Script(Backend):
    """Arbitrary shell. `pkg` is a label; without `remove` the effect is irreversible."""

    install_cmd: str = field(default="", kw_only=True)
    check_cmd: str = field(default="", kw_only=True)
    remove_cmd: str | None = field(default=None, kw_only=True)
    needs_sudo: bool = field(default=False, kw_only=True)

    @property
    def reversible(self) -> bool:
        return self.remove_cmd is not None

    @property
    def sudo(self) -> bool:
        return self.needs_sudo

    def is_installed(self) -> bool:
        return run(self.check_cmd, check=False).returncode == 0

    def install(self) -> None:
        run(self.install_cmd)

    def uninstall(self, snapshot: Any = None) -> None:
        if self.remove_cmd is None:
            raise RuntimeError(f"{self.pkg} has no uninstall command")
        run(self.remove_cmd)


@backend("git")
@dataclass
class GitClone(Backend):
    """`pkg` is the repo URL; cloned into `dest`."""

    dest: str = field(default="", kw_only=True)

    @property
    def path(self) -> Path:
        return Path(self.dest).expanduser()

    def is_installed(self) -> bool:
        return (self.path / ".git").is_dir()

    def install(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth=1", self.pkg, str(self.path)])

    def uninstall(self, snapshot: Any = None) -> None:
        shutil.rmtree(self.path)


@cached
def _krew_list() -> frozenset[str]:
    return frozenset(out(["kubectl", "krew", "list"]).split())


@backend("krew")
class Krew(Backend):
    """kubectl plugin from the krew index."""

    bootstrap = "krew"

    def is_installed(self) -> bool:
        return self.pkg in _krew_list()

    def install(self) -> None:
        run(["kubectl", "krew", "install", self.pkg])

    def uninstall(self, snapshot: Any = None) -> None:
        run(["kubectl", "krew", "uninstall", self.pkg])


CODE_PATHS = (
    "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
    "/usr/bin/code",
    "/usr/share/code/bin/code",
)


def code_bin() -> str | None:
    return shutil.which("code") or next((c for c in CODE_PATHS if os.access(c, os.X_OK)), None)


@cached
def _code_extensions() -> frozenset[str]:
    code = code_bin()
    return frozenset(out([code, "--list-extensions"]).lower().split()) if code else frozenset()


@backend("vscode")
class VSCodeExt(Backend):
    """VS Code extension by marketplace id (publisher.name)."""

    bootstrap = "vscode"

    def _code(self) -> str:
        if not (code := code_bin()):
            raise RuntimeError("VS Code's `code` command is not installed")
        return code

    def is_installed(self) -> bool:
        return self.pkg.lower() in _code_extensions()

    def install(self) -> None:
        run([self._code(), "--install-extension", self.pkg, "--force"])

    def uninstall(self, snapshot: Any = None) -> None:
        run([self._code(), "--uninstall-extension", self.pkg])


@cached
def _uv_tools() -> frozenset[str]:
    lines = out(["uv", "tool", "list"]).splitlines()
    return frozenset(line.split()[0] for line in lines if line and not line.startswith(("-", " ")))


@backend("uvtool")
class UvTool(Backend):
    """Python CLI installed in its own environment with `uv tool install`. `pkg` may carry extras."""

    bootstrap = "uv"

    @property
    def name_only(self) -> str:
        return self.pkg.split("[")[0]

    def is_installed(self) -> bool:
        return self.name_only in _uv_tools()

    def install(self) -> None:
        run(["uv", "tool", "install", self.pkg])

    def uninstall(self, snapshot: Any = None) -> None:
        run(["uv", "tool", "uninstall", self.name_only])


@backend("nerdfont")
class NerdFont(Backend):
    """A Nerd Font family from the nerd-fonts GitHub releases into ~/.local/share/fonts (Linux)."""

    @property
    def path(self) -> Path:
        return Path.home() / ".local/share/fonts/NerdFonts" / self.pkg

    def is_installed(self) -> bool:
        return self.path.is_dir() and any(self.path.iterdir())

    def install(self) -> None:
        url = f"https://github.com/ryanoasis/nerd-fonts/releases/latest/download/{self.pkg}.zip"
        with urllib.request.urlopen(url, timeout=120) as resp:
            data = resp.read()
        self.path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for name in z.namelist():
                if name.lower().endswith((".ttf", ".otf")):
                    (self.path / Path(name).name).write_bytes(z.read(name))
        run("fc-cache -f >/dev/null 2>&1 || true")

    def uninstall(self, snapshot: Any = None) -> None:
        shutil.rmtree(self.path, ignore_errors=True)
        run("fc-cache -f >/dev/null 2>&1 || true")
