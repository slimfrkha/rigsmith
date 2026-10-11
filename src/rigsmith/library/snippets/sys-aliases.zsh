# Swap classic system tools for modern ones, only when they're installed.
(( $+commands[btm] ))   && alias top='btm' htop='btm'
(( $+commands[duf] ))   && alias df='duf'
(( $+commands[dust] ))  && alias du='dust'
(( $+commands[procs] )) && alias ps='procs'
true
