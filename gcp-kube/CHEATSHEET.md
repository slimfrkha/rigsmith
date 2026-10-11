# GCP + K8S CHEATSHEET (Minimalist)

## 🔑 Core Workflow

```bash
gproj           # Select GCP project (fuzzy)
gkecreds        # Get cluster credentials (fuzzy)
k9s             # DO EVERYTHING HERE
```

---

## ☁️ GCloud

| Alias | Command |
|-------|---------|
| `gc` | `gcloud` |
| `gsetp PROJECT` | Set project |
| `gpl` | List projects |
| `gkecl` | List GKE clusters |
| `gkecr CLUSTER --zone ZONE` | Get credentials |
| `grunl` | List Cloud Run services |
| `gfnl` | List Cloud Functions |

**Fuzzy:** `gproj` (select project), `gkecreds` (select cluster)

---

## 🚢 Kubernetes

| Alias | Command |
|-------|---------|
| `k` | `kubectl` |
| `kx` | `kubectx` |
| `kn` | `kubens` |
| `kgp` | Get pods |
| `kgpa` | Get pods (all ns) |
| `kgd` | Get deployments |
| `kgs` | Get services |
| `ka FILE` | Apply manifest |
| `kdel` | Delete |
| `kdiff FILE` | Diff before apply |

**Fuzzy:** `kctx` (context), `kns` (namespace)

---

## 🖥️ K9s (Your Main Tool)

```bash
k9s             # Start
k9a             # All namespaces
```

### Navigation
| Key | Action |
|-----|--------|
| `:pod` | View pods |
| `:deploy` | Deployments |
| `:svc` | Services |
| `:ns` | Namespaces |
| `:ctx` | Contexts |
| `/` | Filter |
| `?` | Help |

### Actions
| Key | Action |
|-----|--------|
| `l` | Logs |
| `s` | Shell |
| `d` | Describe |
| `y` | YAML |
| `e` | Edit |
| `f` | Port-forward |
| `r` | Restart |
| `Ctrl+d` | Delete |
| `x` | Decode secret |

---

## 📜 Stern (Multi-pod Logs)

```bash
st "api.*"              # Tail pods matching pattern
st -l app=backend       # By label
st ".*" --since 5m      # Last 5 minutes
```

---

## 📦 Helm

| Alias | Command |
|-------|---------|
| `hl` | List releases |
| `hla` | List all namespaces |
| `hui NAME CHART` | Upgrade/install |
| `hd NAME` | Delete |
| `hru` | Repo update |
| `ht CHART` | Template |

---

## 🏗️ Terraform

| Alias | Command |
|-------|---------|
| `tf` | `terraform` |
| `tfi` | Init |
| `tfp` | Plan |
| `tfa` | Apply |
| `tfaa` | Apply (auto-approve) |
| `tfd` | Destroy |
| `tfsl` | State list |
| `tfo` | Output |

---

## 🐳 Docker

| Alias | Command |
|-------|---------|
| `d` | `docker` |
| `dc` | `docker compose` |
| `dps` | List containers |
| `di` | List images |

---

## 🔌 kubectl Plugins

```bash
kubectl ctx             # Switch context
kubectl ns              # Switch namespace
kubectl neat get pod X  # Clean YAML
kubectl tree deploy/X   # Resource hierarchy
kubectl images          # List images
kubectl get-all         # Get EVERYTHING
kubectl score FILE      # Static analysis
kubectl whoami          # Current user
```

---

## 🛠️ Functions

| Function | Description |
|----------|-------------|
| `gproj` | Fuzzy GCP project selector |
| `gkecreds` | Fuzzy GKE credentials |
| `kctx` | Fuzzy context switch |
| `kns` | Fuzzy namespace switch |
| `kdebug [image]` | Debug pod (default: busybox) |

---

## 💡 Daily Workflow

```bash
# Morning setup
gproj                   # Select project
gkecreds                # Get cluster creds
k9s                     # Work in K9s all day

# Quick checks without K9s
kgp                     # Pod status
st "api.*"              # Tail logs
ka manifest.yaml        # Apply changes
```
