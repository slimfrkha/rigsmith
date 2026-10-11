# mkcd DIR       create a directory and cd into it
# extract FILE   extract any archive
# bak FILE       timestamped copy
# dirsize [DIR]  biggest entries first
# port N         what listens on port N
# newproject X   ~/projects/X with src/tests/docs + git init

mkcd() { mkdir -p "$@" && cd "$_"; }

extract() {
  [[ -f $1 ]] || { echo "'$1' is not a file"; return 1; }
  case $1 in
    *.tar.bz2|*.tbz2) tar xjf "$1" ;;
    *.tar.gz|*.tgz)   tar xzf "$1" ;;
    *.tar.xz)         tar xJf "$1" ;;
    *.tar)            tar xf "$1" ;;
    *.bz2)            bunzip2 "$1" ;;
    *.gz)             gunzip "$1" ;;
    *.xz)             unxz "$1" ;;
    *.zip)            unzip "$1" ;;
    *.7z)             7z x "$1" ;;
    *.rar)            unrar e "$1" ;;
    *.Z)              uncompress "$1" ;;
    *)                echo "'$1' cannot be extracted"; return 1 ;;
  esac
}

bak() {
  local dest="$1.bak.$(date +%Y%m%d_%H%M%S)"
  cp "$1" "$dest" && echo "Backed up to $dest"
}

dirsize() { du -sh "${1:-.}"/* 2>/dev/null | sort -hr | head -20; }

port() { lsof -i ":$1"; }

newproject() {
  [[ -n $1 ]] || { echo "usage: newproject NAME"; return 1; }
  mkdir -p "$HOME/projects/$1"/{src,tests,docs} && cd "$HOME/projects/$1" && git init && echo "# $1" > README.md
}
