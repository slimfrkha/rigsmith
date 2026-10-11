# VS Code Setup (Minimalist Edition)

> Powerful, lean, no bloat.

---

## 📦 Files

| File | Description |
|------|-------------|
| `install-vscode-extensions.sh` | Install core extensions (32) |
| `cleanup-vscode-bloat.sh` | Remove old bloat extensions |
| `settings.json` | Minimal settings |

---

## ⚡ Quick Start

```bash
# If coming from old bloated setup:
./cleanup-vscode-bloat.sh

# Install minimal extensions:
./install-vscode-extensions.sh

# Copy settings:
# Cmd+Shift+P → "Preferences: Open User Settings (JSON)"
# Paste contents of settings.json
```

---

## 🛠️ What's Installed (32 Extensions)

### Theme (2)
- Catppuccin Mocha
- Catppuccin Icons

### Productivity (7)
- ErrorLens (inline errors)
- Todo Tree
- Project Manager
- Path Intellisense
- Advanced New File
- File Utils
- Bookmarks

### IntelliSense (5)
- YAML (K8s essential)
- TOML
- DotENV
- Markdown All-in-One
- Markdown Lint

### Python (7)
- Python
- Debugpy
- Ruff (linter + formatter)
- Ty (type checker)
- Jupyter
- AutoDocstring
- Python Indent

### DevOps & Git (8)
- Docker
- Kubernetes
- Terraform
- Remote Containers
- Remote SSH
- GitLens
- Git Graph
- GitHub PRs

### Visual (2)
- Better Comments
- Rainbow CSV

---

## 📋 Optional (Commented)

Uncomment in script to install:

| Category | Extensions |
|----------|------------|
| Database | MySQL, Postgres, MongoDB, Redis, SQLite |
| Web Dev | ESLint, Prettier, Tailwind, React, Vue |
| API | REST Client |
| AI | Copilot, Continue |
| Languages | Rust, Go, C++ |
| Testing | Coverage Gutters, Draw.io |
| Fun | Pets, Power Mode, Peacock |

---

## ⚙️ Key Settings

| Setting | Value | Why |
|---------|-------|-----|
| `python.languageServer` | `"None"` | Using Ty instead of Pylance |
| `editor.minimap.enabled` | `false` | Clean UI |
| `editor.formatOnSave` | `true` | Auto-format |
| `gitlens.codeLens.enabled` | `false` | Less intrusive |

---

## 🐍 Python Stack (Astral)

| Tool | Replaces | Why |
|------|----------|-----|
| **Ruff** | Black + isort + Flake8 | Faster, single tool |
| **Ty** | Pylance type checking | Lighter, Astral ecosystem |

**Note:** Pylance intentionally excluded. If you need deep IntelliSense, re-enable:
```json
"python.languageServer": "Pylance"
```

---

## 📉 What Was Removed

| Category | Removed |
|----------|---------|
| Themes | 5 redundant themes |
| TODO | Duplicate highlighter |
| Markdown | 4 extra tools |
| Jupyter | 5 extras |
| Python | 3 extras |
| Git | History viewer |
| Visual | 5 extras |
| Fun | Pets, Power Mode, Peacock |

**Result:** ~60% fewer extensions, same power.

---

## 🔗 Font Setup

Install these fonts:
```bash
brew install --cask font-jetbrains-mono
brew install --cask font-meslo-lg-nerd-font
```

Settings expect:
- Editor: JetBrains Mono
- Terminal: MesloLGS NF
