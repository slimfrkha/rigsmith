# cat → bat (no pager), catp plain output, man pages rendered through bat.
alias cat='bat --paging=never'
alias catp='bat --plain'
export MANPAGER="sh -c 'col -bx | bat -l man -p'"
export MANROFFOPT="-c"
