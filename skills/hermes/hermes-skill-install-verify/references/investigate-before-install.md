# Investigate BEFORE install — technique & case studies

The user repeatedly demands: *research + explain + risk-assess a skill BEFORE
running `hermes skills install`*. This is a standing workflow preference, not
a one-off. Embed it: never jump straight to install for a skill the user hasn't
seen assessed.

## Why it's hard
`hermes skills inspect "clawhub/<id>"` only shows a TRUNCATED preview (≈12
trailing lines cut). There is NO `--dry-run`, NO `--target-dir` probe flag, and
`inspect --json` returns empty for community skills. So you often CANNOT read
the full SKILL.md without installing. Work around it:

1. `hermes skills search <name>` → read the table (Name/Description/Source/Trust/Identifier).
2. `hermes skills inspect "clawhub/<id>"` → read preview + prerequisites + usage.
3. `web_search` the skill id + "github" / "ToS" / "ban" to find real risk reports.
4. BEST-EFFORT full source: `curl -fsSL "https://lobehub.com/skills/openclaw-skills-<id>" -o p.html` then `python` strip tags and grep for keywords (forex, requirements, cookie, auth, API key). ⚠️ This mirror 404s for MANY skills (ai-trading-backtester 404'd) — don't rely on it; fall back to web_search.
5. `web_extract` is UNRELIABLE here: the default ddgs backend returns
   "DuckDuckGo (ddgs) is a search-only backend and cannot extract URL content."
   When you need page text, prefer `curl | python` (strip tags + grep) over web_extract.

## Risk-assessment pattern for automation / third-party-UI skills
If a skill drives a third-party web UI (Playwright, browser automation):
- State plainly it likely VIOLATES that service's ToS (automation/scraping bans).
- `web_search` "<service> bans automation account" to find REAL ban reports
  before declaring risk. Evidence found this session: OpenAI ToS lists
  "bots, scrapers, or automation scripts" as suspension cause; Cloudflare
  blocks Playwright on ChatGPT; multiple Pro/Plus accounts banned w/o warning.
- Flag: such skills "preserve the browser session" → they store the USER's
  login cookies. Using a main account risks losing it. Recommend a throwaway
  account or an official API instead.

## Case study 1 — clawhub/chatgpt-image-generation (DECLINED risk)
Playwright automates ChatGPT web UI to batch-generate images. Community, 23
installs, no license. Risks: violates OpenAI ToS (ban risk, real reports),
stores user ChatGPT session cookies, needs Node + `npm i playwright` +
`npx playwright install chromium` (user had none), redundant with Hermes'
native `image_generate` (FLUX, no ToS issue). Veredict: not recommended.

## Case study 2 — clawhub/ai-trading-backtester (Forex mismatch)
AI backtester (backtrader/vectorbt/pandas) for A-share/HK/US EQUITY only.
Does NOT support Forex — wrong market for a Forex user. Also: backtest != live
trading, no broker connection. Lesson: check the supported MARKETS in the
description before assuming a skill fits the user's asset class.

## Deliverable shape when user says "explain before install"
1. What it is (1-2 lines) + registry facts (source/trust/version/installs).
2. How it works (steps).
3. Prerequisites the user must install.
4. Risks / ToS / ban evidence (HONEST, with real sources when available).
5. Does it actually help the user's stated goal? (e.g. Forex vs equity).
6. Recommend install / decline / alternative. Let the USER decide.
