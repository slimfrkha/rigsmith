# helm completion, loaded the first time you run helm or press Tab after it.
_rs_lazy_helm() {
  unfunction _rs_lazy_helm helm 2>/dev/null
  source <(command helm completion zsh)
  compdef helm=helm
  helm "$@"
}
compdef _rs_lazy_helm helm
helm() { _rs_lazy_helm "$@"; }
