"""From a config + filters + answers to an ordered plan of artifacts."""

from rigsmith.config import Config, ConfigError, Entry


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
