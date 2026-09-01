---
name: autonomy-engine
description: Autonomous priority queue with time-profile scheduling.
---

# Autonomy Engine

Patterns from `42-evey/hermes-plugins` `evey-autonomy` (MIT). Adapted for a self-directed Hermes agent that runs with minimal human input.

Use when the user wants the agent to operate autonomously: prioritize tasks, schedule by time of day, plan and reflect without asking.

## Core data structures

- **Priority queue** of tasks with importance scoring (1-10) and source signals
- **Time profiles**: morning / late_morning / afternoon / evening / night — each maps allowed task types + blocked types
- **Project signals**: track git repos for uncommitted changes, non-default branches, unpushed commits as low-cost signals
- **Config precedence**: env vars > JSON config > neutral defaults (operator, UTC)

## Time-profile pattern (adapt to local timezone)

```
morning      (7-10):  bridge_check, health_check, goal_review, project_check   (block: heavy_research)
late_morning (10-12): research_deep, code_change, goal_work, project_work       (block: none)
afternoon    (12-17): research_quick, bridge_check, goal_work, project_work     (block: none)
evening      (17-21): goal_review, cost_review, light_research                 (block: heavy_delegation)
night        (21-23): memory_maintenance, health_check                         (block: user_alerts, heavy_delegation)
```

## Autonomy loop (per tick)

```
1. GATHER signals  — bridge inbox, goals.md, project git state, cron, memory scores, time
2. SCORE          — rank by importance × urgency × time-profile fit
3. PLAN           — pick top task, decompose if needed
4. EXECUTE        — run with appropriate model (heavy vs cheap)
5. REFLECT        — self-critique via cheap model (see self-reflect skill)
6. LOG            — append to autonomy-log.jsonl
7. REPEAT         — next tick
```

## Config example

```json
{
  "operator_name": "Gio",
  "timezone": "America/Mexico_City",
  "heavy_model": "tencent/hy3",
  "cheap_model": "tencent/hy3",
  "projects": [
    {"name": "mi-app", "path": "/ruta/a/mi-app", "base_branch": "main", "importance": 8}
  ],
  "bridge_peer_names": ["claude-code", "pi", "codex"],
  "disabled_sources": []
}
```

Env overrides: `HERMES_OPERATOR_NAME`, `HERMES_TIMEZONE`, `HERMES_AUTONOMY_HEAVY_MODEL`, `HERMES_AUTONOMY_CHEAP_MODEL`, `HERMES_AUTONOMY_CONFIG`.

## Integration with existing stack

- Use `cronjob` for scheduled ticks (already have self-evolution weekly)
- Use `gbrain` / `memory` for persistence (prefer gbrain over raw MEMORY.md)
- Use `delegate_task` for heavy parallel work
- Use `self-reflect` skill before reporting important outputs

## Source

Ported from https://github.com/42-evey/hermes-plugins (MIT). Plugin: `evey-autonomy/__init__.py` (636 lines).
