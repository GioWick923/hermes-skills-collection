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

## Cold-cache sentinel (portado de oh-my-openagent model-core / MIT)

Patrón del pipeline de resolución de omo: **no elegir modelo con caches fríos.**

Si el catálogo de un gateway (`GET <base_url>/models`) aún no está cargado, o si
`availableModels` + `connectedProviders` están vacíos, la resolución **defiere**
con `{skipped: true}` en lugar de adivinar — el agente espera a que el catálogo
cargue antes de fijar un modelo, porque elegir con datos vacíos casi siempre
elige mal.

Aplicación en nuestro stack:
- Antes de elegir, confirmar que el catálogo del gateway objetivo respondió
  (no asumir 450+ modelos si el request falló o devolvió vacío).
- Si el catálogo está vacío/fallido → NO fijar modelo; reintentar el catálogo o
  pasar a un gateway cuyo catálogo sí respondió.
- `fuzzy match`: omo empareja por **substring corto** (no solo prefijo), así
  `glm-5.3-flash:high` cae en `glm-5.3-flash`. Variantes (`:free`, `:high`)
  matchean el modelo base, nunca se degradan a una variante menor.

## Retry guidance por patrones de error (portado de omo delegate-core / MIT)

Cuando una delegación/request falla, omo clasifica el error contra patrones
conocidos y emite **guía de corrección estructurada** (hint + opciones + ejemplo)
en vez de un error crudo.

Patrones que vale la pena reconocer en nuestro stack:
| Patrón | Señal | Corrección |
|---|---|---|
| Rate limited | HTTP 429 / "rate limit" | bajar max_tokens, esperar, o usar variante free con límite alto |
| Auth fallida | HTTP 401/403 / "invalid key" | verificar key del gateway, no reusar key caída |
| Modelo inexistente | HTTP 404 / "model not found" | probar con request real antes; elegir modelo verificado |
| Cuota free agotada | "free resources... only try N times" | usar modelo de pago o gateway con crédito |
| Timeout | timeout / sin respuesta | modelo flash/turbo o tarea más corta |
| Overload upstream | HTTP 5xx / "upstream" | saltar a siguiente modelo/gateway (no reintentar el mismo) |
| Contexto excedido | "context length" / 402 max_tokens | recortar input, subir max_tokens, o modelo con ventana mayor |

Regla: **clasificar el error ANTES de reintentar.** No reintentar a ciegas el
mismo modelo que falló con 5xx — saltar al siguiente de la lista ordenada.
