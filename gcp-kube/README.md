# GCP + Kubernetes Setup (Minimalist Edition)

> **Personal cloud workstation — powerful, lean, opinionated**

---

## 📦 Files

| File | Description |
|------|-------------|
| `install-gcp-k8s.sh` | Main installer |
| `install-vscode-extensions.sh` | VS Code extensions (10 essential) |
| `cleanup-bloat.sh` | Remove old/redundant tools |
| `CHEATSHEET.md` | Command reference |
| `TOOLS-EXPLAINED.md` | What each tool does |

---

## ⚡ Quick Start

```bash
# 1. Install
chmod +x install-gcp-k8s.sh
./install-gcp-k8s.sh

# 2. Reload shell
source ~/.zshrc

# 3. Login
gcloud auth login
gcloud auth application-default login

# 4. Select project & cluster
gproj           # Fuzzy project selector
gkecreds        # Fuzzy cluster credentials

# 5. Work in K9s
k9s             # Do everything here
```

---

## 🛠️ What Gets Installed

### Core (Always Installed)

| Tool | Purpose |
|------|---------|
| `gcloud` | Google Cloud CLI |
| `kubectl` | Kubernetes CLI |
| `kubectx` | Fast context switching |
| `helm` | Package manager |
| `k9s` | 🔥 Terminal UI (your main tool) |
| `stern` | Multi-pod log tailing |
| `kind` | Local K8s clusters |
| `colima` | Docker runtime |

### Infrastructure

| Tool | Purpose |
|------|---------|
| `terraform` | Infrastructure as Code |
| `terragrunt` | Terraform wrapper |
| `tflint` | Terraform linter |
| `tfsec` | Security scanner |
| `infracost` | Cost estimates |
| `jq` / `yq` | JSON/YAML processors |

### kubectl Plugins (8 essential)

| Plugin | Purpose |
|--------|---------|
| `ctx` | Context switching |
| `ns` | Namespace switching |
| `neat` | Clean YAML output |
| `tree` | Resource hierarchy |
| `images` | List container images |
| `get-all` | Get ALL resources |
| `score` | Static analysis |
| `whoami` | Current user/permissions |

### Optional (Prompted)

| Tool | Purpose |
|------|---------|
| `argocd` | GitOps CD |
| `popeye` | Cluster sanitizer |
| `kubeconform` | Manifest validation |
| `dive` | Docker image explorer |

---

## ⌨️ Key Commands

### Setup (Before K9s)

| Command | Description |
|---------|-------------|
| `gproj` | Fuzzy GCP project selector |
| `gkecreds` | Fuzzy cluster credentials |
| `kctx` | Fuzzy context switch |
| `kns` | Fuzzy namespace switch |

### Then Use K9s

```bash
k9s    # Your command center
```

| K9s Key | Action |
|---------|--------|
| `:pod` | View pods |
| `:deploy` | View deployments |
| `:svc` | View services |
| `l` | Logs |
| `s` | Shell |
| `d` | Describe |
| `f` | Port-forward |
| `r` | Restart |
| `Ctrl+d` | Delete |
| `x` | Decode secret |

### Quick CLI (When Needed)

| Alias | Command |
|-------|---------|
| `k` | `kubectl` |
| `kgp` | Get pods |
| `ka FILE` | Apply manifest |
| `kdel` | Delete |
| `st "pattern"` | Stern logs |

---

## 🔧 Alias Changes

Fixed namespace collisions:

| Old | New | Reason |
|-----|-----|--------|
| `gcp` | `gsetp` | "gcp" = Google Cloud Platform |
| `gcr` | `grun` | "gcr" = Container Registry |
| `gp` | `gproj` | Conflicts with git aliases |

---

## 📊 VS Code Extensions (10 Essential)

| Extension | Purpose |
|-----------|---------|
| Cloud Code | GCP integration |
| Kubernetes | K8s support |
| Docker | Container management |
| YAML | K8s manifest support |
| Terraform | IaC support |
| Helm Intellisense | Chart support |
| Remote Containers | Dev containers |
| Remote SSH | Remote development |
| REST Client | API testing |
| DotENV | .env files |

---

## 🧹 Cleanup Old Bloat

If you had the previous version installed:

```bash
chmod +x cleanup-bloat.sh
./cleanup-bloat.sh
```

This removes: minikube, k3d, flux, pulumi, lazydocker, and 9 rarely-used kubectl plugins.

---

## 💡 Daily Workflow

```bash
# Morning
gproj                   # Select project (if needed)
gkecreds                # Get credentials (if needed)
k9s                     # Work here all day

# Quick checks (without K9s)
kgp                     # Pod status
st "api.*"              # Tail logs

# Deploy
ka manifest.yaml        # Apply
kdiff manifest.yaml     # Diff first
```

---

## 🚨 Troubleshooting

**gcloud not found:**
```bash
source "$(brew --prefix)/share/google-cloud-sdk/path.zsh.inc"
```

**Aliases not working:**
```bash
source ~/.zshrc
```

**K9s shows wrong cluster:**
```bash
kctx    # Select correct context first
```

---

## 📚 Links

- [K9s](https://k9scli.io/)
- [Stern](https://github.com/stern/stern)
- [Helm](https://helm.sh/docs/)
- [Terraform GCP](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [kind](https://kind.sigs.k8s.io/)
