# rigsmith — Design

A CLI that sets up a fresh macOS or Debian/Ubuntu machine from a rich, extensible library of
installable **artifacts**, organized by **section/subsection** and **profile**.

```
curl -fsSL https://raw.githubusercontent.com/<owner>/rigsmith/main/install.sh | sh -s -- install
```

`install.sh` (~10 lines) installs uv if missing, then runs `uv tool run rigsmith "$@"`. A fresh machine needs
only `curl`. For automation, pin both moving parts: fetch `install.sh` from a release tag and set
`RIGSMITH_VERSION=X.Y.Z`, which runs `uv tool run rigsmith==X.Y.Z`. If uv is already present, `uvx rigsmith install` works directly.

## Vision

1. **Now:** port the author's terminal + VS Code + GCP/k8s setup into the engine (slices 1–7).
2. **Then:** grow the library with the famous, widely used tools from many languages and dev domains:
   Go, Rust, Java, Node, platform, backend, data engineering, ML…
3. **Finally:** ship **presets**, curated configs in `config/presets/` for common developer types. Someone
   lands on the repo, sees the catalog, picks the preset closest to them, and installs or forks it with `init`.

Design consequences: the library will hold hundreds of artifacts, so the picker needs search and the catalog needs
to be browsable on GitHub. Sections stay subject-based (what a tool *is*). Presets are role-based (who you *are*)
and are built from sections.

---

## 1. Vocabulary

| Term | Meaning |
|---|---|
| **Artifact** | One installable unit: a package plus the **integration** config the tool needs to work (shell snippet, file, settings keys). Has an id, help text, sources, optional role/tags/requires/notes. Optional **opinions** (aliases, themes, preferred settings) are separate artifacts that `requires` the tool (§3). |
| **Effect** | One concrete change an artifact makes: a package install, a snippet, a file, a settings key, a shell change, a script run. |
| **Receipt** | The state record of one effect: what operation happened and before/after evidence. Uninstall works from receipts (§7). |
| **Backend** | How something is installed: `Brew`, `Cask`, `Apt`, `Krew`, `VSCodeExt`, `UvTool`, `Script`, `GitClone`, `NerdFont`, `Release` (one binary from a release archive). One subclass per package manager. |
| **Library** | All artifacts known to rigsmith: built-in + user-added. |
| **Config (menu)** | YAML that scopes the library: which artifacts exist, how they're organized into sections/subsections, and which profile each belongs to. |
| **Profile** | Depth level. Ordered and cumulative: `minimal ⊂ standard ⊂ comprehensive`. |
| **Section / subsection** | Subject-matter grouping (`kubernetes/logs`, `cli/search`). Subject-first: VS Code extensions live with their subject. |
| **Role** | Exclusive slot only one artifact can fill (`prompt`, `editor`, `container-runtime`). |
| **Question** | A questionnaire entry whose answers set env prefs and/or exclude tagged artifacts. |
| **Selection** | The concrete set of artifacts to act on, produced from a config + questionnaire/flags + picker. |
| **Preset** | A curated config shipped in `config/presets/` for a developer type (`ml-engineer`, `backend-go`). Referenced by name with `-c`. Not to be confused with *profile* (depth). |

---

## 2. Commands

| Command | Reads | Does |
|---|---|---|
| `init` | whole library (or `--from CONFIG`) | Scope picker → writes a forked config → optional `$EDITOR` for restructuring → validate. Installs nothing. |
| `install` | active config | Questionnaire → picker (pre-ticked) → diff screen → confirm → run. |
| `scan` | active config (`--all`: whole library) | Read-only table: installed / missing / n/a, managed vs pre-existing, grouped by section/subsection, profile shown. |
| `uninstall` | active config | Picker of installed **managed** artifacts → confirm → run. |

`init` authors a menu. `install` orders from that menu.

### Arguments

```
rigsmith install   [IDS...] [-c CONFIG] [-p PROFILE] [-s SECTION[/SUB]]... [-y] [--dry-run]
rigsmith uninstall [IDS...] [-c CONFIG] [-p PROFILE] [-s SECTION[/SUB]]... [-y] [--dry-run] [--include-unmanaged]
rigsmith scan      [IDS...] [-c CONFIG] [-p PROFILE] [-s SECTION[/SUB]]... [--all] [--new]
rigsmith init      [--from CONFIG] [-o OUTPUT]
```

- Artifact ids are positional (`install eza fzf`).
- `-s terminal` selects a section; `-s terminal/search` a subsection (subsection names can repeat across sections).
- OR within a flag, AND across flags: `-p minimal -s infra -s python` = minimal artifacts in infra or python.
- Positional ids AND with filters: `install eza fzf -s cli` acts on those ids only if they're in `cli`.
- Flags pre-answer the matching questions; only the rest are asked.
- `--dry-run`: print the diff screen and exit.

### `-y` semantics

Non-interactive: no questionnaire, no picker, no confirm.

- **Profile:** `-p`, else the config's `answers.profile`, else `minimal`.
- **Roles and questions:** the config's `answers:` (§4), else the question default, else for roles: the already-installed
  provider, then the first in config order. Resolved answers are printed at the top of the run and the log.
- **Dependencies:** `requires` resolves against the **library**, not just the config. Dependencies outside the config are
  pulled in and listed as `(dependency)`.
- **Never removes anything.** It never replaces an installed role provider. If several providers of one role are already
  installed, it leaves them all and warns.

Two contracts:

| Use | Contract |
|---|---|
| Workstation convenience | Omitted answers use defaults and are logged. The same config may resolve differently after upgrading rigsmith. |
| Repeatable server / CI bootstrap | Pin the rigsmith version (`RIGSMITH_VERSION`) **and** every relevant answer in `answers:`. Then a run is deterministic for that (config, rigsmith version) pair. |

---

## 3. Artifacts (Python)

Artifacts are **instances**, grouped in modules under `src/rigsmith/library/`, one module per section.
Subclass `Artifact` only when a tool needs real logic.

```python
@backend("brew")
class Brew(Backend):
    bootstrap = "homebrew"          # auto-dependency
    def is_installed(self, pkg): ...
    def install(self, pkg): ...
    def uninstall(self, pkg): ...

eza = Artifact(
    id="eza",
    help="Modern ls with icons and git status. `ls`, `ll`, `lt` (tree).",
    sources=[Brew("eza")],          # resolved by platform before execution; see Platforms
    shell=Snippet("eza.zsh", phase=70),   # reads RIGSMITH_ICONS; works with or without a Nerd Font
)

nerd_font_meslo = Artifact(id="nerd-font-meslo", tags=["icons"], ...)   # dropped when icons=no

starship = Artifact(id="starship", role="prompt", sources=[Brew("starship")], ...)

eza_aliases = Artifact(             # opinion, split from the tool
    id="eza-aliases",
    help="Replace ls/ll/lt with eza.",
    requires=["eza"],
    shell=Snippet("eza-aliases.zsh", phase=70),
)

class Atuin(Artifact):
    def post_install(self):         # irreversible effect, run once (§7)
        run("atuin import auto")
```

**Integration vs opinion (curation rule).** Config the tool needs to function (`zoxide init`, fzf keybindings,
the gcloud PATH) stays inside the tool's artifact. Optional taste (aliases, themes, preferred settings) becomes a
separate artifact that `requires` the tool, so a config can include `eza` without `eza-aliases`. This is a review
decision, not something lint can judge semantically. Lint only checks the structural facts (`requires` resolves).
The PR template asks reviewers to check it.

Artifact fields:

| Field | Purpose |
|---|---|
| `id` | Unique, kebab-case. |
| `help` | 2–4 lines shown by `h` in the picker and by `scan --all`. Required. |
| `sources` | Ordered list of backend instances, optionally constrained by `os=` / `arch=` / `distro=`. Exactly one is chosen **before execution** (see Platforms). None matches → `n/a`. |
| `check` | How to detect presence **regardless of backend**. Default: `command -v <id>`; override for apps, fonts, extensions, renamed binaries. Backends only answer "did *I* install it". Prevents a brew-first setup from double-installing what apt already provides. |
| `shell` | Owned zsh snippet + phase. |
| `files` | Owned files (written whole, backed up if foreign). |
| `settings` | Keys merged into shared files (VS Code `settings.json`, `git config --global`). |
| `role` | Exclusive slot. At most one per artifact. |
| `tags` | Referenced by `Question`s (e.g. `icons`, `tui`, `fun`). |
| `requires` | Other artifact ids. |
| `notes` | Manual post-install steps, collected into "Next steps". |

Artifacts never know their section or profile; that's the config's job.

### Platforms

- **Supported platforms (v1), by name:** macOS 14+ (arm64, x86_64), Ubuntu 22.04 / 24.04, Debian 12 (amd64, arm64).
  The platform is detected as a tuple `(os, distro, version, arch)`. Unsupported platforms fail validation
  before anything runs, unless `--unsupported` is passed.
- **Brew is the primary backend on both OSes** (same names, current versions, no sudo after bootstrap,
  no `fdfind`/`batcat` renames). Native backends (`Apt`) are per-artifact alternatives, e.g. for linux-arm64
  where bottles are often missing.
- **Deterministic source selection:** the first source whose `os`/`distro`/`arch` constraints match the platform tuple
  is chosen during planning, and only that backend runs. There is no runtime probing and **no fallback after a
  mutation starts**. A failed install is reported as failed, not retried with another backend. Constraints use the
  same names as the supported list (`Apt("eza", distro="ubuntu>=24.04")`).
- Brew bootstrap on Linux is not sudo-free: the `homebrew` artifact `requires` an `apt-base` artifact
  (`build-essential`, `curl`, `git`, `procps`) and needs sudo once to create `/home/linuxbrew`.
- Casks are mac-only; Linux equivalents (e.g. `NerdFont` download to `~/.local/share/fonts`) or `n/a`.
- dnf/pacman: future community backends (one `Backend` subclass each).

### Synonyms

- **Exclusive** synonyms share a `role` (p10k vs starship, colima vs OrbStack vs Docker Desktop, eza vs lsd).
  Picker renders them as radio buttons; default = **the already-installed provider**, else first in config order.
  Replacement only happens when the user explicitly picks another provider; the diff screen then asks
  `starship replaces p10k → uninstall p10k? [y/N]`. **`-y` never replaces an installed provider.**
- **Overlapping** tools (htop + bottom) are not modeled. Curate them in the config (different profiles, or drop one).

---

## 4. Config (YAML)

```yaml
profiles: [minimal, standard, comprehensive]

sections:
  cli:
    search:
      ripgrep: minimal
      fd: minimal
      fzf: minimal
  shell:
    prompt:
      p10k: minimal
      starship: minimal        # same role → radio, p10k is default (first)

questions:
  skip: [fun]

answers:                       # pre-answers; used by -y and as interactive defaults
  profile: standard
  prompt: p10k                 # role
  icons: "yes"                 # question

custom:                        # simple user artifacts, inline
  - id: btop
    help: Resource monitor.
    brew: btop
    apt: btop
```

- **Lookup order:** `-c PATH|PRESET` → `~/.config/rigsmith/config.yaml` → `config/reference.yaml` (built-in).
  `-c` accepts a file path or a preset name (`-c ml-engineer` → `config/presets/ml-engineer.yaml`); same for `init --from`.
- **Full replace, no inheritance.** A user config is a forked menu; what's in the file is exactly what you get.
- **New-in-library hint:** `scan` ends with `ℹ N new artifacts in the library not in your config — scan --all --new`.
  `init --from <your config>` shows them unticked.
- **User artifacts:** inline `custom:` entries, or `.py` files in `~/.config/rigsmith/artifacts/` (auto-imported
  into the registry). Both load before the config resolves.

### Validation (on load and after `init` editing)

Unknown artifact ids · `requires` cycles or dangling refs · roles referencing missing artifacts ·
unknown questions in `skip` · empty sections/subsections · unknown profile names ·
`answers:` naming unknown roles/questions or invalid choices.

### Repo configs

- `config/reference.yaml`: the full menu, with every built-in artifact and the canonical taxonomy. A CI test fails if a
  built-in artifact is missing from it.
- `config/example.yaml`: the author's work config. A curated fork and the demo for `-c`.
- `config/presets/*.yaml`: curated menus per developer type (`backend-go.yaml`, `rust.yaml`, `platform.yaml`,
  `data-engineer.yaml`, `ml-engineer.yaml`…). Each is a full menu with no inheritance, consistent with full replace.
  Sections like `python` repeat across presets; library lint validates every preset, so the repetition can't silently break.
  **Presets pin every relevant answer** (profile, each role with ≥ 2 candidates, each referenced question), enforced by
  lint, so `-y -c <preset>` is reproducible for a given rigsmith version.

All are packaged into the wheel via hatch `force-include` and read with `importlib.resources`.

---

## 5. Questionnaire

The engine hardcodes **no** tool-specific questions. Everything is derived from the menu:

| Source | Derived from |
|---|---|
| Profile | `profiles:` |
| Sections | `sections:` (multi-select) |
| Roles | every role with ≥ 2 artifacts in the menu → radio question |
| Questions | `Question` objects in the library, asked **only if an artifact in the menu references them** |

```python
icons = Question(
    id="icons",
    text="Show icons in the terminal? (needs a Nerd Font)",
    choices={
        "yes": {"env": {"RIGSMITH_ICONS": "1"}},
        "no": {"exclude_tags": ["icons"]},
    },
)
```

- `env` answers are written to `shell.d/10-prefs.zsh`; snippets adapt: `alias ls="eza ${RIGSMITH_ICONS:+--icons}"`.
  One snippet handles every answer, with no variant system.
- `exclude_tags` drops tagged artifacts from the pre-ticked selection.
- Config can disable questions: `questions: {skip: [...]}`.

Built-in questions (initial): icons, replace classic commands (aliases), full-screen TUIs, fun stuff, color theme.

---

## 6. TUI screens (Textual)

1. **Questionnaire**: one question per screen, defaults highlighted.
2. **Picker**: tree of section → subsection → artifact, ordered by profile.
   `space` toggle · `h` help popup · `/` search (id, help, section) · `tab` collapse/expand · radio rows for roles · greyed rows for `n/a` or
   unmet `requires`. In `init` mode, `1/2/3` sets the artifact's profile.
3. **Diff / confirm**: already installed vs to install (vs to replace, vs to uninstall), then confirm.
4. **Run**: live progress `[12/38] installing lazygit…`, then a ✓/✗/⊘ summary plus "Next steps".

`scan` output and the progress line use rich.

---

## 7. Execution

- **Dependencies:** `requires` + backend bootstrap (`Brew → homebrew`, `Krew → krew`, `VSCodeExt → vscode`),
  topologically sorted.
- **Sequential** installs.
- **Failure:** continue; dependents of a failed artifact are skipped (`⊘ atuin: skipped, fzf failed`).
  Re-running `install` retries only what's missing.
- **Idempotent:** a second `install` with the same selection performs **no mutations**. Every effect checks its
  current state before acting, and the run reports `0 changes`.
- **sudo:** if any step needs it (apt, chsh), prompt once before starting and keep the session alive.
- **Notes:** collected into a "Next steps" block at the end.
- **Logs:** `~/.local/state/rigsmith/logs/<timestamp>.log`.
- **State:** `~/.local/state/rigsmith/state.json`, a list of **receipts**, one per effect.

### Receipts (undo log)

Ownership is recorded **per effect**, not per artifact. eza installed earlier via apt plus a snippet written by
rigsmith gives two receipts: `package: noop` and `snippet: created`. Uninstall removes the snippet and leaves eza.

| Operation | Recorded | Undo |
|---|---|---|
| `noop` | nothing changed (already present) | nothing |
| `created` | the value or hash written (`after`) | remove, **only if current still equals `after`** |
| `modified` | `before` and `after` | restore `before`, **only if current still equals `after`** |
| `irreversible` | that it ran, and when | none. Kept and reported |

- Packages are usually `created` or `noop`. Files, keys and shell changes are `created` or `modified`.
  Example: `"editor.fontSize": 14 → 16` is `modified`, and uninstall restores 14 if the value is still 16.
  `chsh` is `modified`, and the previous shell is restored only if the current shell is still the one rigsmith set.
- If the current value differs from `after`, the user changed it since install. Uninstall keeps it and warns.
- **Irreversible effects** (`post_install` hooks like the atuin import, `Script` without an `undo`) are listed on the
  diff screen before confirm. Once they succeed, the receipt marks them done, so a second install doesn't rerun them
  just because their side effect can't be inspected.

### Detection vs ownership

- `scan` checks the **real system** (the artifact's `check`). Receipts say who owns the package:
  `✓ eza (managed)` · `✓ git (pre-existing)` · `✗ k9s` · `– iterm2 (n/a)`.
- `uninstall` also takes the **dependencies the plan pulled in**, unless the user requested them explicitly
  (state records requested artifacts) or another managed artifact still needs them, like `brew autoremove`.
- `uninstall` reverses an artifact's receipts. For a pre-existing package, that removes rigsmith's snippets, files and
  keys and leaves the package. `--include-unmanaged` also removes packages rigsmith didn't install.
- Uninstalling something others depend on warns: `⚠ needed by: atuin. Remove them too? [y/N]`.

---

## 8. Shell integration (zsh only, v1)

`zsh` is a `minimal` artifact (on Linux it also runs `chsh`). Bash is deferred: same mechanism via
`~/.bashrc`, but every snippet would need a bash variant.

rigsmith **never overwrites `~/.zshrc`**. It inserts one marked block at the top:

```zsh
# >>> rigsmith >>>
source ~/.config/rigsmith/init.zsh
# <<< rigsmith <<<
```

User content stays below it, so user overrides win. `init.zsh`:

```zsh
for f in ~/.config/rigsmith/shell.d/*.zsh(N); do
  source "$f"
done
```

Each artifact's snippet is written as `shell.d/<phase>-<id>.zsh`:

| Phase | Content |
|---|---|
| `00` | p10k instant prompt |
| `10` | env, PATH, prefs |
| `20` | framework |
| `30` | plugins (zinit) |
| `50` | tool init (zoxide, atuin, fzf) |
| `70` | aliases, functions |
| `90` | prompt finalize |

Uninstalling an artifact deletes its snippet. The marked block is removed when the last snippet is gone.

**Machines that aren't fresh:** before the first install, rigsmith scans the existing `~/.zshrc` for lines that would
double-load with its snippets (`source $ZSH/oh-my-zsh.sh`, `zinit`, `p10k`, `eval "$(zoxide init`, `compinit`…)
and warns with line numbers on the diff screen. It never edits user lines. The patterns are data, declared
by the artifacts that own the equivalent snippet.

## 9. Other owned config

| Kind | Examples | Behavior |
|---|---|---|
| Whole file | `~/.p10k.zsh`, atuin `config.toml`, iTerm colors | `created` if absent; `modified` if a foreign file existed (it is also backed up as `.bak.<timestamp>`). |
| Keys in a shared file | VS Code `settings.json` | Merge only our keys; each key gets its own receipt (`created` or `modified`). OS-specific paths handled by the artifact layer. **Known limit:** JSONC comments are lost on rewrite; the file is backed up before every write. |
| Tool-managed settings | `git config --global core.pager delta` | Per-key receipt, same rules. |

**The promise: rigsmith reverses the effects it tracks, and never overwrites a change made after install.**
Undo follows the receipt rules in §7, so a `~/.p10k.zsh` rewritten by `p10k configure` is kept with a warning.
What this promise does not cover: irreversible effects (listed before confirm) and JSONC comments lost on a
settings rewrite. For both, the backups are a recovery path, not undo.

---

## 10. Default taxonomy (`config/reference.yaml`)

m/s/c = minimal/standard/comprehensive. ◉/○ = role radio.

```
shell        core        zsh(m) zinit(m)
             prompt      ◉p10k(m) ○starship(m)                     role: prompt
             plugins     autosuggestions(m) syntax-highlighting(m) completions(s) history-substring(s)
             history     atuin(s)
             helpers     navigation+safety aliases(m) mkcd/extract/bak(s) note/weather(c)
terminal     emulator    iterm2(s, mac)                             role: terminal
             fonts       meslo-nf(m) jetbrains-nf(c) fira-nf(c)
             theme       catppuccin-iterm(s)
cli          files       eza(m) tree(s) yazi(c)
             search      ripgrep(m) fd(m) fzf(m)
             view-edit   bat(m) sd(s) micro(s)
             navigation  zoxide(m)
             data        jq(m) yq(s)
             system      htop(s) bottom(c) dust(s) duf(s) procs(c)
             network     httpie(s) wget(s)
             docs        tldr(s)
             misc        thefuck(c) watch(s) tokei(c) hyperfine(c)
git          core        git(m) gh(s) git-aliases(m)
             ui          lazygit(s) gitlens-ext(s) git-graph-ext(c)
             diff        delta(s)
python       tooling     uv(m) python(m) python-ext(m) ruff-ext(s) ty-ext(s) jupyter-ext(c)
containers   runtime     ◉colima(s) ○orbstack ○docker-desktop       role: container-runtime
             tools       dive(c) docker-ext(s)
kubernetes   core        kubectl(m) kubectx(m) helm(s) k8s-ext(s) helm-ext(c)
             ui          k9s(s)
             logs        stern(s)
             plugins     krew(c) +neat/tree/images/get-all/whoami(c)
             validate    kubeconform(c) popeye(c) kube-score(c)
             local       kind(s)
             gitops      argocd(c)
cloud        gcp         gcloud(m) gke-auth-plugin(m) gcp-aliases(s) cloudcode-ext(c)
iac          terraform   terraform(m) tflint(s) terraform-ext(s) terragrunt(c) tfsec(c) infracost(c)
editor       vscode      vscode(m) catppuccin-theme(s) errorlens(s) indent-rainbow(c) todo-tree(c) …
             remote      remote-ssh(s) dev-containers(s) liveshare(c)
             ai          copilot(s) continue(c)
web          tooling     node(s) eslint-ext(s) prettier-ext(s) tailwind/volar/svelte-ext(c)
data         db          sqltools(c) sqlite-viewer(c) rainbow-csv(s) mongodb/redis-ext(c)
docs         markdown    markdown-all-in-one(s) mermaid(s) drawio(c)
fun          —           fastfetch cmatrix lolcat figlet cowsay pipes-sh sl power-mode pets  (all c)
```

VS Code extensions `requires: [vscode]` and are greyed out only if vscode is neither selected nor already installed.
The same rule applies to every `requires`.

Curation decisions vs the legacy scripts:
- oh-my-zsh dropped; zinit loads the needed OMZ plugins (`zinit snippet OMZP::git`).
- krew `ctx`/`ns` dropped (duplicate kubectx).
- Duplicate `extract` dropped (OMZ plugin vs custom function).
- tfsec → trivy (tfsec is deprecated in favor of trivy); krew `score` → `kube-score`.
- thefuck kept (its successor pay-respects isn't in Homebrew core yet).
- Commented-out Go/Rust/C++ extensions not ported; future `go`/`rust` sections.

---

## 11. Stack

| Need | Choice |
|---|---|
| CLI | typer |
| Interactive screens | Textual |
| Tables, progress | rich |
| YAML (comment/order preserving) | ruamel.yaml |
| Models | dataclasses + a validation function |
| Python | `requires-python >= 3.14` (bump to 3.15 once stable and deps ship wheels) |
| Packaging | uv, hatch, PyPI (`uvx rigsmith`, `uv tool install rigsmith`) |
| Dev | ruff, ty, pytest |

---

## 12. Repo layout

```
rigsmith/
  README.md
  DESIGN.md
  install.sh                    bootstrap: install uv if missing → uv tool run rigsmith[==RIGSMITH_VERSION]
  pyproject.toml
  config/
    reference.yaml
    example.yaml
    presets/                    backend-go.yaml, rust.yaml, data-engineer.yaml, ml-engineer.yaml …
  docs/
    CATALOG.md                  generated from the library; CI fails if stale
  scripts/
    gen_catalog.py
  .github/
    workflows/
      ci.yml                    ruff check/format, ty, pytest (unit + library lint): every PR
      e2e.yml                   ubuntu container + macos runner: minimal on PR, all profiles nightly
      release.yml               tag v* → build → PyPI trusted publishing
    ISSUE_TEMPLATE/
      bug.yml
      new-artifact.yml          brew/apt names, section, profile, role
    pull_request_template.md    help text, in reference.yaml, snippet phase, integration vs opinion split, tested on mac/linux
    dependabot.yml              pip + github-actions
  src/rigsmith/
    cli.py                      typer commands, plan report
    model.py                    Platform, Artifact, Question, Backend base, registries
    backends.py                 Brew, Cask, Apt, Script, GitClone, Krew, VSCodeExt, UvTool, NerdFont
    config.py                   load, resolve, validate, fork (for init)
    plan.py                     filters, questions, roles, dependency closure, toposort
    effects.py                  package / file / login-shell / post-install effects
    settings.py                 VS Code settings.json (JSONC) and git config effects
    state.py                    receipts (undo log)
    runner.py                   install / uninstall from receipts, sudo keepalive, logs, status
    shell.py                    ~/.zshrc block, init.zsh, prefs, overlap warnings
    tui.py                      questionnaire, picker (help, search, init mode), confirm
    library/                    one module per section
      snippets/                 *.zsh
      files/                    Catppuccin-Mocha.itermcolors
  scripts/check_sources.py      every brew/cask name and VS Code extension id exists
  tests/                        unit, library lint, CLI, TUI (pilot); e2e/ for CI only
```

---

## 13. Testing

1. **Engine unit tests** with a `FakeBackend` (an in-memory installed set): filters, roles, question relevance,
   `-y` resolution, deterministic source selection per platform tuple, toposort, skip-on-failure, receipt operations
   (`noop`/`created`/`modified`/`irreversible`, including "changed since install → kept"), idempotency.
2. **Library lint:** unique ids; every built-in artifact in `reference.yaml`; referenced snippets/files exist;
   `help` non-empty; `requires`/role/question refs resolve; every preset and `example.yaml` validates;
   presets pin every relevant answer; `docs/CATALOG.md` matches `gen_catalog.py` output.
3. **E2E (CI):** pushes and PRs run the minimal core; a weekly run installs every preset, one Ubuntu container
   each (bounded disk); manual runs take any filters. macOS runs only on pushes and manual runs (billed 10× on
   private repos). The cycle: ubuntu container (as a **non-root user with sudo**; brew refuses root) + macOS runner:
   `install -p minimal -y` → `scan` (all ✓) → **second `install -p minimal -y` reports 0 changes** →
   `uninstall -y` → `scan` (**managed** artifacts ✗, pre-existing ones untouched, `~/.zshrc` byte-identical to the
   original). Runners ship brew, git, jq…, so "all ✗" would be wrong.
   Plus `install -c config/example.yaml -y`. Standard/comprehensive run nightly.
4. **Brew bootstrap:** the Ubuntu job runs in a bare `ubuntu:24.04` container, so it installs Homebrew from
   scratch on every run. Hosted macOS runners ship Homebrew, so the macOS bootstrap path is only exercised
   on a clean VM (e.g. Tart) by hand before releases.

---

## 14. Delivery slices

1. **Engine + `scan`**: model, Brew/Cask/Apt, config loading, ~15 artifacts from `shell` and `cli`.
   Check: `rigsmith scan` on a real Mac is correct.
2. **`install -y` + `install.sh`**: receipts, deps, deterministic sources, `answers:`, shell.d, zshrc block, sudo.
   Check: e2e green on ubuntu + macOS, and the **second install reports 0 changes**.
3. **`uninstall -y`**: receipt-driven undo. Check: e2e uninstall leaves pre-existing packages, restores `modified`
   keys, keeps user-changed files, and `~/.zshrc` is byte-identical.
4. **TUI**: questionnaire, picker, diff/confirm. Check: interactive install on a fresh VM (Tart / Multipass).
5. **`init`**: scope picker → fork → `$EDITOR` → validate.
6. **Port the library**: git, python, k8s, cloud, iac, VS Code extensions + settings merge, fun, with opinions
   split from tools. Check: library lint + `scan --all` matches the legacy setup.
7. **Publish**: README, `example.yaml`, PyPI release, public repo.
8. **Grow the library**: one section per PR (go, rust, java, node, data, ml, platform…), each meeting the
   inclusion policy below. Adds picker `/` search and `docs/CATALOG.md` generation once the library passes ~150 artifacts.
9. **Presets**: `config/presets/*.yaml` per developer type, each pinning its answers; `-c <preset>` name resolution;
   README points to the catalog and the presets ("start from the closest preset, fork with `init --from`").

### Inclusion policy (for slice 8 and community PRs)

An artifact is accepted if it is **widely used** (a de facto standard in its ecosystem, or a well-known modern
replacement), **actively maintained**, and **installable via brew on macOS + (brew or apt) on Linux**, or
explicitly marked mac-only/linux-only. Niche tools belong in user `custom:` entries or `~/.config/rigsmith/artifacts/`,
not in the built-in library.

## 15. Legacy migration

- `git init`, then commit the legacy folders (`ultimate-cli/`, `gcp-kube/`, `vscode-ultimate/`) as-is first, so the port shows up as a diff.
- Per-tool explanations from the legacy `.md` files become each artifact's `help`.
- Cheatsheets (alias tables, keybindings) become header comments in the snippets they describe.
- Legacy folders are deleted after slice 6.
- README: one-line install, TUI GIF, the 4 commands, "add your own artifact", "write your own config with `init`".
  After slice 9: leads with "browse the catalog → pick a preset → `rigsmith install -c <preset>`".

### Upstream drift

Formulae get removed (tflint left Homebrew core over its license), extensions become built in (Copilot Chat).
`scripts/check_sources.py` checks every name against the live formulae.brew.sh API and the VS Code Marketplace,
weekly in CI (`sources.yml`), because local Homebrew metadata can be stale.

## Deferred

Bash support · dnf/pacman backends · JSONC comment preservation · cheatsheet printing (`scan --verbose`) ·
CHANGELOG (GitHub releases carry generated notes) / docs site · remote configs (`-c https://…`).
