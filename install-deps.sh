#!/usr/bin/env bash
# Bring a machine up to the state this config expects: the herdr binary itself,
# plus the agent integrations herdr uses to detect and resume coding agents.
# Idempotent — safe to re-run, mirrors ~/.config/tmux/install-deps.sh.
set -euo pipefail

INTEGRATIONS=(claude codex)

if command -v herdr >/dev/null 2>&1; then
  # `herdr update` only manages installs made by herdr's own installer;
  # Homebrew/mise/nix copies update through their package manager instead.
  herdr update || echo "herdr update skipped (not an installer-managed copy)"
else
  curl -fsSL https://herdr.dev/install.sh | sh
fi

herdr channel set stable

for name in "${INTEGRATIONS[@]}"; do
  herdr integration install "$name"
done

herdr config check
