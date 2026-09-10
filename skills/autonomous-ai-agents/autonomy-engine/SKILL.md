---
name: autonomy-engine
description: Autonomous priority queue with time-profile scheduling.
---

# Autonomy Engine

Patterns from `42-evey/hermes-plugins` `evey-autonomy` (MIT). Adapted for a self-directed Hermes agent that runs with minimal human input.

Use when the user wants the agent to operate autonomously: prioritize tasks, schedule by time of day, plan and reflect without asking.

## Core data structures

- **Priority queue** of tasks with importance scoring (1-10) and source signals
- **Time profiles**: morning / late_morning / afternoon / evening / night — each maps allowed task types + blocked types
- **Project signals**: track git repos for uncommitted changes, non-default branches, unpushed commits as low-cost signals
- **Config precedence**: env vars > JSON config > neutral defaults (operator, UTC)

## Time-profile pattern (adapt to local timezone)

```
morning      (7-10):  bridge_check, health_check, goal_review, project_check   (block: heavy_research)
late_morning (10-12): research_deep, code_change, goal_work, project_work       (block: none)
afternoon    (12-17): research_quick, bridge_check, goal_work, project_work     (block: none)
evening      (17-21): goal_review, cost_review, light_research                 (block: heavy_delegation)
night        (21-23): memory_maintenance, health_check                         (block: user_alerts, heavy_delegation)
```

## Autonomy loop (per tick)

```
1. GATHER signals  — bridge inbox, goals.md, project git state, cron, memory scores, time
2. SCORE          — rank by importance × urgency × time-profile fit
3. PLAN           — pick top task, decompose if needed
4. EXECUTE        — run with appropriate model (heavy vs cheap)
5. REFLECT        — self-critique via cheap model (see self-reflect skill)
6. LOG            — append to autonomy-log.jsonl
7. REPEAT         — next tick
```

## Config example

```json
{
  "operator_name": "Gio",
  "timezone": "America/Mexico_City",
  "heavy_model": "tencent/hy3",
  "cheap_model": "tencent/hy3",
  "projects": [
    {"name": "mi-app", "path": "/ruta/a/mi-app", "base_branch": "main", "importance": 8}
  ],
  "bridge_peer_names": ["claude-code", "pi", "codex"],
  "disabled_sources": []
}
```

Env overrides: `HERMES_OPERATOR_NAME`, `HERMES_TIMEZONE`, `HERMES_AUTONOMY_HEAVY_MODEL`, `HERMES_AUTONOMY_CHEAP_MODEL`, `HERMES_AUTONOMY_CONFIG`.

## Re-wake throttle exponencial (portado de Paperclip)

El job "Hermes autonomy-tick" usa `autonomy_tick_gate.sh` como monitor-script.
El scheduler suprime el run del agente si la salida del gate es byte-estable vs
el tick anterior; corre si cambia. El gate v3 implementa el patrón
`issue-rewake-throttle.ts` de Paperclip (MIT):

- **Firma** = hash del set de items pendientes (paths de observational-memory
  + memories con status activo). Detecta progreso real, no solo conteo.
- **Firma nueva** (trabajo fresco / el agente avanzo) => resetea streak y despierta.
- **Firma identica** (el agente NO avanzo) => streak++, arma cooldown exponencial
  y SUPRIME repitiendo la linea previa (byte-identica = 0 tokens).
- **Cooldown expirado** => 1 retry, re-arranca cooldown doble.
- Backoff: base 2h -> dobla -> cap 24h (cadencia de tick ~2h; Paperclip usaba
  120s/30min). Modelos caros => ahorra tokens directo.

Estado: `$HERMES_HOME/autonomy-rewake-state.conf` (prev_sig/streak/cooldown_until_ms/last_line).
Tunables env: `REWAKE_THRESHOLD`, `REWAKE_BASE_COOLDOWN_MS`, `REWAKE_MAX_COOLDOWN_MS`.

Comportamiento verificado: trabajo estatico => 1 run fresco + 1 retry + backoff
(0 tokens despues); trabajo nuevo => despierta; cooldown expirado => 1 retry.

## Guard determinista + grader ciego (portado de loop-rat, verificado 2026-09-03)

Fuente: https://github.com/mrbuzzoni/loop-rat (MIT). El harness NO se instaló
(91/129 tests fallan en Windows); se portaron sus 2 ideas netas como scripts propios:

- **`%LOCALAPPDATA%/hermes/scripts/shift_guard.py`** — gate determinista post-turno.
  Ciclo: `snapshot <dir> base.json` ANTES del trabajo → `check <dir> base.json <autonomy>`
  DESPUÉS. Bloquea (exit 3) por: denylist de rutas, path_policy por nivel de autonomía,
  blast radius (`max_files_changed`), y formas de secreto en el diff. Un trabajo sucio
  preexistente NO se le achaaca al turno (fingerprint size:mtime). Config: `shift_guard.json`
  (misma estructura autonomy/guard que loop-rat). `diff <dir> base.json` → sólo paths cambiados.
- **`%LOCALAPPDATA%/hermes/scripts/blind_grade.py`** — grader ciego: un agente que califica
  su propio turno siempre lo encuentra excelente. `compose` arma el brief (rúbricas +
  output.md + diff atribuible, NUNCA el repo); `run` lo manda a Ollama local
  (env `BLIND_GRADE_MODEL`=qwen14-agent, `BLIND_GRADE_URL`) y exige PASS/REVISE/FAIL en la
  primera línea; exit 0 sólo con PASS. Rúbricas en `scripts/rubrics/{code,safety,writing}.md`.

**Protocolo por tick autónomo con writes de código** (integrar al loop GATHER→…→LOG):
```
4a. shift_guard.py snapshot <repo> $TEMP/shift_baseline.json   # antes de ejecutar
4b. EXECUTE (act: shell recoge hechos; modelo sólo para juicio)
4c. verify determinista: comando del plan + exit code — la opinion del modelo no es evidencia
4d. shift_guard.py check <repo> $TEMP/shift_baseline.json <autonomy>   # exit 3 => revertir/reporte
4e. blind_grade.py run output.md --diff-from <repo> $TEMP/shift_baseline.json --save grade.md
5.  REFLECT/LOG — receipt incluye guard verdict + grade verdict
```
Report-only loops: autonomy `report-only` → cualquier archivo escrito bloquea el turno.

## Integration with existing stack

- Use `cronjob` for scheduled ticks (already have self-evolution weekly)
- Use `gbrain` / `memory` for persistence (prefer gbrain over raw MEMORY.md)
- Use `delegate_task` for heavy parallel work
- Use `self-reflect` skill before reporting important outputs

## Source

Ported from https://github.com/42-evey/hermes-plugins (MIT). Plugin: `evey-autonomy/__init__.py` (636 lines).
