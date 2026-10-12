"""Receipts: the per-effect undo log in ~/.local/state/rigsmith/state.json."""

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from rigsmith.model import state_home

NOOP, CREATED, MODIFIED, IRREVERSIBLE = "noop", "created", "modified", "irreversible"


@dataclass
class Receipt:
    key: str
    artifact: str
    op: str  # noop | created | modified | irreversible
    after: str | None = None  # fingerprint rigsmith left behind
    backup: Any = None  # what restores the pre-install state
    ts: str = field(default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds"))


class State:
    def __init__(self) -> None:
        self.path = state_home() / "state.json"
        data = json.loads(self.path.read_text()) if self.path.exists() else {}
        self.receipts: dict[str, Receipt] = {r["key"]: Receipt(**r) for r in data.get("receipts", [])}
        self.requested: set[str] = set(data.get("requested", []))  # selected by the user, not pulled in
        self.answers: dict[str, str] = data.get("answers", {})  # last questionnaire answers, reused as defaults

    def get(self, key: str) -> Receipt | None:
        return self.receipts.get(key)

    def put(self, r: Receipt) -> None:
        self.receipts.pop(r.key, None)  # re-insert at the end: undo runs in reverse order
        self.receipts[r.key] = r

    def drop(self, key: str) -> None:
        self.receipts.pop(key, None)

    def for_artifact(self, id: str) -> list[Receipt]:
        return [r for r in self.receipts.values() if r.artifact == id]

    def managed(self, id: str) -> bool:
        """Did rigsmith change anything for this artifact?"""
        return any(r.op != NOOP for r in self.for_artifact(id))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(
                {
                    "version": 1,
                    "requested": sorted(self.requested),
                    "answers": self.answers,
                    "receipts": [asdict(r) for r in self.receipts.values()],
                },
                indent=1,
            )
        )
        os.replace(tmp, self.path)
