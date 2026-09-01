---
name: third-party-skill-install
description: >
  Evaluate and install skills from an arbitrary GitHub repo into Hermes Agent
  WITHOUT running the repo's own installer. Covers the safe subset-install
  pattern (clone to temp, inspect, copy only selected skill dirs), the critical
  dependency check (many "skills" secretly require an external LLM API like
  Anthropic/OpenAI and will not run on an OpenRouter/Ollama-only stack), and
  file-based verification (since `hermes skills list` can hang on Windows).
  Use when the user points at a GitHub skill-pack and asks "should I install
  this" or "install this for me" — especially multi-skill repos.
---

# Third-Party Skill Install (Hermes Agent)

Install skills from any GitHub repo into Hermes *selectively and safely*. Do not
blindly run the repo's installer (`install.sh`/`install.js`/`npx skills add`) —
it may (a) install more than you want, (b) wire hooks/agents you don't use, or
(c) require a provider you don't have. Prefer the manual subset-copy pattern.

## When to use
- User says "analyze this repo / should I install it" about a skill-pack on GitHub.
- User wants only some skills from a multi-skill repo.
- You need to vet a skill's real dependencies before committing to it.

## Step-by-step (verified on Windows + git-bash)

1. **Clone to TEMP, never into Hermes.**
   ```bash
   cd /tmp && rm -rf skill_inspect && git clone --depth 1 <REPO_URL> skill_inspect
   ```
   Avoid `web_extract`/`web_search` for content — the default extract backend
   here is search-only and cannot fetch page bodies. Clone is reliable.

2. **Map the repo layout.**
   ```bash
   search_files(pattern='*', target='files', path='/tmp/skill_inspect', limit=100)
   ```
   Note where skills live (usually `skills/<name>/SKILL.md`) and whether there's
   an `install.js`/`install.sh` and a test matrix (e.g. `tests/installer/*.mjs`).

3. **Read the skill definitions** (`SKILL.md` + `README.md`) for each candidate.
   Judge per skill: does it add value on THIS user's stack? Does its behavior
   conflict with the user's mandated output format? (Example: a "speak tersely,
   no emoji, no tables" skill conflicts with a user who requires emoji + tables
   + a closing format — install the skill but keep its mode OFF.)

4. **READ THE SCRIPTS — dependency check (CRITICAL).** Many "skills" are not
   offline prompt files; they shell out to an LLM. Grep the scripts for:
   - `anthropic`, `ANTHROPIC_API_KEY`, `claude --print`, `claude --` → needs Anthropic
   - `openai`, `OPENAI_API_KEY` → needs OpenAI
   - `subprocess`, `fetch`, `requests` to an external host
   If a skill requires a provider the user does NOT have configured, it will
   either fail or silently exfiltrate the user's data to that provider. **Flag
   this before installing/automating.** Do not run it until adapted to the
   user's stack, or the user confirms a target file + that the endpoint is live.

5. **Selective copy to Hermes.** Destination base:
   - Windows: `%APPDATA%\hermes\skills\` (i.e. `C:\Users\<user>\AppData\Roaming\hermes\skills\`)
   - Honors `HERMES_HOME` env var if set (some installers use it).
   Put each skill in a **category subfolder** (the installer convention uses
   `productivity/`). Copy only the chosen dirs:
   ```bash
   SRC="/tmp/skill_inspect/skills"; DST="$APPDATA/hermes/skills/productivity"
   mkdir -p "$DST"
   for s in caveman-commit caveman-review caveman-compress; do
     rm -rf "$DST/$s"; cp -r "$SRC/$s" "$DST/$s"
   done
   ```
   Overwriting an existing dir is fine (clean copy). Symlink/recursive copy must
   preserve `scripts/` subfolders — verify they landed.

## Verification (do NOT rely on `hermes skills list`)
- `hermes skills list` **hung for 120s** on this Windows host (appears
  interactive/network). Don't block on it.
- Verify by direct file inspection instead:
  ```bash
  for s in caveman-commit caveman-review caveman-compress; do
    head -1 "$DST/$s/SKILL.md"   # must be '---' (YAML frontmatter)
    ls "$DST/$s/scripts" 2>/dev/null && echo "scripts OK"
  done
  ```
- Skills load from disk at Hermes startup; they activate next session.

## Pitfalls / lessons
- **External-LLM dependency is the #1 gotcha.** A skill that "compresses
  markdown" may actually POST your notes to Anthropic via `claude --print`.
  Inspect `compress.py`/`*.js` before trusting it. See `references/caveman-pack.md`.
- **Don't auto-activate conflicting modes.** Install useful sub-skills
  (commit/review generators that YOU produce text for) but leave the repo's
  "persona/style" skill OFF if it fights the user's required format.
- **Automation needs the dependency satisfied.** A weekly cron for a skill that
  needs Anthropic will just fail/leak. Gate the cron on a real target file + a
  live endpoint you control.
- **Uninstall symmetry matters.** Some installers had regressions where
  `--uninstall` orphaned skill folders. Manual copies are trivially removable
  (`rm -rf` the dir) — another reason to prefer the copy pattern.

## See also
- `references/caveman-pack.md` — concrete analysis of the `JuliusBrussee/caveman`
  skill-pack: what's useful on a non-Anthropic stack vs what silently needs
  Anthropic API access.
