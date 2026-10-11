"""Infrastructure as code."""

from rigsmith.library._util import ext, snippet, tool

tool(
    "terraform",
    "HashiCorp Terraform (from HashiCorp's tap: core Homebrew froze at the old license).",
    brew="hashicorp/tap/terraform",
)
tool("tflint", "Terraform linter: provider-aware checks and best practices.")
snippet("terraform-aliases", "tf, tfi, tfp, tfa, tfaa, tfd, tfsl, tfo.", 70, requires=["terraform"])
tool("terragrunt", "Thin wrapper for DRY Terraform configs across environments.")
tool("trivy", "Security scanner for IaC, images and repos (successor of tfsec): `trivy config .`.")
tool("infracost", "Cloud cost estimates for Terraform changes, in the terminal or PRs.")
ext("terraform-ext", "hashicorp.terraform", "Terraform/HCL in VS Code: syntax, validation, completion.")
