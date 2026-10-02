---
name: evolution-gate
description: Use before applying a hermes-self-evolution patch (skill/prompt change) to get a typed Jev risk gate (safe/neutral/risky + breaks-tests + reversible).
---

# Evolution Gate (typed, Jev-backed)

Part of the Jev evolution plan (SOUL.md §15 self-evolution + §20.7 no-temporary-fixes).
Before applying any self-evolution patch, get a typed risk signal instead of guessing.

## When to use
- In the self-evolution cron (Sun 06:00) or any manual skill/prompt edit: gate the change first.
- When a proposed patch deletes, overwrites, widens permissions, or changes core behavior.

## Core rules
- State = the diff or description of the change (verbatim).
- This skill returns a typed gate; the CALLER enforces it (never trust the model as a security boundary — AGENTS.md).
- Offline-validate or mock by default; only `--live` costs money (TYPESAFE_API_KEY).

## Run
```bash
# MOCK (no network)
node "$LOCALAPPDATA/hermes/jev-client/evolution-gate.mjs" \
  --state "<diff o descripción del cambio>" --mock

# OFFLINE validation
node "$LOCALAPPDATA/hermes/jev-client/evolution-gate.mjs" --state "<cambio>"

# LIVE
TYPESAFE_API_KEY=... node "$LOCALAPPDATA/hermes/jev-client/evolution-gate.mjs" \
  --state "<cambio>" --live
```

## Output shape
```json
{
  "risk": 1,
  "breaks_tests_prob": 0.5,
  "reversible_prob": 0.5,
  "gate": "REVIEW",   // AUTO (risk0+rev) | REVIEW (risk1) | BLOCK (risk>=2 or breaks>0.5)
  "model": "jev-1.13.0",
  "usage": { "input_tokens": 10, "output_tokens": 6 }
}
```

## Gate policy (caller enforces)
- `AUTO` → aplica sin fricción.
- `REVIEW` → aplica pero registra en EVOLUTION.md + avisa al usuario.
- `BLOCK` → requiere validación humana o tests verdes antes de aplicar.

## Improvement backlog
- [ ] Fan-out: gate + validate + classify en un solo call.
- [ ] Emit OMH brief with gate evidence.
- [ ] Learn from blocks (feed intent-router triage).

## References
- Wrapper: `$LOCALAPPDATA/hermes/jev-client/evolution-gate.mjs` (verified mock+offline).
- Questions: `$LOCALAPPDATA/hermes/jev-client/evolution-gate-questions.json`.
- Helper: `decide.mjs` (Part 1). Base: `jev-decision`.
- Awesome Jev: C:/Users/<USER>/awesome-jev.
