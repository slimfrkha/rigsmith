"""Settings effects: keys in shared files (VS Code settings.json, global git config)."""

import json
import re
import shlex
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from rigsmith.effects import Effect
from rigsmith.model import Artifact, GitConfig, Platform, VSCodeSetting, render, run, sh_path


def vscode_settings_path(p: Platform) -> Path:
    if p.os == "darwin":
        return Path.home() / "Library/Application Support/Code/User/settings.json"
    return Path.home() / ".config/Code/User/settings.json"


def loads_jsonc(text: str) -> dict[str, Any]:
    """JSON with comments and trailing commas (VS Code's format)."""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(text[i : i + 2] if c == "\\" else c)
            i += 2 if c == "\\" else 1
            in_str = c != '"'
            continue
        if text.startswith("//", i):
            end = text.find("\n", i)
            i = n if end < 0 else end
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
        else:
            in_str = c == '"'
            out.append(c)
            i += 1
    # ponytail: trailing-comma regex runs on comment-free text; a literal ",}" inside a string would break it
    cleaned = re.sub(r",(\s*[}\]])", r"\1", "".join(out))
    return json.loads(cleaned) if cleaned.strip() else {}


_backed_up: set[Path] = set()


class VSCodeSettingEffect(Effect):
    def __init__(self, artifact: str, path: Path, key: str, value: Any) -> None:
        self.artifact, self.path, self.skey, self.value = artifact, path, key, value
        self.key, self.label = f"vscode:{key}", f"set VS Code {key}"

    def _load(self) -> dict[str, Any]:
        return loads_jsonc(self.path.read_text()) if self.path.is_file() else {}

    def current(self) -> str | None:
        data = self._load()
        return json.dumps(data[self.skey], sort_keys=True) if self.skey in data else None

    def desired(self) -> str:
        return json.dumps(self.value, sort_keys=True)

    def backup(self) -> Any:
        data = self._load()
        return {"value": data[self.skey]} if self.skey in data else None

    def _write(self, data: dict[str, Any]) -> None:
        if self.path.is_file() and self.path not in _backed_up:  # comments are lost on rewrite
            shutil.copy2(self.path, self.path.with_name(f"settings.json.bak.{datetime.now():%Y%m%d_%H%M%S}"))
            _backed_up.add(self.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")

    def apply(self) -> None:
        self._write({**self._load(), self.skey: self.value})

    def restore(self, backup: Any) -> None:
        data = self._load()
        if backup is None:
            data.pop(self.skey, None)
        else:
            data[self.skey] = backup["value"]
        self._write(data)

    def sh(self) -> list[str]:  # JSON with comments can't be edited safely in sh: say what to set instead
        return [f'# VS Code {sh_path(self.path)}: set "{self.skey}": {json.dumps(self.value, ensure_ascii=False)}']

    def undo_sh(self, backup: Any) -> list[str]:
        if backup is None:
            return [f'# VS Code {sh_path(self.path)}: remove "{self.skey}"']
        return [f'# VS Code {sh_path(self.path)}: set "{self.skey}" back to {json.dumps(backup["value"])}']


class GitConfigEffect(Effect):
    """One key in the global git config, or in another git config file (`file`)."""

    def __init__(self, artifact: str, key: str, value: str, file: str | None = None) -> None:
        self.artifact, self.gkey, self.value, self.file = artifact, key, value, file
        self.key = f"git:{file}:{key}" if file else f"git:{key}"
        self.where = ["--file", str(Path(file).expanduser())] if file else ["--global"]
        self.label = f"git config {' '.join(self.where)} {key}"

    def current(self) -> str | None:
        r = run(["git", "config", *self.where, "--get", self.gkey], check=False)
        return r.stdout.strip() if r.returncode == 0 else None

    def desired(self) -> str:
        return self.value

    def backup(self) -> Any:
        existed = Path(self.file).expanduser().exists() if self.file else True
        return {"value": self.current(), "existed": existed, "key": self.gkey, "file": self.file}

    def apply(self) -> None:
        run(["git", "config", *self.where, self.gkey, self.value])

    def restore(self, backup: Any) -> None:
        if isinstance(backup, dict):  # older receipts stored the bare previous value
            value, existed = backup.get("value"), backup.get("existed", True)
        else:
            value, existed = backup, True
        if value is None:
            run(["git", "config", *self.where, "--unset", self.gkey], check=False)
        else:
            run(["git", "config", *self.where, self.gkey, value])
        path = Path(self.file).expanduser() if self.file else None
        if path and not existed and path.exists() and not run(["git", "config", *self.where, "--list"]).stdout.strip():
            path.unlink()  # we created the file and it holds no settings anymore: remove it

    def _where_sh(self) -> str:
        return f"--file {sh_path(self.file)}" if self.file else "--global"

    def sh(self) -> list[str]:
        return [f"git config {self._where_sh()} {shlex.quote(self.gkey)} {shlex.quote(self.value)}"]

    def undo_sh(self, backup: Any) -> list[str]:
        value = backup.get("value") if isinstance(backup, dict) else backup
        if value is None:
            return [f"git config {self._where_sh()} --unset {shlex.quote(self.gkey)} || true"]
        return [f"git config {self._where_sh()} {shlex.quote(self.gkey)} {shlex.quote(value)}"]


def setting_effects(art: Artifact, p: Platform, answers: dict[str, str] | None = None) -> list[Effect]:
    """Settings with `{{answer}}` placeholders filled in. A git setting whose value comes out empty is skipped."""
    effs: list[Effect] = []
    answers = answers or {}
    for s in art.settings:
        if isinstance(s, VSCodeSetting):
            effs.append(VSCodeSettingEffect(art.id, vscode_settings_path(p), s.key, s.value))
        elif isinstance(s, GitConfig):
            key, value = render(s.key, answers), render(s.value, answers)
            if value and "{{" not in key + value:  # unanswered → nothing to set yet
                effs.append(GitConfigEffect(art.id, key, value, s.file))
    return effs
