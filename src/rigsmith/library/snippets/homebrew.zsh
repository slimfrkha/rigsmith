# Homebrew environment (PATH, MANPATH, …) on Apple Silicon, Intel macOS and Linux.
for _rs_brew in /opt/homebrew/bin/brew /usr/local/bin/brew /home/linuxbrew/.linuxbrew/bin/brew; do
  [[ -x $_rs_brew ]] && eval "$($_rs_brew shellenv)" && break
done
unset _rs_brew
