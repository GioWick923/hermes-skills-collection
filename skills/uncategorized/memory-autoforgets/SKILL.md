---
name: memory-autoforgets
description: "Auto-forgetting system for Hermes memory. Expires temporary facts based on TTL. Use when user wants automatic cleanup of old memories or to configure forgetting rules."
metadata:
  hermes:
    tags: [memory, autoforgets, ttl, cleanup]
    category: memory
---

# Memory Auto-Forgetting System

Sistema de olvido automático para la memoria de Hermes. Elimina facts temporales basados en TTL (Time To Live) configurable.

## Cuándo usar

- Cleanup periódico de memoria
- Configuración de reglas de expiración
- Diagnóstico de facts por expirar

## Configuración

Archivo: `~/.hermes/memory-config.json`

```json
{
  "ttl": {
    "temporary": 7,      // Facts temporales (1 semana)
    "project": 30,       // Facts de proyecto (1 mes)
    "preference": 90,    // Preferencias (3 meses)
    "decision": 180,     // Decisiones (6 meses)
    "ephemeral": 1       // Facts efímeros (1 día)
  },
  "enabled": true
}
```

## Uso

```bash
# Ver estado actual
python ~/.hermes/scripts/memory-autoforgets.py --status

# Escanear facts por expirar
python ~/.hermes/scripts/memory-autoforgets.py --scan

# Limpiar facts expirados
python ~/.hermes/scripts/memory-autoforgets.py --cleanup

# Configurar TTL personalizado
python ~/.hermes/scripts/memory-autoforgets.py --set-ttl temporary 14
```

## Integración con gbrain

El sistema escanea:
- `~/.hermes/gbrain/state.json` (facts indexados)
- `~/.hermes/memos-state.json` (memorias MemOS)

Y aplica TTL según el tipo de fact.

## Cron job recomendado

Agregar a cron para cleanup diario:
```bash
0 3 * * * python ~/.hermes/scripts/memory-autoforgets.py --cleanup >> ~/.hermes/logs/autoforgets.log 2>&1
```
