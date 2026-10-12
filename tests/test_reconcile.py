"""Every receipt rule, one row each, at the reconciler's interface; plus: --script and a real run end up identical."""

import subprocess

import pytest

from rigsmith import config, library  # noqa: F401  (registers built-in artifacts)
from rigsmith import reconcile as rc
from rigsmith.effects import Effect
from rigsmith.model import Platform
from rigsmith.plan import Plan
from rigsmith.runner import Runner
from rigsmith.script import install_script
from rigsmith.state import CREATED, IRREVERSIBLE, MODIFIED, NOOP, Receipt


class FakeEffect(Effect):
    def __init__(self, cur=None, want="new", inspectable=True, reversible=True, key="file:/x"):
        self.cur, self.want, self.key, self.artifact, self.label = cur, want, key, "a", "fake"
        self.inspectable, self.reversible = inspectable, reversible

    def current(self):
        return self.cur

    def desired(self):
        return self.want


def receipt(op, after="new", backup=None, key="file:/x"):
    return Receipt(key, "a", op, after, backup)


INSTALL = [
    # (case, effect, receipt, absent at start, expected action, expected op)
    ("one-time step already done", FakeEffect(inspectable=False), receipt(IRREVERSIBLE), set(), rc.SKIP, None),
    ("one-time step not run yet", FakeEffect(inspectable=False), None, set(), rc.RUN_ONCE, IRREVERSIBLE),
    ("already as desired, there before", FakeEffect(cur="new"), None, set(), rc.RECORD, NOOP),
    ("already as desired, pulled in by this run", FakeEffect(cur="new"), None, {"file:/x"}, rc.RECORD, CREATED),
    ("already as desired, has a receipt", FakeEffect(cur="new"), receipt(CREATED), set(), rc.SKIP, None),
    ("changed since install", FakeEffect(cur="theirs"), receipt(CREATED, after="ours"), set(), rc.KEEP, None),
    ("our own older version", FakeEffect(cur="ours"), receipt(CREATED, after="ours"), set(), rc.UPDATE, None),
    ("absent", FakeEffect(cur=None), None, set(), rc.APPLY, CREATED),
    ("foreign value", FakeEffect(cur="theirs"), None, set(), rc.APPLY, MODIFIED),
    ("can't be undone", FakeEffect(reversible=False), None, set(), rc.APPLY, IRREVERSIBLE),
    ("noop receipt, gone since", FakeEffect(cur=None), receipt(NOOP), set(), rc.APPLY, CREATED),
]


@pytest.mark.parametrize("case, effect, rec, absent, action, op", INSTALL, ids=[r[0] for r in INSTALL])
def test_install_decisions(case, effect, rec, absent, action, op):
    d = rc.decide_install(effect, rec, absent)
    assert (d.action, d.op) == (action, op)
    assert d.changes == (action in (rc.APPLY, rc.UPDATE, rc.RUN_ONCE))


UNDO = [
    # (case, effect, receipt, include unmanaged, expected action, expected backup)
    ("there before, kept", FakeEffect(cur="new"), receipt(NOOP), False, rc.FORGET, None),
    (
        "there before, --include-unmanaged",
        FakeEffect(cur="new", key="pkg:a"),
        receipt(NOOP, key="pkg:a"),
        True,
        rc.UNDO,
        None,
    ),
    ("can't be undone", FakeEffect(inspectable=False), receipt(IRREVERSIBLE), False, rc.CANT_UNDO, None),
    ("unknown effect", None, receipt(CREATED), False, rc.UNKNOWN, None),
    ("still ours", FakeEffect(cur="new"), receipt(MODIFIED, backup={"value": 1}), False, rc.UNDO, {"value": 1}),
    ("already gone", FakeEffect(cur=None), receipt(CREATED), False, rc.FORGET, None),
    ("changed since install", FakeEffect(cur="theirs"), receipt(CREATED), False, rc.KEEP, None),
]


@pytest.mark.parametrize("case, effect, rec, unmanaged, action, backup", UNDO, ids=[r[0] for r in UNDO])
def test_undo_decisions(case, effect, rec, unmanaged, action, backup):
    d = rc.decide_undo(effect, rec, unmanaged)
    assert (d.action, d.backup) == (action, backup)


MENU = """
profiles: [minimal]
sections:
  shell:
    helpers: {shell-aliases: minimal, shell-extras: minimal}
  git:
    core: {git-defaults: minimal}
"""


def test_script_and_a_real_run_end_up_identical(home, monkeypatch):
    """The drift test: `--script` run by sh and `rigsmith install` must leave the same files behind."""
    cfg = config.parse(config.yaml().load(MENU))
    ids = ["shell-aliases", "shell-extras", "git-defaults"]
    plan = Plan(order=ids, reasons={i: "selected" for i in ids}, answers={}, env={})
    p = Platform.detect()
    homes = {}
    for name in ("script", "rigsmith"):
        h = home / name
        h.mkdir()
        (h / ".zshrc").write_text("# mine\n")
        monkeypatch.setenv("HOME", str(h))
        if name == "script":
            (h / "out.sh").write_text(install_script(cfg, plan, p, "rigsmith install"))
            subprocess.run(["sh", "out.sh"], cwd=h, check=True, env={"HOME": str(h), "PATH": "/usr/bin:/bin"})
            (h / "out.sh").unlink()
        else:
            Runner(p, say=lambda _: None).install(cfg, plan)
        homes[name] = {
            str(f.relative_to(h)): f.read_bytes()
            for f in h.rglob("*")
            if f.is_file() and ".local/state" not in str(f)  # receipts exist only in a real run
        }
    assert homes["script"] == homes["rigsmith"]
