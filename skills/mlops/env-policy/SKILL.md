---
name: env-policy
description: "Entornos Python: venv GPU/CPU, abrir-ejecutar-cerrar."
version: 1.0.0
author: Hermes Agent (decisión de Gio 2026-08-31)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [entornos, venv, gpu, cpu, lifecycle, recursos, ram, env_manager]
    related_skills: [vram-watchdog, granite-asr, local-llm-picker]
---

# Política de Entornos Python (GPU/CPU + ciclo de vida)

> Decisión de Gio (2026-08-31): NO usar siempre el python global CPU para todo. Clasificar
> por tipo de trabajo, y **abrir→ejecutar→cerrar** para no dejar procesos robando RAM.

## When to Use
- Antes de EJECUTAR cualquier script/trabajo Python, decidir QUÉ entorno usar (no el global por defecto).
- Cuando un trabajo termina, CERRAR el proceso si es one-shot (no dejarlo vivo).

## REGLA DE ORO (liderazgo — qué usar cuándo)

| Tipo de trabajo | Entorno | Ejemplo |
|---|---|---|
| **Modelos ML** (torch, cuda) | Venv **GPU** | chatterbox (TTS), granite-asr (ASR), local_ai_ocr |
| **Utilidades ligeras** (sin torch) | Venv **CPU** o global | parse, scrape, scripts de análisis |
| **Infraestructura Hermes** | NO tocar NUNCA | gateway, serve, headroom, MCP servers |
| **Modelos locales (llama.cpp)** | Ya lo gestiona `vram-watchdog` | ornith/ablit (se desmontan por inactividad) |

## GESTOR (scripts/env_manager.py) — el que decide por ti

```bash
EM="python $LOCALAPPDATA/hermes/scripts/env_manager.py"
"$EM" list                    # venvs + GPU/CPU + torch (auditoría)
"$EM" ps                      # procesos python + clase (INFRA|LLM|one-shot)
"$EM" run <script.py> [--venv X]   # ejecuta one-shot en venv CORRECTO y cierra al terminar
"$EM" clean [--kill]          # cierra one-shots ML huérfanos (dry-run por defecto)
```

### `run` (el más usado) — eliges sin pensar
`env_manager run script.py` → detecta un venv GPU (si hay torch) y ejecuta ahí, one-shot.
Para forzar: `env_manager run --venv granite-asr script.py`.

### `clean` — SIEMPRE dry-run (seguro)
Por defecto SOLO LISTA lo que mataría. Requiere `--kill` para ejecutar. **Nunca toca infra**
(Hermes, MCP servers, llm-servers) — verificado con parser CSV robusto.

## CICLO DE VIDA (abrir→ejecutar→cerrar)
1. **Abrir**: `env_manager run` levanta el venv correcto (GPU para modelos, CPU para util).
2. **Ejecutar**: corre el script.
3. **Cerrar**: al terminar, el proceso muere (one-shot). Si queda huérfano → `env_manager clean --kill`.
4. **Servicios** (llama.cpp, ComfyUI): los gestiona `vram-watchdog` (desmonta por inactividad).

## Infraestructura que NUNCA se cierra (protegida en `_is_infra`)
- `hermes_cli.main` (gateway/serve), `gateway.proxy` (idamcp), `headroom` proxy.
- MCP servers: `mcp-servers/`, `stealth-browser-mcp`, `agent_reach`, `scrapling`, `obscura`,
  `gbrain`, `browserbase`, `trader_dev`, `AI-Video-Transcriber`.
- `llama-server` / `ollama` (machine: los maneja vram-watchdog).

## Auditoría (líder) — cuándo y por qué
- **`list`** antes de hacer trabajo: saber qué entornos hay y su capacidad.
- **`ps`** para ver qué consume RAM: si un one-shot ML quedó vivo, cerrarlo.
- **`clean`** (dry-run) como chequeo periódico — si la RAM crece sin motivo.

## Pitfalls (aprendidos 2026-08-31)
- **PowerShell `Format-List` TRUNCA el CommandLine** → usar `ConvertTo-Csv` (o `_is_infra` no
  detecta infra y `clean` podría matar a Hermes). SIEMPRE CSV.
- **Codepage Windows** → `encoding="latin-1"` en subprocess (no utf-8), sino UnicodeDecodeError.
- **`uv venv` no trae pip** → instalar con `uv pip install --python <venv>/Scripts/python.exe`.
- **`uv pip install torch` = CPU por defecto** → usar `--index-url https://download.pytorch.org/whl/cu126` + `--reinstall`.
- **torchaudio nuevo requiere torchcodec/FFmpeg** → para ASR usar `librosa.load(sr=16000)` en vez de torchaudio.load.

## Verificación
- [ ] `list` muestra venvs con GPU/CPU reales
- [ ] `ps` clasifica infra (Hermes/MCP) correctamente
- [ ] `clean` dry-run NO lista infra
- [ ] `run` ejecuta en venv correcto y cierra al terminar
- [ ] Procesos one-shot no quedan vivos tras `run`
