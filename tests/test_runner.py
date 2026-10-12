"""Install/uninstall semantics with a fake backend in a throwaway HOME."""

import json
from dataclasses import dataclass

import pytest

from rigsmith import config
from rigsmith.model import Artifact, Backend, Platform, Snippet, VSCodeSetting, backend
from rigsmith.plan import build
from rigsmith.runner import Runner, status
from rigsmith.settings import vscode_settings_path
from rigsmith.shell import BLOCK, zshrc

P = Platform.detect()
INSTALLED: set[str] = set()
FAIL: set[str] = set()


@backend("fake")
@dataclass
class Fake(Backend):
    def is_installed(self) -> bool:
        return self.pkg in INSTALLED

    def install(self) -> None:
        if self.pkg in FAIL:
            raise RuntimeError("boom")
        INSTALLED.add(self.pkg)

    def uninstall(self, snapshot=None) -> None:
        INSTALLED.discard(self.pkg)


RAN: list[str] = []


class Hooked(Artifact):
    def post_install(self) -> None:
        RAN.append(self.id)


MENU = """
profiles: [minimal, standard]
sections:
  s:
    a: {alpha: minimal, beta: minimal, gamma: standard, hooked: standard, editor: standard}
    p: {p1: minimal, p2: minimal}
"""


@pytest.fixture
def cfg():
    INSTALLED.clear()
    FAIL.clear()
    RAN.clear()
    c = config.parse(config.yaml().load(MENU))
    arts = [
        Artifact(id="alpha", help="a", sources=[Fake("alpha")], shell=Snippet("zoxide.zsh", 50), register=False),
        Artifact(id="beta", help="b", sources=[Fake("beta")], requires=["alpha"], register=False),
        Artifact(id="gamma", help="g", sources=[Fake("gamma")], register=False),
        Hooked(id="hooked", help="h", sources=[Fake("hooked")], register=False),
        Artifact(
            id="editor",
            help="e",
            settings=[VSCodeSetting("editor.fontSize", 16), VSCodeSetting("new.key", True)],
            register=False,
        ),
        Artifact(id="p1", help="p1", sources=[Fake("p1")], role="prompt", register=False),
        Artifact(id="p2", help="p2", sources=[Fake("p2")], role="prompt", register=False),
    ]
    c.library.update({a.id: a for a in arts})
    return c


def install(cfg, **kw):
    plan = build(cfg, P, **kw)
    return plan, Runner(P, say=lambda _: None).install(cfg, plan)


def uninstall(cfg, ids, **kw):
    from rigsmith.plan import toposort

    order = list(reversed(toposort(cfg.library, ids, P)))
    return Runner(P, say=lambda _: None).uninstall(cfg, order, **kw)


def test_install_is_idempotent_and_uninstall_restores_zshrc(cfg, home):
    zshrc().write_text("# my stuff\nexport FOO=1\n")
    before = zshrc().read_bytes()
    plan, res = install(cfg, profile="minimal")
    assert plan.order == ["alpha", "beta", "p1"]  # p2 dropped: same role, first wins
    assert res.changes and not res.failed
    assert zshrc().read_text().startswith(BLOCK)
    assert (home / ".config/rigsmith/shell.d/50-alpha.zsh").is_file()
    assert INSTALLED == {"alpha", "beta", "p1"}
    assert status(cfg.library["alpha"], P) == "installed"

    _, again = install(cfg, profile="minimal")
    assert again.changes == 0

    res = uninstall(cfg, ["alpha", "beta", "p1"])
    assert not res.failed
    assert INSTALLED == set()
    assert zshrc().read_bytes() == before
    assert not list((home / ".config/rigsmith/shell.d").glob("*"))


def test_zshrc_created_by_rigsmith_is_removed_again(cfg, home):
    install(cfg, ids=["alpha"])
    assert zshrc().is_file()
    uninstall(cfg, ["alpha"])
    assert not zshrc().exists()


def test_preexisting_package_is_noop_and_survives_uninstall(cfg):
    INSTALLED.add("alpha")
    install(cfg, ids=["alpha"])
    uninstall(cfg, ["alpha"])
    assert "alpha" in INSTALLED  # rigsmith didn't install it, so it doesn't remove it
    install(cfg, ids=["alpha"])
    uninstall_res = uninstall(cfg, ["alpha"], include_unmanaged=True)
    assert uninstall_res.changes and "alpha" not in INSTALLED


def test_modified_key_is_restored_and_user_changes_are_kept(cfg):
    path = vscode_settings_path(P)
    path.parent.mkdir(parents=True)
    path.write_text('{\n  // comment\n  "editor.fontSize": 14,\n}\n')
    install(cfg, ids=["editor"])
    data = json.loads(path.read_text())
    assert data == {"editor.fontSize": 16, "new.key": True}
    uninstall(cfg, ["editor"])
    assert json.loads(path.read_text()) == {"editor.fontSize": 14}

    install(cfg, ids=["editor"])
    data = json.loads(path.read_text())
    data["editor.fontSize"] = 20  # the user changes it after install
    path.write_text(json.dumps(data))
    res = uninstall(cfg, ["editor"])
    assert json.loads(path.read_text()) == {"editor.fontSize": 20}
    assert any("changed since install" in w for w in res.warnings)


def test_user_edited_snippet_is_kept_on_reinstall_and_uninstall(cfg, home):
    install(cfg, ids=["alpha"])
    snip = home / ".config/rigsmith/shell.d/50-alpha.zsh"
    snip.write_text("# mine now\n")
    _, res = install(cfg, ids=["alpha"])
    assert snip.read_text() == "# mine now\n" and res.changes == 0
    res = uninstall(cfg, ["alpha"])
    assert snip.read_text() == "# mine now\n"
    assert any("changed since install" in w for w in res.warnings)


def test_irreversible_post_install_runs_once(cfg):
    install(cfg, ids=["hooked"])
    install(cfg, ids=["hooked"])
    assert RAN == ["hooked"]
    res = uninstall(cfg, ["hooked"])
    assert any("can't be undone" in w for w in res.warnings)


def test_failure_skips_dependents_and_retry_resumes(cfg):
    FAIL.add("alpha")
    _, res = install(cfg, ids=["beta"])
    assert "alpha" in res.failed and "beta" in res.skipped
    FAIL.clear()
    _, res = install(cfg, ids=["beta"])
    assert res.ok == ["alpha", "beta"]


def test_role_keeps_installed_provider_and_honors_answers(cfg):
    plan = build(cfg, P, profile="minimal", answers={"prompt": "p2"})
    assert "p2" in plan.order and "p1" not in plan.order
    INSTALLED.add("p1")
    plan = build(cfg, P, profile="minimal", answers={"prompt": "p2"})
    assert "p1" in plan.order and "p2" not in plan.order
    assert any("keeping installed p1" in w for w in plan.warnings)


def test_dependencies_come_from_the_library_and_profile_defaults(cfg):
    plan = build(cfg, P, ids=["beta"])
    assert plan.order == ["alpha", "beta"] and plan.reasons["alpha"] == "dependency of beta"
    assert "gamma" not in build(cfg, P).order  # default profile = first (minimal)
    assert "gamma" in build(cfg, P, profile="standard").order


def test_uninstall_takes_orphaned_dependencies_but_not_requested_ones(cfg):
    from rigsmith.plan import with_orphans
    from rigsmith.state import State

    plan, _ = install(cfg, ids=["beta"])  # alpha comes along as a dependency
    st = State()
    assert st.requested == {"beta"}
    managed = [i for i in cfg.library if st.managed(i)]
    assert with_orphans(cfg.library, ["beta"], managed, st.requested, P) == ["beta", "alpha"]
    uninstall(cfg, ["beta", "alpha"])
    assert INSTALLED == set()

    install(cfg, ids=["alpha"])  # now alpha is asked for explicitly…
    install(cfg, ids=["beta"])
    st = State()
    managed = [i for i in cfg.library if st.managed(i)]
    assert with_orphans(cfg.library, ["beta"], managed, st.requested, P) == ["beta"]  # …so it stays


def test_package_pulled_in_by_an_earlier_step_is_owned_not_preexisting(cfg):
    class PullsBeta(Fake):
        def install(self):
            super().install()
            INSTALLED.add("beta")  # side effect, like an extension pack installing its members

    cfg.library["alpha"].sources = [PullsBeta("alpha")]
    cfg.library["beta"].requires = []
    install(cfg, ids=["alpha", "beta"])
    from rigsmith.state import State

    assert State().get("pkg:beta").op == "created"
    uninstall(cfg, ["alpha", "beta"])
    assert INSTALLED == set()


def test_git_identities_really_switch_by_folder(home):
    import subprocess

    from rigsmith.model import ARTIFACTS
    from rigsmith.plan import Plan

    c = config.parse(
        config.yaml().load("profiles: [minimal]\nsections:\n  git:\n    core: {git-identities: minimal}\n")
    )
    answers = {"work-dir": "~/w/", "work-email": "me@work.io"}
    plan = Plan(order=["git-identities"], reasons={"git-identities": "selected"}, answers=answers, env={})
    res = Runner(P, say=lambda _: None).install(c, plan)  # deps left out on purpose: never install real packages
    assert not res.failed, res.failed
    assert status(ARTIFACTS["git-identities"], P, answers) == "installed"

    def email(where):
        where.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q"], cwd=where, check=True)
        out = subprocess.run(["git", "config", "user.email"], cwd=where, capture_output=True, text=True)
        return out.stdout.strip()

    assert email(home / "w/project") == "me@work.io"
    assert email(home / "personal/project") == ""  # outside the work folder: the global identity (none here)

    Runner(P, say=lambda _: None).uninstall(c, ["git-identities"])
    assert not (home / ".gitconfig-work").exists()  # rigsmith created it, and nothing else is in it
    assert "includeIf" not in (home / ".gitconfig").read_text()


def test_git_identities_without_email_only_sets_the_folder_rule(home):
    from rigsmith.model import ARTIFACTS
    from rigsmith.runner import effects_for

    effs = effects_for(ARTIFACTS["git-identities"], P, {"work-dir": "~/w/", "work-email": ""})
    assert [e.label for e in effs] == ["git config --global includeIf.gitdir:~/w/.path"]


def test_orphans_behind_a_preexisting_dependency_are_removed_too(cfg):
    from rigsmith.plan import with_orphans
    from rigsmith.state import State

    # hooked → beta (already on the machine, so not managed) → alpha (pulled in, managed)
    cfg.library["hooked"].requires = ["beta"]
    INSTALLED.add("beta")
    install(cfg, ids=["hooked"])
    st = State()
    managed = [i for i in cfg.library if st.managed(i)]
    assert "beta" not in managed and "alpha" in managed
    assert with_orphans(cfg.library, ["hooked"], managed, st.requested, P) == ["hooked", "alpha"]
