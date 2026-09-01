---
name: local-llm-constrained-output
description: "Delegar a Ollama con format=schema para JSON válido."
version: 1.0.0
author: Hermes Agent (integrado desde SKILL.state 2026-08-31)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [llm-local, ollama, constrained-decoding, json-schema, structured-output, skill-state]
    related_skills: [local-llm-operator-loop, dsh-ornith-bridge, local-llm-picker]
---

# Local LLM Constrained Output (Ollama + JSON Schema)

## When to Use
Delegar cualquier tarea estructurada a un modelo local vía Ollama y forzar salida JSON
válida y completa con `format` = schema. Úsalo cuando el output no sea texto libre para
leer: estado de merge de checkpoints, publish Civitai, señales de trading, state transitions.

> Patrón del paper **SKILL.state** (arXiv 2608.26263v2, §5.7 error taxonomy):
> en modelos pequeños el 68% de errores es **overwrite prematuro de claves**, 20% type coercion,
> 12% JSON syntax. El problema NO es razonamiento — es **adherencia al formato estructurado**.
> La solución: **grammar/format-constrained decoding** (Ollama `format`), que garantiza salida
> JSON válida SIN costo de retry.

## Cuándo usar
- Delegar cualquier tarea estructurada a `qwen3-moe-G:latest` (Ollama, RTX 3060, 30B-A3B MoE).
- Cuando necesitas que el modelo local produzca estado/JSON que luego consumirá el agente
  (merge de checkpoints, publish Civitai, trading signals, state transitions).
- SIEMPRE que pidas output que no sea texto libre para leer.

## Verificado (prueba directa 2026-08-31, Ollama 0.33.2)
| Escenario | Resultado |
|---|---|
| `format` = schema anidado | HTTP 200, `json.loads` OK, claves completas y densas |
| `format` = "json" (string) | HTTP 200, JSON válido |
| Sin `format` (status quo) | ⚠️ ` ```json` envoltorio + **claves infladas con relleno** (no datos densos) |

**Lectura clave**: sin `format`, el modelo envuelve en markdown y rellena las claves con verbosidad,
en vez de devolver solo los datos. Con `format`, devuelve exactamente lo pedido. Esto degenera
menos y evita retries.

## Endpoint y formato

```
POST http://127.0.0.1:11434/api/chat
```
```json
{
  "model": "qwen3-moe-G:latest",
  "messages": [{"role":"user","content":"..."}],
  "format": { TIPO_JSON_SCHEMA },
  "stream": false,
  "options": {"temperature": 0}
}
```

### Reglas del `format`
- **`format` = objeto schema** (JSON Schema draft-07 subset): fuerza la salida a respetar
  types y `required`. Es la opción óptima para estado estructurado. **Mantén el schema plano
  cuando puedas** — schemas demasiado anidados pueden dar 500 (probado: un schema con objetos
  profundos devolvió 500; uno modesto con `object>object>number` pasó).
- **`format` = "json"** (string): suficiente cuando solo quieres JSON válido pero el shape
  lo remata el prompt. Más robusto que nada.
- Esquema anidado que PASÓ (estado de merge):
```json
{"type":"object","properties":{"arq_verificada":{"type":"boolean"},"salida":{"type":"string"},"pesos":{"type":"object","properties":{"wA":{"type":"number"},"wB":{"type":"number"},"wC":{"type":"number"}}},"pasos":{"type":"array","items":{"type":"string"}}},"required":["arq_verificada","salida","pesos"]}
```

## Receta para delegar con estado (SKILL.state aplicado)
1. **Definir schema fijo** del estado del dominio (una vez, no por tarea) — igual que los
   bloques `Estado de ejecución` de las skills.
2. **Inyectar estado en el prompt**: `(spec + Estado actual + última observación)`.
3. **Pedir SOLO el JSON del paso siguiente** con `format` = schema.
4. **Validar** el JSON devuelto (json.loads + verificar claves `required`).
5. **Actualizar estado + descartar razonamiento** (el modelo no re-lee historia).

## Llamada de ejemplo completa (probada)
```python
import json, urllib.request
schema = {"type":"object","properties":{"wA":{"type":"number"},"wB":{"type":"number"}},"required":["wA","wB"]}
payload = {"model":"qwen3-moe-G:latest",
  "messages":[{"role":"user","content":"Devuelve JSON con pesos wA=0.5 wB=0.5"}],
  "format": schema, "stream": False, "options":{"temperature":0}}
req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req, timeout=90) as r:
    print(json.loads(r.read())["message"]["content"])
```

## Pitfalls
- **HTTP 500 con schema anidado profundo**: simplifica (aplanar objetos, quitar `additionalProperties`)
  o usa `format:"json"`. El 500 no es del proxy ni del modelo — es el schema.
- **`stream`**: mantener `false` para parsear la respuesta completa. Con `true`, hay que acumular SSE.
- **`enable_thinking`**: si usas el proxy `ornith_proxy.py:8081` queda inyectado; con Ollama directo
  `:11434`, no apliques thinking off salvo que el modelo lo requiera (qwen3-moe lo tolera).
- **Claves `required`**: defínelas — sin `required`, el modelo puede omitir claves (el 68% del paper).

## Verificación
- [ ] `format` presente en el payload SIEMPRE que pidas JSON estructurado
- [ ] `json.loads` del output pasa + claves `required` presentes
- [ ] Schema plano preferido; anidado solo si pasa sin 500
- [ ] Resultado `qwen3-moe-G` verificado con llamada real, no asumido
