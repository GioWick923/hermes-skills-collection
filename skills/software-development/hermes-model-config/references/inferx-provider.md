# Inferx Provider Integration

## Overview
Inferx provides OpenAI-compatible endpoints with pay-per-token billing. Models include
`deepseek-v4-flash-0731` and others hosted at `https://model.inferx.net`.

## Key Format
- API keys start with `ix_` (e.g. `ix_01fc...`)
- Not `sk-` based — do NOT mistake for DeepSeek or OpenAI keys

## Configuration Steps
1. Set `INFERX_API_KEY=<key>` in `.env`
2. Add a `providers` entry in `config.yaml`:
```yaml
providers:
  inferx:
    name: inferx
    base_url: https://model.inferx.net/endpoints/v1
    api_key: ix_<your_key>
    api_mode: openai
    default_model: deepseek-v4-flash-0731
```
3. (Optional) Add to `fallback_providers` for failover

## Liveness Check
```bash
curl https://model.inferx.net/endpoints/v1/chat/completions \
  -H "Authorization: Bearer $INFERX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash-0731","max_tokens":20,"messages":[{"role":"user","content":"di hola"}]}'
```

## Caveats
- Endpoint may return HTTP 200 but with a long cold-start delay.
- Use 120s timeout, not 45s, for first-time checks. See the parent skill's pitfall
  "Slow OpenAI-compatible endpoints time out on first liveness check" for retry logic.
