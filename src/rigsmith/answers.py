"""Answers: profile, role picks and question answers, under one precedence wherever they're read.

explicit (flags, the questionnaire) → the config's `answers:` → remembered from earlier runs. The first source that has
a key wins, even with an empty value; an empty question answer then means the question's default. The profile is
never remembered: it scopes one run.
"""

from rigsmith.config import Config
from rigsmith.model import QUESTIONS
from rigsmith.state import State


def resolve(cfg: Config, remembered: dict[str, str], explicit: dict[str, str] | None = None) -> dict[str, str]:
    return {**{k: v for k, v in remembered.items() if k != "profile"}, **cfg.answers, **(explicit or {})}


def remember(state: State, answers: dict[str, str]) -> None:
    """Keep this run's answers as the next run's defaults."""
    state.answers.update({k: v for k, v in answers.items() if k != "profile"})


def prefs_env(answers: dict[str, str]) -> dict[str, str]:
    """Environment for every remembered question answer, not just this run's: installing one artifact must not
    drop the preferences other installed snippets read (icons, theme)."""
    env: dict[str, str] = {}
    for qid, answer in answers.items():
        if qid in QUESTIONS:
            env.update(QUESTIONS[qid].env(answer))
    return env
