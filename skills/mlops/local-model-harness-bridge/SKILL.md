---
name: local-model-harness-bridge
description: "Harness de agentes a modelos locales via proxy."
version: 1.0.0
author: Hermes
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [harness, dsh, modelo-local, proxy, openai-compatible, streaming, delegacion]
    related_skills: [local-model-install, local-gguf-deployment, ornith-code-audit, vram-watchdog]
---

# Local Model Harness Bridge

Clase de trabajo: hacer que un CLI/harness de agentes (DSH/DeepSeek Harness, Codex, etc.)
pueda usar un **modelo local** (llama.cpp, Ollama) como proveedor "nativo" de LLM.

Validado con DSH ↔ Ornith (2026-08-20): `dsh` habla con llama.cpp :8080 vía
`dsh-llm-pi-ai` + un proxy en :8081.

## Arquitectura general

```
harness (adaptador multi-proveedor) → proxy local (:8081) → modelo local (:8080)
                                           ↑ inyecta params necesarios
```

El proxy existe por una razón concreta: **modelos modernos (Qwen3.x) piensan por
defecto** — gastan todos los tokens en `reasoning_content` y responden vacío.
El proxy inyecta `chat_template_kwargs.enable_thinking=false` en cada request.

## Pasos

1. **Detectar el mecanismo de proveedores del harness.**
   - DSH: plugin `dsh-llm-pi-ai` — acepta gateways OpenAI-compatibles hand-declared
     en `~/.dsh/settings.yaml` bajo `llm-pi-ai.providers.<name>`.
   - Config: `api: openai-completions`, `baseURL`, `apiKeyEnv` (placeholder OK),
     `models: [{id, contextWindow, maxTokens}]`.
2. **Proxy**: reenviar POST `/v1/chat/completions` al upstream inyectando el flag.
   - Script de referencia: `$LOCALAPPDATA/hermes/scripts/ornith_proxy.py`
   - Endpoints GET `/health` y `/models` para que el harness sondee.
3. **Contexto**: harnesses mandan system prompts largos (~11k tokens). Si el modelo
   local arranca con `-c 8192` → `CONTEXT_WINDOW_EXCEEDED`. Subir a 16384
   (modelo 9B Q5 cabe en 12GB VRAM).
4. **Probar**: primero petición corta ("di OK") → luego tarea real.

## Pitfalls (verificados en producción)

- **SSE streaming**: DSH usa streaming; el proxy debe reenviar `text/event-stream`
  chunk por chunk (`resp.read(8192)` en loop) — NO leer todo y devolver JSON,
  o el harness se cuelga o trunca la respuesta.
- **Respuestas largas en modo headless**: `dsh --profile headless` con código largo
  a veces devuelve solo el primer token ("Par" en vez de "París") con EXIT=1
  (finish_reason=length). Para generar CÓDIGO largo, consultar el proxy directo
  con curl/python (max_tokens 2000+), no vía headless.
- **Prompts largos**: prompts muy largos (rutas Windows `C:\Windows\Temp`) pueden
  dar HTTP 400 del upstream. Simplificar el prompt.
- **reasoningEffort**: NO declarar `reasoning: off` ni `reasoningEffort` en modelos
  hand-declared → error `UNSUPPORTED_REASONING_EFFORT`. Cada modelo maneja su default.
- **apiKeyEnv**: pi-ai exige una referencia de key aunque el endpoint local no la
  valide — cualquier placeholder (`local-no-key`) funciona.
- **Sesiones zstd corruptas**: tras errores, `~/.dsh/sessions/*` puede quedar
  ilegible; borrarlas si DSH falla al releer.
- **enable_thinking**: sin el proxy (o sin el flag), el modelo responde vacío.

## Modo cerebro/manos (delegación a modelo abliterado)

Cuando el usuario pide que un modelo local abliterado **mejore código de Hermes**:
- Hermes = manos: ejecuta el entregable TAL CUAL (solo quitar envoltorio ``` si trae).
- NO auditar/corregir su código (intervenir le quita el estilo abliterado).
- Backup del original (`archivo.bak.ornith`) antes de reemplazar.
- Si hay bug: devolverle el error al modelo para que ÉL se autocorrija, no corregir
  uno mismo. (Verificado: Ornith olvidó `import urllib` → se le devolvió el
  NameError → él mismo lo corrigió en su v3.)
- Reportar al usuario: qué cambió (diff resumido), qué pruebas se corrieron, qué
  observaciones — sin tocar el código.

## Verificación
- [ ] `curl http://127.0.0.1:<proxy>/health` → ok
- [ ] Harness responde a petición corta
- [ ] Petición larga/código: usar proxy directo si headless trunca
- [ ] Sin proxy: content vacío; con proxy: content limpio (thinking off)