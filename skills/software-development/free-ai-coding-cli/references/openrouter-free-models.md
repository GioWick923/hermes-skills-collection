# OpenRouter free models — endpoint & rules

## Anthropic-compatible endpoint
Claude Code (and any Anthropic-Messages-API client) can be redirected here:
```
https://openrouter.ai/api/anthropic
```
Set three env vars:
- `ANTHROPIC_BASE_URL=https://openrouter.ai/api/anthropic`
- `ANTHROPIC_API_KEY=***  (OpenRouter key, not Anthropic)
- `ANTHROPIC_MODEL=<openrouter model id, e.g. tencent/hy3:free>

## List models (verify an id exists)
```bash
curl -s https://openrouter.ai/api/v1/models \
 | python -c "import sys,json;d=json.load(sys.stdin);print([m['id'] for m in d['data'] if 'hy3' in m['id'].lower()])"
```

## Free models seen working (ids are exact, copy verbatim)
- `tencent/hy3:free` — Hunyuan-style, strong coding, used as default in our launcher
- `tencent/hy3` / `tencent/hy3-preview` — non-free variants
- `moonshotai/kimi-k2:free` — the model the tutorial mislabels as "Kimiko 2.6"
- Gemma variants exist but tutorial's "Gemma 431B" is a misnomer; copy the real id
  from openrouter.ai/models

## Key rules
- Keys: https://openrouter.ai/keys — format `sk-or-...`, shown once, store safely.
- Free tier: rate-limited + higher latency; cold-start first response ~40s is normal.
- Optional headers reduce warnings: `HTTP_REFERER`, `X_TITLE`.
- OpenRouter account may need a tiny credit balance for some models; pure `:free`
  models work with $0 but may throttle.
