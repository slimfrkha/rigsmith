"""Shorthands for the common artifact shapes."""

from typing import Any

from rigsmith.backends import Brew
from rigsmith.model import Artifact, Snippet


def tool(id: str, help: str, *, brew: str | None = None, bin: str | None = None, **kw: Any) -> Artifact:
    """A command-line tool installed with brew (macOS and Linux). Presence = binary on PATH."""
    kw.setdefault("sources", [Brew(brew or id)])
    return Artifact(id=id, help=help, bin=bin or id, **kw)


def snippet(id: str, help: str, phase: int, **kw: Any) -> Artifact:
    """Config-only artifact: one zsh snippet named after the id, no package."""
    return Artifact(id=id, help=help, shell=Snippet(f"{id}.zsh", phase), **kw)


def ext(id: str, ext_id: str, help: str, **kw: Any) -> Artifact:
    """A VS Code extension (needs VS Code)."""
    from rigsmith.backends import VSCodeExt  # noqa: PLC0415

    kw.setdefault("requires", ["vscode"])
    return Artifact(id=id, help=help, sources=[VSCodeExt(ext_id)], **kw)
