# OpenRouter Decisions provider (Jev)

Use when calling Jev through OpenRouter instead of TypeSafe direct.

## Endpoint and auth
- `POST https://openrouter.ai/api/alpha/decisions`
- Header `Authorization: Bearer $OPENROUTER_API_KEY`. Optional: `HTTP-Referer`, `X-OpenRouter-Title`.
- Request body: `{ "model": "~typesafe/jev-latest", "state": <text|json>, "questions": { ... } }`
- Response: `{ "model", "answers", "usage", "id", "provider" }` — `answers` shape is identical to the
  TypeSafe SystemOne SDK result (noul/choice/score carry the same fields).

## Model alias
- Use `~typesafe/jev-latest` (resolves to a dated build like `typesafe/jev-1.13-20260917`).
- Do NOT send `jev-1.13.0` to OpenRouter — it returns 400 "Model does not exist". Let `decide()`
  resolve the model from the provider; never hardcode a TypeSafe-only model string in a wrapper.

## Score rubric limit (hard constraint)
- A `score` question's `criteria` array may have **at most 10 entries** (levels 0-9).
- 11 entries → HTTP 400 `Too many score levels. Must have at most 10 levels.`
- Encode importance/severity as 0-9, not 0-10, when using score questions.

## Transport
- The `@typesafe-ai/sdk` only targets `api.typesafe.ai`. For OpenRouter use a raw `fetch`
  (see `decide.mjs` openrouter branch) — do not route OpenRouter through the SDK.
- Per-call cost is sub-cent (~$0.000018 for 3 questions); safe for live opt-in.

## Verification
- A live call with a real `OPENROUTER_API_KEY` returns HTTP 200 and typed answers; the 404 page
  shown by the OpenRouter web UI for an unauthenticated/placeholder key is NOT an API error.
