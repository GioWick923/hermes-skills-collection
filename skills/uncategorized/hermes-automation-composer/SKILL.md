---
name: hermes-automation-composer
description: Generate a composed Hermes automation stack (/loop + /goal + cron) for any recurring work shape. Applies the "pick by shape, not by habit" doctrine from @IBuzovskyi's full guide. Use when the user wants to automate a workflow, set up monitoring, scheduled jobs, or a "full automation stack" — or when designing the agent's own autonomous backbone.
---

# Hermes Automation Composer

Turn a natural-language workflow description into a concrete, correct Hermes automation
stack using the three primitives. Built from the canonical reference:
`x.com/IBuzovskyi/status/2088969342415196650` (stored in MEMORY.md as "DOCTRINA DE AUTOMATIZACIÓN").

## The three primitives (pick by SHAPE, not habit)

| Primitive | Trigger | Scope | Use when |
|-----------|---------|-------|----------|
| `/loop <interval> <prompt>` | timer, inside a live session | dies with session | poll/watch WHILE user is present; heartbeat on state change |
| `/goal <contract>` | judge model, inside session | dies with session | drive ONE objective to verified completion (turn budget, gates) |
| `cron <schedule> <prompt>` | schedule, outside sessions | survives reboots | unattended scheduled work; fresh session each tick |

Cadence modes for /loop:
- Fixed: `/loop 2m poll CI` — you set the clock.
- Self-paced (default): `/loop keep an eye on migration` — starts 1m, backs off 2/4/8…15m, snaps back to 1m on change.

/goal contracts (ALWAYS add verification — vague goal = vague judge):
- `/goal draft <one-liner>` → Hermes expands to full contract via goal_judge.
- Inline: `verify: <shell cmd exits 0>` and/or `/goal gate add <cmd>` (deterministic check before judge).

Cron tiers:
- T1 full LLM (default) — reasoning per tick.
- T2 wakeAgent gate — pre-check script prints `{"wakeAgent": false}` on last line → skip, $0 tokens on empty ticks.
- T3 no_agent — script stdout delivered verbatim; empty = silent; nonzero exit/timeout = alert.

Silent suppression: final response containing `[SILENT]` suppresses delivery (audited locally). Failed jobs always deliver.
Chaining: `context_from` wires Job B to read Job A's last output. Cron jobs are isolated — prompts must be self-contained.

## The 5 mistakes to never ship

1. M1 cron when /loop suffices → fresh session, no project context, duplicates.
2. M2 /loop for overnight → dies with session. Overnight = cron (with wakeAgent gate).
3. M3 /goal without verify → judge reads prose, marks done prematurely. Always add `verify:`/gate.
4. M4 cron >1/hr without wakeAgent gate → 700 empty LLM calls/day. Attach gate.
5. M5 /loop without stop (`--times N` / `--until`) → backstop tick 100 (~50min). Always bound it.

## Composition patterns (emit these)

- **Loop + Goal (same session):** goal owns session; loop wakeups defer until goal pauses/parks (wait on CI) or finishes. Use when goal waits on async work and you want a heartbeat.
- **Cron → Goal:** `cron` fires session whose prompt is `/goal ... verify: ...`. Scheduled long-horizon verified work.
- **Cron (wakeAgent) = overnight loop:** cron every N min with gate checks for work; agent wakes only when needed.
- **All three:** cron triggers → goal drives to completion → loop monitors deploy → deliver to Telegram. $0 on idle ticks.

## Workflow

1. Ask (or infer) the work SHAPE: is it present-session monitoring? a defined objective? unattended schedule?
2. Map to primitive(s). If >1 shape, compose per patterns above.
3. Emit concrete commands/skills:
   - For chat-driven: `/loop ...`, `/goal draft ...`, `/cron add "..." "..."`.
   - For CLI: `hermes cron create "every 5m" --no-agent --script x.sh --deliver telegram`.
   - For the agent's OWN backbone: suggest cron jobs with wakeAgent gates + /goal contracts.
4. Apply the 5-mistake checklist before finalizing. Flag any violation.
5. Suggest delivery target (telegram:USERID, discord, slack, email, origin).

## Self-reinforcement hook

When composing for the agent's own operation, prefer:
- wakeAgent gates on any cron polling >1/hr.
- /goal with `verify:` for "drive to done" tasks instead of blind cron.
- /loop in-session for live monitoring instead of cron.
- Record the resulting stack in MEMORY.md under "DOCTRINA DE AUTOMATIZACIÓN / APLICACIÓN".
