# note [TEXT]  append to ~/notes/quick-notes.md (no args: open the folder)
# wttr [CITY]  weather (also: weather)
# cheat CMD    tldr, falling back to cheat.sh
note() {
  mkdir -p ~/notes
  if (( $# )); then echo "$(date '+%Y-%m-%d %H:%M'): $*" >> ~/notes/quick-notes.md; else ${EDITOR:-vi} ~/notes; fi
}
wttr() { curl -s "wttr.in/${1:-}"; }
alias weather='wttr'
cheat() { tldr "$1" 2>/dev/null || curl -s "cheat.sh/$1"; }

alias myip='curl -s https://ipinfo.io/ip && echo'
alias ports='lsof -i -P -n | grep LISTEN'
alias now='date +"%Y-%m-%d %H:%M:%S"'
alias timestamp='date +%s'
alias path='echo $PATH | tr ":" "\n"'
alias uuid='uuidgen | tr "[:upper:]" "[:lower:]"'
alias serve='python3 -m http.server 8000'
