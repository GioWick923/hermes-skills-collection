---
name: hermes-skill-install-verify
description: Install, debug, and verify Hermes Agent skills from the hub/official/clawhub registries on Windows — platform-exclusion pitfalls, binary prerequisites, dangerous-verdict blocks, and ad-hoc verification discipline.
version: 1.0.0
author: <USER> GAMES (via Hermes)
license: MIT
platforms: [windows, linux, macos]
---

# Hermes Skill Install & Verify (Windows-focused)

Operational playbook for `hermes skills install` when a skill won't show up,
won't run, or you need proof it actually works. Grown from real Windows installs
of llm-wiki, blogwatcher, duckduckgo-search, searxng-search, domain-intel,
parallel-cli, deep-researcher-rr, ai-newsletter-toolkit,
axiom-image-metadata-stripper.

## When to use
- `hermes skills install <x>` reported installed but `hermes skills list` does NOT show it.
- A skill is enabled but its command/binary is missing at runtime.
- An install is BLOCKED by a "dangerous" audit verdict.
- You edited a skill's code and must verify it works (not just "it ran").
- You need to confirm a skill is operational before relying on it in a pipeline.

## USER WORKFLOW RULE — investigate & explain BEFORE installing
The user's STANDING preference: for any skill they have not yet assessed,
RESEARCH + EXPLAIN + RISK-ASSESS it first, then let them decide. Do NOT run
`hermes skills install` first and explain after. Sequence:
1. `hermes skills search <name>` → table (Source/Trust/Identifier).
2. `hermes skills inspect "clawhub/<id>"` (full `source/<id>` form) → read
   preview, prerequisites, supported markets/asset class.
3. If preview is truncated and you need the full SKILL.md: try
   `curl -fsSL "https://lobehub.com/skills/openclaw-skills-<id>" -o p.html`
   then strip tags + grep (⚠️ 404s for many skills — fall back to web_search).
   `web_extract` is unreliable on the default ddgs backend ("search-only,
   cannot extract URL content") — prefer `curl | python`.
4. `web_search` the id + "ToS"/"ban"/"github" to find REAL risk/ban reports
   for automation/third-party-UI skills (Playwright, browser automation).
5. Deliver: what it is + registry facts + how it works + prerequisites +
   HONEST risks (with real sources) + does it fit the user's actual goal
   (e.g. Forex vs equity) + recommend install/decline/alternative.
Full technique + case studies: references/investigate-before-install.md

## Install flow (registry)
- Official: `echo y | hermes skills install official/research/<name>`
- ClawHub: `echo y | hermes skills install clawhub/<id>`
- If `install <name>` says "No exact match" because the display name has spaces,\n  use the full `source/<id>` identifier from `hermes skills search --json`\n  (the `identifier` field). `inspect` can also fail to resolve while\n  `install clawhub/<id>` still works.\n- After install, confirm with `hermes skills list | grep -i <name>`.

## PITFALL 1 — Windows platform exclusion (silent disappear) [HIGH]
A skill installed on Windows may NOT appear in `hermes skills list` if its
SKILL.md frontmatter says `platforms: [linux, macos]` (no `windows`). The
loader filters it out. The files ARE on disk; it just isn't "enabled".
FIX: add `windows` to the `platforms:` list, then re-list.
(Real case: searxng-search shipped `platforms: [linux, macos]`; adding
`windows` made it show as enabled.) Full recipe: references/windows-platform-exclusion.md

## PITFALL 2 — Binary not bundled (skill enabled, command missing)
Some skills only ship instructions; the binary must be installed separately:
- blogwatcher → `blogwatcher-cli`. Download `blogwatcher-cli_windows_amd64.zip`
  from GitHub releases, unzip to a PATH dir (e.g. `%LOCALAPPDATA%\hermes\bin`),
  then persist PATH with `setx PATH "..."`. Verify: `command -v blogwatcher-cli`.
- duckduckgo-search → `ddgs` CLI (usually already in the Hermes venv).
- parallel-cli → `pip install "parallel-web-tools[cli]"` + `parallel-cli login`
  (PAID service, free tier; needs API key). Not free like DDG/SearXNG.

## PITFALL 3 — Dangerous verdict blocks install (cannot override)
`hermes skills audit` may return `Verdict: DANGEROUS` (e.g. CRITICAL
exfiltration findings) for a community skill. `--force` does NOT override a
dangerous verdict — install is blocked and the skill is quarantined to
`skills/.hub/quarantine/`. Review the findings; patterns like
`fetch(`${apiBaseUrl}/...`)` are often FALSE POSITIVES for local-only web UIs
(backend on localhost). You cannot install it via CLI. Either decline, or
manually place reviewed files at your own risk. Also note: many such skills
target macOS/Apple Silicon and won't run on Windows anyway.

## PITFALL 4 — SearXNG needs SEARXNG_URL; public instances block JSON
`searxng-search` requires `SEARXNG_URL`. Public instances return 403/429 or
anti-bot pages for `?format=json`. Reliable path = self-host (Docker). Without
Docker on Windows, the skill stays installed-but-inoperable.

## PITFALL 5 — Code bug in a hub skill (axiom-image-metadata-stripper)
`strip_jpeg` had an off-by-2: `i += length - 2` should be `i += length`
(length already includes the 2 length bytes). The bad version CORRUPTS JPEG
output (PIL can't open it) even though it reports success. Fix + verify recipe
in references/axiom-jpeg-offby2.md. Hub-installed skills are PROTECTED — patch
on the user's machine only after explicit request, and keep the recipe here.

## PITFALL 6 — Skill-availability backup (preserve before hub removes it) [MEDIUM]
User may ask: "guarda este skill por si ya no llega a estar disponible en el hub"
(real case: asked to preserve `mt5-trading-assistant-pro` and `oanda-forex-trading`
"por si ya no llegan a estar disponibles"). The hub can remove/rename a skill;
once gone, `hermes skills install` can no longer fetch it.
FIX: install normally, then COPY the skill folder to an EXTERNAL backup dir
OUTSIDE `%LOCALAPPDATA%\hermes\skills\` so it survives Hermes-side changes:
```bash
BACKUP="$HOME/skills-backup-<topic>"
mkdir -p "$BACKUP"
cp -r "$LOCALAPPDATA/hermes/skills/<id>" "$BACKUP/"
find "$BACKUP" -name SKILL.md   # verify the copy landed
```
To restore later, copy the folder back into `skills/`. IMPORTANT: a backup alone
does NOT keep the skill enabled — restoring requires copying back and (on Windows)
confirming `platforms:` includes `windows` (Pitfall 1). Full recipe:
references/skill-availability-backup.md

## Verification discipline (ALWAYS after editing a skill's code)
1. Write a temp script to %TEMP% named `hermes-verify-<topic>.py`/`.sh`.
2. Use GENUINE valid inputs (e.g. a real PIL-generated JPEG/PNG/GIF) — do NOT
   hand-inject malformed segments; that makes "output unopenable" ambiguous and
   produces a false VERIFIED_FAIL (seen when re-checking the axiom JPEG fix: a
   hand-injected APP1 segment made PIL reject BOTH input and output, masking the
   real PASS). Test with a plain valid image first; only inject a secret AFTER
   confirming the plain-image pass.
3. Assert: input valid → tool runs rc=0 → output is valid/openable AND behavior
   changed as intended (e.g. secret string absent).
4. Print VERIFIED_OK / VERIFIED_FAIL, then DELETE the temp file.
Template: scripts/verify_skill_change.py

## Config notes
- llm-wiki: set `WIKI_PATH` in `.env` (default `~/wiki`).
- Skills live at `%LOCALAPPDATA%\hermes\skills\<name>\`.
- `hermes skills audit` re-scans and may surface a skill after a frontmatter fix.

## Overlap note
This complements the bundled `hermes-skills-management` skill (discover/search/
install mechanics). This skill adds the Windows-specific DEBUG + VERIFY layer
(platform exclusions, binary prereqs, dangerous-verdict handling, code-bug
fixes, and verification discipline) that the catalog skill does not cover.
