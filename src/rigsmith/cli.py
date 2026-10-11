"""rigsmith command line: init / install / scan / uninstall."""

from typing import Annotated

import typer
from rich.console import Console
from rich.text import Text

from rigsmith import config as cfgmod
from rigsmith import library  # noqa: F401  (registers built-in artifacts)
from rigsmith.config import Config, ConfigError, Entry
from rigsmith.model import Platform, ensure_path
from rigsmith.plan import Plan, build, dependents, select, toposort
from rigsmith.runner import Result, Runner, effects_for, pending, status
from rigsmith.shell import conflicts
from rigsmith.state import NOOP, State

app = typer.Typer(no_args_is_help=True, add_completion=False, help=__doc__)
console = Console(highlight=False)

Ids = Annotated[list[str] | None, typer.Argument(help="Artifact ids (AND with the filters).", show_default=False)]
ConfigOpt = Annotated[str | None, typer.Option("-c", "--config", help="Config file or preset name.")]
ProfileOpt = Annotated[str | None, typer.Option("-p", "--profile", help="Profile cutoff (cumulative).")]
SectionOpt = Annotated[
    list[str] | None,
    typer.Option("-s", "--section", help="SECTION or SECTION/SUB, repeatable.", show_default=False),
]
YesOpt = Annotated[bool, typer.Option("-y", "--yes", help="Non-interactive: defaults, no picker, no confirm.")]
DryOpt = Annotated[bool, typer.Option("--dry-run", help="Show the plan and exit.")]
UnsupportedOpt = Annotated[bool, typer.Option("--unsupported", help="Run on a platform rigsmith doesn't support.")]


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


def _platform(unsupported: bool) -> Platform:
    p = Platform.detect()
    if not p.supported and not unsupported:
        raise ConfigError(
            f"{p} is not a supported platform (macOS 14+, Ubuntu 22.04/24.04, Debian 12). "
            "Pass --unsupported to try anyway."
        )
    return p


def library_config(active: Config) -> Config:
    """The whole library: reference.yaml plus any user artifact it doesn't list."""
    ref = cfgmod.load("reference")
    ref.library = {**ref.library, **active.library}
    extra = [id for id in ref.library if ref.entry(id) is None]
    ref.entries += [Entry(id, "custom", "user", ref.profiles[-1]) for id in extra]
    return ref


ICON = {"installed": "[green]✓[/]", "partial": "[yellow]◐[/]", "missing": "[red]✗[/]", "n/a": "[dim]–[/]"}


# ── scan ─────────────────────────────────────────────────────────────────────


@app.command()
def scan(
    ids: Ids = None,
    config: ConfigOpt = None,
    profile: ProfileOpt = None,
    section: SectionOpt = None,
    all: Annotated[bool, typer.Option("--all", help="Scan the whole library, not just the config.")] = False,
    new: Annotated[bool, typer.Option("--new", help="Only library artifacts missing from the config.")] = False,
) -> None:
    """Show what is installed, partial, missing or unavailable, by section."""
    active = _load(config)
    cfg = library_config(active) if all or new else active
    entries = select(cfg, ids=ids or [], profile=profile, sections=section or [])
    if new:
        entries = [e for e in entries if active.entry(e.id) is None]
    p, state = Platform.detect(), State()

    counts: dict[str, int] = {}
    last: tuple[str, str] | None = None
    w = max((len(e.id) for e in entries), default=0)
    for e in entries:
        if (e.section, e.subsection) != last:
            console.print(f"[bold magenta]{e.section}[/] [magenta]/ {e.subsection}[/]")
            last = (e.section, e.subsection)
        art = cfg.library[e.id]
        st = status(art, p)
        counts[st] = counts.get(st, 0) + 1
        src = art.source(p)
        owner = "managed" if state.managed(e.id) else "pre-existing" if st in ("installed", "partial") else ""
        line = Text.from_markup(f"  {ICON[st]} ") + Text(
            f"{e.id:<{w}}  {e.profile:<13}  {src.name if src else 'config':<7}  {owner:<12}  "
        )
        line.append(art.help, style="dim")
        console.print(line, no_wrap=True, overflow="ellipsis")
    console.print(
        f"\n[bold]{len(entries)}[/] artifacts · "
        + " · ".join(f"{ICON[k]} {k} {v}" for k, v in counts.items())
        + f" · platform {p}{'' if p.supported else ' [yellow](unsupported)[/]'}"
    )
    if not (all or new) and cfg.name != str(cfgmod.bundled_dir() / "reference.yaml"):
        missing = [id for id in library_config(active).ids if active.entry(id) is None]
        if missing:
            console.print(f"[cyan]ℹ {len(missing)} library artifacts are not in your config — `scan --all --new`[/]")


# ── install ──────────────────────────────────────────────────────────────────


def plan_report(cfg: Config, plan: Plan, p: Platform) -> list[str]:
    """The diff screen as markup lines: answers, already in place, to install, caveats."""
    state = State()
    lines = ["[bold]Answers:[/] " + ", ".join(f"{k}={v}" for k, v in plan.answers.items())]
    todo, done, irreversible, labels = [], [], [], {}
    for i in plan.order:
        effs = pending(cfg.library[i], p, state)
        (todo if effs else done).append(i)
        labels[i] = ", ".join(e.label for e in effs)
        irreversible += [f"{i}: {e.label}" for e in effs if not e.reversible]
    if done:
        lines += ["", f"[green]Already in place ({len(done)}):[/] " + ", ".join(done)]
    if todo:
        lines += ["", f"[bold]To install ({len(todo)}):[/]"]
        for i in todo:
            why = "" if plan.reasons[i] == "selected" else f" ({plan.reasons[i]})"
            lines.append(f"  + {i}[dim]{why} — {labels[i]}[/]")
    lines += [f"  [dim]– {i}: {why}[/]" for i, why in plan.skipped.items()]
    if plan.replace:
        lines += ["", "[yellow]Replaced (uninstalled after install):[/] " + ", ".join(plan.replace)]
    if irreversible:
        lines += ["", "[yellow]Can't be undone by uninstall:[/]", *(f"  {x}" for x in irreversible)]
    pats = {i: cfg.library[i].conflicts for i in plan.order if cfg.library[i].conflicts}
    if found := conflicts(pats):
        lines += ["", "[yellow]Your ~/.zshrc may double-load these (rigsmith never edits your lines):[/]"]
        lines += [f"  {x}" for x in found]
    lines += [f"[yellow]⚠ {w}[/]" for w in plan.warnings]
    return lines


def show_plan(cfg: Config, plan: Plan, p: Platform) -> None:
    for line in plan_report(cfg, plan, p):
        console.print(line, no_wrap=line.startswith("  +"), overflow="ellipsis")


def show_result(res: Result, verb: str) -> None:
    console.print(
        f"\n[bold]{verb}:[/] {res.changes} changes · ✓ {len(res.ok)} · ✗ {len(res.failed)} · ⊘ {len(res.skipped)}"
    )
    for i, err in res.failed.items():
        console.print(f"  [red]✗ {i}: {err}[/]")
    for w in res.warnings:
        console.print(f"  [yellow]⚠ {w}[/]")
    if res.notes:
        console.print("\n[bold]Next steps:[/]\n  " + "\n  ".join(f"• {n}" for n in dict.fromkeys(res.notes)))
    if verb == "Installed" and res.changes:
        console.print("\nOpen a new terminal (or run `exec zsh`) to load the changes.")


@app.command()
def install(
    ids: Ids = None,
    config: ConfigOpt = None,
    profile: ProfileOpt = None,
    section: SectionOpt = None,
    yes: YesOpt = False,
    dry_run: DryOpt = False,
    unsupported: UnsupportedOpt = False,
) -> None:
    """Questionnaire → picker → diff → confirm → install."""
    cfg = _load(config)
    p = _platform(unsupported)
    if yes or dry_run:
        plan = build(cfg, p, ids=ids or [], profile=profile, sections=section or [])
    else:
        from rigsmith.tui import interactive_install  # noqa: PLC0415  (Textual loads lazily)

        plan = interactive_install(cfg, p, ids=ids or [], profile=profile, sections=section or [])
        if plan is None:
            raise typer.Exit(1)
    show_plan(cfg, plan, p)
    if dry_run:
        return
    if not plan.order:
        console.print("Nothing selected.")
        return
    runner = Runner(p, say=console.print)
    res = runner.install(cfg, plan.order, plan.env)
    show_result(res, "Installed")
    if plan.replace and not res.failed:
        show_result(runner.uninstall(cfg, plan.replace), "Replaced")
    if res.failed:
        raise typer.Exit(1)


# ── uninstall ────────────────────────────────────────────────────────────────


@app.command()
def uninstall(
    ids: Ids = None,
    config: ConfigOpt = None,
    profile: ProfileOpt = None,
    section: SectionOpt = None,
    yes: YesOpt = False,
    dry_run: DryOpt = False,
    include_unmanaged: Annotated[
        bool, typer.Option("--include-unmanaged", help="Also remove packages rigsmith didn't install.")
    ] = False,
) -> None:
    """Undo what rigsmith installed, from its receipts."""
    cfg = _load(config)
    p, state = Platform.detect(), State()
    scope = [e.id for e in select(cfg, ids=ids or [], profile=profile, sections=section or [])]
    present = {i for i in scope if include_unmanaged and status(cfg.library[i], p) != "missing"}
    candidates = [i for i in scope if state.managed(i) or i in present]
    if not yes and not dry_run:
        from rigsmith.tui import pick_uninstall  # noqa: PLC0415

        picked = pick_uninstall(cfg, p, candidates)
        if picked is None:
            raise typer.Exit(1)
        candidates = picked
    order = list(reversed(toposort(cfg.library, candidates, p)))
    if not order:
        console.print("Nothing rigsmith installed matches.")
        return
    console.print(f"[bold]To uninstall ({len(order)}):[/] " + ", ".join(order))
    installed_elsewhere = [i for i in cfg.ids if state.managed(i) and i not in order]
    for i in order:
        if needed := dependents(cfg.library, i, installed_elsewhere):
            console.print(f"[yellow]⚠ {i} is needed by: {', '.join(needed)} (they stay installed)[/]")
    if not include_unmanaged:
        kept = [
            i
            for i in order
            if any(
                (r := state.get(e.key)) and r.op == NOOP
                for e in effects_for(cfg.library[i], p)
                if e.key.startswith("pkg:")
            )
        ]
        if kept:
            console.print("[dim]Pre-existing packages left alone: " + ", ".join(kept) + "[/]")
    if dry_run:
        return
    if not yes and not typer.confirm("Proceed?", default=False):
        raise typer.Exit(1)
    res = Runner(p, say=console.print).uninstall(cfg, order, include_unmanaged)
    show_result(res, "Uninstalled")
    if res.failed:
        raise typer.Exit(1)


def main() -> None:
    try:
        app()
    except ConfigError as e:
        console.print(f"[red]✗ {e}[/]")
        raise SystemExit(2) from None
