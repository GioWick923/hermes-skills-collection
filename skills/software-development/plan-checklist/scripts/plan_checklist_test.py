#!/usr/bin/env python3
"""plan_checklist_test.py — Self-test for plan_checklist.py (isolated, no real files).

Validates the parser against the upstream oh-my-openagent boulder-state behavior.
Run: python plan_checklist_test.py   (exit 0 = all pass)
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan_checklist import parse_plan_checklist  # noqa: E402


def check(name, cond, extra=""):
    if not cond:
        print(f"FAIL: {name} {extra}")
        raise SystemExit(1)
    print(f"ok: {name}")


# --- Structured mode: TODOs + Final Verification Wave ---
PLAN = """# Feature X Implementation Plan

**Goal:** Build X.

## TODOs
- [ ] 1. Setup project
- [x] 2. Add model
- [ ] 3. Wire API
- [ ] 4. Tests

## Final Verification Wave
- [ ] F1. E2E smoke
- [x] F2. Typecheck

## Notes
- [ ] this is NOT counted (indented under a non-task heading, unnumbered)
"""

c = parse_plan_checklist(PLAN)
check("structured: mode", c.mode == "structured", c.mode)
check("structured: total (1,2,3,4,F1,F2)=6", c.total == 6, str(c.total))
check("structured: completed (2,F2)=2", c.completed == 2, str(c.completed))
check("structured: remaining=4", c.remaining == 4, str(c.remaining))
check("structured: next=1. Setup project", c.next_task_label == "1. Setup project", str(c.next_task_label))


# --- Code fences ignored (checkboxes inside ``` should NOT count) ---
PLAN_FENCE = """## TODOs
- [ ] 1. Real task

```python
# - [ ] 2. Fake task inside fence
- [ ] not a real checkbox
```

- [ ] 2. Second real task
"""
c = parse_plan_checklist(PLAN_FENCE)
check("fence: total=2 (fence ignored)", c.total == 2, str(c.total))
check("fence: next=1. Real task", c.next_task_label == "1. Real task", str(c.next_task_label))


# --- Simple mode (no TODOs heading): any top-level checkbox ---
PLAN_SIMPLE = """# Simple Plan

- [x] task one
- [ ] task two
* [ ] task three
- [x] task four
"""
c = parse_plan_checklist(PLAN_SIMPLE)
check("simple: mode", c.mode == "simple", c.mode)
check("simple: total=4", c.total == 4, str(c.total))
check("simple: completed=2", c.completed == 2, str(c.completed))
check("simple: next=task two", c.next_task_label == "task two", str(c.next_task_label))


# --- Indented checkboxes NOT counted in simple mode ---
PLAN_INDENT = """# Indented

- [ ] top task
  - [ ] indented task (should NOT count)
"""
c = parse_plan_checklist(PLAN_INDENT)
check("indent: total=1 (indented ignored)", c.total == 1, str(c.total))
check("indent: next=top task", c.next_task_label == "top task", str(c.next_task_label))


# --- Empty / missing file ---
empty = parse_plan_checklist("")
check("empty: total=0", empty.total == 0, str(empty.total))
check("empty: next=None", empty.next_task_label is None, str(empty.next_task_label))


# --- All unchecked → next is first ---
ALL = """## TODOs
- [ ] 1. alpha
- [ ] 2. beta
"""
c = parse_plan_checklist(ALL)
check("all-unchecked: next=alpha", c.next_task_label == "1. alpha", str(c.next_task_label))
check("all-unchecked: remaining=2", c.remaining == 2, str(c.remaining))


# --- All checked → no next, isComplete semantics ---
DONE = """## TODOs
- [x] 1. alpha
- [x] 2. beta
"""
c = parse_plan_checklist(DONE)
check("all-done: next=None", c.next_task_label is None, str(c.next_task_label))
check("all-done: completed=2 remaining=0", c.completed == 2 and c.remaining == 0, f"{c.completed}/{c.remaining}")


print("\nAll plan-checklist tests passed.")
sys.exit(0)
