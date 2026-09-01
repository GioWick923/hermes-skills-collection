---
name: hermes-self-optimizing-loop
category: hermes
description: Audits Hermes health and auto‑fixes common drifts.
---

# Hermes Self‑Optimizing Loop

**Purpose**: Run a closed‑loop watchdog that audits the Hermes ecosystem, automatically repairs typical issues (dirty git, excess config backups, oversized MEMORY.md), re‑audits to confirm health, and produces a final markdown report.

## How it works (script `scripts/fix_hermes.sh`)
1. Execute `scripts/audit_hermes.sh` and capture output.
2. **Git fix** – if `git status --porcelain` shows changes, `git add -A && git commit -m "Auto‑commit: fix dirty state after audit"`.
3. **Backup pruning** – keep only the three newest `config.yaml*.bak*` files, deleting older ones.
4. **Memory truncation** – if `MEMORY.md` exceeds ~85 % of the 2 200‑char limit, truncate to the last 1 500 bytes.
5. Re‑run the audit; if any `REVISAR` remains, exit with error; otherwise output the final healthy report.

## Cron example (daily at 02:00, Telegram delivery)
```bash
cronjob action=create \
  name="Hermes auto‑optimiser" \
  schedule="0 2 * * *" \
  no_agent=true \
  script="fix_hermes.sh" \
  deliver=origin
```
This schedules the fixer to run each morning, keeping Hermes tidy without manual intervention.

## References
- `scripts/audit_hermes.sh` – health‑check script (see skill **hermes-self-audit**).
- `scripts/fix_hermes.sh` – the automated fixer implemented by this skill.

---
