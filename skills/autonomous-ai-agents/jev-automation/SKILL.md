---
name: jev-automation
description: Use to wire Jev typed decisions into Hermes cron jobs and hooks (memory-consolidate, self-evolution gate, post-delegate validation) via the OpenRouter provider.
---

# Jev Automation (cron + hooks wired to Hermes)

Part of the Jev evolution plan. Wires the 5 typed wrappers into Hermes' existing automation
so decisions are auditable and cheap (~$0.000018/call via OpenRouter `~typesafe/jev-latest`).

## Scripts (all in $LOCALAPPDATA/hermes/jev-client/)
- `cron-memory-consolidate.mjs` — F1: 3am memory-consolidate + classify-memory
- `cron-self-evolution-gate.mjs` — F2: Sun 6am self-evolution + evolution-gate
- `hook-validate-output.mjs`       — F3: post-delegate_task validation (exit 2 = no_report)

## Cron registration (Hermes job spec)
```json
// F1 — memory-consolidate @ 3am
{ "name": "jev-memory-consolidate", "schedule": "0 3 * * *",
  "command": "node $LOCALAPPDATA/hermes/jev-client/cron-memory-consolidate.mjs --live",
  "env": { "OPENROUTER_API_KEY": "<from vault>" } }

// F2 — self-evolution gate @ Sun 6am
{ "name": "jev-self-evolution-gate", "schedule": "0 6 * * 0",
  "command": "node $LOCALAPPDATA/hermes/jev-client/cron-self-evolution-gate.mjs --live",
  "env": { "OPENROUTER_API_KEY": "<from vault>" } }
```

## Hook usage (F3)
After any `delegate_task` returns `result`:
```bash
echo "$RESULT" | node "$LOCALAPPDATA/hermes/jev-client/hook-validate-output.mjs" --live
# exit 0 → presentable (trust/flag); exit 2 → do NOT present as fact, re-run or disclose
```

## Core rules
- Provider default: openrouter (uses OPENROUTER_API_KEY). TypeSafe direct needs TYPESAFE_API_KEY.
- All scripts support `--dry` (no network) and `--mock` (synthetic) for testing.
- Jev is a SIGNAL, not a security boundary (AGENTS.md). The cron/hook caller enforces the action.
- Log `model` from each response for eval traceability (alias can move).

## Verification done
- All 3 scripts: dry-run OK (no cost).
- Live smoke (separate session): 5 wrappers return typed answers via OpenRouter.

## Improvement backlog
- [ ] F4: intent-router pre-turn hook (classify incoming msg).
- [ ] F5: correction-triage auto-persist to gbrain.
- [ ] F6: fan-out batch (intent+validate+gate+classify in one SystemOne call).

## References
- Wrappers: decide.mjs, classify-memory.mjs, validate-output.mjs, evolution-gate.mjs, triage-correction.mjs
- Skills: jev-decision, intent-router, memory-classifier, jev-validate, evolution-gate, correction-triage
- Awesome Jev: C:/Users/<USER>/awesome-jev
