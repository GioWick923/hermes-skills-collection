# colibri — Reference rápida

## Repo oficial
https://github.com/JustVugg/colibri

## Resumen corto
Colibrì es un motor de inferencia escrito en C para ejecutar **GLM-5.2 (744B MoE)** en hardware de consumo mediante streaming de expertos desde disco.

## Datos verificados del repo
- Repositorio: `JustVugg/colibri`
- Branch por defecto: `main`
- Licencia: `Apache-2.0`
- Estrellas: ~4.0k
- Forks: ~339
- Open issues: ~20
- Idioma principal: C
- Descripción del repo: `Run GLM-5.2 (744B MoE) on a 25GB-RAM consumer machine — pure C, zero deps, experts streamed from disk. Tiny engine, immense model.`

## Lo más importante
- Runtime en C puro, sin dependencias en ejecución.
- Enfoque en memoria reducida a costa de I/O intenso.
- Arquitectura muy especializada para MoE grande.
- Incluye servidor OpenAI-compatible, KV persistence, grammar drafts, MTP speculative decoding y rutas experimentales CUDA.

## Señales de adopción
Útil como referencia si quieres estudiar:
- streaming de expertos desde disco,
- cuantización int4/int8/int2,
- planificación de memoria,
- modelos MoE gigantes en hardware limitado,
- backend local privado sin Python runtime.

## Riesgos / límites
- Muy pesado en disco.
- Latencia fría puede ser alta.
- Es un proyecto experimental, no un backend simple.
- No es la mejor opción si buscas facilidad de mantenimiento.

## Recomendación para Hermes
Tratarlo como **referencia de investigación** y posible backend opcional, no como dependencia principal.

## Flujo recomendado
1. `researcher` para evaluar viabilidad.
2. `builder` para probar integración o API.
3. `reviewer` para riesgo/costo/mantenibilidad.
4. `orchestrator` para decidir si se adopta o solo se documenta.
