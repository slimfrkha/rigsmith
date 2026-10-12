"""Decisions: what rigsmith will do with each effect, and why, given its receipt.

Every receipt rule lives here. Install, uninstall, `--dry-run` and `--script` all act on these decisions, so a preview
can't contradict a real run. Generators decide one effect at a time: an executor that applies each decision before
asking for the next sees the state earlier effects left (a package pulled in by a previous step), and a preview
that collects them all at once describes the system as it is now.
"""

from collections.abc import Iterator
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rigsmith.answers import prefs_env
from rigsmith.effects import Effect, FileEffect, LoginShellEffect, PackageEffect
from rigsmith.settings import GitConfigEffect
from rigsmith.shell import CORE, ZshrcBlock, core_effects
from rigsmith.state import CREATED, IRREVERSIBLE, MODIFIED, NOOP, Receipt, State

# install
APPLY = "apply"  # change the system, then record `op` with a backup taken right before
UPDATE = "update"  # rigsmith's own earlier version: change it, keep the original undo data
RUN_ONCE = "run-once"  # an irreversible step that hasn't run yet
RECORD = "record"  # already as desired: record `op` (noop, or created if this run brought it in)
SKIP = "skip"  # nothing to do, nothing to record
# both
KEEP = "keep"  # changed since rigsmith wrote it: the user's now, leave it and warn
# uninstall
UNDO = "undo"  # restore `backup`
FORGET = "forget"  # nothing to undo (there before rigsmith, or already gone): drop the receipt
CANT_UNDO = "cant-undo"  # irreversible: drop the receipt, warn
UNKNOWN = "unknown"  # no way to rebuild the effect: drop the receipt, warn

CHANGES = {APPLY, UPDATE, RUN_ONCE, UNDO}


@dataclass
class Decision:
    action: str
    reason: str = ""  # shown as a warning, or as a comment in --script
    op: str | None = None  # receipt op to record after APPLY / RECORD
    backup: Any = None  # what UNDO restores

    @property
    def changes(self) -> bool:
        return self.action in CHANGES


# ── install ──────────────────────────────────────────────────────────────────


def decide_install(e: Effect, r: Receipt | None, absent_at_start: AbstractSet[str]) -> Decision:
    if not e.inspectable:  # its result can't be observed, so a receipt means "done"
        return Decision(SKIP) if r else Decision(RUN_ONCE, op=IRREVERSIBLE)
    cur, want = e.current(), e.desired()
    if cur == want:
        if r:
            return Decision(SKIP)
        # missing when the run started and present now: an earlier step pulled it in, so rigsmith owns it
        return Decision(RECORD, op=CREATED if e.key in absent_at_start else NOOP)
    if r and r.op != NOOP:
        if cur != r.after:
            return Decision(KEEP, f"{e.label}: changed since install, kept")
        return Decision(UPDATE)
    return Decision(APPLY, op=IRREVERSIBLE if not e.reversible else CREATED if cur is None else MODIFIED)


def install(
    effects: list[Effect], state: State, absent_at_start: AbstractSet[str] = frozenset()
) -> Iterator[tuple[Effect, Decision]]:
    for e in effects:
        yield e, decide_install(e, state.get(e.key), absent_at_start)


def pending(effects: list[Effect], state: State) -> list[Effect]:
    """The effects an install would change, as of now."""
    return [e for e, d in install(effects, state) if d.changes]


def shell_integration(answers: dict[str, str], state: State) -> Iterator[tuple[Effect, Decision]]:
    """Prefs, init.zsh and the ~/.zshrc block: needed as soon as one rigsmith snippet exists."""
    return install(core_effects(prefs_env(answers)), state)


# ── uninstall ────────────────────────────────────────────────────────────────


def decide_undo(e: Effect | None, r: Receipt, include_unmanaged: bool) -> Decision:
    if r.op == NOOP:
        if include_unmanaged and r.key.startswith("pkg:") and e and e.current() == r.after:
            return Decision(UNDO, backup=None)
        return Decision(FORGET, f"{e.label if e else r.key}: was there before rigsmith, kept")
    if r.op == IRREVERSIBLE:
        return Decision(CANT_UNDO, f"`{e.label if e else r.key}` can't be undone, kept")
    if e is None:
        return Decision(UNKNOWN, f"don't know how to undo {r.key}, kept")
    cur = e.current()
    if cur == r.after:
        return Decision(UNDO, backup=r.backup)
    if cur is None:
        return Decision(FORGET)  # already gone
    return Decision(KEEP, f"{e.label}: changed since install, kept")


def undo(
    artifact: str, effects: dict[str, Effect], state: State, include_unmanaged: bool
) -> Iterator[tuple[Effect | None, Receipt | None, Decision]]:
    """An artifact's receipts, newest first; then, with include_unmanaged, its packages rigsmith never touched."""
    for r in reversed(state.for_artifact(artifact)):
        e = effects.get(r.key) or generic_effect(r)
        yield e, r, decide_undo(e, r, include_unmanaged)
    if include_unmanaged:  # installed before rigsmith, no receipt to replay
        for e in effects.values():
            if isinstance(e, PackageEffect) and not state.get(e.key) and e.current() == e.desired():
                yield e, None, Decision(UNDO, backup=None)


def undo_shell_integration(state: State) -> Iterator[tuple[Effect | None, Receipt | None, Decision]]:
    """Prefs, init.zsh and the ~/.zshrc block: removed once no rigsmith snippet is left."""
    return undo(CORE, {}, state, False)


def generic_effect(r: Receipt) -> Effect | None:
    """Rebuild an effect from its receipt alone (artifact no longer in the library, or core files)."""
    if r.key.startswith("file:"):
        return FileEffect(r.artifact, Path(r.key[5:]), b"")
    if r.key == "zshrc-block":
        return ZshrcBlock()
    if r.key == "login-shell":
        return LoginShellEffect(r.artifact)
    if r.key.startswith("git:") and isinstance(r.backup, dict) and "key" in r.backup:
        return GitConfigEffect(r.artifact, r.backup["key"], "", r.backup.get("file"))
    return None
