"""AI coding assistants: terminal agents and their editor integrations."""

from rigsmith.backends import Cask, Script
from rigsmith.library._util import ext
from rigsmith.model import Artifact

Artifact(
    id="claude-code",
    help="Claude Code: Anthropic's coding agent in your terminal. Run `claude` in a repo.",
    sources=[
        Cask("claude-code", os="darwin"),
        Script(
            "claude-code",
            install_cmd="curl -fsSL https://claude.ai/install.sh | bash",
            check_cmd="command -v claude || test -x ~/.local/bin/claude",
            remove_cmd="rm -f ~/.local/bin/claude && rm -rf ~/.local/share/claude",
            os="linux",
        ),
    ],
    bin="claude",
)
Artifact(
    id="codex",
    help="Codex: OpenAI's coding agent in your terminal. Run `codex` in a repo.",
    sources=[
        Cask("codex", os="darwin"),
        Script(
            "codex",
            install_cmd="npm install -g @openai/codex",
            check_cmd="command -v codex",
            remove_cmd="npm uninstall -g @openai/codex",
            os="linux",
        ),
    ],
    bin="codex",
    requires=["node"],
)
ext("claude-code-ext", "anthropic.claude-code", "Claude Code inside VS Code: diffs, context from open files.")
ext("continue", "Continue.continue", "Open-source AI assistant: bring your own model.")
