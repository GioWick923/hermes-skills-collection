# Cline CLI → custom gateway connection (Responses vs Chat Completions)

Connecting the **Cline CLI** (v3.0.55, installed at `$LOCALAPPDATA/hermes/node/cline.cmd`)
to an OpenAI-compatible gateway (aihubmix / openrouter / bai) to run a model like glm-5.3.

## Key facts about Cline CLI
- Any OpenAI-compatible endpoint is reachable via provider **`openai-native`** with an explicit base URL.
- Native providers with saved credentials: `cline`, `openai-codex`, `oca` (OAuth) — need explicit `cline auth`.
- Auth is non-interactive:
  ```bash
  cline auth -p openai-native -k <KEY> -m <model> -b <base_url>
  ```
  Output: `Provider configured: openai-native (<model>)` + exit 0.
- Provider IDs are NOT arbitrary: `-p aihubmix-glm` → `error: invalid provider`. Use `openai-native`
  (or a Cline-known ID like `openrouter`) + `-b` for the base URL.

## THE trap: Responses API vs Chat Completions
Cline's `openai-native` provider sends the OpenAI **Responses API** shape by default.
Our gateways (aihubmix, and most OpenAI-compatible aggregators) serve **Chat Completions**.
Result — a stream-type validation error, NOT an auth error:

```
error: Received a Chat Completions stream while using the OpenAI Responses API.
The default OpenAI provider model uses the Responses API. If your custom baseURL
targets a Chat Completions-compatible endpoint, use openai.chat('model-id') ...
AI_TypeValidationError: expected "response.output_text.delta" ... received undefined
```

So a "Provider configured" success does NOT mean inference works — you must run a real
prompt to confirm. If this error appears, the endpoint speaks Chat Completions and
`openai-native` is the wrong provider type for it (Cline needs a Chat-Completions-capable
adapter; `openrouter` and other known providers that use Chat Completions may be the
pragmatic path, or a base URL that serves Responses API).

## Free-model quota exhaustion (aihubmix)
`coding-glm-5.3-free` returned:
```
Sorry, to prevent abuse of free resources, accounts that have not been recharged
can only try 10 times. You can increase the free quota after recharging;
https://console.aihubmix.com/topup
```
Meaning: the `-free` GLM models on aihubmix cap at ~10 calls on an unrecharged account.
This is a credit/quota message (see aihubmix-gateway.md fix section) — switch to a paid
model with balance, or top up. Do NOT treat it as "the model is broken".

## Verified workflow (2026-08-31)
1. `cline auth -p openai-native -k <key> -m coding-glm-5.3-free -b https://aihubmix.com/v1` → ✅ configured
2. `cline -P openai-native -m coding-glm-5.3-free "<prompt>"` → ❌ Responses-vs-ChatCompletions error
   (and, separately, the free quota was exhausted).

Lesson: **"configured" ≠ "working"** — always run one real inference before declaring
a CLI↔gateway wiring successful.
