---
category: hermes
name: bot-fleet-registry
description: "Audita la flota Hermes: skills, cronjobs y su salud."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [fleet, registry, audit, cron, skills]
    related_skills: [port-external-pattern-to-hermes, hermes-self-audit, agent-operating-manual, hermes-observational-memory]
---

# Bot Fleet Registry

## Qué es

El equivalente Hermes del "Bot Advisor" de Grok Bot: un inventario central y vivo
de TODA la flota — skills, cronjobs, MCPs — con propósito, estado y salud.
Cuando alguien pregunta "¿qué tenemos?", la respuesta sale de aquí, no de memoria.

## Estado inicial (2026-08-26)

### Cronjobs detectados vía `hermes cron list`

| Job | Schedule | Estado | Notas |
|-----|----------|--------|-------|
| gbrain-sync-vault | `0 23 * * *` | 🔴 error 4x | `RuntimeError: 'NoneType' has no attribute 'build_kwargs'` |
| Hermes self-audit | `0 22 */3 * *` | 🟢 ok | script no-agent, el único sano |
| Hermes auto-evolución semanal | `0 6 * * 0` | 🔴 error | mismo bug build_kwargs — la auto-evolución NO corre |
| Hermes memory-consolidate nocturno | `0 3 * * *` | 🔴 error 3x | mismo bug build_kwargs |
| Hermes validate-loop calidad | `0 */6 * * *` | 🔴 error 15x | mismo bug build_kwargs |
| Hermes autonomy-tick | `0 */2 7-21 * * *` | ⚪ sin datos | next run 2026-09-07 (perfil de tiempo) |

**Actualización registry.py (2026-08-26)**: inventario real = 336 skills, 14 cronjobs,
5 en error (todos `build_kwargs`): gbrain-sync-vault, auto-evolución, memory-consolidate,
validate-loop, morning brief. Los demás ok.

**Actualización 2026-09-07 (auditoría + fixes):**

| Job | Estado final | Fix aplicado |
|-----|--------------|--------------|
| gbrain-sync-vault | 🟢 OK (verificado E2E) | Ver lección de lock wedged abajo |
| memory-consolidate nocturno | 🟢 build_kwargs desapareció tras restart del gateway | Errores recientes eran HTTP 500 transitorios del proveedor |
| morning brief | 🟢 idem | idem |
| obsidian-memory-consolidate | 🟢 idem | idem |

### Lección 1: `gbrain serve` wedged bloquea el CLI sync
- Síntoma: `gbrain sync` falla con "a live `gbrain serve` (PID X) is not answering its IPC socket. It may be wedged"
- Causa: el gateway de Hermes mantiene un MCP `gbrain serve` vivo; si ese proceso arrancó con código viejo (pre-upgrade) o se wedged, su lock PGLite bloquea al CLI y su IPC no responde
- Fix (en `scripts/sync_gbrain_vault.sh`): si el bridge falla con ese error, matar los procesos bun.exe y reintentar una vez. El gateway re-spawnea el serve fresco automáticamente (verificado: reconnect OK)
- Probar SIEMPRE con `hermes cron run <job-id>` E2E, no solo con el script suelto

### Lección 2: "llama-server 127.0.0.1:4086" = error del PROVEEDOR, no local
- El stack `HTTP 500: error reading llama-server response: read tcp 127.0.0.1:4145->127.0.0.1:4086` parece error local pero es del lado de orcarouter.ai (su infra interna). Igual que sus 503 de capacidad. No buscar el puerto 4086 en la config local — no existe

### Lección 3: `build_kwargs` RuntimeError = gateway muerto, no bug de jobs
- Cuando el gateway muere (OOM/kill) y los jobs corren en catch-up, fallan con `RuntimeError: 'NoneType' object has no attribute 'build_kwargs'`. Fix: restart del gateway (`hermes gateway stop && hermes gateway start`), no tocar los jobs

### Lección 4: orcarouter key tiene alcance LIMITADO (2026-09-09)
- La key orcarouter solo tiene acceso a `z-ai/glm-5.3-flash-free`. Cualquier job/config fijado a `deepseek/*` o `qwen/*` vía orcarouter da `HTTP 403 model_access_denied`
- Fix raíz (2026-09-09, verificado 15/15 ok): jobs deepseek → provider `openrouter` (deepseek-v4-flash verificado OK ahí); fallback_providers orcarouter/qwen → openrouter/deepseek; aliases orcarouter-qwen → glm-5.3-flash-free
- Antes de fijar un modelo a un provider, PROBAR con `hermes chat -q "di OK" -m <model> --provider <prov>`

### Lección 5: `nvidia/glm-5.2` SIEMPRE piensa (no acepta thinking off)
- Jobs con reasoning off + glm-5.2 → `HTTP 400: 该模型始终思考`. Fix: `reasoning: low` en el job
- 429 de Tencent Cloud = límite transitorio de concurrencia; reintentar luego, no cambiar config

### Lección 6: `tasklist //FO` falla en git-bash (MSYS convierte `//` a path)
- En scripts .sh usar `tasklist /FO CSV` con `MSYS_NO_PATHCONV=1` si hace falta. `//FO` → "Argumento u opción no válido"

### Estado post-auditoría 2026-09-09 (15/15 ok)
- Todos los cron jobs verdes E2E. Fixes aplicados: 6 jobs deepseek→openrouter, morning brief reasoning low, sync_gbrain_vault.sh tasklist, model.default→openrouter/deepseek-v4-flash, fallback qwen→deepseek
- Backups: jobs.json.bak-20260909, presets.ini.bak-20260909, config.yaml.bak-20260909 (+bak2), SOUL.md.bak-20260909, sync_gbrain_vault.sh.bak-20260909
- Pendiente aceptado: 8 npm vulns en código fuente hermes-agent (NO parchear local: rompería hermes update; esperar upstream). getrlimit fix: .pth de VideoCaptioner deshabilitado (reversible). llama-server preset: draft-mtp quitado, ctx 32K
- supermemory sin API key (provider configurado pero muerto — cae al built-in, no bloquea)

**Diagnóstico del bug `build_kwargs` (v0.20.4, 2026-08-26):**
- Patrón: fallan los jobs que despachan con **agente/skills**; el que corre script
  puro (`Hermes self-audit`, modo no-agent) funciona.
- REINTERPRETADO 2026-09-07: no es bug del ejecutor — es el gateway caído durante el catch-up. Tras restart del gateway los 3 jobs afectados dejaron de reportar build_kwargs.

## Cómo mantener el registro

1. **Regenerar inventario**: `python scripts/registry.py` (escribe `registry.json`
   con timestamp, skills escaneadas de `$LOCALAPPDATA/hermes/skills` + estado de cronjobs).
2. **Al crear/borrar un skill o cronjob** → regenerar el inventario.
3. **Auditoría semanal** (integrar con hermes-self-audit):
   - `hermes cron list` → ¿algún job en error? Anotar y escalar.
   - `hermes gateway status` → si hay errores masivos en jobs de agente, el gateway probablemente murió (ver Lección 3).
   - Skills huérfanas (sin uso en 30 días) → marcar para revisión, NO borrar sin
     aprobación del usuario (regla SOUL.md).
4. **Portes externos** (prompts de botdirectory/Grok/etc.): registrar cada skill
   portado aquí con su fuente (`source: botdirectory/<slug>`), fecha y veredicto
   🟢/🟡/🔴.

## Criterios de entrada en el registro

- Skill/cron/MCP que aporta valor recurrente.
- Nombre, propósito (1 línea), dependencias (MCP/API/credenciales), estado.
- Veredicto si vino de un porte externo.

## Checklist de auditoría

- [ ] `hermes cron list` sin errores nuevos (o bug documentado)
- [ ] `registry.py` regenerado tras cambios
- [ ] Skills huérfanas identificadas
- [ ] Portes externos registrados con fuente
