#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║           VS CODE EXTENSIONS (Minimalist Edition)                         ║
# ║                                                                           ║
# ║   Powerful, lean, no bloat. Commented sections available if needed.       ║
# ║                                                                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
cat << 'EOF'
   ╔════════════════════════════════════════════════════════════════╗
   ║     VS Code Extensions (Minimalist Edition)                    ║
   ╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

if ! command -v code &> /dev/null; then
    echo -e "${YELLOW}⚠ 'code' command not found!${NC}"
    echo "VS Code → Cmd+Shift+P → 'Shell Command: Install code command'"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════
# 🎨 THEME (One theme, not seven)
# ═══════════════════════════════════════════════════════════════════════════
THEME=(
    "catppuccin.catppuccin-vsc"              # Theme
    "catppuccin.catppuccin-vsc-icons"        # Matching icons
)

# ═══════════════════════════════════════════════════════════════════════════
# ⚡ CORE PRODUCTIVITY (What you actually use daily)
# ═══════════════════════════════════════════════════════════════════════════
PRODUCTIVITY=(
    "usernamehw.errorlens"                    # Inline errors (ESSENTIAL)
    "Gruntfuggly.todo-tree"                   # Find TODOs
    "alefragnani.project-manager"             # Quick project switching
    "christian-kohler.path-intellisense"      # Path autocomplete
    "patbenatar.advanced-new-file"            # Create files quickly
    "sleistner.vscode-fileutils"              # File operations
    "alefragnani.Bookmarks"                   # Bookmark lines
)

# ═══════════════════════════════════════════════════════════════════════════
# 🧠 INTELLISENSE & CONFIG FILES
# ═══════════════════════════════════════════════════════════════════════════
INTELLISENSE=(
    "redhat.vscode-yaml"                      # YAML (essential for K8s)
    "tamasfe.even-better-toml"                # TOML
    "mikestead.dotenv"                        # .env files
    "yzhang.markdown-all-in-one"              # Markdown (one tool, not five)
    "DavidAnson.vscode-markdownlint"          # Markdown linting
)

# ═══════════════════════════════════════════════════════════════════════════
# 🐍 PYTHON (Astral stack: Ruff + Ty)
# ═══════════════════════════════════════════════════════════════════════════
PYTHON=(
    "ms-python.python"                        # Core Python
    "ms-python.debugpy"                       # Debugger
    "charliermarsh.ruff"                      # Linter + formatter
    "astral-sh.ty"                            # Type checker (replaces Pylance)
    "ms-toolsai.jupyter"                      # Notebooks
    "njpwerner.autodocstring"                 # Docstrings
    "KevinRose.vsc-python-indent"             # Correct indentation
    # NOTE: Pylance excluded - using Ty instead
    # Set "python.languageServer": "None" in settings
)

# ═══════════════════════════════════════════════════════════════════════════
# 🔧 DEVOPS / GIT / REMOTE
# ═══════════════════════════════════════════════════════════════════════════
DEVOPS=(
    "ms-azuretools.vscode-docker"             # Docker
    "ms-kubernetes-tools.vscode-kubernetes-tools" # Kubernetes
    "hashicorp.terraform"                     # Terraform (includes HCL)
    "ms-vscode-remote.remote-containers"      # Dev Containers
    "ms-vscode-remote.remote-ssh"             # Remote SSH
    "eamodio.gitlens"                         # Git supercharged
    "mhutchie.git-graph"                      # Git visualization
    "GitHub.vscode-pull-request-github"       # GitHub PRs
)

# ═══════════════════════════════════════════════════════════════════════════
# 🎯 VISUAL (Minimal, functional only)
# ═══════════════════════════════════════════════════════════════════════════
VISUAL=(
    "aaron-bond.better-comments"              # Comment highlighting
    "mechatroner.rainbow-csv"                 # CSV columns
)

# ═══════════════════════════════════════════════════════════════════════════
# INSTALLATION
# ═══════════════════════════════════════════════════════════════════════════

install_extensions() {
    local category=$1
    shift
    local extensions=("$@")

    echo -e "\n${GREEN}$category${NC}"
    for ext in "${extensions[@]}"; do
        echo -ne "  ${ext}..."
        if code --install-extension "$ext" --force &>/dev/null; then
            echo -e " ${GREEN}✓${NC}"
        else
            echo -e " ${YELLOW}(skipped)${NC}"
        fi
    done
}

# Core install
install_extensions "Theme" "${THEME[@]}"
install_extensions "Productivity" "${PRODUCTIVITY[@]}"
install_extensions "IntelliSense" "${INTELLISENSE[@]}"
install_extensions "Python" "${PYTHON[@]}"
install_extensions "DevOps & Git" "${DEVOPS[@]}"
install_extensions "Visual" "${VISUAL[@]}"

echo -e "\n${GREEN}✓ Core extensions installed (32 total)${NC}"

# ═══════════════════════════════════════════════════════════════════════════
# OPTIONAL: Uncomment sections below and re-run to install
# ═══════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# 🗄️ DATABASE (Heavy - only install if actively using)
# ─────────────────────────────────────────────────────────────────────────────
#DATABASE=(
#    "cweijan.vscode-database-client2"         # Multi-DB client (MySQL, Postgres, etc)
#    "mtxr.sqltools"                           # SQL tools
#    "mtxr.sqltools-driver-pg"                 # PostgreSQL driver
#    "mtxr.sqltools-driver-mysql"              # MySQL driver
#    "mongodb.mongodb-vscode"                  # MongoDB
#    "redis.redis-for-vscode"                  # Redis
#    "qwtel.sqlite-viewer"                     # SQLite viewer
#)
#install_extensions "Database" "${DATABASE[@]}"

# ─────────────────────────────────────────────────────────────────────────────
# 🌐 WEB DEVELOPMENT (JS/TS/React/Vue/etc)
# ─────────────────────────────────────────────────────────────────────────────
#WEBDEV=(
#    "dbaeumer.vscode-eslint"                  # ESLint
#    "esbenp.prettier-vscode"                  # Prettier formatter
#    "bradlc.vscode-tailwindcss"               # Tailwind CSS
#    "formulahendry.auto-rename-tag"           # Auto rename HTML tags
#    "formulahendry.auto-close-tag"            # Auto close HTML tags
#    "naumovs.color-highlight"                 # Highlight colors
#    "pranaygp.vscode-css-peek"                # CSS peek
#    "dsznajder.es7-react-js-snippets"         # React snippets
#    "Vue.volar"                               # Vue 3
#    "svelte.svelte-vscode"                    # Svelte
#)
#install_extensions "Web Development" "${WEBDEV[@]}"

# ─────────────────────────────────────────────────────────────────────────────
# 🔌 API TESTING
# ─────────────────────────────────────────────────────────────────────────────
#API=(
#    "humao.rest-client"                       # REST client (like Postman in VS Code)
#)
#install_extensions "API Testing" "${API[@]}"

# ─────────────────────────────────────────────────────────────────────────────
# 🤖 AI ASSISTANTS
# ─────────────────────────────────────────────────────────────────────────────
#AI=(
#    "GitHub.copilot"                          # GitHub Copilot
#    "GitHub.copilot-chat"                     # Copilot Chat
#    "Continue.continue"                       # Open-source AI assistant
#)
#install_extensions "AI Assistants" "${AI[@]}"

# ─────────────────────────────────────────────────────────────────────────────
# 🎯 OTHER LANGUAGES
# ─────────────────────────────────────────────────────────────────────────────
#LANGUAGES=(
#    "rust-lang.rust-analyzer"                 # Rust
#    "golang.go"                               # Go
#    "ms-vscode.cpptools"                      # C/C++
#)
#install_extensions "Languages" "${LANGUAGES[@]}"

# ─────────────────────────────────────────────────────────────────────────────
# 🧪 TESTING & DEBUGGING
# ─────────────────────────────────────────────────────────────────────────────
#TESTING=(
#    "ryanluker.vscode-coverage-gutters"       # Code coverage in gutter
#    "ms-vscode.test-adapter-converter"        # Test adapter
#    "hediet.vscode-drawio"                    # Draw.io diagrams
#    "hediet.debug-visualizer"                 # Visualize data while debugging
#)
#install_extensions "Testing" "${TESTING[@]}"

# ─────────────────────────────────────────────────────────────────────────────
# 📝 EXTRA MARKDOWN & DOCS
# ─────────────────────────────────────────────────────────────────────────────
#MARKDOWN_EXTRA=(
#    "shd101wyy.markdown-preview-enhanced"     # Enhanced preview
#    "bierner.markdown-mermaid"                # Mermaid diagrams
#    "bierner.markdown-emoji"                  # Emoji support
#    "mushan.vscode-paste-image"               # Paste images
#)
#install_extensions "Markdown Extra" "${MARKDOWN_EXTRA[@]}"

# ─────────────────────────────────────────────────────────────────────────────
# 🎮 FUN (Focus killers - think twice)
# ─────────────────────────────────────────────────────────────────────────────
#FUN=(
#    "tonybaloney.vscode-pets"                 # Pets in editor
#    "hoovercj.vscode-power-mode"              # Explosions while typing
#    "johnpapa.vscode-peacock"                 # Color-coded workspaces
#)
#install_extensions "Fun" "${FUN[@]}"

# ─────────────────────────────────────────────────────────────────────────────
# 📊 EXTRA VISUAL
# ─────────────────────────────────────────────────────────────────────────────
#VISUAL_EXTRA=(
#    "oderwat.indent-rainbow"                  # Colorful indentation
#    "IBM.output-colorizer"                    # Colorize output panel
#    "kisstkondansen.vscode-gutter-preview"    # Image preview in gutter
#)
#install_extensions "Visual Extra" "${VISUAL_EXTRA[@]}"

# ─────────────────────────────────────────────────────────────────────────────
# 🔗 COLLABORATION
# ─────────────────────────────────────────────────────────────────────────────
#COLLAB=(
#    "ms-vsliveshare.vsliveshare"              # Real-time collaborative coding
#)
#install_extensions "Collaboration" "${COLLAB[@]}"

# ═══════════════════════════════════════════════════════════════════════════

echo -e "\n${GREEN}"
cat << 'EOF'
   ╔════════════════════════════════════════════════════════════════╗
   ║   ✓ Done! Restart VS Code.                                     ║
   ║                                                                ║
   ║   To install optional extensions:                              ║
   ║   1. Edit this script                                          ║
   ║   2. Uncomment the section you want                            ║
   ║   3. Run again                                                 ║
   ╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
