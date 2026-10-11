# VS Code Extensions Explained

> What each core extension does and how to use it.

---

## 🎨 Theme

### Catppuccin

Beautiful pastel theme with multiple flavors.

**Setup:**
1. Install extension
2. `Cmd+K Cmd+T` → Select "Catppuccin Mocha"
3. Install "Catppuccin Icons" for matching file icons

---

## ⚡ Productivity

### Error Lens

Shows errors and warnings inline — no hovering required.

**Why it's essential:** See errors instantly as you type, color-coded by severity.

**Example:**
```python
def foo(x)    # ← Missing colon — Error: expected ':'
    return x
```

**Settings:**
```json
"errorLens.enabledDiagnosticLevels": ["error", "warning"]
```

---

### GitLens

Git superpowers — blame, history, comparison.

**Key features:**
- Inline blame (hover any line)
- File history (right-click → "Open File History")
- Commit graph (`>GitLens: Show Commit Graph`)
- Compare branches (`>GitLens: Compare with...`)

**Settings:**
```json
"gitlens.codeLens.enabled": false,
"gitlens.currentLine.enabled": true
```

---

### Git Graph

Visual git history like GitKraken/SourceTree.

**Usage:** Click "Git Graph" in source control panel or `>Git Graph: View Git Graph`

---

### Project Manager

Save and switch between projects instantly.

**Usage:**
- Save: `>Project Manager: Save Project`
- Switch: `Cmd+Alt+P`
- Edit list: `>Project Manager: Edit Projects`

---

### TODO Tree

Finds all TODO/FIXME/BUG comments in your project.

**Tags it finds:**
```
TODO:    — Something to do
FIXME:   — Needs fixing
BUG:     — Known bug
HACK:    — Workaround
NOTE:    — Important info
```

**Usage:** Click tree icon in sidebar

---

### Bookmarks

Mark lines to jump back to.

**Shortcuts:**
- Toggle: `Cmd+Alt+K`
- Next: `Cmd+Alt+L`
- Previous: `Cmd+Alt+J`
- List all: `>Bookmarks: List`

---

### Path Intellisense

Autocompletes file paths as you type.

**Usage:** Just type a path in quotes — suggestions appear automatically.

---

### Advanced New File

Create files anywhere with one command.

**Usage:** `Cmd+Alt+N` → Type `src/components/Button/index.tsx` → Creates file AND folders.

---

### File Utils

Rename, move, duplicate files from command palette.

**Usage:** `>File: Rename` / `>File: Move` / `>File: Duplicate`

---

## 🐍 Python

### The Astral Stack

Modern Python tooling from [Astral](https://astral.sh):

| Tool | Role | Speed |
|------|------|-------|
| **Ruff** | Lint + Format | 10-100x faster than Black/Flake8 |
| **Ty** | Type checking | Faster than Pylance |

**Why this setup:**
- Single config (`pyproject.toml`)
- Ruff replaces Black, Flake8, isort
- Ty replaces Pylance type checking
- All Rust = blazing fast

---

### Ruff

Linter AND formatter in one.

**Usage:**
- Format on save (automatic with settings)
- Fix issues: `>Ruff: Fix all auto-fixable problems`
- Organize imports: `>Ruff: Organize Imports`

**Config (pyproject.toml):**
```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I", "UP"]
```

---

### Ty

Type checker from Astral.

**Setup:**
1. Install Ty extension
2. Disable Pylance: `"python.languageServer": "None"`
3. Ty runs automatically

---

### Jupyter

Notebooks inside VS Code.

**Shortcuts:**
- `Shift+Enter` — Run cell, move next
- `Cmd+Enter` — Run cell, stay
- `A` — Insert above (command mode)
- `B` — Insert below (command mode)
- `DD` — Delete cell (command mode)

---

### autoDocstring

Generate docstrings for functions.

**Usage:** Inside function, type `"""` + Enter

---

## 🔧 DevOps

### Docker

Build, run, manage containers from VS Code.

**Commands:**
- `>Docker: Add Docker Files`
- `>Docker: Build Image`
- `>Docker: Compose Up`
- `>Docker: Attach Shell`

---

### Remote SSH

Edit files on remote machines as if local.

**Setup:**
1. `>Remote-SSH: Add New SSH Host`
2. Enter `ssh user@hostname`
3. `>Remote-SSH: Connect to Host`

Everything works remotely — terminal, debugging, extensions.

---

### Dev Containers

Develop inside Docker containers.

**Usage:**
1. `>Dev Containers: Add Dev Container Config`
2. Choose template
3. `>Dev Containers: Reopen in Container`

---

## 📝 Config Files

### YAML (Red Hat)

YAML support with Kubernetes schema validation.

**Settings:**
```json
"[yaml]": {
  "editor.defaultFormatter": "redhat.vscode-yaml",
  "editor.tabSize": 2
}
```

---

### Markdown All in One

Swiss Army knife for Markdown.

**Features:**
- Preview: `Cmd+Shift+V`
- Side preview: `Cmd+K V`
- Generate TOC: `>Markdown All in One: Create Table of Contents`
- Bold: `Cmd+B`
- Italic: `Cmd+I`

---

## ✨ Visual

### Better Comments

Color-coded comments:

```python
# ! Alert (red)
# ? Question (blue)
# TODO: Task (orange)
# * Important (purple)
```

---

### Rainbow CSV

Color-codes CSV columns for readability.

**Usage:** Open CSV — colors appear automatically.

---

## 📦 Optional Extensions

These are commented in the install script. Uncomment to add.

### Database (Heavy — ~200MB)

| Extension | Use Case |
|-----------|----------|
| Database Client | Multi-DB GUI |
| SQLTools | SQL queries |
| MongoDB | MongoDB |
| Redis | Redis |

### Web Development

| Extension | Use Case |
|-----------|----------|
| ESLint | JS/TS linting |
| Prettier | Formatting |
| Tailwind CSS | Class autocomplete |
| Auto Rename Tag | HTML editing |
| React Snippets | React/JSX |
| Volar | Vue 3 |

### REST Client

Send HTTP requests from `.http` files:

```http
### Get users
GET https://api.example.com/users
Authorization: Bearer {{token}}

### Create user
POST https://api.example.com/users
Content-Type: application/json

{
    "name": "John"
}
```

Click "Send Request" above each request.

### AI Assistants

| Extension | Cost |
|-----------|------|
| GitHub Copilot | $10/mo |
| Copilot Chat | Included |
| Continue | Free (local models) |

---

## 🎯 Summary: Install Priority

### Always Install (Core 32)
- Error Lens, GitLens, Project Manager, TODO Tree
- Python + Ruff + Ty + Jupyter
- Docker, Kubernetes, Terraform
- Remote SSH, Dev Containers
- YAML, Markdown

### Install If Needed
- Database tools (if using DBs daily)
- Web dev (ESLint, Prettier, Tailwind)
- AI (Copilot, Continue)
- Language-specific (Rust, Go, C++)

### Skip Unless You Really Want
- Multiple themes (pick one)
- Fun extensions (Pets, Power Mode)
- Redundant tools

---

**32 extensions. Maximum power. Zero bloat.**
