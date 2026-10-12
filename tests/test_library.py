"""Library lint: keeps built-in artifacts, configs and presets consistent."""

from importlib.resources import files

import pytest

from rigsmith import config, library  # noqa: F401
from rigsmith.model import ARTIFACTS, QUESTIONS

SNIPPETS = files("rigsmith.library") / "snippets"
FILES = files("rigsmith.library") / "files"
CONFIGS = ["reference", "example", *config.presets()]


def test_every_artifact_is_in_reference():
    ref = config.load("reference")
    assert sorted(set(ARTIFACTS) - set(ref.ids)) == []


@pytest.mark.parametrize(
    "name", [c for c in CONFIGS if (config.bundled_dir() / f"{c}.yaml").exists() or c in config.presets()]
)
def test_configs_validate(name):
    cfg = config.load(name)
    assert config.validate(cfg) == []


@pytest.mark.parametrize("art", ARTIFACTS.values(), ids=list(ARTIFACTS))
def test_artifact(art):
    assert art.help.strip(), "help text is required"
    assert art.id == art.id.lower() and " " not in art.id, "ids are kebab-case"
    for req in art.requires:
        assert req in ARTIFACTS, f"requires unknown {req}"
    phases = [s.phase for s in art.snippets]
    assert len(phases) == len(set(phases)), "two snippets in the same phase would overwrite each other"
    for s in art.snippets:
        assert (SNIPPETS / s.name).is_file(), f"missing snippet {s.name}"
    for f in art.files:
        assert (FILES / f.src).is_file(), f"missing file {f.src}"
    for p in art.prefs:
        assert p in QUESTIONS, f"prefs references unknown question {p}"
    assert art.sources or art.snippets or art.files or art.settings, "artifact does nothing"


def test_snippets_are_all_used():
    used = {s.name for a in ARTIFACTS.values() for s in a.snippets}
    assert sorted({p.name for p in SNIPPETS.iterdir()} - used) == []


def test_no_requires_cycles():
    seen: dict[str, int] = {}

    def visit(id: str) -> None:
        assert seen.get(id) != 1, f"requires cycle through {id}"
        if seen.get(id) == 2:
            return
        seen[id] = 1
        for r in ARTIFACTS[id].requires:
            visit(r)
        seen[id] = 2

    for id in ARTIFACTS:
        visit(id)


def test_catalog_is_up_to_date():
    import subprocess
    import sys
    from pathlib import Path

    script = Path(__file__).resolve().parents[1] / "scripts/gen_catalog.py"
    r = subprocess.run([sys.executable, str(script), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("name", config.presets())
def test_presets_pin_every_answer(name):
    """`rigsmith install -c <preset> -y` must not depend on library defaults (reproducible per version)."""
    from rigsmith.plan import questions_for, roles_for

    cfg = config.load(name)
    needed = {"profile", *roles_for(cfg, cfg.ids), *(q.id for q in questions_for(cfg, cfg.ids))}
    assert sorted(needed - cfg.answers.keys()) == []


def test_there_are_presets():
    assert len(config.presets()) >= 5


def test_doc_links_resolve():
    """Relative links and #anchors in the docs point at files and headings that exist."""
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    docs = [root / f for f in ("README.md", "DESIGN.md", "CONTRIBUTING.md", "SECURITY.md", "CLAUDE.md")]
    docs += sorted((root / "docs").glob("*.md"))

    def anchors(path: Path) -> set[str]:
        heads = re.findall(r"^#+ (.+)$", path.read_text(), re.M)
        return {re.sub(r"[^\w\- ]", "", h).strip().lower().replace(" ", "-") for h in heads}

    broken = []
    for doc in docs:
        text = re.sub(r"```.*?```", "", doc.read_text(), flags=re.S)  # links inside code blocks are examples
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, anchor = target.partition("#")
            dest = (doc.parent / path).resolve() if path else doc
            if not dest.exists():
                broken.append(f"{doc.name}: {target}")
            elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                broken.append(f"{doc.name}: {target} (no such heading)")
    assert broken == []
