# gs status  ga add  gaa add all  gc commit  gcm commit -m  gp push  gl/gpl pull  gf fetch
# gb branch  gco checkout  gcob new branch  gd diff  gds staged diff  gst stash  gstp pop
# glog graph  gloga graph --all  gundo undo last commit (soft)  gwip commit everything as WIP
# gfco  fuzzy checkout a branch        gitlog  fuzzy browse the log with previews
alias g='git'
alias gs='git status'
alias ga='git add'
alias gaa='git add --all'
alias gc='git commit'
alias gcm='git commit -m'
alias gca='git commit -am'
alias gp='git push'
alias gpl='git pull'
alias gl='git pull'
alias gf='git fetch'
alias gfa='git fetch --all'
alias gb='git branch'
alias gba='git branch -a'
alias gco='git checkout'
alias gcob='git checkout -b'
alias gd='git diff'
alias gds='git diff --staged'
alias gm='git merge'
alias gr='git rebase'
alias gst='git stash'
alias gstp='git stash pop'
alias gstl='git stash list'
alias glog='git log --oneline --graph --decorate'
alias gloga='git log --oneline --graph --decorate --all'
alias glp='git log --pretty=format:"%C(yellow)%h%Creset %C(blue)%ad%Creset %C(cyan)%an%Creset %s" --date=short'
alias gundo='git reset HEAD~1 --soft'
alias gwip='git add -A && git commit -m "WIP"'

gfco() {
  local branch
  branch=$(git branch --all | grep -v HEAD | fzf --preview "git log --oneline --graph --color=always \$(echo {} | sed 's/.* //' | sed 's#remotes/[^/]*/##')" |
    sed 's/.* //' | sed 's#remotes/[^/]*/##') && git checkout "$branch"
}

gitlog() {
  git log --graph --color=always --format="%C(auto)%h%d %s %C(black)%C(bold)%cr" "$@" |
    fzf --ansi --no-sort --reverse --tiebreak=index \
      --preview 'git show --color=always $(echo {} | grep -o "[a-f0-9]\{7,\}" | head -1)'
}
