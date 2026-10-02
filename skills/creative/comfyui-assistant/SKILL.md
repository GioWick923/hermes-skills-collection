---
name: comfyui-assistant
description: "Use for any ComfyUI talk: assistant panel, KB, config."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
---

# ComfyUI Assistant (BobbtheBuilder) — adoptado 2026-09-14

## When to Use

- Cualquier tarea que toque ComfyUI en este stack: generar/editar workflows, instalar
  nodos, diagnosticar el panel flotante, cambiar su LLM provider o actualizar el repo.
- Cuando el usuario mencione el "asistente de ComfyUI", la burbuja flotante o pida
  construir/editar workflows conversando.
- Companion de la skill `comfyui` (esa cubre comfy-cli + REST puro; esta cubre el
  asistente embebido instalado).

## Qué es y dónde vive

Chat flotante dentro del editor de ComfyUI: lee/edita el workflow activo (añadir/
quitar/conectar nodos, set_prompt, auto-arrange, validación con auto-fix), ve imágenes
de entrada/salida, busca en una KB local de docs y recuerda correcciones entre sesiones.

- **Instalación:** `F:\ComfyUI\custom_nodes\ComfyUI_Assistant` (git clone, rama main,
  v0.2.0+). NO confundir con `C:\Users\<USER>\Documents\comfy\ComfyUI` (carcasa vacía).
- **Config:** `chatbot_config.json` en la carpeta del nodo (mergea sobre DEFAULTS de
  `config_store.py`). Escribirla AHÍ pre-configura sin tocar la UI.
- **Provider actual:** Ollama `http://127.0.0.1:11434/v1` con
  `hf.co/noctrex/Huihui-Qwen3-VL-8B-Instruct-abliterated-GGUF:Q6_K` (visión + native
  tool-calls, verificado con request real 2026-09-14).
- **Repo:** https://github.com/BobbtheBuilder/ComfyUI_Assistant (MIT, LM Studio es el
  provider más testeado upstream; Ollama funciona aquí).

## Endpoints verificados (todos bajo http://127.0.0.1:8188)

| Endpoint | Uso |
|---|---|
| `GET /chatbot/config` | config resuelta (sin secretos) — smoke test de que el nodo cargó |
| `POST /chatbot/chat` | chat streaming NDJSON `{messages, tools}` → eventos `{type: tool_call\|delta\|done\|error}` |
| `POST /chatbot/models` | lista modelos del provider configurado |
| `GET /chatbot/kb/status` | estado KB (`Ready` = ok; chunks/files/official) |
| `POST /chatbot/kb/rebuild` | reconstruir KB local |

UI: `web/chatbot.js` se sirve en `/extensions/ComfyUI_Assistant/chatbot.js`; monta
`#ccb-root` (burbuja arrastrable, settings, sesiones por workflow). KB del 2026-09-14:
18,548 chunks / 149 archivos, docs oficiales incluidos.

## Pitfalls verificados (2026-09-14)

- **Bug de rutas en terminal Hermes**: git/curl NO reciben traducción MSYS — `/f/...`
  se interpretó como `C:\f\` literal (creó basura en C:). Usar rutas nativas
  `C:/...`/`F:/...` para binarios nativos, o PowerShell.
- **Doble proceso python de ComfyUI** (launcher + hijo dueño del puerto) es NORMAL en
  esta versión (0.33): no matar el "duplicado" sin ver `netstat -ano | grep 8188` y el
  ParentProcessId.
- **Ollama crashea transitoriamente** (`llama-server exit status 1`, HTTP 500 del
  provider) si choca con la carga fría del modelo — reintentar; no es bug del plugin.
- **Lanzar ComfyUI desde Hermes**: `Start-Process` con `-RedirectStandard*` deja
  handles abiertos → timeout del tool call aunque el server arranque bien. Verificar
  con `curl /system_stats` en llamada aparte, no esperar el exit del comando.
- **Gateway keys de LLM**: tokenharbor.ai, experientiallabs, orcarouter y la OpenRouter
  del config.yaml daban 401 al 2026-09-14. Si se quiere quitar Ollama del asistente,
  probar la key REAL del provider activo antes de escribir la config.

## Verificación reproducible (smoke, 30s)

```bash
# 1. nodo cargado
curl -s http://127.0.0.1:8188/chatbot/config | head -c 200
# 2. provider vivo (lista modelos de Ollama)
curl -s -X POST http://127.0.0.1:8188/chatbot/models -d '{}'
# 3. chat end-to-end (streaming NDJSON, ver evento tool_call)
curl -s -N -X POST http://127.0.0.1:8188/chatbot/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"hi"}]}'
# 4. KB
curl -s http://127.0.0.1:8188/chatbot/kb/status
```

## Regla de oro

Para construir/editar workflows conversando → el asistente vive DENTRO de la UI de
ComfyUI (burbuja). Para ejecución headless/batch desde Hermes → skill `comfyui`
(comfy-cli + run_workflow.py). No duplicar: no re-implementar edición de grafos vía
REST cuando el usuario puede pedirlo al asistente en pantalla.
