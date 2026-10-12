# rgs PATTERN   search file contents, preview the hit, open nothing (prints file:line)
# fkill [SIG]   pick processes to kill (default signal 9)
# fp            fuzzy-find a file with a bat preview
alias fp="fzf --preview 'bat --style=numbers --color=always --line-range :500 {}'"

rgs() {
  rg --color=always --line-number --no-heading --smart-case "$@" |
    fzf --ansi --color "hl:-1:underline,hl+:-1:underline:reverse" --delimiter : \
      --preview 'bat --color=always {1} --highlight-line {2}' \
      --preview-window 'up,60%,border-bottom,+{2}+3/3,~3'
}

fkill() {
  local pid
  pid=$(command ps -ef | sed 1d | fzf -m | awk '{print $2}')
  [[ -n $pid ]] && echo "$pid" | xargs kill -"${1:-9}"
}
