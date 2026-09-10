---
category: automation
name: automation-workflow-patterns
description: "Patrón probado de automatización de agentes (adaptado de OpenHands Agent Canvas Automation Server): script-bundle que hace polling/dedup/llamadas fijas de API, y el agente solo interviene en las partes que requieren juicio. Aplica a cronjobs de Hermes, monitores de GitHub/repos, contenido programado y tareas de trading. Usa cuando se diseñe una automatización recurrente o schedule, un monitor de repo/issue, un flujo Slack/GitHub/Linear, o cuando un cronjob deba separar 'lógica determinista' de 'juicio de agente'."
version: 1.0.0
author: Hermes Agent (patrón adaptado de OpenHands Agent Canvas, MIT)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [automation, workflow, cron, schedule, webhook, github-monitor, script-bundle, agent-canvas, polling, dedup]
    related_skills: [cron-content-delivery, github-issue-to-pr, github-repo-management, safe-autonomy-operations]
---

# Automation Workflow Patterns

> Adaptado del patrón de **Automation Server** de OpenHands Agent Canvas (MIT). La idea central:
> **los flujos automatizados mezclan lógica determinista (polling, dedup, llamadas fijas de API) con
> juicio de agente (¿qué importa?, ¿qué decido?). Sepáralos — no desperdicies tokens del agente en
> lo que un script puede hacer, y no dejes la decisión importante a un script ciego.**

## Cuándo usar
- Diseñar un cronjob de Hermes que repite tareas (trading, contenido, monitoreo)
- Monitorizar un repo/issue/PR de GitHub y convertir eventos en trabajo
- Flujo que responde a webhooks (GitHub, Slack, Linear)
- Cualquier "automatización" que hoy harías con un solo `cronjob` sin pensar en la separación

## Principio central: separar "script-bundle" de "agente"

OpenHands lo llama **script-bundle**: un trozo de código autocontenido que hace el trabajo
determinista — polling, deduplicación, llamadas fijas de API — y **solo delega al agente las
partes que genuinamente requieren juicio**. El agente nunca gasta tokens en lo mecánico.

| Capa | Quién | Qué hace | Ejemplos |
|------|-------|----------|----------|
| **Script-bundle** | Código (python/bash) | Polling, dedup, API fijas, parseo, formato | Fetch de Finviz, chequear issues nuevos, parsear un feed, armar el reporte base |
| **Agente (juicio)** | Hermes (cron) | Decidir, priorizar, redactar, proponer | "¿Este issue es bug o feature?", "¿qué trade es relevante hoy?", redactar el mensaje final |
| **Delivery** | Hermes cron | Enviar al canal correcto | Telegram DM, local, GitHub PR/issue |

## El patrón (5 pasos)

### Paso 1: Identifica la tarea recurrente y su schedule
- ¿Cada cuánto? (minutos, horas, días)
- ¿Qué la dispara? (tiempo, evento/webhook, estado externo)
- Hermes cron: `hermes cron create "every 2h"` o 5-field cron, o webhook.

### Paso 2: Separa lo determinista de lo que necesita juicio
Pregúntate por cada parte del flujo:
- ¿Es una regla fija sin ambigüedad? → **script**
- ¿Requiere interpretar, priorizar o redactar? → **agente**

Regla OpenHands: *"El script hace el trabajo, el agente solo para lo que necesita criterio."*

### Paso 3: Construye el script-bundle (sin agente)
```python
# fetch_datos.py — determinista, sin agente
import urllib.request, json
data = fetch("https://api...")            # llamada fija
seen = load_cache(".cache.json")           # estado previo
new = dedup(data, seen)                    # dedup contra cache
save_cache(".cache.json", data)            # persiste estado
print(json.dumps({"new_items": new}))      # solo lo nuevo sale
```
- **Dedup contra un cache/estado** — evita re-procesar lo mismo
- **Idempotente** — correrlo 2 veces da el mismo resultado
- Guarda estado en un archivo local (`~/.automations/<name>.json`)

### Paso 4: El cronjob solo recibe el output del script
```bash
hermes cron create "0 9 * * *" \
  --script "python ~/automations/fetch_datos.py" \
  --prompt "Con estos datos nuevos: {output}, haz X con juicio..."
```
- `--script` corre el script primero, `{output}` alimenta al agente
- Si el script no produce nada nuevo (dedup vacío) → no gastas tokens del agente

### Paso 5: Verifica la separación
- [ ] ¿El script NO necesita modelo LLM? (si sí, está mal separado)
- [ ] ¿El agente NO hace polling ni parseo manual? (debería recibir datos listos)
- [ ] ¿Correr el script 2× da output idéntico (idempotente)?
- [ ] ¿El estado/cache persiste entre corridas?

## Caso de uso: GitHub Repo Monitor (adaptado de Agent Canvas)
El prebuilt "GitHub Repository Monitor" de OpenHands mira un repo y dispara el agente en eventos.
Versión Hermes con el patrón:

```python
# github_monitor.py — determinista
import urllib.request, json, os
# gh api list issues (state=open), dedup contra cache
new = gh_new_issues("<GITHUB_USER>/hermes-skills-collection")
if not new:
    exit(0)              # nada nuevo → sin gasto de tokens
print(json.dumps({"issues": new}))
```
```bash
# cronjob
hermes cron create "every 30m" \
  --script "python ~/automations/github_monitor.py" \
  --prompt "Revisa estos issues nuevos y sugiere cómo triagear cada uno: {output}"
```
- El script chequea issues **nuevos** (dedup), el agente solo triagea los que sí son nuevos.

## Caso de uso: trading / Finviz (tu flujo real)
```python
# finviz_pulse.py — determinista
fetch = get_finviz_screener("your-scan")
last = load_cache(); save_cache(fetch)
moves = [s for s in fetch if s in interesting_screener(fetch)]  # reglas fijas
print(json.dumps({"moves": moves}))
```
```bash
hermes cron create "0 */4 * * *" \
  --script "python ~/automations/finviz_pulse.py" \
  --prompt "Analiza estos movimientos del mercado y dime cuál merece un backtest: {output}"
```
- El script filtra con reglas deterministas, el agente aplica criterio de trading.

## Caso de uso: contenido programado (cron-content-delivery)
- Script-bundle: fetch de fuentes (feeds, Reddit, X) + dedup de lo ya publicado
- Agente: elige el mejor, redacta humanizado, verifica
- Delivery: cron a Telegram

## Pitfalls
- **No gastar tokens en lo mecánico** — si el cronjob invoca el agente aunque no haya nada nuevo, estás quemando tokens en vacío. El `exit(0)` del script cuando no hay novedad es clave.
- **No dejar decisión importante a un script ciego** — dedup/parseo en script está bien; "¿qué hago con esto?" es del agente.
- **Estado entre corridas** — sin cache, cada corrida reprocesa todo (no idempotente). Persiste en `~/.automations/<name>.json`.
- **Schedule vs evento** — polling (cada X min) está bien para monitoreo barato; para latencia usa webhook si la fuente lo permite.
- **Seguridad del script** — el script corre con tus permisos; nunca incrustes secrets, lee de `.env` / `hermes auth`.

## Seguridad (postura OpenHands)
- Los agents y scripts son **no confiables por defecto** — corre el script con el mínimo privilegio
- Keys/credentials fuera del script (`.env` / vault), nunca hardcodeadas
- Si el backend corre en tu máquina, el agente actúa con tus permisos → define el límite

## Verificación
- [ ] Script determinista sin LLM, idempotente, con dedup
- [ ] Agente recibe solo output filtrado del script
- [ ] Cronjob con `--script` + `{output}`
- [ ] `exit(0)` cuando no hay novedad (cero gasto de tokens)
- [ ] Estado/cache persiste entre corridas

## Fuente
- OpenHands Agent Canvas Automation Server: https://github.com/OpenHands/OpenHands (MIT)
- Docs: https://docs.openhands.dev/openhands/usage/agent-canvas/prebuilt-automations
