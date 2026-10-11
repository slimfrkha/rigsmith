# y: open yazi; on quit, cd into the directory you were browsing.
y() {
  local tmp="$(mktemp -t yazi-cwd.XXXXXX)" cwd
  yazi "$@" --cwd-file="$tmp"
  if cwd="$(command cat -- "$tmp")" && [[ -n $cwd && $cwd != "$PWD" ]]; then builtin cd -- "$cwd"; fi
  rm -f -- "$tmp"
}
