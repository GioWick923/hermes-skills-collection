#!/usr/bin/env bash
# Launcher: Claude Code -> proxy local -> OpenRouter (tencent/hy3:free)
# Uso: OR_KEY=sk-or-... ./claude-openrouter.sh [-p "prompt" | interactivo]
set -euo pipefail
if [ -z "${OR_KEY:-}" ]; then
  echo "ERROR: OR_KEY=sk-or-... ./claude-openrouter.sh" >&2
  exit 1
fi
export ANTHROPIC_BASE_URL="http://127.0.0.1:8081"
export ANTHROPIC_API_KEY=*** exec claude "$@"
