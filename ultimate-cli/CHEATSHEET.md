# 🚀 ULTIMATE TERMINAL CHEATSHEET

> **Print this out or keep it handy!** This covers everything your terminal can do.

---

## 📋 TABLE OF CONTENTS

1. [FZF - Fuzzy Finder](#-fzf---the-game-changer)
2. [File Listing (eza)](#-file-listing-eza)
3. [File Viewing (bat)](#-file-viewing-bat)
4. [Search Tools (ripgrep, fd)](#-search-tools)
5. [Navigation (zoxide)](#-navigation-zoxide)
6. [Shell History (atuin)](#-shell-history-atuin)
7. [Git Commands](#-git-commands)
8. [Lazygit](#-lazygit---terminal-git-ui)
9. [File Manager (yazi)](#-file-manager-yazi)
10. [System Monitoring](#-system-monitoring)
11. [Python / UV](#-python--uv)
12. [Network Utilities](#-network-utilities)
13. [System Maintenance](#-system-maintenance)
14. [Custom Functions](#-custom-functions)
15. [Fun Stuff](#-fun-stuff)
16. [Keyboard Shortcuts](#-keyboard-shortcuts)
17. [The ** Tab Trick](#-the--tab-trick-explained)
18. [Tips & Tricks](#-tips--tricks)

---

## 🔍 FZF - THE GAME CHANGER

FZF (Fuzzy Finder) is probably the most powerful tool in your arsenal. It lets you find ANYTHING instantly.

### Core Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+T` | **Fuzzy find files** - Start typing any part of the filename |
| `Ctrl+R` | **Search command history** - Find any command you've ever run |
| `Alt+C` | **Fuzzy cd into directory** - Jump to any folder |
| `**<Tab>` | **Trigger fuzzy completion** - Works with any command! |

### Inside FZF

| Key | Action |
|-----|--------|
| `↑/↓` or `Ctrl+K/J` | Move selection up/down |
| `Enter` | Select item |
| `Tab` | Multi-select (when supported) |
| `Ctrl+/` | Toggle preview panel |
| `Ctrl+Y` | Copy selection to clipboard |
| `Ctrl+E` | Open in editor (micro) |
| `Esc` or `Ctrl+C` | Cancel |

### FZF Custom Commands

| Command | What It Does |
|---------|--------------|
| `fp` | Find files with preview |
| `rgs pattern` | Search in file contents with preview |
| `gfco` | Fuzzy git checkout branch |
| `gitlog` | Interactive git log browser |
| `fkill` | Find and kill processes |

### Example Workflow

```bash
# Find a config file somewhere in home directory
Ctrl+T → type "zshrc" → Enter

# Find that command you ran last week
Ctrl+R → type "docker compose" → Enter

# Jump to a project folder
Alt+C → type "myproject" → Enter
```

---

## 📁 FILE LISTING (EZA)

eza is a modern replacement for `ls` with icons, colors, and git integration.

| Command | Description |
|---------|-------------|
| `ls` | List files with icons |
| `ll` | Long list with permissions, size, git status |
| `la` | List all including hidden files |
| `lt` | Tree view (auto-excludes .git, __pycache__, etc.) |
| `lt2` | Tree view, 2 levels deep |
| `lt3` | Tree view, 3 levels deep |
| `lta` | Tree view including hidden files |
| `lsize` | Sort by file size (largest first) |
| `ltime` | Sort by modification time (newest first) |
| `lext` | Sort by file extension |

### Understanding the Output

```
drwxr-xr-x   - user  5 Jan 10:30  📁 directory/
.rw-r--r-- 1.2k user  5 Jan 10:30  📄 file.txt
.rw-r--r-- 2.3M user  5 Jan 10:30  🐍 script.py
                                   ●  (staged in git)
                                   M  (modified)
```

---

## 🐱 FILE VIEWING (BAT)

bat is `cat` with syntax highlighting, line numbers, and git integration.

| Command | Description |
|---------|-------------|
| `cat file` | View file with syntax highlighting |
| `catp file` | Plain view (no line numbers) |
| `cat -A file` | Show all characters (like tabs, newlines) |
| `cat -l python file` | Force specific language highlighting |
| `cat --diff file` | Show git diff for the file |

### Viewing Specific Lines

```bash
bat --line-range 10:20 file.py    # Lines 10-20
bat -r :50 file.py                 # First 50 lines
bat -r 100: file.py                # From line 100 to end
```

### Pro Tip
Man pages are now beautiful! Try:
```bash
man git
man zsh
```

---

## 🔎 SEARCH TOOLS

### ripgrep (rg) - Search File Contents

| Command | Description |
|---------|-------------|
| `rg pattern` | Search for pattern in all files |
| `rgi pattern` | Case-insensitive search |
| `rgl pattern` | Only list matching files |
| `rgc pattern` | Count matches per file |
| `rgh pattern` | Include hidden files |
| `rgs pattern` | **Interactive search with preview** |

### Examples

```bash
# Find all TODO comments
rg "TODO"

# Find function definitions in Python files
rg "def " --type py

# Search only in specific directory
rg "error" ./logs/

# Exclude directories
rg "pattern" --glob '!node_modules'

# Show context (2 lines before/after)
rg -C 2 "error"
```

### fd - Find Files

| Command | Description |
|---------|-------------|
| `fd pattern` | Find files matching pattern |
| `fdi pattern` | Case-insensitive |
| `fdh pattern` | Include hidden files |
| `fde py` | Find by extension |

### Examples

```bash
# Find all Python files
fd -e py

# Find files modified in last 24h
fd --changed-within 24h

# Find and delete all .DS_Store files
fd -H ".DS_Store" -x rm {}

# Find large files (>100MB)
fd --size +100m
```

---

## 🚀 NAVIGATION (ZOXIDE)

Zoxide remembers the directories you visit and lets you jump to them with partial names.

| Command | Description |
|---------|-------------|
| `cd dir` | Regular cd (zoxide-enhanced) |
| `j pattern` | Jump to best matching directory |
| `ji` | Interactive directory selection with fzf |

### How It Works

```bash
# First, visit some directories
cd ~/projects/my-awesome-app/frontend/src
cd ~/Documents/work/reports

# Later, from anywhere:
j awesome     # → ~/projects/my-awesome-app
j front       # → ~/projects/my-awesome-app/frontend
j reports     # → ~/Documents/work/reports

# Multiple patterns work too:
j proj front  # → ~/projects/my-awesome-app/frontend
```

### Quick Directory Aliases

| Alias | Goes To |
|-------|---------|
| `~` | Home directory |
| `-` | Previous directory |
| `..` | Parent directory |
| `...` | Two directories up |
| `....` | Three directories up |
| `.....` | Four directories up |
| `dl` | ~/Downloads |
| `dt` | ~/Desktop |
| `pj` | ~/projects |
| `doc` | ~/Documents |

---

## 📜 SHELL HISTORY (ATUIN)

Atuin supercharges your command history with sync, search, and statistics.

### Using Atuin

| Key | Action |
|-----|--------|
| `Ctrl+R` | Open history search |
| `↑/↓` | Navigate history |
| `Enter` | Execute selected command |
| `Tab` | Copy to command line (edit before running) |
| `Ctrl+D` | Delete entry from history |

### Inside Atuin Search

- Type to filter commands
- Results update in real-time
- Shows when and where commands were run

### Useful Commands

```bash
# View statistics
atuin stats

# Import history from zsh (run once on new machine)
atuin import auto

# Search history
atuin search "docker"
```

---

## 🌿 GIT COMMANDS

### Quick Aliases

| Alias | Command | Description |
|-------|---------|-------------|
| `g` | `git` | Shorter git |
| `gs` | `git status` | Repository status |
| `ga` | `git add` | Stage files |
| `gaa` | `git add --all` | Stage everything |
| `gc` | `git commit` | Commit (opens editor) |
| `gcm "msg"` | `git commit -m` | Commit with message |
| `gca "msg"` | `git commit -am` | Add all + commit |
| `gp` | `git push` | Push to remote |
| `gpl` | `git pull` | Pull from remote |
| `gf` | `git fetch` | Fetch from remote |
| `gfa` | `git fetch --all` | Fetch all remotes |

### Branching

| Alias | Command | Description |
|-------|---------|-------------|
| `gb` | `git branch` | List branches |
| `gba` | `git branch -a` | List all branches |
| `gco branch` | `git checkout` | Switch branch |
| `gcob name` | `git checkout -b` | Create & switch |
| `gfco` | - | **Fuzzy checkout** (fzf) |

### Viewing Changes

| Alias | Command | Description |
|-------|---------|-------------|
| `gd` | `git diff` | Show unstaged changes |
| `gds` | `git diff --staged` | Show staged changes |
| `glog` | - | Pretty log (graph) |
| `gloga` | - | Log all branches |
| `glp` | - | Log with dates |
| `gitlog` | - | **Interactive log** (fzf) |

### Stashing

| Alias | Command | Description |
|-------|---------|-------------|
| `gst` | `git stash` | Stash changes |
| `gstp` | `git stash pop` | Pop last stash |
| `gstl` | `git stash list` | List stashes |

### Quick Actions

| Alias | Command | Description |
|-------|---------|-------------|
| `gundo` | `git reset HEAD~1 --soft` | Undo last commit (keep changes) |
| `gwip` | - | Quick WIP commit |

---

## 🎯 LAZYGIT - TERMINAL GIT UI

**This will change your life.** Type `lg` in any git repo.

### Navigation

| Key | Action |
|-----|--------|
| `h/l` or `←/→` | Switch panels |
| `j/k` or `↑/↓` | Move within panel |
| `Enter` | Expand/collapse or select |
| `q` | Quit |
| `?` | Help |

### Common Actions

| Key | Panel | Action |
|-----|-------|--------|
| `Space` | Files | Stage/unstage file |
| `a` | Files | Stage all |
| `c` | Files | Commit |
| `C` | Files | Commit with editor |
| `p` | Files | Pull |
| `P` | Files | Push |
| `Space` | Branches | Checkout branch |
| `n` | Branches | New branch |
| `d` | Branches | Delete branch |
| `M` | Branches | Merge into current |
| `r` | Branches | Rebase onto current |
| `Enter` | Commits | View commit details |
| `g` | Commits | Reset to commit |
| `c` | Commits | Cherry-pick |

### Pro Tips

- Press `x` to see context-specific menu
- Press `@` to see command log
- Press `+` to increase panel size
- Press `[` and `]` to cycle through tabs

---

## 📂 FILE MANAGER (YAZI)

Type `y` to open yazi - a blazing fast terminal file manager.

### Navigation

| Key | Action |
|-----|--------|
| `h/l` or `←/→` | Parent/Enter directory |
| `j/k` or `↑/↓` | Move cursor |
| `gg` | Go to top |
| `G` | Go to bottom |
| `~` | Go to home |
| `/` | Search |
| `z` | Jump with zoxide |
| `q` | Quit |

### File Operations

| Key | Action |
|-----|--------|
| `Enter` | Open file |
| `Space` | Select file |
| `V` | Visual select mode |
| `y` | Copy selected |
| `x` | Cut selected |
| `p` | Paste |
| `d` | Delete (to trash) |
| `D` | Permanently delete |
| `r` | Rename |
| `a` | Create file |
| `A` | Create directory |
| `.` | Toggle hidden files |

### Tabs

| Key | Action |
|-----|--------|
| `t` | New tab |
| `1-9` | Go to tab N |
| `[` / `]` | Previous/Next tab |
| `Ctrl+c` | Close tab |

---

## 📊 SYSTEM MONITORING

### bottom (btm) - System Monitor

Type `btm` or `top` or `htop` to open.

| Key | Action |
|-----|--------|
| `q` | Quit |
| `?` | Help |
| `e` | Expand selected widget |
| `h/l` | Move between widgets |
| `gg` / `G` | Go to top/bottom |
| `k` | Kill process |
| `/` | Search processes |
| `Tab` | Toggle process grouping |
| `s` | Sort menu |
| `I` | Invert sort |
| `%` | Toggle percentage/values |

### Other Monitoring

| Command | Description |
|---------|-------------|
| `df` | Disk space (pretty) |
| `du` | Folder sizes (visual) |
| `ps` | Process list (colored) |
| `ports` | Show listening ports |
| `port 8080` | Check what's using port 8080 |

---

## 🐍 PYTHON / UV

### Python Aliases

| Alias | Command |
|-------|---------|
| `py` | `python3` |
| `pip` | `pip3` |
| `venv` | Create .venv and activate |
| `activate` | Activate .venv |

### UV - Fast Python Package Manager

| Alias | Command |
|-------|---------|
| `uvi` | `uv install` |
| `uvr` | `uv run` |
| `uvs` | `uv sync` |
| `uva package` | `uv add package` |
| `uvad package` | `uv add --dev package` |
| `uvp` | `uv pip` |

### Example Workflow

```bash
# New project
mkdir myproject && cd myproject
uv init
uva requests pandas
uvr python main.py

# Or with venv
venv                    # Creates and activates .venv
pip install requests
```

---

## 🌐 NETWORK UTILITIES

| Command | Description |
|---------|-------------|
| `myip` | Show public IP address |
| `localip` | Show local IP address |
| `ips` | Show all IP addresses |
| `ports` | Show listening ports |
| `port 3000` | Check what's using port 3000 |
| `flushdns` | Flush DNS cache |
| `weather` | Current weather |
| `weather London` | Weather in London |
| `moon` | Moon phase |

### Quick Server

| Command | Description |
|---------|-------------|
| `serve` | Python HTTP server on :8000 |
| `servephp` | PHP server on :8000 |

### HTTP Requests (httpie)

```bash
# GET request
http httpbin.org/get

# POST with JSON
http POST api.example.com/users name=John email=john@example.com

# With headers
http example.com Authorization:"Bearer token123"
```

---

## 🔧 SYSTEM MAINTENANCE

| Command | Description |
|---------|-------------|
| `brewup` | Update + upgrade + cleanup brew |
| `cleanup` | Remove all .DS_Store files |
| `emptytrash` | Empty trash completely |
| `showfiles` | Show hidden files in Finder |
| `hidefiles` | Hide hidden files in Finder |

### Updating Everything

```bash
# Update Homebrew and all packages
brewup

# Update Oh My Zsh
omz update

# Update Powerlevel10k
git -C ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k pull
```

---

## ⚡ CUSTOM FUNCTIONS

| Function | Usage | Description |
|----------|-------|-------------|
| `mkcd` | `mkcd new-folder` | Create folder and cd into it |
| `extract` | `extract archive.zip` | Extract any archive format |
| `bak` | `bak important.txt` | Create timestamped backup |
| `fkill` | `fkill` | Fuzzy find and kill process |
| `note` | `note Buy milk` | Add quick note |
| `note` | `note` (no args) | Open notes directory |
| `rgs` | `rgs "TODO"` | Search in files with preview |
| `gfco` | `gfco` | Fuzzy git checkout |
| `gitlog` | `gitlog` | Interactive git log |
| `newproject` | `newproject myapp` | Create project structure |
| `dirsize` | `dirsize` | Show directory sizes |
| `wttr` | `wttr Paris` | Weather for location |
| `cheat` | `cheat tar` | Show cheatsheet for command |

---

## 🎮 FUN STUFF

| Command | Description |
|---------|-------------|
| `fastfetch` | Faster system info |
| `matrix` | Matrix-style animation |
| `pipes` | Pipe screensaver |
| `parrot` | Party parrot! |
| `cowsay "Hello"` | Cow says hello |
| `figlet "TEXT" \| lolcat` | Rainbow ASCII text |
| `sl` | Steam locomotive (typo punishment) |

### Clipboard Emoji

| Command | Copies |
|---------|--------|
| `shrug` | ¯\_(ツ)_/¯ |
| `flip` | (╯°□°)╯︵ ┻━┻ |
| `lenny` | ( ͡° ͜ʖ ͡°) |

---

## ⌨️ KEYBOARD SHORTCUTS

### Line Editing

| Shortcut | Action |
|----------|--------|
| `Ctrl+A` | Go to beginning of line |
| `Ctrl+E` | Go to end of line |
| `Ctrl+U` | Delete from cursor to start |
| `Ctrl+K` | Delete from cursor to end |
| `Ctrl+W` | Delete word backward |
| `Alt+D` | Delete word forward |
| `Ctrl+Y` | Paste deleted text |
| `Ctrl+L` | Clear screen |

### Command Control

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Cancel current command |
| `Ctrl+Z` | Suspend current process |
| `Ctrl+D` | Exit shell / EOF |
| `ESC ESC` | **Add sudo to current command** |

### History

| Shortcut | Action |
|----------|--------|
| `!!` | Repeat last command |
| `!$` | Last argument of previous command |
| `!*` | All arguments of previous command |
| `!cmd` | Last command starting with "cmd" |
| `^old^new` | Replace "old" with "new" in last command |

### Examples

```bash
# Forgot sudo?
apt install something
# Press ESC ESC → becomes: sudo apt install something

# Repeat with different file
cat /very/long/path/file.txt
vim !$    # Opens vim /very/long/path/file.txt

# Fix typo
git statsu
^statsu^status    # Runs: git status
```

---

## 🌟 THE ** TAB TRICK EXPLAINED

The `**` followed by `Tab` triggers fzf completion. It works with almost any command!

### Syntax

```bash
command path/**<Tab>
# or just
command **<Tab>
```

### Examples

```bash
# Edit a file (don't know exact path)
vim **<Tab>
# → type "readme" → finds all README files → select one

# cd to nested directory
cd ~/projects/**<Tab>
# → type "src" → shows all src/ directories → select one

# Kill a process
kill **<Tab>
# → type "node" → shows node processes → select to kill

# Git checkout branch
git checkout **<Tab>
# → type "feature" → shows matching branches

# Open specific file type
code **/*.py<Tab>
# → shows all Python files

# SSH to a host
ssh **<Tab>
# → shows hosts from ~/.ssh/config

# Docker exec into container
docker exec -it **<Tab>
# → shows running containers
```

### Power Move: Combine with Path

```bash
# Only search in specific directory
vim src/**<Tab>

# Only specific extension
cat *.json<Tab>   # Not fuzzy, but still completion
```

---

## 💡 TIPS & TRICKS

### 1. Auto-Correct Typos
Made a typo? Just type `fk` (or `fuck`):
```bash
gti status    # Typo!
fk            # Automatically corrects to: git status
```

### 2. Repeat with Modifications
```bash
# Run last command with sudo
sudo !!

# Run last command but replace something
^old^new

# Use last argument
mkdir /some/new/directory
cd !$    # cd /some/new/directory
```

### 3. Quick Directory Stack
```bash
# Push current directory and go somewhere
pushd ~/projects

# Come back
popd

# See the stack
dirs -v
```

### 4. Brace Expansion
```bash
# Create multiple files
touch file{1,2,3}.txt    # file1.txt, file2.txt, file3.txt

# Create multiple directories
mkdir -p project/{src,tests,docs}

# Backup with timestamp
cp file.txt{,.bak}    # file.txt → file.txt.bak
```

### 5. Process Substitution
```bash
# Diff two commands' outputs
diff <(ls dir1) <(ls dir2)

# Compare sorted files
diff <(sort file1) <(sort file2)
```

### 6. Quick Math
```bash
echo $((2 + 2))         # 4
echo $((10 * 5))        # 50
echo $((100 / 3))       # 33
```

### 7. Watch Command Output
```bash
# Run command every 2 seconds
watch -n 2 'ls -la'

# Highlight changes
watch -d 'date'
```

### 8. Quick File Preview
```bash
# Preview any file with fzf
fp

# Preview specific directory
ls | fzf --preview 'bat {}'
```

---

## 🔄 ROLLBACK

If something goes wrong:

```bash
# Restore original .zshrc
cp ~/.zshrc.backup.* ~/.zshrc
source ~/.zshrc

# Or switch between configs
alias use-ultimate='cp ~/.zshrc.ultimate ~/.zshrc && source ~/.zshrc'
alias use-basic='cp ~/.zshrc.backup ~/.zshrc && source ~/.zshrc'
```

---

## 📚 LEARN MORE

| Tool | Documentation |
|------|---------------|
| Powerlevel10k | https://github.com/romkatv/powerlevel10k |
| Oh My Zsh | https://ohmyz.sh/ |
| fzf | https://github.com/junegunn/fzf |
| zoxide | https://github.com/ajeetdsouza/zoxide |
| eza | https://github.com/eza-community/eza |
| bat | https://github.com/sharkdp/bat |
| ripgrep | https://github.com/BurntSushi/ripgrep |
| fd | https://github.com/sharkdp/fd |
| lazygit | https://github.com/jesseduffield/lazygit |
| yazi | https://github.com/sxyazi/yazi |
| atuin | https://github.com/atuinsh/atuin |
| bottom | https://github.com/ClementTsang/bottom |

---

**🎉 Enjoy your ULTIMATE terminal!**

*Last updated: 2025*
