# matrix · pipes · rainbow TEXT · shrug / flip / lenny (copied to the clipboard)
if (( $+commands[pbcopy] )); then _rs_clip=pbcopy; else _rs_clip='xclip -selection clipboard'; fi
alias matrix='cmatrix -b -s -C cyan'
alias pipes='pipes-sh'
rainbow() { figlet -f slant "$@" | lolcat; }
alias shrug="echo '¯\_(ツ)_/¯' | $_rs_clip && echo '¯\_(ツ)_/¯ copied'"
alias flip="echo '(╯°□°)╯︵ ┻━┻' | $_rs_clip && echo '(╯°□°)╯︵ ┻━┻ copied'"
alias lenny="echo '( ͡° ͜ʖ ͡°)' | $_rs_clip && echo '( ͡° ͜ʖ ͡°) copied'"
unset _rs_clip
