"""Interactive screens: questionnaire → picker (help, search) → confirm. Textual loads only when used."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Header, Input, OptionList, SelectionList, Static, Tree
from textual.widgets.option_list import Option
from textual.widgets.tree import TreeNode

from rigsmith import config as cfgmod
from rigsmith.config import Available, Config, ConfigError, Entry
from rigsmith.model import Platform
from rigsmith.plan import Plan, build, questions_for, roles_for, select
from rigsmith.runner import status
from rigsmith.state import State

ICON = {"installed": "[green]✓[/]", "partial": "[yellow]◐[/]", "missing": " ", "n/a": "[dim]–[/]"}


# ── questionnaire ────────────────────────────────────────────────────────────


@dataclass
class Step:
    key: str
    title: str
    options: list[tuple[str, str]]  # (value, label)
    default: str | list[str]
    help: str = ""
    multi: bool = False


class ChoiceScreen(Screen[Any]):
    """One question. Dismisses with the answer, or None to go back."""

    BINDINGS = [Binding("escape", "back", "Back"), Binding("q", "app.exit", "Quit")]

    def __init__(self, step: Step, n: int, total: int) -> None:
        super().__init__()
        self.step, self.n, self.total = step, n, total

    def compose(self) -> ComposeResult:
        s = self.step
        yield Header()
        yield Static(f"[dim]Question {self.n}/{self.total}[/]\n[bold]{s.title}[/]\n[dim]{s.help}[/]", classes="title")
        if s.multi:
            yield SelectionList[str](*[(label, v, v in s.default) for v, label in s.options], id="choices")
        else:
            yield OptionList(*[Option(label, id=v) for v, label in s.options], id="choices")
        keys = "space toggle · enter next" if s.multi else "↑↓ choose · enter next"
        yield Static(f"[dim]{keys} · esc back · q quit[/]", classes="hint")
        yield Footer()

    def on_mount(self) -> None:
        choices = self.query_one("#choices")
        choices.focus()
        if isinstance(choices, OptionList) and not self.step.multi:
            values = [v for v, _ in self.step.options]
            d = self.step.default
            choices.highlighted = values.index(d) if isinstance(d, str) and d in values else 0

    def action_submit(self) -> None:
        self.dismiss(list(self.query_one(SelectionList).selected))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if not self.step.multi:
            self.dismiss(event.option.id)

    def action_back(self) -> None:
        self.dismiss(None)


class MultiChoiceScreen(ChoiceScreen):
    BINDINGS = [Binding("enter", "submit", "Next", priority=True)]


def install_steps(
    cfg: Config,
    p: Platform,
    ids: list[str],
    profile: str | None,
    sections: list[str],
    answers: dict[str, str],
    chosen: list[str],
) -> list[Step]:
    """The questionnaire for the current answers: later questions depend on earlier ones."""
    steps: list[Step] = []
    if not profile and not ids:
        counts = [len(select(cfg, profile=pf)) for pf in cfg.profiles]
        steps.append(
            Step(
                "profile",
                "How much do you want installed?",
                [(pf, f"{pf}  [dim]({n} artifacts)[/]") for pf, n in zip(cfg.profiles, counts, strict=True)],
                answers.get("profile") or cfg.profiles[0],
                "Profiles are cumulative: each one includes everything before it.",
            )
        )
    if not sections and not ids:
        secs = list(dict.fromkeys(e.section for e in cfg.entries))
        n = {s: sum(e.section == s for e in cfg.entries) for s in secs}
        steps.append(
            Step(
                "sections",
                "Which areas are you interested in?",
                [(s, f"{s}  [dim]({n[s]})[/]") for s in secs],
                chosen or secs,
                "You can still pick individual tools on the next screen.",
                multi=True,
            )
        )
    prof = profile or answers.get("profile") or (None if ids else cfg.profiles[0])
    scope = [e.id for e in select(cfg, ids=ids, profile=prof, sections=chosen or sections)]
    for role, cands in roles_for(cfg, scope).items():
        installed = [c for c in cands if cfg.library[c].sources and cfg.library[c].present(p)]
        wanted = answers.get(role, "")
        default = installed[0] if installed else wanted if wanted in cands else cands[0]
        options = [
            (c, f"{c}{' [green](installed)[/]' if c in installed else ''}  [dim]{cfg.library[c].help}[/]")
            for c in cands
        ]
        steps.append(Step(role, f"Pick your {role}", options, default, "Only one can be active at a time."))
    for q in questions_for(cfg, scope):
        steps.append(Step(q.id, q.text, [(c, c) for c in q.choices], answers.get(q.id, q.default), q.help))
    return steps


# ── picker ───────────────────────────────────────────────────────────────────


class HelpScreen(ModalScreen[None]):
    BINDINGS = [Binding(k, "dismiss", show=False) for k in ("escape", "h", "q", "enter", "space")]

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text

    def compose(self) -> ComposeResult:
        yield Static(self.text, id="help")


class PickTree(Tree[str]):
    BINDINGS = [
        Binding("space", "screen.pick", "Toggle"),
        Binding("tab", "toggle_node", "Expand/collapse"),
        Binding("enter", "screen.submit", "Continue"),
    ]


class PickerScreen(Screen[Any]):
    """Sections → subsections → artifacts with checkboxes (radio buttons for roles)."""

    BINDINGS = [
        Binding("h", "help", "Help"),
        Binding("slash", "search", "Search"),
        Binding("escape", "cancel", "Quit"),
        Binding("q", "cancel", "Quit", show=False),
        *(Binding(str(k), f"set_profile({k})", f"profile {k}", show=k <= 3) for k in range(1, 10)),
    ]

    def __init__(
        self,
        cfg: Config,
        p: Platform,
        entries: list[Entry],
        ticked: set[str],
        mode: str = "install",  # install | uninstall | init
        title: str = "",
    ) -> None:
        super().__init__()
        self.cfg, self.p, self.entries, self.mode = cfg, p, entries, mode
        self.picked = set(ticked)
        self.profiles = {e.id: e.profile for e in entries}
        self.status = {e.id: status(cfg.library[e.id], p) for e in entries}
        self.roles = {i: r for r, members in roles_for(cfg, [e.id for e in entries]).items() for i in members}
        self.nodes: dict[str, TreeNode[str]] = {}
        self.filter = ""
        self.title_text = title

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "set_profile":  # profile keys only exist in `init`, for profiles that exist
            return self.mode == "init" and int(str(parameters[0])) <= len(self.cfg.profiles)
        return True

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self.title_text or self._title(), classes="title")
        yield Input(placeholder="search id, help or section… (esc to close)", id="search")
        yield PickTree("menu", id="tree")
        yield Footer()

    def _title(self) -> str:
        verb = {"install": "install", "uninstall": "uninstall", "init": "include in your config"}[self.mode]
        return f"[bold]Pick what to {verb}[/]  [dim]space toggle · enter continue · h help · / search · tab fold[/]"

    def on_mount(self) -> None:
        self.query_one("#search").display = False
        tree = self.query_one(PickTree)
        tree.show_root = False
        self.rebuild()
        tree.focus()

    def shown_entries(self) -> list[Entry]:
        f = self.filter.lower()
        return [
            e
            for e in self.entries
            if not f or f in e.id or f in self.cfg.library[e.id].help.lower() or f in e.section or f in e.subsection
        ]

    def rebuild(self) -> None:
        tree = self.query_one(PickTree)
        tree.clear()
        self.nodes.clear()
        sections: dict[str, TreeNode[str]] = {}
        subs: dict[tuple[str, str], TreeNode[str]] = {}
        for e in self.shown_entries():
            if e.section not in sections:
                sections[e.section] = tree.root.add(e.section, data=f"§{e.section}", expand=True)
            key = (e.section, e.subsection)
            if key not in subs:
                subs[key] = sections[e.section].add(e.subsection, data=f"§{e.section}/{e.subsection}", expand=True)
            self.nodes[e.id] = subs[key].add_leaf(self.label(e.id), data=e.id)
        self.refresh_groups()

    def label(self, id: str) -> str:
        art = self.cfg.library[id]
        on = id in self.picked
        box = ("◉" if on else "○") if id in self.roles else ("☑" if on else "☐")
        st = self.status[id]
        w = max(len(e.id) for e in self.entries)
        text = f"{box} {ICON[st]} {id:<{w}}  {self.profiles[id]:<13}  [dim]{art.help}[/]"
        return f"[dim]{text}[/]" if st == "n/a" else text

    def refresh_groups(self) -> None:
        tree = self.query_one(PickTree)
        for sec in tree.root.children:
            for sub in sec.children:
                ids = [n.data for n in sub.children if n.data]
                sub.set_label(
                    f"{str(sub.data)[1:].split('/')[1]}  [dim]{sum(i in self.picked for i in ids)}/{len(ids)}[/]"
                )
            ids = [leaf.data for sub in sec.children for leaf in sub.children if leaf.data]
            sec.set_label(f"[bold]{str(sec.data)[1:]}[/]  [dim]{sum(i in self.picked for i in ids)}/{len(ids)}[/]")

    def relabel(self, *ids: str) -> None:
        for i in ids:
            if i in self.nodes:
                self.nodes[i].set_label(self.label(i))
        self.refresh_groups()

    def set_picked(self, id: str, on: bool) -> list[str]:
        if self.status[id] == "n/a" and self.mode != "init":
            return []
        changed = [id]
        if on:
            self.picked.add(id)
            if id in self.roles and self.mode == "install":  # radio: one provider per role
                mates = [m for m, r in self.roles.items() if r == self.roles[id] and m != id and m in self.picked]
                self.picked -= set(mates)
                changed += mates
        else:
            self.picked.discard(id)
        return changed

    def action_pick(self) -> None:
        node = self.query_one(PickTree).cursor_node
        if node is None or node.data is None:
            return
        if node.data.startswith("§"):  # a group: tick all, or untick all if all were ticked
            leaves = [n.data for n in _leaves(node) if n.data]
            on = not all(i in self.picked for i in leaves)
            changed = [c for i in leaves for c in self.set_picked(i, on)]
        else:
            changed = self.set_picked(node.data, node.data not in self.picked)
        self.relabel(*changed)

    def action_set_profile(self, k: int) -> None:
        node = self.query_one(PickTree).cursor_node
        if node and node.data and not node.data.startswith("§"):
            self.profiles[node.data] = self.cfg.profiles[k - 1]
            self.relabel(node.data)

    def action_help(self) -> None:
        node = self.query_one(PickTree).cursor_node
        if node and node.data and not node.data.startswith("§"):
            self.app.push_screen(HelpScreen(describe(self.cfg, node.data, self.p, self.status[node.data])))

    def action_search(self) -> None:
        box = self.query_one("#search", Input)
        box.display = True
        box.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.filter = event.value.strip()
        self.rebuild()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.query_one(PickTree).focus()

    def on_key(self, event) -> None:
        box = self.query_one("#search", Input)
        if event.key == "escape" and box.has_focus:
            event.stop()
            box.value, box.display = "", False
            self.query_one(PickTree).focus()

    def action_submit(self) -> None:
        order = [e.id for e in self.entries if e.id in self.picked]
        self.dismiss({"picked": order, "profiles": self.profiles} if self.mode == "init" else order)

    def action_cancel(self) -> None:
        self.dismiss(None)


def _leaves(node: TreeNode[str]) -> list[TreeNode[str]]:
    return [n for c in node.children for n in (_leaves(c) if c.children else [c])]


def describe(cfg: Config, id: str, p: Platform, st: str) -> str:
    art = cfg.library[id]
    src = art.source(p)
    rows = [
        f"[bold]{id}[/]  {ICON[st]} {st}",
        "",
        art.help,
        "",
        f"[dim]source:[/]   {src or ('config only' if not art.sources else 'not available on ' + str(p))}",
    ]
    if art.requires:
        rows.append(f"[dim]requires:[/] {', '.join(art.requires)}")
    if art.role:
        rows.append(f"[dim]role:[/]     {art.role} (only one provider at a time)")
    if art.tags:
        rows.append(f"[dim]tags:[/]     {', '.join(art.tags)}")
    if art.snippets:
        rows.append(f"[dim]snippets:[/] {', '.join(s.name for s in art.snippets)}")
    if art.settings:
        rows.append(f"[dim]settings:[/] {', '.join(s.key for s in art.settings)}")
    rows += [f"[yellow]note:[/] {n}" for n in art.notes]
    return "\n".join(rows) + "\n\n[dim]any key to close[/]"


# ── confirm ──────────────────────────────────────────────────────────────────


class ConfirmScreen(Screen[str | None]):
    BINDINGS = [
        Binding("y", "go", "Install"),
        Binding("enter", "go", "Install", show=False),
        Binding("b", "back", "Back to picker"),
        Binding("escape", "back", "Back", show=False),
        Binding("q", "app.exit", "Quit"),
    ]

    def __init__(self, lines: list[str], verb: str = "install") -> None:
        super().__init__()
        self.lines, self.verb = lines, verb

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"[bold]Ready to {self.verb}[/]  [dim]y/enter go · b back · q quit[/]", classes="title")
        with VerticalScroll():
            yield Static("\n".join(self.lines))
        yield Footer()

    def action_go(self) -> None:
        self.dismiss("go")

    def action_back(self) -> None:
        self.dismiss("back")


# ── app + flows ──────────────────────────────────────────────────────────────

CSS = """
.title { padding: 1 2 0 2; }
.hint { padding: 0 2; }
#tree { margin: 1 2; height: 1fr; }
#choices { margin: 1 2; height: auto; max-height: 1fr; }
VerticalScroll { padding: 0 2; }
#search { margin: 0 2; }
#help { width: 80%; max-width: 100; height: auto; padding: 1 2; border: round $accent; background: $panel; }
HelpScreen { align: center middle; }
"""


class Flow(App[Any]):
    CSS = CSS
    TITLE = "rigsmith"

    def __init__(self, job: Callable[[App[Any]], Awaitable[Any]]) -> None:
        super().__init__()
        self.job = job

    def on_mount(self) -> None:
        self.run_job()

    @work(exclusive=True)
    async def run_job(self) -> None:
        self.exit(await self.job(self))


async def questionnaire(app: App[Any], cfg: Config, p: Platform, ids, profile, sections) -> tuple | None:
    answers, chosen, i = dict(cfg.answers), list(sections), 0
    while True:
        steps = install_steps(cfg, p, ids, profile, sections, answers, chosen)
        if i >= len(steps):
            return answers, chosen
        step = steps[i]
        screen = (MultiChoiceScreen if step.multi else ChoiceScreen)(step, i + 1, len(steps))
        res = await app.push_screen_wait(screen)
        if res is None:
            if i == 0:
                return None
            i -= 1
            continue
        if step.key == "sections":
            chosen = res
        else:
            answers[step.key] = res
        i += 1


def replacements(cfg: Config, p: Platform, picked: list[str]) -> list[str]:
    """Installed, rigsmith-managed role providers the user swapped for another one."""
    state, out = State(), []
    for members in roles_for(cfg, cfg.ids).values():
        if any(m in picked for m in members):
            out += [m for m in members if m not in picked and state.managed(m) and cfg.library[m].present(p)]
    return out


class PathScreen(Screen[str | None]):
    """Ask for the path of a YAML config."""

    BINDINGS = [Binding("escape", "back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("[bold]Path to your YAML config[/]\n[dim]enter to use it · esc back[/]", classes="title")
        yield Input(placeholder="~/dotfiles/rigsmith.yaml", id="path")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip() or None)

    def action_back(self) -> None:
        self.dismiss(None)


OWN_FILE = "__file__"


def base_step(bases: list[Available]) -> Step:
    options = [(a.name, f"{a.name:<14} [dim]{a.count:>3} tools · {a.description}[/]") for a in bases]
    return Step(
        "base",
        "Start from which menu?",
        [*options, (OWN_FILE, "a YAML file of your own…")],
        "reference",
        "Presets are curated per kind of work; reference has everything. You can still adjust it all later.",
    )


async def choose_base(app: App[Any], bases: list[Available]) -> tuple[str, Config] | None:
    """Pick a bundled config or a YAML path, loaded and validated. None if the user backs out."""
    step = base_step(bases)
    while True:
        choice = await app.push_screen_wait(ChoiceScreen(step, 1, 1))
        if choice is None:
            return None
        if choice == OWN_FILE:
            choice = await app.push_screen_wait(PathScreen())
            if choice is None:
                continue
        try:
            cfgmod.load_user_artifacts()
            cfg = cfgmod.load(choice)
            if errors := cfgmod.validate(cfg):
                raise ConfigError("; ".join(errors[:3]))
        except ConfigError as e:
            app.notify(str(e), title="Can't use that config", severity="error", timeout=8)
            continue
        return choice, cfg


def pick_config(bases: list[Available]) -> str | None:
    """`rigsmith use` without an argument."""

    async def job(app: App[Any]) -> str | None:
        picked = await choose_base(app, bases)
        return picked[0] if picked else None

    return Flow(job).run()


def interactive_install(
    cfg: Config, p: Platform, *, ids, profile, sections, bases: list[Available] | None = None
) -> tuple[Plan, Config, str | None] | None:
    """Questionnaire → picker → confirm. With `bases` (first run, no config yet) it starts by picking a menu."""
    from rigsmith.cli import plan_report  # noqa: PLC0415  (cli imports this module lazily)

    async def job(app: App[Any]) -> tuple[Plan, Config, str | None] | None:
        menu, base = cfg, None
        if bases:
            picked = await choose_base(app, bases)
            if picked is None:
                return None
            base, menu = picked
        q = await questionnaire(app, menu, p, ids, profile, sections)
        if q is None:
            return None
        answers, chosen = q
        prof = profile or answers.get("profile")
        start = build(menu, p, ids=ids, profile=prof, sections=chosen or sections, answers=answers)
        ticked = {i for i in start.order if menu.entry(i)}
        while True:
            picked_ids = await app.push_screen_wait(PickerScreen(menu, p, menu.entries, ticked))
            if picked_ids is None:
                return None
            plan = build(menu, p, answers=answers, picked=picked_ids)
            plan.replace = replacements(menu, p, picked_ids)
            choice = await app.push_screen_wait(ConfirmScreen(plan_report(menu, plan, p)))
            if choice == "go":
                return plan, menu, base
            if choice is None:
                return None
            ticked = set(picked_ids)

    return Flow(job).run()


def pick_uninstall(cfg: Config, p: Platform, candidates: list[str]) -> list[str] | None:
    if not candidates:
        return []
    entries = [e for e in cfg.entries if e.id in candidates]

    async def job(app: App[Any]) -> list[str] | None:
        return await app.push_screen_wait(PickerScreen(cfg, p, entries, set(), mode="uninstall"))

    return Flow(job).run()


def pick_scope(cfg: Config, p: Platform, entries: list[Entry], ticked: set[str]) -> dict | None:
    """init: choose which artifacts the new config includes and their profiles."""

    async def job(app: App[Any]) -> dict | None:
        return await app.push_screen_wait(PickerScreen(cfg, p, entries, ticked, mode="init"))

    return Flow(job).run()
