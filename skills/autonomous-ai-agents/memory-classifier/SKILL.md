---
name: memory-classifier
description: Use when consolidating memory facts at night or after a session, to tag each fact with a typed Jev category/epistemic/importance before storing.
---

# Memory Classifier (typed, Jev-backed)

Part of the Jev evolution plan (SOUL.md §19 / §21.2). Tags memory facts with typed decisions
so `memory-consolidate` output is structured, not free-form.

## When to use
- In the nightly `memory-consolidate` cron (3am) or after a session: classify each extracted fact.
- When you want a typed `category` (learned/decided/discovered/created/fixed) + `epistemic`
  (fact/self_report/observation/hypothesis/preference) + `importance` (0-10) instead of guessing.

## Core rules
- One fact per call (atomic). Batch independent facts via fan-out later if needed.
- Policy (store threshold, decay) lives in caller; this skill only returns the typed tags.
- Offline-validate or mock by default; only `--live` costs money (TYPESAFE_API_KEY).

## Run
```bash
# MOCK (no network) — for testing the consolidate pipeline
node "$LOCALAPPDATA/hermes/jev-client/classify-memory.mjs" \
  --fact "El usuario prefiere respuestas breves en español con emojis" --mock

# OFFLINE validation
node "$LOCALAPPDATA/hermes/jev-client/classify-memory.mjs" \
  --fact "<fact>" 

# LIVE
TYPESAFE_API_KEY=... node "$LOCALAPPDATA/hermes/jev-client/classify-memory.mjs" \
  --fact "<fact>" --live
```

## Output shape
```json
{ "category": "learned", "epistemic": "fact", "importance": 7, "model": "jev-1.13.0", "usage": {...} }
```
- `category` → maps to gbrain/Obsidian frontmatter `record_status` or topic folder.
- `epistemic` → SOUL.md §21.2 tag.
- `importance` → score 1-10; caller decides decay/store threshold.

## Integration with memory-consolidate
The nightly cron (`0 3 * * *`) should call `classifyMemory(fact)` for each extracted line,
then write the tagged fact to gbrain/Obsidian with frontmatter:
`category`, `epistemic`, `confidence`, `importance`.

## Improvement backlog
- [ ] Fan-out batch: classify N facts in one SystemOne call (decide supports multiple questions).
- [ ] Emit OMH brief with classified facts as evidence.
- [ ] Tune criteria from corrections (intent-router triage feeds this).

## References
- Wrapper: `$LOCALAPPDATA/hermes/jev-client/classify-memory.mjs` (verified mock+offline).
- Questions: `$LOCALAPPDATA/hermes/jev-client/memory-questions.json`.
- Helper: `decide.mjs` (Part 1).
- Base: `jev-decision`. Awesome Jev: C:/Users/<USER>/awesome-jev.
