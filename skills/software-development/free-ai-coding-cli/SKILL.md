---
category: software-development
name: free-ai-coding-cli
description: "Run paid AI coding CLIs (Claude Code, Codex) for free by routing them to OpenRouter's Anthropic-compatible endpoint with a free model. Covers install, key setup, env-var redirection, and verification."
platforms: [linux, macos, windows]
---

# Free AI Coding CLI via OpenRouter

## When to use
- User wants to use Claude Code (or another Anthropic-API-speaking coding agent) but
  avoid Anthropic's paid API/subscription.
- Tutorials show "Claude Code for free" by pointing it at OpenRouter's free models.
- Any task where you must redirect a commercial AI coding CLI to an alternative
  (free or cheaper) provider.

Core trick: Claude Code (and compatible CLIs) read `ANTHROPIC_BASE_URL`,
`ANTHROPIC_API_KEY`, and `ANTHROPIC_MODEL`. Point `ANTHROPIC_BASE_URL` at
OpenRouter's Anthropic-compatible endpoint and supply an OpenRouter API key plus a
free model id. The CLI then "thinks" it talks to Anthropic but actually runs a free
open-source model. This generalizes to any CLI that speaks the Anthropic Messages API.

## Prerequisites
- Node.js (Claude Code needs it as runtime). Check: `node --version`.
- Git Bash (Windows) or any bash.
- An OpenRouter account + free API key: https://openrouter.ai/keys (format `sk-or-...`).
  Copy it once and store it safely — it cannot be re-viewed.

## Steps
1. Install Claude Code:
   - Linux/macOS: `curl -fsSL https://cli.claude.com/install.sh | bash`
   - Windows (npm): `npm install -g @anthropic-ai/claude-code`
     (PowerShell `irm https://cli.claude.com/install.ps1 | iex` fails if DNS for
     cli.claude.com is blocked; npm registry usually still resolves — use npm.)
   - Verify: `claude --version`
2. Verify the target free model exists:
   ```bash
   curl -s https://openrouter.ai/api/v1/models | python -c "import sys,json;d=json.load(sys.stdin);print([m['id'] for m in d['data'] if 'hy3' in m['id'].lower()])"
   ```
   Confirm e.g. `tencent/hy3:free` is in the list.
3. Confirm the Anthropic-compatible endpoint is reachable:
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" https://openrouter.ai/api/anthropic
   ```
   Expect `200`.
4. Launch with env vars (see templates/claude-openrouter-launcher.sh):
   ```bash
   OR_KEY=sk-or-... ./claude-openrouter-launcher.sh -p "hola"
   ```
   The launcher sets:
   - `ANTHROPIC_BASE_URL=https://openrouter.ai/api/anthropic`
   - `ANTHROPIC_API_KEY=$OR_KEY` (injected at runtime, NEVER stored on disk)
   - `ANTHROPIC_MODEL=${ANTHROPIC_MODEL:-tencent/hy3:free}`
   - `HTTP_REFERER` / `X_TITLE` (OpenRouter optional headers)

## Pitfalls
- **Do NOT store the API key in a file.** Inject via env var at runtime; the launcher
  reads `OR_KEY` and exports it. If you must persist it, put it in a `.env` outside
  shared paths and `chmod 600`.
- **Free models have rate limits and latency.** `tencent/hy3:free` is capable but
  slower and quota-limited vs paid Opus. First response can take 40s+ (cold start).
- **Newer Claude Code versions may demand an Anthropic login** even with custom base
  URL. If it blocks, set the env vars BEFORE launching `claude`, or use a community
  router (e.g. "Claude Code Router"). Verify the redirect worked by checking the
  model id in the first response line.
- **Model id must be exact.** Copy it verbatim from OpenRouter (e.g.
  `tencent/hy3:free`). A typo = silent failure / wrong model.
- **Tutorials misname models.** The popular video calls Kimi K2 "Kimiko 2.6" and
  Gemma variants "Gemma 431B" — use the real OpenRouter ids.
- **Verify after writing scripts.** A launcher shell script is easy to corrupt with
  placeholder typos (`***`, fused lines). Always `bash -n script.sh` and run an
  ad-hoc test with a `claude` stub that dumps the env (see Verification below).

## Verification (ad-hoc, not a test suite)
Before claiming success, prove the launcher wires the env correctly WITHOUT a real
key:
1. Create a temp `bin/claude` stub that writes `ANTHROPIC_*` vars to a file, `chmod +x`.
2. `PATH="$STUB:$PATH" OR_KEY=dummy bash launcher.sh`.
3. Assert `BASE_URL=https://openrouter.ai/api/anthropic`, `MODEL=tencent/hy3:free`,
   key present, referer set.
4. Live proof still requires the real key: `OR_KEY=sk-or-... ./launcher.sh -p "hola"`.

## Support files
- `templates/claude-openrouter-launcher.sh` — ready-to-use launcher.
- `references/openrouter-free-models.md` — endpoint, header rules, how to list models.
