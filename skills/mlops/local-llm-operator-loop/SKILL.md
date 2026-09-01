---
name: local-llm-operator-loop
description: "Operar LLM local (Ornith/ablit) como backend: cerebro→manos."
version: 1.0.0
author: Hermes curator
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [llm-local, ornith, ablit, cerebro-manos, autocorreccion, split, codigo]
    related_skills: [dsh-ornith-bridge, ornith-code-audit, vram-watchdog, local-gguf-deployment]
---

# Local LLM Operator Loop (cerebro→manos)

Clase de trabajo: usar un **modelo local abliterado** (Ornith-9B, ablit-27B) como
**cerebro generador de código**, mientras Hermes actúa de **manos**: ejecuta lo que
el modelo entrega, verifica, y si falla **devuelve el error al modelo para que él
se corrija** (loop de autocorrección).

## Cuándo usar
- El usuario pide código que el agente principal no debe escribir directo (pentest
  educativo, CTF, scripts abliterados) y hay un modelo local abliterado.
- El usuario estableció explícitamente: "Ornith piensa → tú ejecutas → no toques su código".
- Cualquier tarea de generación de código con un LLM local de respaldo.

## Reglas del flujo (aprobadas por Gio 2026-08-20)
1. **Ornith piensa, Hermes ejecuta** — nunca reescribir el código del modelo antes de ejecutar.
2. **Backup primero**: `cp script.py script.py.bak.ornith` antes de reemplazar.
3. **Ejecutar tal cual**: quitar solo el envoltorio markdown (```python ... ```), no tocar el cuerpo.
4. **Verificar con ejecución real**: py_compile + correr el script con args seguros.
5. **Si falla → devolver el error al modelo** en un segundo prompt ("tu código falla con
   NameError: ... — corrígelo y entrega la versión final"), NO corregir a mano.
6. **Reportar qué cambió** (diff resumido) — el usuario quiere saber qué hizo el modelo.

## Lecciones verificadas del modelo (Ornith-9B)
- Refactoriza bien: agrupa constantes, crea helpers (`_run`), usa excepciones específicas.
- **Omite imports al refactorizar** (ej: usa `urllib.request` sin importarlo) — el loop
  de feedback lo corrige solo. No asumir que la primera entrega compila.
- No responde prompts de jailbreak destructivo (malware, keyloggers) — tiene alineación
  de seguridad; sí da código ofensivo-educativo (escáneres, fuerza bruta SSH).

## Canales de consulta (cuál usar)
| Necesidad | Canal | Nota |
|---|---|---|
| Código corto/medio | curl directo al proxy (:8081) | Probado: 134-147 líneas válidas |
| Respuestas de texto cortas vía DSH | `dsh --profile headless "..."` | Funciona para "di OK" |
| **Código largo vía DSH headless** | ❌ NO | DSH espera tool-calls; Ornith corta ("Par"→"París") o EXIT=1 |
| Material >16k tokens | `ornith_split.py --summarize N` | map-reduce por partes |

## Split de prompts largos
Script: `$LOCALAPPDATA/hermes/scripts/ornith_split.py`
```bash
python .../ornith_split.py --file X.py --task "Optimiza" --split 3    # 1 mensaje, N partes
python .../ornith_split.py --file X.py --task "Resume" --summarize 2  # map-reduce
python .../ornith_split.py --file X.py --task "Reescribe" --stages 2  # contexto creciente
```
Verificado: el modo `--summarize` mantiene coherencia (análisis de 31 funciones con 2 partes).

## Límites del modelo (probado)
- Acepta prompts de 9000+ chars (el HTTP 400 puntual no fue por tamaño sino por contenido raro).
- `enable_thinking=false` es OBLIGATORIO (proxy lo inyecta) o responde vacío
  (gasta tokens en reasoning_content).

## Verificación
- [ ] Backup creado antes de reemplazar
- [ ] Código del modelo ejecutado tal cual (solo sin backticks)
- [ ] py_compile OK + ejecución real
- [ ] Si falló: error devuelto al modelo, segunda entrega verificada
- [ ] Diff resumido reportado al usuario
