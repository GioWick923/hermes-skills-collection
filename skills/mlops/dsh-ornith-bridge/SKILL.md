---
name: dsh-ornith-bridge
description: "DSH usa Ornith local: proxy thinking off + settings pi-ai."
version: 1.0.0
author: Gio + Hermes
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [dsh, ornith, deepseek-harness, proxy, llama-cpp, pi-ai]
    related_skills: [vram-watchdog, ornith-code-audit, local-ablit-delegation]
---

# DSH ↔ Ornith Bridge (mancuerna DeepSeek Harness + modelo local)

Conecta **DeepSeek Harness (dsh)** con **Ornith** (modelo local abliterado en llama.cpp :8080)
para que DSH pueda usar el modelo local como proveedor nativo, sin proxy complejo:
DSH usa el plugin `dsh-llm-pi-ai` (multi-provider, OpenAI-compatible).

## Arquitectura

```
dsh (pi-ai adapter) → ornith_proxy.py (:8081) → llama.cpp Ornith (:8080)
                        ↑ inyecta enable_thinking=false
```

## Por qué el proxy
Ornith (Qwen3.5) piensa por defecto: gasta todos los tokens en `reasoning_content`
y responde vacío. El proxy inyecta `chat_template_kwargs.enable_thinking=false`
en cada request — sin esto, DSH recibe respuestas en blanco.

## Componentes

### 1. Proxy
- Script: `$LOCALAPPDATA/hermes/scripts/ornith_proxy.py`
- Correr: `python "$LOCALAPPDATA/hermes/scripts/ornith_proxy.py" --port 8081`
- Reenvía POST `/v1/chat/completions` a `http://127.0.0.1:8080` con thinking off
- Endpoints GET `/health` y `/models` para sondear

### 2. Settings de DSH (`~/.dsh/settings.yaml`)
```yaml
agent-default-model:
  provider: ornith
  model: ornith-9b

llm-pi-ai:
  providers:
    ornith:
      displayName: Ornith Local (9B abliterado)
      apiKeyEnv: ORNITH_API_KEY
      api: openai-completions
      baseURL: http://127.0.0.1:8081/v1
      models:
        - id: ornith-9b
          name: Ornith 9B uncensored
          contextWindow: 16384
          maxTokens: 4096
    ablit:
      displayName: Ablit Local (qwen27b MTP)
      apiKeyEnv: ORNITH_API_KEY
      api: openai-completions
      baseURL: http://127.0.0.1:8081/v1
      models:
        - id: qwen27b-ablit
          name: Qwen 27B abliterated
          contextWindow: 16384
          maxTokens: 4096
```
- `ORNITH_API_KEY` debe existir en el entorno (placeholder `local-no-key`; llama.cpp no la valida)
- `contextWindow` 16384: DSH envía system prompt largo (~11k tokens); 8192 NO alcanza
- `agent-default-model.provider` = ornith para que headless use el local

### 3. Uso
```bash
export ORNITH_API_KEY=local-no-key
python "$LOCALAPPDATA/hermes/scripts/model_manager.py" start ornith   # server :8080
python "$LOCALAPPDATA/hermes/scripts/ornith_proxy.py" --port 8081      # proxy :8081
cd "$LOCALAPPDATA/hermes/node" && dsh --profile headless "tu tarea"
```

## Cuándo usar qué (regla de decisión)
| Situación | Usar |
|---|---|
| Código abliterado, pentest, sin restricciones | Ornith (model_manager start ornith) |
| Razonamiento fuerte, tareas complejas normales | DSH con proveedor cloud (codex/deepseek) |
| Respuestas sin filtro, texto sensible | ablit (qwen27b) |
| Alternar: `model_manager.py start ablit|ornith` | Cambia el modelo en :8080 |

## Pitfalls
- **enable_thinking**: sin el proxy (o sin inyectar el flag) Ornith responde vacío.
- **Contexto**: DSH manda ~11k tokens de system prompt; 8192 falla con
  `CONTEXT_WINDOW_EXCEEDED`. Subir a 16384 en model_manager (`ctx`) y settings.
- **reasoningEffort**: NO declarar `reasoning: off` ni `reasoningEffort` para modelos
  hand-declared → error `UNSUPPORTED_REASONING_EFFORT`.
- **ORNITH_API_KEY**: pi-ai exige apiKeyEnv aunque el endpoint no valide key;
  cualquier placeholder funciona.
- **VRAM**: Ornith y ablit no corren a la vez (12GB). El watchdog los alterna.
- **dsh sessions zstd**: tras errores, las sesiones pueden quedar corruptas;
  borrar `~/.dsh/sessions/*` si DSH falla al releer.

## Verificación
- [ ] `curl http://127.0.0.1:8081/health` → {"status": "ok"}
- [ ] `dsh --profile headless "di OK"` → responde OK
- [ ] Sin proxy: `curl :8080` con thinking → content vacío; con proxy → content limpio
