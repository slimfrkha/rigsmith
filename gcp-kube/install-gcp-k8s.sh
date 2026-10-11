#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║     🚀 GCP + KUBERNETES SETUP (Minimalist Edition)                        ║
# ║                                                                           ║
# ║   Personal cloud workstation - powerful, lean, opinionated                ║
# ║                                                                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << 'EOF'
   ╔════════════════════════════════════════════════════════════════════════╗
   ║     GCP + K8S SETUP (Minimalist Edition)                               ║
   ╚════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

print_step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}▶ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_substep() { echo -e "  ${CYAN}→${NC} $1"; }
print_success() { echo -e "  ${GREEN}✓${NC} $1"; }
print_warning() { echo -e "  ${YELLOW}⚠${NC} $1"; }
print_error()   { echo -e "  ${RED}✗${NC} $1"; }

check_command() { command -v "$1" &> /dev/null; }

install_brew() {
    local tool="$1"
    print_substep "Installing $tool..."
    if brew install "$tool" 2>&1 | grep -q "Error\|fatal"; then
        print_error "Failed to install $tool"
        return 1
    fi
    print_success "$tool installed"
}

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: HOMEBREW
# ═══════════════════════════════════════════════════════════════════════════

print_step "Step 1/7: Checking Homebrew"

if ! check_command brew; then
    print_substep "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    print_success "Homebrew already installed"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: GOOGLE CLOUD SDK
# ═══════════════════════════════════════════════════════════════════════════

print_step "Step 2/7: Google Cloud SDK"

if ! check_command gcloud; then
    print_substep "Installing Google Cloud SDK..."
    brew install --cask google-cloud-sdk
fi
print_success "gcloud ready"

print_substep "Installing gcloud components..."
gcloud components install kubectl gke-gcloud-auth-plugin --quiet 2>/dev/null || true

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: CORE K8S TOOLS (The Essentials)
# ═══════════════════════════════════════════════════════════════════════════

print_step "Step 3/7: Core Kubernetes Tools"

CORE_TOOLS=(
    "kubectl"       # K8s CLI
    "kubectx"       # Fast context/namespace switching
    "helm"          # Package manager
    "k9s"           # 🔥 THE terminal UI
    "stern"         # Multi-pod logs
    "krew"          # Plugin manager
)

for tool in "${CORE_TOOLS[@]}"; do
    check_command "$tool" && print_success "$tool already installed" || install_brew "$tool"
done

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: KUBECTL PLUGINS (Minimal Set)
# ═══════════════════════════════════════════════════════════════════════════

print_step "Step 4/7: kubectl Plugins (Essential Only)"

export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

# Only the plugins you'll actually use
KREW_PLUGINS=(
    "ctx"           # Context switching
    "ns"            # Namespace switching
    "neat"          # Clean YAML output
    "tree"          # Resource hierarchy
    "images"        # List images
    "get-all"       # Get ALL resources
    "score"         # Static analysis
    "whoami"        # Current user/permissions
)

print_substep "Updating krew..."
kubectl krew update 2>/dev/null || true

for plugin in "${KREW_PLUGINS[@]}"; do
    print_substep "Installing kubectl-$plugin..."
    kubectl krew install "$plugin" 2>/dev/null || print_warning "kubectl-$plugin skipped"
done

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: INFRASTRUCTURE TOOLS
# ═══════════════════════════════════════════════════════════════════════════

print_step "Step 5/7: Infrastructure Tools"

INFRA_TOOLS=(
    "terraform"     # IaC
    "terragrunt"    # Terraform wrapper
    "tflint"        # Linter
    "tfsec"         # Security scanner
    "infracost"     # Cost estimates
    "jq"            # JSON processor
    "yq"            # YAML processor
)

for tool in "${INFRA_TOOLS[@]}"; do
    check_command "$tool" && print_success "$tool already installed" || install_brew "$tool"
done

# ═══════════════════════════════════════════════════════════════════════════
# STEP 6: LOCAL K8S + DOCKER
# ═══════════════════════════════════════════════════════════════════════════

print_step "Step 6/7: Local Kubernetes"

# Only kind - it's the fastest and most reliable
LOCAL_TOOLS=(
    "kind"          # K8s in Docker (the best one)
    "colima"        # Docker runtime (better than Docker Desktop)
)

for tool in "${LOCAL_TOOLS[@]}"; do
    check_command "$tool" && print_success "$tool already installed" || install_brew "$tool"
done

# Optional tools - prompt user
echo -e "\n${YELLOW}Install optional tools? (argocd, popeye, kubeconform, dive) [y/N]${NC}"
read -r install_optional
if [[ $install_optional == "y" ]]; then
    OPTIONAL_TOOLS=("argocd" "popeye" "kubeconform" "dive")
    for tool in "${OPTIONAL_TOOLS[@]}"; do
        check_command "$tool" && print_success "$tool already installed" || install_brew "$tool"
    done
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 7: SHELL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

print_step "Step 7/7: Shell Configuration"

# Backup
if [[ -f ~/.zshrc ]]; then
    cp ~/.zshrc ~/.zshrc.backup.gcp-k8s.$(date +%Y%m%d_%H%M%S)
    print_success "Backed up .zshrc"
fi

# Add config if not present
if ! grep -q "# GCP & KUBERNETES CONFIGURATION" ~/.zshrc 2>/dev/null; then
    print_substep "Adding configuration to .zshrc..."
    cat >> ~/.zshrc << 'ZSHRC'

# ═══════════════════════════════════════════════════════════════════════════
# GCP & KUBERNETES CONFIGURATION (Minimalist)
# ═══════════════════════════════════════════════════════════════════════════

# Google Cloud SDK
if [[ -f "$(brew --prefix 2>/dev/null)/share/google-cloud-sdk/path.zsh.inc" ]]; then
    source "$(brew --prefix)/share/google-cloud-sdk/path.zsh.inc"
    source "$(brew --prefix)/share/google-cloud-sdk/completion.zsh.inc"
fi
export USE_GKE_GCLOUD_AUTH_PLUGIN=True

# Krew path
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

# ─────────────────────────────────────────────────────────────────────────────
# GCLOUD ALIASES (fixed namespace collisions)
# ─────────────────────────────────────────────────────────────────────────────
alias gc="gcloud"
alias gcfg="gcloud config"
alias gcfgl="gcloud config list"
alias gsetp="gcloud config set project"       # was gcp - conflicts with "Google Cloud Platform"
alias gsetr="gcloud config set compute/region"
alias gsetz="gcloud config set compute/zone"

alias gpl="gcloud projects list"
alias gcel="gcloud compute instances list"
alias gcess="gcloud compute ssh"

alias gkecl="gcloud container clusters list"
alias gkecr="gcloud container clusters get-credentials"

alias grun="gcloud run"                        # was gcr - conflicts with Container Registry
alias grunl="gcloud run services list"
alias grund="gcloud run deploy"

alias gfn="gcloud functions"
alias gfnl="gcloud functions list"

alias gsl="gsutil ls"
alias gscp="gsutil cp"

alias bql="bq ls"
alias bqq="bq query --use_legacy_sql=false"

# ─────────────────────────────────────────────────────────────────────────────
# KUBECTL ALIASES (K9s-first - minimal CLI aliases)
# ─────────────────────────────────────────────────────────────────────────────
alias k="kubectl"
alias kx="kubectx"
alias kn="kubens"

# Quick checks (before diving into K9s)
alias kgp="kubectl get pods"
alias kgpa="kubectl get pods -A"
alias kgd="kubectl get deployments"
alias kgs="kubectl get services"
alias kgn="kubectl get nodes"

# Apply/delete (K9s can't do these as easily)
alias ka="kubectl apply -f"
alias kdel="kubectl delete"
alias kdelf="kubectl delete -f"
alias kdiff="kubectl diff -f"

# K9s (your main tool)
alias k9="k9s"
alias k9a="k9s -A"

# Stern (multi-pod logs)
alias st="stern"

# ─────────────────────────────────────────────────────────────────────────────
# HELM ALIASES
# ─────────────────────────────────────────────────────────────────────────────
alias hl="helm list"
alias hla="helm list -A"
alias hui="helm upgrade --install"
alias hd="helm delete"
alias hru="helm repo update"
alias ht="helm template"

# ─────────────────────────────────────────────────────────────────────────────
# TERRAFORM ALIASES
# ─────────────────────────────────────────────────────────────────────────────
alias tf="terraform"
alias tfi="terraform init"
alias tfp="terraform plan"
alias tfa="terraform apply"
alias tfaa="terraform apply -auto-approve"
alias tfd="terraform destroy"
alias tfsl="terraform state list"
alias tfo="terraform output"

# ─────────────────────────────────────────────────────────────────────────────
# DOCKER ALIASES
# ─────────────────────────────────────────────────────────────────────────────
alias d="docker"
alias dc="docker compose"
alias dps="docker ps"
alias di="docker images"

# ─────────────────────────────────────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

# Switch GCP project (fuzzy)
gproj() {
    local project
    project=$(gcloud projects list --format="value(projectId)" | fzf --height 40% --reverse --prompt="GCP Project: ")
    [[ -n "$project" ]] && gcloud config set project "$project" && echo "→ $project"
}

# Get GKE credentials (fuzzy)
gkecreds() {
    local cluster
    cluster=$(gcloud container clusters list --format="value(name,zone)" | fzf --height 40% --reverse --prompt="GKE Cluster: ")
    if [[ -n "$cluster" ]]; then
        local name=$(echo "$cluster" | awk '{print $1}')
        local zone=$(echo "$cluster" | awk '{print $2}')
        gcloud container clusters get-credentials "$name" --zone "$zone"
        echo "→ $name (run: k9s)"
    fi
}

# Context switch (fuzzy) - then start k9s
kctx() {
    local ctx
    ctx=$(kubectl config get-contexts -o name | fzf --height 40% --reverse --prompt="Context: ")
    [[ -n "$ctx" ]] && kubectl config use-context "$ctx" && echo "→ $ctx"
}

# Namespace switch (fuzzy)
kns() {
    local ns
    ns=$(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | fzf --height 40% --reverse --prompt="Namespace: ")
    [[ -n "$ns" ]] && kubectl config set-context --current --namespace="$ns" && echo "→ $ns"
}

# Debug pod
kdebug() {
    kubectl run debug-$$  --rm -it --restart=Never --image="${1:-busybox}" -- /bin/sh
}

# ─────────────────────────────────────────────────────────────────────────────
# LAZY-LOADED COMPLETIONS (faster shell startup)
# ─────────────────────────────────────────────────────────────────────────────
# Completions load on first use, not at startup

_lazy_kubectl() {
    unfunction _lazy_kubectl kubectl 2>/dev/null
    source <(command kubectl completion zsh)
    compdef kubectl=kubectl
    kubectl "$@"
}

_lazy_helm() {
    unfunction _lazy_helm helm 2>/dev/null
    source <(command helm completion zsh)
    compdef helm=helm
    helm "$@"
}

if (( $+commands[kubectl] )); then
    compdef _lazy_kubectl kubectl
    kubectl() { _lazy_kubectl "$@" }
fi

if (( $+commands[helm] )); then
    compdef _lazy_helm helm
    helm() { _lazy_helm "$@" }
fi

# Alias completions
compdef k=kubectl

# End of GCP & Kubernetes configuration
ZSHRC
    print_success "Configuration added"
else
    print_success "Configuration already present"
fi

# ═══════════════════════════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════════════════════════

echo -e "\n${GREEN}"
cat << 'EOF'
   ╔════════════════════════════════════════════════════════════════════════╗
   ║   ✓ INSTALLATION COMPLETE                                              ║
   ╠════════════════════════════════════════════════════════════════════════╣
   ║                                                                        ║
   ║   1. source ~/.zshrc                                                   ║
   ║   2. gcloud auth login                                                 ║
   ║   3. gproj          (select project)                                   ║
   ║   4. gkecreds       (get cluster credentials)                          ║
   ║   5. k9s            (do everything here)                               ║
   ║                                                                        ║
   ╚════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}Installed:${NC}"
echo "  gcloud, kubectl, kubectx, helm, k9s, stern, kind, terraform"
echo "  + 8 kubectl plugins via krew"
echo ""
