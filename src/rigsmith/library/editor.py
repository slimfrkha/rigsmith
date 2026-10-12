"""VS Code: the editor, its settings (opinions, split by topic) and general-purpose extensions."""

from rigsmith.backends import Cask, Script
from rigsmith.library._util import ext
from rigsmith.model import Artifact, Setting, VSCodeSetting

VSCODE_LINUX = Script(
    "code",
    install_cmd='arch=$(dpkg --print-architecture); [ "$arch" = amd64 ] && arch=x64; '
    'curl -fsSL -o /tmp/rigsmith-code.deb "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-$arch" '
    "&& sudo apt-get install -y -q /tmp/rigsmith-code.deb && rm -f /tmp/rigsmith-code.deb",
    check_cmd="command -v code",
    remove_cmd="sudo apt-get remove -y -q code",
    needs_sudo=True,
    os="linux",
)

Artifact(
    id="vscode",
    help="Visual Studio Code, with the `code` command on PATH. GitHub Copilot chat is built in.",
    sources=[Cask("visual-studio-code", os="darwin"), VSCODE_LINUX],
    check="command -v code || test -x '/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code'",
)


def settings(**pairs: object) -> list[Setting]:
    return [VSCodeSetting(k.replace("__", "."), v) for k, v in pairs.items()]


Artifact(
    id="vscode-settings",
    help="Calm, focused editor defaults: no minimap, smooth cursor, sticky scroll, format and trim on save, "
    "autosave on focus change, telemetry off.",
    requires=["vscode"],
    settings=[
        *settings(
            workbench__startupEditor="none",
            editor__fontSize=14,
            editor__fontLigatures=True,
            editor__lineHeight=1.6,
            editor__cursorStyle="line",
            editor__cursorBlinking="smooth",
            editor__cursorSmoothCaretAnimation="on",
            editor__smoothScrolling=True,
            workbench__list__smoothScrolling=True,
            terminal__integrated__smoothScrolling=True,
            editor__minimap__enabled=False,
            editor__wordWrap="on",
            editor__tabSize=2,
            editor__insertSpaces=True,
            editor__formatOnSave=True,
            editor__linkedEditing=True,
            editor__bracketPairColorization__enabled=True,
            editor__guides__bracketPairs=True,
            editor__stickyScroll__enabled=True,
            editor__inlineSuggest__enabled=True,
            files__autoSave="onFocusChange",
            files__trimTrailingWhitespace=True,
            files__insertFinalNewline=True,
            terminal__integrated__fontSize=13,
            terminal__integrated__defaultProfile__osx="zsh",
            git__autofetch=True,
            git__confirmSync=False,
            git__enableSmartCommit=True,
            telemetry__telemetryLevel="off",
        ),
        VSCodeSetting("files.exclude", {"**/__pycache__": True, "**/.git": True, "**/.DS_Store": True}),
        VSCodeSetting("search.exclude", {"**/node_modules": True, "**/dist": True, "**/build": True, "**/.venv": True}),
        VSCodeSetting("[markdown]", {"editor.wordWrap": "on", "editor.formatOnSave": False}),
        VSCodeSetting("[json]", {"editor.tabSize": 2}),
        VSCodeSetting("[jsonc]", {"editor.tabSize": 2}),
    ],
)
Artifact(
    id="vscode-nerd-fonts",
    help="Use the Nerd Fonts in the editor and integrated terminal (JetBrains Mono, MesloLGS for the terminal).",
    requires=["vscode", "jetbrains-nf", "meslo-nf"],
    tags=["icons"],
    settings=settings(
        editor__fontFamily="JetBrainsMono Nerd Font, MesloLGS Nerd Font, Menlo, Monaco, monospace",
        terminal__integrated__fontFamily="MesloLGS Nerd Font",
    ),
)
ext(
    "catppuccin-vscode",
    "Catppuccin.catppuccin-vsc",
    "Catppuccin Mocha color theme for VS Code.",
    settings=[VSCodeSetting("workbench.colorTheme", "Catppuccin Mocha")],
    tags=["theme"],
)
ext(
    "catppuccin-icons",
    "Catppuccin.catppuccin-vsc-icons",
    "Catppuccin file icons for VS Code.",
    settings=[VSCodeSetting("workbench.iconTheme", "catppuccin-mocha")],
    tags=["theme"],
)
ext(
    "errorlens",
    "usernamehw.errorlens",
    "Errors and warnings inline, at the end of the line.",
    settings=[VSCodeSetting("errorLens.enabledDiagnosticLevels", ["error", "warning"])],
)
ext(
    "todo-tree",
    "Gruntfuggly.todo-tree",
    "Every TODO/FIXME/BUG/HACK/NOTE in a tree view.",
    settings=[VSCodeSetting("todo-tree.general.tags", ["TODO", "FIXME", "BUG", "HACK", "NOTE"])],
)
ext("better-comments", "aaron-bond.better-comments", "Color-coded comments: ! alerts, ? questions, TODO.")
ext("path-intellisense", "christian-kohler.path-intellisense", "Autocomplete file paths.")
ext("project-manager", "alefragnani.project-manager", "Save projects and switch between them quickly.")
ext("bookmarks", "alefragnani.Bookmarks", "Bookmark lines and jump between them.")
ext("indent-rainbow", "oderwat.indent-rainbow", "Color each indentation level.")
ext("advanced-new-file", "patbenatar.advanced-new-file", "Create files anywhere with fuzzy folder search.")
ext("fileutils", "sleistner.vscode-fileutils", "Rename, move, duplicate and delete files from the command palette.")
ext("peacock", "johnpapa.vscode-peacock", "Color each workspace's window so you know which repo you're in.")
ext("coverage-gutters", "ryanluker.vscode-coverage-gutters", "Show test coverage in the editor gutter.")
ext("remote-ssh", "ms-vscode-remote.remote-ssh", "Open folders on remote machines over SSH.")
ext("dev-containers", "ms-vscode-remote.remote-containers", "Develop inside containers (devcontainer.json).")
ext("liveshare", "MS-vsliveshare.vsliveshare", "Real-time collaborative editing and debugging.")
ext(
    "yaml-ext",
    "redhat.vscode-yaml",
    "YAML with schemas (Kubernetes, compose, GitHub Actions).",
    settings=[VSCodeSetting("[yaml]", {"editor.defaultFormatter": "redhat.vscode-yaml", "editor.tabSize": 2})],
)
ext("toml-ext", "tamasfe.even-better-toml", "TOML: syntax, validation, formatting (pyproject.toml, Cargo.toml).")
ext("dotenv-ext", "mikestead.dotenv", "Syntax highlighting for .env files.")
