---
category: software-development
name: claude-code-free
description: "Run the Claude Code CLI for $0 using OpenRouter free models via a local Anthropic->OpenAI protocol proxy. Use when the user wants Claude Code without paying for Anthropic, or when wiring coding agents to free/open models."
platforms: [windows, linux, macos]
---

# Claude Code Free (via OpenRouter + local proxy)

## When to use
- The user wants to run **Claude Code** (the `claude` CLI) without an Anthropic paid subscription.
- You need a coding agent backed by a free/open model (e.g. `tencent/hy3:free`, `moonshotai/kimi-k2:free`, `meta-llama/llama-3.3-70b-instruct:free`).
- The naive approach from tutorials (`ANTHROPIC_BASE_URL=https://openrouter.ai/api/anthropic`) FAILS — see Pitfalls.

## Why the tutorial method breaks
OpenRouter's Anthropic-compatible endpoint (`https://openrouter.ai/api/anthropic`) returns **404** from many environments, and even when reachable, Claude Code rejects free model IDs it doesn't recognize. The robust fix is a **local proxy** that:
1. Listens for Claude Code's Anthropic-format `POST /v1/messages`.
2. Translates to OpenRouter's **OpenAI-compatible** `POST /api/v1/chat/completions` (which works).
3. Returns the response in Anthropic format.

## Setup (one-time)
1. Install Claude Code: `npm install -g @anthropic-ai/claude-code` (needs Node). Verify `claude --version`.
2. Get a free OpenRouter key: https://openrouter.ai/keys (format `sk-or-...`). Keep it as an env var, never hard-coded.
3. Place `scripts/proxy_anthropic_openrouter.py` and `scripts/claude-openrouter.sh` (see this skill's `scripts/`).

## Run (per session)
```bash
# Terminal 1 — start proxy (background; it binds 127.0.0.1:8081)
cd <skill>/scripts
OPENROUTER_KEY=sk-or-... OPENROUTER_MODEL=tencent/hy3:free \
  uv run --python 3.12 --with fastapi --with uvicorn --with httpx \
  python proxy_anthropic_openrouter.py

# Terminal 2 — launch Claude Code against the proxy
cd <skill>/scripts
OR_KEY=sk-or-... ./claude-openrouter.sh -p "tu prompt"
```
Non-interactive: `OR_KEY=... ./claude-openrouter.sh -p "..."` (proven working, returns model output).

## Files in this skill
- `scripts/proxy_anthropic_openrouter.py` — the local protocol translator (FastAPI/uvicorn).
- `scripts/claude-openrouter.sh` — sets `ANTHROPIC_BASE_URL=http://127.0.0.1:8081` and launches `claude`.
- `references/pitfalls.md` — MSYS/curl quoting, venv `_socket` corruption, terminal server-blocking, port zombies.

## Pitfalls (read references/pitfalls.md before debugging)
- OpenRouter `/api/anthropic` → 404. Always proxy through the OpenAI-compatible endpoint.
- Hermes venv Python has a broken `_socket` (DLL load fail) — run any networked Python via `uv run --python 3.12` in an isolated env.
- The Terminal tool blocks `uvicorn`/`uv run` as "long-lived" in foreground — always `background=true` for the proxy, then test separately.
- Port 8081 can be held by a zombie process; free it with `netstat -ano | grep :8081` + `taskkill /PID <n> /F`.
- In MSYS bash, `curl` with multiple `-H "..."` breaks quoting. Use `-H@<winpath>` with a header file, and `--data-binary @file.json` for the body.

## Verification
- Launcher: `bash -n` for syntax; stub `claude` to confirm `ANTHROPIC_BASE_URL`/`ANTHROPIC_API_KEY` propagate; must fail when `OR_KEY` unset.
- End-to-end: `OR_KEY=... ./claude-openrouter.sh -p "responde hola"` should print a model reply with exit 0.
- Ad-hoc verify scripts: put them under a `hermes-verify-` tempfile prefix, run, then delete.
