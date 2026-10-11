# VS Code Command Palette Cheatsheet

> **Press `Cmd+Shift+P`** and type these commands.

---

## 🎯 Most Used

| Command | Shortcut | Action |
|---------|----------|--------|
| Quick Open | `Cmd+P` | Find file |
| Command Palette | `Cmd+Shift+P` | This menu |
| Go to Symbol | `Cmd+Shift+O` | Symbols in file |
| Go to Line | `Ctrl+G` | Jump to line |
| Search Files | `Cmd+Shift+F` | Search all files |
| Toggle Terminal | `` Ctrl+` `` | Show/hide terminal |
| Toggle Sidebar | `Cmd+B` | Show/hide sidebar |
| Format Document | `Shift+Alt+F` | Format file |
| Quick Fix | `Cmd+.` | Fix problems |
| Rename | `F2` | Rename symbol |

---

## 🔧 Core VS Code

| Command | Action |
|---------|--------|
| `>Reload Window` | Restart VS Code |
| `>Open Settings (JSON)` | Edit settings.json |
| `>Preferences: Color Theme` | Change theme |
| `>Preferences: File Icon Theme` | Change icons |
| `>Shell Command: Install 'code'` | Enable `code` in terminal |

---

## 🌿 Git

### Core Git

| Command | Action |
|---------|--------|
| `>Git: Clone` | Clone repo |
| `>Git: Checkout to...` | Switch branch |
| `>Git: Create Branch` | New branch |
| `>Git: Pull` | Pull |
| `>Git: Push` | Push |
| `>Git: Commit` | Commit |
| `>Git: Stage All` | Stage everything |
| `>Git: Undo Last Commit` | Undo commit (keep changes) |
| `>Git: Stash` | Stash changes |

### GitLens

| Command | Action |
|---------|--------|
| `>GitLens: Open File History` | All commits for file |
| `>GitLens: Show Commit Graph` | Visual graph |
| `>GitLens: Compare with...` | Compare branches |
| `>GitLens: Toggle File Blame` | Toggle blame |

### Git Graph

| Command | Action |
|---------|--------|
| `>Git Graph: View Git Graph` | Open visual graph |

---

## 🐍 Python

### Python

| Command | Action |
|---------|--------|
| `>Python: Select Interpreter` | Choose Python/venv |
| `>Python: Create Environment` | Create venv |
| `>Python: Run Python File` | Run file |
| `>Python: Start REPL` | Open REPL |
| `>Python: Configure Tests` | Setup pytest |

### Ruff

| Command | Action |
|---------|--------|
| `>Ruff: Fix all auto-fixable problems` | Auto-fix |
| `>Ruff: Format Document` | Format |
| `>Ruff: Organize Imports` | Sort imports |

### Jupyter

| Command | Action |
|---------|--------|
| `>Jupyter: Create New Notebook` | New .ipynb |
| `>Jupyter: Run All Cells` | Run all |
| `>Jupyter: Run Cell` | Run current (`Shift+Enter`) |
| `>Jupyter: Restart Kernel` | Restart |
| `>Jupyter: Clear All Outputs` | Clear outputs |
| `>Jupyter: Select Kernel` | Choose kernel |

---

## 📁 Files & Projects

### File Utils

| Command | Action |
|---------|--------|
| `>File: Rename` | Rename file |
| `>File: Move` | Move file |
| `>File: Duplicate` | Duplicate file |
| `>File: Copy Path` | Copy path |

### Advanced New File

| Command | Shortcut |
|---------|----------|
| `>Advanced New File` | `Cmd+Alt+N` |

### Project Manager

| Command | Shortcut |
|---------|----------|
| `>Project Manager: List Projects` | `Cmd+Alt+P` |
| `>Project Manager: Save Project` | — |

### Bookmarks

| Command | Shortcut |
|---------|----------|
| `>Bookmarks: Toggle` | `Cmd+Alt+K` |
| `>Bookmarks: List` | — |
| `>Bookmarks: Jump to Next` | `Cmd+Alt+L` |

---

## 🔍 Search

| Command | Action |
|---------|--------|
| `>Go to File...` | Quick open (`Cmd+P`) |
| `>Go to Symbol in Workspace` | Find symbol (`Cmd+T`) |
| `>Go to Definition` | Jump to def (`F12`) |
| `>Go to References` | Find refs (`Shift+F12`) |

### TODO Tree

| Command | Action |
|---------|--------|
| `>Todo Tree: Show Tree` | Open sidebar |
| `>Todo Tree: Refresh` | Refresh TODOs |

---

## 🎨 Formatting

| Command | Action |
|---------|--------|
| `>Format Document` | Format file |
| `>Format Selection` | Format selection |
| `>Organize Imports` | Sort imports |

---

## 🐳 Docker & Remote

### Docker

| Command | Action |
|---------|--------|
| `>Docker: Add Docker Files` | Add Dockerfile |
| `>Docker: Build Image` | Build |
| `>Docker: Compose Up` | docker-compose up |
| `>Docker: Compose Down` | docker-compose down |
| `>Docker: Attach Shell` | Shell into container |

### Remote SSH

| Command | Action |
|---------|--------|
| `>Remote-SSH: Connect to Host` | Connect |
| `>Remote-SSH: Add New SSH Host` | Add host |

### Dev Containers

| Command | Action |
|---------|--------|
| `>Dev Containers: Reopen in Container` | Open in container |
| `>Dev Containers: Rebuild Container` | Rebuild |

---

## 📝 Markdown

| Command | Action |
|---------|--------|
| `>Markdown: Open Preview` | Preview (`Cmd+Shift+V`) |
| `>Markdown: Open Preview to Side` | Side preview (`Cmd+K V`) |
| `>Markdown All in One: Create Table of Contents` | Generate TOC |

---

## 🧪 Testing

| Command | Action |
|---------|--------|
| `>Test: Run All Tests` | Run all |
| `>Test: Run Test at Cursor` | Run current |
| `>Test: Debug Test at Cursor` | Debug test |

---

## 🎨 View

| Command | Action |
|---------|--------|
| `>View: Toggle Minimap` | Show/hide minimap |
| `>View: Toggle Zen Mode` | Distraction-free |
| `>View: Toggle Panel` | Show/hide bottom panel |

---

## 💡 Tips

1. **Fuzzy matching works** — type `"gitcom"` finds `"Git: Commit"`

2. **Recently used** commands appear at top

3. **In Quick Open (`Cmd+P`):**
   - `@` — go to symbol
   - `:` — go to line
   - `>` — run command
   - `#` — search workspace symbols

---

## ⚡ Quick Reference Card

```
Cmd+P           → Find file
Cmd+Shift+P     → Commands
Cmd+Shift+F     → Search all
Cmd+Shift+O     → Symbols
Ctrl+G          → Go to line
Cmd+B           → Sidebar
Cmd+J           → Terminal
Shift+Alt+F     → Format
Cmd+.           → Quick fix
F2              → Rename
F12             → Definition
Shift+F12       → References
Cmd+D           → Select next
Cmd+/           → Comment
```
