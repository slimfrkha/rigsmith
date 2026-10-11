"""Bootstrap artifacts other backends depend on."""

from rigsmith.backends import BREW_PATHS, Apt, Script
from rigsmith.model import Artifact, Snippet

BREW_INSTALL = (
    'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
)

Artifact(
    id="apt-base",
    help="Build tools Homebrew needs on Linux: build-essential, procps, curl, file, git.",
    sources=[Apt("build-essential procps curl file git", os="linux")],
)

Artifact(
    id="homebrew",
    help="The package manager rigsmith uses on macOS and Linux. Never uninstalled by rigsmith.",
    sources=[Script("homebrew", install_cmd=BREW_INSTALL, needs_sudo=True)],
    check=" || ".join(f"test -x {b}" for b in BREW_PATHS),
    shell=Snippet("homebrew.zsh", 5),
    requires=["apt-base"],
)
