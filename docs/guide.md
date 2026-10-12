# Guide

Task-by-task recipes for people already using rigsmith. New here? Start with the [README](../README.md). Looking up a
flag or a config key? See the [reference](reference.md).

- [Choose a config](#choose-a-config)
- [Tailor a config](#tailor-a-config)
- [Install part of your config](#install-part-of-your-config)
- [Switch configs](#switch-configs)
- [Set up per-project contexts](#set-up-per-project-contexts)
- [Add your own tools](#add-your-own-tools)
- [Bootstrap reproducibly (CI, servers)](#bootstrap-reproducibly-ci-servers)
- [Remove what rigsmith installed](#remove-what-rigsmith-installed)
- [Troubleshooting](#troubleshooting)

## Choose a config

A config is the menu rigsmith works from: which tools are in scope, in which section, at which profile. The
bundled presets are curated per kind of work:

```sh
rigsmith use              # pick from a list
rigsmith use platform     # or name one
```

```text
✓ now using your config (~/.config/rigsmith/config.yaml, from platform): 97 artifacts
Next: rigsmith install (or `rigsmith scan` to see where you stand)
```

`use` copies the preset to `~/.config/rigsmith/config.yaml`. Edit that file freely: upgrades never change it. Every
command prints which config it's using on its first line. To try a config without switching, pass `-c`:
`rigsmith scan -c python`.

## Tailor a config

To keep only some tools, or move them between profiles:

```sh
rigsmith init --from platform
```

1. Tick what your config should include (`space`). Tools from the library that the preset doesn't list are
   shown unticked.
2. Press `1`, `2` or `3` on a tool to set its profile (minimal, standard, comprehensive).
3. Press `enter`. rigsmith writes `~/.config/rigsmith/config.yaml` and asks whether to open it in `$EDITOR`, for
   example to rename sections. It's validated again when you close the editor.

## Install part of your config

```sh
rigsmith install -p minimal                  # the essentials only
rigsmith install -s kubernetes -s cloud      # two sections
rigsmith install k9s stern                   # two tools
rigsmith install -s git --dry-run            # see the plan, change nothing
```

Filters combine as **OR within a flag, AND across flags** ([details](reference.md#filters)). Running `install`
again is safe: what's already in place is skipped and reported as `0 changes`.

## Switch configs

```sh
rigsmith use python -y
```

Switching changes the menu, not your machine: nothing is installed or removed. Tools installed from the previous
config stay installed, `scan` lists them ("rigsmith also manages … not in this config"), and `uninstall` can still
remove them.

## Set up per-project contexts

rigsmith installs tools once for the whole machine. What changes from one project to the next is handled by three
tools in the library that switch **automatically when you `cd`**, so there's nothing to activate or forget.

| You want, per project | Use | Artifact |
|---|---|---|
| the right git identity (work vs personal) | git's `includeIf` by folder | `git-identities` |
| cloud project, cluster, account, secrets | a `.envrc` file | `direnv` |
| tool versions (node, terraform, python…) | a `mise.toml` file | `mise` |

### Git identity by folder

```sh
rigsmith install git-identities -c reference
```

`-c reference` takes it from the full library; add it to a section of your own config to keep it there. You're
asked for your work folder (default `~/work/`) and work email. Every repo under that folder then commits
with the work email; everything else keeps your usual one. To check, inside a work repo:

```sh
git config user.email
```

```text
you@company.com
```

Work-only settings (signing key, `core.sshCommand`) go in `~/.gitconfig-work`.

### Environment per folder with direnv

```sh
# ~/work/client-a/.envrc
export CLOUDSDK_ACTIVE_CONFIG_NAME=client-a   # gcloud project and account for this client
export KUBECONFIG=$PWD/.kube/config            # only this client's clusters
export AWS_PROFILE=client-a
dotenv .env                                     # secrets from a git-ignored file
```

direnv loads the file when you enter the folder and unloads it when you leave. Run `direnv allow` once for each new
or changed `.envrc`, so a cloned repo can't run code in your shell on its own.

### Tool versions per folder with mise

```toml
# ~/work/api/mise.toml
[tools]
node = "22"
terraform = "1.9.5"

[env]
DATABASE_URL = "postgres://localhost/api"
```

Each version is downloaded once and shared by every project that uses it. Use mise for versions and simple
variables, direnv when you need shell logic.

## Add your own tools

For a tool Homebrew or apt already packages, declare it in your config:

```yaml
custom:
  - {id: btop, help: "Resource monitor", brew: btop, apt: btop}
sections:
  extra:
    tools: {btop: minimal}
```

For anything else (a cask, a role, a snippet, a check), drop a Python file in `~/.config/rigsmith/artifacts/`:

```python
from rigsmith.backends import Brew, Cask
from rigsmith.model import Artifact

Artifact(
    id="wezterm",
    help="GPU-accelerated terminal configured in Lua.",
    sources=[Cask("wezterm", os="darwin"), Brew("wezterm")],
    check="test -d /Applications/WezTerm.app || command -v wezterm",
    role="terminal",
)
```

Then list `wezterm` in a section of your config. Every field and backend is in the
[reference](reference.md#artifacts). Want it in the built-in library instead? Open an issue with the **New artifact**
template.

## Bootstrap reproducibly (CI, servers)

Pin the rigsmith version **and** every answer, so a run doesn't depend on library defaults:

```sh
curl -fsSL https://raw.githubusercontent.com/slimfrkha/rigsmith/v0.1.0/install.sh \
  | RIGSMITH_VERSION=0.1.0 sh -s -- install -c my-config.yaml -y
```

Every bundled preset already pins its answers; `server` is a good start for headless machines.

## Remove what rigsmith installed

```sh
rigsmith uninstall              # pick from what rigsmith installed
rigsmith uninstall k9s -y       # one tool, no questions
rigsmith uninstall --dry-run    # see what would go
```

Only what rigsmith did is undone: tools you had before stay (unless `--include-unmanaged`), and a file or setting you
changed since install is kept, with a warning. Installing Homebrew and one-time steps like importing shell history
can't be undone; they're listed before you confirm an install.

## Troubleshooting

- **My shell loads things twice (slow start, duplicate prompt).** Your own `~/.zshrc` probably loads oh-my-zsh,
  zinit or a prompt too. `rigsmith install` lists those lines before running; remove or comment them out.
- **A tool says "installed but not detected".** The install ran but the binary isn't where rigsmith looks. Open a new
  terminal (PATH changes) and run `rigsmith scan`; if it persists, open a bug with the log from
  `~/.local/state/rigsmith/logs/`.
- **"is not a supported platform".** rigsmith supports macOS 14+, Ubuntu 22.04/24.04 and Debian 12. Elsewhere,
  `--unsupported` lets you try anyway.
- **A setting or file was "changed since install, kept".** You edited it after rigsmith wrote it, so rigsmith
  leaves your version alone. Delete or restore it by hand if you want it gone.
