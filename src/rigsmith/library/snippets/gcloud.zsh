# Google Cloud SDK: PATH and completion (Homebrew cask or ~/.local/share install).
for _rs_gc in "$(brew --prefix 2>/dev/null)/share/google-cloud-sdk" "$HOME/.local/share/google-cloud-sdk"; do
  if [[ -f $_rs_gc/path.zsh.inc ]]; then
    source "$_rs_gc/path.zsh.inc"
    [[ -f $_rs_gc/completion.zsh.inc ]] && source "$_rs_gc/completion.zsh.inc"
    break
  fi
done
unset _rs_gc
export USE_GKE_GCLOUD_AUTH_PLUGIN=True
