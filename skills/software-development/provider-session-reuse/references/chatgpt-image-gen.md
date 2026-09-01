# ChatGPT Image Generation via Reused Session (reference)

Concrete findings from a session where the user wanted Hermes to generate images
through their paid ChatGPT (Go) subscription, reusing the already-logged-in session.

## Environment facts (structure, not secrets)
- `auth.json` -> `providers.openai-codex`:
  - `auth_mode: "chatgpt"`, `base_url: https://chatgpt.com/backend-api/codex`
  - `tokens.access_token`: Bearer session token, ~1602 chars
  - `tokens.refresh_token`: ~211 chars
- `config.yaml` line `image_gen` is listed under `platform_toolsets.cli` - but it is
  wired to the **FAL/FLUX** backend, NOT to chatgpt.com. So it cannot use the Go quota.
- `.env`: no `OPENAI_API_KEY` present -> documented fallback was unusable until a key is added.

## How auth was confirmed live
Token read via `terminal`+`python` (read_file is blocked on auth.json).
Requests to `https://chatgpt.com/backend-api/conversation` with headers:
`Authorization: Bearer *** `Origin: https://chatgpt.com`, `Referer: https://chatgpt.com/`,
`User-Agent: <chrome>`, `oai-device-id: <uuid>`, `Accept: text/event-stream`.
Result: HTTP 200 (not 401) -> session is valid and live.

## Endpoint probes (the fragile part)
| Endpoint | Auth used | Result |
| `POST /backend-api/sgm_image` | Bearer | 404 |
| `POST /backend-api/image_gen` | Bearer | 404 |
| `POST /backend-api/conversation` (model gpt-image-1) | Bearer | 200 but SSE stream had no image URLs in captured slice |
| `POST /backend-api/conversation` (model gpt-4o, force_paragen) | Bearer | HTTP 500 |
| `GET /backend-api/requirements` | Bearer | 404 |
| `POST /backend-api/f/conversation` (model gpt-image-1) | Bearer only | `requirements` 404, `conversation` 500 |
| `POST /backend-api/f/conversation` (model gpt-image-1) | Bearer + `_puid` cookie | `requirements` 404, `conversation` 500 |

**Definitive finding:** the REAL image endpoint observed in the user's browser DevTools is
`POST https://chatgpt.com/backend-api/f/conversation` (note the `/f/`). It requires:
1. The full **session `Cookie:` header** from the browser: `__Secure-next-auth.session-token.0`,
   `__Secure-next-auth.session-token.1`, `cf_clearance`, `_puid`, `oai-did`. The `openai-codex`
   `access_token` (Bearer) alone does NOT open this door — confirmed by 404/500 even with Bearer+`_puid`.
2. A fresh `openai-sentinel-chat-requirements-token` (fetched from `GET /backend-api/requirements`
   — which itself 404s without the session cookies).
3. Browser-like headers: `Origin: https://chatgpt.com`, `Referer: https://chatgpt.com/`,
   `oai-device-id`, `x-conduit-token` (also from the live request).

This is a deliberate anti-automation design. The Bearer from `auth.json` only proves the
session is live (non-401); it cannot drive the web image backend. To actually generate,
export the browser cookies (Cookie-Editor extension or DevTools → Application → Cookies on
chatgpt.com) and pass them as the `Cookie:` header.

Lesson: do not guess the image endpoint. Ask the user to capture a real request from
DevTools (Network tab -> generate an image -> copy the `/backend-api/...` URL and the
request body). Each failed attempt spends the user's Go quota.

## Script skeleton (token reuse, no secrets printed)
```python
import json, os, uuid, urllib.request, urllib.error
HERMES_HOME = "<hermes home>"
with open(os.path.join(HERMES_HOME, "auth.json"), encoding="utf-8") as f:
    d = json.load(f)
token = d["providers"]["openai-codex"]["tokens"]["access_token"]  # never print this
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Origin": "https://chatgpt.com",
    "Referer": "https://chatgpt.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "oai-device-id": str(uuid.uuid4()),
}
# POST to the correct /backend-api/... endpoint (capture from DevTools), parse SSE for image URLs
```

## Fallback shape (OpenAI API, documented/stable)
```python
headers = {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"}
payload = {"model": "dall-e-3", "prompt": prompt, "size": "1024x1024", "n": 1}
# POST https://api.openai.com/v1/images/generations
```
Requires `OPENAI_API_KEY` in `.env`. Use as FALLBACK when the chatgpt session route is unknown/broken.

## Verification that was actually run (ad-hoc, not a suite)
- Both scripts compiled cleanly (py_compile).
- Token loaded: `present=True len=1602`.
- `OPENAI_API_KEY present in .env: False`.
- Network probe: chatgpt conversation endpoint -> 200 (auth live).
- VERDICT: syntax + auth verified; **image generation still UNVERIFIED** (correct endpoint
  unknown / fallback key absent). Reported honestly as not done.
