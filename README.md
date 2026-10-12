# rigsmith

[![ci](https://github.com/slimfrkha/rigsmith/actions/workflows/ci.yml/badge.svg)](https://github.com/slimfrkha/rigsmith/actions/workflows/ci.yml)
[![e2e](https://github.com/slimfrkha/rigsmith/actions/workflows/e2e.yml/badge.svg)](https://github.com/slimfrkha/rigsmith/actions/workflows/e2e.yml)

Set up a fresh macOS or Linux machine from a curated library of developer tools and the config that
makes them work, then see what's installed and undo it cleanly.

```sh
curl -fsSL https://raw.githubusercontent.com/slimfrkha/rigsmith/main/install.sh | sh -s -- install
```

Or start from a preset for your kind of work:

```sh
curl -fsSL https://raw.githubusercontent.com/slimfrkha/rigsmith/main/install.sh | sh -s -- install -c platform
```

| Preset | For |
|---|---|
| [`python`](config/presets/python.yaml) | uv + ruff + ty, notebooks, VS Code with the Astral stack |
| [`backend-go`](config/presets/backend-go.yaml) | Go toolchain, containers, a local cluster, API and load-testing tools |
| [`rust`](config/presets/rust.yaml) | rustup, bacon, nextest, rust-analyzer |
| [`java`](config/presets/java.yaml) | OpenJDK, Maven, Gradle, the VS Code Java pack |
| [`web`](config/presets/web.yaml) | Node, pnpm, Bun, Biome, ESLint/Prettier, Tailwind |
| [`data-engineer`](config/presets/data-engineer.yaml) | Python + SQL in the terminal (DuckDB, Postgres, Kafka), notebooks, cloud CLIs |
| [`ml-engineer`](config/presets/ml-engineer.yaml) | Python with uv, notebooks, Hugging Face, local LLMs |
| [`platform`](config/presets/platform.yaml) | containers, Kubernetes end to end, Terraform and friends, GCP and AWS |
| [`server`](config/presets/server.yaml) | a headless box over SSH: shell and modern CLI, no fonts or GUI apps |

![start from](docs/screenshots/start-from.svg)

The first `rigsmith install` asks which of these to start from. To pick one for good, run
`rigsmith use platform` (or `rigsmith use` for the menu): it copies the preset to your config, and
`install`, `scan` and `uninstall` use it from then on. Every command prints which config it's using.

Every preset shares a sane base (zsh, starship, fzf, ripgrep, eza, zoxide, git, lazygit, VS Code) and pins
all its answers, so `-y` gives the same result every time. Fork one with `rigsmith init --from <preset>`.

A short questionnaire, a picker where you can tick or untick anything, a summary of exactly what will
change, then one install after the other. **[Browse the catalog →](docs/CATALOG.md)** 220+ tools across
shell, CLI, git, Python, Go, Rust, Java, JS, containers, Kubernetes, cloud, IaC, data, ML and VS Code.

![picker](docs/screenshots/picker.svg)

## Contents

- [Commands](#commands)
- [How it's organized](#how-its-organized)
- [Safe by design](#safe-by-design)
- [Configs](#configs)
- [Per-project setups](#per-project-setups)
- [Add your own tools](#add-your-own-tools)
- [Platforms](#platforms)
- [Development](#development)

## Commands

| Command | What it does |
|---|---|
| `rigsmith use` | Pick your config: copies a preset (or your own YAML) to `~/.config/rigsmith/config.yaml`. |
| `rigsmith install` | Questionnaire → picker → summary → install. `-y` skips the screens and uses defaults. |
| `rigsmith scan` | What's installed, partial, missing or unavailable, by section. `--all` scans the whole library. |
| `rigsmith uninstall` | Undo what rigsmith installed, from its receipts, even if it came from another config. Things you had before are left alone. |
| `rigsmith init` | Create your own config: pick artifacts and profiles, then optionally restructure in `$EDITOR`. |

Every command takes the same filters:

```sh
rigsmith install -p standard -s python -s kubernetes   # standard profile, two sections
rigsmith install fzf zoxide                            # just these
rigsmith scan -s cli/search                            # a subsection
rigsmith install -c example -y                         # someone else's config, no questions
rigsmith install --dry-run                             # show the plan, change nothing
```

`-s` and `-p` combine as **OR within a flag, AND across flags**. Artifact ids narrow the result further.

## How it's organized

- **Artifact**: one installable unit: a package plus the config the tool needs to work (a zsh snippet,
  a file, a few settings). `fzf` brings its key bindings, `gcloud` its PATH and completion.
  Optional taste (aliases, themes, preferred settings) lives in separate artifacts such as `eza-aliases`.
- **Section / subsection**: what a tool *is*: `cli/search`, `kubernetes/logs`, `python/vscode`.
- **Profile**: how much you want: `minimal ⊂ standard ⊂ comprehensive`. Profiles are cumulative.
- **Role**: tools that can't coexist, such as two prompts (`p10k` / `starship`) or two container runtimes.
  The picker shows them as radio buttons. A provider that's already installed is always kept unless you pick another one.
- **Question**: the questionnaire is built from the artifacts in your config. Each question is
  asked only if something in scope cares about it: icons, aliases, full-screen TUIs, fun stuff, color theme.

| | |
|---|---|
| ![questionnaire](docs/screenshots/questionnaire.svg) | ![help](docs/screenshots/help.svg) |

In the picker: `space` toggles, `h` explains the row, `/` searches, `tab` folds a section, `enter` continues.

## Safe by design

- **Your `~/.zshrc` is never overwritten.** rigsmith adds one marked block at the top that sources
  `~/.config/rigsmith/init.zsh`, which sources one small file per tool from `~/.config/rigsmith/shell.d/`.
  Your own lines stay below the block and win. Before the first install, rigsmith warns about lines in
  your `~/.zshrc` that would load the same things twice.
- **Every change gets a receipt** in `~/.local/state/rigsmith/state.json`, recording what it was before and what rigsmith
  left behind. `uninstall` reverses only what rigsmith did, and only if it's still what rigsmith left. If you
  edited a file or changed a setting since, your version is kept with a warning.
- **Things you already had stay put.** A tool that was installed before shows as `pre-existing` and isn't
  removed (unless you pass `--include-unmanaged`).
- **Irreversible steps are listed before you confirm**, such as installing Homebrew or importing shell history.
- **Idempotent**: running `install` again reports `0 changes`. CI checks this on real macOS and Ubuntu
  machines, along with uninstall restoring `~/.zshrc` byte for byte.

![confirm](docs/screenshots/confirm.svg)

## Configs

A config is a menu: which artifacts are in scope, in which section, at which profile.

| Config | |
|---|---|
| [`config/reference.yaml`](config/reference.yaml) | The whole library. Used when you have no config of your own. |
| [`config/example.yaml`](config/example.yaml) | The author's setup (zsh, k9s, GCP, Terraform, VS Code), with every answer pinned. |
| [`config/presets/`](config/presets) | Curated menus per developer type (table above). |
| `~/.config/rigsmith/config.yaml` | Yours: a copy written by `rigsmith use` (or tailored with `rigsmith init`). Used automatically when it exists. |

`-c` takes a path or a bundled name: `rigsmith install -c example`, `rigsmith install -c ml-engineer`.

```yaml
profiles: [minimal, standard, comprehensive]
sections:
  cli:
    search: {ripgrep: minimal, fzf: minimal, fd: standard}
  shell:
    prompt: {p10k: minimal, starship: minimal}   # same role: one of them
answers:          # pre-answers: used by -y, and as defaults in the questionnaire
  prompt: starship
  icons: "yes"
questions:
  skip: [fun]
```

A config fully replaces the reference. When the library gains artifacts your config doesn't list,
`scan` says so (`scan --all --new` lists them, and `init --from <your config>` offers them unticked).

**Reproducible bootstraps** (CI, servers): pin the rigsmith version *and* every answer:

```sh
curl -fsSL https://raw.githubusercontent.com/slimfrkha/rigsmith/v0.1.0/install.sh \
  | RIGSMITH_VERSION=0.1.0 sh -s -- install -c my-config.yaml -y
```

## Per-project setups

rigsmith installs tools once, for the whole machine. What changes from one project to the next is handled by
three things in the library that switch **automatically when you `cd`**, so there's nothing to activate or forget:

| You want, per project | Use | Artifact |
|---|---|---|
| the right git identity (work vs personal) | git's `includeIf` by folder | `git-identities` |
| cloud project, cluster, account, secrets | a `.envrc` file | `direnv` |
| tool versions (node, terraform, python…) | a `mise.toml` file | `mise` |

**git-identities** asks for your work folder and work email. Every repo under that folder commits with the
work email; everything else keeps your usual one. Extra work-only settings (signing key, SSH key) go in
`~/.gitconfig-work`.

**direnv** loads a project's `.envrc` when you enter the folder and unloads it when you leave. Run `direnv allow`
once per new or changed file (a cloned repo can't run code in your shell on its own):

```sh
# ~/work/client-a/.envrc
export CLOUDSDK_ACTIVE_CONFIG_NAME=client-a   # gcloud project/account for this client
export KUBECONFIG=$PWD/.kube/config            # only this client's clusters
export AWS_PROFILE=client-a
dotenv .env                                     # secrets from a git-ignored file
```

**mise** activates the tool versions a project declares, downloading each version once:

```toml
# ~/work/api/mise.toml
[tools]
node = "22"
terraform = "1.9.5"

[env]
DATABASE_URL = "postgres://localhost/api"
```

Rule of thumb: mise for versions and simple variables, direnv when you need shell logic.

## Add your own tools

The simple case is a few lines of YAML in your config:

```yaml
custom:
  - {id: btop, help: "Resource monitor", brew: btop, apt: btop}
sections:
  extra:
    tools: {btop: minimal}
```

For anything else, drop a Python file in `~/.config/rigsmith/artifacts/`:

```python
from rigsmith.backends import Brew, Cask
from rigsmith.model import Artifact, Snippet

Artifact(
    id="wezterm",
    help="GPU-accelerated terminal configured in Lua.",
    sources=[Cask("wezterm", os="darwin"), Brew("wezterm")],
    check="test -d /Applications/WezTerm.app || command -v wezterm",
    role="terminal",
)
```

Backends: `Brew`, `Cask`, `Apt`, `Krew`, `VSCodeExt`, `UvTool`, `Script`, `GitClone`, `NerdFont`.
Artifacts can also own zsh snippets (`shell=Snippet(...)`), whole files (`files=[File(...)]`), VS Code and
git settings (`settings=[VSCodeSetting(...), GitConfig(...)]`), a role, tags and notes. See
[DESIGN.md](DESIGN.md) for the full model.

Want a tool in the built-in library? Open an issue with the **New artifact** template. The bar is a widely used,
maintained tool that installs with Homebrew on macOS and Homebrew or apt on Linux.

## Platforms

macOS 14+ (Apple Silicon and Intel), Ubuntu 22.04 / 24.04 and Debian 12 (amd64, arm64). Homebrew is the
primary package manager on both, with apt for the few things that need it. zsh only, for now.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md): setup and tests, adding an artifact, end-to-end tests, releasing.

## License

[MIT](LICENSE)
