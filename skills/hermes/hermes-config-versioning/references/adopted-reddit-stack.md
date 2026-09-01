# Adopted Reddit Stack (r/HermesAgent) — knowledge bank

Condensed from a session where the user asked for Reddit community signals on
Hermes Agent config/skills and wanted them adopted step by step.

## Adoption list format (use this shape)
| # | Tool / patrón | Qué hace | Calificación |
Build a TABLE with columns: Tool | What it does | Signal found | How to implement | Recommendation (adopt now / later / watch / skip), each row tagged Direct/Indirect/Official/Inferred.

## The 4 adopted (signal: r/HermesAgent posts, read directly via old.reddit HTML)
1. **Git-versioned config** — `git init` in `AppData\Local\hermes`; security `.gitignore`
   (exclude `.env`/`auth.json`/`config.yaml`/`*.db`/`state.db`/`tools/`/`sessions/`/
   caches/`lsp/`/embedded `**/.git/`/per-minute `cron/ticker_*`); `git add .` (NOT `-A`
   → mmap fails on MSYS); `backup-state.sh` tars secrets+DB to ignored `backups/`.
2. **Second Brain** — `second-brain/README.md` (index) + `zettel/AAAA-MM-DD-tema.md`.
   Rule in every profile SOUL.md: reusable facts → zettel; durable prefs → `memories/MEMORY.md`.
   Consult via `search_files` (target=content), never load all into context.
3. **Ingest + morning digest (medium tier)** — `yt-dlp` in isolated venv
   (`uv venv tools/ingest_venv && uv pip install yt-dlp`); reuse `skills/watch-video/scripts/{download,transcribe}.py`;
   `ingest_url.py` → zettel in `second-brain/zettel/`; `morning_digest.py` as cron `0 8 * * *`
   sends new zettels to Telegram via `hermes message telegram <name>`.
4. **Voice dictation → structured doc** — skill `voice-idea-to-doc` (2-shot); `save_doc.py`
   → `docs/AAAA-MM-DD-tema.md`. Needs Telegram DM already `connected` (gateway_state.json).

## Reddit signals that were SKIP/warn (do not blindly adopt)
- GBrain — cited <25% retrieval in a community eval; prefer Hindsight/Mnemosyne.
- Hermes Channels fork — niche; only if native channels fail.
- Mnemosyne/gbrain compatibility — unconfirmed; treat as experimental.
- Jarvis/Kid Mode, 9Router — personal experiments, not priority.

## Community pitfalls surfaced
- Desktop app pins default profile to REMOTE gateway when using VPS; can't mix local+remote easily.
- Local thinking models (Qwen) loop on 30s title-generation timeout → pin a fast aux model.
- CCR redaction sometimes triggered by provider guardrails (e.g. OpenCode), not Hermes itself.
- ~15k initial tokens are by design (skills/tools/rules); cache on provider, not a bug.

## How to run the loop with this user
- Adopt ONE item at a time; verify before next. "vamos paso a paso".
- Always run an ad-hoc verification script (`hermes-verify-*.sh` in %TEMP%) after editing config, report as ad-hoc not suite green, then clean up.
