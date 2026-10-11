"""rigsmith command line: init / install / scan / uninstall."""

from typing import Annotated

import typer
from rich.console import Console
from rich.text import Text

from rigsmith import config as cfgmod
from rigsmith import library  # noqa: F401  (registers built-in artifacts)
from rigsmith.config import Config, ConfigError, Entry
from rigsmith.model import Platform, ensure_path
from rigsmith.plan import select

app = typer.Typer(no_args_is_help=True, add_completion=False, help=__doc__)
console = Console()

Ids = Annotated[
    list[str] | None, typer.Argument(help="Artifact ids (AND with the filters).", show_default=False)
]
ConfigOpt = Annotated[str | None, typer.Option("-c", "--config", help="Config file or preset name.")]
ProfileOpt = Annotated[str | None, typer.Option("-p", "--profile", help="Profile cutoff (cumulative).")]
SectionOpt = Annotated[
    list[str] | None,
    typer.Option("-s", "--section", help="SECTION or SECTION/SUB, repeatable.", show_default=False),
]


@app.callback()
def _root() -> None:
    """Set up a machine from a curated, extensible library of tools and configs."""


def _load(source: str | None) -> Config:
    cfgmod.load_user_artifacts()
    ensure_path()
    cfg = cfgmod.load(source)
    if errors := cfgmod.validate(cfg):
        raise ConfigError(f"invalid config {cfg.name}:\n  " + "\n  ".join(errors))
    return cfg


def library_config(active: Config) -> Config:
    """The whole library: reference.yaml plus any user artifact it doesn't list."""
    ref = cfgmod.load("reference")
    ref.library = {**ref.library, **active.library}
    extra = [id for id in ref.library if ref.entry(id) is None]
    ref.entries += [Entry(id, "custom", "user", ref.profiles[-1]) for id in extra]
    return ref


STATUS = {"installed": "[green]✓[/]", "missing": "[red]✗[/]", "n/a": "[dim]–[/]"}


def status(cfg: Config, id: str, p: Platform) -> str:
    art = cfg.library[id]
    if not art.available(p):
        return "n/a"
    if not art.sources:
        return "missing"  # config-only artifacts: refined once receipts exist
    return "installed" if art.present(p) else "missing"


@app.command()
def scan(
    ids: Ids = None,
    config: ConfigOpt = None,
    profile: ProfileOpt = None,
    section: SectionOpt = None,
    all: Annotated[bool, typer.Option("--all", help="Scan the whole library, not just the config.")] = False,
    new: Annotated[
        bool, typer.Option("--new", help="Only library artifacts missing from the config.")
    ] = False,
) -> None:
    """Show what is installed, missing or unavailable, by section."""
    active = _load(config)
    cfg = library_config(active) if all or new else active
    entries = select(cfg, ids=ids or [], profile=profile, sections=section or [])
    if new:
        entries = [e for e in entries if active.entry(e.id) is None]
    p = Platform.detect()

    counts: dict[str, int] = {}
    last: tuple[str, str] | None = None
    w = max((len(e.id) for e in entries), default=0)
    for e in entries:
        if (e.section, e.subsection) != last:
            console.print(f"[bold magenta]{e.section}[/] [magenta]/ {e.subsection}[/]")
            last = (e.section, e.subsection)
        art = cfg.library[e.id]
        st = status(cfg, e.id, p)
        counts[st] = counts.get(st, 0) + 1
        src = art.source(p)
        line = Text.from_markup(f"  {STATUS[st]} ") + Text(
            f"{e.id:<{w}}  {e.profile:<13}  {src.name if src else 'config':<7}  "
        )
        line.append(art.help, style="dim")
        console.print(line, no_wrap=True, overflow="ellipsis")
    console.print(
        f"\n[bold]{len(entries)}[/] artifacts · "
        + " · ".join(f"{STATUS[k]} {k} {v}" for k, v in counts.items())
        + f" · platform {p}{'' if p.supported else ' [yellow](unsupported)[/]'}"
    )
    if not (all or new):
        missing = [id for id in library_config(active).ids if active.entry(id) is None]
        if missing and cfg.name != str(cfgmod.bundled_dir() / "reference.yaml"):
            console.print(
                f"[cyan]ℹ {len(missing)} library artifacts are not in your config — `scan --all --new`[/]"
            )


def main() -> None:
    try:
        app()
    except ConfigError as e:
        console.print(f"[red]✗ {e}[/]")
        raise SystemExit(2) from None
