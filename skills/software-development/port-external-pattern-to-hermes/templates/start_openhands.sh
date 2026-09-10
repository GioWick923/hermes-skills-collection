#!/usr/bin/env bash
# Arranca OpenHands (self-hosted) en Docker usando la clave OpenRouter de Hermes.
# Reusable wrapper for port-external-pattern-to-hermes Option B.
# Uso: bash start_openhands.sh
# Prerreq: Docker Desktop instalado y arrancado; OPENROUTER_API_KEY en %LOCALAPPDATA%/hermes/.env
set -e

ENV_FILE="$LOCALAPPDATA/hermes/.env"
if [ -f "$ENV_FILE" ]; then
  OPENROUTER_API_KEY=*** "$ENV_FILE" | grep -E '^OPENROUTER_API_KEY=*** | head -1 | sed 's/^OPENROUTER_API_KEY=*** | sed 's/^"//;s/"$//'
fi

if [ -z "$OPENROUTER_API_KEY" ]; then
  echo "ERROR: no se encontro OPENROUTER_API_KEY en $ENV_FILE" >&2
  exit 1
fi

export LLM_MODEL="${LLM_MODEL:-openrouter/tencent/hy3:free}"
LLM_BASE_URL="${LLM_BASE_URL:-https://openrouter.ai/api/v1}"
IMAGE="docker.all-hands.dev/all-hands-ai/openhands:latest"
WORKSPACE="$HOME/openhands-workspace"

mkdir -p "$WORKSPACE"

echo "Arrancando OpenHands: LLM_MODEL=$LLM_MODEL WORKSPACE=$WORKSPACE"
echo "LLM_BASE_URL=$LLM_BASE_URL  (API key desde .env de Hermes, nunca se imprime)"

docker run -it --rm --pull always \
  -e SANDBOX_RUNTIME_CONTAINER_IMAGE="docker.all-hands.dev/all-hands-ai/runtime:latest" \
  -e LOG_ALL_EVENTS=true \
  -e LLM_MODEL="$LLM_MODEL" \
  -e LLM_API_KEY=*** \
  -e LLM_BASE_URL="$LLM_BASE_URL" \
  -v "$WORKSPACE:/workspace" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 3000:3000 \
  "$IMAGE"
