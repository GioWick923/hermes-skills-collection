---
category: hermes
name: hermes-self-audit
description: "Set up and operate a zero-cost self-audit watchdog for the Hermes ecosystem (skills, profiles, cron, memory, state.db, second brain) via a no_agent cron + a bash health script. Use when the user wants Hermes to 'watch itself', 'audit itself', 'stay in order', 'self-monitor', or 'optimize/clean up the agent setup'."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, self-audit, watchdog, cron, health, hygiene, monitoring]
    related_skills: [hermes-config-versioning, hermes-closed-loop-engineering]
---

# Hermes Self-Audit (Watchdog)

## Overview
A "super agent" is not just many skills — it is a system that **watches its own health** and tells you when something drifts. This skill sets up a recurring, **zero-token-cost** watchdog: a `no_agent=True` cron that runs a bash health script and delivers the report (markdown) to Telegram. The agent builds/verifies the script; the cron then runs it forever with no LLM spend.

Use this when the user asks Hermes to keep itself organized, audit itself, clean up, or become a self-managing agent.

## When to use
- "quiero que te audites solo", "que el sistema se mantenga en orden", "self-audit", "watchdog".
- After a big config/skills change, to confirm drift is caught.
- As the closing step of any "optimize my Hermes" session.

## Where things live (Windows)
Config root: `$LOCALAPPDATA/hermes` (a.k.a. `C:\Users\<user>\AppData\Local\hermes`).
- `skills/` — global skills (level 1 `skills/name/SKILL.md` AND level 2 `skills/cat/name/SKILL.md`).
- `profiles/<name>/` — multi-agent personas (orchestrator, reviewer, builder, researcher, optimizer, prompt, voice, writer...).
- `memories/MEMORY.md` — capped at ~2,200 chars.
- `cron/jobs.json` — job definitions.
- `config.yaml` + `config.yaml*.bak*` — live config + redundant backups (hygiene target).
- `state.db` — grows over time; watch its size.
- `second-brain/` — optional second brain / gbrain vault.

## Workflow (closed loop)
1. **Write the health script** to `$LOCALAPPDATA/hermes/scripts/audit_hermes.sh` (reuse `scripts/audit_hermes.sh` from this skill as the base). It must print a markdown report to stdout.
2. **Verify the script runs correctly NOW:**
   `bash "$LOCALAPPDATA/hermes/scripts/audit_hermes.sh"; echo "EXIT=$?"`
   Confirm `EXIT=0` and a sane report. Do NOT trust a first draft — see Pitfalls (the `find` bug).
3. **Create the watchdog cron** (zero cost):
   `cronjob action=create name="Hermes self-audit" no_agent=true script=audit_hermes.sh schedule="0 22 * * *" deliver=origin`
   `no_agent=true` = the script's stdout is delivered verbatim, no LLM call.
4. **Verify the cron truly fires (E2E, not just "scheduled"):**
   `cronjob action=run job_id=<id>` → confirm `execution_success: true`.
5. If the report shows drift (git dirty, backups piling up, memory near cap), **fix only the safe items** and re-run the audit until verdict improves.

## What the audit checks (7 metrics)
| Métrica | Señal de alerta |
|---------|-----------------|
| Git hygiene | working tree sucio (SKILL.md/cambios sin commitear) |
| Config backups | >3 `config.yaml*.bak*` acumulados |
| Skills integrity | count de `SKILL.md` reales (ver Pitfall) |
| Cron jobs | total / deshabilitados |
| Memoria | `wc -m` de MEMORY.md vs 2,200 (crítico ≥85%) |
| state.db | tamaño en MB |
| Second brain | nº de notas |

Verdicto: REVISAR (errores críticos) / OK CON ADVERTENCIAS / SALUDABLE.

## Hygiene practices (safe to apply automatically)
- **Limpiar backups redundantes:** conserva los 2 más recientes, borra el resto:
  `ls -1t config.yaml*.bak* | tail -n +3 | xargs -r rm -v`
  NUNCA borres el `.bak` que usaste como seguridad de un cambio reciente.
- **Enable a sync cron the user wants ON:** e.g. `gbrain-sync-vault` was left OFF with a one-shot `once` schedule — enable it AND change schedule to a daily recurrence (`0 23 * * *`) if it should run forever. `cronjob action=update job_id=... enabled=true schedule="0 23 * * *"`.

## Pitfalls (learned the hard way)
1. **`find` depth bug (false positive):** `find skills -mindepth 2 -maxdepth 2 -name SKILL.md` MISSES level-1 skills (`skills/name/SKILL.md`) and double-counts structure. It reported "FALTAN 39 SKILL.md" when 120 were actually fine. Fix: count ALL real SKILL.md with `find skills -name SKILL.md | wc -l`. An auditor that lies invalidates the whole loop.
2. **`no_agent` requires clean stdout:** with `no_agent=true`, the script IS the message — no agent reformats it. Keep output valid markdown and quiet on success.
3. **Cron `deliver=origin` needed for Telegram:** default local delivery won't reach the user on a gateway channel. Set `deliver=origin` (or the chat target) when the watchdog must notify.
4. **`once` schedule is not recurring:** a cron created with `once in 30m` / `once at ...` runs once then shows `completed`. For forever-monitoring, use a cron expression (`0 22 * * *`).
5. **Don't autocommit the user's git tree without asking:** `git status` showing 125 modified SKILL.md is common; committing bundled-skill changes is a USER decision (decisión de versionar). Flag it, don't do it silently.

## Verification (REQUIRED)
- Script: `bash scripts/audit_hermes.sh` → `EXIT=0` + report.
- Cron: `cronjob action=run` → `execution_success: true`.
- Report content sanity: skills count matches `find skills -name SKILL.md | wc -l`; no fabricated "missing" rows.

## References / support files
- `scripts/audit_hermes.sh` — drop-in, corrected health script (7 metrics, markdown output). Reuse and extend.
