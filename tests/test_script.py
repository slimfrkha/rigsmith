"""`--script`: the generated sh does what rigsmith would do, is safe to rerun, and its uninstall twin undoes it."""

import subprocess

import pytest

from rigsmith import config, library  # noqa: F401  (registers built-in artifacts)
from rigsmith.backends import Apt, Brew, Cask, GitClone, Krew, NerdFont, Release, Script, UvTool, VSCodeExt
from rigsmith.model import ARTIFACTS, Platform
from rigsmith.plan import Plan, build
from rigsmith.runner import Runner, status
from rigsmith.script import WARNING, install_script, uninstall_script
from rigsmith.shell import BLOCK, zshrc

P = Platform.detect()
MENU = """
profiles: [minimal]
sections:
  shell:
    helpers: {shell-aliases: minimal}
  git:
    core: {git-defaults: minimal}
"""


def run_sh(script: str, home) -> None:
    path = home / "out.sh"
    path.write_text(script)
    subprocess.run(["sh", str(path)], check=True, env={"HOME": str(home), "PATH": "/usr/bin:/bin:/opt/homebrew/bin"})


def plan_for(cfg, ids):
    # deps left out on purpose: the test must never generate package installs for the real machine
    return Plan(order=ids, reasons={i: "selected" for i in ids}, answers={}, env={})


def test_install_script_does_what_rigsmith_would_and_reruns_cleanly(home):
    cfg = config.parse(config.yaml().load(MENU))
    zshrc().write_text("# mine\n")
    script = install_script(cfg, plan_for(cfg, ["shell-aliases", "git-defaults"]), P, "rigsmith install")
    assert WARNING.splitlines()[1] in script and "Equivalent to: rigsmith install" in script
    run_sh(script, home)
    assert status(ARTIFACTS["shell-aliases"], P) == "installed"
    assert status(ARTIFACTS["git-defaults"], P) == "installed"
    assert zshrc().read_text() == BLOCK + "# mine\n"
    snapshot = {f: f.read_bytes() for f in home.rglob("*") if f.is_file() and f.name != "out.sh"}
    run_sh(script, home)  # a second run changes nothing
    assert snapshot == {f: f.read_bytes() for f in home.rglob("*") if f.is_file() and f.name != "out.sh"}


def test_uninstall_script_replays_receipts_backwards(home):
    cfg = config.parse(config.yaml().load(MENU))
    zshrc().write_text("# mine\n")
    subprocess.run(["git", "config", "--global", "pull.rebase", "false"], check=True)  # a value to restore
    Runner(P, say=lambda _: None).install(cfg, plan_for(cfg, ["shell-aliases", "git-defaults"]))
    script = uninstall_script(cfg, ["git-defaults", "shell-aliases"], P, False, "rigsmith uninstall")
    run_sh(script, home)
    assert zshrc().read_text() == "# mine\n"
    assert not list((home / ".config/rigsmith/shell.d").glob("*.zsh"))
    got = subprocess.run(["git", "config", "--global", "pull.rebase"], capture_output=True, text=True).stdout
    assert got.strip() == "false"  # modified → restored to what it was
    unset = subprocess.run(["git", "config", "--global", "rerere.enabled"], capture_output=True)
    assert unset.returncode == 1  # created → removed


def test_vscode_settings_are_comments_only(home):
    cfg = config.load("reference")
    plan = build(cfg, P, ids=["errorlens"])
    plan.order = ["errorlens"]  # just the extension's own effects
    script = install_script(cfg, plan, P, "rigsmith install errorlens")
    assert '# VS Code "$HOME' in script and '"errorLens.enabledDiagnosticLevels"' in script


@pytest.mark.parametrize(
    "backend, install, uninstall",
    [
        (Brew("eza"), "brew install eza", "brew uninstall eza"),
        (Cask("iterm2"), "brew install --cask iterm2", "brew uninstall --cask iterm2"),
        (Apt("zsh git"), "apt-get install -y -q zsh git", "apt-get remove -y -q zsh git"),
        (Krew("neat"), "command kubectl krew install neat", "command kubectl krew uninstall neat"),
        (VSCodeExt("a.b"), "code --install-extension a.b --force", "code --uninstall-extension a.b"),
        (UvTool("huggingface_hub[cli]"), "uv tool install 'huggingface_hub[cli]'", "uv tool uninstall huggingface_hub"),
        (GitClone("https://x/y.git", dest="~/y"), 'git clone --depth=1 https://x/y.git "$HOME/y"', 'rm -rf "$HOME/y"'),
        (Script("s", install_cmd="echo hi", check_cmd="true", remove_cmd="echo bye"), "echo hi", "echo bye"),
        (Release("tool", url="https://x/tool_{os}_{arch}.zip"), 'chmod +x "$HOME/.local/bin/tool"', "rm -f"),
        (NerdFont("Meslo"), "unzip -o -q -j", "rm -rf"),
    ],
)
def test_every_backend_has_a_shell_form(backend, install, uninstall):
    assert any(install in line for line in backend.install_sh())
    assert any(uninstall in line for line in backend.uninstall_sh())
    assert backend.check_sh() != "false"
