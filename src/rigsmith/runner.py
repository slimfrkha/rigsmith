"""Execute plans: install with receipts, uninstall by replaying receipts backwards."""

import os
import shutil
import subprocess
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from rigsmith import answers as answersmod
from rigsmith import model, reconcile
from rigsmith.config import Config
from rigsmith.effects import (
    LIBRARY,
    Effect,
    FileEffect,
    PackageEffect,
    PostInstallEffect,
    snippet_effects,
)
from rigsmith.model import Artifact, Platform, state_home
from rigsmith.plan import Plan
from rigsmith.settings import setting_effects
from rigsmith.shell import CORE, has_snippets
from rigsmith.state import CREATED, IRREVERSIBLE, NOOP, Receipt, State


def effects_for(art: Artifact, p: Platform, answers: dict[str, str] | None = None) -> list[Effect]:
    effs: list[Effect] = []
    if src := art.source(p):
        effs.append(PackageEffect(art, src, p))
    effs += snippet_effects(art)
    effs += [
        FileEffect(art.id, Path(f.dest).expanduser(), (LIBRARY / "files" / f.src).read_bytes())
        for f in art.files
        if f.os in (None, p.os)
    ]
    effs += setting_effects(art, p, answers)
    effs += art.extra_effects(p)
    if art.has_post_install:
        effs.append(PostInstallEffect(art))
    return effs


def status(art: Artifact, p: Platform, answers: dict[str, str] | None = None) -> str:
    """installed | partial | missing | n/a — from the real system, not from receipts."""
    if not art.available(p):
        return "n/a"
    done = [e.current() == e.desired() for e in effects_for(art, p, answers) if e.inspectable]
    if not done:  # every effect skipped (e.g. its questions aren't answered yet): nothing is in place
        return "missing"
    return "installed" if all(done) else "partial" if any(done) else "missing"


def pending(art: Artifact, p: Platform, state: State, answers: dict[str, str] | None = None) -> list[Effect]:
    """The effects an install of `art` would change, as of now."""
    return reconcile.pending(effects_for(art, p, state.answers if answers is None else answers), state)


@dataclass
class Result:
    changes: int = 0
    ok: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class Runner:
    def __init__(self, p: Platform, say: Callable[[str], None] = print) -> None:
        self.p, self.say, self.state = p, say, State()

    # ── install ──────────────────────────────────────────────────────────────

    def install(self, cfg: Config, plan: Plan) -> Result:
        res, order = Result(), plan.order
        self.state.requested |= {i for i, why in plan.reasons.items() if why == "selected"}
        todo = {i: pending(cfg.library[i], self.p, self.state, plan.answers) for i in order}
        answersmod.remember(self.state, plan.answers)
        # packages missing when the run starts: if one appears before its turn, this run brought it in
        absent = {e.key for effs in todo.values() for e in effs if isinstance(e, PackageEffect)}
        with self._log("install"):
            if any(e.sudo for effs in todo.values() for e in effs):
                sudo_upfront(self.say)
            for n, i in enumerate(order, 1):
                art = cfg.library[i]
                blocked = [r for r in art.requirements(self.p) if r in res.failed or r in res.skipped]
                if blocked:
                    res.skipped[i] = f"{', '.join(blocked)} failed"
                    self.say(f"[{n}/{len(order)}] ⊘ {i}: skipped, {res.skipped[i]}")
                    continue
                if todo[i]:
                    self.say(f"[{n}/{len(order)}] … {i}: {', '.join(e.label for e in todo[i])}")
                try:
                    decisions = reconcile.install(effects_for(art, self.p, plan.answers), self.state, absent)
                    changed = sum(self._execute(e, d, res) for e, d in decisions)
                except Exception as e:  # one artifact failing must not stop the run
                    res.failed[i] = str(e)
                    self.say(f"[{n}/{len(order)}] ✗ {i}: {e}")
                    continue
                finally:
                    self.state.save()
                res.ok.append(i)
                res.changes += changed
                if changed:
                    res.notes += art.notes
                self.say(f"[{n}/{len(order)}] ✓ {i}" + (f" ({changed} changes)" if changed else ""))
            if has_snippets():
                core = reconcile.shell_integration(self.state.answers, self.state)
                res.changes += sum(self._execute(e, d, res) for e, d in core)
            self.state.save()
        return res

    def _execute(self, e: Effect, d: reconcile.Decision, res: Result) -> int:
        """Carry out one install decision. Receipts are committed only after the change succeeded."""
        if d.action == reconcile.KEEP:
            res.warnings.append(d.reason)
        elif d.action == reconcile.RECORD:
            self.state.put(Receipt(e.key, e.artifact, d.op or NOOP, e.desired()))
        elif d.action == reconcile.RUN_ONCE:
            e.apply()
            self.state.put(Receipt(e.key, e.artifact, IRREVERSIBLE, e.desired()))
        elif d.action == reconcile.UPDATE:
            want = e.desired()
            e.apply()
            if r := self.state.get(e.key):
                r.after = want
        elif d.action == reconcile.APPLY:
            want, backup = e.desired(), e.backup()
            e.apply()
            self.state.put(Receipt(e.key, e.artifact, d.op or CREATED, want, backup))
        return int(d.changes)

    # ── uninstall ────────────────────────────────────────────────────────────

    def uninstall(self, cfg: Config, order: list[str], include_unmanaged: bool = False) -> Result:
        res = Result()
        with self._log("uninstall"):
            answers = self.state.answers
            effs_all = [e for i in order if i in cfg.library for e in effects_for(cfg.library[i], self.p, answers)]
            if any(e.sudo and (r := self.state.get(e.key)) and r.op != NOOP for e in effs_all):
                sudo_upfront(self.say)
            for n, i in enumerate(order, 1):
                art = cfg.library.get(i)
                effs = {e.key: e for e in effects_for(art, self.p, self.state.answers)} if art else {}
                try:
                    changed = self._undo_artifact(i, effs, include_unmanaged, res)
                except Exception as e:
                    res.failed[i] = str(e)
                    self.say(f"[{n}/{len(order)}] ✗ {i}: {e}")
                    continue
                finally:
                    self.state.save()
                res.ok.append(i)
                res.changes += changed
                self.state.requested.discard(i)
                if art and art.role and self.state.answers.get(art.role) == i:
                    del self.state.answers[art.role]  # removed on purpose: no longer the pick
                self.say(f"[{n}/{len(order)}] ✓ {i}" + (f" ({changed} changes)" if changed else ""))
            if not has_snippets():
                res.changes += self._execute_undo(CORE, reconcile.undo_shell_integration(self.state), res)
            self.state.save()
        return res

    def _undo_artifact(self, id: str, effs: dict[str, Effect], include_unmanaged: bool, res: Result) -> int:
        decisions = reconcile.undo(id, effs, self.state, include_unmanaged)
        return self._execute_undo(id, decisions, res)

    def _execute_undo(self, id: str, decisions, res: Result) -> int:
        """Carry out undo decisions in order; each receipt is dropped once handled."""
        changed = 0
        for e, r, d in decisions:
            if d.action == reconcile.UNDO and e is not None:
                try:
                    e.restore(d.backup)
                except Exception:
                    if e.current() is not None:  # still there: a real failure
                        raise
                changed += 1
            elif d.action in (reconcile.CANT_UNDO, reconcile.UNKNOWN):
                res.warnings.append(f"{id}: {d.reason}")
            elif d.action == reconcile.KEEP:
                res.warnings.append(d.reason)
            if r is not None:
                self.state.drop(r.key)
        return changed

    def _log(self, what: str):
        return _LogContext(state_home() / "logs" / f"{datetime.now():%Y%m%d-%H%M%S}-{what}.log")


class _LogContext:
    def __init__(self, path: Path) -> None:
        self.path = path

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        model.LOG = self.path.open("a")
        return self

    def __exit__(self, *exc) -> None:
        if model.LOG:
            model.LOG.close()
        model.LOG = None


def sudo_upfront(say: Callable[[str], None]) -> None:
    """Ask for the sudo password once, then keep the credential warm for the whole run."""
    if os.geteuid() == 0 or not shutil.which("sudo"):
        return
    if subprocess.run(["sudo", "-n", "true"], capture_output=True).returncode != 0:
        say("Some steps need sudo (apt, chsh, Homebrew). You'll be asked for your password once.")
        subprocess.run(["sudo", "-v"], check=True)

    def keepalive() -> None:
        while True:
            time.sleep(50)
            subprocess.run(["sudo", "-n", "-v"], capture_output=True)

    threading.Thread(target=keepalive, daemon=True).start()
