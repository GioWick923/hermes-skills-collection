---
name: hermes-observational-memory
description: Portable 2-layer memory model (Observations + Reflections + Dropper + Recall) adapted from Pi's pi-observational-memory for Hermes Agent. Use proactively at session start (fold) and session end (observe/reflect/prune) to keep long sessions coherent without context-window compression loss. Use when a task spans many turns, multi-day work, or when you need durable facts separated from ephemeral event records.
---

# hermes-observational-memory (Skill)

Adapts the mental model of Pi's `pi-observational-memory` to Hermes' real tools
(`write_file`/`read_file`/`execute_code`/`terminal`/`memory`). Hermes has no Pi
runtime (no `turn_end` hooks, no `ctx.compact()`), so the AGENT drives the
lifecycle: it reasons, then calls the ledger engine to persist structure.

## Core model (from the source repo)

- **Observation** — timestamped event record from a session. Ephemeral-ish.
  `{id, timestamp, relevance(low|medium|high|critical), content, sourceIds}`.
  Examples: "user switched from REST to GraphQL", "bug traced to module X".
- **Reflection** — durable fact distilled from observations. Long-lived.
  `{id, content, supportingObservationIds}`.
  Examples: "project uses Next.js 15 + Supabase", "ship before Jan 22".
- **Drop** — tombstone removing an observation id from *active* memory.
  History is kept; id stays recallable.
- **Coverage** — how many reflections support an observation (none/partial/strong).
  Strong coverage (>=2) makes an observation eligible for pruning.
- **Recall** — recover source evidence for a 12-hex id (not semantic search).

## Lifecycle (agent-driven)

1. **SESSION START** -> load folded projection as context:
   `python scripts/leager.py fold`
   (Gives you reflections + active observations without re-reading raw history.)
2. **DURING / END OF SESSION** -> capture observations you notice:
   `python scripts/leager.py observe --content "..." --relevance high [--source OID]`
3. **PERIODICALLY / END** -> distill durable reflections:
   `python scripts/leager.py reflect --content "..." --supports OID OID`
   (A reflection should cite the observation ids whose meaning it preserves.)
4. **END** -> prune observations now strongly covered, to bound active memory:
   `python scripts/leager.py prune`
5. **ON DEMAND** -> inspect / recall:
   `python scripts/leager.py status`
   `python scripts/leager.py view [--full]`
   `python scripts/leager.py recall --id XXXXXXXXXX`

## Where it lives

Ledger: `%LOCALAPPDATA%/hermes/observational-memory/ledger.jsonl`
(preferred; engine falls back to `%APPDATA%` then `~/.hermes` if unset — so the
ledger always resolves next to the skills dir on Windows).
Engine: `scripts/leager.py` (Python stdlib only; no pip needed).
Verification: `python scripts/leager_verify.py` (isolated, ad-hoc; exits 0 on pass).

## Crash-safe writes (ported from oh-my-openagent memory-core, MIT)

`leager.py` v2 writes to the ledger under a **domain lock + fsync**, so a crash
or concurrent writer can never corrupt a line (fail-closed):

- **`memory-write.lock`** (O_EXCL, `0o600`) guarantees a single writer.
- **Append** writes the full line + `flush()` + `os.fsync()` → durable.
- **Stale-lock reclaim** via mtime TTL (300s); `PermissionError` on Windows is
  treated as contention (retry), not a fatal error.
- `_load()` skips unparseable lines (fail-closed) — reads never block.

Verificado 2026-08-31: 15 writers concurrentes × 3 rondas = 0 corrupción, lock
siempre liberado; `leager_verify.py` PASS.

## Why this helps Hermes

- Separates **what happened** (observations) from **what durably matters**
  (reflections) — Hermes' `memory` tool alone mixes both and never prunes.
- Proactive distillation means when context gets long, the folded projection is
  already ready -> less coherence loss, faster "compaction" (session handoff).
- Recall-by-id gives traceability: you can cite `why` you know something.

## Pitfalls

- The AGENT must do the reasoning; the engine only stores/validates. Do NOT put
  raw transcript dumps as observations — distill first.
- Keep reflections FEW and DURABLE. Don't reflect every observation.
- `prune` only drops observations with >=2 reflection coverage; manual `drop`
  exists for explicit tombstoning.
- IDs are deterministic hashes, not random — identical content+timestamp+index
  yields same id; fine for recall, but avoid feeding the exact same seed twice
  in one second.
- Cross-session: ledger persists on disk; load `fold` at start of every session
  to stay oriented.

## Pitfalls

- **APPDATA vs LOCALAPPDATA (Windows):** Hermes skills live under
  `%LOCALAPPDATA%/hermes/skills/...`, but many shells set `$APPDATA` to
  `%APPDATA%` (Roaming). If the engine resolves the ledger from `$APPDATA` it
  writes to Roaming while the skill expects Local — commands "can't find the
  file". The engine now prefers `$LOCALAPPDATA` and falls back to `$APPDATA`
  then `~/.hermes`, so always invoke a subcommand with a working dir under the
  skill, or set both env vars consistently. When testing, isolate both env vars
  to a temp dir (see `scripts/leager_verify.py`).
- **`--supports`/`--source` are repeatable flags**, not positional. Passing
  `2cc43d6d1ff4` as a bare arg after `reflect` errors with "unrecognized
  arguments". Repeat the flag: `--supports ID1 --supports ID2`.

## Verification

After any write command, run `status` and confirm counts increased as expected.
After `prune`, run `view` to confirm active observations shrank but `recall --id`
still returns dropped ones.

For ad-hoc isolated verification (never touches your real ledger), run:
`python scripts/verify.py` — it overrides APPDATA to a temp dir, exercises
observe/reflect/prune/recall/fold/status/drop, and asserts transitions. This is
the script used to verify the skill; keep it and re-run after any engine change.
