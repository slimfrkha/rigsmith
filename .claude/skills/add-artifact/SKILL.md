---
name: add-artifact
description: >-
  Add a tool, VS Code extension, font, app or config snippet to the rigsmith library. Use whenever the user
  wants something new installable: "add X to rigsmith", "can rigsmith install Y", "support Z", "we're missing
  lazygit-like tool", "add the Go extension", "put X in the platform preset", a pasted new-artifact issue, or a
  bare tool name in this repo. Also for swapping a tool's install source (a formula removed from Homebrew,
  a cask renamed). Do NOT use for engine changes (new backends, plan/runner/TUI logic, config format) or for
  editing an existing artifact's help text, where you edit and regenerate the catalog.
---

# Adding an artifact to rigsmith

Read the artifact fields in docs/reference.md#artifacts once if you haven't this session. The laws govern; the rest serves them.

## Laws

1. **Verify upstream live, before writing a line.** Local `brew info` metadata goes stale: tflint passed locally
   after Homebrew core had already dropped it. Names get guessed wrong (pay-respects isn't in core; Docker
   Desktop's cask is `docker-desktop`); casks are mac-only; some formulae are keg-only (not on PATH); some VS Code
   extensions are now built in (Copilot Chat) and can't be installed. Check with
   `curl -s -o /dev/null -w '%{http_code}' https://formulae.brew.sh/api/formula/NAME.json` (or `/cask/`), and run
   `uv run python scripts/check_sources.py` at the end. A 404 means pick another source, never "probably fine".
2. **Detection must match reality.** `scan` and the e2e "installed after install" assertion depend on how presence
   is detected: `bin=` (the real binary: ripgrep → `rg`, bottom → `btm`), else `check=` (apps:
   `test -d /Applications/X.app`), else the backend's own listing. A wrong `bin` means the install "succeeds" and
   then fails with "installed but not detected".
3. **Tool vs taste.** Config the tool needs to work (PATH, `eval "$(tool init zsh)"`, completion) goes in the tool's
   own snippet. Aliases, themes and preferences are a separate `<id>-aliases` / settings artifact that
   `requires` the tool and carries the right tag (`aliases`, `theme`, `icons`), so configs can take the tool
   without the taste. **Counter-law:** don't split what the tool can't work without. `zoxide init` is integration,
   not taste. A plain CLI with no config needs no snippet at all.
4. **Wire every place the lint checks, then pass the gate.** The artifact goes in `config/reference.yaml`, the
   catalog is regenerated, and presets that include it pin any new role or question answer. Done means:
   `uv run ruff format && uv run ruff check && uv run ty check src && uv run pytest` green, plus `check_sources.py`.
5. **Never install on the dev machine.** No `rigsmith install` or `uninstall`, no `tests/e2e/run.sh`. Verify with
   `uv run rigsmith scan -s SECTION`, `uv run rigsmith install ID --dry-run`, the tests, and for anything with a
   new install path, CI: `gh workflow run e2e -f args="ID" -f os=ubuntu` (ids resolve against reference.yaml).
   Use `-f os=macos` only when the change is mac-specific: macOS minutes cost 10×.

## Choosing the source

Illustrations of Laws 1–2: anchors, not a complete list. Reason from the laws for anything not covered.

| Situation | Write | Detection |
|---|---|---|
| CLI in Homebrew core (both OSes) | `tool("id", "help")` (`brew=` if the formula name differs) | `bin` defaults to id; set it if the binary differs |
| Mac app | `Artifact(sources=[Cask("x", os="darwin")], check="test -d /Applications/X.app")` | `check` |
| Needs a Linux alternative | extra source with `os="linux"`: `Apt(...)`, `Script(...)`, `NerdFont(...)` | first matching source wins, chosen before running |
| Formula removed or BUSL (HashiCorp) | `brew="hashicorp/tap/x"` for HashiCorp; else `Release("x", url=".../x_{os}_{arch}.zip")` | `bin` |
| Keg-only formula | `Artifact(sources=[Brew(...)])` with no `bin`, plus a snippet putting it on PATH | backend listing |
| Python CLI | `tool(..., sources=[UvTool("pkg")])` | `bin` |
| VS Code extension | `ext("id-ext", "publisher.name", "help")` | backend listing |
| Official curl installer only | `Script(install_cmd=, check_cmd=, remove_cmd=)`; without `remove_cmd` it's irreversible (shown before confirm) | `check_cmd` |

## Placement decisions

- **Section**: what the tool *is* (`kubernetes/logs`), never who uses it. That's what presets are for.
- **Profile**: `minimal` only if most people in that section want it on day one; `comprehensive` for niche or heavy.
- **Role**: only when two providers *can't coexist* (two prompts, two container runtimes, two `ls` alias sets).
  Tools that merely overlap (fzf/peco, kubectl/k9s) get no role. Adding a second provider to a role in a preset means
  pinning that role in the preset's `answers:`.
- **requires**: the real dependency direction. VS Code extensions that pull in others declare it: `debugpy`
  depends on the Python extension, so `debugpy-ext` requires `python-ext`, not the reverse.
- **Presets**: add it only to presets whose developer type would expect it; most new tools only go in `reference.yaml`.
- **Inclusion bar**: widely used and maintained. If the user asks for a niche tool, say so in one line and offer a
  `custom:` entry in their own config. If they still want it built in, add it. It's their repo.

## Artifacts that need the user's input

If the artifact needs a value only the user knows (a folder, an email), add a `Question(kind="text", ...)` in
`library/questions.py`, list its id in the artifact's `prefs`, and use `{{question-id}}` in git setting keys or
values. A text question is asked only when an artifact in scope references it; an empty answer skips the
setting. `git-identities` is the worked example.

## Help text

One or two sentences: what it is, then the one command or key to try. `"Fast, disk-efficient Node package
manager."` passes; `"An amazing, powerful tool for developers"` fails (says nothing, no command).

## Acceptance tests (these win over the prose)

- "add gping" → API check (200) → `tool("gping", "Ping with a live graph. Try: gping 1.1.1.1.")` in `cli.py`
  with the network tools → `cli/network: gping: comprehensive` in reference.yaml → catalog → gate → done.
  No snippet, no preset edits, no install.
- "add lsd as an ls replacement" → `lsd` tool plus `lsd-aliases` (tag `aliases`). Because `eza-aliases` and
  `lsd-aliases` both alias `ls`, give **both alias artifacts** `role="ls-aliases"`, not the tools. Check presets
  containing `eza-aliases`: they don't contain `lsd-aliases`, so no answer to pin.
- "add tflint" when the API returns 404 → `Release` with the upstream release URL, not a guessed tap.
- "add the Copilot extension" → it's built into VS Code; say so and add nothing.
- Inverse: "fix fzf's help text" → edit the string, regenerate the catalog, run pytest. No source verification,
  no e2e.
- Out of scope: "add a dnf backend" → that's engine work (a `Backend` subclass in `backends.py` plus tests);
  this checklist doesn't apply. Say so in one line and work on it as an engine change.

## Pre-flight before saying done (silent)

1. Did the live API or `check_sources.py` confirm every name? 2. Will detection find it right after install?
3. Is taste split from integration, and nothing over-split? 4. Is it in reference.yaml, is the catalog
regenerated, and are new role answers pinned in presets? 5. Did anything get installed on this machine? (Must be no.)
