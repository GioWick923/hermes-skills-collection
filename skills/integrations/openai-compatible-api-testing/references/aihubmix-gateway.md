# AI HubMix (console.aihubmix.com) — gateway testing notes

OpenAI-compatible proxy/aggregator (US, AIHubMix LLC). Serves 500+ models incl. 27+ free models with `-free` suffix. Docs index: https://docs.aihubmix.com/llms.txt (also `/agents.md`).

## Endpoints
- Base URL: `https://aihubmix.com/v1` (alias `https://api.aihubmix.com/v1` also answers `/v1/models`)
- OpenAI chat: `POST https://aihubmix.com/v1/chat/completions`
- Anthropic-compatible: `POST https://aihubmix.com/v1/messages`
- Manage/CLI endpoints (need a separate "Manage Key", NOT the API key): available-models, balance, key CRUD — documented under `cn/api/CliEndpoints/*.md`

## Free GLM catalog (from docs `cn/blogs/free-ai-models.md`, 2026-05)
- General chat: `glm-4.7-flash-free` (128K ctx)
- Coding: `coding-glm-4.6-free`, `coding-glm-4.7-free`, `coding-glm-5-free` (745B MoE), `coding-glm-5-turbo-free`, `coding-glm-5.1-free` (SWE-bench Pro #1, 58.4%)
- Other free highlights: `gpt-5.5-free`, `gpt-4.1-free` (1M ctx), `gemini-3-flash-preview-free`, `gpt-image-2-free`, `gemini-3.1-flash-image-preview-free` (Nano Banana 2), `xiaomi-mimo-v2.5-free`, `kimi-for-coding-free`

## Error taxonomy observed (2026-08-26 session)
- Zhipu official endpoints (`open.bigmodel.cn/api/paas/v4`, `api.z.ai/api/paas/v4`, GLM Coding `open.bigmodel.cn/api/coding/paas/v4`, `api.siliconflow.cn/v1`) → **401 "token expired or incorrect" / 令牌已过期或验证不正确** for an AI HubMix key. Normal: gateway keys only work on the gateway.
- `GET /v1/models` with gateway key → HTTP 200 but `{"data":[],"object":"list"}` → **key has a model whitelist** (restricted keys hide the catalog).
- Any chat completion → `403 Forbidden – key:(last4) not authorized to access the requested model:(model)` → per-key whitelist in console, regardless of model name (18+ names tested incl. documented free IDs; all forbidden).
- Free-model quota exhaustion (2026-08-31, `coding-glm-5.3-free`): completion body says `accounts that have not been recharged can only try 10 times. You can increase the free quota after recharging; https://console.aihubmix.com/topup` → distinct from the whitelist 403; it means the `-free` model still answered but the account's free quota is spent. Switch to a paid model with balance or top up. Do NOT treat as "model broken".

## Fix (user-side, not solvable by model-name guessing)
1. https://console.aihubmix.com → API Keys → open the key → "模型限制 / Model Restrictions" — add the free GLM model ID or remove restriction.
2. Check balance (0 balance can block everything).
3. Otherwise create a fresh key without restrictions.
