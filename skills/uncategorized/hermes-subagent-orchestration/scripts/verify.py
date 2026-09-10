#!/usr/bin/env python3
"""Ad-hoc verification for hermes-subagent-orchestration/orch.py.
Isolates APPDATA to a temp dir so the real state file is never touched.
Run: python scripts/verify.py   (from the skill directory)
This is AD-HOC verification, not a committed test suite.
"""
import os, sys, subprocess, tempfile, json, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "orch.py")


def run(appdata_tmp, *args):
    env = dict(os.environ)
    env["APPDATA"] = appdata_tmp
    p = subprocess.run([sys.executable, ENGINE, *args],
                       capture_output=True, text=True, env=env)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def main():
    tmp = tempfile.mkdtemp(prefix="hermes-verify-orch-")
    state_dir = os.path.join(tmp, "hermes", "subagent-orchestration")
    os.makedirs(state_dir, exist_ok=True)
    fails = []
    try:
        rc, out, err = run(tmp, "role", "--list")
        assert rc == 0, err
        for role in ("planner", "scout", "worker", "reviewer"):
            assert role in out, f"role {role} missing"

        rc, out, err = run(tmp, "role", "--name", "worker")
        assert rc == 0, err
        spec = json.loads(out)
        assert "toolsets" in spec and "system" in spec

        rc, out, err = run(tmp, "spawn", "--role", "worker", "--name", "W1",
                           "--task", "implement login")
        assert rc == 0 and "[spawned]" in out and "starting" in out, f"spawn: {out} {err}"
        assert "delegate_task" in out

        rc, out, err = run(tmp, "ping", "--name", "W1", "--message", "schema?")
        assert rc == 0 and "[caller_ping]" in out, f"ping: {out} {err}"

        rc, out, err = run(tmp, "status")
        assert rc == 0 and "W1" in out, f"status: {out} {err}"

        lf = os.path.join(state_dir, "state.jsonl")
        rows = [json.loads(l) for l in open(lf, encoding="utf-8") if l.strip()]
        for r in rows:
            if r.get("name") == "W1":
                r["ts"] = "2000-01-01 00:00:00"
        with open(lf, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        rc, out, err = run(tmp, "watch", "--timeout-min", "1")
        assert rc == 0 and "W1" in out, f"watch should flag W1: {out} {err}"

        rc, out, err = run(tmp, "close", "--name", "W1")
        assert rc == 0 and "[closed]" in out, f"close: {out} {err}"
        rc, out, err = run(tmp, "watch", "--timeout-min", "1")
        assert rc == 0 and "W1" not in out, f"watch should skip done W1: {out} {err}"

        rc, out, err = run(tmp, "plan", "--goal", "dark mode")
        assert rc == 0 and "1. Investigate" in out and "6. Close" in out, f"plan: {out} {err}"

        with open(lf, encoding="utf-8") as f:
            for line in f:
                json.loads(line)
    except AssertionError as e:
        fails.append(str(e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print("VERIFY: FAIL")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("VERIFY: PASS -- orch.py checks passed (ad-hoc, isolated APPDATA, FRESH).")


if __name__ == "__main__":
    main()
