---
name: rqgm-coevolution-pattern
description: "Use when tuning LLM judges or self-eval loops: RQGM pattern."
version: 1.0.0
author: Hermes (Gio)
license: internal
metadata:
  hermes:
    tags: [research, self-improvement, llm-judge, co-evolution]
    related_skills: [self-reflect, validate-output, hermes-self-evolution]
---

## When to Use
- Al usar o construir un LLM judge (self-reflect, validate-output, QA de outputs).
- Al modificar skills/prompts que se auto-evalúan (riesgo de reward hacking o scores incomparables).
- Al querer auto-mejora sin benchmark objetivo.
---

# Patrón RQGM: Co-evolución agente-evaluador

Fuente: paper completo en vault `90-Recursos/Papers/RQGM-Red-Queen-Godel-Machine.md` + PDF adjunto. arXiv 2606.26294 (Cambridge/NVIDIA, jun 2026).

## El patrón en 5 reglas
1. **Nunca confíes en un judge fijo para auto-mejora**: un evaluador estático se satura o se hackea (reward hacking, self-preference bias: LLM judges aceptan texto IA 1.42–1.91× más).
2. **Epochs + checkpoints**: congela el evaluador durante un período (garantías de estacionariedad), cámbialo solo en checkpoints exponenciales (base 2 → costo de transición lineal O(B)).
3. **Reemplazo solo por anchor**: el challenger reemplaza al incumbente SOLO si supera su ε-best-belief (cuantil 5% de la posterior Beta) en un dataset ground-truth fijo e independiente del evaluador.
4. **Selective erasure**: al cambiar de juez, borra los registros de calidad que dependían del juez viejo; mezclar scores de dos jueces corrompe la señal (control sin erasure: rankings se pegan al juez desplazado).
5. **Curriculum implícito**: jueces progresivamente más estrictos endurecen la población; conserva la lineage ganadora mientras re-rancas el resto.

## Aplicaciones en Hermes
- **self-reflect / validate-output**: correr muestras adversariales (outputs propios previamente aceptados por el judge) como test de leniencia; si acepta todo, recalibrar la rúbrica.
- **QA de outputs sin test objetivo** (escritura, análisis): usar judge de UNA llamada (1.35–1.72× más barato que evaluación multi-turno) con rúbrica criterion-bearing, no "¿está bien?".
- **Evolución de skills/cronjobs**: al modificar un prompt/skill que se auto-evalúa, invalidar métricas antiguas (erasure) en vez de acumular scores incomparables.
- **Juez calibrado**: preferir "accuracy con aceptación baja calibrada" sobre raw accuracy — un juez leniente da señal débil y hackeable.

## Reglas de judge evolucionadas por el propio paper (ejemplos listos para copiar)
- Reviewer adversarial: "aceptar solo si contribución no-trivial + metodología sólida + posicionamiento adecuado + claims soportados por evidencia; rechazar por validación faltante, poca novedad, gaps técnicos u overclaiming. No dejarse llevar por escritura fluida."
- Grader calibrado: "no bajar puntos por brevedad/compresión/teoremas citados de forma tersa; bajar a partial/incorrect solo por gap fatal o claim central falso sin reparación razonable."
- Code reviewer pragmático: "FAIL solo por blocker concreto visible en el diff; si la evidencia está equilibrada, PASS. No inventar blockers por falta de contexto del proyecto."

## Límites (no sobre-aplicar)
- Garantías solo por-epoch (sin convergencia global probada).
- El judge es tan bueno como su anchor: si el dataset de verdad es débil/biasado, drift.
- Preprint preliminar: GPT-5.5 low, horizontes cortos, dominios aislados.