---
name: openrouter-decisions
description: Use when building OpenRouter Alpha typed classifiers.
---

# OpenRouter Decisions Integration

Type-safe decision/triage API from OpenRouter Alpha. Model: `~typesafe/jev-latest`.

## When to use
- Classify free-text or structured state into typed answers
- Triage support tickets, route messages, score sentiment/urgency
- Any workflow where you need a model to answer narrow, typed questions about a state your code owns

## Install
```bash
npm init -y
npm install @openrouter/sdk
# package.json MUST have "type": "module" (SDK is ESM)
```

## API key
- Use `process.env.OPENROUTER_API_KEY` (already in Hermes env as `***`).
- DO NOT hardcode example keys (causes 401 "User not found").

## Core wrapper (openrouter-decisions.js)
```javascript
import { OpenRouter } from "@openrouter/sdk";

export async function decide({ state, questions, model = "~typesafe/jev-latest", sessionId, user, apiKey = process.env.OPENROUTER_API_KEY }) {
  if (!apiKey) throw new Error("OPENROUTER_API_KEY not set");
  // SDK v1.3.6 expects `questions` as a RECORD keyed by id, NOT an array.
  // Accept either form for caller convenience.
  const questionsRecord = Array.isArray(questions)
    ? Object.fromEntries(questions.map((q) => [q.id, q]))
    : questions;
  const openrouter = new OpenRouter({ apiKey });
  const decision = await openrouter.alpha.decisions.create({
    decisionsRequest: { model, state, questions: questionsRecord, ...(sessionId && { sessionId }), ...(user && { user }) }
  });
  return { answers: decision.answers, id: decision.id, model: decision.model, provider: decision.provider, usage: decision.usage };
}
```

## Question types
- **noul**: `{ type: "noul", instructions, criteria: { true: "...", false: "..." } }` → answer: `{ noul: 0-1, type }`
- **choice**: `{ type: "choice", instructions, criteria: { opt1: "desc", opt2: "desc" } }` → answer: `{ choice: string, confidence?, probabilities?, type }`
- **score**: `{ type: "score", instructions, criteria: ["low", "mid", "high"] }` → answer: `{ score: number, legend?, probabilities?, confidence?, type }`

## State formats
`state` accepts: `string`, `Record<string,any>`, or `array`. Use objects/arrays for structured context.

## Gotchas
- `package.json` needs `"type": "module"` or SDK import fails
- Windows CLI: compare `realpathSync(fileURLToPath(import.meta.url))` not raw string (backslashes)
- Response `model` is the resolved version (e.g. `typesafe/jev-1.13-20260917`), `provider` is `TypeSafe`
- `usage.cost` is in USD (very cheap: ~$0.000017 per call)
- Answers are a discriminated union by `type` field — check `answer.type` before reading `noul`/`choice`/`score`

## Verification
Always run a real call before claiming success:
```bash
node test-wrapper.js  # or: node openrouter-decisions.js "<state>" questions.json
```
Expected: JSON with `answers`, `usage.cost`, `provider`.
