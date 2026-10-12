"""One precedence for answers: explicit → config → remembered; empty means the default; the profile isn't kept."""

import pytest

from rigsmith import config, library  # noqa: F401  (registers built-in artifacts)
from rigsmith.answers import remember, resolve
from rigsmith.model import Platform
from rigsmith.plan import build
from rigsmith.state import State

P = Platform.detect()
MENU = "profiles: [minimal]\nsections:\n  git:\n    core: {git-identities: minimal}\n"

RESOLVE = [
    # (case, remembered, config answers, explicit, expected)
    ("remembered", {"theme": "nord"}, {}, None, {"theme": "nord"}),
    ("config beats remembered", {"theme": "nord"}, {"theme": "dracula"}, None, {"theme": "dracula"}),
    ("explicit beats config", {}, {"theme": "dracula"}, {"theme": "catppuccin"}, {"theme": "catppuccin"}),
    ("an explicit blank still wins", {"work-email": "old@x.io"}, {}, {"work-email": ""}, {"work-email": ""}),
    ("remembered roles count", {"prompt": "starship"}, {}, None, {"prompt": "starship"}),
    ("the profile is never remembered", {"profile": "comprehensive"}, {}, None, {}),
]


@pytest.mark.parametrize("case, remembered, pinned, explicit, expected", RESOLVE, ids=[r[0] for r in RESOLVE])
def test_resolve(case, remembered, pinned, explicit, expected):
    cfg = config.parse(config.yaml().load(MENU))
    cfg.answers = pinned
    assert resolve(cfg, remembered, explicit) == expected


def test_remember_keeps_everything_but_the_profile():
    st = State()
    remember(st, {"profile": "standard", "prompt": "starship", "icons": "yes"})
    assert st.answers == {"prompt": "starship", "icons": "yes"}


def test_a_cleared_answer_sticks_and_empty_means_the_default():
    cfg = config.parse(config.yaml().load(MENU))
    old = {"work-dir": "~/jobs/", "work-email": "old@jobs.io"}
    plan = build(cfg, P, answers={"work-email": "", "work-dir": ""}, remembered=old)
    assert plan.answers["work-email"] == ""  # cleared in the questionnaire: last run's email doesn't come back
    assert plan.answers["work-dir"] == "~/work/"  # empty means the default, never "/" (every repo would be work)
