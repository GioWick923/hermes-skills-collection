---
name: local-model-agent-integration
description: "Integra servidores locales OpenAI-compatibles con harnesses."
version: 1.0.0
author: Hermes Curator
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [llama-cpp, local-model, agent-harness, dsh, openai-compatible, proxy, thinking]
    related_skills: [local-gguf-deployment, local-ablit-delegation, vram-watchdog]
---

# Local Model ↔ Agent Harness Integration

Clase de trabajo: conectar un servidor local OpenAI-compatible (llama.cpp, Ollama, LM Studio)
como proveedor de un harness de agentes (DeepSeek Harness/dsh, pi-ai, OpenHands, etc.).
Técnicas validadas en 2026-08-20 con Ornith-1.5-9B-uncensored + DSH.

## Cuándo usar
- El usuario quiere que un harness/CLI de agentes use un modelo local (no solo la API cloud).
- Un proveedor local responde vacío, corta la respuesta, o falla con errores crípticos.
- Configurar un gateway OpenAI-compatible (llama.cpp :8080, etc.) dentro de un framework
  que espera proveedores nativos (codex, anthropic, deepseek).

## Patrón 1: Plugin multi-provider nativo (preferido)
Muchos harnesses modernos (DSH usa `dsh-llm-pi-ai`) aceptan gateways OpenAI-compatibles
SIN proxy: declarar la ruta en settings con `api: openai-completions` + `baseURL`.
La ruta se registra como proveedor y aparece en el selector de modelos.

```yaml
llm-pi-ai:
  providers:
    local:
      displayName: Local (9B)
      apiKeyEnv: LOCAL_API_KEY          # placeholder obligatorio aunque el server no valide
      api: openai-completions
      baseURL: http://127.0.0.1:8081/v1 # apuntar al proxy si hace falta (ver Patrón 3)
      models:
        - id: local-9b
          contextWindow: 16384
          maxTokens: 4096
```

## Patrón 2: Desactivar "thinking" (crítico para Qwen3.5 / DeepSeek-family)
Modelos tipo Qwen3.5 gastan todos los tokens en `reasoning_content` y devuelven
`content: ""` si el thinking está activo. Sin esto, el harness recibe respuestas vacías.

- Directo al servidor: inyectar en el body
  `"chat_template_kwargs": {"enable_thinking": false}`
- Vía settings del harness: NO declarar `reasoning: off` ni `reasoningEffort` en modelos
  hand-declared — un modelo sin `reasoningEfforts` rechaza el esfuerzo con
  `UNSUPPORTED_REASONING_EFFORT`. La ausencia = sin opción de razonamiento.

## Patrón 3: Proxy con inyección automática (cuando el harness no deja pasar el flag)
Si el harness no puede inyectar `chat_template_kwargs`, poner un mini-proxy Python
(http.server) entre el harness y llama.cpp que:
1. Lee el body JSON, añade `chat_template_kwargs.enable_thinking=false`, reenvía.
2. **Soporta streaming SSE**: si `stream:true`, reenviar chunk a chunk con
   `Content-Type: text/event-stream` — devolver JSON completo cuelga al cliente.
3. Expone `/health` y `/models` (el harness puede sondear).
Véase `scripts/ornith_proxy_template.py` (plantilla reutilizable).

## Patrón 4: Contexto suficiente para el system prompt del harness
Harnesses de agentes mandan system prompts enormes (~10-11k tokens). Con `-c 8192`
en llama.cpp falla con `CONTEXT_WINDOW_EXCEEDED` (400). Subir a 16384 en el server
y declarar el mismo `contextWindow` en el settings del proveedor.

## Patrón 5: Fallos silenciosos y sesiones corruptas
- Harness headless que sale EXIT=1 con stdout vacío: revisar sesiones internas
  (p. ej. `~/.dsh/sessions/*.jsonl.zstd`) — tras fallos quedan corruptas
  ("could not determine content size") y el harness falla en silencio. Limpiar la carpeta.
- Respuestas CORTAS de modelos locales suelen funcionar; prompts largos/generación de
  código pueden truncarse por max_tokens del agente (sale fragmento + EXIT≠0).
  Para generar código largo, usar el flujo directo al servidor/proxy (curl), no el headless.

## Pitfalls
- **LLM local ≠ jailbreak total**: modelos "abliterados" pueden seguir rechazando malware
  destructivo, keyloggers, NSFW explícito e insultos, aunque den código de pentest/CTF
  y humor subido. Verificar el límite real por modelo, no asumir.
- **netstat/tasklist en Windows** devuelven codepage (no UTF-8): usar `encoding="latin-1"`
  en subprocess para no romper con UnicodeDecodeError.
- **apiKeyEnv placeholder**: pi-ai y similares exigen una referencia de credencial aunque
  el endpoint local no valide keys; cualquier placeholder (`local-no-key`) funciona.
- **VRAM compartida**: varios modelos locales (9B + 27B) no corren a la vez en 12GB;
  alternar con un manager (véase skill vram-watchdog).

## Verificación
- [ ] `curl <baseURL>/health` responde ok
- [ ] Sin inyección thinking → content vacío; con ella → content limpio
- [ ] Harness headless con prompt corto responde
- [ ] Streaming SSE fluye sin colgarse (si el harness usa stream)
- [ ] Modelo local responde a prompt de código largo por el flujo directo

## Scripts y referencias
- `scripts/ornith_proxy_template.py` — plantilla del proxy (thinking-off + SSE)
