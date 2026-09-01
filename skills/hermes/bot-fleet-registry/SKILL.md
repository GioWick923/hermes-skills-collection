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

**Diagnóstico del bug `build_kwargs` (v0.20.4, 2026-08-26):**
- Patrón: fallan los jobs que despachan con **agente/skills**; el que corre script
  puro (`Hermes self-audit`, modo no-agent) funciona.
- Sospecha: bug del ejecutor de cronjobs de Hermes v0.20.4 en el armado de kwargs
  del agente. Verificar en docs hermes-agent; si persiste tras actualizar, reportar.
- Impacto: auto-evolución, consolidación de memoria y QA de alucinaciones están
  muertos silenciosamente. Prioridad alta de fix.

## Cómo mantener el registro

1. **Regenerar inventario**: `python scripts/registry.py` (escribe `registry.json`
   con timestamp, skills escaneadas de `$LOCALAPPDATA/hermes/skills` + estado de cronjobs).
2. **Al crear/borrar un skill o cronjob** → regenerar el inventario.
3. **Auditoría semanal** (integrar con hermes-self-audit):
   - `hermes cron list` → ¿algún job en error? Anotar y escalar.
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
