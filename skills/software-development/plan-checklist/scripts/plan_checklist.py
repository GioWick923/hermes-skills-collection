#!/usr/bin/env python3
"""plan_checklist.py — Parse a markdown plan into progress + next task.

Ports `plan-checklist.ts` from oh-my-openagent `boulder-state` (MIT) to pure
Python stdlib. Two modes:
  - Structured: active when `## TODOs` or `## Final Verification Wave` heading
    exists. Counts only numbered top-level checkboxes (`- [ ] 1. <title>` /
    `- [ ] F1. <title>`).
  - Simple: otherwise counts any top-level `- [ ]` / `* [ ]` checkbox.

Code fences (``` and ~~~) are ignored. Indented checkboxes are NOT counted.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from typing import Optional

# --- Regexes (mirror upstream plan-checklist.ts) ---
SIMPLE_CHECKBOX = re.compile(r"^[-*][ \t]*\[[ \t]*([xX]?)[ \t]*\][ \t]+(.+)$")
TODO_HEADING = re.compile(r"^##[ \t]+TODOs(?:[ \t]+#+)?[ \t]*$", re.IGNORECASE)
FINAL_WAVE_HEADING = re.compile(
    r"^##[ \t]+Final Verification Wave(?:[ \t]+#+)?[ \t]*$", re.IGNORECASE
)
SECTION_BOUNDARY = re.compile(r"^#{1,2}(?:[ \t]+|$)")
FENCE_OPEN = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$")
TODO_CHECKBOX = re.compile(r"^- \[([ xX])\] ([1-9]\d*\. .+)$")
FINAL_WAVE_CHECKBOX = re.compile(r"^- \[([ xX])\] (F[1-9]\d*\. .+)$", re.IGNORECASE)


@dataclass
class Checklist:
    completed: int
    remaining: int
    total: int
    next_task_label: Optional[str]
    mode: str = "simple"


def _opening_fence(line: str):
    m = FENCE_OPEN.match(line)
    if not m:
        return None
    run, info = m.group(1), m.group(2)
    marker = run[0]
    if marker not in ("`", "~"):
        return None
    if marker == "`" and "`" in info:
        return None
    return {"marker": marker, "length": len(run)}


def _closing_fence(line: str, fence) -> bool:
    m = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})[ \t]*$", line)
    if not m:
        return False
    run = m.group(1)
    return run[0] == fence["marker"] and len(run) >= fence["length"]


def _parse_section_heading(line: str) -> str:
    if TODO_HEADING.match(line):
        return "todo"
    if FINAL_WAVE_HEADING.match(line):
        return "final-wave"
    return "other"


def _structured_checkbox(line: str, section: str):
    pattern = TODO_CHECKBOX if section == "todo" else FINAL_WAVE_CHECKBOX
    m = pattern.match(line)
    if not m:
        return None
    marker, label = m.group(1), m.group(2)
    # Only numbered items with a valid task ref count.
    task_pattern = r"^([1-9]\d*)\. (.+)$" if section == "todo" else r"^(F[1-9]\d*)\. (.+)$"
    tm = re.match(task_pattern, label, re.IGNORECASE)
    if not tm:
        return None
    return {"checked": marker.lower() == "x", "label": label}


def _has_structured_section(lines) -> bool:
    fence = None
    for line in lines:
        if fence is not None:
            if _closing_fence(line, fence):
                fence = None
            continue
        open_fence = _opening_fence(line)
        if open_fence is not None:
            fence = open_fence
            continue
        if _parse_section_heading(line) != "other":
            return True
    return False


def _parse_structured(lines) -> Checklist:
    remaining = 0
    total = 0
    next_label = None
    section = "other"
    fence = None

    for line in lines:
        if fence is not None:
            if _closing_fence(line, fence):
                fence = None
            continue
        open_fence = _opening_fence(line)
        if open_fence is not None:
            fence = open_fence
            continue
        if SECTION_BOUNDARY.match(line):
            section = _parse_section_heading(line)
            continue
        if section == "other":
            continue
        cb = _structured_checkbox(line, section)
        if cb is None:
            continue
        total += 1
        if cb["checked"]:
            continue
        remaining += 1
        if next_label is None:
            next_label = cb["label"]

    return Checklist(
        completed=total - remaining,
        remaining=remaining,
        total=total,
        next_task_label=next_label,
        mode="structured",
    )


def _parse_simple(lines) -> Checklist:
    remaining = 0
    total = 0
    next_label = None
    fence = None

    for line in lines:
        if fence is not None:
            if _closing_fence(line, fence):
                fence = None
            continue
        open_fence = _opening_fence(line)
        if open_fence is not None:
            fence = open_fence
            continue
        m = SIMPLE_CHECKBOX.match(line)
        if m is None:
            continue
        marker, label = m.group(1), m.group(2)
        total += 1
        if marker.lower() == "x":
            continue
        remaining += 1
        if next_label is None:
            next_label = label

    return Checklist(
        completed=total - remaining,
        remaining=remaining,
        total=total,
        next_task_label=next_label,
        mode="simple",
    )


def parse_plan_checklist(markdown: str) -> Checklist:
    lines = markdown.split("\n")
    if _has_structured_section(lines):
        return _parse_structured(lines)
    return _parse_simple(lines)


def get_plan_checklist(plan_path: str) -> Checklist:
    try:
        with open(plan_path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except (OSError, UnicodeDecodeError):
        return Checklist(0, 0, 0, None, mode="simple")
    return parse_plan_checklist(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse a markdown plan into progress + next task")
    parser.add_argument("plan", help="Path to the markdown plan file")
    out = parser.add_mutually_exclusive_group()
    out.add_argument("--json", action="store_true", help="JSON output (default)")
    out.add_argument("--human", action="store_true", help="Human-readable output")
    out.add_argument("--next", action="store_true", help="Print only the next task label")
    args = parser.parse_args()

    c = get_plan_checklist(args.plan)

    if args.next:
        print(c.next_task_label or "")
        return 0
    if args.human:
        print(f"progress: {c.completed}/{c.total}")
        print(f"remaining: {c.remaining}")
        print(f"next: {c.next_task_label or '(none)'}")
        print(f"mode: {c.mode}")
        return 0
    # --json / default
    print(json.dumps({
        "completed": c.completed,
        "remaining": c.remaining,
        "total": c.total,
        "nextTaskLabel": c.next_task_label,
        "mode": c.mode,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
