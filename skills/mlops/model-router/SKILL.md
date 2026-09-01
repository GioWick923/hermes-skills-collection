---
name: model-router
description: "Elegir mejor modelo según la tarea (catálogo de gateways)."
version: 1.0.0
author: Hermes Agent (decisión de Gio 2026-08-31 - siempre tener opciones, ordenadas de mejor a menor)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [modelos, ranking, gateway, seleccion, openrouter, aihubmix, orcarouter]
    related_skills: [local-llm-picker, env-policy, hermes-model-config]
---

# Model Router — elegir el mejor modelo según la tarea

## When to Use
Antes de ejecutar cualquier tarea de IA que requiera un LLM, elegir el MEJOR modelo del
catálogo según el tipo de tarea (no fijarse en uno solo). También para escalar si el
resultado no cumple, o proponer alternativas ordenadas de mejor a menor.

> Decisión de Gio: "quiero 1200+ modelos expuestos (investigación, no producción), para
> siempre tener opciones y ordenarlas de la mejor opción a la menor." Hermes debe poder
> **elegir el mejor modelo para CADA tarea**, no fijarse en uno solo.

## Catálogo de gateways (VERIFICADO 2026-08-31, +450 modelos accesibles)
| Gateway | base_url | Modelos | Nota |
|---|---|---|---|
| **aihubmix** | `https://aihubmix.com/v1` | 409 | ✅ Principal, muchos free (glm-5.3-flash, hy3-free, minimax-free, coding-glm-free) |
| **bai** | `https://api.b.ai/v1` | 44 | glm-5.x, gpt-5.x, minimax |
| **orcarouter** | `https://api.orcarouter.ai/v1` | varios free | deepseek, qwen, hy3, tencent |
| **openrouter** | `https://openrouter.ai/api/v1` | cientos | fallback |
| **empero** | `https://free.empero.org/v1` | free | alternativo |
| **Ollama local** | `http://127.0.0.1:11434/v1` | qwen3-moe-G, ablit-30b, qwen25vl, nomic | local, aire-gapped |

> Listar modelos reales de un gateway:
> `GET <base_url>/models` con `Authorization: Bearer <key>` (ver `hermes-model-config`).

## REGLAS DE ELECCIÓN (mejor → menor) según la tarea

### 1. Primero clasificar la tarea
| Tipo de tarea | Mejor opción (orden) |
|---|---|
| **Código / tool-use / razonamiento fuerte** | `claude-opus-5`, `deepseek-v4-pro`, `coding-glm-5.3`, `gpt-5.6` → luego free |
| **Analizar/dialogar en español, costo 0** | `glm-5.3-flash` (default), `qwen3.8-flash` → `hy3-free` |
| **Costo cero / rate-limits altos** | `*-free` primero: glm-5.3-flash, minimax-m2.7-free, hy3-free, nemotron-free |
| **Voz / audio (ASR, TTS)** | **Granite** (ASR), **chatterbox/xtts** (TTS) — local |
| **Visión / imagen** | `qwen25vl` local, `gemini-3.7-flash` |
| **Privacidad / air-gapped** | **Ollama local** (qwen3-moe-G) — nunca sale del equipo |
| **Investigación / probar algo nuevo** | cualquier modelo del catálogo (no productivo) |

### 2. Ordenar por prioridad (siempre mejor→menor)
1. **Costo**: gratis primero (a menos que la tarea lo justifique).
2. **Calidad**: para razonamiento difícil, priorizar modelo fuerte sobre free.
3. **Velocidad**: para tareas cortas, flash/turbo; para largo, pro/max.
4. **Rendimiento percibido**: si un modelo falla o es lento → saltar al siguiente.

### 3. Evitar
- ❌ No fijarse SIEMPRE en `glm-5.3-flash` si la tarea es compleja.
- ❌ No elegir un modelo solo porque está en el catálogo — verificar que ande (probar con request real).
- ❌ No mezclar acceso a gateways con keys caídas — verificar antes.

## Flujo para elegir (cuando el usuario pide algo de IA)
1. **Clasificar la tarea** (tabla arriba).
2. **Elegir el mejor** → probar con un request real (si falla, saltar al siguiente).
3. **Justificar** brevemente al usuario por qué esa opción.
4. **Escalar**: si la tarea es muy compleja o el resultado es malo, subir de calidad (costo).

## Verificación
- [ ] Elegir el modelo según la tarea, no por inercia
- [ ] Probar con request real antes de afirmar que funciona
- [ ] Ordenar gratis primero (salvo tarea que justifique costo)
- [ ] Local (Ollama) para privacidad, cloud para potencia
- [ ] Saltar a siguiente si falla/lento
