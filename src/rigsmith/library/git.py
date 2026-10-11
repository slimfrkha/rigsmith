"""git, GitHub CLI, git UIs and diff tooling."""

from rigsmith.library._util import snippet, tool
from rigsmith.model import Snippet

tool("git", "Distributed version control.")
tool("gh", "GitHub CLI: PRs, issues, releases and API from the terminal. `gh pr create`, `gh pr checkout`.")
snippet(
    "git-aliases",
    "Short git aliases (gs, ga, gc, gp, gl, glog, gundo, gwip…) plus fzf helpers gfco and gitlog.",
    70,
    requires=["git"],
)
tool(
    "lazygit",
    "Terminal UI for git: stage hunks, rebase, resolve conflicts with single keys. `lg` opens it.",
    shell=Snippet("lazygit.zsh", 70),
    tags=["tui"],
)
