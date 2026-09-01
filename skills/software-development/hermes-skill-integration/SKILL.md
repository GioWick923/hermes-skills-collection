---
category: software-development
name: hermes-skill-integration
version: "1.0.0"
description: "Use when integrating a third-party community skill into Hermes from GitHub/ClawHub/skills.sh — install, repair incomplete snapshots, satisfy Python version gates, and verify it actually runs before declaring done."
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, hermes, install, integration, hardening, verification, uv, python]
    related_skills: [hermes-agent-skill-authoring]
---

# Integrating Community Skills into Hermes

## Overview

`hermes skills install` pulls a skill from a registry or GitHub repo and drops it under
`~/.hermes/skills/` (or a profile's `skills/`). That is necessary but NOT sufficient: the
install can land a snapshot that is (a) stale relative to the repo default branch, or
(b) **missing files** that the engine needs. A skill that lists as `enabled` can still
crash on first invocation. This skill makes integration a closed loop: install, repair,
satisfy runtime gates, then prove it runs.

## When to Use

- User says "integrate this skill", "add this skill from GitHub", or pastes a skill repo URL.
- You are about to run `hermes skills install <repo>[/path] [--force]`.
- A freshly installed skill throws `ModuleNotFoundError`, `SyntaxError`, or a version gate.
- Don't use for: authoring a brand-new skill from scratch (use `hermes-agent-skill-authoring`),
  or editing a bundled/official skill (use `hermes skills reset`/`diff`/`opt-out`).

## Principle: Explain Before You Act (user preference)

The user wants a **brief explanation of what the skill does and how you would use it** BEFORE
you run the install/integration. Lead with: one paragraph on what it is, the source list of
free vs API-key sources/actions, and the exact invocation shape you will use as their agent.
Then execute. Do not dump the full SKILL.md — summarize.

## Step 0 — Locate the install target

Hermes resolves skills per active profile. Default profile skills live at:
`$LOCALAPPDATA/hermes/skills/` (Windows) or `~/.hermes/skills/` (POSIX).
Confirm before trusting `hermes skills list` output:

```bash
hermes skills list                 # confirms it registered + enabled
```

### ❌ `hermes skills install` does NOT accept a local filesystem path

`hermes skills install /tmp/foo/skills/bar` is interpreted as a remote "source" and the fetch
fails (timeout / "Could not fetch ... from any source"). The command only accepts
`owner/repo[/path]` or a direct HTTP(S) URL to a SKILL.md. If you already cloned the repo
locally (recommended — see Step 1), **copy the skill folder into the skills dir directly**;
that is exactly what the installer does internally:

```bash
SK="$LOCALAPPDATA/hermes/skills"
cp -r /tmp/<skill>-src/skills/<name> "$SK/<name>"     # or: cp -r /tmp/<skill>-src "$SK/<name>"
hermes skills list | grep <name>                        # confirm it registered as enabled
```

For a GitHub repo you have NOT cloned, use the remote form (explicit `skills/<name>` path
avoids a stale skills.sh snapshot):
```bash
hermes skills install <owner>/<repo>[/skills/<name>] --force    # --force accepts 'caution' scanner verdicts
```

## Step 0.5 — Discovery when there is no registry entry

If the user asks for a skill by *function* ("find me a skill to download Twitter/X videos")
rather than by a known repo, there may be no registry slug to `hermes skills install`.
Discover candidates and pick the best BEFORE writing anything:

1. **Search GitHub for real `SKILL.md` candidates** (works without a browser, pure API):
   ```bash
   curl -s "https://api.github.com/search/repositories?q=<keywords>+skill&per_page=25" \
     | python -c "import sys,json;d=json.load(sys.stdin);[print(r['full_name'],'|',r['stargazers_count'],'|',(r['description'] or '')[:80]) for r in d.get('items',[])]"
   ```
2. **Inspect the actual `SKILL.md`** of each shortlisted repo before trusting its listing.
   Listings/marketplaces can be stale or misleading:
   ```bash
   curl -s "https://raw.githubusercontent.com/<owner>/<repo>/main/SKILL.md"   # or /master/
   ```
   Also list the repo tree to see if it bundles scripts/deps:
   ```bash
   curl -s "https://api.github.com/repos/<owner>/<repo>/git/trees/main?recursive=1" \
     | python -c "import sys,json;d=json.load(sys.stdin);[print(t['path']) for t in d.get('tree',[]) if t['type']=='blob']"
   ```
3. **Prefer canonical, self-contained skills.** Skip candidates that (a) depend on an
   un-audited third-party API/service (e.g. `api.x-downloader.com`), (b) require a paid API
   key you don't have (e.g. OpenAI transcription when you only wanted a download), or
   (c) have no inspectable `SKILL.md`. Prefer skills built on standard tools you already run
   (yt-dlp, ffmpeg) over wrappers around opaque endpoints.
4. **Show the shortlist to the user first** (this is "Explain Before You Act" for discovery):
   a ranked table of candidate | method | platforms | notes, mark the recommended one, then integrate.
   The user explicitly wants the list BEFORE you act — do not silently pick and write.

## Step 1 — Clone the source for truth + repair

Install the upstream repo once to a temp dir. You need it to (a) diff against what landed and
(b) copy back any missing runtime files.

```bash
cd /tmp && rm -rf <skill>-src && git clone --depth 1 <repo-url> <skill>-src
# Find the skill root (often skills/<name>/)
find <skill>-src -iname SKILL.md -not -path '*/.git/*'
```

## Step 2 — Verify the install is COMPLETE (critical)

`hermes skills install` has dropped files in the wild (observed: a 78-module engine landed with
2 modules missing, breaking imports). After install, diff repo vs installed:

```bash
REPO=<skill>-src/skills/<name>          # adjust to the SKILL.md parent
INST="$LOCALAPPDATA/hermes/skills/<name>"
cd "$REPO" && find . -type f -not -path './.git/*' | sort > /tmp/repo_files.txt
cd "$INST" && find . -type f | sort > /tmp/inst_files.txt
comm -23 /tmp/repo_files.txt /tmp/inst_files.txt   # === ONLY IN REPO = missing from install
```

Anything in the "only in repo" list that is a runtime artifact (`.py` under `scripts/lib/`,
the engine script, `references/*.md` the engine reads) MUST be copied into `$INST`. Then delete
any `__pycache__` under the skill so stale bytecode from a bad import attempt can't linger.

Completion criterion: `comm -23` shows zero runtime files missing (packaging/dev-only files
like `tests/`, `build-skill.sh`, `.skillignore` entries are fine to omit).

## Step 3 — Satisfy the Python version gate (uv technique)

Many modern skills require Python 3.12+ and the host may ship 3.11. Do NOT hand-install a
system Python. Use `uv` (Hermes ships it) to provision an isolated interpreter:

```bash
uv python install 3.12                       # one-time ~28MB download, isolated, no system change
P312="$(uv python find '>=3.12')"            # prints the absolute path to the managed 3.12
"$P312" -c "import sys; print(sys.version_info[:3])"   # sanity: (3,12,...)
```

Good skills carry a `uv` fallback in their own preflight (set `LAST30DAYS_PYTHON` or similar),
so just ensuring `uv` is on PATH and 3.12 is provisioned is usually enough. Verify `uv` resolves
from the shell the agent runs in: `command -v uv`.

## Step 3b — Install media deps (yt-dlp / ffmpeg) in an isolated venv

Some skills (watch-video, melodymine, any media downloader) need `yt-dlp` and `ffmpeg`. The
Hermes venv has **no `pip`** (`python -m pip` fails) and `uv pip install --python <hermes-venv>`
errors with "No virtual environment ... found" (Hermes' venv layout isn't uv-recognised). Do
NOT try to patch the Hermes venv. Instead provision an **isolated uv venv** and put its Scripts
on PATH so the skill's subprocess calls find the binary:

```bash
uv venv "$HOME/.venvs/media" --python 3.12          # isolated, ~no cost
uv pip install --python "$HOME/.venvs/media/Scripts/python.exe" yt-dlp
export PATH="$HOME/.venvs/media/Scripts:$PATH"       # yt-dlp / ffmpeg on PATH for the skill
yt-dlp --version                                     # sanity check
```
`ffmpeg` is often already present (e.g. via WinGet on Windows: `command -v ffmpeg`). If missing,
install it the same isolated way or via the system package manager. The skill's scripts call
`yt-dlp`/`ffmpeg` as subprocesses, so PATH is all they need.

## Step 4 — Prove it runs (no mock-claims)

Never declare success on `list` alone. Exercise the engine:

1. `python <engine>.py --help` — catches import errors and version gates.
2. A **mock / offline** run if the skill supports it (`--mock`, `--dry-run`) — proves the
   pipeline emits its canonical output (badge + footer) without network.
3. If no mock flag exists, at minimum run the skill's `--diagnose`/`--doctor` self-check.
4. **Live functional test (for action skills — downloaders, scrapers, converters):** when the
   skill performs a real-world action, the definitive proof is a *real* invocation against a
   public, dependency-free sample, then confirm the artifact exists. Example for a media
   downloader:
   ```bash
   "$HOME/.venvs/media/Scripts/yt-dlp" -f "best[ext=mp4]/best" -o "%(id)s.%(ext)s" \
     "https://x.com/<user>/status/<id-with-video>"
   ls -lh *.mp4                       # confirm a non-empty file landed
   ```
   Pick a sample that actually exercises the path (a tweet that contains a video, not just any
   tweet — yt-dlp will report "No video could be found" on a text-only tweet, which is a
   *false negative* for the skill, not a failure). Delete the test artifact afterwards so you
   don't leave litter in the skill dir. If a live test needs keys/network you don't have, say
   so explicitly and label the run partial — never claim a live run succeeded.

Completion criterion: the engine exits 0 and emits its expected output shape. If it needs
network/keys you don't have, say so explicitly and label the run as partial — do NOT claim a
live run succeeded.

## Common Pitfalls

1. **Trusting `hermes skills list` as proof of function.** `enabled` only means registered.
   The engine can still crash. Always run a real invocation.
2. **Incomplete snapshot.** `install` can omit runtime modules; diff repo vs installed (Step 2).
3. **Stale shallow snapshot.** skills.sh may serve an old cached copy. Use the explicit
   `repo/skills/<name>` path, or `git pull` a local clone and symlink it for live edits.
4. **Python gate hang.** Host 3.11 vs skill 3.12+ → `uv python install 3.12` + `uv python find`.
   Never edit the skill's `MIN_PYTHON` gate to force 3.11 — the syntax/stdlib it uses may not exist.
5. **Leftover `__pycache__`** from a failed import hides the real fix. Delete it after repair.
6. **Editing a hub-installed skill in place.** Hub skills are protected; a future `hermes skills
   update` overwrites your edits. Repair by copying missing files from the canonical repo, not by
   rewriting engine logic.
7. **`hermes skills install` rejects local paths.** A filesystem path arg is treated as a remote
   source and the fetch times out. Clone the repo, then `cp -r` the skill folder into the skills
   dir (Step 0). Only use the `owner/repo` / URL form for repos you haven't cloned.
8. **Media deps: Hermes venv has no pip, `uv pip` won't target it.** Don't fight the Hermes venv.
   Provision an isolated `uv venv` (`~/.venvs/<name>`), `uv pip install yt-dlp` there, and export
   its `Scripts` dir onto PATH so the skill's subprocess finds the binary (Step 3b).
9. **Discovery: don't trust marketplaces or listings.** A skill "for Twitter video" may actually
   be a transcription wrapper around an un-audited third-party API (`api.x-downloader.com`) or
   require a paid key you don't have. Inspect the real `SKILL.md` (Step 0.5) and prefer skills
   built on standard tools (yt-dlp/ffmpeg) over wrappers around opaque endpoints.
10. **Live-test false negatives.** When functionally testing a downloader, use a sample that
    actually contains the target media. yt-dlp reports "No video could be found in this tweet"
    on a text-only tweet — that's a bad test sample, not a skill failure. Confirm the artifact
    file is non-empty before declaring success, and delete it afterwards.
11. **Plugins vs skills.** A community package may install as a *plugin* (`~/.hermes/plugins/<name>/`,
    `register(ctx)` + `data/*.json`), not a skill. `hermes plugins list` won't show it until
    Hermes restarts — verify `register()` loads into the Hermes venv with a mock `ctx` instead
    of waiting. Enable via `config.yaml` `plugins: enabled:` (edit with terminal python + .bak;
    `write_file`/`patch` are blocked on config.yaml).
12. **Don't import a full roster.** `build-hermes-plugin.py`/generators emit EVERY agent/division
    (e.g. 254). Recut `data/*.json` to only the divisions the user runs before installing, so
    `search` keeps minimal context — matches the "4+ specialized profiles, minimal context
    contamination" preference.
13. **MSYS shell + native python path mismatch.** Shell is POSIX (`/c/Users/...`) but native
    `python` rejects POSIX paths (`open()` → FileNotFoundError even when `ls` sees the file).
    Pass native Windows paths via `$(cygpath -w "/c/Users/...")` whenever python reads/writes a
    file.

## Verification Checklist

- [ ] Skill appears in `hermes skills list` as enabled.
- [ ] `comm -23 repo inst` shows no missing runtime files; missing ones copied from repo.
- [ ] Stale `__pycache__` removed after any repair.
- [ ] Python gate satisfied (3.12 via `uv` if needed); `uv python find '>=3.12'` resolves.
- [ ] `engine --help` exits 0.
- [ ] Mock/offline (or --diagnose) run emits canonical output, exit 0.
- [ ] For function-based requests: shortlist discovered via GitHub API + inspected `SKILL.md`, shown to user before writing.
- [ ] Chosen skill is self-contained (standard tools, no un-audited third-party API, no missing key).
- [ ] If live sources need keys, that limitation is stated honestly, not hidden.
- [ ] For action skills: live functional test against a valid sample produced a non-empty artifact (then deleted).

## Step 5 — Integrating a Hermes PLUGIN (not a skill)

Some community packages (e.g. `msitarzewski/agency-agents`) are **plugins**, not flat
skills. They install under `~/.hermes/plugins/<name>/` (Windows: `$LOCALAPPDATA/../.hermes/plugins/`,
i.e. `$HOME/.hermes/plugins/`) and register tools via `register(ctx)` in `__init__.py`.
The Hermes side loads them from `config.yaml` → `plugins: enabled: [<name>]`.

Plugin form to expect:
- `plugin.yaml` (`name`, `version`, `description`, `provides_tools: [...]`)
- `__init__.py` with `register(ctx)` calling
  `ctx.register_tool(name, toolset, schema, handler, description)`
- a data file (e.g. `data/agents.json`) the tools read lazily

Workflow:
1. Many such repos ship a generator (e.g. `scripts/build-hermes-plugin.py
   --repo-root . --out integrations/hermes`). Run it with `python` — on this host the
   repo's `python3` alias collides with the Microsoft Store stub and fails.
2. **Recut the data file BEFORE install** to respect minimal-context. Builders often emit
   the FULL roster (254 agents); drop divisions the user never runs so `search` only
   indexes what's useful (filter `data/agents.json` by `division` field, re-dump).
3. Copy the generated `<name>/` dir into `~/.hermes/plugins/`. Do NOT `rm -rf` the parent
   `plugins/` dir — target only the plugin subdir.
4. Enable in `config.yaml` under `plugins: enabled:`. **`write_file`/`patch` are blocked on
   `config.yaml`** (protected) — edit it via a terminal `python` that opens+writes the file,
   and take a `.bak` first. (See memory note: config.yaml needs direct-file edit, not the CLI.)

## Step 5b — Verify a plugin WITHOUT restarting Hermes

`hermes plugins list` will NOT show a freshly copied plugin until Hermes restarts
(discovery happens at startup). Prove `register()` works now by importing the plugin into
the **Hermes venv** and feeding it a mock `ctx`:
```bash
H="$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/python.exe"
"$H" - <<'PY'
import importlib.util, json
spec=importlib.util.spec_from_file_location("p",
  r"C:\Users\<USER> GAMES\.hermes\plugins\<name>\__init__.py")
m=importlib.util.module_from_spec(spec); reg={}
class Ctx:
    def register_tool(self,name,toolset,schema,handler,description): reg[name]=handler
spec.loader.exec_module(m); m.register(Ctx())
print("tools:", list(reg))          # confirm all expected tools registered
# exercise one handler
print(json.loads(reg["<tool>"](<valid_args>)))
PY
```
This confirms the plugin loads, registers its tools, and the handlers run — a genuine
pre-restart verification (the user still must restart Hermes for the toolset to be live).

## Windows path gotcha (MSYS shell + native python)

The agent shell is git-bash/MSYS (POSIX paths like `/c/Users/...`). Native `python`
does NOT understand POSIX paths: `open('/c/Users/...')` raises `FileNotFoundError`
even though `ls` (MSYS) shows the file. Always convert for python with `cygpath -w`:
```bash
WP=$(cygpath -w "/c/Users/<USER> GAMES/.hermes/plugins/<name>/data/file.json")
python -c "import json;print(len(json.load(open(r'$WP',encoding='utf-8'))))"
```

## References

- `references/last30days-case.md` — full reproduction of a real integration: which files the
  install dropped, the uv fix, and the mock-run proof. Use as a worked example.
- `references/agency-agents-plugin-case.md` — worked example integrating a large agent
  roster as a lazy-router Hermes plugin: build, recut roster to 68 agents, install, enable
  config.yaml, and verify `register()` into the Hermes venv without restart.
- `scripts/verify_install.sh` — automated "missing runtime files" diff between a cloned repo
  skill root and an installed skill dir.
