---
category: mlops
name: minicpm-v
description: "Integrate and use OpenBMB MiniCPM-V for efficient image/video understanding in Hermes workflows."
---

# MiniCPM-V

Usa esta skill cuando necesites trabajar con el repositorio y modelos **OpenBMB/MiniCPM-V** para visión multimodal eficiente: imagen, video, OCR visual, explicación de escenas y despliegue edge/mobile.

## Qué es
MiniCPM-V es una familia MLLM open source enfocada en comprensión eficiente de imagen y video. La línea actual destacada es **MiniCPM-V 4.6**, con énfasis en:
- bajo costo computacional,
- buena eficiencia en dispositivos,
- soporte para imagen, multi-imagen y video,
- despliegue en plataformas edge/móvil,
- formatos y frameworks comunes (Transformers, vLLM, llama.cpp, Ollama, SWIFT, LLaMA-Factory).

Repo oficial: https://github.com/OpenBMB/MiniCPM-V

## Cuándo usarla
- Cuando el usuario necesita un modelo de visión ligero y práctico.
- Cuando hay que decidir si MiniCPM-V encaja mejor que un VLM más grande.
- Cuando se quiere resumir, anotar o integrar el repo en la arquitectura Hermes.
- Cuando haya que comparar MiniCPM-V con otras opciones como Qwen-VL, LLaVA, Gemma multimodal, etc.
- Cuando el objetivo sea correr visión en hardware más modesto o en mobile/edge.

## Cuándo no usarla
- Si el problema es puramente textual.
- Si se necesita máxima investigación académica sin enfoque de despliegue.
- Si no hay intención de usar visión/video/OCR de forma recurrente.
- Si el usuario pidió solo una respuesta breve y no necesita integración.

## Señales clave del repo
Verifica en el repo oficial antes de afirmar detalles que cambian con el tiempo:
- licencia,
- versión destacada,
- compatibilidad con frameworks,
- demos,
- cuantización,
- soporte para móvil,
- noticias/releases.

## Recomendación de uso dentro de Hermes
- `researcher`: para comparar MiniCPM-V contra alternativas y extraer ventajas/desventajas.
- `builder`: para integrar ejemplos, scripts, demos o pipelines.
- `reviewer`: para revisar compatibilidad, costos, riesgos y claims.
- `writer`: para documentar la decisión en tablas claras.
- `orchestrator`: para decidir si vale la pena adoptarlo como estándar de visión ligera.

## Formato de salida preferido
Cuando uses esta skill, entrega:
1. Resumen corto.
2. Tabla de compatibilidad/casos de uso.
3. Pros y contras.
4. Recomendación para Hermes.
5. Próximo paso accionable.

## Regla práctica
Si la solución necesita visión y debe ser eficiente, MiniCPM-V es una de las primeras opciones a evaluar.
