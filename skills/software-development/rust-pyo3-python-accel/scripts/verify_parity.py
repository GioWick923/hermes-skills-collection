"""Reusable AD-HOC parity + speedup harness for a PyO3 port.

NOT a test suite. Validates a compiled Rust module against the ORIGINAL
Python function for (1) output parity on a broad case list and (2) not being
slower. Adjust ORIG_IMPORT / RS_IMPORT / CASES / payload builder per module.

Usage:
  export PATH="$HOME/.local/bin:$PATH"
  MSVC_BIN=".../VC/Tools/MSVC/<ver>/bin/Hostx64/x64"; export PATH="$MSVC_BIN:$PATH"
  cd <project>; source .venv/Scripts/activate
  python verify_parity.py
Exit 0 only if parity holds AND rust is not slower.
"""
import sys, time, importlib, random

# --- point these at the real implementations ---
ORIG_IMPORT = "tools.ansi_strip"          # module path of ORIGINAL
ORIG_FN = "strip_ansi"
RS_IMPORT = "ansi_strip_rs"               # compiled Rust module
RS_FN = "strip_ansi"
HERMES_SRC = r"C:\Users\<USER> GAMES\AppData\Local\hermes\hermes-agent"

sys.path.insert(0, HERMES_SRC)
py_fn = getattr(importlib.import_module(ORIG_IMPORT), ORIG_FN)
rs_fn = getattr(importlib.import_module(RS_IMPORT), RS_FN)

CASES = [
    "plain text",
    "\x1b[31mred\x1b[0m",
    "\x1b]0;t\x07a",
    "\x1b]2;t\x1b\\a",
    "\x9b31m\x9b0m",
    "\x9d1;2\x9ct",
    "mix\x1b[1;32m\x1b]0;x\x07\x1b[0mend",
    "emoji \U0001f680 and \u4f60\u597d",
    "",
    "\x1b",            # lone ESC must be KEPT (regex strips only full sequences)
    "\x1b\x80",        # ESC + C1 byte
    "esc+newline\x1b\nkeep",
]
fails = 0
for c in CASES:
    if py_fn(c) != rs_fn(c):
        fails += 1
        print(f"  PARITY FAIL: {c!r} py={py_fn(c)!r} rs={rs_fn(c)!r}")
print(f"[parity] {len(CASES)-fails}/{len(CASES)} ok")

assert py_fn("no escapes") == rs_fn("no escapes") == "no escapes"
print("[fastpath] unchanged-on-no-escape ok")

random.seed(3)
ch = []
for _ in range(70000):
    ch.append("ok: wrote 1234 bytes in 0.02s\n")
    if random.random() < 0.15:
        ch.append("\x1b[32m\x1b]0;x\x07d\x1b[0m\n")
payload = "".join(ch)
py_fn(payload[:1000]); rs_fn(payload[:1000])
def t(fn, r=80):
    s = time.perf_counter()
    for _ in range(r): fn(payload)
    return (time.perf_counter() - s) / r
pt, rt = t(py_fn), t(rs_fn)
print(f"[speed] py={len(payload)/1e6/pt:5.1f} MB/s rs={len(payload)/1e6/rt:5.1f} MB/s speedup={pt/rt:.2f}x")
ok = (fails == 0) and (rt <= pt)
print(f"[verdict] {'PASS' if ok else 'FAIL'} (parity_fails={fails}, rust_not_slower={rt<=pt})")
sys.exit(0 if ok else 1)
