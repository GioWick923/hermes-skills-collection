---
name: memory-consolidate
description: Daily fact extraction with importance scoring and decay.
---

# Memory Consolidate

From `42-evey/hermes-plugins` `evey-memory-consolidate` + `evey-memory-adaptive` (MIT). Nightly extraction of key facts from conversations into durable memory, with importance scoring and decay.

Use in a cron (e.g. 3am) or on-demand after significant sessions.

## Pipeline

```
1. QUERY      — pull recent conversation traces (last 24h)
2. EXTRACT    — local/cheap model pulls 3-5 key facts
3. SCORE      — rate importance 1-10 (critical=10, trivial=1)
4. STORE      — high-value facts → gbrain / MEMORY.md; vectors if available
5. DECAY      — low-value memories fade over time, high-value persist
```

## Extract prompt (terse)

```
Extract 3-5 key facts from these AI agent conversation traces.

Rules:
- Only novel, useful facts (not greetings, errors, tool calls)
- Format: "- [category] fact" where category is: learned, decided, discovered, created, fixed
- COMPACT language — no filler, abbreviate
- Specific, terse, max 15 words per fact
- Skip trivial or repetitive

TRACES:
{traces}

KEY FACTS:
```

## Score rubric

```
10 = Critical (security rule, user preference, architecture decision)
7-9 = Important (learned behavior, tool discovery, cost insight)
4-6 = Useful (research finding, model comparison, minor observation)
1-3 = Trivial (greeting, routine check, temporary state)
```

## Adaptive memory

- **Importance scoring**: weight recall by score
- **Decay**: low-score memories drop priority after N days; high-score persist
- Store durable facts in `gbrain` (preferred) or `MEMORY.md`

## Cron hook

Schedule via `cronjob`: run nightly, call this skill, sync to gbrain.

## Source

Ported from https://github.com/42-evey/hermes-plugins (MIT). Plugins: `evey-memory-consolidate/__init__.py` (206 lines), `evey-memory-adaptive/__init__.py`. Original uses qwen35-4b + Qdrant; adapt to gbrain.
