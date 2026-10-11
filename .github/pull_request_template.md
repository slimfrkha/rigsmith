## What

## Checklist (library changes)

- [ ] Every new artifact has a 1–2 sentence `help` that says what it is and the one command to try
- [ ] It's listed in `config/reference.yaml` (section, subsection, profile)
- [ ] Config the tool **needs** stays in its artifact; aliases, themes and preferences are a separate artifact
- [ ] Snippets use the right phase (10 env · 30 plugins · 50 tool init · 70 aliases · 90 prompt)
- [ ] `uv run python scripts/check_sources.py` passes (brew names and VS Code ids exist)
- [ ] Tried on macOS / Linux (say which), or explain why CI covers it
