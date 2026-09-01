---
category: hermes
name: hermes-config-versioning
description: "Version and back up Hermes Agent's own configuration (skills, profiles, SOUL.md, memories, cron, kanban) with git while excluding secrets/state — plus a safe tar backup for the parts git must never track. Use when the user wants to protect their Hermes setup, recover from a bad update, snapshot a multi-profile configuration, or 'back up my hermes config'."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, backup, version-control, config, git, secrets, profiles]
    related_skills: [hermes-agent]
---

# Hermes Config Versioning & Backup

## Overview
Hermes Agent stores a lot of valuable, hard-won config outside any version control: tuned `SOUL.md` files per profile, customized skills, memories, cron jobs, kanban boards. A bad update or a wrong edit can nuke weeks of tuning. This skill gives a closed-loop, **security-first** way to (a) git-version the safe parts and (b) tar-backup the secret/state parts git must never touch.

## When to use
- "back up my hermes config", "version my hermes setup", "snapshot my profiles"
- After building a valuable SOUL.md / skill and wanting it safe
- Before a Hermes update
- When running 2+ profiles and wanting change history

## Where Hermes config actually lives (Windows)
Do NOT assume `~/.hermes` is the gold mine — on this host it is nearly empty (just `plans/`, `plugins/`).
- **Real config root:** `C:\Users\<user>\AppData\Local\hermes` (a.k.a. `$LOCALAPPDATA/hermes`)
  - `config.yaml`, `.env`, `auth.json` — **SECRETS** (never commit)
  - `skills/` (global), `profiles/<name>/` (per-profile: `SOUL.md`, `profile.yaml`, `skills/`, `memories/`, `cron/`)
  - `memories/`, `cron/`, `kanban/`, `kanban.db`
  - `tools/` (154M+ runtime — exclude), `sessions/`, `state.db` (exclude)
- `AppData\Roaming\hermes` = Electron app cache only (`Local Storage`, `GPUCache`...). Do NOT version. **BUT** this same dir is where the **desktop GUI's own settings live** — in Electron `localStorage` (a LevelDB at `Roaming\hermes\Local Storage\leveldb`, key `hermes.desktop.<x>`). GUI settings are NOT in `config.yaml`. See `references/desktop-gui-settings.md`.
- **LOCK pitfall:** the Electron LevelDB is held exlusively by the running app. You cannot open/edit it externally while Hermes is open (`classic-level` → `LEVEL_DATABASE_NOT_OPEN`). Closing the app to edit it also kills the current chat session (TUI runs inside that process). For any GUI setting with a Settings control, give the user the in-app click path — do NOT try to hand-edit the LevelDB.
- **"cambialo tu" / "hazlo tu" preference:** when the user asks you to change a setting, *execute* it (backup first), don't just return steps. `config.yaml` is locked against `write_file`/`patch` — edit it via a `python` heredoc after `cp config.yaml backups/config.yaml.bak.<ts>`. GUI-localStorage settings you cannot reach externally: tell them the exact clicks, or use CDP if they relaunch with `--remote-debugging-port`.
- `AppData\Local\hermes\hermes-agent` = bundled repo (exclude).

## Workflow (closed loop)
1. `cd "$LOCALAPPDATA/hermes" && git init -q`
2. Drop the tuned `.gitignore` from `templates/hermes-gitignore.txt` into the root.
3. `git add .`  ← use `.`, NOT `-A` (see Pitfalls: mmap).
4. **Verify nothing sensitive is staged:**
   `git diff --cached --name-only | grep -iE '\.env$|auth\.json|config\.yaml$|\.db$|state\.db|tools/|sessions/' || echo "SAFE"`
5. Commit. Then run `scripts/backup-state.sh` for the secret/state parts → `backups/` (gitignored).
6. Re-run the check after every `.gitignore` tweak. Iterate until `git status --porcelain` is clean.

## Pitfalls (learned the hard way)
- **`git add -A` fails with `mmap failed: Invalid argument`** on MSYS/Windows when a large runtime dir (`tools/` 154M) is present. Use `git add .` (more efficient, same result) and `git config core.packedGitMMAP false`.
- **Embedded git repos inside skills** (`skills/hermes-self-evolution/repo`, `melodymine`, `skill-radar`, `watch-video`) produce "adding embedded git repository" warnings and bloat the repo. Ignore with `**/.git/`.
- **Stuck `index.lock`** ("Device or resource busy") when a `git` command times out: a prior process is still holding it. `rm -f .git/index.lock`, confirm no `git` lingers (`ps aux | grep git`), then retry.
- **Cron ticker files** (`cron/ticker_heartbeat`, `cron/ticker_last_success`) rewrite every minute and pollute `git status`. Ignore them explicitly.
- **Temp dir `/tmp` does NOT persist** between separate `terminal` calls on this MSYS host — write scratch/verify scripts under `$HOME` (e.g. `$HOME/hermes_scan/`), or inline them.
- **Never version `config.yaml`** even though it is "config" — it carries tokens/provider keys. If you want change history of settings, keep a hand-redacted `config.example.yaml`.

## Second Brain (desacoplar memoria de contexto) — Paso hermano
Versionar no basta: meter todo en `memories/MEMORY.md` infla el contexto de cada
sesión. Patrón adoptado (basado en r/HermesAgent "Need advice on Hermes memory"):

1. Crear `second-brain/` en el config root con `README.md` (índice maestro + reglas)
   y `zettel/` (una nota = un `.md` tipo `AAAA-MM-DD-tema.md`).
2. Regla para los SOUL.md de cada perfil: hechos/procedimientos reutilizables y
   estables → zettel en `second-brain/zettel/`; preferencias/identidad duras →
   promover a `memories/MEMORY.md`. Consultar bajo demanda con `search_files`
   (target=content), NUNCA cargar todo en contexto.
3. Mantener el README como índice (una línea por zettel).
4. Usar markdown + `search_files`, NO el skill de Obsidian: cero dependencias
   nuevas, reversible, y abre como vault en Obsidian si se quiere UI después.
5. El propio `second-brain/` se versiona en git (sin secretos: jamás poner tokens).
Template de zettel útil en `references/zettel-template.md`.

## Verification (ad-hoc, not a suite) — REQUIRED by runtime
El runtime de Hermes exige evidencia fresca de verificación tras editar archivos
de config/skills. Patrón operativo que funciona:
1. Escribir script temporal en `%TEMP%` con prefijo `hermes-verify-`
   (ej. `C:\Users\<user>\AppData\Local\Temp\hermes-verify-git-config.sh`).
   Usar ruta OS-safe tipo `tempfile`, NO `/tmp` (no persiste entre calls MSYS).
2. Ejecutarlo contra el repo vivo (`git status`, `git check-ignore`,
   `git ls-files`, `tar -tzf`, `grep` de secretos, conteo de commits).
3. Reportar explícitamente como "verificación ad-hoc, no suite green".
4. Limpiar el script temporal al terminar (`rm -f`).
Reusa `references/verify-snippet.sh` como base (cópialo a `%TEMP%` y corre).

Run contra el repo vivo para probar seguridad:
- `git status --porcelain` → must be empty (except intended).
- `for f in .env config.yaml auth.json state.db kanban.db tools/x sessions/x; do git check-ignore -q "$f" && echo OK:$f; done`
- `tar -tzf backups/hermes-state-*.tar.gz` → must list `config.yaml`/`.env`/`auth.json`/`*.db`.

## PC Migration Backup (tar both locations, verify old before restore)

When the user says "nos vamos a pasar a otra PC", "emigrar", "mudanza", or asks to
update an old `HermesMigration_*.tar.gz` backup: produce a FRESH snapshot of the CURRENT
state, do NOT restore the old one (it would overwrite newer skills/SOUL.md).

**What to capture (both locations exist on this Windows host):**
- `$LOCALAPPDATA/hermes` (the real live install: skills, profiles, config, cron, memories, SOUL.md) → `appdata.tar`
- Dotfiles in `$HOME` that carry config/cookies state → `home.tar`:
  `.hermes`, `.agent-reach` (Agent Reach cookies in `config.yaml`), `.opencli`,
  `.twitter-cli`, `.gbrain`, `.blogwatcher-cli`, `.mcporter`
- A `manifest.txt` with generation date + key integrations present (SOUL.md sections, skills, crons, model).

**Build order (script under `scripts/` or inline, NOT `write_file` with `/c/` paths):**
```
TS=$(date +%Y%m%d_%H%M%S)
OUT="$HOME/Pictures/HermesMigration_${TS}.tar.gz"
TMP=$(mktemp -d)
tar -cf "$TMP/appdata.tar" -C "$LOCALAPPDATA" hermes
tar -cf "$TMP/home.tar" -C "$HOME" .hermes .agent-reach .opencli .twitter-cli .gbrain .blogwatcher-cli .mcporter
# write manifest.txt into $TMP
tar -czf "$OUT" -C "$TMP" appdata.tar home.tar manifest.txt
rm -rf "$TMP"
```
Run in BACKGROUND (`terminal(background=true, notify_on_complete=true)`) — the skills dir is large (can take 2-5 min). The `.tar.gz` lands in `Pictures/` (Spanish Windows: `Imágenes` is a symlink/junction; `Pictures` is the real dir — verify with `ls`).

**Verify the OLD backup before trusting/overwriting it (critical pitfall):**
- `tar -tzf <old>.tar.gz` lists contents WITHOUT extracting. Always inspect first.
- Layout mismatch trap: an old backup may have been taken from `~/.hermes` (Linux-style) while the current host uses `AppData\Local\hermes`. Compare `SOUL.md` line counts and skill dirs (`comm -23 actual backup`) before deciding restore vs fresh-backup.
- Decision matrix offered to user: (1) create NEW backup, keep old intact [recommended]; (2) overwrite old; (3) extract-merge-repack old; (4) show diffs first.

**Restore on the new PC (hand off, user runs):**
```
cd ~/Pictures
tar -xzf HermesMigration_<TS>.tar.gz   # yields appdata.tar, home.tar, manifest.txt
tar -xf appdata.tar -C "/c/Users/<user>/AppData/Local/"
tar -xf home.tar   -C "/c/Users/<user>/"
```
Then reinstall externals whose binaries don't travel (agent-reach CLI, twitter-cli pipx,
opencli npm, Python venvs, Ollama) — but CONFIGS/COOKIES already landed. Verify with
`skills_list` (should show autonomous-ai-agents, engineering…) and `cronjob list`
(should show the 8 jobs).

## Reddit-adoption loop (practical list format)
When the user asks "what is the community adopting on Reddit", produce a TABLE, not a flat list:
`Tool | What it does | Signal found | How to implement | Recommendation (adopt now / later / watch / skip)`,
tagging each row with evidence strength (Direct / Indirect / Official / Inferred). Then **adopt chosen items ONE AT A TIME, verifying each before moving on** ("si ves que es mucho, vamos paso a paso"). Worked example (4 tools adopted from r/HermesAgent in one session): git-versioned config, second brain, YouTube/URL ingest + morning Telegram digest, voice-dictation → structured doc. See `references/adopted-reddit-stack.md`.

### Worked building blocks for the Reddit stack
- **Voice dictation → doc**: skill `voice-idea-to-doc` (2-shot: confirm skeleton, then fill) + `scripts/save_doc.py` → `docs/AAAA-MM-DD-tema.md`. Requires the Telegram gateway already `connected` (DM target). No gateway config needed if it's already up.
- **YouTube/URL ingest → zettel + digest**: reuse `skills/watch-video/scripts/{download,transcribe}.py`. Install `yt-dlp` in an ISOLATED venv (`uv venv tools/ingest_venv && uv pip install yt-dlp`) — do NOT touch Hermes' own venv. `ingest_url.py` downloads → parses VTT → summarizes → writes `second-brain/zettel/`. `morning_digest.py` (copied to `~/.hermes/scripts/`) runs as a cron (`0 8 * * *`) and sends new zettels to Telegram via `hermes message telegram <name>`.

## References / support files
- `templates/hermes-gitignore.txt` — drop-in security-tuned `.gitignore`.
- `scripts/backup-state.sh` — tars secrets/state into `backups/` (excluded from git).
- `scripts/make_migration_backup.sh` — PC-migration builder: tars `$LOCALAPPDATA/hermes` + dotfiles into `~/Pictures/HermesMigration_<TS>.tar.gz`. Run via `terminal(background=true)`.
- `references/desktop-gui-settings.md` — Hermes GUI settings live in Electron `localStorage` (LevelDB), not `config.yaml`; the LOCK constraint and safe change paths (in-app Settings vs CDP).
- `references/verify-snippet.sh` — ad-hoc verification script (run it after changes).
- `references/zettel-template.md` — template for a Second Brain zettel note.
- `references/adopted-reddit-stack.md` — condensed knowledge bank: the 4 Reddit-adopted tools, the adoption-list format, and the ingest/digest/voice building blocks.

## Memory consolidation pipeline (nightly fact extraction)

When the user has a `memory-consolidate` cron or asks for nightly fact extraction, this section governs the pipeline. The audit loop watches for drift; consolidation **extracts durable facts** from recent sessions so the agent starts oriented next session.

### Pipeline
```
1. QUERY      — pull session traces from state.db (last 24h)
2. EXTRACT    — distill 3-10 key facts (agent does the reasoning, no external model)
3. SCORE      — rate importance 1-10 (critical=10, trivial=1)
4. STORE      — high-value (>=7): MEMORY.md + observational ledger (+ gbrain)
5. DECAY      — low-value (<7): noted, not stored durably
6. SYNC       — gbrain put_page (if available); skip if Ollama embed offline
7. LOG        — append to EVOLUTION.md if structural changes detected
```

### QUERY — state.db schema for consolidation
Tables: `sessions(id, title, started_at REAL unix-ts, message_count)` and `messages(session_id, role, content, timestamp REAL, active INT)`. Filter: `started_at >= cutoff` and `message_count > 5` (idle sessions rarely yield facts). Pull `role='user' AND active=1` for highest signal — assistant messages contain the agent's own commentary.

### Score rubric
```
10 = Critical (security rule, architecture decision, user preference)
7-9 = Important (learned behavior, tool fix, config change)
4-6 = Useful (minor observation, one-time event)
1-3 = Trivial (greeting, routine check)
```

### Storage targets (priority order)
1. **MEMORY.md** — durable facts only, char budget ~2,200. Keep under 75% (~1,650 chars) to leave room for future entries.
2. **Observational-memory ledger** — append `{"type":"reflection",...}` entries. May live in `%APPDATA%` (Roaming) not `%LOCALAPPDATA%` on Windows — check both.
3. **gbrain** — `mcp__gbrain__put_page` if Ollama embed backend online.
4. **EVOLUTION.md** — append entry when structural changes detected.

### Pitfalls (learned from real consolidate runs)
- **gbrain requires Ollama embed:** `put_page` calls `embed(ollama:nomic-embed-text)` internally. If Ollama daemon is down, EVERY `put_page` fails with "Cannot connect to API". Do NOT retry 3x — skip gbrain, store in MEMORY.md + ledger.
- **MEMORY.md char budget:** `memory` tool rejects writes exceeding ~2,200 chars. Always check `len(content)` before writing.
- **Ledger path mismatch:** observational-memory ledger may resolve to `%APPDATA%/hermes/observational-memory/ledger.jsonl` (Roaming) not `%LOCALAPPDATA%`. Check both.
- **Don't extract greetings or system messages:** filter `[System:` and `hola`/`hey` from traces — they pollute the fact set.
- **`session_search` is FTS-based:** for consolidation you need chronological raw traces with timestamps, not semantic search. Use SQLite query directly.
