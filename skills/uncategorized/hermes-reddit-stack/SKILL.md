---
category: hermes-reddit-stack
name: hermes-reddit-stack
description: "Stack de adopciones de r/HermesAgent: (1) git de config, (2) segundo cerebro en markdown, (3) ingest de YouTube/URL a zettel, (4) dictado->doc y digest matutino por Telegram. Setup idempotente + verificacion."
version: 1.0.0
author: Gio / Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [reddit, productivity, second-brain, telegram, voice-notes, youtube, digest]
    related_skills: [voice-idea-to-doc, note-taking, watch-video]
---

# Hermes Reddit Stack

Paquete de 4 adopciones extraidas de r/HermesAgent, verificadas en Windows.
Autocontenido y reversible. Los scripts viven en `scripts/`; el setup los
coloca en las rutas vivas de Hermes.

## Componentes
1. **Git de config** — repo git en `AppData\Local\hermes` que versiona
   skills/perfiles/memories/cron y EXCLUYE secretos/estado via `.gitignore`.
   Helper `backup-state.sh` respalda secretos+DB en `backups/` (fuera de git).
2. **Segundo cerebro** — `second-brain/` (README indice + `zettel/`). Hechos
   reutilizables van ahi, NO a `memories/MEMORY.md`. Consulta con `search_files`.
3. **Ingest YouTube/URL** — `ingest_url.py` descarga (yt-dlp venv aislado),
   transcribe VTT (reusa `watch-video`), resume y guarda zettel.
4. **Dictado->doc + digest** — `save_doc.py` guarda docs en `docs/`;
   `morning_digest.py` manda resumen diario por Telegram (cron 08:00).

## Setup (idempotente)
```bash
python scripts/setup.py
```
Hace: crea `tools/ingest_venv` + instala yt-dlp (uv), copia `morning_digest.py`
a `~/.hermes/scripts/` para el cron, crea `docs/` y `second-brain/` si faltan.
El cron se crea aparte via el agente (requiere auth):
```python
cronjob(action="create", name="Hermes morning digest",
        schedule="0 8 * * *", script="morning_digest.py",
        prompt="Corre morning_digest.py ...")
```

## Uso diario
- Dictas por Telegram -> "estructura esto: <idea>" -> doc en `docs/`.
- Mandas URL/YouTube -> "ingiere esto: <url>" -> zettel en `second-brain/zettel/`.
- Cada mañana 8 AM -> resumen por Telegram de lo nuevo.

## Referencias
- `references/hermes-cli-mcp.md` — command surface real de `hermes` (chat/send/mcp serve),
  pitfall de subprocess sin returncode, y research de MCP (Hermes SÍ sirve MCP, Pi NO lo consume).

## Pitfalls
- `git add -A` falla con `mmap failed` en MSYS si `tools/` (154M) esta en el tree.
  Usar `git add .` y excluir `tools/` en `.gitignore`.
- Repos git embebidos en skills -> excluir con `**/.git/`.
- `cronjob` script debe estar en `~/.hermes/scripts/` (no ruta absoluta).
- yt-dlp va en venv aislado, NO en el venv de Hermes. Y su carpeta Scripts debe
  ir al frente del PATH antes de llamar a watch-video/download.py (usa `shutil.which`).
- **Comandos CLI reales (NO existe `hermes ask` ni `hermes message`)**:
  - Resumir/preguntar sin interaccion: `hermes chat -q "PROMPT" -Q`
  - Enviar a Telegram: `hermes send -t telegram "MSG"` (requiere home channel:
    `hermes config set TELEGRAM_HOME_CHANNEL <chat_id>`), o `hermes send -t telegram:<chat_id> "MSG"`.
  - Ver targets: `hermes send --list telegram`.
- `subprocess.run` SIN chequear `returncode` reporta exito falso: un comando CLI
  inexistente sale rc!=0 pero no lanza excepcion. SIEMPRE validar `r.returncode==0`
  antes de imprimir "enviado".
- yt-dlp puede avisar "No JS runtime"/"impersonation": los subtitulos igual bajan;
  no es fatal para el pipeline de transcripcion.
- **Hermes como MCP server (real, confirmado en `hermes-agent/mcp_serve.py`)**:
  `hermes mcp serve` arranca un stdio MCP server con 10 tools. Clientes tipo
  Claude Code/Cursor/VS Code lo consumen con
  `{"mcpServers":{"hermes":{"command":"hermes","args":["mcp","serve"]}}}`.
- **Pi (pi.dev) es anti-MCP por diseno**: su README dice literal "No MCP." — no
  puede consumir Hermes como MCP server. Integrar Pi con Hermes requiere puente
  por CLI (`hermes send`/`hermes chat`) o un extension custom, NO MCP.
- Command surface completo + snippets en `references/hermes-cli-mcp.md`.
