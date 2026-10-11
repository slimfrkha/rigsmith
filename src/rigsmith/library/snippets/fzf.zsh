# fzf key bindings: Ctrl+T files, Alt+C directories, Ctrl+R history, ** <Tab> completion.
#   In the finder: Ctrl+/ toggle preview, Ctrl+Y copy selection.
source <(fzf --zsh)

if (( $+commands[fd] )); then
  export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
  export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
  export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'
fi

if (( $+commands[pbcopy] )); then _rs_copy=pbcopy; elif (( $+commands[wl-copy] )); then _rs_copy=wl-copy; else _rs_copy='xclip -selection clipboard'; fi
if (( $+commands[bat] )); then _rs_preview='bat --color=always --style=numbers --line-range=:500 {}'; else _rs_preview='cat {}'; fi

export FZF_DEFAULT_OPTS="--height 60% --layout=reverse --border=rounded --info=inline
  --bind='ctrl-/:toggle-preview' --bind='ctrl-y:execute-silent(echo {} | $_rs_copy)+abort'"
if [[ $RIGSMITH_THEME == catppuccin ]]; then
  FZF_DEFAULT_OPTS+=" --color=bg+:#313244,bg:#1e1e2e,spinner:#f5e0dc,hl:#f38ba8
  --color=fg:#cdd6f4,header:#f38ba8,info:#cba6f7,pointer:#f5e0dc
  --color=marker:#f5e0dc,fg+:#cdd6f4,prompt:#cba6f7,hl+:#f38ba8"
fi
export FZF_CTRL_T_OPTS="--preview '$_rs_preview'"
if (( $+commands[eza] )); then
  export FZF_ALT_C_OPTS="--preview 'eza --tree --level=2 --color=always ${RIGSMITH_ICONS:+--icons} {}'"
fi
export FZF_CTRL_R_OPTS="--preview 'echo {}' --preview-window=down:3:wrap"
unset _rs_copy _rs_preview
