---
name: jev-evolution-loop
description: Use to keep Jev integrations in Hermes evolving automatically — fan-out, pre-turn intent, auto-persist triage, terminal gate, weekly dashboard, research-verify, and a policy to improve when needed.
---

# Jev Evolution Loop (automejora continua)

Todas las mejoras de Jev en Hermes, cableadas y con política de evolución. Base: `decide.mjs`
(una sola función `decide()` + `decideBatch()` fan-out). Proveedor default openrouter
(`typesafe/jev-1.13`), key `OPENROUTER_API_KEY`.

## Componentes (en $LOCALAPPDATA/hermes/jev-client/)
| Script | Rol | Cuándo |
|--------|-----|-------|
| `decide.mjs` | core + `decideBatch` (fan-out 1 llamada N jueces) | siempre |
| `hook-intent-pre-turn.mjs` | F4: clasifica msg usuario → route_hint | inicio de turno |
| `triage-correction.mjs --persist` | F5: corrige→clasifica→escribe a Obsidian | tras corrección usuario |
| `gate-terminal.mjs` | gate rm/del/git push --force (exit 2=BLOCK) | antes de comando destructivo |
| `hook-validate-output.mjs` | F3: validate post-delegate (exit 2=no_report) | tras delegate_task |
| `hook-research-verify.mjs` | verify claims investigación (exit 2=no citar) | tras deep-research |
| `cron-memory-consolidate.mjs` | F1: 3am facts→classify→gbrain | cron 3am |
| `cron-self-evolution-gate.mjs` | F2: dom 6am patch→gate→apply/block | cron dom 6am |
| `cron-jev-dashboard.mjs` | dashboard semanal de veredictos | cron dom 6am |

## Política de evolución (SOUL.md §15/§20.3/§20.7)
1. **Mejora cuando haga falta, no por rutina.** Si un juez falla o el usuario corrige,
   registrar patrón en Obsidian (`correction-triage --persist`) y proponer patch al script.
2. **Código mínimo.** Todo reusa `decide()`/`decideBatch()`. No duplicar lógica de red.
3. **Offline-first.** Dry-run/mock en cada cambio; live solo con opt-in + key.
4. **Jev es señal, no frontera.** El caller (cron/hook) decide la acción final.
5. **Trazabilidad.** Log `model` + `usage.cost` en cada llamada para el dashboard.

## Fan-out (ahorro)
`decideBatch({ state, groups: { intent: intentQ, validate: validateQ }, live })` →
1 llamada en vez de 2. Usar en hooks que necesiten 2+ jueces.

## Cron spec (Hermes)
```json
{ "name":"jev-3am-consolidate", "schedule":"0 3 * * *", "command":"node $LOCALAPPDATA/hermes/jev-client/cron-memory-consolidate.mjs --live" }
{ "name":"jev-sun-gate", "schedule":"0 6 * * 0", "command":"node $LOCALAPPDATA/hermes/jev-client/cron-self-evolution-gate.mjs --live" }
{ "name":"jev-sun-dashboard", "schedule":"5 6 * * 0", "command":"node $LOCALAPPDATA/hermes/jev-client/cron-jev-dashboard.mjs --log @$LOCALAPPDATA/hermes/jev-client/verdicts.jsonl" }
```

## Verification done
- `decideBatch` mock: OK (2 jueces, 1 llamada).
- Todos los scripts: dry-run OK.
- Live de componentes base: verify en sesión previa (~$0.00002/llamada).

## Backlog (siguiente evolución)
- [ ] Usar decideBatch en hook-intent-pre-turn + validate juntos (ahorro real).
- [ ] gbrain sync (requiere git init en vault).
- [ ] Auto-proponer patch a script cuando triage persiste 3+ correcciones iguales.

## References
- Skills: jev-decision, intent-router, memory-classifier, jev-validate, evolution-gate, correction-triage, jev-automation.
- Vault notas: Memorias/Agente/2026-09-19-233742-* (decision), 2026-09-19-233758-* (learning).
- Awesome Jev: C:/Users/<USER>/awesome-jev.
