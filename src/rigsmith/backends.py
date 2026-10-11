"""Package-manager backends. Each answers is_installed / install / uninstall for one package."""

import os
import shutil
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
