"""Infrastructure as code."""

from rigsmith.backends import Release
from rigsmith.library._util import ext, snippet, tool

TFLINT = "https://github.com/terraform-linters/tflint/releases/latest/download/tflint_{os}_{arch}.zip"

tool(
    "terraform",
    "HashiCorp Terraform (from HashiCorp's tap: core Homebrew froze at the old license).",
    brew="hashicorp/tap/terraform",
)
tool(
    "tflint",
    "Terraform linter: provider-aware checks and best practices (official release binary, BUSL-licensed).",
    sources=[Release("tflint", url=TFLINT)],
)
snippet("terraform-aliases", "tf, tfi, tfp, tfa, tfaa, tfd, tfsl, tfo.", 70, requires=["terraform"])
tool("terragrunt", "Thin wrapper for DRY Terraform configs across environments.")
tool("trivy", "Security scanner for IaC, images and repos (successor of tfsec): `trivy config .`.")
tool("infracost", "Cloud cost estimates for Terraform changes, in the terminal or PRs.")
ext("terraform-ext", "hashicorp.terraform", "Terraform/HCL in VS Code: syntax, validation, completion.")
tool("opentofu", "OpenTofu: the open-source Terraform fork (`tofu`). Coexists with terraform.", bin="tofu")
tool("packer", "Build machine images from code.", brew="hashicorp/tap/packer")
tool("vault", "HashiCorp Vault CLI: secrets, PKI, dynamic credentials.", brew="hashicorp/tap/vault")
tool("pulumi", "Infrastructure as code in real languages (Python, TS, Go).")
tool("ansible", "Agentless configuration management over SSH.")
tool("sops", "Encrypt secrets in YAML/JSON/ENV files, keep them in git.")
tool("age", "Simple, modern file encryption (pairs with sops).")
ext("ansible-ext", "redhat.ansible", "Ansible playbooks in VS Code: completion, linting.")
