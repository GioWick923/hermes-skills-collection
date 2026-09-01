---
category: hermes
name: memory-layer-ops
description: "Store durable memory via the 3-layer memory bridge."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [memory, persistence, obsidian, gbrain, bridge, knowledge-management]
    related_skills: [headroom-integration, hermes-observational-memory, hermes-obsidian-ops]
---

# Memory Layer Ops — 3-Layer Memory Bridge

Class-level skill for operating Hermes' 3-layer persistent memory architecture.
Not tied to any single tool — covers the protocol, commands, and automation
for writing durable facts to the canonical layer (Obsidian), syncing to the
semantic index (gbrain), and reading context back.

## Architecture

```
┌───────────────────────────────────────────────────┐
│  Layer 1: OBSIDIAN VAULT (canónica, visible)      │
│  ├─ Memorias/Agente/*.md  — hechos persistentes   │
│  ├─ 10-Diario/*.md        — consolidación diaria   │
│  └─ 20-Proyectos/*.md     — contexto de proyectos  │
├───────────────────────────────────────────────────┤
│  Layer 2: GBRAIN MCP (índice semántico, embeds)   │
│  └─ sync vía bridge consolidate (cron 4am)         │
├───────────────────────────────────────────────────┤
│  Layer 3: HERMES MEMORY (built-in, short-term)    │
│  └─ facts entre sesiones, 2.2K chars               │
└───────────────────────────────────────────────────┘
```

## Bridge script

**Ruta:** `$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py`

| Comando | Función | Cuándo usarlo |
|---------|---------|---------------|
| `remember <text> --category X --tags Y` | Guarda hecho en Memorias/Agente/ | Al final de sesión/al aprender algo importante |
| `recall <query>` | Busca en vault + Hermes memory | Antes de responder con info durable |
| `consolidate` | diario con learnings del día | Fin de sesión (o cron 4am) |
| `health` | Check de estado del vault | Diagnóstico |
| `sync-gbrain` | Sincroniza notas a gbrain | Diario (cron 4am) |
| `process-inbox [--apply]` | Procesa capturas | Semanal |

## Protocolo para el agente

1. **Antes de responder con info durable**: ejecutar `recall <query>` — no asumir que la built-in memory es suficiente
2. **Después de aprender algo duradero**: ejecutar `remember` con frontmatter completo
3. **Al final de sesión**: ejecutar `consolidate` (el cron 4am lo hará si se olvida)
4. **Decisiones de arquitectura**: persistir con `--epistemic decision --confidence high`
5. **Contexto de usuario**: checkear memory built-in, luego vault (recall), luego web

## Frontmatter estándar

Notas en `Memorias/Agente/`:
```yaml
type: config|decision|learning|preference|fact
confidence: high|medium|low
epistemic: fact|self_report|observation|hypothesis|preference
tags: [tag1, tag2]
source: hermes
```

## Routing

| Tipo | Destino |
|------|---------|
| Config/decisiones/learnings/preferencias/facts | `Memorias/Agente/` |
| Consolidación diaria | `10-Diario/` |
| Capturas rápidas | `00-Inbox/` |
| Proyectos | `20-Proyectos/` |

## Pitfalls

- **MSYS path**: en git-bash `/c/Users/...` → `C:\Users\...`. Preferir nativa.
- **No editar notas del agente** sin actualizar frontmatter.
- **gbrain sync** solo indexa notas nuevas por mtime. Editar no re-indexa.
- **No duplicar**: hecho va a Memorias/Agente/ o Inbox, no ambos.
- **Nunca sobrescribir** sin diff. `process-inbox` preview por defecto.

## Verificación

```bash
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" health
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" recall "query de prueba"
```

## Vault

`C:\Users\<USER>\Documents\Obsidian Vault\`
Override: `OBSIDIAN_VAULT_PATH`