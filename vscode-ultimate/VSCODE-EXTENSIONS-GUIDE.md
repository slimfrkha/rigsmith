# VS Code Extensions Guide (Minimalist Edition)

> **32 core extensions** — powerful, lean, no bloat.

---

## 📋 Table of Contents

1. [🎨 Theme](#-theme)
2. [⚡ Productivity](#-productivity)
3. [🐍 Python](#-python)
4. [🔧 DevOps & Git](#-devops--git)
5. [📝 Config Files](#-config-files)
6. [✨ Visual](#-visual)
7. [📦 Optional Categories](#-optional-categories)
8. [⚙️ Settings](#-settings)
9. [⌨️ Shortcuts](#-shortcuts)

---

## 🎨 Theme

| Extension | Description |
|-----------|-------------|
| **[Catppuccin](https://marketplace.visualstudio.com/items?itemName=catppuccin.catppuccin-vsc)** | Beautiful pastel theme (use "Mocha") |
| **[Catppuccin Icons](https://marketplace.visualstudio.com/items?itemName=catppuccin.catppuccin-vsc-icons)** | Matching file icons |

**Font:** [JetBrains Mono](https://www.jetbrains.com/lp/mono/) with ligatures

---

## ⚡ Productivity

### 🔴 Essential

| Extension | What It Does | Why You Need It |
|-----------|--------------|-----------------|
| **[Error Lens](https://marketplace.visualstudio.com/items?itemName=usernamehw.errorlens)** | Shows errors inline | See errors WITHOUT hovering |
| **[TODO Tree](https://marketplace.visualstudio.com/items?itemName=Gruntfuggly.todo-tree)** | Find all TODOs | Sidebar with all tasks |
| **[Project Manager](https://marketplace.visualstudio.com/items?itemName=alefragnani.project-manager)** | Quick project switching | `Cmd+Alt+P` to switch |
| **[Path Intellisense](https://marketplace.visualstudio.com/items?itemName=christian-kohler.path-intellisense)** | Autocomplete paths | Never mistype imports |
| **[Bookmarks](https://marketplace.visualstudio.com/items?itemName=alefragnani.Bookmarks)** | Bookmark lines | `Cmd+Alt+K` to toggle |

### File Management

| Extension | What It Does |
|-----------|--------------|
| **[Advanced New File](https://marketplace.visualstudio.com/items?itemName=patbenatar.advanced-new-file)** | Create files anywhere with `Cmd+Alt+N` |
| **[File Utils](https://marketplace.visualstudio.com/items?itemName=sleistner.vscode-fileutils)** | Rename, move, duplicate files |

---

## 🐍 Python

### The Astral Stack

Modern, all-Rust Python toolchain:

| Tool | Role | Replaces |
|------|------|----------|
| **[Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)** | Linting + Formatting | Flake8, Black, isort |
| **[Ty](https://marketplace.visualstudio.com/items?itemName=astral-sh.ty)** | Type checking | Pylance type checking |

### Full Stack

| Extension | Priority |
|-----------|----------|
| **[Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)** | 🔴 Required |
| **[Debugpy](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy)** | 🔴 Debugging |
| **[Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)** | 🔴 Lint + format |
| **[Ty](https://marketplace.visualstudio.com/items?itemName=astral-sh.ty)** | 🔴 Type checking |
| **[Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)** | 🟡 Notebooks |
| **[autoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring)** | 🟢 Docstrings |
| **[Python Indent](https://marketplace.visualstudio.com/items?itemName=KevinRose.vsc-python-indent)** | 🟢 Indentation |

> **Note:** Pylance excluded — Ty replaces its type checking. Set `"python.languageServer": "None"`.

### Python Settings

```json
{
  "python.languageServer": "None",
  "ruff.enable": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  }
}
```

---

## 🔧 DevOps & Git

### Git

| Extension | What It Does |
|-----------|--------------|
| **[GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)** | 🏆 Blame, history, compare |
| **[Git Graph](https://marketplace.visualstudio.com/items?itemName=mhutchie.git-graph)** | Visual commit graph |
| **[GitHub PRs](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-pull-request-github)** | Review PRs in VS Code |

### Containers & Cloud

| Extension | What It Does |
|-----------|--------------|
| **[Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)** | Docker support |
| **[Kubernetes](https://marketplace.visualstudio.com/items?itemName=ms-kubernetes-tools.vscode-kubernetes-tools)** | K8s support |
| **[Terraform](https://marketplace.visualstudio.com/items?itemName=hashicorp.terraform)** | HCL support |

### Remote

| Extension | What It Does |
|-----------|--------------|
| **[Remote SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)** | Edit on remote machines |
| **[Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)** | Develop inside containers |

---

## 📝 Config Files

| Extension | What It Does |
|-----------|--------------|
| **[YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)** | YAML with K8s schemas |
| **[Even Better TOML](https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml)** | TOML support |
| **[DotENV](https://marketplace.visualstudio.com/items?itemName=mikestead.dotenv)** | .env files |
| **[Markdown All in One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one)** | Markdown editing |
| **[markdownlint](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)** | Markdown linting |

---

## ✨ Visual

| Extension | What It Does |
|-----------|--------------|
| **[Better Comments](https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments)** | Color-coded comments |
| **[Rainbow CSV](https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv)** | Color CSV columns |

---

## 📦 Optional Categories

Uncomment in install script to add these.

### 🗄️ Database

| Extension | Description |
|-----------|-------------|
| Database Client | MySQL, Postgres, SQLite, etc. |
| SQLTools + drivers | Alternative DB client |
| MongoDB | MongoDB support |
| Redis | Redis support |

### 🌐 Web Development

| Extension | Description |
|-----------|-------------|
| ESLint | JS/TS linting |
| Prettier | Code formatting |
| Tailwind CSS | Tailwind autocomplete |
| Auto Rename Tag | Rename HTML tags |
| React Snippets | React/JSX snippets |
| Volar | Vue 3 |
| Svelte | Svelte |

### 🔌 API Testing

| Extension | Description |
|-----------|-------------|
| REST Client | HTTP requests from .http files |

### 🤖 AI

| Extension | Description |
|-----------|-------------|
| GitHub Copilot | AI pair programmer ($10/mo) |
| Copilot Chat | Chat with Copilot |
| Continue | Open-source, local models |

### 🎯 Languages

| Extension | Language |
|-----------|----------|
| rust-analyzer | Rust |
| Go | Go |
| C/C++ | C/C++ |

### 🧪 Testing

| Extension | Description |
|-----------|-------------|
| Coverage Gutters | Show code coverage |
| Draw.io | Diagrams |

---

## ⚙️ Settings

Core settings (see `settings.json` for full config):

```json
{
  "workbench.colorTheme": "Catppuccin Mocha",
  "workbench.iconTheme": "catppuccin-mocha",
  "editor.fontFamily": "JetBrains Mono",
  "editor.fontSize": 14,
  "editor.fontLigatures": true,
  "editor.minimap.enabled": false,
  "editor.formatOnSave": true,
  "editor.smoothScrolling": true,
  "files.autoSave": "onFocusChange",
  "terminal.integrated.fontFamily": "MesloLGS NF",
  "gitlens.codeLens.enabled": false,
  "errorLens.enabledDiagnosticLevels": ["error", "warning"],
  "telemetry.telemetryLevel": "off"
}
```

---

## ⌨️ Shortcuts

### Navigation

| Shortcut | Action |
|----------|--------|
| `Cmd+P` | Quick file open |
| `Cmd+Shift+P` | Command palette |
| `Cmd+Shift+F` | Search in files |
| `Cmd+B` | Toggle sidebar |
| `Cmd+J` | Toggle terminal |
| `Ctrl+\`` | Focus terminal |

### Editing

| Shortcut | Action |
|----------|--------|
| `Cmd+D` | Select next occurrence |
| `Cmd+Shift+L` | Select all occurrences |
| `Alt+↑/↓` | Move line |
| `Shift+Alt+↑/↓` | Copy line |
| `Cmd+/` | Toggle comment |
| `Shift+Alt+F` | Format document |
| `Cmd+.` | Quick fix |
| `F2` | Rename symbol |
| `F12` | Go to definition |

### Extensions

| Shortcut | Action |
|----------|--------|
| `Cmd+Alt+N` | Advanced New File |
| `Cmd+Alt+P` | Project Manager |
| `Cmd+Alt+K` | Toggle bookmark |

---

## 🚀 Quick Install

```bash
./install-vscode-extensions.sh
```

---

## 📋 The 32 Core Extensions

1. Catppuccin + Icons
2. Error Lens
3. TODO Tree
4. Project Manager
5. Path Intellisense
6. Bookmarks
7. Advanced New File
8. File Utils
9. Python + Debugpy
10. Ruff
11. Ty
12. Jupyter
13. autoDocstring
14. Python Indent
15. GitLens
16. Git Graph
17. GitHub PRs
18. Docker
19. Kubernetes
20. Terraform
21. Remote SSH
22. Dev Containers
23. YAML
24. TOML
25. DotENV
26. Markdown All in One
27. markdownlint
28. Better Comments
29. Rainbow CSV

**32 extensions. Zero bloat.**
