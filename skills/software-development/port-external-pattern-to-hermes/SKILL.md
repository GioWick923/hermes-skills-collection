---
category: software-development
name: port-external-pattern-to-hermes
description: "Use when the user points at an external repo (GitHub, often a different agent ecosystem like Pi) and asks to 'learn from it / port it / do the same for Hermes'. Covers the mandatory consult-before-execute discipline, honest portability assessment, building on existing Hermes tools, and isolated ad-hoc verification."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skill-authoring, porting, repo-analysis, verification, workflow]
    related_skills: [hermes-agent-skill-authoring, hermes-skill-integration, hermes-observational-memory, hermes-subagent-orchestration]
---

# Porting an External Pattern into a Hermes Skill

## Overview

Users sometimes hand you a GitHub repo from *another* agent ecosystem (e.g. Pi's
`pi-*` extensions) and ask you to "learn from it," "port it," or "do the same for
Hermes." The valuable output is usually the **pattern/method**, not a literal
port — because Hermes already has its own runtime and tools.

This skill encodes a discipline that was missed once: the agent read a repo's
docs and jumped to proposing, silently dropping the user's agreed
"study-then-consult" flow. Capture it so every future port starts correctly.

## When to Use

- User pastes a repo URL and says "aprende de esto", "haz lo mismo para Hermes",
  "porta esto", "estudia y me dices qué haremos".
- You are about to create a skill whose design is inspired by an external project.
- Don't use for: installing an existing hub skill (`hermes-skill-integration`),
  or authoring a from-scratch skill with no external reference (`hermes-agent-skill-authoring`).

## Mandatory Sequence (consult-before-execute)

1. **Re-affirm the rule in your FIRST message.** State explicitly: *"Recuerda:
   leo, aprendo y te consulto ANTES de ejecutar."* Then study. Never read docs
   and jump straight to a proposal — that silently drops the agreed flow.
2. **Read the docs, not just the README.** Pull `README.md` + every file under
   `docs/` via `curl -sL https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`
   through the terminal. (See Pitfalls: `web_extract` cannot read raw GitHub.)
3. **Honestly assess portability — two buckets:**
   - **Capability Hermes ALREADY has** → do NOT reimplement it. Example:
     `delegate_task` already runs non-blocking parallel subagents, so a Pi
     subagent-spawner's *mechanism* needs no port — only its *orchestration
     pattern* (roles, caller_ping, /plan) is worth capturing.
   - **Pattern worth porting** → the method/structure, modeled with `write_file`
     + Python stdlib scripts invoked via `terminal`, state persisted as JSONL.
4. **Report evolution + REAL improvement, THEN stop.** Before any code:
   - What you learned.
   - Whether it's implementable here.
   - What the improvement actually is (mark each candidate as 🟢 already-have /
     🟡 real-improvement / 🔴 decoration-you-should-skip).
   - Why you previously forgot to consult (own the miss).
   - Present the plan and WAIT for the user's "ejecuta" / choice.
5. **Build only the approved parts.** Prefer a MINIMAL version first if the user
   offers it; skip decorative features (e.g. a simulated UI widget when Hermes
   has no panes).
6. **Verify ad-hoc, isolated.** Ship a `scripts/verify.py` that overrides
   `APPDATA` to a temp dir so the real state file is never touched; assert state
   transitions; delete it after. See `hermes-observational-memory` /
   `hermes-subagent-orchestration` for reference `verify.py` implementations.

## Completion Criteria

- User saw the assessment AND the plan before any file was written.
- The skill reuses an existing Hermes capability rather than duplicating it.
- A verify script passed against an isolated state (not the real ledger).
A simulated widget you'll never look at is ruido — skip it unless the user wants it.

## Concrete Recipe: Porting OpenHands `skills/*.md` → Hermes Skills

OpenHands (80k⭐, `OpenHands/OpenHands`) ships reusable **skills** (V1) / **microagents**
(V0) as Markdown files in `skills/*.md` plus repo-private `.openhands/microagents/`
and `.agents/skills/*/SKILL.md`. These are pure *content* (prompts/knowledge), NOT an
executable runtime — so they port cleanly to Hermes as read-only knowledge skills.

**Frontmatter translation (this is the actual port work):**
- OpenHands V1: `name:` + `description:` → already compatible with Hermes. ✅
- OpenHands V0 microagent: `triggers: [list]` → Hermes has no `triggers:` field.
**Move the trigger keywords INTO `description:`** so Hermes' skill matcher fires on them.
e.g. `triggers:\n- /codereview` → `description: ... Trigger keywords: /codereview, review PR, code review.`
- If a file has no usable title (no H1, no `description`, no triggers), derive one from
the first heading and WRITE an explicit keyword-rich description — otherwise the skill
loads as `available` but is "deaf" to the matcher (silent miss). Always verify.

**Batch port script pattern** (run via `terminal` with `python`, NOT via write_file's
in-tool path — see Pitfall 6 about the Windows path bug):
```python
import os, re, json, urllib.request
SKILLS = ["code-review","security","docker","kubernetes","github","gitlab","ssh","npm","fix_test","update_pr_description"]
BASE="https://raw.githubusercontent.com/OpenHands/OpenHands/main/skills/"
OUT="C:/Users/<user>/AppData/Local/hermes/skills/"   # note: forward slashes, no leading /c/
def fetch(u):
 r=urllib.request.Request(u,headers={"User-Agent":"hermes-port"})
 return urllib.request.urlopen(r,timeout=30).read().decode()
# ... read each, reempack frontmatter name+description, write OUT/<name>/SKILL.md
```
Verify each ported skill by calling `skill_view(name=...)` and asserting
`readiness_status == "available"` (and that `description` contains real keywords).
The OpenHands catalog is discoverable via the GitHub contents API:
`https://api.github.com/repos/OpenHands/OpenHands/contents/skills`.

**What you do NOT get by copying `.md`:** the OpenHands runtime (autonomous agent in a
Docker sandbox, GitHub/GitLab/Jira webhook integrations). Those require option B — running
OpenHands itself as a subagent (docker pull + delegate_task), not a file copy.

### Option B — Mount OpenHands LIVE as a Docker subagent (real isolation)

This is the capability-copying-`.md` can't give you: OpenHands executing code in its own
sandbox. Recipe validated this session:

1. **Precondition check first (honest-block discipline — Pitfall 7).** Before claiming you
   can run it, verify in the terminal: `docker --version` (must exist), the model API key is
   present (`grep OPENROUTER_API_KEY "$LOCALAPPDATA/hermes/.env"`), and disk space. If Docker
   is absent, STOP and tell the user the install path — do NOT simulate output.
2. **Install Docker Desktop (Windows):** `winget install Docker.DockerDesktop
   --accept-package-agreements --accept-source-agreements --silent` (background, ~500 MB).
   Requires a **Windows reboot** + first-launch accept of terms before `docker` works.
3. **Run OpenHands** against OpenRouter (the Hermes `.env` key works as the LLM key):
   ```bash
   docker run -it --rm --pull always \
     -e SANDBOX_RUNTIME_CONTAINER_IMAGE="docker.all-hands.dev/all-hands-ai/runtime:latest" \
     -e LLM_MODEL="openrouter/tencent/hy3:free" \
     -e LLM_API_KEY="$OPE...EY" \
     -e LLM_BASE_URL="https://openrouter.ai/api/v1" \
     -v "$HOME/openhands-workspace:/workspace" \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -p 3000:3000 \
     docker.all-hands.dev/all-hands-ai/openhands:latest
   ```
   UI at `http://localhost:3000`. The key is read from Hermes' `.env` at runtime, never
   echoed. A ready-to-run wrapper lives at `templates/start_openhands.sh` — copy it,
   `bash start_openhands.sh`, and the sandbox isolation is real (code runs in-container).
4. **Wire it as a Hermes subagent** with `delegate_task` (role=leaf) only AFTER the container
   is proven reachable; the container is the executor, Hermes is the orchestrator.

## Common Pitfalls

1. **`APPDATA` vs `LOCALAPPDATA` (Windows).**
   `%LOCALAPPDATA%\hermes\skills\` (Local), but the MSYS/bash terminal resolves
   `$APPDATA` to **Roaming**. A skill script doing `cd "$APPDATA/hermes/..."`
   or reading `os.environ["APPDATA"]` for its state will look in the wrong place.
   Fix: use `$LOCALAPPDATA` explicitly, or build paths with
   `os.path.expanduser("~")` + `AppData\Local`. To find a skill dir reliably,
   use `search_files(target='files', pattern='SKILL.md')`.

2. **`web_extract` cannot read GitHub raw / many URLs.** Its default backend is
   DuckDuckGo (search-only) and returns "cannot extract URL content." For raw
   files use `curl -sL https://raw.githubusercontent.com/...` via `terminal`.
   For rendered pages, `browser_*` tools need Chrome (`agent-browser install`);
   if absent, fall back to `curl`.

3. **Stale verification flagged by the system.** If you edit a skill's code, the
   harness may keep showing an OLD verify output. Re-run a FRESH isolated verify
   in the same turn you claim done, and clean up the temp script.

4. **Over-porting decoration.** If the source depends on a runtime/UI Hermes
   lacks (multiplexer panes, Pi hooks), port the *pattern* only. A simulated
   widget you'll never look at is ruido — skip it unless the user wants it.

5. **Memory bloat.** Don't save the whole technique to `memory` (it's for who/
   state). The skill file is the durable home; `memory` gets only a one-line
   pointer that the skill exists.

6. **Windows `write_file` / `patch` path duplication bug.** On this Windows host the
   `write_file` and `patch` tools inside the agent resolve a path like
   `/c/Users/<user>/...` to `C:\\c\\Users\\<user>\\...` (duplicate `c:` prefix), writing the
   file to the WRONG place (or failing to read it). **Workaround:** (a) write scripts with a
   plain relative name (e.g. `oh_port.py`) so they land in the terminal cwd
   (`C:\\Users\\<user>\\`), then run with `python oh_port.py`; OR (b) use `terminal` + in-line
   `python - <<'PY' ... PY` with `os.path.join`-built paths using forward slashes
   (`C:/Users/<user>/AppData/Local/hermes/skills/`) — these land correctly. Avoid absolute
   `/c/...` paths in `write_file`/`patch` tool arguments. `terminal`'s own bash handles
   `/c/Users/...` fine; the agent's file tools do not.

7. **Honest-precondition / honest-output discipline (Option B).** Before claiming you can run
   OpenHands (or any Dockerized tool), verify the precondition in the terminal for real:
   `docker --version`, that the API key exists, disk space. If Docker is absent, STOP and tell
   the user the install path — do NOT fake a successful run or invent container output. The
   install itself needs a Windows **reboot** + first-launch accept; that step is the user's, and
   you must hand off with the exact remaining manual steps rather than pretending completion.

## Support files
- `templates/start_openhands.sh` — ready-to-copy wrapper that reads OpenRouter key from the
  Hermes `.env` and launches OpenHands in Docker (`-p 3000:3000`, isolated `/workspace`).

## Verification Checklist

- [ ] First message re-affirmed "study-then-consult" before reading.
- [ ] README + docs/ read via curl (not web_extract).
- [ ] Assessment separated already-have vs real-improvement vs decoration.
- [ ] Plan shown; no code written before user approval.
- [ ] Skill uses existing Hermes tools (delegate_task, write_file, terminal).
- [ ] `scripts/verify.py` overrides APPDATA to temp and passes; temp cleaned.
- [ ] Pointer to verify.py added to SKILL.md.
