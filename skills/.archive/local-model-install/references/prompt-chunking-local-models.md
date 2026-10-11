# Chunking de prompts para modelos con contexto limitado

Validado 2026-08-20 con Ornith-1.5-9B (16k ctx) vía proxy OpenAI-compatible.

## Cuándo
- El modelo local rechaza prompts largos (HTTP 400 / CONTEXT_WINDOW_EXCEEDED).
- Necesitas procesar archivos/código > ventana de contexto del modelo.
- El agente debe entregar un resultado completo sin truncar el material fuente.

## Diagnóstico primero (no asumas)
- Probar el límite real con request incremental: 1k, 3k, 6k, 9k chars.
  Muchos "límites" son puntuales (contenido específico rompió el JSON), no del tamaño.
- En Windows, backslashes en prompts JSON (`C:\Windows\Temp`) NO rompen si el JSON
  se serializa con `json.dumps` (escapado correcto). El fallo 400 puntual suele ser
  otra cosa (payload corrupto, carácter raro) — reintentar con prompt simplificado.

## Los 3 modos (script: `$LOCALAPPDATA/hermes/scripts/ornith_split.py`)
Requiere ornith_proxy.py en :8081 (o --url directo).

| Modo | Estrategia | Cuándo |
|------|-----------|--------|
| `--split N` | 1 mensaje con N partes marcadas `[PARTE i/N]` | Contexto alcanza, texto largo |
| `--summarize N` | Map-reduce: resumen por parte, luego síntesis final | Contexto NO alcanza |
| `--stages N` | Contexto creciente: instrucción + parte 1, + parte 2... | Necesitas razonar incremental |

```bash
python ornith_split.py --file big.py --task "Optimiza esto" --summarize 3
python ornith_split.py --file big.txt --task "Resume" --split 2
python ornith_split.py --file code.py --task "Reescribe" --stages 2
```

## Reglas de oro
- `--split`: todo en un mensaje — solo ayuda si la suma de partes + sistema cabe.
- `--summarize`: cada parte se resume con max_tokens acotado (~1500); la síntesis
  final recibe SOLO los resúmenes, nunca el texto completo.
- `--stages`: cada respuesta del modelo se reinyecta como assistant message para
  que el siguiente stage tenga contexto acumulado. Útil para "leer por capítulos".
- Verificar SIEMPRE el resultado: el chunking puede perder contexto entre partes
  (el modelo a veces no ve el final). Pedir conteos/verificaciones cruzadas.

## Trampas
- **Tiempo**: N llamadas = N × latencia del modelo (~10-30s c/u en 9B local).
  Correr en background con notify_on_complete.
- **max_tokens por etapa**: si el resumen es más corto que el contexto, se pierde
  detalle. Ajustar según la tarea (1500 para resumen, 4000 para análisis).
- **No mezclar**: si el modelo pierde el hilo en `--stages`, reiniciar la sesión.
