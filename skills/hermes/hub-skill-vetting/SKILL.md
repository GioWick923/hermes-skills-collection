---
name: hub-skill-vetting
description: Evaluate Hermes hub skills for safety, compatibility, and real usefulness BEFORE installing. Covers the resolver source-prefix quirk (install fails to match when display name has a space), the Windows 'platforms:' load-pitfall (skill installs but never appears in 'hermes skills list'), and a ToS/risk checklist for account- or broker-connected skills. Use whenever the user asks to install a hub skill, or before running 'hermes skills install <id>'. Pair with hermes-skill-install-verify for post-install checks.
version: 1.0.0
---

# Hub Skill Vetting (pre-install evaluation)

Do NOT blind-install hub skills. Before `hermes skills install <id>`, vet it:
1. Inspect the skill and its real code/docs.
2. Check the resolver quirk and Windows load-pitfall below.
3. Run the risk/ToS checklist for anything that touches accounts, brokers, or external services.
4. Report findings in plain language + a glossary of unknown terms, then let the user decide.

This skill is about PRE-install vetting. Post-install verification (does it actually run?) belongs to `hermes-skill-install-verify`.

## Step 1 — Inspect before install
```bash
hermes skills search <term>            # find the exact identifier
hermes skills inspect <id>              # preview SKILL.md + metadata
```
If `inspect` shows a "No exact match" but lists the name, the resolver choked on the
display name (usually a space). Use the explicit source prefix (see Pitfall A).

For a deeper read of community skills whose preview is truncated, fetch the source
mirror (e.g. lobehub.com/skills/... or the project's GitHub) via curl + grep to scan
for: auth/cookie handling, external endpoints, data exfiltration patterns, supported
markets/platforms, and required credentials.

## Step 2 — Risk / ToS checklist (run for any skill touching accounts/brokers/APIs)
- 🔴 Does it automate a web UI that violates the provider's Terms of Service?
  (e.g. Playwright-driving ChatGPT web UI = ToS violation → account ban risk. Real
  bans are documented for bot/scraper automation of ChatGPT.)
- 🔴 Does it require YOUR credentials/API key and send them to a THIRD PARTY
  (not the official provider)? Flag the intermediary.
- 🟡 Does it claim support for a market/platform it doesn't actually cover?
  (e.g. an "AI trading backtester" that lists only A-share/HK/US equities, NOT Forex.)
- 🟡 Is it "community" trust with no license / low install count? Less audited.
- 🟢 Is it pure stdlib / no API key / no external calls? Lowest risk.
Always state the risk level and let the user decide. For risky-but-wanted skills,
recommend a throwaway/secondary account, never the user's primary.

## Step 3 — Activation honesty
Installed ≠ activated. Before telling the user a skill is "active", check its own
STATUS/setup notes. Some skills:
- need `pip install -e .` of bundled deps + an env var (e.g. HERMES_AGENT_REPO),
- cost money per run (API calls),
- require an external service/MCP server that isn't present.
If prereqs are unmet, say "installed and ready, but X is needed to actually run" —
do NOT claim activation you haven't verified.

## Pitfall A — Resolver source-prefix quirk (tool-usage pattern)
`hermes skills install <id>` (and `inspect`) can fail to resolve an identifier whose
DISPLAY NAME contains a space, even when the search lists it. The resolver matches on
the rendered name, not the raw identifier.
FIX: pass the explicit source prefix:
```bash
hermes skills install "clawhub/<id>"
hermes skills install "official/research/<id>"
```
This reliably resolves. (Confirmed pattern: chatgpt-image-generation,
ai-trading-backtester, forex-skill, mt5-trading-assistant-pro, oanda-forex-trading all
needed the `clawhub/` prefix to install despite appearing in search.)

## Pitfall B — Windows 'platforms:' load-pitfall (debug pattern)
Symptom: `hermes skills install` reports success, but the skill NEVER shows as
`enabled` in `hermes skills list` on Windows, even though its folder exists in
`%LOCALAPPDATA%\hermes\skills\`.
Root cause: the skill's SKILL.md frontmatter has `platforms: [linux, macos]` and
omits `windows`, so the loader filters it out on Windows.
FIX: add `windows` to the platforms list:
```yaml
platforms: [linux, macos, windows]
```
Then re-run `hermes skills list` — it now appears as `enabled`.
(Confirmed: searxng-search shipped as `[linux, macos]`; adding `windows` made it load.
The edit is to a hub-installed skill file on disk — allowed for a load fix; keep a
`.bak` backup first.)

## References
See `references/vetting-checklist.md` for the concrete examples from real vettings
(ToS-violating ChatGPT automation, Forex-unsupported backtester, third-party AgentPMT
OANDA dependency, axiom JPEG off-by-2 fix, searxng Windows pitfall).
