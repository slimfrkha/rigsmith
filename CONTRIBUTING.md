# Contributing

## Setup

```sh
uv sync
uv run pytest                              # unit, library lint, CLI and TUI tests: never touch your machine
uv run ruff check . && uv run ruff format --check . && uv run ty check src
uv run python scripts/check_sources.py     # every brew name and VS Code extension id exists (network)
```

Never run `tests/e2e/run.sh` on a machine you care about: it really installs and uninstalls things.

## Adding an artifact

1. Add it to the section's module in [`src/rigsmith/library/`](src/rigsmith/library). Most tools are one line:
   `tool("eza", "Modern ls with colors and git status.")`. Use `ext(...)` for VS Code extensions,
   or a full `Artifact(...)` for anything else ([DESIGN.md §3](DESIGN.md) lists every field).
2. Config the tool **needs** to work (PATH, `eval "$(tool init zsh)"`) goes in its snippet. Aliases, themes and
   preferences go in a separate artifact that `requires` it, so configs can take the tool without the taste.
3. Snippets go in `src/rigsmith/library/snippets/`, at the right phase:
   10 env · 30 plugins · 50 tool init · 70 aliases · 90 prompt.
4. List it in [`config/reference.yaml`](config/reference.yaml) under a section, subsection and profile.
5. Regenerate the catalog: `uv run python scripts/gen_catalog.py`.
6. `uv run pytest` and `uv run python scripts/check_sources.py` must pass.

The bar for the built-in library is a **widely used, maintained** tool that installs with Homebrew on macOS and
Homebrew or apt on Linux (or is clearly marked mac-only / linux-only). Niche tools belong in your own config's
`custom:` section.

## End-to-end tests

[`e2e.yml`](.github/workflows/e2e.yml) runs install → verify → reinstall (must be 0 changes) → uninstall →
verify (`~/.zshrc` byte-identical) on throwaway machines:

- every push and PR: the minimal core, on macOS and a bare Ubuntu container
- weekly: every preset, one Ubuntu container each
- by hand: **Actions → e2e → Run workflow**, with any filters (`-c platform`, `-p standard`) and a choice of OS

## Releasing

Releases publish to PyPI from GitHub Actions through a
[trusted publisher](https://docs.pypi.org/trusted-publishers/) (owner `slimfrkha`, repo `rigsmith`, workflow
`release.yml`, environment `pypi`), so no token is stored anywhere. The `pypi` environment only accepts `v*`
tags and waits for the maintainer's approval, so nobody else can publish, collaborators included.

1. Make sure `main` is green (`ci` and `e2e`).
2. Bump `version` in [`pyproject.toml`](pyproject.toml) (`uv version --bump patch|minor|major`), commit, push.
3. Tag and push:

   ```sh
   git tag -a v0.2.0 -m "rigsmith 0.2.0"
   git push origin v0.2.0
   ```

4. [`release.yml`](.github/workflows/release.yml) **waits for your approval**: open the run in Actions →
   **Review deployments** → approve `pypi`. It then checks the tag matches the version, builds, publishes to
   PyPI and creates the GitHub release with generated notes.
5. Check it the way a user would:

   ```sh
   uvx rigsmith@0.2.0 scan -c server
   ```

A version on PyPI can never be re-uploaded. If a release is broken, fix it and release the next patch version.
