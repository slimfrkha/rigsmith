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
