"""~/.zshrc integration: one marked block that sources init.zsh, which sources shell.d/*.zsh."""

import re
from pathlib import Path
from typing import Any

from rigsmith.effects import Effect, FileEffect, shell_d
from rigsmith.model import config_home

BEGIN, END = "# >>> rigsmith >>>", "# <<< rigsmith <<<"
BLOCK = f"{BEGIN}\nsource ~/.config/rigsmith/init.zsh\n{END}\n"
INIT = """# Managed by rigsmith: sources every snippet in shell.d in order. Do not edit.
for _rs_snippet in ~/.config/rigsmith/shell.d/*.zsh(N); do
  source "$_rs_snippet"
done
unset _rs_snippet
"""
CORE = "_rigsmith"  # pseudo-artifact owning the block, init.zsh and prefs


def zshrc() -> Path:
    return Path.home() / ".zshrc"


class ZshrcBlock(Effect):
    artifact, key, label = CORE, "zshrc-block", "add the rigsmith block to ~/.zshrc"

    def current(self) -> str | None:
        return "present" if zshrc().is_file() and BEGIN in zshrc().read_text() else None

    def desired(self) -> str:
        return "present"

    def backup(self) -> Any:
        return {"existed": zshrc().exists()}

    def apply(self) -> None:
        text = zshrc().read_text() if zshrc().exists() else ""
        zshrc().write_text(BLOCK + text)

    def sh(self) -> list[str]:
        lines = " ".join(f"'{line}'" for line in BLOCK.splitlines())
        return [
            f"if ! grep -qx '{BEGIN}' \"$HOME/.zshrc\" 2>/dev/null; then",
            f'  {{ printf \'%s\\n\' {lines}; cat "$HOME/.zshrc" 2>/dev/null || true; }} > "$HOME/.zshrc.rigsmith-tmp"',
            '  mv "$HOME/.zshrc.rigsmith-tmp" "$HOME/.zshrc"',
            "fi",
        ]

    def undo_sh(self, backup: Any) -> list[str]:
        lines = [f'sed -i.rigsmith-bak \'/^{BEGIN}$/,/^{END}$/d\' "$HOME/.zshrc" && rm -f "$HOME/.zshrc.rigsmith-bak"']
        if not (backup or {}).get("existed", True):
            lines.append('[ -s "$HOME/.zshrc" ] || rm -f "$HOME/.zshrc"')
        return lines

    def restore(self, backup: Any) -> None:
        text = zshrc().read_text()
        if text.startswith(BLOCK):
            text = text[len(BLOCK) :]
        else:  # moved by the user: drop the block wherever it is
            text = re.sub(rf"{re.escape(BEGIN)}.*?{re.escape(END)}\n?", "", text, flags=re.S)
        if text or (backup or {}).get("existed", True):
            zshrc().write_text(text)
        else:
            zshrc().unlink()


def core_effects(env: dict[str, str]) -> list[Effect]:
    """Effects shared by every snippet: prefs, init.zsh and the ~/.zshrc block."""
    prefs = "# Managed by rigsmith: answers to the questionnaire.\n" + "".join(
        f"export {k}={v}\n" for k, v in sorted(env.items())
    )
    return [
        FileEffect(CORE, shell_d() / "01-rigsmith-prefs.zsh", prefs.encode()),
        FileEffect(CORE, config_home() / "init.zsh", INIT.encode()),
        ZshrcBlock(),
    ]


def has_snippets() -> bool:
    return any(p.name != "01-rigsmith-prefs.zsh" for p in shell_d().glob("*.zsh"))


def conflicts(patterns: dict[str, list[str]]) -> list[str]:
    """Lines of the user's ~/.zshrc (outside our block) that would double-load with our snippets."""
    if not zshrc().is_file():
        return []
    found, inside = [], False
    for n, line in enumerate(zshrc().read_text().splitlines(), 1):
        inside = (inside or line.strip() == BEGIN) and line.strip() != END
        if inside or line.lstrip().startswith("#"):
            continue
        for art, pats in patterns.items():
            if any(re.search(p, line) for p in pats):
                found.append(f"~/.zshrc:{n} `{line.strip()[:70]}` overlaps with {art}")
                break
    return found
