#!/usr/bin/env python3
"""Reusable AD-HOC verification for a PyO3 hot-path accelerator.

NOT a test suite. Proves three things against the REAL app interpreter:
  A) accelerator active: native module imported, parity vs Python impl, speedup.
  B) fallback safe: with the .pyd renamed, a FRESH process falls back to
     Python and still produces correct output.

Usage:
  Set env HERMES_SRC to the app source root that contains tools/<mod>.py
  Set env MOD_NAME   to the python module name, e.g. "tools.ansi_strip"
  Set env FUNC_NAME  to the function, e.g. "strip_ansi"
  Set env RUST_MOD   to the compiled rust module, e.g. "ansi_strip_rs"
  (optional) PY_IMPL  name of the pure-python impl to compare against parity,
                      e.g. "_ANSI_ESCAPE_RE" based wrapper — if absent, parity
                      is checked by toggling the accelerator off vs on.

Run with the APP's python (the one that will actually load the .pyd):
  HERMES_SRC=... MOD_NAME=... FUNC_NAME=... RUST_MOD=... \
      /path/to/app/venv/Scripts/python.exe verify_parity_speed.py
"""
import os
import sys
import subprocess

HERMES = os.environ["HERMES_SRC"]
MOD_NAME = os.environ["MOD_NAME"]
FUNC_NAME = os.environ["FUNC_NAME"]
RUST_MOD = os.environ["RUST_MOD"]

# locate the native .pyd inside the app venv site-packages
pyd = None
sp = os.path.join(HERMES, "venv", "Lib", "site-packages")
for root, _, files in os.walk(sp):
    for f in files:
        if f.startswith(RUST_MOD) and f.endswith(".pyd"):
            pyd = os.path.join(root, f)
print(f"[setup] native pyd: {pyd}")

CHECK_A = r'''
import sys, os, time, importlib, random
HERMES = os.environ["HERMES_SRC"]
MOD_NAME = os.environ["MOD_NAME"]
FUNC_NAME = os.environ["FUNC_NAME"]
RUST_MOD = os.environ["RUST_MOD"]
sys.path.insert(0, HERMES)
m = importlib.import_module(MOD_NAME)
fn = getattr(m, FUNC_NAME)
# parity vs fallback: force python path by toggling the rust flag off
has_rust = getattr(m, "_HAS_RUST_ACCEL", False)
# build a python-only reference: if module exposes _PYTHON_IMPL use it,
# else compare by importing the rust module's pure-python branch indirectly.
ESC = chr(27); OSC8 = chr(155)
cases = ["plain", ESC+"[31mred"+ESC+"[0m", OSC8+"31m"+OSC8+"0m",
         "emoji \U0001f680 hi", "", ESC, ESC+chr(128),
         "mix"+ESC+"[1;32m"+ESC+"]0;x"+chr(7)+ESC+"[0mend"]
# Reference = result with accelerator disabled (re-import without rust mod)
import importlib.util
# mask the rust module so the fallback engages
sys.modules.pop(RUST_MOD, None)
# re-import fresh in a subprocess-free way: just call the python branch if present
py_ref = None
if hasattr(m, "_PYTHON_IMPL"):
    py_impl = getattr(m, "_PYTHON_IMPL")
    py_ref = [py_impl(c) for c in cases]
else:
    # fallback: disable flag and call
    m._HAS_RUST_ACCEL = False
    py_ref = [fn(c) for c in cases]
    m._HAS_RUST_ACCEL = has_rust
rs_ref = [fn(c) for c in cases]
bad = sum(1 for a, b in zip(py_ref, rs_ref) if a != b)
print("ACCEL_ACTIVE", has_rust)
print("PARITY_FAILS", bad)
random.seed(9)
hit = ESC+"[32m"+ESC+"]0;x"+chr(7)+"d"+ESC+"[0m\n"
lines = [("ok: line\n" + (hit if random.random() < 0.15 else "")) for _ in range(70000)]
pay = "".join(lines)
fn(pay[:1000])
def t(fn_, r=60):
    s = time.perf_counter()
    for _ in range(r): fn_(pay)
    return (time.perf_counter() - s) / r
# speed: python branch vs rust branch
m._HAS_RUST_ACCEL = False
pt = t(fn)
m._HAS_RUST_ACCEL = has_rust
rt = t(fn)
print("SPEEDUP", round(pt / rt, 2))
print("VERDICT_A", "PASS" if (has_rust and bad == 0 and rt <= pt) else "FAIL")
'''

CHECK_B = r'''
import sys, os, importlib
HERMES = os.environ["HERMES_SRC"]
MOD_NAME = os.environ["MOD_NAME"]
FUNC_NAME = os.environ["FUNC_NAME"]
RUST_MOD = os.environ["RUST_MOD"]
sys.path.insert(0, HERMES)
# ensure rust module is NOT importable
sys.modules[RUST_MOD] = None
m = importlib.import_module(MOD_NAME)
fn = getattr(m, FUNC_NAME)
print("ACCEL_ACTIVE", getattr(m, "_HAS_RUST_ACCEL", "MISSING"))
ok = fn(chr(27)+"[31mhi"+chr(27)+"[0m") == "hi"
print("STRIP_OK", ok)
print("VERDICT_B", "PASS" if (not getattr(m, "_HAS_RUST_ACCEL", True) and ok) else "FAIL")
'''

APP_PY = os.path.join(HERMES, "venv", "Scripts", "python.exe")

def run(label, code, rename_pyd):
    disabled = pyd + ".disabled" if (pyd and rename_pyd) else None
    if disabled:
        os.rename(pyd, disabled)
    try:
        p = subprocess.run([APP_PY, "-c", code], capture_output=True, text=True,
                           cwd=HERMES, env=dict(os.environ))
        print(f"--- {label} (exit {p.returncode}) ---")
        print(p.stdout.strip())
        if p.stderr.strip():
            print("STDERR:", p.stderr.strip()[:300])
        return "PASS" in p.stdout
    finally:
        if disabled:
            os.rename(disabled, pyd)

import tempfile
fa = os.path.join(tempfile.gettempdir(), "hermes-verify-A.py")
with open(fa, "w") as f:
    f.write(CHECK_A)
fb = os.path.join(tempfile.gettempdir(), "hermes-verify-B.py")
with open(fb, "w") as f:
    f.write(CHECK_B)

ok_a = run("CHECK A (accelerator)", f"exec(open(r'{fa}').read())", rename_pyd=False)
ok_b = run("CHECK B (fallback, pyd renamed)", f"exec(open(r'{fb}').read())", rename_pyd=True)

for x in (fa, fb):
    try: os.remove(x)
    except OSError: pass

print(f"\n[FINAL] A={ok_a} B={ok_b} -> {'PASS' if ok_a and ok_b else 'FAIL'}")
sys.exit(0 if (ok_a and ok_b) else 1)
