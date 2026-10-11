---
category: software-development
name: free-claude-code
description: "Use when configuring the FCC free-model coding router."
version: 1.0.0
author: Gio
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [fcc, free-models, router, openrouter, nvidia-nim, coding-agents, hermes-integration]
    related_skills: [free-ai-coding-cli, hermes-agent, claude-code, pi-coding]
---

# Free Claude Code (FCC) — router local de modelos gratis para coding agents

FCC (github.com/Alishahryar1/free-claude-code, MIT) es un proxy local que da a los coding
agents (Claude Code, Codex, Pi, OpenCode, Cline, **Hermes**, DeepSeek Harness, Grok Build)
acceso a 48 providers ToS-friendly (~1.3B+ tokens gratis/mes) con **fallback automático**
entre modelos cuando uno falla (429/quota/outage). Corresponde al mismo truco que
`free-ai-coding-cli` (OpenRouter como backend Anthropic) pero como producto completo.

## When to Use
- User wants free/cheap models for coding agents (Hermes, Pi, DSH, Claude Code, Codex, OpenCode).
- Existing setup hits provider 429s / rate limits and needs automatic fallback.
- User asks to install or integrate "free-claude-code", "FCC", "free coding router".

## Instalación (Windows)
1. Descargar `scripts/install.ps1` del repo main y REVISAR antes de ejecutar.
2. **Modo no-interactivo**: si el stdin está redirigido, el instalador NO pregunta y usa los
   defaults del script (líneas ~38-45: `$script:InstallClaudeCode`, `InstallCodex`, `InstallPi`,
   `InstallOpenCode`, `InstallCline`, `InstallHermes`, `InstallDsh`, `InstallGrok`). Para elegir
   agentes, editar esos flags en la copia local ANTES de correr:
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File install.ps1 < /dev/null`
3. Instala: uv, Python aislado, launchers `fcc-*` en `~/.local/bin`, atajo de escritorio,
   carpeta `~/.fcc/`. Detecta agentes ya instalados (no duplica).
4. Verificar: `fcc-server --version` → `free-claude-code X.Y.Z`.

## Arranque
- `fcc-server` (daemon, mantener en background) → Admin UI en `http://127.0.0.1:8082/admin`
  (local-only). Log: `~/.fcc/logs/server.log`.
- Launchers: `fcc-hermes`, `fcc-pi`, `fcc-dsh`, `fcc-claude`, `fcc-codex`, `fcc-opencode`,
  `fcc-cline`, `fcc-grok`, `fcc-desktop`.

## Configurar providers y modelo (API, sin GUI)
- Ver campos: `GET http://127.0.0.1:8082/admin/api/config` (JSON con `fields[]`; el modelo es `MODEL`).
- Aplicar: `POST /admin/api/config/apply` con `{"MODEL": "open_router/openrouter/free"}` →
  `{"applied":true,"valid":true}`.
- Persistencia real: el valor también va al `.env` de `~/.fcc/.env` (formato `KEY=value`).
  Si el apply no lo persiste, escribir `MODEL=...` manualmente en ese `.env` y **reiniciar fcc-server**.
- Keys: copiar de la config existente, p. ej. `OPENROUTER_API_KEY` desde `$LOCALAPPDATA/hermes/.env`
  → `~/.fcc/.env` (no exponer valores en logs/respuestas).
- Descubrimiento de modelos: `GET /admin/api/models` (OpenRouter suele listar ~348).

## Probar integración con Hermes
```bash
fcc-hermes chat -q "hola" -m "open_router/openrouter/free" -Q   # -m sobreescribe el modelo FCC
```
- Sin `-m`: usa el `MODEL` configurado en FCC (¡el launcher hereda el modelo del proxy!).
- Override de modelo para FCC vía flag de Hermes: `fcc-hermes chat -q "..." -m "open_router/deepseek/deepseek-v4-flash"`.

## Pitfalls
- **MODEL por defecto = `nvidia_nim/nvidia/nemotron-3-super-120b-a12b`** → sin `NVIDIA_NIM_API_KEY`
  da HTTP 503 en cada request ("NVIDIA_NIM_API_KEY is not set"). Arreglo: setear
  `MODEL=open_router/openrouter/free` (o `open_router/<modelo específico>`) en el `.env` + reiniciar.
- **El fallo aparece como 503 "API call failed after 3 retries"** en la salida de Hermes — no es
  fallo de Hermes, es el proxy FCC rechazando el modelo sin key.
- **El launcher NO cachea tu config de Hermes**: `fcc-hermes` arranca Hermes con env del proxy;
  usar `/model` dentro de Hermes para volver a tu provider normal deja la ruta FCC.
- **No es destructivo**: convive con tu Hermes/pi/dsh existentes; uninstall = `scripts/uninstall.ps1` (quita `~/.fcc/` y launchers, conserva agentes).
- **Instalar con input redirigido evita los prompts interactivos** (`Read-YesNo`) — sin flags CLI
  para elegir agentes; hay que editar los defaults del script.

## Verificación
1. `fcc-server --version` OK.
2. `curl http://127.0.0.1:8082/health` → 200.
3. `fcc-hermes chat -q "Responde solo: OK" -Q` → responde "OK" (con `-m open_router/openrouter/free`).
4. Sin `-m` tras configurar `MODEL` en `.env` → también responde (valida la persistencia).

## Relación con otras skills
- `free-ai-coding-cli` = versión mínima (solo OpenRouter→Claude Code). FCC la supera para uso
  continuo (48 providers, fallback, launchers). Ver `references/fcc-hermes-session-2026-08-20.md`
  para el transcript de la integración real.
