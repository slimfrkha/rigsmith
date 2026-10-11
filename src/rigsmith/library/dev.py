"""General developer tooling, whatever the language."""

from rigsmith.library._util import tool
from rigsmith.model import Snippet

tool("just", "A command runner: project recipes in a justfile, `just test`.")
tool(
    "direnv",
    "Load and unload environment variables per directory from .envrc.",
    shell=Snippet("direnv.zsh", 50),
    conflicts=[r"direnv hook"],
)
tool(
    "mise",
    "Polyglot version manager (node, python, go, java… per project) and task runner. Successor of asdf.",
    shell=Snippet("mise.zsh", 50),
    conflicts=[r"mise activate", r"asdf\.sh"],
)
tool("pre-commit", "Run linters and formatters as git hooks: `pre-commit install`.")
tool("watchexec", "Run a command when files change: `watchexec -e py pytest`.")
tool("glow", "Render Markdown beautifully in the terminal.")
