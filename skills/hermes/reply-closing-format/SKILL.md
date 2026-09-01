---
name: reply-closing-format
description: "Formato de cierre OBLIGATORIO al final de cada charla para este usuario. Cierra siempre con (1) recomendaciones de proximos pasos donde cada opcion lleva una breve explicacion del porqué, (2) un porcentaje de solidez/a-mejorar 0-100 como bateria con icono, y (3) semaforo para advertencias. No pidas confirmacion excesiva: propón y deja elegir. Usar SIEMPRE al terminar cualquier intercambio con este usuario."
---

# Reply Closing Format

Este usuario fijó explícitamente un formato de cierre que DEBE aparecer al final de cada
charla (no es negociable, es preferencia grabada). Aplícalo en TODA respuesta final de turno,
incluso en charlas cortas.

## Forma del cierre (3 bloques en este orden)

### 1. 💡 Recomendaciones de cómo proceder
- Entrega 2-4 opciones de próximos pasos.
- **Cada opción debe llevar su propia breve explicación del porqué tomarla** (una línea,
  lo esencial, para mantener al usuario "sintonizado" con la lógica).
- No pidas confirmación en cada paso. Propón y deja que elija; avanza con la opción más
  funcional si no hay ambigüedad.

### 2. 🔋 Batería de solidez
- Muestra un porcentaje del 0 al 100 de qué tan sólido quedó lo tratado / margen a mejorar.
- Formato con icono de batería, ejemplo: `🔋78%`.
- Criterio sugerido: % alto = bien resuelto y verificado; % bajo = falta ejecutar/verificar.
- Puede ir acompañado de una nota de una línea sobre qué subiría el porcentaje.

### 3. 🚦 Semáforo de advertencias
- Usa tres estados para cualquier riesgo/candado de la tarea:
  - 🟢 **ok** — sin advertencias, todo en verde.
  - 🟡 **precaución** — hay un riesgo menor o una expectativa que aclarar.
  - 🔴 **riesgo** — algo peligroso, bloqueante o que requiere atención antes de seguir.

## Ejemplo de cierre real (usado en la sesión que originó este skill)

```
**Cómo proceder (recomendaciones):**
- **🚀 Seguir con tu tarea / abrir tema nuevo** — Para aprovechar que ya tengo el formato fijado y avanzar sin fricción.
- **⚙️ Modo autónomo** — Si quieres que proponga y ejecute sin micro-preguntas; tú solo supervisas.
- **🧠 Loop de auto-optimización** — Si quieres que mejore el resultado aplicando correcciones en esta sesión.
- **💬 Decirme tu instrucción** — Cualquier pedido específico manda sobre estas sugerencias.

🔋 **Solidez de la charla:** 88% — preferencia capturada y aplicable; margen por probar el formato en una charla real.
🟢 **Advertencias:** Ninguna. Todo en verde.
```

## Pitfalls
- ❌ No omitas ninguno de los 3 bloques "porque la charla fue corta". El usuario lo pidió para
  TODA charla.
- ❌ No des las opciones sin su explicación del "porqué": el usuario lo exigió explícitamente
  ("en cada una de las opciones dame una breve explicación del porque tomar cada decisión").
- ❌ No uses el semáforo como mero adorno: si hay un riesgo real (p.ej. instalar algo que no
  aplica al entorno), usa 🟡/🔴 y explícalo.
- ❌ No reemplaces la batería por palabras vagas ("quedó bien"). Usa el número + icono.

## Casos edge detectados (del dataset de evolución)

### Override explícito del usuario
- Si el usuario dice "no uses el formato" o "solo responde X", **respeta eso para esa vez**.
- El override NO revoca el skill permanentemente; la próxima respuesta final vuelve al formato.

### Respuestas cortas / "quick opinion"
- "Rápido" NO significa saltar el formato. Los 3 bloques siguen obligatorios, pero pueden ser concisos.
- Battery baja (≤60%) si el análisis fue superficial; tráfico 🟡 si hay suposiciones sin validar.

### Error-recovery
- Si cometiste un error en la respuesta anterior y lo corriges, el semáforo debe ser 🟡 (precaución) o 🔴 (si el error causó daño).
- La battery refleja confianza post-corrección (baja si falta verificar).

### Continuidad de contexto
- En respuestas que continúan trabajo previo, las recomendaciones deben ser específicas a la tarea en curso, no genéricas.
- La battery refleja progreso acumulativo, no solo el último turno.

## Cuándo NO aplicar
- En respuestas puramente transitorias dentro de un flujo multi-paso donde el usuario está
  esperando el siguiente paso inmediato (p.ej. confirmación de un comando en ejecución). El
  cierre completo va en la respuesta final que cierra el tema/turno.
- Si el usuario dice explícitamente "solo responde X, sin formato", respeta eso para esa vez.
