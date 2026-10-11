#!/usr/bin/env bash
# End-to-end on a REAL machine (CI only): install → verify → idempotent reinstall → uninstall → verify.
set -euo pipefail
cd "$(dirname "$0")/../.."
read -ra ARGS <<< "${E2E_ARGS:--p minimal -s system -s shell -s cli -s git}"
rs() { uv run rigsmith "$@"; }
dump_logs() {
  echo "::group::rigsmith command log"
  grep -hE '^(\$ |\[exit)' ~/.local/state/rigsmith/logs/* || true
  echo "::endgroup::"
}
trap dump_logs ERR

if [[ -f ~/.zshrc ]]; then cp ~/.zshrc /tmp/zshrc.before; else command rm -f /tmp/zshrc.before; fi
git config --global init.defaultBranch trunk  # a pre-existing value rigsmith must restore

echo "::group::install"
rs install "${ARGS[@]}" -y
echo "::endgroup::"
uv run python tests/e2e/check.py installed "${ARGS[@]}"
test "$(git config --global init.defaultBranch)" = main

echo "::group::second install must change nothing"
rs install "${ARGS[@]}" -y | tee /tmp/second.log
grep -q "Installed: 0 changes" /tmp/second.log
echo "::endgroup::"

echo "::group::a login shell loads every snippet"
zsh -i -c 'echo "zsh ok: $ZSH_VERSION"' </dev/null
echo "::endgroup::"

echo "::group::uninstall"
rs uninstall "${ARGS[@]}" -y
echo "::endgroup::"
uv run python tests/e2e/check.py uninstalled "${ARGS[@]}"
test "$(git config --global init.defaultBranch)" = trunk  # modified key restored
if [[ -f /tmp/zshrc.before ]]; then cmp ~/.zshrc /tmp/zshrc.before; else test ! -e ~/.zshrc; fi
echo "e2e ok"
