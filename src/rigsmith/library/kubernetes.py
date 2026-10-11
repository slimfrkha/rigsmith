"""Kubernetes: CLIs, UIs, logs, plugins, validation, local clusters, GitOps."""

from rigsmith.backends import Brew, Krew
from rigsmith.library._util import ext, snippet, tool
from rigsmith.model import Artifact, Snippet

tool(
    "kubectl",
    "The Kubernetes CLI, with lazy-loaded completion so shell startup stays fast.",
    brew="kubernetes-cli",
    shell=Snippet("kubectl.zsh", 50),
)
tool("kubectx", "kubectx / kubens: switch context and namespace in one word.")
snippet(
    "k8s-aliases",
    "k, kgp, kgpa, kgd, kgs, kgn, ka, kdel, kdiff, k9 + fuzzy kctx/kns and kdebug (throwaway pod).",
    70,
    requires=["kubectl"],
)
tool("helm", "The Kubernetes package manager, with lazy-loaded completion.", shell=Snippet("helm.zsh", 50))
snippet("helm-aliases", "hl, hla, hui (upgrade --install), hd, hru, ht.", 70, requires=["helm"])
tool(
    "k9s", "THE terminal UI for Kubernetes: browse, logs, exec, port-forward, edit. `:pods`, `/` filter.", tags=["tui"]
)
tool("kustomize", "Template-free customization of Kubernetes YAML (`kubectl -k` without the version lag).")
tool("stern", "Tail logs from many pods at once, color-coded: `stern api -n prod`.")
Artifact(
    id="krew",
    help="kubectl plugin manager. Plugins land in ~/.krew/bin.",
    sources=[Brew("krew")],
    bin="kubectl-krew",
    shell=Snippet("krew.zsh", 10),
    requires=["kubectl"],
)
for plugin, about in [
    ("neat", "kubectl neat: strip clutter from YAML output"),
    ("tree", "kubectl tree: ownership hierarchy of resources"),
    ("images", "kubectl images: container images running in the cluster"),
    ("get-all", "kubectl get-all: really list every resource"),
    ("whoami", "kubectl whoami: the subject your credentials map to"),
]:
    Artifact(id=f"krew-{plugin}", help=f"{about}.", sources=[Krew(plugin)])
tool("kubeconform", "Validate manifests against Kubernetes schemas, fast. Good in CI.")
tool("popeye", "Scan a live cluster for misconfigurations and stale resources.")
tool("kube-score", "Static analysis of manifests for reliability and security best practices.")
tool("kind", "Kubernetes in Docker: local clusters in seconds for testing. `kind create cluster`.")
tool("argocd", "Argo CD CLI for GitOps deployments.")
ext(  # depends on the YAML extension
    "k8s-ext",
    "ms-kubernetes-tools.vscode-kubernetes-tools",
    "Kubernetes explorer, manifests and Helm in VS Code.",
    requires=["vscode", "yaml-ext"],
)
ext("helm-ext", "Tim-Koehler.helm-intellisense", "Autocomplete for Helm chart templates and values.")
