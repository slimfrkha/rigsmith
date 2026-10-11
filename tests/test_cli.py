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
    yield lambda *args: runner.invoke(app, list(args), catch_exceptions=False)
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
