#!/usr/bin/env python3
"""
hermes-observational-memory ledger engine (v1)
Port of Pi's pi-observational-memory mental model to Hermes tools.

Stores two memory layers in a JSONL ledger:
  - OBSERVATION: timestamped event record from a session (ephemeral-ish)
  - REFLECTION: durable fact distilled from observations (long-lived)

Supports: add observation, reflect (distill durable facts), drop (prune
covered observations), recall (trace by 12-hex id), status (drift/pressure),
view (rendered projection).

The AGENT (LLM) does the reasoning: it calls these subcommands with content
it has distilled. The script only enforces structure, ids, and persistence.

Usage:
  python ledger.py observe  --content "..." [--relevance high] [--source SID]...
  python ledger.py reflect  --content "..." --supports OID...
  python ledger.py drop     --ids OID...   (tombstone; still recallable)
  python ledger.py recall   --id XXXXXXXXXX
  python ledger.py status
  python ledger.py view     [--full]
  python ledger.py prune    (auto-drop observations covered strongly by reflections)
  python ledger.py fold     (render a compact projection string for session boot)
"""
import argparse
import json
import os
import re
import sys
import hashlib
import time
from datetime import datetime

LEDGER_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA",
        os.environ.get("APPDATA", os.path.expanduser("~"))),
    "hermes", "observational-memory")
LEDGER_PATH = os.path.join(LEDGER_DIR, "ledger.jsonl")
LOCK_PATH = os.path.join(LEDGER_DIR, "memory-write.lock")

RELEVANCE = ("low", "medium", "high", "critical")
ID_RE = re.compile(r"^[0-9a-f]{12}$")

# Lock por dominio (patron memory-core de oh-my-openagent / MIT):
# - O_EXCL (fail-if-exists) = compare-and-swap atomico en el FS
# - Contenido = ownerTag + pid + timestamp => deteccion de locks stale
# - TTL 300s: un lock muerto (proceso crasheado) se puede reclamar
LOCK_TTL_S = 300


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _mid(seed: str) -> str:
    """Deterministic-ish 12-char lowercase hex id from seed + counter."""
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return h


class DomainLock:
    """Lock por dominio (memory-write) con deteccion de stale locks.

    Porta el patron `withLock` + `open(path, "wx")` de oh-my-openagent
    team-core / memory-core. Escribir al ledger adquiere este lock para
    garantizar un solo escritor y publicacion atomica.
    """

    def __init__(self, path: str, ttl_s: int = LOCK_TTL_S):
        self.path = path
        self.ttl_s = ttl_s
        self._fd = None

    def _is_stale(self) -> bool:
        """Stale si el lock supera el TTL de edad.

        Usa mtime (os.stat) en lugar de abrir/leer el contenido: abrir el lock
        para leerlo en Windows mantiene un handle abierto que BLOQUEA a otro
        proceso de hacer os.remove() al liberar, dejando el lock colgado.
        os.stat no abre el archivo, asi que nunca interfiere con la liberacion.
        """
        try:
            mtime = os.path.getmtime(self.path)
            return (time.time() - mtime) > self.ttl_s
        except OSError:
            return False

    def acquire(self, wait_s: float = 2.0):
        deadline = time.time() + wait_s
        while True:
            try:
                self._fd = os.open(
                    self.path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o600,
                )
                meta = {"owner": "leager", "pid": os.getpid(), "ts": time.time()}
                os.write(self._fd, json.dumps(meta).encode("utf-8"))
                # NO fsync aqui: el meta del lock es solo un marcador de
                # contención, no datos durables. fsync aqui hace lenta la
                # contención bajo muchos writers concurrentes (el append del
                # ledger SI hace fsync para durabilidad real).
                return True
            except FileExistsError:
                # lock existe y es de otro -> contención legítima
                if self._is_stale():
                    # lock stale => reclamar (rm + reintentar)
                    try:
                        os.remove(self.path)
                    except OSError:
                        pass
                    continue
                if time.time() >= deadline:
                    return False
                time.sleep(0.05)
            except PermissionError:
                # WINDOWS: si el lock esta abierto por otro proceso, os.open
                # O_EXCL lanza PermissionError (no FileExistsError). Es
                # contención legítima, NO un fallo fatal. Reintentar.
                if time.time() >= deadline:
                    return False
                time.sleep(0.05)
            except OSError:
                return False

    def release(self):
        try:
            if self._fd is not None:
                os.close(self._fd)
                self._fd = None
        except OSError:
            pass
        try:
            os.remove(self.path)
        except OSError:
            pass


def _append(entry):
    """Append atomico al ledger bajo lock por dominio + fsync (fail-closed).

    Patron memory-core de oh-my-openagent (MIT): un solo escritor via lock
    O_EXCL, escritura completa + flush + fsync (crash-safe), fail-closed si no
    se puede tomar el lock. Para un JSONL append no hace falta temp+rename:
    el lock ya garantiza exclusividad, y fsync garantiza durabilidad.
    """
    os.makedirs(LEDGER_DIR, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False) + "\n"

    lock = DomainLock(LOCK_PATH)
    if not lock.acquire(wait_s=15.0):
        # no pudimos tomar el lock => fail-closed (no escribir a ciegas)
        raise RuntimeError(f"could not acquire memory-write lock: {LOCK_PATH}")

    try:
        with open(LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
    finally:
        lock.release()


def _load():
    if not os.path.exists(LEDGER_PATH):
        return []
    rows = []
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _next_obs_id(content, ts):
    # avoid collisions by mixing content+ts+counter
    rows = _load()
    n = sum(1 for r in rows if r.get("type") == "observation")
    return _mid(f"{content}|{ts}|{n}")


# ---------- commands ----------
def cmd_observe(args):
    ts = _now()
    oid = _next_obs_id(args.content, ts)
    rel = args.relevance if args.relevance in RELEVANCE else "medium"
    sources = []
    for s in args.source or []:
        if not ID_RE.match(s):
            print(f"[warn] invalid source id ignored: {s}", file=sys.stderr)
            continue
        sources.append(s)
    entry = {
        "type": "observation", "id": oid, "content": args.content,
        "timestamp": ts, "relevance": rel, "sourceIds": sources,
        "tokenCount": max(1, len(args.content) // 4),
    }
    _append(entry)
    print(f"[observation recorded] {oid} [{rel}] {ts}")
    return oid


def cmd_reflect(args):
    supports = []
    for s in args.supports or []:
        if not ID_RE.match(s):
            print(f"[warn] invalid support id ignored: {s}", file=sys.stderr)
            continue
        supports.append(s)
    rid = _mid(f"{args.content}|{len(_load())}")
    entry = {
        "type": "reflection", "id": rid, "content": args.content,
        "supportingObservationIds": supports,
        "tokenCount": max(1, len(args.content) // 4),
    }
    _append(entry)
    print(f"[reflection recorded] {rid} supports={supports}")
    return rid


def cmd_drop(args):
    ids = [i for i in args.ids if ID_RE.match(i)]
    bad = [i for i in args.ids if not ID_RE.match(i)]
    if bad:
        print(f"[warn] invalid ids ignored: {bad}", file=sys.stderr)
    entry = {"type": "drop", "observationIds": ids, "timestamp": _now()}
    if ids:
        _append(entry)
        print(f"[dropped] {ids}")
    else:
        print("[drop] no valid ids")
    return ids


def cmd_prune(args):
    """Auto-drop observations covered 'strong' by >=2 reflections."""
    rows = _load()
    reflections = [r for r in rows if r.get("type") == "reflection"]
    dropped = set()
    drops = [r for r in rows if r.get("type") == "drop"]
    for d in drops:
        dropped.update(d.get("observationIds", []))
    # count support per observation id
    coverage = {}
    for rf in reflections:
        for oid in rf.get("supportingObservationIds", []):
            coverage[oid] = coverage.get(oid, 0) + 1
    to_drop = [oid for oid, c in coverage.items()
               if c >= 2 and oid not in dropped]
    if to_drop:
        _append({"type": "drop", "observationIds": to_drop, "timestamp": _now()})
        print(f"[pruned] {to_drop}")
    else:
        print("[pruned] nothing eligible (need >=2 reflection coverage)")
    return to_drop


def cmd_recall(args):
    rows = _load()
    qid = args.id
    for r in rows:
        if r.get("type") == "observation" and r.get("id") == qid:
            status = "dropped" if _is_dropped(rows, qid) else "active"
            print(f"OBSERVATION [{status}] {r['id']} {r['timestamp']} [{r['relevance']}]")
            print(f"  {r['content']}")
            if r.get("sourceIds"):
                print(f"  sourceIds: {r['sourceIds']}")
            return
        if r.get("type") == "reflection" and r.get("id") == qid:
            print(f"REFLECTION {r['id']}")
            print(f"  {r['content']}")
            print(f"  supports: {r.get('supportingObservationIds', [])}")
            return
    print(f"[recall] no entry for {qid}")


def _is_dropped(rows, oid):
    for d in rows:
        if d.get("type") == "drop" and oid in d.get("observationIds", []):
            return True
    return False


def cmd_status(args):
    rows = _load()
    obs = [r for r in rows if r.get("type") == "observation"]
    refs = [r for r in rows if r.get("type") == "reflection"]
    drops = [r for r in rows if r.get("type") == "drop"]
    dropped_ids = set()
    for d in drops:
        dropped_ids.update(d.get("observationIds", []))
    active = [o for o in obs if o["id"] not in dropped_ids]
    active_tokens = sum(o.get("tokenCount", 0) for o in active)
    # drift: recorded vs visible (visible = observations not dropped)
    print(f"observations recorded : {len(obs)}")
    print(f"observations active   : {len(active)}  (dropped {len(dropped_ids)})")
    print(f"reflections           : {len(refs)}")
    print(f"active obs tokens     : {active_tokens}  (target 10000-ish)")
    # coverage tiers
    coverage = {}
    for rf in refs:
        for oid in rf.get("supportingObservationIds", []):
            coverage[oid] = coverage.get(oid, 0) + 1
    tiers = {"none": 0, "partial": 0, "strong": 0}
    for o in active:
        c = coverage.get(o["id"], 0)
        tiers["strong" if c >= 2 else "partial" if c == 1 else "none"] += 1
    print(f"coverage  none/partial/strong : {tiers['none']}/{tiers['partial']}/{tiers['strong']}")


def _projection(full=False):
    rows = _load()
    drops = [r for r in rows if r.get("type") == "drop"]
    dropped = set()
    for d in drops:
        dropped.update(d.get("observationIds", []))
    refs = [r for r in rows if r.get("type") == "reflection"]
    if full:
        obs = [r for r in rows if r.get("type") == "observation"]
    else:
        obs = [r for r in rows if r.get("type") == "observation" and r["id"] not in dropped]
    lines = []
    lines.append("These are condensed memories from earlier sessions.")
    lines.append("- Reflections: stable, long-lived facts about the user, project, decisions, and constraints.")
    lines.append("- Observations: timestamped events, chronological. Use recall <id> for source evidence.")
    lines.append("")
    lines.append("## Reflections")
    for rf in refs:
        lines.append(f"[{rf['id']}] {rf['content']}")
    lines.append("")
    lines.append("## Observations")
    for o in sorted(obs, key=lambda x: x.get("timestamp", "")):
        lines.append(f"[{o['id']}] {o['timestamp']} [{o['relevance']}] {o['content']}")
    return "\n".join(lines)


def cmd_view(args):
    print(_projection(full=args.full))


def cmd_fold(args):
    print(_projection(full=False))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("observe")
    o.add_argument("--content", required=True)
    o.add_argument("--relevance", default="medium")
    o.add_argument("--source", action="append")
    r = sub.add_parser("reflect")
    r.add_argument("--content", required=True)
    r.add_argument("--supports", action="append")
    d = sub.add_parser("drop")
    d.add_argument("--ids", nargs="+", required=True)
    sub.add_parser("prune")
    rc = sub.add_parser("recall")
    rc.add_argument("--id", required=True)
    sub.add_parser("status")
    v = sub.add_parser("view")
    v.add_argument("--full", action="store_true")
    sub.add_parser("fold")
    args = p.parse_args()
    {
        "observe": cmd_observe, "reflect": cmd_reflect, "drop": cmd_drop,
        "prune": cmd_prune, "recall": cmd_recall, "status": cmd_status,
        "view": cmd_view, "fold": cmd_fold,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
