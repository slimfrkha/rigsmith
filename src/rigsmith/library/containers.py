"""Container runtimes and tooling."""

from rigsmith.backends import Apt, Cask
from rigsmith.library._util import ext, snippet, tool
from rigsmith.model import Artifact

tool("docker-cli", "The docker and docker compose CLIs (talk to colima or any engine).", brew="docker", bin="docker")
tool(
    "colima",
    "Colima: lightweight container runtime in a VM, no Docker Desktop license. `colima start`.",
    role="container-runtime",
    requires=["docker-cli"],
    notes=["Run `colima start` to boot the container VM."],
)
Artifact(
    id="orbstack",
    help="OrbStack: fast, light Docker and Linux VMs for macOS (commercial for business use).",
    sources=[Cask("orbstack", os="darwin")],
    role="container-runtime",
    check="test -d /Applications/OrbStack.app",
)
Artifact(
    id="docker-desktop",
    help="Docker Desktop: the official Docker app (license required for larger companies).",
    sources=[Cask("docker-desktop", os="darwin")],
    role="container-runtime",
    check="test -d /Applications/Docker.app",
)
Artifact(
    id="docker-engine",
    help="Docker Engine from your distro (docker.io) with the compose plugin.",
    sources=[Apt("docker.io docker-compose-v2", os="linux")],
    bin="dockerd",
    role="container-runtime",
    notes=["To use docker without sudo: `sudo usermod -aG docker $USER`, then log out and back in."],
)
tool("dive", "Explore a docker image layer by layer and find wasted space.")
tool("lazydocker", "Terminal UI for docker and compose: logs, stats, restart with one key.", tags=["tui"])
snippet("docker-aliases", "d (docker), dc (compose), dps, di. Works with any docker (Desktop, colima, engine).", 70)
ext("docker-ext", "ms-azuretools.vscode-docker", "Dockerfiles, compose and containers in VS Code.")
