---
category: agent
name: agent-tentacles
description: "Map all tools/skills/MCP/CLIs before claiming any missing."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [agent, self-awareness, tools, inventory]
    related_skills: [hermes-self-audit, hermes-migration-restore]
---

# Agent Tentacles — El mapa del pulpo

## When to Use
- Al inicio de cualquier sesión de auditoría/auto-optimización del agente.
- Antes de afirmar que una herramienta falta, no está instalada o "no sé dónde está".
- Tras migración entre PCs (drift de paths/MCP).
- Cuando el usuario pregunte "qué herramientas tienes" / "cuántos CLI".
- Ante CUALQUIER decisión o elección de opciones: guiar al usuario con consejo + RAZONES
  (pros/contras/trade-offs) de por qué una opción es mejor que las alternativas (fact #265).
  No solo decir qué hacer: explicar el porqué de forma concreta, estilo clase, sin rodeos.

## Por qué existe
El agente es un pulpo: cada tentáculo es una herramienta. Antes de decir "no tengo X" o
"no sé dónde está", DEBE escanear este mapa. Toda afirmación de "falta/desconocido" requiere
haber corrido el escaneo de 4 pasos abajo. No se asume ignorancia.

## Al inicio de sesión (recall proactivo — OBLIGATORIO)
Para no repetir el gap de "DeepSeek harness perdido" (2026-08-19), el agente DEBE hacer
recall de su segundo cerebro ANTES de operar:
1. `gbrain` recall/search por "deepseek", "harness", "tentáculos" para traer registros recientes.
2. `gbrain` recall de reglas de comportamiento (#240-249) para no re-cometer errores de canal.
3. Si el backend Docker está caído (fact #240), usar `read_terminal` (shell local) o tools MCP
   directos — NUNCA execute_code para verificar estado de MCP locales (fact #247/#248).

## Regla de oro (comportamiento obligatorio)
> Nunca afirmes que una herramienta falta o que "no sabes dónde está" sin antes ejecutar:
> 1. `skills_list` — ¿existe como skill?
> 2. `tool_search` — ¿es una herramienta diferida (MCP)?
> 3. `gbrain` recall — ¿hay record operativo de ella?
> 4. `hermes config show` + `grep -ril <tool>` en `$LOCALAPPDATA/hermes` — ¿está en host?
> Solo después de los 4, se permite reportar "no encontrado" y pedir contexto al usuario.

Si el backend de terminal/Docker está caído, DILO explícitamente (infra, no ignorancia) y
marca el ítem como "pendiente de verificar al recuperar backend".

## Tentáculos — Herramientas directas (siempre en el runtime)
apply_layout, close_terminal, execute_code, focus_pane, open_preview, process,
project_create, project_list, project_switch, read_preview, read_terminal,
read_window_below, setup_mcp, skill_manage, skill_view, skills_list, tour,
vision_analyze, tool_search, tool_describe, tool_call

## Tentáculos — Herramientas diferidas (MCP, 280+ vía tool_search)
Cargar con `tool_describe` + `tool_call`. Catálogo parcial conocido:
- gbrain (124 tools) — segundo cerebro canónico: remember, recall, search, put_page, sync_brain...
- chrome-devtools (34) — navegador real, screenshots, evaluate, network, lighthouse
- obscura (37) — browser stealth, scrape, screenshots, forms
- playwright (24) — browser automation
- scrapling (14) — scraping anti-bot
- codebase-memory (17) — grafo de código, arquitectura, ADRs
- context7 (6) — docs de librerías
- browserbase (6) — cloud browser
- agent-reach (1) — estado de plataformas
- video-transcriber (5) — transcribir video
- omh (12) — orquestación oh-my-hermes

Para ver el resto: `tool_search(query="...")` o listar todos.

## Tentáculos — Skills (workflows reutilizables)
Catálogos principales (ver `skills_list` para el índice vivo):
- **hermes/**: hermes-agent, hermes-self-audit, hermes-self-optimizing-loop, hermes-model-config,
  hermes-mcp-integration, hermes-migration-restore, hermes-self-evolution, hermes-skill-install-verify,
  hermes-telegram-gateway, hermes-multi-agent, hermes-config-versioning, hermes-reliability, hermes-reddit-stack
- **engineering/**: codebase-design, grill-with-docs, improve-codebase-architecture, resolving-merge-conflicts
- **agent-skills/**: code-review, tdd, spec-driven-development, debugging, performance, security, planning...
- **autonomous-ai-agents/**: autonomy-engine, self-reflect, validate-output, memory-consolidate, merge-reconciler,
  claude-code, codex, opencode, pi-coding, computer-use
- **research/**: arxiv, deep-research-loop, markdown-browser, grounded-citations, blogwatcher, polymarket, llm-wiki
- **productivity/**: docx, pptx, xlsx, pdf, notion, google-workspace, obsidian, officecli
- **creative/**: architecture-diagram, excalidraw, ascii-art, claude-design, p5js, manim-video, comfyui
- **integrations/**: gbrain, chatgpt-web-bridge
- **mlops/**: huggingface-hub, llama-cpp, local-llm-picker, segment-anything, colibri
- **agency/**: orchestrator, architect, senior-developer, reality-checker, ai-engineer
- **ultrawork/**: ulw-loop, ulw-plan, ulw-qa, ulw-research, ulw-work, ulw-perf
- **omh-***: decenas de workflows operativos (ops-review, code-review, plan, product-brief...)

## Tentáculos — Host CLIs (Windows host, vía terminal — VERIFICAR al recuperar backend)
Confirmados en MEMORY (2026-08): hermes, agent-reach, pi-run.sh, gws, ntn, blogwatcher-cli,
himalaya, openhue, uv, pipx, npm, git, docker.
⚠️ Pendiente de verificación live (Docker caído al crear este skill): rutas exactas y
disponibilidad de cada uno.

## Tentáculos — MCP servers (estado conocido 2026-08-16: 7/9 caídos post-migración)
scrapling, agent-reach, lightpanda, chrome-devtools, playwright, obscura, gbrain reportados
caídos (rutas a usuario viejo / bins faltantes). Capacidad de tools severamente reducida hasta reparar.
Ver `hermes-migration-restore` para el fix de las 4 clases de drift.

## Gap crítico registrado por el usuario (2026-08-19)
- El usuario reportó haber instalado un "DeepSeek harness" recientemente. NO hay record en gbrain/MEMORY.
- `deepseek-v4-flash-0731` devolvió 404 en endpoint NVIDIA custom (2026-08-16).
- ACCIÓN: al recuperar terminal, correr `hermes config show` + `grep -ril deepseek` +
  `hermes cron ls` y grabar ubicación real en gbrain para cerrar el hueco.

## Verificación (cuándo revisar este mapa)
- Al inicio de cada sesión de "auditoría/auto-optimización" del agente.
- Antes de cualquier afirmación de "no tengo / no sé dónde está".
- Tras cualquier migración entre PCs (drift de paths/MCP).
