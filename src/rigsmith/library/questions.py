"""Built-in questions. Each is asked only if an artifact in the menu references it."""

from rigsmith.model import Question

Question(
    id="icons",
    text="Show icons in the terminal? (needs a Nerd Font in your terminal)",
    help="Yes installs a Nerd Font and turns on icons in eza, fzf previews, yazi. No skips the fonts.",
    choices={"yes": {"env": {"RIGSMITH_ICONS": "1"}}, "no": {"exclude_tags": ["icons"]}},
    default="yes",
)
Question(
    id="aliases",
    text="Replace classic commands with modern ones? (ls→eza, cat→bat, grep→rg, …)",
    help="Yes installs alias artifacts. No keeps the tools under their own names (eza, bat, rg).",
    choices={"yes": {}, "no": {"exclude_tags": ["aliases"]}},
    default="yes",
)
Question(
    id="tui",
    text="Install full-screen terminal apps? (lazygit, k9s, yazi, bottom)",
    choices={"yes": {}, "no": {"exclude_tags": ["tui"]}},
    default="yes",
)
Question(
    id="fun",
    text="Install fun stuff? (cmatrix, lolcat, cowsay, fastfetch)",
    choices={"yes": {}, "no": {"exclude_tags": ["fun"]}},
    default="no",
)
Question(
    id="theme",
    text="Color theme for terminal tools and editors",
    help="Catppuccin Mocha everywhere (fzf, delta, iTerm2, VS Code), or leave tools on their defaults.",
    choices={"catppuccin": {"env": {"RIGSMITH_THEME": "catppuccin"}}, "none": {"exclude_tags": ["theme"]}},
    default="catppuccin",
)
Question(
    id="work-dir",
    kind="text",
    text="Folder that holds your work repositories",
    help="Every git repo under it commits with your work identity; everything else keeps your global one.",
    default="~/work/",
    normalize=lambda v: v.rstrip("/") + "/",  # git only matches subfolders when the pattern ends with /
)
Question(
    id="work-email",
    kind="text",
    text="Your work email for git commits",
    help="Leave empty to set it later: git config --file ~/.gitconfig-work user.email you@company.com",
    default="",
)
