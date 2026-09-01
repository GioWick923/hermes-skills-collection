# Bridge Command Reference — memory-layer-ops

## Quick reference for hermes_obsidian_bridge.py

### Remember (store durable facts)

```bash
# Basic
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" remember "text to remember"

# With metadata
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" remember \
  "fact text" \
  --category config \
  --tags "tag1,tag2" \
  --confidence high \
  --epistemic fact

# Categories: config, decision, learning, preference, fact
# Epistemic: fact, self_report, observation, hypothesis, preference
```

### Recall (search vault)

```bash
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" recall "search query"
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" recall "search query" --limit 5
```

### Consolidate (daily summary)

```bash
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" consolidate
```

### Health check

```bash
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" health
```

### Sync to gbrain

```bash
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" sync-gbrain
```

### Process inbox

```bash
# Preview (default)
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" process-inbox

# Apply (move notes to targets)
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" process-inbox --apply
```

## Arquitectura de memoria instalada

```
Observations (session) → Obsidian vault (Memorias/Agente/*.md)
                        → gbrain (semantic index, MCP 124 tools)
                        → Hermes memory (built-in, 2.2K chars)
                        → Cron consolidación 4am
```

## Frontmatter template

```yaml
---
type: config|decision|learning|preference|fact
created: 2026-08-22T02:03:11
updated: 2026-08-22T02:03:11
confidence: high|medium|low
tags: [tag1, tag2]
source: hermes
epistemic: fact|self_report|observation|hypothesis|preference
---
```

## Daily note structure

Las notas de consolidación en `10-Diario/YYYY-MM-DD.md` contienen:
- Frontmatter (date, type: consolidation, entries: N)
- Secciones por categoría con el texto de cada learning del día

## Script location

- Bridge: `$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py`
- Legacy ops: `$LOCALAPPDATA/hermes/scripts/obsidian_ops.py`
- Actualización de índices: `$LOCALAPPDATA/hermes/scripts/update_vault_index.py`

## Cron automation

| Job | Schedule | Action |
|-----|----------|--------|
| obsidian-memory-consolidate | 0 4 * * * | consolidate + sync-gbrain + health |
| headroom-proxy-monitor | */10 * * * * | Proxy health check |

## SOUL.md reference

§24 contiene la especificación completa de la arquitectura de memoria 3 capas.

## Env vars

```bash
OBSIDIAN_VAULT_PATH=C:\Users\<USER>\Documents\Obsidian Vault
```