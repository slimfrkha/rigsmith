"""Go."""

from rigsmith.library._util import ext, tool
from rigsmith.model import Snippet

tool("go", "The Go toolchain. Puts ~/go/bin (go install targets) on PATH.", shell=Snippet("go.zsh", 10))
tool("gopls", "The official Go language server (editors use it for completion and refactors).", requires=["go"])
tool("golangci-lint", "Fast meta-linter running dozens of Go linters in one pass.")
tool("delve", "The Go debugger: `dlv debug`, `dlv test`.", bin="dlv")
tool("goreleaser", "Build, package and publish Go releases from a single config.")
ext("go-ext", "golang.Go", "Go in VS Code: gopls, tests, debugging, coverage.")
