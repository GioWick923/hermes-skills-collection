---
name: jev-decision
description: Use when you need a typed Jev/TypeSafe decision in Hermes.
---

# Jev Decision (TypeSafe SystemOne) for Hermes

Make a typed judgment about text or structured state using Jev (`jev-1.13.0` or newer).
The client lives at `$LOCALAPPDATA/hermes/jev-client/` (Node 22+, `@typesafe-ai/sdk@0.6.0`).

## When to use
- Classify / route / triage a text or JSON state (e.g. support ticket, log line, user intent).
- Score something on a rubric (urgency, quality, risk) with an ordered legend.
- Ask one or more independent yes/no (Noul) questions.
- Any decision where you want a *typed, inspectable* answer instead of free-form LLM text.

## Core rules (from awesome-jev AGENTS.md)
- Questions are atomic and complete; question IDs are lookup keys, NOT model instructions.
- Keep all policy (thresholds, weights, arithmetic, downstream actions) in CODE, not in the model.
- Preserve the raw typed answer for inspection; never invent or round-trip a value the model did not return.
- Default to OFFLINE validation or `--mock` unless the user explicitly opts into `--live` (costs money, needs `TYPESAFE_API_KEY`).

## Setup
```bash
# one-time (already done if client exists)
mkdir -p "$LOCALAPPDATA/hermes/jev-client"
cd "$LOCALAPPDATA/hermes/jev-client"
npm init -y >/dev/null 2>&1
npm install @typesafe-ai/sdk@0.6.0
# write jev.mjs + decide.mjs (helper) + per-wrapper *-questions.json
```

## Run (always verify the environment first)
```bash
# 1) OFFLINE: validate payload shape, no network
node "$LOCALAPPDATA/hermes/jev-client/decide.mjs" \
  --state "<text or @file.json>" --questions @<questions.json>

# 2) MOCK: synthetic answers, no network, for workflow testing
node "$LOCALAPPDATA/hermes/jev-client/decide.mjs" \
  --state "..." --questions @<questions.json> --mock

# 3) LIVE: real API call — OpenRouter (default, uses OPENROUTER_API_KEY)
node "$LOCALAPPDATA/hermes/jev-client/decide.mjs" \
  --state "..." --questions @<questions.json> --live --provider openrouter

# Alt: TypeSafe direct (needs TYPESAFE_API_KEY)
node "$LOCALAPPDATA/hermes/jev-client/decide.mjs" \
  --state "..." --questions @<questions.json> --live --provider typesafe
```
Provider default: openrouter if OPENROUTER_API_KEY is set, else typesafe. Model default per provider (typesafe/jev-1.13 for openrouter, jev-1.13.0 for typesafe). To pin exactly: `--model typesafe/jev-1.13` (openrouter) or `--model jev-1.13.0` (typesafe).

## Questions file format (questions.json)
```json
{
  "is_billing": { "type": "noul", "instructions": "Is this about billing?" },
  "department": { "type": "choice", "instructions": "Which department?",
                  "criteria": { "sales": "Sales", "support": "Support", "none": "Other" } },
  "urgency": { "type": "score", "instructions": "Urgency 0-2",
               "criteria": ["Low", "Medium", "High"] }
}
```
- `noul` → `{ type:"noul", noul: 0..1 }` (probability of yes; near 0 = no, not low confidence).
- `choice` → `{ type:"choice", choice, confidence, probabilities }`. Always include a `none`/`other` outcome.
- `score` → `{ type:"score", score, confidence, legend, probabilities }`. Rubric needs >=2 entries.

## Response handling (in your code / skill step)
- Read answers by ID: `answers.department.choice`, `answers.is_billing.noul`, `answers.urgency.score`.
- Apply thresholds in code: e.g. `if (answers.is_billing.noul < 0.5) route_to_review()`.
- Never trust confidence as accuracy; it is not calibrated. Abstain when below your policy floor.
- Report the `model` field from the response (alias can change; pin version for evaluations).

## Live mode guardrails
- Require explicit opt-in (`--live`) AND a set `TYPESAFE_API_KEY`.
- Do not load `.env` automatically; use the user's shell env.
- Log `model` + `usage` for cost tracking.
- On `429`/`5xx` the SDK retries with backoff (configurable). On `4xx` it throws — surface the error.

## The five wrappers built on decide()
All live in `$LOCALAPPDATA/hermes/jev-client/` and share the `decide.mjs` helper:
- `intent-router` → `decide.mjs` + `intent-questions.json` (message intent + clarity)
- `memory-classifier` → `classify-memory.mjs` + `memory-questions.json` (category/epistemic/importance)
- `jev-validate` → `validate-output.mjs` + `validate-questions.json` (4 score dims)
- `evolution-gate` → `evolution-gate.mjs` + `evolution-gate-questions.json` (risk/breaks/reversible)
- `correction-triage` → `triage-correction.mjs` + `triage-questions.json` (type/repeat/durable)
Each wrapper is also a Hermes skill under `skills/autonomous-ai-agents/`. Add a new consumer by
copying the wrapper shape and a `*-questions.json`; do NOT duplicate `decide.mjs`.

## Windows execution pitfalls (learned this session)
- Pass native Windows paths (`C:/Users/x` or `$LOCALAPPDATA/...`), never `/c/Users/x` — MSYS path
  conversion is disabled for native node, so `/c/...` falls to `C:\c\...` and the file is not found.
- Import `decide.mjs` from another script with a `file://` URL (`import('file:///C:/.../decide.mjs')`),
  not a raw `c:` path — Node's ESM loader rejects bare drive-letter URLs on Windows.
- Write skill SKILL.md files directly to the skills dir (`$LOCALAPPDATA/hermes/skills/<cat>/<name>/`)
  when `skill_manage` create/write_file returns a schema error; the file loads identically. Do not
  loop on the same failing `skill_manage` call — disk write is equivalent and verified by `skill_view`.
- Use `$LOCALAPPDATA/Temp` for scratch JSON, not `/tmp` — on this host `/tmp` resolves to `C:\tmp`
  (nonexistent) and `readFileSync` throws ENOENT.

## Jev question-design pitfalls (cost real debug time this session)
- Keep `score` rubrics at **10 levels max (0-9)**: OpenRouter rejects 11+ with HTTP 400
  `Too many score levels`. Encode importance/severity 0-9, never 0-10, in score questions.
- Never hardcode `model` in a wrapper that calls `decide()` — it overrides provider resolution and
  OpenRouter gets `jev-1.13.0` (400 "Model does not exist"). Pass `model` undefined and let `decide()`
  pick `~typesafe/jev-latest` for openrouter / `jev-1.13.0` for typesafe.
- Use OpenRouter via raw `fetch`, not the `@typesafe-ai/sdk` (the SDK only targets `api.typesafe.ai`).
  See `references/openrouter.md` for endpoint, auth, and the score-limit rule.

## Improvement backlog (make this skill better)
- [ ] Add Python wrapper using `typesafe-sdk` for Hermes python toolchain parity.
- [ ] Add a `--fan-out` mode for speculative question batches (see docs/typesafe fan-out).
- [ ] Cache repeated `(state,questions)` offline fixtures for replay.
- [ ] Emit OMH brief/handoff with the typed answer as evidence (align with awesome-jev OMH notes).
- [ ] Pin model version per eval; allow `JEV_MODEL` override from env.

## References
- Full client source: `$LOCALAPPDATA/hermes/jev-client/jev.mjs` (offline + mock verified).
- Helper: `$LOCALAPPDATA/hermes/jev-client/decide.mjs` (importable via file:// URL).
- SDK API: verified from `node_modules/@typesafe-ai/sdk/dist/index.d.mts` (v0.6.0).
- Upstream docs: https://docs.typesafe.ai/api , https://docs.typesafe.ai/primitives/noul
- Awesome Jev repo: C:/Users/<USER>/awesome-jev (cloned, `npm run check` passes)
