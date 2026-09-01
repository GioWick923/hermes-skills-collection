# chatgpt-image-gen.md — real observed responses & feature flag (Route B)

## Verified responses (2026-07-12, valid session extracted from saved HTML)
Machine: Windows, chatgpt.com session = `sessionToken` cookie + `accessToken` Bearer.

| Call | Body | Result |
|------|------|--------|
| `POST /backend-api/requirements` | `{"conversation_mode":{"kind":"primary_assistant"},"kind":"init_image_generation"}` | **404** `{"detail":"Not Found"}` — sentinel EMPTY |
| `POST /backend-api/f/conversation` | `model:"gpt-image-1"` + `parent_message_id` etc. | **422** `{"detail":"Invalid conversation body"}` |
| `POST /backend-api/f/conversation` | `model:"image_gen"` (slug from HTML) + `conversation_mode` | **422** `{"detail":"Invalid conversation body"}` |

Interpretation: error moved `500` (Bearer-only, no session) → `422` (session
accepted, body rejected). So the **session cookie worked**; the blocker is the
undocumented request body of the web image endpoint. Do NOT keep guessing
payloads after session acceptance — fall back to Route A/C.

## Feature-flag check (do this BEFORE investing in Route B)
The saved page HTML (and bootstrap JSON) exposes capability flags. Grep:
```python
import re
txt = open(html).read()
for m in re.finditer(r'.{40}(image_gen_enabled|image_gen_limit_window_mins|dalle_limit_window_min).{10}', txt):
    print(m.group(0))
```
Observed on **ChatGPT Go**: `"image_gen_enabled":false`. With that flag false,
the web image route is disabled for the plan regardless of payload correctness.

## Header set that was accepted (session), for reference
```
authorization: Bearer <accessToken>
cookie: __Secure-next-auth.session-token=<sessionToken>
content-type: application/json
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
origin: https://chatgpt.com
referer: https://chatgpt.com/
accept: text/event-stream
openai-sentinel-chat-requirements-token: <sentinel>   # empty here because /requirements 404'd
```

## Takeaway
Route B (chatgpt.com web image endpoint) is reverse-engineered and fragile.
Prefer **Route A** (`OPENAI_API_KEY` + `api.openai.com/v1/images/generations`,
`model: gpt-image-1`/`dall-e-3`) for reliable output, or **Route C** (Obscura
browser, no extraction). Use Route B only when the user insists on spending
their ChatGPT subscription quota specifically.
