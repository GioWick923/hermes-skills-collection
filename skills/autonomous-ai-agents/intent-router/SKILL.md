---
name: intent-router
description: Use when you need to classify the user's message intent (code/research/creative/meta) via a typed Jev decision before acting.
---

# Intent Router (typed, Jev-backed)

Classify the user's incoming message into an intent category with a typed Jev decision,
so routing is *auditable* instead of free-form LLM guessing. Built on `jev-decision` + `decide.mjs`.

## When to use
- At the start of a turn when the task type is ambiguous and you want a typed signal before choosing a skill/path.
- To replace or augment OMH route hints with a verifiable classification (keeps the hint, adds evidence).
- NEVER as a security boundary — only as a routing signal your code still validates.

## Core rules
- One atomic question for intent (choice), plus one score for clarity (policy lives in caller).
- Always include a `none` outcome; abstain when confidence score < your floor (default 1 of 2).
- Offline-validate or mock by default; only `--live` (needs TYPESAFE_API_KEY) costs money.

## Run
```bash
# 1) OFFLINE: confirm payload shape
node "$LOCALAPPDATA/hermes/jev-client/decide.mjs" \
  --state "<user message>" --questions @"$LOCALAPPDATA/hermes/jev-client/intent-questions.json"

# 2) MOCK: synthetic classification (no network)
node "$LOCALAPPDATA/hermes/jev-client/decide.mjs" \
  --state "<user message>" --questions @"$LOCALAPPDATA/hermes/jev-client/intent-questions.json" --mock

# 3) LIVE: real typed classification
TYPESAFE_API_KEY=... node "$LOCALAPPDATA/hermes/jev-client/decide.mjs" \
  --state "<user message>" --questions @"$LOCALAPPDATA/hermes/jev-client/intent-questions.json" --live
```

## Questions file (intent-questions.json)
```json
{
  "intent": { "type": "choice", "instructions": "¿Cuál es la intención principal de este mensaje?",
              "criteria": { "code": "Escribir/ejecutar/depurar código", "research": "Investigar o buscar info",
                             "creative": "Generar contenido/arte/audio", "meta": "Hablar del agente o flujo", "none": "Ninguna clara" } },
  "clarity": { "type": "score", "instructions": "¿Qué tan claro está el pedido? 0=vago, 2=explícito",
               "criteria": ["Vago", "Medio", "Explícito"] }
}
```

## Response handling (in your code)
- `answers.intent.choice` → route to that skill family.
- `answers.clarity.score` → if < 1, ask a clarifying question before acting (do not guess intent).
- Report `model` from response for eval traceability.

## Improvement backlog
- [ ] Fan-out: batch intent + safety + memory-class in one call (decide supports it).
- [ ] Emit OMH brief with the typed intent as evidence.
- [ ] Tune criteria per user vocabulary (learn from corrections via jev-decision triage).

## References
- Helper: `$LOCALAPPDATA/hermes/jev-client/decide.mjs` (verified offline+mock+import).
- Base skill: `jev-decision`.
- Awesome Jev: C:/Users/<USER>/awesome-jev (AGENTS.md rules applied).
