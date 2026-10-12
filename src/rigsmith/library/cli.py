"""Modern command-line tools and the aliases that swap them in for the classics."""

from rigsmith.library._util import snippet, tool
from rigsmith.model import Snippet

# files
tool("eza", "Modern ls with colors, git status and optional icons. `eza -la --git`, `eza --tree`.")
snippet(
    "eza-aliases",
    "ls/ll/la/lt/lsize/ltime → eza (icons when enabled).",
    70,
    requires=["eza"],
    tags=["aliases"],
    prefs=["icons"],
)
tool("tree", "Print directory trees.")
tool(
    "yazi",
    "Blazing fast terminal file manager with previews. `y` opens it and cds to where you quit.",
    shell=Snippet("yazi.zsh", 70),
    tags=["tui"],
    prefs=["icons"],
)

# search
tool("ripgrep", "rg: recursive grep that respects .gitignore, extremely fast.", bin="rg")
snippet("ripgrep-aliases", "grep → rg, plus rgi/rgl/rgc/rgh.", 70, requires=["ripgrep"], tags=["aliases"])
tool("fd", "Simple, fast find. `fd pattern`, `fd -e py`.")
tool("peco", "Interactive filter for any list: `ls | peco`, `kubectl get pods | peco`.")
snippet("fd-aliases", "find → fd, plus fdi/fdh/fde.", 70, requires=["fd"], tags=["aliases"])
snippet(
    "fzf-functions",
    "fzf helpers: rgs (search contents with preview), fkill (pick processes to kill), fp (find a file with preview).",
    70,
    requires=["fzf", "ripgrep", "bat"],
)
tool(
    "fzf",
    "The fuzzy finder. Ctrl+T files, Alt+C dirs, ** <Tab> fuzzy completion. Uses fd and bat when present.",
    shell=Snippet("fzf.zsh", 50),
    prefs=["icons", "theme"],
    conflicts=[r"fzf --zsh", r"\.fzf\.zsh"],
)

# view & edit
tool("bat", "cat with syntax highlighting, line numbers and git markers.")
snippet(
    "bat-aliases",
    "cat → bat, catp (plain), and colored man pages through bat.",
    70,
    requires=["bat"],
    tags=["aliases"],
)
tool("sd", "Intuitive find & replace: `sd 'from' 'to' file`.")
tool(
    "micro",
    "Modern terminal editor with mouse support and familiar shortcuts (Ctrl+S, Ctrl+Q).",
    role="editor",
    shell=Snippet("micro.zsh", 10),
)
tool(
    "neovim",
    "Hyperextensible Vim-based editor.",
    bin="nvim",
    role="editor",
    shell=Snippet("neovim.zsh", 10),
)
tool(
    "helix",
    "Post-modern modal editor with built-in LSP and tree-sitter.",
    bin="hx",
    role="editor",
    shell=Snippet("helix.zsh", 10),
)

# navigation
tool(
    "zoxide",
    "Smarter cd that learns your habits: `z proj` jumps to the best match, `zi` picks interactively.",
    shell=Snippet("zoxide.zsh", 50),
    conflicts=[r"zoxide init"],
)

# data
tool("jq", "Slice, filter and transform JSON.")
tool("yq", "jq for YAML (and JSON, XML, TOML).")

# system
tool("htop", "Classic interactive process viewer.", role="system-monitor", tags=["tui"])
tool(
    "bottom",
    "Graphical system monitor: CPU, memory, network, disks (`btm`).",
    bin="btm",
    role="system-monitor",
    tags=["tui"],
)
tool("btop", "Resource monitor with graphs and mouse support.", role="system-monitor", tags=["tui"])
tool("dust", "Intuitive du: which directories eat your disk.")
tool("duf", "Friendly df: disk usage overview.")
tool("procs", "Modern ps with colors, tree view and search.")
snippet(
    "sys-aliases",
    "top/htop → btm, df → duf, du → dust, ps → procs (each only if installed).",
    70,
    tags=["aliases"],
)

# network
tool("httpie", "Human-friendly HTTP client: `http GET api.example.com`.", bin="http")
tool("wget", "Download files from the web.")

# docs & misc
tool("tldr", "Simplified, example-driven man pages (tlrc client): `tldr tar`.", brew="tlrc")
tool("watch", "Run a command periodically and show its output.")
tool("tokei", "Count lines of code by language.")
tool("hyperfine", "Command-line benchmarking: `hyperfine 'cmd1' 'cmd2'`.")
tool(
    "thefuck",
    "Fix your previous command: type `fuck` (or `fk`) after a typo.",
    shell=Snippet("thefuck.zsh", 50),
)
