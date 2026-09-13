#!/usr/bin/env python3
"""
hermes-subagent-orchestration engine (v1)
Ports the useful PATTERNS from Pi's pi-interactive-subagents to Hermes:
  - Fixed roles (planner/scout/worker/reviewer) as reusable delegate_task templates
  - caller_ping concept: a subagent escalates to parent with a help message
  - /plan workflow: investigate -> plan -> execute(parallel workers) -> review
  - status widget + stall watchdog: track subagent state in a file, flag stalled

Hermes already parallelizes via delegate_task (background). This engine only
models the ORCHESTRATION layer: role templates, a state ledger for watchdog,
and a /plan pipeline description. The AGENT does the reasoning and calls
delegate_task; the engine persists state and renders status.

Usage:
  python orch.py role     --list
  python orch.py role     --name planner          # print template json
  python orch.py spawn    --role worker --name "W1" --task "..." [--session SID]
  python orch.py ping     --name "W1" --message "need help choosing schema"
  python orch.py status   [--stalled-only]
  python orch.py watch    [--timeout-min 15]      # flag stalled runs
  python orch.py plan     --goal "..."            # print /plan pipeline steps
  python orch.py close    --name "W1"             # mark done
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime

STATE_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "hermes", "subagent-orchestration")
STATE_PATH = os.path.join(STATE_DIR, "state.jsonl")

# ---- role templates (reusable delegate_task specs) ----
ROLES = {
    "planner": {
        "role": "leaf",
        "toolsets": ["terminal", "file", "web"],
        "model_hint": "reasoning",
        "system": "You are a planner. Clarify requirements, explore approaches, "
                  "write a concrete plan with numbered todos. Do NOT implement; "
                  "hand the plan back.",
    },
    "scout": {
        "role": "leaf",
        "toolsets": ["terminal", "file", "web"],
        "model_hint": "fast",
        "system": "You are a scout. Fast codebase/web reconnaissance: map files, "
                  "patterns, conventions, and report findings concisely.",
    },
    "worker": {
        "role": "leaf",
        "toolsets": ["terminal", "file", "web", "coding"],
        "model_hint": "default",
        "system": "You are a worker. Implement the given todo list: write code, "
                  "run tests, make polished commits. Report what changed.",
    },
    "reviewer": {
        "role": "leaf",
        "toolsets": ["terminal", "file", "coding"],
        "model_hint": "reasoning",
        "system": "You are a reviewer. Review changes for bugs, security, and "
                  "correctness. Return a concise list of issues + verdict.",
    },
}


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _load():
    if not os.path.exists(STATE_PATH):
        return []
    rows = []
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


def _append(entry):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _state_of(rows, name):
    latest = None
    for r in rows:
        if r.get("name") == name:
            latest = r
    return latest


# ---------- commands ----------
def cmd_role(args):
    if args.list:
        for k, v in ROLES.items():
            print(f"{k:10} tools={v['toolsets']} model={v['model_hint']}")
        return
    if args.name:
        if args.name not in ROLES:
            print(f"[warn] unknown role: {args.name}", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(ROLES[args.name], ensure_ascii=False, indent=2))


def cmd_spawn(args):
    if args.role not in ROLES:
        print(f"[warn] unknown role: {args.role}", file=sys.stderr)
        sys.exit(1)
    entry = {
        "event": "spawn", "name": args.name, "role": args.role,
        "task": args.task, "session": args.session or "",
        "state": "starting", "ts": _now(),
    }
    _append(entry)
    print(f"[spawned] {args.name} ({args.role}) state=starting")
    print("  -> call delegate_task with these specs:")
    t = ROLES[args.role]
    print(json.dumps({"role": t["role"], "toolsets": t["toolsets"],
                      "system": t["system"], "goal": args.task},
                     ensure_ascii=False, indent=2))


def cmd_ping(args):
    """caller_ping: child escalates to parent with a help message."""
    entry = {"event": "ping", "name": args.name, "message": args.message,
             "state": "waiting", "ts": _now()}
    _append(entry)
    print(f"[caller_ping] {args.name} needs help: {args.message}")
    print("  -> PARENT: resume child with guidance, then re-delegate or continue.")


def cmd_close(args):
    entry = {"event": "close", "name": args.name, "state": "done", "ts": _now()}
    _append(entry)
    print(f"[closed] {args.name} -> done")


def cmd_status(args):
    rows = _load()
    if args.stalled_only:
        # delegate watchdog decision to watch()
        cmd_watch(argparse.Namespace(timeout_min=args.timeout or 15,
                                     stalled_only=True))
        return
    names = {}
    for r in rows:
        names[r["name"]] = r
    if not names:
        print("[status] no subagents tracked")
        return
    print(f"{'NAME':12} {'ROLE':10} {'STATE':10} {'TS'}")
    for n, r in names.items():
        print(f"{n:12} {r.get('role','-'):10} {r.get('state','-'):10} {r.get('ts','')}")


def cmd_watch(args):
    rows = _load()
    names = {}
    for r in rows:
        names[r["name"]] = r
    now = time.time()
    stall_min = args.timeout_min
    flagged = []
    for n, r in names.items():
        if r.get("state") in ("done",):
            continue
        try:
            ts = datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        age_min = (now - ts.timestamp()) / 60.0
        if age_min > stall_min and r.get("state") not in ("done",):
            flagged.append((n, round(age_min)))
    if args.stalled_only:
        for n, a in flagged:
            print(f"STALLED {n} (~{a} min, last state={names[n].get('state')})")
        if not flagged:
            print("[watch] no stalled runs")
        return
    if flagged:
        print(f"[watch] {len(flagged)} possibly stalled:")
        for n, a in flagged:
            print(f"  - {n}: ~{a} min, state={names[n].get('state')}")
    else:
        print("[watch] all healthy")


def cmd_plan(args):
    goal = args.goal
    steps = [
        ("1. Investigate", "spawn scout -> map scope/repo/web", "scout"),
        ("2. Plan", "spawn planner -> todos + approach", "planner"),
        ("3. Confirm", "parent reviews plan with user", "parent"),
        ("4. Execute", "spawn N workers in PARALLEL (delegate_task xN)", "worker"),
        ("5. Review", "spawn reviewer -> issues + verdict", "reviewer"),
        ("6. Close", "parent summarizes; close all", "parent"),
    ]
    print(f"/plan pipeline for goal: {goal}\n")
    for title, desc, who in steps:
        print(f"  {title:14} [{who:8}] {desc}")
    print("\nUse: orch.py spawn --role <who> --name <X> --task <...>")


# ---------- file locks (ported from oh-my-openagent team-core / MIT) ----------
# Patron `withLock` + `open(path, "wx")` (O_EXCL fail-if-exists = compare-and-swap
# atomico en el FS). Contenido = ownerTag + pid + ts => deteccion de locks stale.
# Reclaim: si el lock supera el TTL, se borra y se reintenta. PermissionError en
# Windows = contention legitima (retry), no error fatal.
LOCK_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", os.path.expanduser("~"))),
    "hermes", "subagent-orchestration", "locks")
LOCK_TTL_S = 300


def _lock_stale(path):
    try:
        return (time.time() - os.path.getmtime(path)) > LOCK_TTL_S
    except OSError:
        return False


def _release_lock(path):
    try:
        os.remove(path)
    except OSError:
        pass


def cmd_lock(args):
    """Bloquear un archivo (path canonicalizado) para un worker/lane.

    Evita que 2 subagentes editen el mismo archivo en paralelo.
    Uso (ANTES de delegar un worker):
      orch.py lock --acquire --file src/x.py --by W1
      orch.py lock --release --file src/x.py --by W1
    """
    if args.list:
        cmd_lock_list(args)
        return
    if not args.file or not args.by:
        print("[lock] --file and --by required (or use --list)", file=sys.stderr)
        sys.exit(1)
    os.makedirs(LOCK_DIR, exist_ok=True)
    # canonicalizar path: abs + normpath => mismo archivo mismo lock, sin ..
    canon = os.path.normpath(os.path.abspath(args.file))
    # nombre seguro del lock: hash del path (evita caracteres invalidos / traversal)
    lock_name = hashlib.sha256(canon.encode("utf-8")).hexdigest() + ".lock"
    lock_path = os.path.join(LOCK_DIR, lock_name)

    if args.release:
        _release_lock(lock_path)
        print(f"[lock released] {args.file}")
        return

    if args.status:
        if os.path.exists(lock_path):
            meta = {}
            try:
                with open(lock_path, encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                pass
            print(f"[locked] {args.file} by={meta.get('owner')} pid={meta.get('pid')}")
        else:
            print(f"[free] {args.file}")
        return

    # acquire
    deadline = time.time() + args.wait
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(fd, json.dumps({"owner": args.by, "pid": os.getpid(),
                                     "ts": time.time()}).encode("utf-8"))
            os.close(fd)
            print(f"[locked] {args.file} by {args.by}")
            return
        except FileExistsError:
            if _lock_stale(lock_path):
                _release_lock(lock_path)
                continue
            if time.time() >= deadline:
                print(f"[lock busy] {args.file} (holder another process); wait or retry",
                      file=sys.stderr)
                sys.exit(2)
            time.sleep(0.1)
        except PermissionError:
            # Windows: lock abierto por otro proceso = contention, retry
            if time.time() >= deadline:
                print(f"[lock busy] {args.file} (permission/windows contention)",
                      file=sys.stderr)
                sys.exit(2)
            time.sleep(0.1)
        except OSError:
            print(f"[lock error] cannot create lock for {args.file}", file=sys.stderr)
            sys.exit(1)


def cmd_lock_list(args):
    """Listar locks activos."""
    if not os.path.isdir(LOCK_DIR):
        print("[locks] none")
        return
    names = sorted(n for n in os.listdir(LOCK_DIR) if n.endswith(".lock"))
    if not names:
        print("[locks] none")
        return
    print(f"{'FILE':40} {'OWNER':10} {'PID':6}")
    for n in names:
        p = os.path.join(LOCK_DIR, n)
        meta = {}
        try:
            with open(p, encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            pass
        # no podemos revertir el hash al path original, solo mostramos meta
        print(f"{n[:38]:40} {str(meta.get('owner','?')):10} {str(meta.get('pid','?')):6}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("role")
    r.add_argument("--list", action="store_true")
    r.add_argument("--name")
    s = sub.add_parser("spawn")
    s.add_argument("--role", required=True)
    s.add_argument("--name", required=True)
    s.add_argument("--task", required=True)
    s.add_argument("--session")
    pg = sub.add_parser("ping")
    pg.add_argument("--name", required=True)
    pg.add_argument("--message", required=True)
    c = sub.add_parser("close")
    c.add_argument("--name", required=True)
    st = sub.add_parser("status")
    st.add_argument("--stalled-only", action="store_true")
    st.add_argument("--timeout", type=int, default=15)
    w = sub.add_parser("watch")
    w.add_argument("--timeout-min", type=int, default=15)
    w.add_argument("--stalled-only", action="store_true")
    pl = sub.add_parser("plan")
    pl.add_argument("--goal", required=True)
    lk = sub.add_parser("lock")
    lk.add_argument("--file")
    lk.add_argument("--by")
    lk.add_argument("--acquire", action="store_true")
    lk.add_argument("--release", action="store_true")
    lk.add_argument("--status", action="store_true")
    lk.add_argument("--list", action="store_true", help="list active locks")
    lk.add_argument("--wait", type=float, default=10.0)
    args = p.parse_args()
    if args.cmd == "lock" and args.list:
        cmd_lock_list(args)
        return
    {
        "role": cmd_role, "spawn": cmd_spawn, "ping": cmd_ping,
        "close": cmd_close, "status": cmd_status, "watch": cmd_watch,
        "plan": cmd_plan, "lock": cmd_lock,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
