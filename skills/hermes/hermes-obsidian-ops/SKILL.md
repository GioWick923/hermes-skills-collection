---
category: hermes
name: hermes-obsidian-ops
description: "Minimal Obsidian operating layer for Hermes: safe capture, inbox preview, daily brief, and vault health. Uses Obsidian Skills for Markdown/Bases/Canvas conventions without adding another memory database."
version: 1.0.0
author: <USER> + Hermes
license: MIT
metadata:
  hermes:
    tags: [obsidian, inbox, daily-brief, vault-health, provenance]
    related_skills: [obsidian-skills, hermes-reliability]
---

# Hermes Obsidian Ops

## Source of truth
Obsidian Markdown is the visible canonical layer. GBrain is an index/retrieval layer. Do not create a second hidden vault or silently duplicate notes.

## Safe operations

```bash
python "$LOCALAPPDATA/hermes/scripts/obsidian_ops.py" capture "idea or note"
python "$LOCALAPPDATA/hermes/scripts/obsidian_ops.py" process-inbox
python "$LOCALAPPDATA/hermes/scripts/obsidian_ops.py" daily-brief
python "$LOCALAPPDATA/hermes/scripts/obsidian_ops.py" vault-health
```

`process-inbox` previews by default. Only use `--apply` when the note has a valid explicit `target` in frontmatter. Never overwrite existing notes without a diff/backup.

## Obsidian conventions
Use the installed `obsidian-skills` repository for Obsidian Flavored Markdown, properties, Bases, JSON Canvas, CLI, and clean web extraction. Prefer small atomic notes, wikilinks, provenance, confidence, and status fields.

## Routing
- quick ideas, captures, voice, links → `00-Inbox/`
- daily reports → `10-Diario/`
- projects → `20-Proyectos/`
- durable resources → `30-Recursos/`
- references and sources → `40-Referencias/`
- indexes/MOCs → `50-Indice/`
- durable agent/system memory → `Memorias/`

## Guardrails
No secrets in the vault. No automatic edits to canonical memory, projects, indexes, or personal notes. Generate preview/diff first. Keep GBrain and Obsidian roles distinct.

## GBrain sync pitfall (learned 2026-09-13, self-evolution cycle)
- `gbrain sync` imports only COMMITTED vault files; uncommitted/untracked notes are only counted+warned ("N uncommitted file(s) not synced…"), never imported. The vault drifts because daily notes rarely get committed (13→24 files, 09-09→09-13).
- Do NOT "fix" this by adding `--working-tree` to `cmd_sync_gbrain` in `scripts/hermes_obsidian_bridge.py`: gbrain `--working-tree` is **unsupported through serve-delegated sync**, and the nightly `gbrain-sync-vault` cron (like any sync while a live `gbrain serve` holds the PGLite lock) always delegates → the flag makes the sync fail with "--working-tree isn't supported through serve-delegated sync. drop the unsupported flag". It would REGRESS the 23:00 job. Verified by dry-run 2026-09-13.
- Real resolutions need a human/config decision (out of scope for safe script patches): periodically commit the vault, run the sync with `--no-delegate` / stopped serve, or `gbrain config set sync.include_working_tree true` (confirm it applies to the delegated path first).
