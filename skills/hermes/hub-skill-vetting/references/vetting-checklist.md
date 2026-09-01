# Hub Skill Vetting — Concrete Examples (from real sessions)

This file records actual vettings that produced durable lessons. Not a mirror of
upstream docs — just the patterns worth re-using.

## 1. ToS-violating web automation (chatgpt-image-generation)
- What it is: Playwright drives the ChatGPT **web UI** to generate images.
- Risk: Automating ChatGPT's UI violates OpenAI ToS. Documented account bans exist
  for "bots, scrapers, or automation scripts" on ChatGPT. Cloudflare also challenges
  Playwright sessions (latenode community report).
- Verdict: risky. Recommend `image_generate` (native FLUX, no ToS issue) instead, or
  the official OpenAI Images API. If installed anyway, use a throwaway account.

## 2. Market mismatch (ai-trading-backtester)
- Claims: quantitative backtesting. Lists A-share (China), HK, US equity only.
- User asked about FOREX → NOT supported. Forex needs broker feeds (OANDA/MT5), not
  yfinance equities. Skill is useless for FX as-is.
- Lesson: read the "supported markets" line in SKILL.md before claiming a skill fits
  the user's actual use case.

## 3. Third-party intermediary + paid credits (oanda-forex-trading)
- Connects to OANDA v20 API but ONLY through AgentPMT (a 3rd-party marketplace MCP).
- Credentials flow through AgentPMT, not direct to OANDA. Every action costs "2
  credits". Requires AgentPMT account + MCP server; inert in plain Hermes.
- Lesson: flag skills that depend on an external paid intermediary. Better path:
  write a direct Python client to the provider's official API (no intermediary).

## 4. Windows load-pitfall (searxng-search)
- Installed fine but never appeared in `hermes skills list` on Windows.
- Cause: SKILL.md `platforms: [linux, macos]` omitted `windows`.
- Fix: changed to `[linux, macos, windows]` → appeared as enabled. Keep `.bak`.

## 5. Off-by-2 corruption bug (axiom-image-metadata-stripper)
- Symptom: output JPEG failed to open in PIL though the tool reported success.
- Cause: in `strip_jpeg`, after keeping a non-metadata segment the loop did
  `i += length - 2` (double-subtracting the 2 length bytes). Correct: `i += length`.
- Fix applied + verified on a real valid JPEG (openable, metadata removed).
- Lesson: when a tool reports success but output is invalid, trust the verifier
  (PIL/open) over the tool's stdout. Off-by errors in byte-stream parsers are common.

## 6. Resolver source-prefix quirk (all clawhub installs this session)
- `hermes skills install <id>` failed to match names with spaces; needed
  `hermes skills install "clawhub/<id>"`. Same for official: `"official/research/<id>"`.

## 7. Activation honesty (hermes-self-evolution)
- Skill is installed but its SKILL.md states it does NOT self-execute. Needs
  `pip install -e .` (dspy, gepa) + `HERMES_AGENT_REPO` + ~$2-10/run API cost.
- Lesson: "installed" ≠ "active". Check the skill's own STATUS/setup notes before
  telling the user it's running.
