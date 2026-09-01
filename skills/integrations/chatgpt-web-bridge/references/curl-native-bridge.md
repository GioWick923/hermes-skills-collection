# curl-native-bridge.md — Route B when local Python has no working socket

When `python -c "import socket"` fails in the active interpreter (e.g. `_socket`
DLL load error on all `uv` Python versions on the Windows host), do NOT assert
Python is broken. Delegate the HTTP work to the **native Windows curl** binary
and keep Python only for pure parsing (no `import socket`/`urllib`/`requests`).

## Flow that worked (2026-07-12, chatgpt.com image bridge)
1. Extract tokens with Python **stdlib only** (`re`, `json`, `os`) — write them
   to TEMP files, never to stdout/context.
2. Drive the calls with `curl` from bash, reading tokens from the temp files.

### Step 1 — extractor (pure stdlib, no network)
```python
import re, json, os
HTML = r"C:/path/to/chatgpt_page.html"
TMP  = r"C:/Users/.../AppData/Local/Temp"
txt = open(HTML, encoding="utf-8", errors="replace").read()
m = re.search(r'<script[^>]*id="client-bootstrap"[^>]*>(.*?)</script>', txt, re.S)
boot = json.loads(m.group(1))
s = boot.get("session", {})
st = s.get("sessionToken")   # -> cookie
at = s.get("accessToken")    # -> Bearer  (fallback: auth.json openai-codex token)
open(os.path.join(TMP,"cg_session.txt"),"w").write(st or "")
open(os.path.join(TMP,"cg_access.txt"), "w").write(at or "")
print("HAS_SESSION_TOKEN", bool(st), "len", len(st or ""))
print("HAS_ACCESS_TOKEN",  bool(at), "len", len(at or ""))
print("RESULT", "TOKENS_READY" if st and at else "MISSING_TOKENS")
```

### Step 2 — curl driver (bash)
```bash
#!/usr/bin/env bash
set -u
TMP="C:/Users/.../AppData/Local/Temp"
ST=$(cat "$TMP/cg_session.txt")   # never echo these
AT=$(cat "$TMP/cg_access.txt")
BASE="https://chatgpt.com/backend-api"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
# Put headers in VARIABLES -- avoids bash 'unexpected EOF' on inline quoted -H
AUTHH=*** Bearer $AT"
COOKIEH="cookie: __Secure-next-auth.session-token=$ST"

# requirements (sentinel) -- may 404; sentinel stays empty then
curl -sS -o "$TMP/cg_req.json" -w "HTTP_STATUS=%{http_code}\n" \
  -X POST "$BASE/requirements" -H "$AUTHH" -H "$COOKIEH" \
  -H "content-type: application/json" -H "user-agent: $UA" \
  -H "origin: https://chatgpt.com" -H "referer: https://chatgpt.com/" \
  --data '{"conversation_mode":{"kind":"primary_assistant"},"kind":"init_image_generation"}'

SENT=$(grep -o '"token"\s*:\s*"[^"]*"' "$TMP/cg_req.json" | head -1 | sed -E 's/.*"token"\s*:\s*"([^"]*)"/\1/')
SENTH=""; [ -n "$SENT" ] && SENTH="-H openai-sentinel-chat-requirements-token: $SENT"

# conversation (body in a file -> --data-binary @file avoids quote hell)
curl -sS -o "$TMP/cg_gen.txt" -w "HTTP_STATUS=%{http_code}\n" \
  -X POST "$BASE/f/conversation" -H "$AUTHH" -H "$COOKIEH" \
  -H "content-type: application/json" -H "user-agent: $UA" \
  -H "origin: https://chatgpt.com" -H "referer: https://chatgpt.com/" \
  -H "accept: text/event-stream" $SENTH --data-binary @"$TMP/cg_body.json"

echo "GEN_BYTES=$(wc -c < "$TMP/cg_gen.txt")"
grep -oE 'https?://[^"\\\ ]+' "$TMP/cg_gen.txt" | grep -iE 'image|oaiusercontent|files/' | sort -u > "$TMP/cg_urls.txt"
echo "IMG_URL_COUNT=$(wc -l < "$TMP/cg_urls.txt")"
```

### Bash quoting gotcha (cost real debugging time)
Inline `-H 'authorization: Bearer *** inside single quotes leaves an
unterminated string -> `unexpected EOF while looking for matching`. Fix: assign
headers to shell variables and pass `-H "$VAR"`. Also: write JSON bodies to a
file and use `--data-binary @file` instead of `--data "$JSON"` when the JSON
contains double quotes.

### Cleanup
After the run, `rm` the temp token files (`cg_session.txt`, `cg_access.txt`,
`cg_req.json`, `cg_gen.txt`, `cg_body.json`, `cg_urls.txt`). Never persist
session tokens.
