#!/usr/bin/env python3
"""Ad-hoc verification for hermes-observational-memory/leager.py.
Isolates APPDATA to a temp dir so the real ledger is never touched.
Run: python scripts/verify.py   (from the skill directory)
This is AD-HOC verification, not a committed test suite.
"""
import os, sys, subprocess, tempfile, json, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "leager.py")


def run(appdata_tmp, *args):
    env = dict(os.environ)
    env["APPDATA"] = appdata_tmp
    p = subprocess.run([sys.executable, ENGINE, *args],
                       capture_output=True, text=True, env=env)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def main():
    tmp = tempfile.mkdtemp(prefix="hermes-verify-")
    ledger_dir = os.path.join(tmp, "hermes", "observational-memory")
    os.makedirs(ledger_dir, exist_ok=True)
    failures = []
    try:
        rc, out, err = run(tmp, "observe", "--content", "obs A crit",
                           "--relevance", "critical")
        assert rc == 0 and "[observation recorded]" in out, f"observe1: {out} {err}"
        oid_a = out.split()[2]
        rc, out, err = run(tmp, "observe", "--content", "obs B high", "--relevance", "high")
        oid_b = out.split()[2]
        rc, out, err = run(tmp, "observe", "--content", "obs C med", "--relevance", "medium")
        oid_c = out.split()[2]

        rc, out, err = run(tmp, "reflect", "--content", "ref durable 1",
                           "--supports", oid_a, "--supports", oid_a)
        assert rc == 0 and "[reflection recorded]" in out, f"reflect: {out} {err}"

        rc, out, err = run(tmp, "prune")
        assert rc == 0 and oid_a in out, f"prune: {out} {err}"

        rc, out, err = run(tmp, "recall", "--id", oid_a)
        assert rc == 0 and "OBSERVATION [dropped]" in out, f"recall: {out} {err}"

        rc, out, err = run(tmp, "recall", "--id", "deadbeef0000")
        assert rc == 0 and "no entry" in out, f"recall-unknown: {out} {err}"

        rc, out, err = run(tmp, "fold")
        assert rc == 0, f"fold: {err}"
        assert oid_a not in out and oid_b in out and oid_c in out, "fold leak/omit"

        rc, out, err = run(tmp, "status")
        assert rc == 0, f"status: {err}"
        assert "observations active   : 2" in out
        assert "observations recorded : 3" in out
        assert "reflections           : 1" in out

        rc, out, err = run(tmp, "drop", "--ids", oid_b)
        assert rc == 0 and oid_b in out, f"drop: {out} {err}"
        rc, out, err = run(tmp, "recall", "--id", oid_b)
        assert rc == 0 and "[dropped]" in out, f"drop-recall: {out} {err}"

        rc, out, err = run(tmp, "observe", "--content", "x", "--source", "zzz")
        assert rc == 0 and "invalid source id ignored" in err, f"invalid: {out} {err}"

        lf = os.path.join(ledger_dir, "ledger.jsonl")
        assert os.path.exists(lf)
        with open(lf, encoding="utf-8") as f:
            for line in f:
                json.loads(line)
    except AssertionError as e:
        failures.append(str(e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print("VERIFY: FAIL")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("VERIFY: PASS -- all checks on leager.py passed (ad-hoc, isolated APPDATA).")


if __name__ == "__main__":
    main()
