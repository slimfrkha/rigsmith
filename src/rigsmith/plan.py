"""From a config + filters + answers to an ordered plan of artifacts."""

from dataclasses import dataclass, field

from rigsmith.config import Config, ConfigError, Entry
from rigsmith.model import QUESTIONS, Artifact, Platform, Question


def select(
    cfg: Config,
    *,
    ids: list[str] | tuple[str, ...] = (),
    profile: str | None = None,
    sections: list[str] | tuple[str, ...] = (),
) -> list[Entry]:
    """Filter the menu. OR within a flag, AND across flags; ids AND with the rest."""
    unknown = [i for i in ids if cfg.entry(i) is None]
    if unknown:
        raise ConfigError(f"not in config {cfg.name}: {', '.join(unknown)}")
    known = {(e.section, e.subsection) for e in cfg.entries}
    for s in sections:
        sec, _, sub = s.partition("/")
        if not any(k[0] == sec and (not sub or k[1] == sub) for k in known):
            raise ConfigError(f"no section {s!r} in config {cfg.name}")
    if profile is not None and profile not in cfg.profiles:
        raise ConfigError(f"unknown profile {profile!r} (profiles: {', '.join(cfg.profiles)})")

    def in_sections(e: Entry) -> bool:
        return not sections or any(
            e.section == sec and (not sub or e.subsection == sub)
            for sec, _, sub in (s.partition("/") for s in sections)
        )

    cutoff = cfg.profiles.index(profile) if profile else len(cfg.profiles)
    return [
        e
        for e in cfg.entries
        if in_sections(e) and cfg.profiles.index(e.profile) <= cutoff and (not ids or e.id in ids)
    ]


def questions_for(cfg: Config, ids: list[str]) -> list[Question]:
    """Questions referenced by at least one artifact in `ids`, minus the config's skip list."""
    arts = [cfg.library[i] for i in ids]
    return [q for q in QUESTIONS.values() if q.id not in cfg.skip and any(q.referenced_by(a) for a in arts)]


def roles_for(cfg: Config, ids: list[str]) -> dict[str, list[str]]:
    """Roles with 2+ providers among `ids`, in config order."""
    roles: dict[str, list[str]] = {}
    for i in ids:
        if role := cfg.library[i].role:
            roles.setdefault(role, []).append(i)
    return {r: c for r, c in roles.items() if len(c) > 1}


@dataclass
class Plan:
    order: list[str]  # artifact ids, dependencies first
    reasons: dict[str, str]  # id -> "selected" | "dependency of X"
    answers: dict[str, str]  # resolved profile/roles/questions
    env: dict[str, str]
    skipped: dict[str, str] = field(default_factory=dict)  # id -> why
    warnings: list[str] = field(default_factory=list)
    replace: list[str] = field(default_factory=list)  # installed role providers to uninstall afterwards


def resolve_profile(cfg: Config, profile: str | None, ids: list[str] | tuple[str, ...], answers: dict[str, str]):
    """-p, else answers.profile, else the first profile. Explicit ids alone imply no cutoff."""
    if profile:
        return profile
    if ids:
        return None
    return answers.get("profile") or cfg.profiles[0]


def build(
    cfg: Config,
    p: Platform,
    *,
    ids: list[str] | tuple[str, ...] = (),
    profile: str | None = None,
    sections: list[str] | tuple[str, ...] = (),
    answers: dict[str, str] | None = None,
    picked: list[str] | None = None,
    remembered: dict[str, str] | None = None,
) -> Plan:
    """Resolve a selection into an ordered plan. `picked` (the picker's result) replaces the filters."""
    answers = {**cfg.answers, **(answers or {})}
    prof = resolve_profile(cfg, profile, ids, answers)
    if prof:
        answers["profile"] = prof
    chosen = picked if picked is not None else [e.id for e in select(cfg, ids=ids, profile=prof, sections=sections)]
    plan = Plan(order=[], reasons={}, answers=answers, env={})

    # questions: env prefs + excluded tags (only when the picker didn't already decide)
    excluded: set[str] = set()
    for q in questions_for(cfg, chosen):  # explicit/config answer, else last run's, else the default
        a = q.clean(answers.get(q.id) or (remembered or {}).get(q.id) or q.default)
        if q.kind == "choice" and a not in q.choices:
            a = q.default
        answers[q.id] = a
        excluded |= q.excluded_tags(a)
        plan.env.update(q.env(a))
    if picked is None:
        chosen = [i for i in chosen if not excluded & set(cfg.library[i].tags)]

    # roles: one provider each. An installed provider always wins; never replace it implicitly.
    for role, cands in roles_for(cfg, chosen).items():
        installed = [i for i in cands if cfg.library[i].sources and cfg.library[i].present(p)]
        wanted = answers.get(role)
        if picked is not None:
            keep = [i for i in cands if i in picked]
            keep = keep[:1]
        elif installed:
            keep = installed[:1]
            if wanted and wanted != keep[0]:
                plan.warnings.append(f"{role}: keeping installed {keep[0]} (answer was {wanted})")
            if len(installed) > 1:
                plan.warnings.append(f"{role}: several providers installed ({', '.join(installed)}), left alone")
        else:
            keep = [wanted if wanted in cands else cands[0]]
        if keep:
            answers[role] = keep[0]
        chosen = [i for i in chosen if i not in cands or i in keep]

    # availability + dependency closure (requires resolve against the library, not just the config)
    def add(i: str, reason: str) -> None:
        if i in plan.reasons or i in plan.skipped:
            return
        art = cfg.library.get(i)
        if art is None:
            raise ConfigError(f"unknown artifact {i!r} ({reason})")
        if not art.available(p):
            if reason == "selected":
                plan.skipped[i] = f"not available on {p}"
            return  # an n/a dependency is simply not needed on this platform
        plan.reasons[i] = reason
        for r in art.requirements(p):
            add(r, f"dependency of {i}")

    for i in chosen:
        add(i, "selected")
    plan.order = toposort(cfg.library, list(plan.reasons), p)
    return plan


def toposort(lib: dict[str, Artifact], ids: list[str], p: Platform) -> list[str]:
    """Dependencies first, otherwise stable in the given order."""
    out: list[str] = []
    seen: set[str] = set()
    wanted = set(ids)

    def visit(i: str, stack: tuple[str, ...]) -> None:
        if i in seen:
            return
        if i in stack:
            raise ConfigError(f"requires cycle: {' → '.join([*stack, i])}")
        for r in lib[i].requirements(p):
            if r in wanted:
                visit(r, (*stack, i))
        seen.add(i)
        out.append(i)

    for i in ids:
        visit(i, ())
    return out


def dependents(lib: dict[str, Artifact], target: str, among: list[str]) -> list[str]:
    return [i for i in among if target in lib[i].requires]


def with_orphans(lib: dict[str, Artifact], targets: list[str], managed: list[str], requested: set[str], p: Platform):
    """`targets` plus the managed dependencies only they need, never ones the user asked for themselves.

    The walk goes through dependencies rigsmith doesn't manage (e.g. a pre-existing git) to the managed ones
    behind them (the Homebrew snippet it pulled in).
    """
    out = list(targets)
    grew = True
    while grew:
        grew = False
        stack, seen = list(out), set(out)
        while stack:
            for dep in lib[i].requirements(p) if (i := stack.pop()) in lib else []:
                if dep in seen:
                    continue
                seen.add(dep)
                if dep not in managed:
                    stack.append(dep)  # not ours to remove, but look behind it
                elif dep not in requested and not any(
                    dep in lib[j].requirements(p) for j in managed if j not in out and j in lib
                ):
                    out.append(dep)
                    stack.append(dep)
                    grew = True
    return out


def inactive_providers(
    cfg: Config, p: Platform, answers: dict[str, str]
) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Installed role providers that aren't the active one: [(id, role, active)], plus roles that are ambiguous.

    The active provider is the one pinned in answers (config or remembered); with no pin, a lone installed provider
    is active. Several installed and none pinned: ambiguous, so nothing is called inactive for that role.
    """
    inactive, ambiguous = [], []
    for role, members in roles_for(cfg, cfg.ids).items():
        installed = [m for m in members if cfg.library[m].sources and cfg.library[m].present(p)]
        active = answers.get(role)
        if active not in members:
            active = installed[0] if len(installed) == 1 else None
        if active is None:
            if len(installed) > 1:
                ambiguous.append(f"{role}: {', '.join(installed)} are all installed; pin one under answers:")
            continue
        inactive += [(m, role, active) for m in installed if m != active]
    return inactive, ambiguous
