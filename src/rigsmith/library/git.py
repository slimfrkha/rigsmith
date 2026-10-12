"""git, GitHub CLI, git UIs and diff tooling."""

from rigsmith.library._util import ext, snippet, tool
from rigsmith.model import Artifact, GitConfig, Snippet, VSCodeSetting

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
Artifact(
    id="git-identities",
    help="Work identity in work repos, your own everywhere else: git switches by folder (includeIf), "
    "nothing to remember.",
    settings=[
        GitConfig("includeIf.gitdir:{{work-dir}}.path", "~/.gitconfig-work"),
        GitConfig("user.email", "{{work-email}}", file="~/.gitconfig-work"),
    ],
    prefs=["work-dir", "work-email"],
    requires=["git"],
    notes=[
        "Clone work repos under your work folder; inside one, `git config user.email` shows the work email.",
        "Add more work-only settings (signing key, sshCommand) to ~/.gitconfig-work.",
    ],
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
ext(
    "gitlens-ext",
    "eamodio.gitlens",
    "GitLens: blame, history and comparisons in VS Code (code lens off, current-line blame on).",
    settings=[VSCodeSetting("gitlens.codeLens.enabled", False), VSCodeSetting("gitlens.currentLine.enabled", True)],
)
ext("git-graph-ext", "mhutchie.git-graph", "Interactive git graph of your repository.")
ext("github-pr-ext", "GitHub.vscode-pull-request-github", "Review and manage GitHub pull requests in VS Code.")
