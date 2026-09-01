# Pitfalls — Claude Code Free via OpenRouter proxy

## 1. OpenRouter /api/anthropic returns 404
The tutorial method (`ANTHROPIC_BASE_URL=https://openrouter.ai/api/anthropic`) does NOT work
from most environments — that route returns an HTML "Not Found" page (HTTP 404). The
OpenAI-compatible endpoint (`https://openrouter.ai/api/v1/chat/completions`) DOES work with
free models. Always proxy Anthropic-format requests through the local translator.

## 2. Free model IDs rejected by Claude Code
Even when the Anthropic endpoint is reachable, Claude Code may reject `tencent/hy3:free`
("It may not exist or you may not have access to it"). The local proxy bypasses that check
because Claude Code only validates that the endpoint responds — the model is chosen server-side
by the proxy, not by Claude Code's own allowlist.

## 3. Hermes venv Python has broken _socket
`import urllib.request` / `httpx` in the Hermes agent venv raises
`ImportError: DLL load failed while importing _socket: %1 no es una aplicación Win32 válida.`
Fix: run any networked Python via an isolated env, e.g.
`uv run --python 3.12 --with fastapi --with uvicorn --with httpx python proxy_anthropic_openrouter.py`

## 4. Terminal tool blocks "long-lived" commands
The Terminal tool (Hermes) refuses foreground commands it detects as servers/watch (it flags
the words `uvicorn`/`uv run`). Always start the proxy with `background=true`, then test with a
separate foreground call. Verify readiness by polling `curl http://127.0.0.1:8081/` (404 is
expected; only `/v1/messages` is served) or by running the end-to-end Claude Code test.

## 5. Port 8081 zombie
If a previous proxy was killed but held the socket, the next start fails with
`[Errno 10048] error while attempting to bind ... 8081 ... solo se permite un uso de cada
dirección`. Free it:
```
netstat -ano | findstr :8081
taskkill /PID <pid> /F
sleep 2
```

## 6. MSYS bash quoting breaks curl with multiple -H
In Git-Bash/MSYS, `curl -H "x: a" -H "y: b" --data '...'` throws
`unexpected EOF while looking for matching `"'`. Workarounds that work:
- Put headers in a file and use `curl -H@<winpath>` (NOT `-H @` with a space; NOT a `/tmp/...`
  MSYS path — use the Windows path, e.g. `C:\Users\...\headers.txt`).
- Put the JSON body in a file and use `--data-binary @file.json`.
- Or just test the proxy with a Python `urllib.request` script (but see pitfall #3 about _socket;
  use `uv run --python 3.12` or a known-good Python).

## 7. Keep the API key out of files
Pass `OPENROUTER_KEY` / `OR_KEY` via environment variable at launch. Do NOT write the key into
the launcher or proxy files. If a .bat is needed for the user, read the key from a
user-only-readable file (e.g. `%LOCALAPPDATA%\hermes\scripts\.openrouter_key`).

## 8. Verify, don't assume
After editing the launcher, re-run an ad-hoc verify (tempfile prefix `hermes-verify-`):
- `bash -n launcher` for syntax
- stub `claude` that dumps env to confirm BASE_URL + API_KEY propagate
- must exit non-zero when OR_KEY unset
- end-to-end: `OR_KEY=... ./claude-openrouter.sh -p "hola"` returns model text, exit 0
Clean up temp files after. State explicitly it is ad-hoc, not a CI suite.
