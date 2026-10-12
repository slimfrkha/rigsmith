# rigsmith: design

How rigsmith works and why it works that way, for contributors and anyone deciding whether to trust it with their
machine. Flags, config keys and fields are in the [reference](docs/reference.md); tasks are in the
[guide](docs/guide.md).

- [Vocabulary](#vocabulary)
- [Configs: the menu](#configs-the-menu)
- [Artifacts](#artifacts)
- [Questionnaire and picker](#questionnaire-and-picker)
- [Execution and receipts](#execution-and-receipts)
- [Shell integration](#shell-integration)
- [Other owned config](#other-owned-config)
- [Non-goals](#non-goals)
- [Stack and layout](#stack-and-layout)
- [Testing](#testing)
- [Deferred](#deferred)

## Vocabulary

| Term | Meaning |
|---|---|
| **Artifact** | One installable unit: a package plus the **integration** config the tool needs to work (snippet, file, settings). Optional **opinions** (aliases, themes, preferred settings) are separate artifacts that `requires` the tool. |
| **Backend** | How a package gets installed: one class per package manager (`Brew`, `Cask`, `Apt`, `Release`…). |
| **Library** | Every artifact rigsmith knows: built in, plus the user's own. |
| **Config (menu)** | YAML that scopes the library: which artifacts are in scope, in which section and subsection, at which profile. |
| **Preset** | A bundled config for a kind of developer (`platform`, `ml-engineer`). Not to be confused with a profile. |
| **Profile** | Depth, ordered and cumulative: `minimal ⊂ standard ⊂ comprehensive`. |
| **Section / subsection** | What a tool *is* (`kubernetes/logs`). Presets cover who you *are*. |
| **Role** | An exclusive slot only one artifact fills at a time (`prompt`, `editor`, `container-runtime`). |
| **Question** | A questionnaire entry whose answer sets environment preferences, skips tagged artifacts, or fills a placeholder. |
| **Effect** | One concrete change: a package install, a snippet, a file, a settings key, a login-shell change, a one-time script. |
| **Receipt** | The record of one effect: what happened, with before/after evidence. Uninstall works from receipts. |

## Configs: the menu

A config decides what's on the menu; the questionnaire and picker decide what's ordered from it.

- **`use` copies, it doesn't point.** `rigsmith use platform` copies the preset to `~/.config/rigsmith/config.yaml`,
  with a first-line marker naming its origin. A pointer would follow the preset as it evolves, but an upgrade could
  silently change what `install` does, and you couldn't edit it. When the library gains artifacts your config lacks,
  `scan` says so and `init --from` offers them unticked.
- **Full replace, no inheritance.** A config is a complete menu: what's in the file is what you get. Presets repeat
  sections like `python`; library lint validates every preset, so the repetition can't silently break.
- **One state, made visible.** The user config file *is* the remembered choice, and every command prints which config
  it's using. A second mechanism (a pointer, an "active env") would give two answers to "which config is active?".
- **Presets pin every answer** (profile, every role with two or more providers, every referenced question), enforced
  by lint. `install -c <preset> -y` then gives the same result for a given rigsmith version. Without pins, a library
  default changing in an upgrade would change a CI bootstrap.
- **Lookup order:** `-c` (path or bundled name) → user config → bundled `reference`. Bundled configs ship inside the
  wheel (hatch `force-include`) and are read with `importlib.resources`.
- **First run:** an interactive `install` with no config of its own asks "Start from which menu?" before the
  questionnaire, so presets are discoverable without reading docs.

## Artifacts

Artifacts are Python instances in [`src/rigsmith/library/`](src/rigsmith/library), one module per section. Subclass
`Artifact` only when a tool needs real logic.

```python
tool("eza", "Modern ls with colors, git status and optional icons.")  # Brew("eza"), detected by `eza` on PATH

Artifact(  # an opinion, split from the tool
    id="eza-aliases",
    help="ls/ll/la/lt → eza.",
    requires=["eza"],
    shell=Snippet("eza-aliases.zsh", 70),
    tags=["aliases"],  # the aliases question can skip it
    prefs=["icons"],  # its snippet reads RIGSMITH_ICONS
)


class Atuin(Artifact):
    def post_install(self) -> None:  # irreversible, run once
        run("atuin import auto", check=False)
```

Artifacts never know their section or profile; that's the config's job.

**Integration vs opinion.** Config a tool needs to work (`zoxide init`, fzf key bindings, the gcloud PATH) stays in
its artifact. Taste (aliases, themes, preferred settings) is a separate artifact, so a config can take `eza` without
`eza-aliases`. This is a review rule: lint only checks that `requires` resolves.

**Detection is separate from installation.** An artifact is present if its `check` command succeeds, its binary is on
PATH (`bin`), or its backend lists it, in that order, regardless of who installed it. Without this, a brew-first
setup would reinstall what apt already provides, and `scan` would lie.

### Platforms and sources

- **Supported:** macOS 14+ (arm64, x86_64), Ubuntu 22.04 / 24.04, Debian 12 (amd64, arm64). The platform is the tuple
  `(os, distro, version, arch)`; anything else fails before running, unless `--unsupported`.
- **Homebrew first on both OSes:** same names, current versions, no sudo after bootstrap, and none of apt's renames
  (`fdfind`, `batcat`). Apt is a per-artifact alternative, for example where Linux bottles are missing.
- **One source, chosen up front.** The first source whose `os`/`distro`/`arch` matches is chosen during planning, and
  only that backend runs. There's no runtime probing and no fallback once something has changed: a failure is
  reported, not retried elsewhere.
- **Linux Homebrew isn't sudo-free:** `homebrew` requires `apt-base` (build tools) and needs sudo once.
- **Casks are mac-only;** Linux gets an equivalent (`NerdFont` for fonts) or the artifact is `n/a`.

### Roles

Exclusive alternatives (p10k vs starship, colima vs OrbStack vs Docker Desktop) share a `role`. The picker shows them
as radio buttons, defaulting to **the provider already installed**, else the first in config order. Replacing one
happens only when you pick another explicitly, and `-y` never replaces an installed provider. A role is the arbitration between synonyms: a config can list every alternative, `answers:` pins the
active one, and `uninstall --inactive` removes installed providers that aren't active (pre-existing ones included,
since that's the explicit intent). With several installed and nothing pinned, rigsmith reports it and doesn't guess.
Tools that overlap but stay useful side by side (fzf and peco, kubectl and k9s) get no role.

## Questionnaire and picker

The engine hardcodes no tool-specific questions. Everything comes from the menu:

| Asked | Derived from |
|---|---|
| Profile | `profiles:` |
| Sections | `sections:` |
| One question per role | every role with two or more providers in scope |
| Library `Question`s | only those an artifact in scope references (by tag or `prefs`) |

Why: a Rust developer's config never asks about icons or GCP, and a new question added by a contributor appears
without engine changes.

- **Choice answers** set environment variables (written to `shell.d/01-rigsmith-prefs.zsh`) or skip tagged artifacts.
  Snippets read the variables (`alias ls="eza ${RIGSMITH_ICONS:+--icons}"`), so one snippet serves every answer and
  there's no variant system.
- **Text answers** (`kind="text"`, e.g. the work folder) fill `{{question-id}}` placeholders in git settings. A
  setting that's still unanswered or empty is skipped rather than written half-filled.
- **Answers are remembered** in state: they're the next run's defaults, and `scan`/`uninstall` use them to rebuild the
  exact keys. Precedence: explicit → config `answers:` → remembered → default.
- **Questions for artifacts ticked in the picker** are asked right after the picker.
- **The picker** is a tree of section → subsection → artifact with live status. `n/a` rows can't be ticked, and a row
  whose requirement is neither selected nor installed is greyed.

## Execution and receipts

- **Order:** `requires` plus each backend's bootstrap (`Brew` → `homebrew`, `VSCodeExt` → `vscode`), resolved
  against the whole library (not just the config) and topologically sorted. Installs run one after another.
- **Failure:** keep going; artifacts that depend on a failed one are skipped. Running `install` again retries only
  what's missing.
- **Idempotent:** every effect compares current and desired state first, so a second run reports `0 changes`.
- **sudo:** asked once, up front, only if a step needs it, then kept alive for the run.

### Receipts

Ownership is recorded **per effect**, not per artifact. eza installed earlier with apt, plus a snippet rigsmith wrote,
gives two receipts: `package: noop` and `snippet: created`. Uninstall removes the snippet and leaves eza.

| Operation | Recorded | Undo |
|---|---|---|
| `noop` | it was already there | nothing |
| `created` | what rigsmith wrote | remove it, **only if it's still what rigsmith wrote** |
| `modified` | before and after | restore before, **only if it's still what rigsmith wrote** |
| `irreversible` | that it ran | nothing; reported |

- **A value changed since install is the user's.** Uninstall keeps it and warns. That's the core promise: rigsmith
  reverses the effects it tracks and never overwrites a change made after install.
- **Irreversible effects** (installing Homebrew, importing shell history) are listed before you confirm, and once
  done they're never rerun just because their result can't be inspected.
- **Pulled in by this run means owned.** A package missing when the run started that appears before its own step
  (an extension pulled in by another) is recorded as `created`, not `noop`.
- **Uninstall works from receipts, not the active config**, so artifacts installed from a previous config stay
  removable after `use` switches menus. It also removes managed dependencies the plan pulled in, unless the user
  requested them or something else managed still needs them (`brew autoremove` logic, looking through dependencies
  rigsmith doesn't manage). Removing something others need prints a warning; they stay installed.
- **Multi-package backends snapshot what existed**, so uninstalling `apt-base` never removes a `git` that was there
  before.

## Shell integration

zsh only for now: every snippet would need a bash variant. `zsh` is a minimal artifact, and on Linux it also changes
the login shell (a `modified` receipt that restores the previous one).

rigsmith **never rewrites `~/.zshrc`**. It inserts one marked block at the top:

```zsh
# >>> rigsmith >>>
source ~/.config/rigsmith/init.zsh
# <<< rigsmith <<<
```

The user's own lines stay below, so their overrides win. `init.zsh` sources `shell.d/*.zsh` in name order, and each
snippet is named `<phase>-<id>.zsh`, so the phase number sets load order (instant prompt first, prompt last; phases
are in the [reference](docs/reference.md#artifacts)). Uninstalling an artifact deletes its snippet; the block goes when
the last snippet does, leaving `~/.zshrc` byte-identical to before.

On machines that aren't fresh, artifacts declare `conflicts` (regexes for lines that would load the same thing), and
the plan lists matching lines from the user's `~/.zshrc` with line numbers. rigsmith never edits them.

## Other owned config

| Kind | Examples | Behavior |
|---|---|---|
| Whole file | iTerm colors | `created` if absent; `modified`, after a backup, if a foreign file existed |
| Keys in a shared file | VS Code `settings.json` | Only rigsmith's keys, one receipt each. Comments in the file are lost on rewrite, so it's backed up before every write |
| Git settings | `git config --global core.pager delta`, `~/.gitconfig-work` | One receipt per key. A file rigsmith created is removed again once empty |

## Non-goals

- **Package isolation and environments.** Per-environment visibility of installed tools is what Nix (and devbox/flox)
  do properly; rebuilding it on Homebrew with unlinked kegs and symlink farms would be a worse Nix. The real needs
  behind "environments" are per-directory, and existing tools switch them automatically: git `includeIf`
  (`git-identities`), direnv and mise, all in the library. A manual "active environment" fails the usual way: you
  forget to switch.
- **Fully declarative machines.** rigsmith changes a normal machine reversibly instead of owning it.

## Stack and layout

| Need | Choice |
|---|---|
| CLI | typer |
| Interactive screens | Textual |
| Tables, progress | rich |
| YAML that keeps comments (for `init`) | ruamel.yaml |
| Models | dataclasses and a validation function |
| Python | `requires-python >= 3.14`; run with `uvx`, so users don't need it installed |
| Dev | uv, ruff, ty, pytest, pre-commit |

```text
src/rigsmith/
  cli.py          commands, plan report
  model.py        Platform, Artifact, Question, Backend base, registries
  backends.py     one class per package manager
  config.py       load, resolve, validate, fork (init), use (copy, labels)
  plan.py         filters, questions, roles, dependency closure, order, orphans
  effects.py      package / file / login-shell / one-time effects
  settings.py     VS Code settings.json and git config effects
  state.py        receipts, requested artifacts, remembered answers
  runner.py       install / uninstall from receipts, status, sudo, logs
  shell.py        ~/.zshrc block, init.zsh, prefs, overlap warnings
  tui.py          start-from menu, questionnaire, picker, confirm
  library/        artifacts by section; snippets/*.zsh; files/
config/           reference.yaml, example.yaml, presets/*.yaml
docs/             guide, reference, CATALOG (generated by scripts/gen_catalog.py), screenshots
scripts/          gen_catalog.py, check_sources.py
tests/            unit, library lint, CLI, TUI; e2e/ (CI only)
```

## Testing

1. **Unit tests** use a fake backend and a throwaway `HOME`: filters, roles, questions, source selection, ordering,
   failure handling, every receipt operation, idempotency. They never touch the real machine.
2. **Library lint** keeps a growing library honest: unique ids, every artifact in `reference.yaml`, snippets and
   files exist, help text present, references resolve, every bundled config validates, presets pin their answers,
   the catalog is current, links in the docs resolve.
3. **End-to-end** runs the real cycle on throwaway machines: install → verify → reinstall (must be `0 changes`) →
   uninstall → verify (only managed artifacts gone, pre-existing ones kept, `~/.zshrc` byte-identical). The Ubuntu
   job is a bare container, so it installs Homebrew from scratch every time; hosted macOS runners already ship
   Homebrew, so the macOS bootstrap is checked by hand on a clean VM before releases. When each job runs is in
   [CONTRIBUTING](CONTRIBUTING.md#end-to-end-tests).
4. **Upstream drift:** formulae get removed (tflint left Homebrew core over its license) and extensions become built
   in (Copilot Chat). `scripts/check_sources.py` checks every name against the live Homebrew API and the VS Code
   Marketplace, weekly in CI, because local Homebrew metadata can be stale.

## Deferred

Bash support · dnf/pacman backends · keeping comments in VS Code settings · remote configs (`-c https://…`) · a
CHANGELOG (GitHub releases carry generated notes) · a docs site.
