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

from rigsmith import model
from rigsmith.config import Config
from rigsmith.effects import (
    LIBRARY,
    Effect,
    FileEffect,
    LoginShellEffect,
    PackageEffect,
    PostInstallEffect,
    snippet_effects,
)
from rigsmith.model import Artifact, Platform, state_home
from rigsmith.settings import setting_effects
from rigsmith.shell import CORE, ZshrcBlock, core_effects, has_snippets
from rigsmith.state import CREATED, IRREVERSIBLE, MODIFIED, NOOP, Receipt, State


def effects_for(art: Artifact, p: Platform) -> list[Effect]:
    effs: list[Effect] = []
    if src := art.source(p):
        effs.append(PackageEffect(art, src, p))
    effs += snippet_effects(art)
    effs += [
        FileEffect(art.id, Path(f.dest).expanduser(), (LIBRARY / "files" / f.src).read_bytes())
        for f in art.files
        if f.os in (None, p.os)
    ]
    effs += setting_effects(art, p)
    effs += art.extra_effects(p)
    if art.has_post_install:
        effs.append(PostInstallEffect(art))
    return effs


def status(art: Artifact, p: Platform) -> str:
    """installed | partial | missing | n/a — from the real system, not from receipts."""
    if not art.available(p):
        return "n/a"
    done = [e.current() == e.desired() for e in effects_for(art, p) if e.inspectable]
    return "installed" if all(done) else "partial" if any(done) else "missing"


def pending(art: Artifact, p: Platform, state: State) -> list[Effect]:
    """Effects an install would apply (ignores effects the user changed since install)."""
    out = []
    for e in effects_for(art, p):
        r = state.get(e.key)
        if not e.inspectable:
            if not r:
                out.append(e)
            continue
        cur = e.current()
        if cur != e.desired() and not (r and r.op != NOOP and cur != r.after):
            out.append(e)
    return out


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

    def install(self, cfg: Config, order: list[str], env: dict[str, str]) -> Result:
        res = Result()
        todo = {i: pending(cfg.library[i], self.p, self.state) for i in order}
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
                    changed = sum(self._apply(e, res) for e in effects_for(art, self.p))
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
                res.changes += sum(self._apply(e, res) for e in core_effects(env))
            self.state.save()
        return res

    def _apply(self, e: Effect, res: Result) -> int:
        """Apply one effect following the receipt rules. Returns 1 if the system changed."""
        r = self.state.get(e.key)
        if not e.inspectable:
            if r:
                return 0
            e.apply()
            self.state.put(Receipt(e.key, e.artifact, IRREVERSIBLE, e.desired()))
            return 1
        cur, want = e.current(), e.desired()
        if cur == want:
            if not r:
                self.state.put(Receipt(e.key, e.artifact, NOOP, want))
            return 0
        if r and r.op != NOOP:
            if cur != r.after:
                res.warnings.append(f"{e.label}: changed since install, kept")
                return 0
            e.apply()  # our own earlier version: update it, keep the original undo data
            r.after = want
            return 1
        backup = e.backup()
        e.apply()
        op = IRREVERSIBLE if not e.reversible else CREATED if cur is None else MODIFIED
        self.state.put(Receipt(e.key, e.artifact, op, want, backup))
        return 1

    # ── uninstall ────────────────────────────────────────────────────────────

    def uninstall(self, cfg: Config, order: list[str], include_unmanaged: bool = False) -> Result:
        res = Result()
        with self._log("uninstall"):
            effs_all = [e for i in order if i in cfg.library for e in effects_for(cfg.library[i], self.p)]
            if any(e.sudo and (r := self.state.get(e.key)) and r.op != NOOP for e in effs_all):
                sudo_upfront(self.say)
            for n, i in enumerate(order, 1):
                art = cfg.library.get(i)
                effs = {e.key: e for e in effects_for(art, self.p)} if art else {}
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
                self.say(f"[{n}/{len(order)}] ✓ {i}" + (f" ({changed} changes)" if changed else ""))
            if not has_snippets():
                res.changes += self._undo_artifact(CORE, {}, False, res)
            self.state.save()
        return res

    def _undo_artifact(self, id: str, effs: dict[str, Effect], include_unmanaged: bool, res: Result) -> int:
        changed = 0
        for r in reversed(self.state.for_artifact(id)):
            e = effs.get(r.key) or generic_effect(r)
            if r.op == NOOP:
                if include_unmanaged and r.key.startswith("pkg:") and e and e.current() == r.after:
                    e.restore(None)
                    changed += 1
            elif r.op == IRREVERSIBLE:
                res.warnings.append(f"{id}: `{e.label if e else r.key}` can't be undone, kept")
            elif e is None:
                res.warnings.append(f"{id}: don't know how to undo {r.key}, kept")
            else:
                cur = e.current()
                if cur == r.after:
                    e.restore(r.backup)
                    changed += 1
                elif cur is not None:
                    res.warnings.append(f"{e.label}: changed since install, kept")
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


def generic_effect(r: Receipt) -> Effect | None:
    """Rebuild an effect from its receipt alone (artifact no longer in the library, or core files)."""
    if r.key.startswith("file:"):
        return FileEffect(r.artifact, Path(r.key[5:]), b"")
    if r.key == "zshrc-block":
        return ZshrcBlock()
    if r.key == "login-shell":
        return LoginShellEffect(r.artifact)
    return None


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
