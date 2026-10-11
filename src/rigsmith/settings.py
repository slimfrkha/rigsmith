"""Settings effects: keys in shared files (VS Code settings.json, global git config)."""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from rigsmith.effects import Effect
from rigsmith.model import Artifact, GitConfig, Platform, VSCodeSetting, run


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


class GitConfigEffect(Effect):
    def __init__(self, artifact: str, key: str, value: str) -> None:
        self.artifact, self.gkey, self.value = artifact, key, value
        self.key, self.label = f"git:{key}", f"git config --global {key}"

    def current(self) -> str | None:
        r = run(["git", "config", "--global", "--get", self.gkey], check=False)
        return r.stdout.strip() if r.returncode == 0 else None

    def desired(self) -> str:
        return self.value

    def backup(self) -> Any:
        return self.current()

    def apply(self) -> None:
        run(["git", "config", "--global", self.gkey, self.value])

    def restore(self, backup: Any) -> None:
        if backup is None:
            run(["git", "config", "--global", "--unset", self.gkey], check=False)
        else:
            run(["git", "config", "--global", self.gkey, backup])


def setting_effects(art: Artifact, p: Platform) -> list[Effect]:
    effs: list[Effect] = []
    for s in art.settings:
        if isinstance(s, VSCodeSetting):
            effs.append(VSCodeSettingEffect(art.id, vscode_settings_path(p), s.key, s.value))
        elif isinstance(s, GitConfig):
            effs.append(GitConfigEffect(art.id, s.key, s.value))
    return effs
