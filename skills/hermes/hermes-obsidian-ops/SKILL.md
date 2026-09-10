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
