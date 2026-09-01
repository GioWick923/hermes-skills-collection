# -*- coding: utf-8 -*-
"""Ad-hoc verification harness for a cron content-delivery script.

Correctly mocks the wall clock by monkeypatching the REAL datetime.datetime class
(because the target does `import datetime`, patching the test module's binding fails).

Usage:
  python scripts/verify_cron_script.py <path/to/script.py> <marker1> [marker2 ...]

It re-execs the target at hours 9, 14, 20 on a fixed date and asserts:
  - output is produced at every hour
  - the three hour-runs are DISTINCT (date+hour seed works)
  - the declared markers (e.g. 🇪🇸 🔊 📂) appear in output
  - spaced repetition triggers when old history entries (>=2 days) are present

Backs up and restores any real english_history.json next to the target so the
live cron is not disturbed. Cleans up the temp history when done.
"""
import os, sys, io, contextlib, json, importlib.util, datetime

if len(sys.argv) < 3:
    print("usage: python verify_cron_script.py <script.py> <marker> ...")
    sys.exit(2)

SCRIPT = os.path.abspath(sys.argv[1])
MARKERS = sys.argv[2:]
HIST = os.path.join(os.path.dirname(SCRIPT), "english_history.json")

real_hist = open(HIST, encoding="utf-8").read() if os.path.exists(HIST) else None

results = []
def check(n, ok, d=""):
    results.append(ok)
    print(("PASS" if ok else "FAIL"), "-", n, ("| " + d) if d else "")

_orig_dt = datetime.datetime
class FakeDT(_orig_dt):
    _fake = None
    @classmethod
    def now(cls, tz=None):
        f = cls._fake
        return cls(f.year, f.month, f.day, f.hour, f.minute)
datetime.datetime = FakeDT

def capture(hour):
    FakeDT._fake = datetime.datetime(2026, 7, 12, hour, 0)
    if os.path.exists(HIST):
        os.remove(HIST)
    buf = io.StringIO()
    spec = importlib.util.spec_from_file_location("ep_%d" % hour, SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(buf):
        spec.loader.exec_module(mod)
    return buf.getvalue()

c9, c14, c20 = capture(9), capture(14), capture(20)
check("3 schedules produce output", all([c9, c14, c20]))
check("schedule 09 != 14 (distinct)", c9 != c14)
check("schedule 14 != 20 (distinct)", c14 != c20)
check("schedule 09 != 20 (distinct)", c9 != c20)
for mk in MARKERS:
    check("output has marker %r" % mk, mk in c9)

# spaced repetition: inject >=2-day-old entries
old = [{"en": "X1", "date": "2026-07-09", "cat": "c"},
       {"en": "X2", "date": "2026-07-09", "cat": "c"}]
with open(HIST, "w", encoding="utf-8") as f:
    json.dump(old, f, ensure_ascii=False)
found = False
for h in range(24):
    FakeDT._fake = datetime.datetime(2026, 7, 12, h, 0)
    if os.path.exists(HIST):
        # re-write old seed so it persists across this run's append
        with open(HIST, "w", encoding="utf-8") as f:
            json.dump(old, f, ensure_ascii=False)
    buf = io.StringIO()
    spec = importlib.util.spec_from_file_location("ep_r_%d" % h, SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(buf):
        spec.loader.exec_module(mod)
    if "REFUERZO" in buf.getvalue():
        found = True
        break
check("spaced repetition (REFUERZO) triggers from old entries", found)

datetime.datetime = _orig_dt
if real_hist is not None:
    open(HIST, "w", encoding="utf-8").write(real_hist)
elif os.path.exists(HIST):
    os.remove(HIST)

passed = sum(1 for r in results if r)
print("\n=== %d/%d checks passed (ad-hoc) ===" % (passed, len(results)))
sys.exit(0 if passed == len(results) else 1)
