"""Config (the menu): load, resolve, validate."""

import importlib.resources
import importlib.util
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from rigsmith.backends import Apt, Brew, Cask
from rigsmith.model import ARTIFACTS, QUESTIONS, Artifact, Backend, config_home


class ConfigError(Exception):
    pass


@dataclass
class Entry:
    id: str
    section: str
    subsection: str
    profile: str


@dataclass
class Config:
    name: str
    profiles: list[str]
    entries: list[Entry]
    skip: list[str] = field(default_factory=list)
    answers: dict[str, str] = field(default_factory=dict)
    library: dict[str, Artifact] = field(default_factory=dict)
    doc: Any = None  # the round-trip YAML document, for `init`

    def entry(self, id: str) -> Entry | None:
        return next((e for e in self.entries if e.id == id), None)

    @property
    def ids(self) -> list[str]:
        return [e.id for e in self.entries]


def bundled_dir() -> Path:
    """config/ shipped inside the wheel, or the repo's config/ in a dev checkout."""
    packaged = importlib.resources.files("rigsmith") / "_config"
    if packaged.is_dir():
        return Path(str(packaged))
    return Path(__file__).resolve().parents[2] / "config"


def user_config() -> Path:
    return config_home() / "config.yaml"


def presets() -> list[str]:
    return sorted(p.stem for p in (bundled_dir() / "presets").glob("*.yaml"))


def resolve(source: str | None) -> Path:
    """-c PATH|PRESET → ~/.config/rigsmith/config.yaml → bundled reference.yaml."""
    if source is None:
        return user_config() if user_config().exists() else bundled_dir() / "reference.yaml"
    path = Path(source).expanduser()
    if path.is_file():
        return path
    for cand in (bundled_dir() / f"{source}.yaml", bundled_dir() / "presets" / f"{source}.yaml"):
        if cand.is_file():
            return cand
    raise ConfigError(
        f"no config file or preset named {source!r} (presets: {', '.join(presets()) or 'none'})"
    )


def yaml() -> YAML:
    y = YAML()
    y.indent(mapping=2, sequence=4, offset=2)
    y.preserve_quotes = True
    return y


def load(source: str | None = None) -> Config:
    path = resolve(source)
    try:
        doc = yaml().load(path.read_text()) or {}
    except Exception as e:  # ruamel raises many types
        raise ConfigError(f"{path}: {e}") from e
    return parse(doc, name=str(path))


def parse(doc: Any, name: str = "<config>") -> Config:
    library = dict(ARTIFACTS)
    for raw in doc.get("custom") or []:
        art = custom_artifact(raw)
        library[art.id] = art
    entries = [
        Entry(str(id), str(sec), str(sub), str(prof))
        for sec, subs in (doc.get("sections") or {}).items()
        for sub, arts in (subs or {}).items()
        for id, prof in (arts or {}).items()
    ]
    return Config(
        name=name,
        profiles=[str(p) for p in doc.get("profiles") or []],
        entries=entries,
        skip=[str(q) for q in (doc.get("questions") or {}).get("skip") or []],
        answers={str(k): str(v) for k, v in (doc.get("answers") or {}).items()},
        library=library,
        doc=doc,
    )


def custom_artifact(raw: dict[str, Any]) -> Artifact:
    """An inline `custom:` entry: id, help, brew/cask/apt, bin, requires, tags, role."""
    if "id" not in raw:
        raise ConfigError(f"custom artifact without id: {dict(raw)}")
    sources: list[Backend] = []
    if raw.get("brew"):
        sources.append(Brew(str(raw["brew"])))
    if raw.get("cask"):
        sources.append(Cask(str(raw["cask"]), os="darwin"))
    if raw.get("apt"):
        sources.append(Apt(str(raw["apt"]), os="linux"))
    return Artifact(
        id=str(raw["id"]),
        help=str(raw.get("help", "")),
        sources=sources,
        bin=raw.get("bin") or (str(raw["id"]) if sources and not raw.get("cask") else None),
        requires=[str(r) for r in raw.get("requires") or []],
        tags=[str(t) for t in raw.get("tags") or []],
        role=raw.get("role"),
        register=False,
    )


def validate(cfg: Config) -> list[str]:
    errors: list[str] = []
    if not cfg.profiles:
        errors.append("no profiles defined")
    seen: set[str] = set()
    for e in cfg.entries:
        where = f"{e.section}/{e.subsection}/{e.id}"
        if e.id not in cfg.library:
            errors.append(f"{where}: unknown artifact")
        if e.id in seen:
            errors.append(f"{where}: listed more than once")
        if e.profile not in cfg.profiles:
            errors.append(f"{where}: unknown profile {e.profile!r}")
        seen.add(e.id)
    for sec, subs in (cfg.doc.get("sections") or {}).items():
        if not subs:
            errors.append(f"section {sec!r} is empty")
        for sub, arts in (subs or {}).items():
            if not arts:
                errors.append(f"subsection {sec}/{sub} is empty")
    for id in seen & cfg.library.keys():
        for req in cfg.library[id].requires:
            if req not in cfg.library:
                errors.append(f"{id}: requires unknown artifact {req!r}")
    errors += [f"questions.skip: unknown question {q!r}" for q in cfg.skip if q not in QUESTIONS]
    errors += validate_answers(cfg)
    return errors


def validate_answers(cfg: Config) -> list[str]:
    errors: list[str] = []
    roles = {a.role for id in cfg.ids if (a := cfg.library.get(id)) and a.role}
    for key, value in cfg.answers.items():
        if key == "profile":
            if value not in cfg.profiles:
                errors.append(f"answers.profile: unknown profile {value!r}")
        elif key in QUESTIONS:
            if value not in QUESTIONS[key].choices:
                errors.append(f"answers.{key}: {value!r} is not one of {list(QUESTIONS[key].choices)}")
        elif key in roles:
            art = cfg.library.get(value)
            if not art or art.role != key or value not in cfg.ids:
                errors.append(f"answers.{key}: {value!r} is not a {key} provider in this config")
        else:
            errors.append(f"answers.{key}: not a profile, role or question")
    return errors


def load_user_artifacts() -> None:
    """Import ~/.config/rigsmith/artifacts/*.py so they register into the library."""
    for path in sorted((config_home() / "artifacts").glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"rigsmith_user_{path.stem}", path)
        if spec and spec.loader:
            spec.loader.exec_module(importlib.util.module_from_spec(spec))


def dump(doc: Any) -> str:
    buf = StringIO()
    yaml().dump(doc, buf)
    return buf.getvalue()
