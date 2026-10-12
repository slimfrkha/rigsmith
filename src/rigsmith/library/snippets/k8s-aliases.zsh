# k kubectl · kx/kn kubectx/kubens · kgp(a) pods · kgd deployments · kgs services · kgn nodes
# ka apply -f · kdel delete · kdelf delete -f · kdiff diff -f · k9/k9a k9s · st stern
# kctx / kns   fuzzy-switch context / namespace
# kdebug [IMG] throwaway debug pod (default busybox)
alias k='kubectl'
alias kx='kubectx'
alias kn='kubens'
alias kgp='kubectl get pods'
alias kgpa='kubectl get pods -A'
alias kgd='kubectl get deployments'
alias kgs='kubectl get services'
alias kgn='kubectl get nodes'
alias ka='kubectl apply -f'
alias kdel='kubectl delete'
alias kdelf='kubectl delete -f'
alias kdiff='kubectl diff -f'
alias k9='k9s'
alias k9a='k9s -A'
(( $+commands[stern] )) && alias st='stern'

kctx() {
  local ctx
  ctx=$(kubectl config get-contexts -o name | fzf --height 40% --reverse --prompt="Context: ")
  [[ -n $ctx ]] && kubectl config use-context "$ctx"
}
kns() {
  local ns
  ns=$(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | fzf --height 40% --reverse --prompt="Namespace: ")
  [[ -n $ns ]] && kubectl config set-context --current --namespace="$ns"
}
kdebug() { kubectl run "debug-$$" --rm -it --restart=Never --image="${1:-busybox}" -- /bin/sh; }
