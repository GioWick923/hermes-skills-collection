---
name: gtm-obsidian-vault
description: Setup GTM Obsidian vault with receipt notes.
trigger: "when building a GTM (Go‑to‑Market) knowledge base in Obsidian"
summary: "Set up an Obsidian vault structured for GTM workflows using receipt‑based notes and organized clusters."
---

# GTM Obsidian Vault Setup

## Overview
Creates an Obsidian vault for GTM (Go‑to‑Market) knowledge base. Uses receipt‑based notes, organized clusters, and agent integration.

## Steps
1. Create `Obsidian_GTM_Vault` folder.
2. Create subfolders: `offer`, `buyers`, `voice`, `market_map`, `rooms`, `workflows`, `rulings`, `prospects`, `signals`, `messages`, `metrics`, `glossary`, `hub`.
3. In each folder, add a `hub.md` index file.
4. Add a README with methodology (see `references/vault_structure.md`).
5. Populate receipts (50‑150 words) with front‑matter (`type`, `tags`, `created`, `source`, `confidence`).
6. Link notes, maintain a glossary.
7. Enable Graph view groups by path.
8. Run agents (Claude Code) inside the vault; respect rulings.
9. Loop: review hubs/rulings before work, write back after.

## Pitfalls
- Missing source field.
- Over‑large receipts.
- Unreferenced rulings.
- Graph clutter.

## Verification
- Verify folder and subfolders exist.
- Check each `hub.md` header.
- Run `git status` if version‑controlled.

## References
- `references/vault_structure.md` contains the exact folder layout and README content.
