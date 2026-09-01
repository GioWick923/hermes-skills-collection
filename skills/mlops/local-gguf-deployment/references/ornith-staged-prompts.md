# Prompts largos a modelos locales (Ornith/Qwen3.5) — staged processing

## Diagnóstico (2026-08-21, verificado)
- Modelos Qwen3.5/Ornith en llama.cpp :8080 (vía ornith_proxy :8081) aceptan
  prompts de **hasta ~9k+ caracteres** sin problema (probado: 1000/3000/6000/9000 chars OK).
- El error HTTP 400 puntual NO es por tamaño: fue contenido específico del prompt.
  Probar con un prompt simplificado antes de asumir límite.
- Límite real de contexto del modelo: ~16k tokens (DSH envía ~11k de system prompt).

## Script: ornith_split.py (hermes/scripts/)
Envía prompts largos por etapas sin romper el prompt original. Tres modos:

```bash
python hermes/scripts/ornith_split.py --file archivo.py --task "Optimiza" --split 3
python hermes/scripts/ornith_split.py --file archivo.txt --task "Resume" --summarize 2
python hermes/scripts/ornith_split.py --file big.py --task "Reescribe" --stages 2
```

| Modo | Cómo funciona | Cuándo |
|------|--------------|--------|
| `--split N` | Divide en N partes, las envía en 1 mensaje marcadas `[PARTE i/N]` | Texto grande que cabe en 1 request |
| `--summarize N` | Map-reduce: resumen de cada parte + síntesis final | Texto enorme (>16k tokens) |
| `--stages N` | Contexto creciente: instrucción + parte 1, + parte 2... | Mantener el hilo conversacional |

## Regla de trabajo con Ornith (corrección del usuario 2026-08-21)
- **Ornith piensa → Hermes ejecuta → si falla, devolver el error a Ornith** (NO tocar su código).
- Backup antes de reemplazar: `archivo.py.bak.ornith`.
- Ornith refactoriza bien (helpers, constantes) pero a veces omite imports — el loop
  de feedback (devolverle el NameError/error) lo corrige solo.
- Si DSH headless corta respuestas largas de Ornith ("Par" en vez de "París" + EXIT=1):
  usar el proxy directo (curl :8081) para código largo, o `--summarize/--stages`.
