#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║           🚀 ULTIMATE MAC TERMINAL SETUP - FRESH INSTALL 🚀              ║
# ║                                                                           ║
# ║   Run this on a brand new Mac to get the perfect terminal setup!         ║
# ║                                                                           ║
# ║   Usage:                                                                  ║
# ║     chmod +x install-ultimate-terminal.sh                                 ║
# ║     ./install-ultimate-terminal.sh                                        ║
# ║                                                                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}▶ $1${NC}"
}

print_info() {
    echo -e "${BLUE}  ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}  ⚠ $1${NC}"
}

print_success() {
    echo -e "${GREEN}  ✓ $1${NC}"
}

# ═══════════════════════════════════════════════════════════════════════════
# PRE-FLIGHT CHECK
# ═══════════════════════════════════════════════════════════════════════════
print_header "🛫 PRE-FLIGHT CHECK"

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${RED}❌ This script is designed for macOS only!${NC}"
    exit 1
fi
print_success "Running on macOS"

# Check for Xcode Command Line Tools
if ! xcode-select -p &> /dev/null; then
    print_step "Installing Xcode Command Line Tools..."
    xcode-select --install
    echo -e "${YELLOW}  Please complete the Xcode installation and run this script again.${NC}"
    exit 0
else
    print_success "Xcode Command Line Tools installed"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: HOMEBREW
# ═══════════════════════════════════════════════════════════════════════════
print_header "📦 STEP 1: Installing Homebrew"

if ! command -v brew &> /dev/null; then
    print_step "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    print_success "Homebrew installed!"
else
    print_success "Homebrew already installed"
fi

# Update Homebrew
print_step "Updating Homebrew..."
brew update

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: INSTALL iTERM2
# ═══════════════════════════════════════════════════════════════════════════
print_header "💻 STEP 2: Installing iTerm2"

if ! brew list --cask iterm2 &> /dev/null; then
    print_step "Installing iTerm2..."
    brew install --cask iterm2
    print_success "iTerm2 installed!"
else
    print_success "iTerm2 already installed"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: INSTALL NERD FONTS (Required for icons!)
# ═══════════════════════════════════════════════════════════════════════════
print_header "🔤 STEP 3: Installing Nerd Fonts"

print_step "Installing MesloLGS Nerd Font (recommended)..."
brew install --cask font-meslo-lg-nerd-font 2>/dev/null || print_warning "Font may already be installed"

print_step "Installing JetBrains Mono Nerd Font..."
brew install --cask font-jetbrains-mono-nerd-font 2>/dev/null || print_warning "Font may already be installed"

print_step "Installing FiraCode Nerd Font..."
brew install --cask font-fira-code-nerd-font 2>/dev/null || print_warning "Font may already be installed"

print_info "⚡ IMPORTANT: After installation, set your iTerm font to 'MesloLGS NF'"
print_info "   Go to: iTerm → Settings → Profiles → Text → Font"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: INSTALL OH MY ZSH
# ═══════════════════════════════════════════════════════════════════════════
print_header "🐚 STEP 4: Installing Oh My Zsh"

if [ ! -d "$HOME/.oh-my-zsh" ]; then
    print_step "Installing Oh My Zsh..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    print_success "Oh My Zsh installed!"
else
    print_success "Oh My Zsh already installed"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: INSTALL POWERLEVEL10K
# ═══════════════════════════════════════════════════════════════════════════
print_header "⚡ STEP 5: Installing Powerlevel10k"

P10K_DIR="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k"
if [ ! -d "$P10K_DIR" ]; then
    print_step "Cloning Powerlevel10k..."
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$P10K_DIR"
    print_success "Powerlevel10k installed!"
else
    print_success "Powerlevel10k already installed"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 6: INSTALL ZPLUG (Plugin Manager)
# ═══════════════════════════════════════════════════════════════════════════
print_header "🔌 STEP 6: Installing zinit"

print_step "Installing zinit..."
brew install zinit 2>/dev/null || print_warning "zinit may already be installed"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 7: INSTALL CLI TOOLS
# ═══════════════════════════════════════════════════════════════════════════
print_header "🛠️ STEP 7: Installing CLI Power Tools"

# Core replacements for standard tools
CORE_TOOLS=(
    "eza"               # Modern ls replacement with icons & git integration
    "bat"               # Cat clone with syntax highlighting
    "ripgrep"           # Blazingly fast grep alternative (rg)
    "fd"                # Simple, fast find alternative
    "sd"                # Intuitive sed alternative
    "fzf"               # THE fuzzy finder
    "zoxide"            # Smarter cd that learns your habits
)

# System monitoring tools
MONITOR_TOOLS=(
    "bottom"            # Beautiful system monitor (btm command)
    "htop"              # Classic system monitor
    "dust"              # More intuitive du (disk usage)
    "duf"               # Better df (disk free)
    "procs"             # Modern ps replacement
)

# Git tools
GIT_TOOLS=(
    "git"               # Git itself
    "lazygit"           # Beautiful terminal git UI
    "git-delta"         # Beautiful git diffs
    "gh"                # GitHub CLI
)

# File management
FILE_TOOLS=(
    "yazi"              # Blazing fast terminal file manager
    "tree"              # Directory tree viewer
)

# JSON & data tools
DATA_TOOLS=(
    "jq"                # JSON processor
    "yq"                # YAML processor
)

# Productivity tools
PRODUCTIVITY_TOOLS=(
    "thefuck"           # Auto-correct previous command
    "atuin"             # Magical shell history search
    "tldr"              # Simplified man pages
    "watch"             # Execute command periodically
)

# Editor
EDITOR_TOOLS=(
    "micro"             # Modern terminal editor (nano replacement)
)

# Networking
NETWORK_TOOLS=(
    "httpie"            # User-friendly HTTP client
    "curl"              # URL transfer tool
    "wget"              # File downloader
)

# Fun stuff
FUN_TOOLS=(
    "fastfetch"         # Faster neofetch alternative
    "figlet"            # ASCII text banners
    "lolcat"            # Rainbow colors for output
    "cowsay"            # Fun ASCII cow messages
    "cmatrix"           # Matrix-style animation
    "pipes-sh"          # Animated pipes screensaver
    "sl"                # Steam locomotive (punishment for typos!)
)

# Development tools (optional but useful)
DEV_TOOLS=(
    "node"              # Node.js
    "python"            # Python 3
    "uv"                # Fast Python package manager
    "tokei"             # Code statistics
    "hyperfine"         # Benchmarking tool
)

# Install all tools
ALL_TOOLS=(
    "${CORE_TOOLS[@]}"
    "${MONITOR_TOOLS[@]}"
    "${GIT_TOOLS[@]}"
    "${FILE_TOOLS[@]}"
    "${DATA_TOOLS[@]}"
    "${PRODUCTIVITY_TOOLS[@]}"
    "${EDITOR_TOOLS[@]}"
    "${NETWORK_TOOLS[@]}"
    "${FUN_TOOLS[@]}"
    "${DEV_TOOLS[@]}"
)

print_step "Installing ${#ALL_TOOLS[@]} tools (this may take a few minutes)..."
for tool in "${ALL_TOOLS[@]}"; do
    echo -ne "  Installing ${BLUE}$tool${NC}..."
    if brew install "$tool" &>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${YELLOW}(skipped)${NC}"
    fi
done

# ═══════════════════════════════════════════════════════════════════════════
# STEP 8: CONFIGURE FZF
# ═══════════════════════════════════════════════════════════════════════════
print_header "🔍 STEP 8: Configuring FZF"

print_step "Installing fzf key bindings and completions..."
$(brew --prefix)/opt/fzf/install --all --no-bash --no-fish 2>/dev/null || true
print_success "FZF configured!"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 9: CONFIGURE GIT DELTA
# ═══════════════════════════════════════════════════════════════════════════
print_header "🎨 STEP 9: Configuring Git Delta"

print_step "Setting up beautiful git diffs..."
git config --global core.pager delta
git config --global interactive.diffFilter "delta --color-only"
git config --global delta.navigate true
git config --global delta.light false
git config --global delta.side-by-side true
git config --global delta.line-numbers true
git config --global delta.syntax-theme "Catppuccin-mocha"
print_success "Git delta configured!"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 10: IMPORT SHELL HISTORY TO ATUIN
# ═══════════════════════════════════════════════════════════════════════════
print_header "📜 STEP 10: Setting Up Atuin"

print_step "Initializing Atuin..."
if command -v atuin &> /dev/null; then
    # Initialize atuin if not already done
    if [ ! -d "$HOME/.local/share/atuin" ]; then
        atuin init zsh > /dev/null 2>&1 || true
    fi

    # Import existing history
    print_step "Importing existing shell history..."
    atuin import auto 2>/dev/null || atuin import zsh 2>/dev/null || print_warning "No history to import yet"
    print_success "Atuin ready!"
else
    print_warning "Atuin not found, skipping..."
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 11: BACKUP EXISTING ZSHRC
# ═══════════════════════════════════════════════════════════════════════════
print_header "💾 STEP 11: Backing Up Existing Config"

if [ -f "$HOME/.zshrc" ]; then
    BACKUP_FILE="$HOME/.zshrc.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$HOME/.zshrc" "$BACKUP_FILE"
    print_success "Existing .zshrc backed up to: $BACKUP_FILE"
else
    print_info "No existing .zshrc found"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 12: INSTALL NEW ZSHRC
# ═══════════════════════════════════════════════════════════════════════════
print_header "📝 STEP 12: Installing New Configuration"

# Check if the zshrc file exists in the same directory as this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "$SCRIPT_DIR/ultimate-zshrc" ]; then
    cp "$SCRIPT_DIR/ultimate-zshrc" "$HOME/.zshrc"
    print_success "New .zshrc installed!"
else
    print_warning "ultimate-zshrc not found in $SCRIPT_DIR"
    print_info "Please manually copy ultimate-zshrc to ~/.zshrc"
fi

# Copy iTerm color scheme if it exists
if [ -f "$SCRIPT_DIR/Catppuccin-Mocha.itermcolors" ]; then
    mkdir -p "$HOME/.config/iterm2"
    cp "$SCRIPT_DIR/Catppuccin-Mocha.itermcolors" "$HOME/.config/iterm2/"
    print_success "Color scheme copied to ~/.config/iterm2/"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 13: CREATE USEFUL DIRECTORIES
# ═══════════════════════════════════════════════════════════════════════════
print_header "📁 STEP 13: Creating Useful Directories"

mkdir -p "$HOME/projects"
mkdir -p "$HOME/notes"
mkdir -p "$HOME/.local/bin"
print_success "Directories created!"

# ═══════════════════════════════════════════════════════════════════════════
# DONE!
# ═══════════════════════════════════════════════════════════════════════════
print_header "🎉 INSTALLATION COMPLETE!"

echo -e "${GREEN}"
cat << 'EOF'
   ╔════════════════════════════════════════════════════════════════════════╗
   ║                                                                        ║
   ║   🚀 Your ULTIMATE terminal is almost ready! 🚀                        ║
   ║                                                                        ║
   ║   FINAL STEPS (Do these now!):                                         ║
   ║                                                                        ║
   ║   1. CLOSE this terminal completely                                    ║
   ║                                                                        ║
   ║   2. Open iTerm2 (not Terminal.app!)                                   ║
   ║                                                                        ║
   ║   3. Set the font:                                                     ║
   ║      iTerm → Settings → Profiles → Text → Font → "MesloLGS NF"        ║
   ║      (Set size to 13-14pt)                                             ║
   ║                                                                        ║
   ║   4. Import color scheme:                                              ║
   ║      Settings → Profiles → Colors → Color Presets → Import            ║
   ║      Select: ~/.config/iterm2/Catppuccin-Mocha.itermcolors            ║
   ║      Then select "Catppuccin Mocha" from presets                       ║
   ║                                                                        ║
   ║   5. Restart iTerm2                                                    ║
   ║                                                                        ║
   ║   6. Run: p10k configure                                               ║
   ║      (Follow the wizard to customize your prompt!)                     ║
   ║                                                                        ║
   ╚════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${CYAN}📚 Don't forget to check the CHEATSHEET.md for all commands!${NC}"
echo ""
echo -e "${YELLOW}🔄 To rollback if needed:${NC}"
echo -e "   cp ~/.zshrc.backup.* ~/.zshrc && source ~/.zshrc"
echo ""
