"""Effects: the concrete changes an artifact makes. Each can report, apply and restore its state."""

import hashlib
import os
import pwd
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from rigsmith.model import Artifact, Backend, Platform, config_home, invalidate_caches, run, sh_path

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

    def sh(self) -> list[str]:
        """This effect as shell commands, guarded so running them twice is harmless (for `--script`)."""
        return [f"# {self.label}: no shell equivalent"]

    def undo_sh(self, backup: Any) -> list[str]:
        return [f"# undo {self.label}: no shell equivalent"]


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

    def guard(self) -> str:
        if self.art.check:
            return f"{{ {self.art.check}; }} >/dev/null 2>&1"
        if self.art.bin:
            return f"command -v {self.art.bin} >/dev/null 2>&1"
        return f"{self.src.check_sh()} >/dev/null 2>&1"

    def sh(self) -> list[str]:
        return [f"if ! {self.guard()}; then", *(f"  {c}" for c in self.src.install_sh()), "fi"]

    def undo_sh(self, backup: Any) -> list[str]:
        return self.src.uninstall_sh(backup)


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

    def sh(self) -> list[str]:
        dest = sh_path(self.dest)
        try:
            text = self.content.decode()
        except UnicodeDecodeError:
            return [f"# {self.label}: binary file, run `rigsmith install` to write it"]
        ours = self.dest.is_relative_to(config_home())  # rigsmith's own files never need a backup
        bak = sh_path(f"{self.dest}.bak.") + "$(date +%Y%m%d%H%M%S)"
        keep = "" if ours else f"[ ! -f {dest} ] || cp -p {dest} {bak}; "
        return [
            "tmp=$(mktemp)",
            "cat > \"$tmp\" <<'RIGSMITH_EOF'",
            *text.rstrip("\n").split("\n"),
            "RIGSMITH_EOF",
            f'if cmp -s "$tmp" {dest}; then rm -f "$tmp"; else mkdir -p {sh_path(self.dest.parent)}; '
            f'{keep}mv "$tmp" {dest}; fi',
        ]

    def undo_sh(self, backup: Any) -> list[str]:
        if backup:
            return [f"mv {sh_path(backup)} {sh_path(self.dest)}"]
        return [f"rm -f {sh_path(self.dest)}"]


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

    def sh(self) -> list[str]:
        return ['[ "$(basename "$SHELL")" = zsh ] || sudo chsh -s "$(command -v zsh)" "$(id -un)"']

    def undo_sh(self, backup: Any) -> list[str]:
        return [f'sudo chsh -s {sh_path(backup or "/bin/bash")} "$(id -un)"']


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

    def sh(self) -> list[str]:
        if self.art.post_install_sh:
            return [f"{self.art.post_install_sh}  # one-time, can't be undone"]
        return [f"# {self.label}: a Python step, run `rigsmith install {self.art.id}`"]

    def undo_sh(self, backup: Any) -> list[str]:
        return [f"# {self.label} can't be undone"]


def _tilde(p: Path) -> str:
    home = str(Path.home())
    return "~" + str(p)[len(home) :] if str(p).startswith(home) else str(p)
