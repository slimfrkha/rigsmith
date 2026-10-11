# 🚀 Ultimate Mac Terminal Setup

> **One script to rule them all.** Transform a brand new Mac into a terminal powerhouse.

![Terminal Preview](https://raw.githubusercontent.com/romkatv/powerlevel10k-media/master/prompt-styles-high-contrast.png)

---

## 📦 What's Included

| File | Description |
|------|-------------|
| `install-ultimate-terminal.sh` | Main installation script - run this first |
| `ultimate-zshrc` | Complete .zshrc configuration |
| `Catppuccin-Mocha.itermcolors` | Beautiful dark color scheme for iTerm |
| `CHEATSHEET.md` | **Comprehensive reference** for all commands |
| `README.md` | This file |

---

## ⚡ Quick Start (New Mac)

```bash
# 1. Download/copy all files to your Mac
# 2. Open Terminal.app (default macOS terminal)
# 3. Navigate to the folder with these files
cd ~/Downloads/ultimate-terminal-setup

# 4. Run the installer
chmod +x install-ultimate-terminal.sh
./install-ultimate-terminal.sh

# 5. Follow the on-screen instructions
```

---

## 🛠️ What Gets Installed

### Terminal & Shell
- **iTerm2** - The best terminal emulator for Mac
- **Oh My Zsh** - Zsh framework with plugins
- **Zplug** - Plugin manager for additional plugins
- **Powerlevel10k** - Beautiful, fast prompt with git info

### Fonts
- **MesloLGS Nerd Font** - Required for icons
- **JetBrains Mono Nerd Font** - Alternative font
- **FiraCode Nerd Font** - Alternative font

### Modern CLI Replacements
| Old | New | Description |
|-----|-----|-------------|
| `ls` | **eza** | File listing with icons & git |
| `cat` | **bat** | Syntax highlighting |
| `grep` | **ripgrep** | 10x faster search |
| `find` | **fd** | Simpler, faster find |
| `cd` | **zoxide** | Smart directory jumping |
| `history` | **atuin** | Better shell history |
| `top` | **bottom** | Beautiful system monitor |
| `du` | **dust** | Visual disk usage |
| `df` | **duf** | Pretty disk free |
| `ps` | **procs** | Colored process list |

### Git Tools
- **git** - Version control
- **lazygit** - Terminal git UI (game-changer!)
- **git-delta** - Beautiful diffs
- **gh** - GitHub CLI

### Productivity
- **fzf** - Fuzzy finder (essential!)
- **thefuck** - Auto-correct commands
- **tldr** - Simplified man pages
- **micro** - Modern terminal editor
- **yazi** - Terminal file manager

### JSON & Data
- **jq** - JSON processor
- **yq** - YAML processor

### Networking
- **httpie** - User-friendly HTTP client
- **curl** & **wget** - URL tools

### Development
- **node** - Node.js
- **python** - Python 3
- **uv** - Fast Python package manager

### Fun
- **neofetch** / **fastfetch** - System info with ASCII art
- **cmatrix** - Matrix animation
- **pipes-sh** - Pipe screensaver
- **figlet** + **lolcat** - Rainbow ASCII text
- **cowsay** - Talking cow
- **sl** - Steam locomotive

---

## 📋 Post-Installation Steps

After running the installer, do these **important** steps:

### 1. Open iTerm2
- Close Terminal.app
- Open iTerm2 (it was just installed)

### 2. Set the Font (REQUIRED for icons!)
1. Open iTerm2 → **Settings** (Cmd+,)
2. Go to **Profiles** → **Text**
3. Click **Font** dropdown
4. Select **MesloLGS NF**
5. Set size to **13** or **14** pt

### 3. Import Color Scheme
1. In iTerm2 Settings, go to **Profiles** → **Colors**
2. Click **Color Presets...** dropdown
3. Click **Import...**
4. Select `Catppuccin-Mocha.itermcolors`
5. Click **Color Presets...** again
6. Select **Catppuccin Mocha**

### 4. Optional Visual Tweaks
- **Profiles** → **Window** → Transparency: 5-10%
- **Profiles** → **Window** → Blur: Enable
- **Profiles** → **Window** → Style: Compact

### 5. Restart iTerm2
Completely quit and reopen iTerm2.

### 6. Configure Your Prompt
```bash
p10k configure
```
Follow the wizard to customize how your prompt looks!

### 7. Import Shell History
```bash
atuin import auto
```
This imports your existing command history into atuin.

---

## 🎮 First Commands to Try

```bash
# See your new system info
neofetch

# List files with icons
ls
ll

# Open lazygit in any git repo
lg

# Browse files with yazi
y

# System monitor
btm

# Fuzzy find any file
# Press Ctrl+T

# Enter the Matrix
matrix

# Rainbow text
figlet "HELLO" | lolcat
```

---

## 🔑 Essential Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+T` | Fuzzy find files |
| `Ctrl+R` | Search command history |
| `Alt+C` | Fuzzy cd into directory |
| `**<Tab>` | Fuzzy completion |
| `ESC ESC` | Add sudo to command |
| `fk` | Fix last typo (thefuck) |

---

## 🔄 Keeping Things Updated

```bash
# Update everything
brewup

# Update Oh My Zsh
omz update

# Update Powerlevel10k
git -C ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k pull

# Update zplug plugins
zplug update
```

---

## 🔙 Rollback

If anything goes wrong, the installer creates a backup:

```bash
# Find your backup
ls ~/.zshrc.backup.*

# Restore it
cp ~/.zshrc.backup.YYYYMMDD_HHMMSS ~/.zshrc
source ~/.zshrc
```

---

## 📁 Adding Custom Configuration

For machine-specific settings, create `~/.zshrc.local`:

```bash
# Example ~/.zshrc.local

# Add custom paths
export PATH="$PATH:/some/custom/path"

# Custom aliases
alias myapp='cd ~/projects/my-app && code .'

# API keys (don't commit these!)
export API_KEY="xxx"
```

This file is automatically loaded if it exists.

---

## 📚 Documentation

| Tool | Docs |
|------|------|
| Oh My Zsh | https://ohmyz.sh/ |
| Powerlevel10k | https://github.com/romkatv/powerlevel10k |
| fzf | https://github.com/junegunn/fzf |
| lazygit | https://github.com/jesseduffield/lazygit |
| yazi | https://github.com/sxyazi/yazi |
| atuin | https://github.com/atuinsh/atuin |

**See `CHEATSHEET.md` for complete command reference!**

---

## 💡 Troubleshooting

### Icons show as boxes/weird characters
→ Set iTerm font to **MesloLGS NF** (Settings → Profiles → Text → Font)

### Prompt looks broken
→ Run `p10k configure` to reconfigure

### Command not found
→ Restart terminal or run `source ~/.zshrc`

### atuin doesn't show old history
→ Run `atuin import auto`

### Something is broken, want to go back
→ See **Rollback** section above

---

## 🎉 Enjoy!

**Read the CHEATSHEET.md** - it has everything you need to master your new terminal.

Questions? Check the documentation links above or search GitHub issues for the specific tool.

---

*Created with ❤️ for future me and anyone setting up a new Mac*
