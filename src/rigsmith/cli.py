"""rigsmith command line: use / install / scan / uninstall / init."""

import dataclasses
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.text import Text

from rigsmith import answers as answersmod
from rigsmith import config as cfgmod
from rigsmith import library  # noqa: F401  (registers built-in artifacts)
from rigsmith.config import Config, ConfigError, Entry
from rigsmith.model import Platform, ensure_path
from rigsmith.plan import (
    Plan,
    active_providers,
    build,
    inactive_providers,
    plan_removal,
    questions_for,
    removal_candidates,
    select,
)
from rigsmith.runner import Result, Runner, pending, status
from rigsmith.script import install_script, uninstall_script
from rigsmith.shell import conflicts
from rigsmith.state import State

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Set up a machine from a curated, extensible library of tools and configs. Start with `rigsmith use`.",
)
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
ScriptOpt = Annotated[
    bool,
    typer.Option(
        "--script",
        help="Print the shell commands this would run, and change nothing. For reading: running it yourself "
        "leaves no receipts.",
    ),
]


def as_command() -> str:
    """The rigsmith command that does for real what a --script run shows."""
    return shlex.join(["rigsmith", *(a for a in sys.argv[1:] if a != "--script")])


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


def with_managed(active: Config, state: State) -> Config:
    """The active config plus every managed artifact it doesn't list (e.g. installed from an earlier config)."""
    ref = library_config(active)
    extra = [e for e in ref.entries if active.entry(e.id) is None and state.managed(e.id)]
    return dataclasses.replace(active, entries=[*active.entries, *extra], library=ref.library)


def header(cfg: Config) -> None:
    console.print(f"[dim]config: {cfgmod.label(cfg.name)}[/]")


ICON = {
    "installed": "[green]✓[/]",
    "partial": "[yellow]◐[/]",
    "missing": "[red]✗[/]",
    "inactive": "[dim]○[/]",  # a role alternative that isn't the active one, and isn't installed: as intended
    "n/a": "[dim]–[/]",
}


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
    header(active)
    roles_active = active_providers(cfg, p, answersmod.resolve(active, state.answers))

    counts: dict[str, int] = {}
    last: tuple[str, str] | None = None
    w = max((len(e.id) for e in entries), default=0)
    for e in entries:
        if (e.section, e.subsection) != last:
            console.print(f"[bold magenta]{e.section}[/] [magenta]/ {e.subsection}[/]")
            last = (e.section, e.subsection)
        art = cfg.library[e.id]
        st = status(art, p, state.answers)
        if st == "missing" and art.role in roles_active and roles_active[art.role] != e.id:
            st = "inactive"
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
    inactive, ambiguous = inactive_providers(cfg, p, answersmod.resolve(active, state.answers))
    for i, role, winner in inactive:
        console.print(
            f"[yellow]⚠ {i} is installed but inactive ({role} → {winner}) — `rigsmith uninstall --inactive`[/]"
        )
    for line in ambiguous:
        console.print(f"[yellow]⚠ {line}[/]")
    elsewhere = [e.id for e in with_managed(active, state).entries if active.entry(e.id) is None]
    if elsewhere and not (all or new):
        console.print(
            f"[cyan]ℹ rigsmith also manages {len(elsewhere)} not in this config: {', '.join(elsewhere[:8])}"
            f"{'…' if len(elsewhere) > 8 else ''} — `rigsmith uninstall` still sees them[/]"
        )


# ── install ──────────────────────────────────────────────────────────────────


def plan_report(cfg: Config, plan: Plan, p: Platform) -> list[str]:
    """The diff screen as markup lines: answers, already in place, to install, caveats."""
    state = State()
    used = {"profile"} | {cfg.library[i].role for i in plan.order} | {q.id for q in questions_for(cfg, plan.order)}
    lines = ["[bold]Answers:[/] " + ", ".join(f"{k}={v}" for k, v in plan.answers.items() if k in used)]
    todo, done, irreversible, labels = [], [], [], {}
    for i in plan.order:
        effs = pending(cfg.library[i], p, state, plan.answers)
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
        lines += ["", "[yellow]Replaced (uninstalled after install):[/] " + ", ".join(plan.replace.order)]
        lines += [f"  [yellow]⚠ {w}[/]" for w in plan.replace.warnings]
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
    script: ScriptOpt = False,
) -> None:
    """Questionnaire → picker → diff → confirm → install."""
    cfg = _load(config)
    p = _platform(unsupported)
    base = None
    if script:
        plan = build(cfg, p, ids=ids or [], profile=profile, sections=section or [], remembered=State().answers)
        typer.echo(install_script(cfg, plan, p, as_command()), nl=False)
        return
    if yes or dry_run:
        plan = build(cfg, p, ids=ids or [], profile=profile, sections=section or [], remembered=State().answers)
    else:
        from rigsmith.tui import interactive_install  # noqa: PLC0415  (Textual loads lazily)

        first_run = config is None and not cfgmod.user_config().exists()
        bases = cfgmod.available() if first_run else None
        result = interactive_install(cfg, p, ids=ids or [], profile=profile, sections=section or [], bases=bases)
        if result is None:
            raise typer.Exit(1)
        plan, cfg, base = result
    header(cfg)
    show_plan(cfg, plan, p)
    if dry_run:
        return
    if not plan.order:
        console.print("Nothing selected.")
        return
    runner = Runner(p, say=console.print)
    res = runner.install(cfg, plan)
    show_result(res, "Installed")
    if plan.replace and not res.failed:
        show_result(runner.uninstall(cfg, plan.replace.order), "Replaced")
    save = f"\nSave {base} as your config, so scan/install/uninstall use it from now on?"
    if base and not cfgmod.user_config().exists() and typer.confirm(save, default=True):
        console.print(f"[green]✓[/] saved {cfgmod.copy_to_user(base)} (yours to edit)")
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
    inactive: Annotated[
        bool,
        typer.Option("--inactive", help="Remove installed synonyms that aren't the active provider of their role."),
    ] = False,
    script: ScriptOpt = False,
) -> None:
    """Undo what rigsmith installed, from its receipts (even if it came from another config)."""
    p, state = Platform.detect(), State()
    cfg = with_managed(_load(config), state)
    if script:
        dry_run = True  # never the picker, never a change
    else:
        header(cfg)
    candidates, warnings, notes = removal_candidates(
        cfg,
        p,
        state,
        ids=ids or [],
        profile=profile,
        sections=section or [],
        include_unmanaged=include_unmanaged,
        inactive=inactive,
    )
    for line in warnings:
        console.print(f"[yellow]⚠ {line}[/]")
    for line in notes:
        console.print(f"  {line}")
    if not yes and not dry_run:
        from rigsmith.tui import pick_uninstall  # noqa: PLC0415

        picked = pick_uninstall(cfg, p, candidates)
        if picked is None:
            raise typer.Exit(1)
        candidates = picked
    rm = plan_removal(cfg, p, state, candidates, include_unmanaged or inactive)
    if script:
        typer.echo(uninstall_script(cfg, rm.order, p, rm.include_unmanaged, as_command()), nl=False)
        return
    if not rm.order:
        console.print("Nothing rigsmith installed matches.")
        return
    console.print(f"[bold]To uninstall ({len(rm.order)}):[/] " + ", ".join(rm.order))
    for line in rm.warnings:
        console.print(f"[yellow]⚠ {line}[/]")
    if rm.kept:
        console.print("[dim]Pre-existing packages left alone: " + ", ".join(rm.kept) + "[/]")
    if dry_run:
        return
    if not yes and not typer.confirm("Proceed?", default=False):
        raise typer.Exit(1)
    res = Runner(p, say=console.print).uninstall(cfg, rm.order, rm.include_unmanaged)
    show_result(res, "Uninstalled")
    if res.failed:
        raise typer.Exit(1)


# ── use ──────────────────────────────────────────────────────────────────────


@app.command()
def use(
    source: Annotated[
        str | None, typer.Argument(help="Preset name or path to a YAML config.", show_default=False)
    ] = None,
    yes: Annotated[bool, typer.Option("-y", "--yes", help="Replace an existing config without asking.")] = False,
) -> None:
    """Choose your config: copies a preset (or your own YAML) to ~/.config/rigsmith/config.yaml."""
    if source is None:
        if not sys.stdin.isatty():
            for a in cfgmod.available():
                console.print(f"  [bold]{a.name:<14}[/] {a.count:>3} tools  [dim]{a.description}[/]")
            console.print("\nPick one: [bold]rigsmith use <name>[/] (or a path to your own YAML)")
            raise typer.Exit(1)
        from rigsmith.tui import pick_config  # noqa: PLC0415

        source = pick_config(cfgmod.available())
        if source is None:
            raise typer.Exit(1)
    cfg = _load(source)
    dest = cfgmod.user_config()
    if dest.exists() and not yes and not typer.confirm(f"Replace {dest} ({cfgmod.label(str(dest))})?", default=False):
        raise typer.Exit(1)
    cfgmod.copy_to_user(source)
    console.print(f"[green]✓[/] now using {cfgmod.label(str(dest))}: {len(cfg.entries)} artifacts")
    console.print("Next: [bold]rigsmith install[/] (or `rigsmith scan` to see where you stand)")


# ── init ─────────────────────────────────────────────────────────────────────


@app.command()
def init(
    from_: Annotated[str | None, typer.Option("--from", help="Config or preset to fork (default: reference).")] = None,
    output: Annotated[str | None, typer.Option("-o", "--output", help="Where to write (default: user config).")] = None,
) -> None:
    """Create your own menu: pick artifacts and profiles, then optionally restructure in $EDITOR."""
    from rigsmith.tui import pick_scope  # noqa: PLC0415

    src = _load(from_ or "reference")
    p = Platform.detect()
    ref = library_config(src)
    entries = [*src.entries, *(e for e in ref.entries if src.entry(e.id) is None)]  # new ones arrive unticked
    picked = pick_scope(src, p, entries, set(src.ids))
    if picked is None:
        raise typer.Exit(1)
    doc = cfgmod.fork(src, entries, picked["picked"], picked["profiles"])
    dest = Path(output).expanduser() if output else cfgmod.user_config()
    if dest.exists() and not typer.confirm(f"{dest} exists. Overwrite?", default=False):
        raise typer.Exit(1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(cfgmod.dump(doc))
    console.print(f"[green]✓[/] wrote {dest} ({len(picked['picked'])} artifacts)")
    if typer.confirm("Restructure sections in your editor?", default=False):
        edit_until_valid(dest)
    hint = "rigsmith install" if dest == cfgmod.user_config() else f"rigsmith install -c {dest}"
    console.print(f"Next: [bold]{hint}[/]")


def edit_until_valid(path: Path) -> None:
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"
    while True:
        subprocess.run([*shlex.split(editor), str(path)], check=False)
        try:
            errors = cfgmod.validate(cfgmod.load(str(path)))
        except ConfigError as e:
            errors = [str(e)]
        if not errors:
            console.print(f"[green]✓[/] {path} is valid")
            return
        console.print("[red]✗ invalid config:[/]\n  " + "\n  ".join(errors))
        if not typer.confirm("Edit again?", default=True):
            console.print(f"[yellow]⚠ {path} is invalid; fix it before installing.[/]")
            return


def main() -> None:
    try:
        app()
    except ConfigError as e:
        console.print(f"[red]✗ {e}[/]")
        raise SystemExit(2) from None
