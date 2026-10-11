# ls → eza. Icons only when RIGSMITH_ICONS is set (icons question).
#   ll long + git   la all   lt tree   lsize/ltime/lext sorted
_rs_eza="eza --group-directories-first ${RIGSMITH_ICONS:+--icons}"
alias ls="$_rs_eza"
alias ll="$_rs_eza -l -g --git"
alias la="$_rs_eza -la --git"
alias lt="$_rs_eza --tree -a -I '.git|__pycache__|.mypy_cache|node_modules|.venv'"
alias lt2="$_rs_eza --tree --level=2"
alias lt3="$_rs_eza --tree --level=3"
alias lsize="$_rs_eza -la --sort=size --reverse"
alias ltime="$_rs_eza -la --sort=modified"
alias lext="$_rs_eza -la --sort=extension"
unset _rs_eza
