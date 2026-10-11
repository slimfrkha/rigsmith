# gc gcloud · gcfgl config list · gsetp/gsetr/gsetz set project/region/zone · gpl projects list
# gcel / gcess  compute instances list / ssh · gkecl / gkecr  GKE clusters list / get-credentials
# grun / grunl / grund  Cloud Run · gfn functions · gsl / gscp gsutil · bql / bqq BigQuery
# gproj      fuzzy-switch the active project
# gkecreds   fuzzy-pick a GKE cluster and fetch credentials
alias gc='gcloud'
alias gcfg='gcloud config'
alias gcfgl='gcloud config list'
alias gsetp='gcloud config set project'
alias gsetr='gcloud config set compute/region'
alias gsetz='gcloud config set compute/zone'
alias gpl='gcloud projects list'
alias gcel='gcloud compute instances list'
alias gcess='gcloud compute ssh'
alias gkecl='gcloud container clusters list'
alias gkecr='gcloud container clusters get-credentials'
alias grun='gcloud run'
alias grunl='gcloud run services list'
alias grund='gcloud run deploy'
alias gfn='gcloud functions'
alias gfnl='gcloud functions list'
alias gsl='gsutil ls'
alias gscp='gsutil cp'
alias bql='bq ls'
alias bqq='bq query --use_legacy_sql=false'

gproj() {
  local project
  project=$(gcloud projects list --format="value(projectId)" | fzf --height 40% --reverse --prompt="GCP Project: ")
  [[ -n $project ]] && gcloud config set project "$project"
}
gkecreds() {
  local cluster name location
  cluster=$(gcloud container clusters list --format="value(name,location)" | fzf --height 40% --reverse --prompt="GKE Cluster: ")
  [[ -z $cluster ]] && return
  read -r name location <<< "$cluster"
  gcloud container clusters get-credentials "$name" --location "$location"
}
