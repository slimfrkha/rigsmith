# GCP + Kubernetes Tools Explained

> What each tool does and why it's in the stack.

---

## ☁️ Google Cloud

### gcloud

The official GCP CLI. Manages everything.

```bash
gcloud auth login                    # Authenticate
gcloud config set project PROJECT    # Set project
gcloud container clusters list       # List GKE clusters
```

**Fuzzy functions:**
```bash
gproj      # Interactive project selector
gkecreds   # Interactive cluster credentials
```

### gsutil

Cloud Storage CLI.

```bash
gsutil ls gs://bucket/              # List
gsutil cp file.txt gs://bucket/     # Upload
gsutil rsync -r ./dir gs://bucket/  # Sync
```

### bq

BigQuery CLI.

```bash
bql                                 # List datasets
bqq "SELECT * FROM table LIMIT 10"  # Query
```

---

## 🚢 Kubernetes Core

### kubectl

The K8s CLI. Foundation for everything.

**But for daily work, use K9s instead.** Keep kubectl for:
- Applying manifests (`ka file.yaml`)
- Quick checks (`kgp`, `kgd`)
- Scripting

### kubectx

Fast context switching. Essential.

```bash
kx              # List and select context
kx production   # Switch directly
kx -            # Previous context
```

**Fuzzy:** `kctx`

### kubens

Fast namespace switching.

```bash
kn              # List and select namespace
kn kube-system  # Switch directly
```

**Fuzzy:** `kns`

---

## 🔥 K9s — The Main Tool

Terminal UI for Kubernetes. **This changes everything.**

### Why K9s?

- See everything at a glance
- Keyboard-driven (fast)
- Real-time updates
- Logs, shell, delete, port-forward — all in one
- No more typing `kubectl get pods` repeatedly

### Start K9s

```bash
k9s         # Start
k9a         # All namespaces
```

### Navigation

| Command | Shows |
|---------|-------|
| `:pod` | Pods |
| `:deploy` | Deployments |
| `:svc` | Services |
| `:ns` | Namespaces |
| `:ctx` | Contexts |
| `:secrets` | Secrets |
| `/pattern` | Filter |

### Actions

| Key | Action |
|-----|--------|
| `l` | Logs |
| `s` | Shell into container |
| `d` | Describe |
| `y` | View YAML |
| `e` | Edit |
| `f` | Port-forward |
| `r` | Restart deployment |
| `Ctrl+d` | Delete |
| `x` | Decode secret |
| `?` | Help |
| `q` | Quit |

### Example Workflow

1. `k9s` — start
2. `:pod` — view pods
3. `/api` — filter to "api" pods
4. `l` — view logs
5. `s` — shell in
6. `Ctrl+d` — delete if needed

**10x faster than kubectl commands.**

---

## 📜 Stern — Multi-Pod Logs

Tail logs from multiple pods simultaneously. The one thing K9s doesn't do as well.

```bash
st "api.*"              # All pods matching "api"
st -l app=backend       # By label
st ".*" --since 5m      # Last 5 minutes
st frontend -c nginx    # Specific container
```

**Example:** 3 replicas of an API:
```bash
st "api-deployment"
# Shows all 3 pods, color-coded:
# api-deployment-abc | Request received
# api-deployment-def | Processing
# api-deployment-ghi | Response sent
```

---

## 📦 Helm

Package manager for Kubernetes.

```bash
# Add repo
helm repo add bitnami https://charts.bitnami.com/bitnami
hru                     # Update repos

# Install
hui my-nginx bitnami/nginx              # Install/upgrade
hui my-nginx bitnami/nginx -f vals.yaml # With values

# Manage
hl                      # List releases
hla                     # All namespaces
hd my-nginx             # Delete
```

---

## 🏗️ Terraform

Infrastructure as Code for GCP.

```bash
tfi         # Init
tfp         # Plan (see changes)
tfa         # Apply
tfaa        # Apply without prompt
tfd         # Destroy
tfsl        # State list
tfo         # Outputs
```

**Example GKE cluster:**
```hcl
resource "google_container_cluster" "primary" {
  name     = "my-cluster"
  location = "us-central1"
  initial_node_count = 3
}
```

### Companion Tools

| Tool | Purpose |
|------|---------|
| `terragrunt` | DRY Terraform, multi-environment |
| `tflint` | Linting |
| `tfsec` | Security scanning |
| `infracost` | Cost estimation |

```bash
tfsec .                 # Scan for security issues
infracost breakdown     # Show estimated costs
```

---

## 🔌 kubectl Plugins

Installed via Krew. Use with `kubectl <plugin>`.

### kubectl neat

Cleans up YAML output (removes managed fields).

```bash
kubectl get pod my-pod -o yaml | kubectl neat
```

### kubectl tree

Shows resource hierarchy.

```bash
kubectl tree deployment/my-app
# Deployment/my-app
# └── ReplicaSet/my-app-abc
#     └── Pod/my-app-abc-xyz
```

### kubectl images

Lists all container images in cluster.

```bash
kubectl images
```

### kubectl get-all

Gets ALL resources (not just common ones).

```bash
kubectl get-all
kubectl get-all -n my-namespace
```

### kubectl score

Static analysis of manifests.

```bash
kubectl score deployment.yaml
```

### kubectl whoami

Shows current user and permissions.

```bash
kubectl whoami
```

---

## 🏠 Local Kubernetes

### kind (Kubernetes in Docker)

The best option. Fast, reliable, matches production K8s.

```bash
kind create cluster                 # Create
kind create cluster --name dev      # Named
kind get clusters                   # List
kind delete cluster                 # Delete
kind load docker-image myapp:v1     # Load local image
```

### colima

Docker runtime for Mac. Better than Docker Desktop.

```bash
colima start                        # Start
colima start --cpu 4 --memory 8     # With resources
colima stop                         # Stop
```

---

## 🛡️ Optional Tools

Installed if you answer "y" to the prompt.

### argocd

GitOps continuous delivery.

```bash
argocd app list
argocd app sync my-app
```

### popeye

Cluster sanitizer. Finds issues.

```bash
popeye                  # Scan cluster
```

### kubeconform

Validates K8s manifests.

```bash
kubeconform deployment.yaml
```

### dive

Explores Docker image layers.

```bash
dive myimage:tag        # Analyze image
```

---

## 🖥️ VS Code Extensions

| Extension | What It Does |
|-----------|--------------|
| **Cloud Code** | GCP integration, GKE explorer, deploy |
| **Kubernetes** | Cluster explorer, apply manifests |
| **Docker** | Container management |
| **YAML** | K8s schema validation, autocomplete |
| **Terraform** | HCL support, autocomplete |
| **Helm Intellisense** | Chart template support |
| **Remote SSH** | Develop on remote machines |
| **Remote Containers** | Dev containers |
| **REST Client** | Test APIs from VS Code |
| **DotENV** | .env file support |

---

## 🎯 The Stack Summary

| Layer | Tool | Why |
|-------|------|-----|
| Cloud | `gcloud` | Manage GCP |
| K8s UI | `k9s` | **Main tool** — 10x productivity |
| K8s CLI | `kubectl` | Apply manifests, scripting |
| Logs | `stern` | Multi-pod tailing |
| Packages | `helm` | Install complex apps |
| IaC | `terraform` | Version-controlled infra |
| Local | `kind` | Fast test clusters |
| Docker | `colima` | Lightweight runtime |

---

## 💡 Philosophy

1. **K9s-first** — Use the UI, not CLI commands
2. **Minimal tools** — Install what you use daily
3. **Fuzzy selectors** — Never copy-paste names
4. **Lazy completions** — Fast shell startup
5. **No bloat** — Removed 40% of original stack

---

*Lean setup. Maximum power.* ⚡
