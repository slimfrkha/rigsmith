# helm completion, loaded on first use.
_rs_lazy_helm() {
  unfunction _rs_lazy_helm helm 2>/dev/null
  source <(command helm completion zsh)
  helm "$@"
}
helm() { _rs_lazy_helm "$@"; }
