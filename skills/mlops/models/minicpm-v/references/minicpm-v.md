# MiniCPM-V — Reference rápida

## Repo oficial
https://github.com/OpenBMB/MiniCPM-V

## Descripción corta
MiniCPM-V es una familia de modelos multimodales open source enfocada en comprensión eficiente de **imagen, multi-imagen y video**, con despliegue orientado a dispositivos y escenarios de bajo costo computacional.

## Datos verificados del repo
- Repositorio: `OpenBMB/MiniCPM-V`
- Branch por defecto: `main`
- Licencia: `Apache-2.0`
- Estrellas: ~25.8k
- Forks: ~2.0k
- Última actualización visible vía API: `2026-07-11T23:44:26Z`
- Descripción del repo: `A Pocket-Sized MLLM for Ultra-Efficient Image and Video Understanding on Your Phone`

## Qué destaca
- MiniCPM-V 4.6: 1.3B parámetros.
- Enfoque en eficiencia de inferencia y despliegue edge/mobile.
- Soporte para Transformers y también adaptaciones hacia vLLM, llama.cpp, Ollama, SWIFT y LLaMA-Factory.
- El README menciona despliegue en iOS, Android y HarmonyOS.
- Hay demos y cookbook/documentación asociada.

## Cuándo vale la pena en Hermes
- Investigación de modelos de visión eficientes.
- Comparativas de VLMs para uso práctico.
- Integraciones donde importa latencia/costo más que tamaño bruto.
- Casos de OCR visual, comprensión de escenas, video corto, y asistentes visuales.

## Riesgos / limitaciones
- La compatibilidad exacta con frameworks y versiones cambia rápido.
- Algunas rutas de video dependen de paquetes como `torchcodec` o alternativas como `PyAV`.
- No asumir que un benchmark aislado garantiza mejor rendimiento en tu caso real.

## Recomendación de adopción
1. Probar en `researcher` para comparar con alternativas.
2. Validar en `builder` con un ejemplo mínimo.
3. Revisar en `reviewer` costo/latencia/riesgo.
4. Documentar la decisión final en `writer`.
