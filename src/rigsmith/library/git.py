"""git, GitHub CLI, git UIs and diff tooling."""

from rigsmith.library._util import snippet, tool
from rigsmith.model import Artifact, GitConfig, Snippet

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

Artifact(
    id="git-defaults",
    help="Sensible global git defaults: main as default branch, auto-setup remote on push, rebase on pull, "
    "reuse recorded conflict resolutions.",
    settings=[
        GitConfig("init.defaultBranch", "main"),
        GitConfig("push.autoSetupRemote", "true"),
        GitConfig("pull.rebase", "true"),
        GitConfig("rerere.enabled", "true"),
    ],
    requires=["git"],
)
tool(
    "delta",
    "Beautiful git diffs: syntax highlighting, side-by-side, line numbers. Becomes git's pager.",
    brew="git-delta",
    settings=[
        GitConfig("core.pager", "delta"),
        GitConfig("interactive.diffFilter", "delta --color-only"),
        GitConfig("delta.navigate", "true"),
        GitConfig("delta.side-by-side", "true"),
        GitConfig("delta.line-numbers", "true"),
    ],
    requires=["git"],
)
