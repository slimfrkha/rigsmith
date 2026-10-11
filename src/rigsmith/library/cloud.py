"""Cloud provider CLIs."""

from rigsmith.backends import Cask, Script
from rigsmith.library._util import ext, snippet, tool
from rigsmith.model import Artifact, Snippet

GCLOUD_LINUX = Script(
    "gcloud",
    install_cmd="curl -fsSL https://sdk.cloud.google.com"
    ' | bash -s -- --disable-prompts --install-dir="$HOME/.local/share"',
    check_cmd='test -x "$HOME/.local/share/google-cloud-sdk/bin/gcloud"',
    remove_cmd='rm -rf "$HOME/.local/share/google-cloud-sdk"',
    os="linux",
)

Artifact(
    id="gcloud",
    help="Google Cloud CLI (gcloud, gsutil, bq) with completion. Then `gcloud auth login`.",
    sources=[Cask("gcloud-cli", os="darwin"), GCLOUD_LINUX],
    bin="gcloud",
    shell=Snippet("gcloud.zsh", 10),
    notes=["Run `gcloud auth login` and `gcloud config set project <id>` (or `gproj`)."],
)
Artifact(
    id="gke-auth-plugin",
    help="GKE auth plugin kubectl needs to talk to GKE clusters.",
    sources=[
        Script(
            "gke-gcloud-auth-plugin",
            install_cmd="gcloud components install gke-gcloud-auth-plugin --quiet",
            check_cmd="gcloud components list --filter=id:gke-gcloud-auth-plugin --format='value(state.name)' "
            "2>/dev/null | grep -q Installed",
            remove_cmd="gcloud components remove gke-gcloud-auth-plugin --quiet",
        )
    ],
    requires=["gcloud"],
)
snippet(
    "gcp-aliases",
    "gcloud shortcuts (gsetp, gkecl, grun…) plus fuzzy gproj (switch project) and gkecreds (cluster credentials).",
    70,
    requires=["gcloud"],
)
ext("cloudcode-ext", "GoogleCloudTools.cloudcode", "Google Cloud Code: GKE, Cloud Run and APIs in VS Code.")
tool("awscli", "AWS CLI v2. Then `aws configure sso` or `aws configure`.", bin="aws")
ext("aws-ext", "AmazonWebServices.aws-toolkit-vscode", "AWS Toolkit: explore resources, Lambda, CodeWhisperer.")
