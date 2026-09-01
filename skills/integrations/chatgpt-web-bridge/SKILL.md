---
category: integrations
name: chatgpt-web-bridge
description: Bridge Hermes to the user's ChatGPT WEB account (chatgpt.com) to exercise capabilities Hermes lacks natively — e.g. image generation via the user's ChatGPT Go/Plus subscription. Covers extracting the session from saved page source, the requirements→sentinel→conversation call flow, why the local auth.json Bearer is insufficient, and the Obscura-browser fallback that needs no cookie extraction. Use when the user wants Hermes to "generate images / use my ChatGPT / drive my ChatGPT account / do X through my subscription".
---

# ChatGPT Web Bridge

Hermes' built-in `image_generate` uses FAL.ai FLUX — it does NOT use the user's ChatGPT subscription. To generate images (or run other ChatGPT-only actions) through the user's own chatgpt.com account, you must call the ChatGPT **web backend API** with the user's **session**, not the OpenAI API key and not the `auth.json` token.

## Trigger
User asks Hermes to: generate images "with my ChatGPT / my Go / my Plus", "use my account", "drive my ChatGPT", or any capability that Hermes can't natively do but ChatGPT web can. Also relevant as the PRIMARY route B when the user has a ChatGPT subscription and wants to avoid spending an OpenAI API key (route A = OpenAI API key in `.env`, fallback).

## Critical fact (verified)
The token in Hermes' `auth.json` under `providers.openai-codex.tokens.access_token` is a **Codex/session Bearer** and is NOT accepted by the chatgpt.com web backend (`/backend-api/*`). Calling `/requirements` or `/f/conversation` with that Bearer alone returns **404 / 500** (`{"detail":"Hmm...something seems to have gone wrong."}`). You need the user's **chatgpt.com session**: `sessionToken` + `accessToken` carried as a cookie + Bearer, plus the anti-bot sentinel from `/requirements`.

## Route B — web backend (the user's subscription)
### Step 1 — obtain the session tokens
Two clean ways. Prefer the one the user can produce without touching their Chrome profile:

**Method 1 — saved page source (no cookie tooling needed).**
Ask the user to open a chat in chatgpt.com, do `Ctrl+S` / "Save page" (complete HTML, not single-file MHTML), and send the `.html` file. The session is embedded in the bootstrap script:

```python
import re, json
txt = open(html_path, encoding="utf-8", errors="replace").read()
m = re.search(r'<script[^>]*id="client-bootstrap"[^>]*>(.*?)</script>', txt, re.S)
boot = json.loads(m.group(1))
sess = boot["session"]
session_token = sess["sessionToken"]   # goes into the cookie
access_token  = sess["accessToken"]    # goes into Authorization: Bearer
```

**Method 2 — Cookie-Editor / DevTools.** If no saved HTML, ask the user for the cookie value of `__Secure-next-auth.session-token` (and `.0`/`.1` shards), `cf_clearance`, `_puid`, `oai-did` from https://chatgpt.com (DevTools → Application → Cookies, or the Cookie-Editor extension → Export as JSON). These are httpOnly and do NOT appear in saved page HTML, so this method is the fallback when Method 1 isn't available.

> SECURITY: cookies/tokens = a live session. Treat them like passwords. Read them into the script, never print full values, never persist them (don't write to files, don't echo), delete the script's working copy when done. They expire on logout / password change.

### Step 2 — the call flow
1. `POST https://chatgpt.com/backend-api/requirements`
   Headers: `authorization: Bearer <accessToken>`, `cookie: __Secure-next-auth.session-token=<sessionToken>`, `content-type: application/json`, plus a browser-like `user-agent`/`origin`/`referer`.
   Body: `{"conversation_mode":{"kind":"primary_assistant"},"kind":"init_image_generation"}`
   Response (JSON) contains a `token` — this is the **sentinel** (`openai-sentinel-chat-requirements-token`).
2. `POST https://chatgpt.com/backend-api/f/conversation` (streaming SSE, `accept: text/event-stream`), adding header `openai-sentinel-chat-requirements-token: <sentinel>`.
   Body: `{"action":"next","messages":[{"id":"m1","role":"user","content":{"content_type":"text","parts":["PROMPT"]}}],"conversation_id":null,"parent_message_id":"00000000-0000-0000-0000-000000000000","model":"gpt-image-1"}`
   Image URLs (e.g. `https://files.oaiusercontent.com/...`) arrive in the stream; collect and download.

> **REALITY CHECK (verified 2026-07-12).** The exact web image payload is **undocumented and fragile**. In a real run with a VALID session (sessionToken cookie + accessToken Bearer extracted from saved HTML):
> - `POST /requirements` returned **404 `{"detail":"Not Found"}`** — the sentinel was empty, so the documented "requirements→sentinel" step did NOT yield a token.
> - `POST /f/conversation` returned **422 `{"detail":"Invalid conversation body"}`** for BOTH `model:"gpt-image-1"` and `model:"image_gen"` with the schema above.
> The error moving from `500` (Bearer-only) to `422` (session accepted but body rejected) confirms the **session was accepted** — the blocker is the undocumented request body, not auth.
> **Check the saved HTML for the feature flag** `image_gen_enabled` in the bootstrap/config JSON. On ChatGPT **Go** it appeared as `"image_gen_enabled":false` — meaning the web route is disabled for that plan regardless of payload correctness. Always grep the HTML for `"image_gen_enabled"` BEFORE investing in Route B.
> Because of this, treat Route B as **experimental**. For reliable image generation prefer **Route A** (OpenAI API key) or **Route C** (Obscura browser, no extraction).

Reference recipe + header detail: `references/chatgpt-image-gen.md`.
Native-curl transport recipe (when local Python can't do HTTP): `references/curl-native-bridge.md`.
OpenRouter image API (Route D) + 402/no-credits gotcha + Windows curl recipe: `references/openrouter-image-gen.md`.

## Route A — OpenAI API key (stable fallback)
Set `OPENAI_API_KEY` in `~/.hermes/.env` and call `https://api.openai.com/v1/images/generations` with `model: gpt-image-1` (or `dall-e-3`). This is the most stable route; recommend it when the user just wants images and doesn't care that it's billed to the API key rather than their ChatGPT subscription.

## Route C — Obscura browser (no cookie extraction at all)
The `mcp_obscura_browser` tools can open https://chatgpt.com, the user logs in once in that browser session, and you drive the page directly (type the prompt, click generate, read the result). Because the session lives in the browser, you never need to extract cookies/tokens. Use this when cookie/token extraction is blocked or fragile.

## Route D — OpenRouter image API (verified working fallback)
If the user has an `OPENROUTER_API_KEY` (Hermes ships with one in `.env`), this is the most
stable route — no cookies, no payload guessing. OpenRouter exposes OpenAI image models as
`openai/gpt-5-image`, `openai/gpt-5-image-mini`, `openai/gpt-5.4-image-2` (NOT `gpt-image-1`,
which is OpenAI-direct only). Endpoint: `POST https://openrouter.ai/api/v1/images/generations`
with `authorization: Bearer <OPENROUTER_API_KEY>`. A `200` on model list + `402` on gen means
the key is fine but the account has **no credits** (buy at https://openrouter.ai/settings/credits)
— that is a billing fix, not a code fix. Full recipe + the Windows-curl transport workaround
(no Python HTTP, CRLF gotcha) in `references/openrouter-image-gen.md`. Prefer D over B whenever
the user's ChatGPT plan shows `image_gen_enabled:false` or B keeps 422'ing.

## Verification discipline
After writing/editing any bridge script, run an **ad-hoc** verification (temp script in `AppData\Local\Temp\hermes-verify-*`, named so it's clearly throwaway), confirm it compiles and loads tokens, then DELETE it and report it as "ad-hoc verified" — NOT "suite green". Never claim an image was generated unless a real run returned image URLs.

## Pitfalls
- **Bearer-only fails.** The `auth.json` openai-codex token is not the chatgpt.com web session. Always carry the `sessionToken` cookie + the `/requirements` sentinel.
- **httpOnly cookies aren't in saved HTML.** `__Secure-next-auth.session-token` won't appear in a saved `.html` file unless OpenAI embedded it in the bootstrap JSON (it does — as `session.sessionToken`). If the user sends DevTools cookies instead, the relevant names are `__Secure-next-auth.session-token[.0/.1]`, `cf_clearance`, `_puid`, `oai-did`.
- **Check `image_gen_enabled` in the saved HTML FIRST.** Grep the bootstrap/config JSON for `"image_gen_enabled"`. If `false` (observed on ChatGPT Go, 2026-07-12), Route B is disabled for that plan — stop and switch to Route A/C. Don't burn requests guessing the payload.
- **The `/f/conversation` image body is undocumented.** With a valid session, `404` on `/requirements` and `422 Invalid conversation body` on `/f/conversation` are the observed real responses. Treat reverse-engineered payloads as best-effort; if it 422s after session acceptance, do NOT keep guessing — fall back to Route A or C.
- **HTTP transport may be unavailable in the local Python.** If `import socket` / `urllib` / `requests` fails in the active interpreter, delegate the network call to a native tool (`curl` on Windows, or the Obscura browser) rather than asserting Python is broken. Preflight: `python -c "import socket"` — if it errors, switch transport. Do NOT hardcode "Python can't do HTTP" as a permanent rule; it's environment state.
- **curl gotcha on Windows bash:** never inline an `Authorization: Bearer <token>` header with a single-quoted `-H '...'` containing a double quote — bash reports `unexpected EOF while looking for matching`. Put headers in **variables** (`AUTHH="authorization: Bearer $AT"`) and pass `-H "$AUTHH"`. Read tokens from temp files, never print them. See `references/curl-native-bridge.md`.
- **Don't fire requests blindly at the user's account.** Have the tokens/session confirmed before any `/f/conversation` call.
- **Route D 402 is billing, not auth.** OpenRouter image gen returning `HTTP 402 {"error":{"code":402,"message":"Insufficient credits..."}}` means the key is valid and reached OpenRouter (401 would mean a bad key). The fix is the user buying credits at https://openrouter.ai/settings/credits — no code change. Don't loop re-trying the call thinking the request is wrong.
- **OpenRouter image model slugs differ from OpenAI-direct.** Use `openai/gpt-5-image` / `gpt-5-image-mini` / `gpt-5.4-image-2` on OpenRouter; `gpt-image-1` exists only on the OpenAI direct API.
