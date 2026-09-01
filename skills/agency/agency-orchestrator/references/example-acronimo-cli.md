# Ejemplo end-to-end verificado — acronimo-cli

Pipeline real ejecutado para probar el orquestador. Fase 1 completa y verificada
en disco; Fases 2-4 siguen el mismo patrón de cierre de loop.

## Workspace
`C:\Users\<USER> GAMES\agency-test\`

## Fase 1 — Architect (`delegate_task`, toolsets=['terminal','file'])
- Goal: diseñar `PLAN.md` (requisitos + contrato CLI + ADR stdlib-only) para una
  CLI que genera acrónimos (`'Hermes Agent Rules' -> 'HAR'`), sin implementar.
- Entregó: `PLAN.md` (128 líneas), `STRUCTURE.md`, stubs `main.py` +
  `tests/test_cli.py`.
- **Pitfall real**: `write_file` del hijo resolvió ruta `C:\c\Users\...` (root
  duplicado MSYS). El subagente lo detectó con `ls`, reubicó y confirmó.
- **Verificación del padre (no confiar en el resumen)**:
  `find . -type f` y `wc -l PLAN.md` -> 128 líneas, archivos presentes.

## Fase 2 — Dev (senior-developer)
- Goal: implementar `acronym/core.py` (`build_acronym` pura), `main.py`
  (argparse+sys), `tests/test_cli.py` (unittest).
- Discipline: marcar completo solo si `python main.py "Hermes Agent Rules"`
  imprime `HAR\n` Y `python -m unittest tests.test_cli -v` está en verde.
- El subagente debe auto-ejecutar la verificación y reportar la salida real.

## Fase 3 — QA (test-automation)
- Validación **independiente** de los tests del dev (no reusar su salida).
- Determinista, sin sleeps; aislar datos; reportar PASS/FAIL con evidencia.

## Fase 4 — Reality Check (reality-checker)
- Certificar con evidencia abrumadora (salida real de unittest, no afirmación).
- Por defecto `NEEDS WORK` salvo evidencia.

## Template PIPELINE.md (estado entre fases)
```
# Estado de Pipeline — <proyecto>
Fase: [Plan/DevQA/Integración/Completo]
Tareas: total X | hechas Y | actual Z
Dev-QA: intento N/3 | último feedback: "..."
Siguiente: [spawn dev / spawn qa / avanzar / escalar]
```
