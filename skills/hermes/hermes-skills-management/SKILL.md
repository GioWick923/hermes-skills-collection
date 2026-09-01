---
name: hermes-skills-management
description: Discover, evaluate, and install Hermes Agent skills (official hub, community repos, discovery hubs) and connect MCP servers — including the non-interactive install workaround required for automation/background runs.
tags: [hermes, skills, install, mcp, discovery]
---

## Triggers
- User asks to "find/browse/install Hermes skills", "busca skills", "instala skill X", or wants to extend capabilities.
- User wants MCP servers connected to Hermes ("dame MCP", "conecta MCP", "configura MCP").
- User pastes a list of skill names to install in batch.

## Verified skill sources (July 2026)
See `references/sources.md` for the live list with URLs and skill counts.

Official:
- Skills Hub: https://hermes-agent.nousresearch.com/docs/skills/
- Skills system docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/

Community repos (SKILL.md format, compatible):
- Undermybelt/hermes-skills — 1422 skills (red-teaming 757, community 494, devops incl MCP, software-dev 65, mlops 5) + a `scripts/validate_skills.py` safety validator.
- itgoyo/hermes-skills — 310+ skills (academic, apple, marketing, design, finance, game dev, MLOps).

Discovery hubs (browse/rank/review):
- Agentskills.io, SkillHub (CN), 虾评 Xiaping (reviews/rankings), hermes-ai.net/skills (unofficial multi-language index).

## Steps
0. **CHECK FIRST whether the skill is already present (bundled/builtin).** Run
   `hermes skills list` and grep for the name. If its `Source` column shows
   `builtin` or `bundled` and `Status` is `enabled`, **STOP — do NOT run
   `hermes skills install`**. Installing from the hub creates a PARALLEL
   "community" copy that conflicts with the official one (duplicate name,
   divergent behavior). The skill is already on disk at
   `AppData\Local\hermes\skills/<category>/<name>/` (Windows) and ready to use.
   Only proceed to install when the skill is genuinely absent, or when the user
   explicitly wants the hub/community variant.
1. Install a known skill by name:
   `hermes skills install <name>`
   Resolves from skills.sh/nousresearch/hermes-agent, runs a security scan (SAFE verdict), then prompts `Confirm [y/N]`.
2. **NON-INTERACTIVE install (required for background / automation / cron / delegate):**
   `echo "y" | hermes skills install <name>`
   Without piping `y`, the install CANCELS in any non-interactive shell.
3. Verify: confirm files at `~/AppData/Local/hermes/skills/<name>/` (Windows) — SKILL.md + any scripts/ present.
4. Bulk from a community repo:
   `git clone <repo> && cd <repo> && python3 scripts/validate_skills.py` — review warnings, then `rsync -an skills/ ~/.hermes/skills/` dry-run before the real copy.
5. MCP (optional): ensure extras with `cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"`, then add an `mcp_servers:` block in config.yaml (filter tools per server) and reload with `/reload-mcp`.

## Pitfalls
- **Install prompt cancels when no TTY.** Always pipe `echo "y" | hermes skills install <name>` outside an interactive terminal (background tasks, cron, subagents). This is the #1 failure mode — a bare call silently reports "Installation cancelled" with exit 0.
- **`hermes skills install` can HANG (separate from the TTY prompt) on this Windows host.** Even with `echo "y" |`, the command sometimes blocks on a slow/unresponsive network fetch and emits no output until the shell timeout (60–240s) fires — and the skill is then NOT on disk. The non-interactive `echo y` workaround does NOT fix a hang. Reliable fallback that always works: download the official repo zip and extract just the skill folder to `%LOCALAPPDATA%\hermes\skills\<category>\<name>\`. Exact procedure + MSYS/Windows path gotchas in `references/install-from-github.md`.
- **Bundled skills often need an external binary (prerequisite) the skill does
  NOT install.** The skill shows enabled but fails at runtime until the binary
  exists. Check the SKILL.md `prerequisites: commands:` field. Real case:
  `blogwatcher` (research) requires `blogwatcher-cli`. If `command -v <bin>` is
  empty, fetch the matching OS binary and put it on PATH:
  - Windows: the GitHub release often ships a `<repo>_windows_amd64.zip` that is
    NOT listed in every SKILL.md install section. Check the releases API:
    `curl -sL https://api.github.com/repos/<owner>/<repo>/releases/latest` and
    grab the `*_windows_amd64.zip`. Unzip into `AppData\Local\hermes\bin`, then
    add that dir to the USER PATH persistently: read current value from
    `reg query HKCU\Environment /v Path`, then run
    `cmd //c "setx PATH <cur>;<dir>"`, then verify `<bin> --version` in a fresh
    shell.
  - Verify functional with a real command (e.g. `blogwatcher-cli add "xkcd"
    https://xkcd.com && blogwatcher-cli scan`) — it should return output, not
    "command not found".
- Don't bulk-install blindly from community repos. Run the validator and read scan output first. `supply_chain MEDIUM` warnings on `pip install` lines are expected/normal for OCR/PDF skills, not a block — just know the skill will pip-install deps at use time.
- The built-in scanner returns "Allowed (community source, safe verdict)" but you should still review installed files before relying on them (third-party skills can influence agent behavior).
- `web_extract` may fail with "DuckDuckGo is search-only backend / cannot extract URL content". Fall back to `curl -sL https://raw.githubusercontent.com/<owner>/<repo>/<branch>/README.md` to read repo READMEs directly.
- **WINDOWS `platforms:` FRONTMATTER TRAP (install reports OK but skill is invisible).** Symptom: `hermes skills install <name>` says "Installed" / "already installed", the files DO exist at `AppData\Local\hermes\skills/<name>/` (SKILL.md + scripts), yet `hermes skills list` does NOT show the skill. Root cause: the SKILL.md frontmatter `platforms:` field omits `windows` (e.g. `platforms: [linux, macos]`), so the loader FILTERS IT OUT on Windows hosts. This is pure metadata — the actual skill logic (bash/curl scripts) usually works fine in git-bash regardless. Fix: patch the frontmatter to add `windows`:
  `platforms: [linux, macos, windows]`
  then re-run `hermes skills list` to confirm it now appears as `enabled`. Real case this session: `official/research/searxng-search` shipped `platforms: [linux, macos]` and was invisible until the field was widened; `duckduckgo-search` worked because it already listed `windows`. After any such patch, verify with a real `hermes skills list | grep <name>` (the list reads `%LOCALAPPDATA%\hermes\skills`, NOT `~/.hermes/skills`, on this host).
- **Both `hermes skills list` and disk live under `%LOCALAPPDATA%\hermes`, NOT `~/.hermes`.** On this Windows host `~/.hermes` exists but the active skills dir is `C:\Users\<user>\AppData\Local\hermes\skills`. If a skill looks "missing" check the right path first.
- Browser tools may be unavailable (Chrome not installed on this host) — prefer `curl` over `browser_navigate` for fetching page content here.

- **COMMUNITY INSTALL CAN FAIL TO RESOLVE THE NAME (use the full identifier).** `hermes skills install <name>` sometimes reports `No exact match for '<name>'. Did you mean one of these?` even when the skill exists in the hub. This happens because the search/display output truncates the real `Identifier` and the resolver matches on the display `Name`, not the id. Fix: copy the **Identifier** column (not the Name) from `hermes skills search <keyword>` output and install with the source prefix, e.g. `echo "y" | hermes skills install "clawhub/deep-researcher-rr"` or `echo "y" | hermes skills install "official/research/searxng-search"`. Searching by the bare keyword (e.g. `audio2srt`, `deep-researcher`, `ai-newsletter`) works; searching by the `source/name` form (e.g. `clawhub/audio2srtlocal`) often returns "No skills found". Read the Identifier from the result, then install by that.
- **DANGEROUS VERDICT BLOCKS INSTALL AND `--force` DOES NOT OVERRIDE.** If the security scan returns `Verdict: DANGEROUS` (e.g. CRITICAL exfiltration / supply_chain findings), the install is **blocked** and `echo "y" | hermes skills install <name> --force` still fails with `Installation blocked: Blocked (community source + dangerous verdict, N findings). --force does not override a dangerous verdict.` The skill is quarantined to `.hub/quarantine/<name>` but on Windows the dir may end up EMPTY (the skill is discarded at block, leaving no installed files and no persistent trace). To "remove" it, just confirm absence: `hermes skills list | grep <name>` (should be empty) and `ls "$LOCALAPPDATA/hermes/skills/<name>"` (should not exist). Before telling the user it's unsafe, READ the scan lines — they are printed right above the block. They frequently flag benign patterns: a local Web-GUI skill that does `fetch(\`${apiBaseUrl}/api/...\`)` to its OWN localhost backend gets tagged `CRITICAL exfiltration` by the scanner (false positive). Judgment call: if the fetches target a localhost/embedded backend and the skill is otherwise benign, report it as likely-false-positive and let the USER decide whether to install manually from quarantine. Also note platform fit: skills written for Apple-Silicon/MLX (e.g. `audio2srtlocal`) will NOT run on Windows regardless, so dropping them is usually correct.

## Verification
- After install: `ls "$LOCALAPPDATA/hermes/skills/<name>"` (Windows) or `search_files` — confirm SKILL.md exists.
- Ask Hermes "show me available skills" or run `hermes skills list`.
- For MCP: `/reload-mcp` then ask "which MCP-backed tools are available right now?".
