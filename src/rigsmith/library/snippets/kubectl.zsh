# kubectl completion, loaded on first use so shell startup stays fast.
_rs_lazy_kubectl() {
  unfunction _rs_lazy_kubectl kubectl 2>/dev/null
  source <(command kubectl completion zsh)
  kubectl "$@"
}
kubectl() { _rs_lazy_kubectl "$@"; }
