"""Interactive screens (questionnaire, picker, confirm)."""

from rigsmith.config import ConfigError


def interactive_install(*args, **kwargs):
    raise ConfigError("interactive mode is not available yet; use -y or --dry-run")


def pick_uninstall(*args, **kwargs):
    raise ConfigError("interactive mode is not available yet; use -y or --dry-run")
