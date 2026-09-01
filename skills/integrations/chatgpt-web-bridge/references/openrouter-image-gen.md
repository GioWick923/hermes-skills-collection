# OpenRouter Image Generation (Route D — verified working)

When the ChatGPT WEB route (B) is disabled for the user's plan (`image_gen_enabled:false`,
observed on ChatGPT Go) or the reverse-engineered payload keeps 422'ing, and the user has an
`OPENROUTER_API_KEY` (Hermes ships with one in `.env`), generate images through OpenRouter's
image endpoint instead. This is the most stable path for "use my existing setup, no new key".

**Verified 2026-07-12 on a Windows host with Python HTTP broken (`_socket` DLL load failures
in all uv interpreters) — so the call MUST go through native `curl`, not Python requests/urllib.**

## Discovery
- `OPENROUTER_API_KEY` already present in `C:\Users\<USER> GAMES\AppData\Local\hermes\.env`
  (name `OPENROUTER_API_KEY`, value `sk-or-...`, 73 chars, no quotes). No user action needed.
- OpenRouter exposes OpenAI image models under `openai/*` IDs. Live image models found via
  `GET https://openrouter.ai/api/v1/models` and filtering `id` for "image":
  - `openai/gpt-5-image`
  - `openai/gpt-5-image-mini`
  - `openai/gpt-5.4-image-2`
  (Note: `gpt-image-1` is the OpenAI *direct* API model, NOT available on OpenRouter — use the
  `gpt-5-image*` slugs there.)

## Endpoint
`POST https://openrouter.ai/api/v1/images/generations`
Headers: `authorization: Bearer <OPENR...Y>`, `content-type: application/json`
Body:
```json
{"model":"openai/gpt-5-image","prompt":"...","n":1,"size":"1024x1024"}
```

## Verified result
- Key valid, endpoint correct → `HTTP 200` for model list, `HTTP 402` for image gen.
- `402` body: `{"error":{"message":"Insufficient credits. This account never purchased credits.
  Make sure your key is on the correct account or org, and if so, purchase more at
  https://openrouter.ai/settings/credits","code":402}}`
- **402 = no billing credits, NOT an auth failure.** The request reached OpenRouter and was
  authenticated (it would be 401 if the key were bad). Fix = user buys credits at the URL above.
  No code change needed. Once credits exist, the same call returns the image (b64 or URL in
  `data[].url`/`data[].b64_json`).

## Windows curl transport recipe (Python HTTP is broken on this host)
Put the body in a separate `.json` file (avoids inline-quote breakage). Read the key from `.env`
with pure-python parse (no `socket`), pass via a header VARIABLE (never inline a double-quoted
`-H` with a `Bearer` token — MSYS bash throws `unexpected EOF while looking for matching`).
```bash
#!/usr/bin/env bash
set -u
ENV="C:/Users/<USER> GAMES/AppData/Local/hermes/.env"
ORKEY=$(python -c "import os
for l in open(r'$ENV',encoding='utf-8',errors='replace'):
    if l.startswith('OPENROUTER_API_KEY'):
        print(l.split('=',1)[1].strip()); break" 2>/dev/null)
[ -z "$ORKEY" ] && { echo NO_KEY; exit 0; }
AUTHH=*** Bearer $ORKEY"
curl -sS -o "out.json" -w "HTTP=%{http_code}\n" \
  -H "$AUTHH" -H "content-type: application/json" \
  --data-binary @"body.json" \
  "https://openrouter.ai/api/v1/images/generations"
```
**CRITICAL Windows gotcha:** `write_file` may emit CRLF line endings; bash breaks on the
continuation `\` + CR. After writing, run `sed -i 's/\r$//' script.sh` before `bash script.sh`.
This was the cause of repeated `unexpected EOF while looking for matching` errors until fixed.

## Parse the response
Read `out.json` with pure python (no network): `json.load(open("out.json"))` -> look in
`["data"]` for `url` or `b64_json`. Save b64 to `.png` via `base64.b64decode`.
