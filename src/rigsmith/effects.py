"""Effects: the concrete changes an artifact makes. Each can report, apply and restore its state."""

import hashlib
import os
import pwd
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from rigsmith.model import Artifact, Backend, Platform, config_home, invalidate_caches, run

LIBRARY = Path(__file__).parent / "library"


def shell_d() -> Path:
    return config_home() / "shell.d"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


class Effect:
    key: str
    artifact: str
    label: str
    reversible = True
    inspectable = True  # False: current state can't be observed, so a receipt means "done"
    sudo = False

    def current(self) -> str | None:
        raise NotImplementedError

    def desired(self) -> str:
        raise NotImplementedError

    def backup(self) -> Any:
        return None

    def apply(self) -> None:
        raise NotImplementedError

    def restore(self, backup: Any) -> None:
        raise NotImplementedError


class PackageEffect(Effect):
    def __init__(self, art: Artifact, src: Backend, p: Platform) -> None:
        self.art, self.src, self.p = art, src, p
        self.key, self.artifact, self.label = f"pkg:{art.id}", art.id, f"install {src}"
        self.reversible, self.sudo = src.reversible, src.sudo

    def current(self) -> str | None:
        return "present" if self.art.present(self.p) else None

    def desired(self) -> str:
        return "present"

    def backup(self) -> Any:
        return self.src.snapshot()

    def apply(self) -> None:
        self.src.install()
        invalidate_caches()
        if not self.art.present(self.p):
            raise RuntimeError(f"{self.src} installed but {self.art.id} is still not detected")

    def restore(self, backup: Any) -> None:
        self.src.uninstall(backup)
        invalidate_caches()


class FileEffect(Effect):
    """A whole file. Foreign files are backed up before being replaced."""

    def __init__(self, artifact: str, dest: Path, content: bytes) -> None:
        self.artifact, self.dest, self.content = artifact, dest, content
        self.key = f"file:{dest}"
        self.label = f"snippet {dest.stem}" if dest.parent == shell_d() else f"write {_tilde(dest)}"

    def current(self) -> str | None:
        return sha(self.dest.read_bytes()) if self.dest.is_file() else None

    def desired(self) -> str:
        return sha(self.content)

    def backup(self) -> Any:
        if not self.dest.exists():
            return None
        bak = self.dest.with_name(f"{self.dest.name}.bak.{datetime.now():%Y%m%d_%H%M%S}")
        shutil.copy2(self.dest, bak)
        return str(bak)

    def apply(self) -> None:
        self.dest.parent.mkdir(parents=True, exist_ok=True)
        self.dest.write_bytes(self.content)

    def restore(self, backup: Any) -> None:
        if backup and Path(backup).exists():
            os.replace(backup, self.dest)
        else:
            self.dest.unlink(missing_ok=True)


def snippet_effects(art: Artifact) -> list[Effect]:
    return [
        FileEffect(art.id, shell_d() / f"{s.phase:02d}-{art.id}.zsh", (LIBRARY / "snippets" / s.name).read_bytes())
        for s in art.snippets
    ]


class LoginShellEffect(Effect):
    """chsh to zsh (Linux). Restores the previous login shell on undo."""

    sudo = True

    def __init__(self, artifact: str) -> None:
        self.artifact, self.key, self.label = artifact, "login-shell", "set login shell to zsh"
        self.user = pwd.getpwuid(os.getuid()).pw_name

    def current(self) -> str | None:
        return pwd.getpwnam(self.user).pw_shell

    def desired(self) -> str:
        return shutil.which("zsh") or "/usr/bin/zsh"

    def backup(self) -> Any:
        return self.current()

    def apply(self) -> None:
        run(["chsh", "-s", self.desired(), self.user], sudo=True)

    def restore(self, backup: Any) -> None:
        run(["chsh", "-s", backup or "/bin/bash", self.user], sudo=True)


class PostInstallEffect(Effect):
    reversible = False
    inspectable = False

    def __init__(self, art: Artifact) -> None:
        self.art, self.artifact, self.key = art, art.id, f"post:{art.id}"
        self.label = f"one-time setup for {art.id}"

    def current(self) -> str | None:
        return None

    def desired(self) -> str:
        return "done"

    def apply(self) -> None:
        self.art.post_install()


def _tilde(p: Path) -> str:
    home = str(Path.home())
    return "~" + str(p)[len(home) :] if str(p).startswith(home) else str(p)
