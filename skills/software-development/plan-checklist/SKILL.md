---
category: software-development
name: plan-checklist
description: "Parse a markdown plan into progress + next task."
version: 1.0.0
author: Hermes Agent (ported from code-yeongyu/oh-my-openagent boulder-state)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, checklist, progress, resume, boulder]
    related_skills: [plan, to-tickets, to-spec, subagent-driven-development]
---

# Plan Checklist Parser

Ports the `plan-checklist.ts` engine from oh-my-openagent's `boulder-state`
(state machine that tracks an active work plan across sessions/worktrees/tasks)
to pure Python stdlib. Extracts structured progress from a markdown plan file:
**completed / remaining / total** and the **next unchecked task label**.

## When to use

- After a plan is written to `.hermes/plans/`, you (or a subagent) need to know
  progress or resume exactly where you left off.
- Multi-day / multi-session work where the plan file is the source of truth.
- Before delegating the next task, to confirm which one is actually next.

## Usage

```bash
python "$LOCALAPPDATA/hermes/skills/software-development/plan-checklist/scripts/plan_checklist.py" <plan.md>
```

Output: a compact JSON line:
```json
{"completed": 2, "remaining": 3, "total": 5, "nextTaskLabel": "Implement auth", "mode": "structured"}
```

Flags:
- `--json` (default): structured JSON output.
- `--human`: human-readable lines (`progress: 2/5`, `next: Implement auth`).
- `--next`: print only the next unchecked task label (for scripting).

## How it parses (matches upstream)

**Two modes:**

1. **Structured mode** — active when the file contains a `## TODOs` heading or a
   `## Final Verification Wave` heading:
   - Counts ONLY numbered top-level checkboxes: `- [ ] 1. <title>` (in `## TODOs`)
     and `- [ ] F1. <title>` (in `## Final Verification Wave`).
   - `nextTaskLabel` = the first unchecked numbered item (TODOs first, then F-wave).

2. **Simple mode** — otherwise counts any top-level `- [ ]` / `* [ ]` checkbox.

**Code fences are ignored** (``` and ~~~ blocks skipped). Indented checkboxes
(more than one space of leading whitespace) are NOT counted — only top-level
`- ` / `* ` list markers.

## Verification

Run the self-test (isolated, no real files touched):
```bash
python "$LOCALAPPDATA/hermes/skills/software-development/plan-checklist/scripts/plan_checklist_test.py"
```
Expected: all assertions pass, exit 0.

## Source

Ported from `code-yeongyu/oh-my-openagent` `packages/boulder-state/src/plan-checklist.ts`
(MIT, Apache-2.0 dual licensed). Inspected 2026-08-31.
