"""zsh, its plugin manager, prompt, plugins, history and helpers."""

import os
from pathlib import Path

from rigsmith.backends import Apt, Brew, GitClone
from rigsmith.effects import Effect, LoginShellEffect
from rigsmith.library._util import snippet, tool
from rigsmith.model import Artifact, Platform, Snippet, run


class Zsh(Artifact):
    def extra_effects(self, p: Platform) -> list[Effect]:
        return [LoginShellEffect(self.id)] if p.os == "linux" else []


Zsh(
    id="zsh",
    help="The Z shell. rigsmith's snippets are zsh. Sets history, options and the completion system.",
    sources=[Brew("zsh", os="darwin"), Apt("zsh", os="linux")],
    bin="zsh",
    shell=[Snippet("zsh-options.zsh", 10), Snippet("zsh-completion.zsh", 40)],
    conflicts=[r"^\s*autoload\s+-Uz\s+compinit"],
)

Artifact(
    id="zinit",
    help="Fast zsh plugin manager (turbo mode). Loads plugins and oh-my-zsh snippets without oh-my-zsh.",
    sources=[GitClone("https://github.com/zdharma-continuum/zinit.git", dest="~/.local/share/zinit/zinit.git")],
    shell=Snippet("zinit.zsh", 20),
    requires=["git"],
    conflicts=[r"zinit\.zsh", r"oh-my-zsh\.sh"],
)

Artifact(
    id="p10k",
    help="Powerlevel10k: a rich, very fast prompt with instant prompt. Run `p10k configure` after install.",
    sources=[Brew("powerlevel10k")],
    role="prompt",
    shell=[Snippet("p10k-instant.zsh", 0), Snippet("p10k.zsh", 90)],
    notes=["Run `p10k configure` to design your prompt (writes ~/.p10k.zsh)."],
    conflicts=[r"powerlevel10k", r"p10k-instant-prompt"],
)

tool(
    "starship",
    "Starship: minimal, fast, cross-shell prompt configured in ~/.config/starship.toml.",
    role="prompt",
    shell=Snippet("starship.zsh", 90),
    conflicts=[r"starship init"],
)

snippet(
    "zsh-autosuggestions",
    "Fish-like suggestions from history as you type. → accepts.",
    30,
    requires=["zinit"],
    conflicts=[r"zsh-autosuggestions"],
)
snippet(
    "zsh-completions",
    "Hundreds of extra completion definitions for common tools.",
    30,
    requires=["zinit"],
)
snippet(
    "zsh-syntax-highlighting",
    "Colors commands as you type: green = valid, red = unknown.",
    80,
    requires=["zinit"],
    conflicts=[r"zsh-syntax-highlighting"],
)
snippet(
    "zsh-history-substring-search",
    "Type part of a command, then ↑/↓ to cycle through matching history.",
    81,
    requires=["zinit"],
)
snippet(
    "omz-plugins",
    "oh-my-zsh goodies via zinit: ESC ESC adds sudo, colored man pages, copypath, copyfile.",
    30,
    requires=["zinit"],
)


class Atuin(Artifact):
    post_install_sh = '[ -f "${ATUIN_DATA_DIR:-$HOME/.local/share/atuin}/history.db" ] || atuin import auto'

    def post_install(self) -> None:  # irreversible: imports existing shell history, only into an empty atuin
        db = Path(os.environ.get("ATUIN_DATA_DIR") or Path.home() / ".local/share/atuin") / "history.db"
        if not db.exists():  # an atuin that already has history would get duplicates
            run("atuin import auto", check=False)


Atuin(
    id="atuin",
    help="Shell history in SQLite with full-text search. Ctrl+R opens a searchable history UI.",
    sources=[Brew("atuin")],
    bin="atuin",
    shell=Snippet("atuin.zsh", 50),
    conflicts=[r"atuin init"],
)

snippet(
    "shell-aliases",
    "Navigation (.., ..., -, dl, dt, pj) and safety aliases (rm -i, cp -i, mv -i, mkdir -p).",
    70,
)
snippet(
    "shell-functions",
    "Helpers: mkcd, extract (any archive), bak (timestamped copy), dirsize, port, newproject.",
    70,
)
snippet(
    "shell-extras",
    "Small utilities: note, wttr (weather), cheat, myip, ports, now/timestamp, path, uuid.",
    70,
)
