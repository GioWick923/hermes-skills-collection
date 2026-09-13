---
name: hermes-subagent-orchestration
description: Reusable subagent orchestration patterns ported from Pi's pi-interactive-subagents, built on Hermes' existing delegate_task (which already parallelizes non-blocking). Provides fixed ROLES (planner/scout/worker/reviewer), caller_ping escalation, a /plan pipeline (investigate->plan->execute->review), and a status+stall-watchdog ledger. Use when a task benefits from multiple specialized subagents, parallel execution, or autonomous work with parent escalation.
---

# hermes-subagent-orchestration (Skill)

Ports the USEFUL patterns of Pi's `pi-interactive-subagents` to Hermes. The
repo is Pi-specific (depends on a multiplexer + Pi runtime), but Hermes already
has non-blocking parallel subagents via `delegate_task`. So this skill does NOT
reimplement spawning — it standardizes the ORCHESTRATION layer on top of it.

## What it gives you (the 4 approved improvements)

1. **Fixed roles** — reusable `delegate_task` templates so you stop spawning
   generic agents every time. `planner / scout / worker / reviewer` each carry
   preset `role`, `toolsets`, and `system` prompt.
2. **caller_ping** — a child escalates a blocker to the parent with a help
   message; parent resumes with guidance. Autonomous work with a safety net.
3. **/plan workflow** — investigate (scout) -> plan (planner) -> confirm ->
   execute (parallel workers) -> review (reviewer) -> close. Repeatable.
4. **Status widget + stall watchdog** — track each subagent's state in a file
   and flag runs that have not advanced past `timeout-min` (Hermes has no panes
   to watch, so state lives in `state.jsonl`).

## Files

- `scripts/orch.py` — engine (Python stdlib). Commands: `role`, `spawn`,
  `ping`, `close`, `status`, `watch`, `plan`.
- State ledger: `%APPDATA%/hermes/subagent-orchestration/state.jsonl`

## How the agent uses it (workflow)

### A) List / inspect roles
`python scripts/orch.py role --list`
`python scripts/orch.py role --name worker`

### B) Spawn a role (then actually call delegate_task with the printed specs)
`python scripts/orch.py spawn --role worker --name W1 --task "Implement login"`
The engine prints the exact `delegate_task` specs (role, toolsets, system).
Then call delegate_task with those. The engine records state=starting.

### C) Parallel execution (the real win)
Spawn several workers, then fire `delegate_task` for each in the SAME turn
(batch). Hermes runs them in background; results re-enter as messages.
Example: Scout finds 3 modules -> spawn worker A/B/C -> delegate_task x3.

### D) caller_ping (child -> parent escalation)
If a subagent is stuck, record the escalation:
`python scripts/orch.py ping --name W1 --message "Two conflicting schemas; use v1 or v2?"`
Parent reads it, decides, resumes the child (re-delegate with guidance or
continue itself).

### E) /plan pipeline
`python scripts/orch.py plan --goal "Add dark mode toggle"`
Follow the printed 6-step pipeline; spawn each stage's role via (B).

### F) Watchdog (catch stalled runs)
`python scripts/orch.py watch --timeout-min 15`
`python scripts/orch.py status --stalled-only`
Flags any tracked run whose last state update is older than the timeout and not
marked done.

### G) Close
`python scripts/orch.py close --name W1`  (state -> done)

### H) File locks (portado de oh-my-openagent team-core / MIT)
Evita que 2 subagentes paralelos editen el mismo archivo:
```bash
# ANTES de delegar un worker, bloquear los archivos que tocara:
python scripts/orch.py lock --acquire --file src/x.py --by W1
python scripts/orch.py lock --status --file src/x.py --by W1   # esta libre/locked?
python scripts/orch.py lock --list                              # todos los locks activos
# AL TERMINAR el worker, liberar:
python scripts/orch.py lock --release --file src/x.py --by W1
```
- **Atomicidad:** `O_EXCL` (fail-if-exists) = compare-and-swap en el FS.
- **Stale reclaim:** si el lock supera el TTL (300s) se reclama (proceso muerto).
- **Windows:** `PermissionError` = contención legítima (retry), no error fatal.
- El path se canonicaliza (abs + normpath) → mismo archivo = mismo lock, sin `..`.
- Verificado 2026-08-31: 8 contendientes al mismo archivo → 1 gana, 7 bloqueados, 1 lock.

## Integration with hermes-observational-memory

When a subagent finishes, write an observation into the observational-memory
ledger so the work is traceable: observation = "W1 implemented login (worker)",
reflection = durable fact about the project. This makes the orchestration
layer feed the memory layer.

## Pitfalls

- The engine only MODELS state; the AGENT must actually call `delegate_task`.
  `spawn` prints specs — you must act on them.
- `watch` uses file timestamps, not live process polling. For true liveness,
  pair with Hermes `process(action='list')` / `delegate_task` results.
- Roles are starting templates; override toolsets/model per task as needed.
- Don't over-engineer: if a single `delegate_task` suffices, skip the skill.

## Verification

Run the ad-hoc isolated verify (never touches your real state file):
`python scripts/verify.py` — overrides APPDATA to a temp dir and exercises
role/spawn/ping/status/watch/close/plan, asserting state transitions and the
6-step plan. Re-run after any engine change. Flag `watch` uses file timestamps;
for true liveness pair with Hermes `process(action='list')`.
