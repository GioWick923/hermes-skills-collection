---
name: memory-supermemory
description: "Integrate Supermemory as extraction layer before gbrain. Use when user wants auto-extraction of facts, contradiction resolution, or auto-forgetting of temporary information."
metadata:
  hermes:
    tags: [memory, supermemory, extraction, gbrain, obsidian]
    category: integrations
---

# Supermemory Integration for Hermes

Esta skill integra **Supermemory** como capa de extracción de memoria antes de gbrain, creando un pipeline de 3 capas:

```
Supermemory (extracción) → gbrain (indexación) → Obsidian (storage)
```

## Cuándo usar

- Usuario dice: "extrae facts de nuestra conversación"
- Quiere auto-forgetting de información temporal
- Necesita resolución automática de contradicciones
- Quiere conectar con GDrive/Gmail/Notion

## Pipeline completo

Ejecutar con:
```bash
python ~/.hermes/scripts/supermemory-bridge.py --full
```

O pasos individuales:
```bash
python ~/.hermes/scripts/supermemory-bridge.py --extract  # Extraer facts
python ~/.hermes/scripts/supermemory-bridge.py --ingest   # Indexar en gbrain
python ~/.hermes/scripts/supermemory-bridge.py --sync     # Sincronizar a Obsidian
```

## Requisitos previos

1. **Supermemory instalado:**
   ```bash
   npm install -g supermemory
   ```

2. **gbrain configurado:** Ya debe estar corriendo el MCP server

3. **Obsidian vault:** Ruta configurada en `~/.hermes/config.yaml`

## Flujo de datos

### 1. Extracción (Supermemory)
- Escanea conversaciones recientes
- Extrae facts sobre:
  - Preferencias del usuario
  - Proyectos activos
  - Decisiones tomadas
  - Contexto de sesiones anteriores
- Detecta y resuelve contradicciones
- Marca facts temporales para expiración

### 2. Indexación (gbrain)
- Recibe facts estructurados en JSON
- Crea embeddings con Ollama local
- Indexa en pgvector
- Construye knowledge graph
- Permite búsqueda híbrida (vector + BM25)

### 3. Sincronización (Obsidian)
- Exporta facts como notas markdown
- Agrega frontmatter con metadatos
- Git commit automático
- Mantiene historial de cambios

## Configuración

### Supermemory config
```json
{
  "sources": [
    {
      "type": "obsidian",
      "path": "C:/Users/<USER>/Documents/Obsidian Vault"
    }
  ],
  "extraction": {
    "auto_extract": true,
    "trigger": "session_end"
  },
  "forgetting": {
    "enabled": true,
    "ttl_days": 30
  }
}
```

### Bridge config (scripts/supermemory-bridge.py)
```python
HERMES_HOME = Path(os.environ.get('LOCALAPPDATA', r'C:\Users\<USER>\AppData\Local')) / 'hermes'
OBSIDIAN_VAULT = Path(r'C:\Users\<USER>\Documents\Obsidian Vault') / 'Memorias' / 'Agente'
```

## Estado del sistema

Verificar con:
```bash
python ~/.hermes/scripts/supermemory-bridge.py --status
```

Muestra:
- Supermemory instalado: ✅/❌
- Facts extraídos: cantidad
- Obsidian vault: accesible

## Troubleshooting

### Supermemory no instalado
```bash
npm install -g supermemory
```

### gbrain no responde
- Verificar que el MCP server esté corriendo
- Reiniciar Hermes (`/reset`)

### Errores de sync
- Verificar permisos en Obsidian vault
- Checkear espacio en disco

## Notas importantes

- **No destructivo:** El pipeline solo lee y escribe en rutas configuradas
- **Reversible:** Cada paso puede deshacerse manualmente
- **Monitorizable:** Logs detallados en `~/.hermes/logs/supermemory-*.log`
- **Automatable:** Puede agregarse a cron jobs para sync periódico

## Referencias

- [Supermemory GitHub](https://github.com/supermemoryai/supermemory)
- [GBrain Documentation](https://github.com/garrytan/gbrain)
- [Hermes Memory Stack](https://hermes-agent.nousresearch.com/docs/guides/memory/)
