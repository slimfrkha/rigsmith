#!/bin/sh
# Bootstrap rigsmith on a fresh machine: installs uv if missing, then runs rigsmith with your arguments.
#
#   curl -fsSL https://raw.githubusercontent.com/slimfrkha/rigsmith/main/install.sh | sh -s -- install
#
# Pin for automation: fetch this script from a release tag and set RIGSMITH_VERSION=X.Y.Z.
# RIGSMITH_FROM overrides the package source (e.g. git+https://github.com/slimfrkha/rigsmith).
set -eu

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  PATH="$HOME/.local/bin:$PATH"
fi

spec="rigsmith${RIGSMITH_VERSION:+==$RIGSMITH_VERSION}"
set -- --from "${RIGSMITH_FROM:-$spec}" rigsmith "$@"

# Piped through `curl | sh`, stdin is the script: reattach the terminal for the interactive screens.
if (exec </dev/tty) 2>/dev/null; then
  exec uv tool run "$@" </dev/tty
fi
exec uv tool run "$@"
