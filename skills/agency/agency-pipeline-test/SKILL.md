---
name: agency-pipeline-test
description: "Cómo ejecutar y verificar el orquestador multiagente Agency (agency-orchestrator) en un proyecto real pequeño, de extremo a extremo, con evidencia en disco. Usar cuando se quiera probar el equipo Agency o cualquier pipeline de delegate_task."
platforms: [linux, macos, windows]
category: agency
---

# Probar el pipeline Agency (orquestador → dev → QA → reality-check)

Plantilla de prueba de humo para validar que el pack `agency-*` funciona de
verdad (no solo que carga). El proyecto de ejemplo es una CLI Python que genera
acrónimos (`'Hermes Agent Rules' -> 'HAR'`), stdlib-only, verificable.

## Por qué esta prueba
El skill `agency-orchestrator` resuelve por `name`, no por ruta. Cargar con
`skill_view` no prueba comportamiento. Esta receta corre el pipeline completo
con subagentes aislados y exige evidencia real en cada gate.

## Pasos

1. **Workspace**: crear `/c/Users/<USER> GAMES/agency-test/` (Windows MSYS:
   `/c/Users/<user>/...`). El orquestador es el agente padre; no hace polling.

2. **Fase 1 — Architect** (`delegate_task`, toolsets `['terminal','file']`):
   goal = diseñar `PLAN.md` (requisitos + contrato CLI + ADR stdlib-only) y
   esquema de archivos. NO implementar código, solo especificación + stubs.

3. **Verificar en disco** (el orquestador, no el subagente): `find . -name '*.py'`
   y `wc -l PLAN.md`. El bug conocido: `write_file` a veces resuelve ruta
   duplicada `C:\c\Users\...`; el subagente la corrige solo, pero confirmar con
   `ls "C:/c/Users/..."` que NO queda duplicado.

4. **Fase 2 — Senior Developer** (`delegate_task`, `['terminal','file']`):
   implementa `acronym/core.py` (función pura `build_acronym`), `main.py` (CLI
   argparse + stdin), `tests/test_cli.py` (unittest). Debe auto-verificar:
   `python -m unittest tests.test_cli -v` y reportar salida real.

5. **Verificar en disco** de nuevo: ejecutar la CLI y la suite UNO MISMO en
   terminal. No confiar en el resumen del subagente (principio del orquestador).

6. **Fase 3 — Test Automation** (`delegate_task`, `['terminal','file']`):
   QA INDEPENDIENTE. Agrega tests de `--version`/`--h`, corre 2 veces para
   anti-flake (determinismo). Veredicto PASS/FAIL con salida real.

7. **Fase 4 — Reality Checker** (`delegate_task`, `['terminal','file']`):
   re-verifica CADA caso del PLAN contra salida real, stdlib-only (grep imports),
   y certifica `PRODUCTION READY` o `NEEDS WORK`. Por defecto NEEDS WORK.

## Cierres de loop (reglas del orquestador)
- Cada fase es subagente aislado, contexto explícito, UN entregable verificable.
- Evidencia requerida (archivos/urls/status/logs), nunca "lo hice".
- Máx 3 reintentos por tarea antes de escalar.
- Avanza solo si QA = PASS.

## Verificación final esperada (proyecto acronimo)
- 7 casos CLI OK: HAR, multi-espacio, ÑAR (Unicode), vacío exit1, --version, -h, ### exit1.
- Suite: `Ran 12 tests ... OK`.
- Imports: solo `argparse, sys, re, unittest, io, contextlib, unittest.mock`.

## Pitfalls
- `write_file` en subagentes Windows puede crear `C:\c\Users\...` duplicado:
  verificar y limpiar. No es fallo del skill, es del resolver de rutas.
- El "file-mutation verifier" del runner a veces da falso positivo si el
  subagente tocó la ruta duplicada primero; confirmar con `find`/`wc` reales.
- NO usar `pytest` en este pack (los skills piden unittest stdlib).
