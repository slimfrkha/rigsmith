"""Python with the Astral stack: uv, ruff, ty, and the VS Code side of it."""

from rigsmith.library._util import ext, snippet, tool
from rigsmith.model import VSCodeSetting

tool("uv", "Astral's uv: Python versions, venvs, dependencies and tools, extremely fast. `uv init`, `uv run`.")
tool("python", "Python 3 from Homebrew (uv can also manage Python versions per project).", bin="python3")
tool("ruff", "Astral's ruff: linter + formatter replacing flake8, isort and black. `ruff check`, `ruff format`.")
tool("ty", "Astral's ty: a very fast Python type checker and language server. `ty check`.")
snippet(
    "python-aliases",
    "Shortcuts: py, uvr (uv run), uvs (sync), uva/uvad (add/dev), venv, activate.",
    70,
    requires=["uv"],
)

ext("debugpy-ext", "ms-python.debugpy", "VS Code Python debugger.")
ext(  # the Python extension pulls in debugpy: install it first so rigsmith owns it
    "python-ext",
    "ms-python.python",
    "VS Code Python support: run, test explorer, environments.",
    requires=["vscode", "debugpy-ext"],
)
ext(
    "ruff-ext",
    "charliermarsh.ruff",
    "Ruff in VS Code: lint as you type, format and organize imports on save.",
    settings=[
        VSCodeSetting("ruff.enable", True),
        VSCodeSetting("ruff.lint.enable", True),
        VSCodeSetting(
            "[python]",
            {
                "editor.defaultFormatter": "charliermarsh.ruff",
                "editor.formatOnSave": True,
                "editor.tabSize": 4,
                "editor.rulers": [88],
                "editor.codeActionsOnSave": {"source.fixAll": "explicit", "source.organizeImports": "explicit"},
            },
        ),
    ],
)
ext(
    "ty-ext",
    "astral-sh.ty",
    "ty in VS Code: type checking and completions. Turns off Pylance's language server.",
    settings=[VSCodeSetting("python.languageServer", "None")],
)
ext(
    "jupyter-ext",
    "ms-toolsai.jupyter",
    "Jupyter notebooks in VS Code, formatted and import-sorted on save.",
    settings=[
        VSCodeSetting("notebook.formatOnSave.enabled", True),
        VSCodeSetting(
            "notebook.codeActionsOnSave",
            {"notebook.source.fixAll": "explicit", "notebook.source.organizeImports": "explicit"},
        ),
    ],
)
ext("autodocstring-ext", "njpwerner.autodocstring", "Generate docstring skeletons from signatures.")
ext("python-indent-ext", "KevinRose.vsc-python-indent", "Correct Python indentation on Enter.")
