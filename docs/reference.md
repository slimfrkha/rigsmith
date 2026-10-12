# Reference

Every command, config key, artifact field, file and variable rigsmith uses. For step-by-step tasks see the
[guide](guide.md); for why things work this way see [DESIGN.md](../DESIGN.md).

- [Commands](#commands)
- [Filters](#filters)
- [Config file](#config-file)
- [Questions](#questions)
- [Artifacts](#artifacts)
- [Backends](#backends)
- [Files and environment](#files-and-environment)
- [Exit codes](#exit-codes)

## Commands

### `rigsmith use [SOURCE]`

Copies a preset or a YAML file to your config, `~/.config/rigsmith/config.yaml`. The copy is yours to edit and
upgrades never change it. Without `SOURCE` it opens a picker (or prints the choices when there's no terminal).

| Option | Description |
|---|---|
| `SOURCE` | Preset name (`platform`, `python`, …), `example`, `reference`, or a path to a YAML file |
| `-y`, `--yes` | Replace an existing config without asking |

### `rigsmith install [IDS]...`

Questionnaire → picker → summary → install. On the first interactive run (no `-c`, no config of your own) it starts
by asking which menu to start from, and offers to save that choice as your config.

| Option | Description |
|---|---|
| `IDS` | Only these artifacts (combined with the filters) |
| `-c`, `--config` | Config file or preset name |
| `-p`, `--profile` | Profile cutoff, cumulative (`minimal` ⊂ `standard` ⊂ `comprehensive`) |
| `-s`, `--section` | `SECTION` or `SECTION/SUB`, repeatable |
| `-y`, `--yes` | No screens: pinned answers, then remembered ones, then defaults. Never replaces an installed role provider |
| `--dry-run` | Print the plan and exit |
| `--unsupported` | Run on a platform rigsmith doesn't support |

### `rigsmith scan [IDS]...`

What's installed (`✓`), partially configured (`◐`), missing (`✗`) or unavailable on this platform (`–`), by section,
and whether rigsmith installed it (`managed`) or it was already there (`pre-existing`).

| Option | Description |
|---|---|
| `IDS`, `-c`, `-p`, `-s` | As for `install` |
| `--all` | Scan the whole library, not just your config |
| `--new` | Only library artifacts your config doesn't list |

### `rigsmith uninstall [IDS]...`

Undoes what rigsmith installed, from its receipts, including artifacts installed from a config you've since
switched away from. Dependencies it pulled in go too, unless you asked for them yourself or something else needs them.

| Option | Description |
|---|---|
| `IDS`, `-c`, `-p`, `-s` | As for `install` |
| `-y`, `--yes` | No picker, no confirmation |
| `--dry-run` | Print what would be removed and exit |
| `--include-unmanaged` | Also remove packages that were installed before rigsmith |

### `rigsmith init`

Tailors a config: tick which artifacts it includes, set their profiles with `1`/`2`/`3`, then optionally
restructure the YAML in `$EDITOR` (re-validated until it's valid). Library artifacts the source doesn't list are
offered unticked.

| Option | Description |
|---|---|
| `--from` | Config or preset to start from (default: `reference`) |
| `-o`, `--output` | Where to write (default: `~/.config/rigsmith/config.yaml`) |

### Picker keys

| Key | Action |
|---|---|
| `space` | Tick / untick (a section or subsection toggles everything in it) |
| `enter` | Continue |
| `h` | Explain the highlighted artifact |
| `/` | Search by id, description or section (`esc` closes the search) |
| `tab` | Fold / unfold a section |
| `1` `2` `3` | Set the artifact's profile (`init` only) |
| `esc`, `q` | Quit |

## Filters

`install`, `scan` and `uninstall` take the same filters:

- **OR within a flag:** `-s python -s kubernetes` means either section.
- **AND across flags:** `-p minimal -s python` means minimal artifacts in python.
- **Ids narrow further:** `install fzf -s cli` installs fzf only if it's in `cli`.
- **Profile default:** without `-p`, `install` uses the config's `answers.profile`, else the first profile. Passing
  ids alone means no profile cutoff.

## Config file

```yaml
profiles: [minimal, standard, comprehensive]

sections:
  cli:
    search: {ripgrep: minimal, fzf: minimal, fd: standard}
  shell:
    prompt: {p10k: minimal, starship: minimal}

answers:
  profile: standard
  prompt: starship        # a role
  icons: "yes"            # a question
  work-dir: ~/work/       # a text question

questions:
  skip: [fun]

custom:
  - {id: btop, help: "Resource monitor", brew: btop, apt: btop}
```

| Key | Type | Description |
|---|---|---|
| `profiles` | list | Ordered, cumulative depth levels |
| `sections` | map | `section → subsection → {artifact id: profile}` |
| `answers` | map | Pre-answers for the profile, roles and questions. Used by `-y` and as defaults in the questionnaire |
| `questions.skip` | list | Questions never to ask (their default is used) |
| `custom` | list | Simple artifacts declared inline: `id`, `help`, `brew`, `cask`, `apt`, `bin`, `requires`, `tags`, `role` |

Which config is used: `-c` (path or bundled name) → `~/.config/rigsmith/config.yaml` → the bundled `reference`.
Validation rejects unknown artifacts or profiles, duplicates, empty sections, unresolved `requires`, unknown questions
in `skip` and answers that don't fit (unknown role provider, invalid choice).

## Questions

Asked only when an artifact in scope references them (through a tag or its `prefs`).

| Id | Kind | Answers | Effect |
|---|---|---|---|
| `icons` | choice | `yes` / `no` | `yes` sets `RIGSMITH_ICONS=1`; `no` skips artifacts tagged `icons` (Nerd Fonts) |
| `aliases` | choice | `yes` / `no` | `no` skips artifacts tagged `aliases` |
| `tui` | choice | `yes` / `no` | `no` skips artifacts tagged `tui` |
| `fun` | choice | `yes` / `no` (default `no`) | `no` skips artifacts tagged `fun` |
| `theme` | choice | `catppuccin` / `none` | `catppuccin` sets `RIGSMITH_THEME=catppuccin`; `none` skips artifacts tagged `theme` |
| `work-dir` | text | a folder (default `~/work/`) | Used by `git-identities`; a trailing `/` is added |
| `work-email` | text | an email (default empty) | Used by `git-identities`; empty skips the email setting |

Roles with two or more providers in scope (prompt, editor, terminal, container runtime…) are asked too.

## Artifacts

Defined in Python under [`src/rigsmith/library/`](../src/rigsmith/library), or in your own
`~/.config/rigsmith/artifacts/*.py`.

| Field | Description |
|---|---|
| `id` | Unique, kebab-case |
| `help` | One or two sentences: what it is, then a command to try. Required |
| `sources` | Backends, each optionally limited with `os=` / `arch=` / `distro=`. The first that matches the platform is used |
| `bin` | Presence check: this binary on PATH |
| `check` | Presence check: a shell command, exit 0 means present |
| `shell` | `Snippet(name, phase)`: zsh files written to `shell.d/<phase>-<id>.zsh` |
| `files` | `File(src, dest, os=)`: whole files, foreign ones backed up first |
| `settings` | `VSCodeSetting(key, value)`, `GitConfig(key, value, file=)`; `{{question-id}}` placeholders allowed in git keys and values |
| `role` | Exclusive slot (`prompt`, `editor`…): one provider at a time |
| `tags` | Used by questions to skip artifacts (`icons`, `aliases`, `tui`, `fun`, `theme`) |
| `prefs` | Questions whose answers the artifact uses |
| `requires` | Other artifact ids |
| `notes` | Manual follow-ups shown after install |
| `conflicts` | Regexes for `~/.zshrc` lines that would load the same thing twice |

Snippet phases: `00` instant prompt · `05` Homebrew · `10` env and PATH · `20` plugin manager · `30` plugins · `40` completion ·
`50` tool init · `70` aliases and functions · `80` late plugins · `90` prompt.

## Backends

| Backend | Installs | Detected by |
|---|---|---|
| `Brew(formula)` | a Homebrew formula (macOS and Linux) | `brew list --formula` |
| `Cask(cask)` | a Homebrew cask (macOS) | `brew list --cask` |
| `Apt("pkg ...")` | Debian/Ubuntu packages | `dpkg-query` |
| `Krew(plugin)` | a kubectl plugin | `kubectl krew list` |
| `VSCodeExt(publisher.name)` | a VS Code extension | `code --list-extensions` |
| `UvTool(package)` | a Python CLI in its own environment | `uv tool list` |
| `Release(name, url=)` | one binary from a release archive into `~/.local/bin`; `url` may use `{os}` and `{arch}` | file exists |
| `NerdFont(family)` | a Nerd Font into `~/.local/share/fonts` (Linux) | folder exists |
| `GitClone(url, dest=)` | a git checkout | `.git` exists |
| `Script(label, install_cmd=, check_cmd=, remove_cmd=)` | anything else; without `remove_cmd` it can't be undone | `check_cmd` |

## Files and environment

| Path | What |
|---|---|
| `~/.config/rigsmith/config.yaml` | Your config (`$XDG_CONFIG_HOME` is honored) |
| `~/.config/rigsmith/artifacts/*.py` | Your own artifacts, loaded on every run |
| `~/.config/rigsmith/init.zsh` | Sources every file in `shell.d/` |
| `~/.config/rigsmith/shell.d/` | One snippet per artifact, plus `01-rigsmith-prefs.zsh` (questionnaire answers) |
| `~/.zshrc` | One marked block at the top that sources `init.zsh`; your lines are never edited |
| `~/.local/state/rigsmith/state.json` | Receipts, requested artifacts, remembered answers (`$XDG_STATE_HOME` is honored) |
| `~/.local/state/rigsmith/logs/` | Every command's output, one file per run |

| Variable | Used by |
|---|---|
| `RIGSMITH_ICONS`, `RIGSMITH_THEME` | Snippets, from the `icons` and `theme` answers |
| `RIGSMITH_VERSION` | `install.sh`: pin the rigsmith version |
| `RIGSMITH_FROM` | `install.sh`: install rigsmith from another source (e.g. `git+https://github.com/slimfrkha/rigsmith`) |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Done |
| `1` | An artifact failed, or you cancelled or declined |
| `2` | Invalid config or arguments |
