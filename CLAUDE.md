# CLAUDE.md: rigsmith operational map

A Python CLI (`init` / `install` / `scan` / `uninstall`) that sets up macOS and Debian/Ubuntu machines from a
library of **artifacts** (a package plus the config it needs), organized in a YAML **config** (sections,
subsections, profiles). Every change it makes gets a **receipt**, so uninstall undoes exactly what it did.

**Read first:** [DESIGN.md](DESIGN.md) (the model and vocabulary; use its terms) and
[CONTRIBUTING.md](CONTRIBUTING.md) (adding artifacts, e2e, releasing).

## Hard rule

**Never run `rigsmith install`, `rigsmith uninstall` or `tests/e2e/run.sh` on the dev machine.** They really
install packages and edit `~/.zshrc`. Use `scan`, `--dry-run`, the unit tests (they sandbox `HOME`), or the e2e
workflow in CI (`gh workflow run e2e -f args="-c platform" -f os=ubuntu`).

## The gate: run before calling anything done

```bash
uv run ruff format --check
uv run ruff check
uv run ty check src
uv run pytest
```

Library changes also need `uv run python scripts/gen_catalog.py` (regenerate docs/CATALOG.md) and
`uv run python scripts/check_sources.py` (every brew name and VS Code extension id exists).

## Map

| Path | What |
|---|---|
| `src/rigsmith/model.py` | Platform, Artifact, Question, Backend base, registries |
| `src/rigsmith/backends.py` | one class per package manager (Brew, Cask, Apt, Release, VSCodeExt, …) |
| `src/rigsmith/plan.py` | filters → questions → roles → dependency closure → order |
| `src/rigsmith/effects.py`, `settings.py` | what an artifact changes, each able to report/apply/restore |
| `src/rigsmith/runner.py`, `state.py` | install/uninstall driven by receipts |
| `src/rigsmith/shell.py` | the `~/.zshrc` block, `init.zsh`, `shell.d/` |
| `src/rigsmith/tui.py` | Textual questionnaire, picker, confirm |
| `src/rigsmith/library/` | built-in artifacts, one module per section; `snippets/*.zsh` |
| `config/` | `reference.yaml` (whole library), `example.yaml`, `presets/` |
| `tests/` | unit, library lint, CLI, TUI (pilot); `e2e/` runs in CI only |

## Conventions

- Integration config (what a tool needs to work) stays in its artifact; aliases, themes and preferences are
  separate artifacts that `requires` it.
- Every new artifact goes in `config/reference.yaml`; library lint fails otherwise.
- Presets pin every answer (lint enforces it).
- Commit messages: imperative subject, a body that says why.
