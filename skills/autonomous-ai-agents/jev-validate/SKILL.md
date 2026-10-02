---
name: jev-validate
description: Use when validating agent output (after delegate_task or before self-reflect) with typed Jev Score primitives instead of a free-form LLM score.
---

# Jev Validate Output (typed, 4-dimension)

Part of the Jev evolution plan (SOUL.md §19 validate-output). Replaces the free-form LLM 0-10
score with four typed `Score` primitives: confidence, consistency, source_verification, format_compliance.

## When to use
- After `delegate_task` returns a result, before presenting it as fact.
- Before `self-reflect` final pass, to gate hallucination-prone outputs.
- Any time you need a deterministic, auditable validation signal rather than a vibe score.

## Core rules
- State = the result/text to validate (verbatim, no rephrasing).
- Policy (thresholds, verdict) lives in caller; this skill returns typed dims + suggested verdict.
- Offline-validate or mock by default; only `--live` costs money (TYPESAFE_API_KEY).

## Run
```bash
# MOCK (no network)
node "$LOCALAPPDATA/hermes/jev-client/validate-output.mjs" \
  --state "<resultado a validar>" --mock

# OFFLINE validation
node "$LOCALAPPDATA/hermes/jev-client/validate-output.mjs" --state "<resultado>"

# LIVE
TYPESAFE_API_KEY=... node "$LOCALAPPDATA/hermes/jev-client/validate-output.mjs" \
  --state "<resultado>" --live
```

## Output shape
```json
{
  "dims": { "confidence": 2, "consistency": 2, "source_verification": 2, "format_compliance": 2 },
  "verdict": "trust",   // trust (all>=2) | flag (any==1) | no_report (any==0)
  "model": "jev-1.13.0",
  "usage": { "input_tokens": 12, "output_tokens": 8 }
}
```

## Veredicto sugerido (caller decides)
- `trust` → publicar como hecho.
- `flag` → revisar antes de cerrar.
- `no_report` → no presentar como hecho (inventado/sin base).

## Improvement backlog
- [ ] Fan-out: validar + clasificar memoria en un solo call.
- [ ] Emit OMH brief with validation dims as evidence.
- [ ] Tune rubric per user red-flags (SOUL.md §19 regex).

## References
- Wrapper: `$LOCALAPPDATA/hermes/jev-client/validate-output.mjs` (verified mock+offline).
- Questions: `$LOCALAPPDATA/hermes/jev-client/validate-questions.json`.
- Helper: `decide.mjs` (Part 1). Base: `jev-decision`.
- Awesome Jev: C:/Users/<USER>/awesome-jev.
