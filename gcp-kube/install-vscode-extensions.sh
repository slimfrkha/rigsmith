#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║           GCP + KUBERNETES VS CODE EXTENSIONS (Essential Only)            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing essential GCP + K8s extensions...${NC}\n"

if ! command -v code &> /dev/null; then
    echo "⚠ 'code' command not found!"
    echo "VS Code → Cmd+Shift+P → 'Shell Command: Install code command'"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════
# ESSENTIAL ONLY - No bloat
# ═══════════════════════════════════════════════════════════════════════════

EXTENSIONS=(
    # Core
    "googlecloudtools.cloudcode"                   # GCP integration
    "ms-kubernetes-tools.vscode-kubernetes-tools"  # K8s support
    "ms-azuretools.vscode-docker"                  # Docker

    # Config files
    "redhat.vscode-yaml"                           # YAML (essential for K8s)
    "hashicorp.terraform"                          # Terraform (includes HCL)
    "tim-koehler.helm-intellisense"                # Helm charts

    # Remote
    "ms-vscode-remote.remote-containers"           # Dev Containers
    "ms-vscode-remote.remote-ssh"                  # Remote SSH

    # API testing (pick ONE)
    "humao.rest-client"                            # REST Client

    # Utilities
    "mikestead.dotenv"                             # .env files
)

for ext in "${EXTENSIONS[@]}"; do
    echo -ne "  ${ext}..."
    if code --install-extension "$ext" --force &>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo " (skipped)"
    fi
done

echo -e "\n${GREEN}Done!${NC} Restart VS Code."
echo ""
echo "Installed:"
echo "  • Cloud Code (GCP)"
echo "  • Kubernetes"
echo "  • Docker"
echo "  • YAML + Terraform + Helm"
echo "  • Remote SSH/Containers"
echo "  • REST Client"
