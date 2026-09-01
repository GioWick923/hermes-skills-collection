---
name: memory-hitrate
description: Use when auditing or measuring Hermes memory quality.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [memory, hitrate, gbrain, vault, observability, audit]
    related_skills: [memory-layer-ops, hermes-observational-memory]
---

# Memory Hit-Rate (lección de LMCache aplicada a Hermes)

## When to Use
Trigger when: (1) the user asks to audit/measure whether Hermes memory is useful, (2) we want to know if gbrain/vault recalls actually hit, (3) deciding which notes to purge, (4) running the weekly memory report.

**Idea:** LMCache mide hit rate de su KV cache; Hermes debe medir el hit rate de su memoria de 3 capas (contexto → gbrain → Obsidian vault). Un caché que no acierta es basura que estorba.

## Script
`$LOCALAPPDATA/hermes/scripts/memory_hitrate.py` (Python, stdlib only, sin deps).

Log: `$LOCALAPPDATA/hermes/data/memory_hitrate.jsonl` (JSONL, auto-creado).

## Comandos

### Registrar un recall (el agente hace esto tras consultar memoria)
```bash
python "$LOCALAPPDATA/hermes/scripts/memory_hitrate.py" record --source gbrain --query "modelo preferido" --hit
python "$LOCALAPPDATA/hermes/scripts/memory_hitrate.py" record --source vault --query "perfil gio" --miss --note "nota stale"
```
`--source`: gbrain | vault | hermes_memory | web | otro
`--hit` o `--miss` obligatorio. `--note` opcional (pista de qué corregir).

### Stats (resumen rápido)
```bash
python "$LOCALAPPDATA/hermes/scripts/memory_hitrate.py" stats            # todo
python "$LOCALAPPDATA/hermes/scripts/memory_hitrate.py" stats --days 7   # ventana
```

### Reporte semanal (accionable, con veredicto 🟢🟡🔴)
```bash
python "$LOCALAPPDATA/hermes/scripts/memory_hitrate.py" report --days 7
```

### Purge candidates (notas que nunca aciertan)
```bash
python "$LOCALAPPDATA/hermes/scripts/memory_hitrate.py" purge-candidates --min-hits 0 --days 30
```

### Reset
```bash
python "$LOCALAPPDATA/hermes/scripts/memory_hitrate.py" reset
```

## Integración con cron
Job semanal (domingo ~06:30): genera reporte y lo persiste en
`$LOCALAPPDATA/hermes/cron/output/memory_hitrate_report.txt`.
Ver cron via `hermes cron list` / `hermes cron edit`.

## Convención de uso para el agente
1. **Después de cada recall** a gbrain/vault/web que determine el rumbo de una respuesta → `record --hit` o `--miss` con query corta.
2. **Al final de sesión larga** (5+ recalls) → `stats` para ver tendencia.
3. **Semanal** (cron) → `report` + `purge-candidates`; si hay candidatas con hits=0 y 30+ días, proponer purga al usuario (no borrar sin confirmar).

## Pitfalls
- Correr con `python` (Windows) — el script usa stdlib, no necesita venv.
- No registrar cada micro-consulta (ruido); registrar recalls significativos.
- `reset` borra historial — usarlo solo si el usuario lo pide.
- Las notas stale detectadas por `--note` son la señal más valiosa: actúa sobre ellas (actualizar o borrar), no solo medir.

## Verification
- `stats` muestra counts + hit rate total y por fuente.
- `report` imprime veredicto semáforo y misses con nota.
- `purge-candidates` lista claves con hits <= min_hits.
