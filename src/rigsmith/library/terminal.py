"""Terminal emulators, Nerd Fonts and terminal themes."""

from rigsmith.backends import Cask, NerdFont
from rigsmith.model import Artifact, File

Artifact(
    id="iterm2",
    help="iTerm2: the classic macOS terminal (split panes, hotkey window, search, profiles).",
    sources=[Cask("iterm2", os="darwin")],
    role="terminal",
    check="test -d /Applications/iTerm.app",
)
Artifact(
    id="ghostty",
    help="Ghostty: fast, native, GPU-accelerated terminal with sane defaults.",
    sources=[Cask("ghostty", os="darwin")],
    role="terminal",
    check="test -d /Applications/Ghostty.app",
)

for id, cask, family, label in [
    ("meslo-nf", "font-meslo-lg-nerd-font", "Meslo", "MesloLGS Nerd Font: the font powerlevel10k recommends"),
    ("jetbrains-nf", "font-jetbrains-mono-nerd-font", "JetBrainsMono", "JetBrains Mono Nerd Font, with ligatures"),
    ("fira-nf", "font-fira-code-nerd-font", "FiraCode", "Fira Code Nerd Font, with ligatures"),
]:
    Artifact(
        id=id,
        help=f"{label}. Patched with icons for eza, yazi and the prompt.",
        sources=[Cask(cask, os="darwin"), NerdFont(family, os="linux")],
        tags=["icons"],
        notes=["Set your terminal font to a Nerd Font (e.g. 'MesloLGS Nerd Font') to see icons."],
    )

Artifact(
    id="catppuccin-iterm",
    help="Catppuccin Mocha color preset for iTerm2.",
    files=[File("Catppuccin-Mocha.itermcolors", "~/.config/iterm2/Catppuccin-Mocha.itermcolors", os="darwin")],
    requires=["iterm2"],
    tags=["theme"],
    notes=[
        "iTerm2 → Settings → Profiles → Colors → Color Presets → Import "
        "~/.config/iterm2/Catppuccin-Mocha.itermcolors, then select it."
    ],
)
