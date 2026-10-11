"""The real CLI against a user plugin (~/.config/rigsmith/artifacts/*.py) with a fake backend."""

import sys
import textwrap

import pytest
from typer.testing import CliRunner

from rigsmith.cli import app
from rigsmith.model import ARTIFACTS

PLUGIN = """
from dataclasses import dataclass
from pathlib import Path
from rigsmith.model import Artifact, Backend, Snippet, backend

DB = Path.home() / "fake-installed"

@backend("fakefile")
@dataclass
class FakeFile(Backend):
    def _set(self):
        return set(DB.read_text().split()) if DB.exists() else set()
    def is_installed(self):
        return self.pkg in self._set()
    def install(self):
        DB.write_text(" ".join(self._set() | {self.pkg}))
    def uninstall(self, snapshot=None):
        DB.write_text(" ".join(self._set() - {self.pkg}))

Artifact(id="t-base", help="Base tool.", sources=[FakeFile("t-base")], shell=Snippet("zoxide.zsh", 50))
Artifact(id="t-top", help="Needs base.", sources=[FakeFile("t-top")], requires=["t-base"])
"""

CONFIG = """
profiles: [minimal, standard]
sections:
  test:
    tools: {t-base: minimal, t-top: standard}
"""


@pytest.fixture
def cli(home):
    d = home / ".config/rigsmith/artifacts"
    d.mkdir(parents=True)
    (d / "fake.py").write_text(PLUGIN)
    (home / ".config/rigsmith/config.yaml").write_text(CONFIG)
    runner = CliRunner()
    yield lambda *args, input=None: runner.invoke(app, list(args), input=input, catch_exceptions=False)
    for id in ("t-base", "t-top"):
        ARTIFACTS.pop(id, None)
    sys.modules.pop("rigsmith_user_fake", None)


def installed(home):
    db = home / "fake-installed"
    return set(db.read_text().split()) if db.exists() else set()


def test_install_scan_uninstall_roundtrip(cli, home):
    out = cli("install", "-p", "standard", "--dry-run", "--unsupported").output
    assert "+ t-base" in out and "+ t-top" in out and installed(home) == set()

    r = cli("install", "-p", "standard", "-y", "--unsupported")
    assert r.exit_code == 0, r.output
    assert installed(home) == {"t-base", "t-top"}
    assert "Installed: 0 changes" in cli("install", "-p", "standard", "-y", "--unsupported").output

    scan = cli("scan").output
    assert "✓ t-base" in scan and "managed" in scan

    out = cli("uninstall", "t-base", "-y").output
    assert "t-base is needed by: t-top" in out
    assert installed(home) == {"t-top"}

    out = cli("uninstall", "-y").output
    assert installed(home) == set()
    assert not (home / ".zshrc").exists()
    assert "Nothing rigsmith installed matches" in cli("uninstall", "-y").output


def test_preexisting_is_left_alone_unless_asked(cli, home):
    (home / "fake-installed").write_text("t-base")
    cli("install", "t-base", "-y", "--unsupported")
    out = cli("uninstall", "-y").output
    assert installed(home) == {"t-base"}
    cli("install", "t-base", "-y", "--unsupported")
    out = cli("uninstall", "t-base", "--include-unmanaged", "-y").output
    assert installed(home) == set(), out


def test_bad_config_is_reported(cli, home):
    (home / ".config/rigsmith/config.yaml").write_text(textwrap.dedent(CONFIG) + "answers: {profile: huge}\n")
    with pytest.raises(Exception, match="answers.profile"):
        cli("scan")


def test_init_forks_a_config(cli, home, monkeypatch):
    import rigsmith.tui

    seen = {}

    def fake_pick(cfg, p, entries, ticked):
        seen["entries"] = [e.id for e in entries]
        return {"picked": ["t-base"], "profiles": {"t-base": "standard"}}

    monkeypatch.setattr(rigsmith.tui, "pick_scope", fake_pick)
    out = home / "mine.yaml"
    r = cli("init", "--from", str(home / ".config/rigsmith/config.yaml"), "-o", str(out), input="n\n")
    assert r.exit_code == 0, r.output
    assert "eza" in seen["entries"]  # library artifacts not in the source are offered (unticked)
    text = out.read_text()
    assert "t-base: standard" in text and "t-top" not in text
    assert cli("scan", "-c", str(out)).exit_code == 0


def test_editor_loop_reports_invalid_configs(cli, home, monkeypatch):
    from rigsmith.cli import edit_until_valid

    path = home / "c.yaml"
    path.write_text(CONFIG)
    breaker = home / "break.sh"
    breaker.write_text('#!/bin/sh\necho "answers: {profile: huge}" >> "$1"\n')
    breaker.chmod(0o755)
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.setenv("EDITOR", str(breaker))
    monkeypatch.setattr("typer.confirm", lambda *a, **k: False)  # "Edit again?" → no
    edit_until_valid(path)
    assert "huge" in path.read_text()

    monkeypatch.setenv("EDITOR", "true")  # an editor that changes nothing
    path.write_text(CONFIG)
    edit_until_valid(path)  # valid on first pass, returns without asking
