import pytest


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    """Every test gets an empty HOME so nothing touches the real machine."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    return tmp_path
