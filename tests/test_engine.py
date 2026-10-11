import pytest

from rigsmith import config, library  # noqa: F401  (registers questions)
from rigsmith.backends import Apt, Brew
from rigsmith.config import ConfigError
from rigsmith.model import Artifact, Platform
from rigsmith.plan import select

MAC = Platform("darwin", "macos", "14.4", "arm64")
NOBLE = Platform("linux", "ubuntu", "24.04", "x86_64")
JAMMY_ARM = Platform("linux", "ubuntu", "22.04", "arm64")


def test_platform_matching():
    assert NOBLE.matches("ubuntu") and NOBLE.matches("ubuntu>=24.04") and not NOBLE.matches("ubuntu<24")
    assert not NOBLE.matches("debian")
    assert MAC.supported and NOBLE.supported and JAMMY_ARM.supported
    assert not Platform("linux", "ubuntu", "20.04", "x86_64").supported
    assert not Platform("linux", "fedora", "40", "x86_64").supported


def test_source_selection_is_deterministic_by_platform():
    art = Artifact(
        id="t",
        help="t",
        sources=[Apt("t-apt", os="linux", arch="arm64"), Brew("t"), Apt("never")],
        register=False,
    )
    assert art.source(JAMMY_ARM).pkg == "t-apt"
    assert art.source(NOBLE).pkg == "t"
    assert art.source(MAC).pkg == "t"
    mac_only = Artifact(id="m", help="m", sources=[Brew("m", os="darwin")], register=False)
    assert mac_only.source(NOBLE) is None and not mac_only.available(NOBLE)
    assert Artifact(id="c", help="c", register=False).available(NOBLE)  # config-only


MENU = """
profiles: [minimal, standard, comprehensive]
sections:
  cli:
    search: {ripgrep: minimal, fd: standard}
    files: {eza: minimal, yazi: comprehensive}
  git:
    core: {git: minimal, gh: standard}
"""


def menu(text=MENU):
    return config.parse(config.yaml().load(text))


def ids(entries):
    return [e.id for e in entries]


def test_select_filters():
    cfg = menu()
    assert ids(select(cfg)) == ["ripgrep", "fd", "eza", "yazi", "git", "gh"]
    assert ids(select(cfg, profile="minimal")) == ["ripgrep", "eza", "git"]
    assert ids(select(cfg, profile="standard", sections=["cli"])) == ["ripgrep", "fd", "eza"]
    assert ids(select(cfg, sections=["cli/files", "git"])) == ["eza", "yazi", "git", "gh"]
    assert ids(select(cfg, ids=["fd", "gh"], sections=["cli"])) == ["fd"]
    with pytest.raises(ConfigError):
        select(cfg, ids=["nope"])
    with pytest.raises(ConfigError):
        select(cfg, sections=["cli/nope"])
    with pytest.raises(ConfigError):
        select(cfg, profile="huge")


def test_validate_reports_problems():
    cfg = menu(
        """
profiles: [minimal]
sections:
  a:
    b: {eza: minimal, nope: minimal, fd: huge}
    empty: {}
questions: {skip: [bogus]}
answers: {profile: huge, icons: maybe, prompt: eza}
"""
    )
    errors = "\n".join(config.validate(cfg))
    for needle in [
        "nope: unknown artifact",
        "unknown profile 'huge'",
        "a/empty is empty",
        "unknown question 'bogus'",
        "answers.profile",
        "answers.icons",
        "answers.prompt",
    ]:
        assert needle in errors


def test_custom_artifacts_are_local_to_the_config():
    cfg = menu(
        """
profiles: [minimal]
sections: {extra: {tools: {btop: minimal}}}
custom:
  - {id: btop, help: Resource monitor, brew: btop, apt: btop}
"""
    )
    assert config.validate(cfg) == []
    art = cfg.library["btop"]
    assert art.bin == "btop" and art.source(MAC).name == "brew"
    from rigsmith.model import ARTIFACTS

    assert "btop" not in ARTIFACTS


def test_resolve_presets_and_user_config(home):
    assert config.resolve(None).name == "reference.yaml"
    user = home / ".config/rigsmith/config.yaml"
    user.parent.mkdir(parents=True)
    user.write_text(MENU)
    assert config.resolve(None) == user
    assert config.resolve("reference").name == "reference.yaml"
    with pytest.raises(ConfigError):
        config.resolve("does-not-exist")


def test_apt_uninstall_keeps_packages_that_existed_before(monkeypatch):
    from rigsmith import backends

    calls = []
    monkeypatch.setattr(backends, "_dpkg", lambda: frozenset({"curl", "git"}))
    monkeypatch.setattr(backends, "run", lambda argv, **kw: calls.append(argv))
    apt = Apt("build-essential curl git")
    snap = apt.snapshot()
    assert snap == ["curl", "git"]
    apt.uninstall(snap)
    assert calls == [["apt-get", "remove", "-y", "-q", "build-essential"]]


def test_fork_keeps_comments_scopes_and_cleans_answers():
    src = menu(
        """
# my team menu
profiles: [minimal, standard, comprehensive]
sections:
  cli:
    search: {ripgrep: minimal, fd: standard}  # search tools
    files: {eza: minimal}
  shell:
    prompt: {p10k: minimal, starship: minimal}
answers: {prompt: p10k, icons: "yes"}
"""
    )
    extra = config.Entry("yazi", "cli", "files", "comprehensive")  # new in the library
    doc = config.fork(src, [*src.entries, extra], ["ripgrep", "starship", "yazi"], {"ripgrep": "standard"})
    out = config.dump(doc)
    assert "# my team menu" in out and "# search tools" in out
    cfg = config.parse(config.yaml().load(out))
    assert [(e.id, e.profile) for e in cfg.entries] == [
        ("ripgrep", "standard"),
        ("yazi", "comprehensive"),
        ("starship", "minimal"),
    ]
    assert cfg.answers == {"icons": "yes"}  # prompt: p10k no longer valid → dropped
    assert config.validate(cfg) == []
