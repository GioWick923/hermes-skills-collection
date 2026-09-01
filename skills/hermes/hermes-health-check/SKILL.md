---
category: hermes
name: hermes-health-check
description: "Check Hermes with real commands before saying it is broken."
version: 1.0.0
author: <USER> + Hermes
license: MIT
---

# Hermes Health Check (diagnosis-first)

## When to use
- User asks "¿tienes todos los componentes?", "¿está roto?", "¿qué pasó con mis memorias?".
- After a Hermes update, migration, or reboot.
- Before ANY repair attempt.

## Golden rules
1. **NEVER assume broken from memory.** Stale memory (e.g. "cron failed on 2026-08-16") is HISTORICAL, not current. Always re-verify with live commands first.
2. **Separate facts from inference.** Mark verified / inferred / blocked in your reply.
3. **Verify execution environment FIRST.** My sandbox (execute_code/terminal) is a Docker Linux container that does NOT mount the host Windows disk and has NO `hermes` CLI. Host repairs MUST run in the user's PowerShell, not my tools.
4. **Docker daemon may be down.** If `docker version` fails with "daemon not running", the engine is off — ask user to launch Docker Desktop; do NOT broadly claim "I can't do anything".

## Diagnostic sequence (run in USER's PowerShell, host-side)
Use the full CLI path (hermes is NOT in PS PATH by default):
```powershell
$cli="$env:LOCALAPPDATA\hermes\hermes-agent\bin\hermes.exe"
& $cli status --all
& $cli cron list
& $cli mcp list
& $cli doctor
```
Also check state of key pieces:
```powershell
Get-Content "$env:USERPROFILE\.gbrain\config.json" | ConvertFrom-Json | Select database_path
(Select-String -Pattern 'OLDUSER' -Path "$env:LOCALAPPDATA\hermes\config.yaml").Count
Test-Path "$env:LOCALAPPDATA\hermes\state.db"
Get-Content "$env:LOCALAPPDATA\hermes\EVOLUTION.md" -Tail 20
```

## Interpretation (anti-false-alarm core)
- `cron list` shows `last_status: ok` → jobs run fine. Do NOT re-pin unless a model 404 is CONFIRMED by the run log.
- gbrain `database_path` must point to `C:\Users\<USER>\.gbrain\brain.pglite` (OK if so).
- MCP OLDUSER hits = 0 → paths already migrated; no MCP repair needed.
- `state.db.pre-update-emergency-*` files = protective snapshots from an update, NOT corruption.
- MEMORY.md / SOUL.md / EVOLUTION.md present → past/identity intact, user will not "feel empty".

## Repair (ONLY if verified broken)
- Cron model 404: `& $cli cron edit <id> --provider nvidia --model nvidia/glm-5.2`
- gbrain path: patch `database_path` (one line, non-destructive, backup first).
- MCP old paths: `(Get-Content cfg) -replace 'OLD','NEW' | Set-Content cfg` (backup first).
- state.db: only move if `doctor`/session_search ACTUALLY fails AND Hermes is fully closed (file lock otherwise).

## Pitfalls
- Don't pin non-agent/script cron jobs (field ignored, noisy).
- Don't move state.db while Hermes is open (file lock → move fails).
- Don't fabricate "fixed" — only report what commands returned.
- Don't conclude "everything broken" from a single failed tool call (Docker down ≠ host broken).

## Verification
After any change, re-run `cron list` + `doctor` and confirm `last_status: ok` / no red before declaring resolved.
