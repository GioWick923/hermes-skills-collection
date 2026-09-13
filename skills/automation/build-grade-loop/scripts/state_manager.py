#!/usr/bin/env python3
"""
Implement-Review Loop — State Manager

状态管理工具（方案A：Agent 手动编排，脚本只管记录）。

用法：
  python state_manager.py init --project /path --target 90 --max-rounds 5
  python state_manager.py record --project /path --score 72 --critical 3 --minor 2
  python state_manager.py status --project /path
  python state_manager.py history --project /path
  python state_manager.py feedback --project /path --append "评审报告内容"
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

STATE_DIR = ".iteration-state"
FEEDBACK_FILE = "feedback.md"
HISTORY_FILE = "round-history.json"


def get_state_dir(project_path="."):
    return Path(project_path) / STATE_DIR


def load_history(state_dir):
    path = state_dir / HISTORY_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_history(state_dir, history):
    path = state_dir / HISTORY_FILE
    path.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


# ── init ──────────────────────────────────────────────

def cmd_init(args):
    project = args.get("--project", ".")
    target = int(args.get("--target", 90))
    max_rounds = int(args.get("--max-rounds", 5))

    state_dir = get_state_dir(project)
    state_dir.mkdir(parents=True, exist_ok=True)

    feedback_path = state_dir / FEEDBACK_FILE
    if not feedback_path.exists():
        feedback_path.write_text("# Iteration Feedback\n\n", encoding="utf-8")
        print(f"  ✅ Created {FEEDBACK_FILE}")
    else:
        print(f"  ⏭️  {FEEDBACK_FILE} already exists, skipped")

    history_path = state_dir / HISTORY_FILE
    if not history_path.exists():
        history = {
            "rounds": [],
            "target_score": target,
            "max_rounds": max_rounds,
            "created_at": datetime.now().isoformat(),
            "project_path": os.path.abspath(project),
        }
        save_history(state_dir, history)
        print(f"  ✅ Created {HISTORY_FILE}")
    else:
        print(f"  ⏭️  {HISTORY_FILE} already exists, skipped")

    print(f"\n  📁 State dir: {state_dir}")
    print(f"  🎯 Target: {target} | Max rounds: {max_rounds}")


# ── record ────────────────────────────────────────────

def cmd_record(args):
    project = args.get("--project", ".")
    score = int(args.get("--score", 0))
    critical = int(args.get("--critical", 0))
    minor = int(args.get("--minor", 0))
    note = args.get("--note", "")

    state_dir = get_state_dir(project)
    history = load_history(state_dir)
    if history is None:
        print("❌ No state found. Run `init` first.")
        sys.exit(1)

    round_num = len(history["rounds"]) + 1
    entry = {
        "round": round_num,
        "score": score,
        "timestamp": datetime.now().isoformat(),
        "critical_fixes": critical,
        "minor_fixes": minor,
    }
    if note:
        entry["note"] = note

    history["rounds"].append(entry)
    save_history(state_dir, history)

    target = history["target_score"]
    max_rounds = history["max_rounds"]

    print(f"  ✅ Round {round_num} recorded: score={score}")
    print(f"  🎯 Target: {target} | Gap: {max(0, target - score)}")

    # 状态判断
    if score >= target:
        print(f"  🎉 TARGET REACHED!")
    elif round_num >= max_rounds:
        print(f"  ⚠️  Max rounds ({max_rounds}) reached")
    else:
        # 平台期检测
        if round_num >= 2:
            prev = history["rounds"][-2]["score"]
            if score <= prev:
                # 数连续不升轮次
                plateau = 0
                for i in range(len(history["rounds"]) - 1, 0, -1):
                    if history["rounds"][i]["score"] <= history["rounds"][i - 1]["score"]:
                        plateau += 1
                    else:
                        break
                if plateau >= 2:
                    print(f"  🛑 PLATEAU: {plateau} rounds without improvement")
                else:
                    print(f"  ⚡ Score not improved (plateau {plateau}/2)")
            else:
                delta = score - prev
                print(f"  📈 +{delta} from last round")

    # 展示分数历史
    if len(history["rounds"]) > 1:
        scores = " → ".join(str(r["score"]) for r in history["rounds"])
        print(f"  📊 History: {scores}")


# ── status ────────────────────────────────────────────

def cmd_status(args):
    project = args.get("--project", ".")
    state_dir = get_state_dir(project)
    history = load_history(state_dir)

    if history is None:
        print("❌ No state found. Run `init` first.")
        sys.exit(1)

    rounds = history["rounds"]
    target = history["target_score"]
    max_rounds = history["max_rounds"]

    print(f"  📁 Project: {history.get('project_path', project)}")
    print(f"  🎯 Target: {target} | Max rounds: {max_rounds}")
    print(f"  📊 Rounds completed: {len(rounds)}/{max_rounds}")
    print()

    if not rounds:
        print("  No rounds yet.")
        return

    # 表格
    print(f"  {'Round':<6} {'Score':<8} {'Delta':<8} {'Critical':<10} {'Minor':<8}")
    print(f"  {'─'*6} {'─'*8} {'─'*8} {'─'*10} {'─'*8}")
    prev = 0
    for r in rounds:
        delta = f"+{r['score'] - prev}" if prev > 0 else "—"
        crit = r.get("critical_fixes", "?")
        minor = r.get("minor_fixes", "?")
        note = f"  ({r['note']})" if r.get("note") else ""
        print(f"  {r['round']:<6} {r['score']:<8} {delta:<8} {crit:<10} {minor:<8}{note}")
        prev = r["score"]

    latest = rounds[-1]["score"]
    print()

    # 状态判断
    if latest >= target:
        print(f"  Status: ✅ TARGET REACHED ({latest}/{target})")
    elif len(rounds) >= max_rounds:
        print(f"  Status: ⚠️  MAX ROUNDS HIT ({latest}/{target})")
    else:
        # 平台期检测
        plateau = 0
        for i in range(len(rounds) - 1, 0, -1):
            if rounds[i]["score"] <= rounds[i - 1]["score"]:
                plateau += 1
            else:
                break
        if plateau >= 2:
            print(f"  Status: 🛑 PLATEAU ({plateau} rounds without improvement, {latest}/{target})")
        elif plateau == 1:
            print(f"  Status: ⚡ PLATEAU WARNING ({latest}/{target})")
        else:
            print(f"  Status: 🔄 IN PROGRESS ({latest}/{target})")

    # 建议
    if rounds and latest < target and len(rounds) < max_rounds:
        gap = target - latest
        print(f"\n  💡 Gap to target: {gap} points")
        if plateau >= 2:
            print(f"  💡 Consider: focus on top stuck items, lower target, or manual intervention")


# ── history ───────────────────────────────────────────

def cmd_history(args):
    """输出纯 JSON 的轮次历史（方便 Agent 解析）"""
    project = args.get("--project", ".")
    state_dir = get_state_dir(project)
    history = load_history(state_dir)

    if history is None:
        print("{}")
        return

    print(json.dumps(history, indent=2, ensure_ascii=False))


# ── feedback ──────────────────────────────────────────

def cmd_feedback(args):
    """向 feedback.md 追加内容"""
    project = args.get("--project", ".")
    content = args.get("--append", "")

    if not content:
        print("❌ No content. Use --append \"your content\"")
        sys.exit(1)

    state_dir = get_state_dir(project)
    feedback_path = state_dir / FEEDBACK_FILE

    if not feedback_path.exists():
        print("❌ No feedback.md found. Run `init` first.")
        sys.exit(1)

    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write("\n" + content + "\n")

    size = feedback_path.stat().st_size
    print(f"  ✅ Appended to {FEEDBACK_FILE} ({size} bytes total)")


# ── CLI ───────────────────────────────────────────────

HELP = """
Implement-Review Loop — State Manager (方案A)

Commands:
  init      Initialize state directory
            --project PATH   Project directory (default: .)
            --target N       Target score (default: 90)
            --max-rounds N   Max rounds (default: 5)

  record    Record a round's score
            --project PATH   Project directory (default: .)
            --score N        Total score (required)
            --critical N     Critical deductions count (default: 0)
            --minor N        Minor deductions count (default: 0)
            --note TEXT      Optional note

  status    Show current progress (human-readable)
            --project PATH   Project directory (default: .)

  history   Output full state as JSON (machine-readable)
            --project PATH   Project directory (default: .)

  feedback  Append content to feedback.md
            --project PATH   Project directory (default: .)
            --append TEXT     Content to append (required)
""".strip()


def parse_args(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help", "help"):
        print(HELP)
        sys.exit(0)

    command = argv[1]
    args = {}
    i = 2
    while i < len(argv):
        if argv[i].startswith("--") and i + 1 < len(argv):
            args[argv[i]] = argv[i + 1]
            i += 2
        else:
            i += 1
    return command, args


def main():
    command, args = parse_args(sys.argv)

    commands = {
        "init": cmd_init,
        "record": cmd_record,
        "status": cmd_status,
        "history": cmd_history,
        "feedback": cmd_feedback,
    }

    if command not in commands:
        print(f"❌ Unknown command: {command}")
        print(f"   Available: {', '.join(commands.keys())}")
        sys.exit(1)

    commands[command](args)


if __name__ == "__main__":
    main()
