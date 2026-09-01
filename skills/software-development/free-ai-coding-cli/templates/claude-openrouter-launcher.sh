#!/usr/bin/env bash
# Launcher: Claude Code -> OpenRouter (modelo gratuito por defecto)
# Uso: OR_KEY=sk-or-... ./claude-openrouter-launcher.sh
# Opcional: ANTHROPIC_MODEL=otro/modelo:free ./claude-openrouter-launcher.sh
# La API key NO se guarda en disco; se inyecta en runtime desde OR_KEY.
set -euo pipefail

if [ -z "${OR_KEY:-}" ]; then
  echo "ERROR: define tu API key asi: OR_KEY=sk-or-... ./claude-openrouter-launcher.sh"
  exit 1
fi

export ANTHROPIC_BASE_URL="https://openrouter.ai/api/anthropic"
export ANTHROPIC_API_KEY="${OR_KEY}"
export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-tencent/hy3:free}"
export HTTP_REFERER="https://localhost/claude-code"
export X_TITLE="claude-code-free"

exec claude "$@"
