# kubectl completion, loaded the first time you run kubectl or press Tab after it (fast shell startup).
_rs_lazy_kubectl() {
  unfunction _rs_lazy_kubectl kubectl 2>/dev/null
  source <(command kubectl completion zsh)
  compdef kubectl=kubectl
  compdef k=kubectl
  kubectl "$@"
}
compdef _rs_lazy_kubectl kubectl
kubectl() { _rs_lazy_kubectl "$@"; }
