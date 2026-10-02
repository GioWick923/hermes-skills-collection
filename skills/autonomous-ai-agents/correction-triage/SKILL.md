---
name: correction-triage
description: Use after the user corrects your work to classify the correction (preference/fact/behavior/bug) via a typed Jev decision and route it to the right memory destination.
---

# Correction Triage (typed, Jev-backed)

Final part of the Jev evolution plan (SOUL.md §20.3). After any user correction, classify it
so the pattern is persisted to the right memory store — not lost or mis-filed.

## When to use
- Immediately after the user says "no, así no", "cambia esto", "por qué hiciste X" (correction).
- To decide: user_profile vs gbrain(learned/decided) vs EVOLUTION.md+issue.

## Core rules
- State = the user's correction verbatim (or close paraphrase).
- One atomic choice (type) + two noul (repeat offense, durable). Policy in caller.
- Offline-validate or mock by default; only `--live` costs money (TYPESAFE_API_KEY).

## Run
```bash
# MOCK (no network)
node "$LOCALAPPDATA/hermes/jev-client/triage-correction.mjs" \
  --state "<corrección del usuario>" --mock

# OFFLINE validation
node "$LOCALAPPDATA/hermes/jev-client/triage-correction.mjs" --state "<corrección>"

# LIVE
TYPESAFE_API_KEY=... node "$LOCALAPPDATA/hermes/jev-client/triage-correction.mjs" \
  --state "<corrección>" --live
```

## Output shape
```json
{
  "type": "preference",
  "repeat_offense_prob": 0.5,
  "durable_prob": 0.5,
  "destination": "user_profile_or_gbrain_preference",
  "persist": false,
  "model": "jev-1.13.0",
  "usage": { "input_tokens": 9, "output_tokens": 5 }
}
```

## Destination map (caller persists)
- `preference` → user profile (memory) or gbrain category `preference`
- `fact`       → gbrain `learned` (epistemic: fact)
- `behavior`   → gbrain `decided` (behavior rule)
- `bug`        → EVOLUTION.md + issue; persist only if pattern repeats

## Loop closure
This completes the 5-evolution Jev plan (intent-router, memory-classifier, jev-validate,
evolution-gate, correction-triage). All share `decide.mjs` (one helper, minimal code).

## Improvement backlog
- [ ] Fan-out: triage + validate + classify in one SystemOne call.
- [ ] Emit OMH brief with correction evidence.
- [ ] Auto-persist to gbrain when `persist: true` (wire to observational-memory).

## References
- Wrapper: `$LOCALAPPDATA/hermes/jev-client/triage-correction.mjs` (verified mock+offline).
- Questions: `$LOCALAPPDATA/hermes/jev-client/triage-questions.json`.
- Helper: `decide.mjs` (Part 1). Base: `jev-decision`.
- Awesome Jev: C:/Users/<USER>/awesome-jev.
