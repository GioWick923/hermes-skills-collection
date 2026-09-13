---
name: loop-rat
description: "Autonomous loop agent for Hermes maintenance — scheduled shifts with contracts, grading, and receipts. Use when user wants automated maintenance loops, self-healing, or scheduled agent tasks."
metadata:
  hermes:
    tags: [loop, rat, automation, maintenance, contract]
    category: automation
---

# Loop Rat — Autonomous Maintenance for Hermes

Sistema de loops autónomos con contratos, grading y receipts para mantenimiento programado de Hermes.

## Arquitectura

```
Schedule → Preflight → Act → Verify → Guard → Grade → Receipt
```

## Loops configurados

| Loop | Frecuencia | Autonomía | Propósito |
|------|------------|-----------|-----------|
| health-check | Cada 6h | report-only | Estado de Hermes |
| memory-consolidate | Cada 12h | assisted | Consolidar memoria |
| skill-audit | Diario (lab) | report-only | Auditar skills |
| evolution-review | Semanal | assisted | Revisar EVOLUTION |

## Uso

```bash
# Ejecutar un shift
python ~/.hermes/scripts/loop_rat_wrapper.py health-check

# Listar loops
python ~/.hermes/scripts/loop_rat_wrapper.py --list

# Ver estado
python ~/.hermes/scripts/loop_rat_wrapper.py --status

# Dry run (sin ejecutar)
python ~/.hermes/scripts/loop_rat_wrapper.py health-check --dry-run
```

## Configuración

- **Contract:** `~/.hermes/loop-rat/CONTRACT.md`
- **Settings:** `~/.hermes/loop-rat/.claude/loops/settings.json`
- **Plans:** `~/.hermes/loop-rat/.claude/loops/<name>/plan.md`
- **State:** `~/.hermes/loop-rat/state/`
- **Receipts:** `~/.hermes/loop-rat/state/receipts/<date>/<loop>/`

## Safety

- **Kill switch:** `kill.sh` o crear `state/HALT`
- **Spend caps:** Max $5/día, $1/shift
- **Blast radius:** Max 5 archivos
- **Denylist:** .env, secrets, credenciales

## Receipt format

```json
{
  "loop": "health-check",
  "started_at": "2026-09-08T19:00:00",
  "phase": "completed",
  "status": "completed",
  "files_changed": 0,
  "cost_usd": 0.00
}
```

## Integración con Hermes

Los loops pueden:
- Leer logs y estado
- Consolidar memoria
- Auditar skills
- Revisar evolución
- Generar reports matutinos

**No pueden:**
- Modificar config.yaml
- Touch .env
- Cambiar credenciales

## Ver

- Repo original: https://github.com/mrbuzzoni/loop-rat
- Docs: https://loop-rat.docs
