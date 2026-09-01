---
name: rust-pyo3-accel
description: >-
  Port CPU-bound / repetitive Python hot-paths to Rust via PyO3 for 3-10x
  speedups, with the Windows-specific build setup that actually works
  (MSVC linker, Git-Bash link.exe shadow, PATH ordering, Python-ABI
  targeting) plus a safe fallback-integration and ad-hoc verification
  pattern. Use when accelerating small repetitive Python (ANSI stripping,
  fuzzy/regex matching, token counting, string parsing) WITHOUT rewriting
  the whole program — leave 90% in Python, ship only the hot loop as a
  native module with a transparent Python fallback.
---

# Accelerate Python hot-paths with Rust (PyO3) — Windows

## When to use
- A Python function runs on every turn / every command and shows up as a
  CPU bottleneck (string/regex/parsing/serialization loops).
- You want speed without rewriting the whole app or breaking behavior.
- Target is **Windows with Git Bash** (MSYS) — the hardest environment.
  On Linux/macOS the same PyO3 flow is simpler (system linker just works).

## When NOT to use
- I/O-bound code (LLM calls, network, sqlite waits) — Rust won't help.
- One-shot scripts / prototypes.
- Code deeply tied to pure-Python libs (pandas/numpy internals).

## Decision: hybrid, not rewrite
Keep the Python module as the public API. Try `from rust_mod import fn`;
on failure fall back to the pure-Python implementation. Output must be
**byte-identical** so the swap is invisible. This is what makes it safe to
ship into a live agent like Hermes.

## Workflow (Windows + Git Bash)
1. **Toolchain**: Rust (`rustup`), `uv`, and `maturin`.
   - `uv tool install maturin` (lands in `~/.local/bin` — add to PATH).
   - `rustc --version` / `cargo --version` must exist.
2. **MSVC C++ linker is REQUIRED** (the default toolchain is
   `x86_64-pc-windows-msvc`; MinGW `ld` is NOT installed by default and
   `winget` alone often fails to add the VC components). Install via the
   official bootstrapper:
   ```bash
   curl -sL -o vsbt.exe "https://aka.ms/vs/17/release/vs_BuildTools.exe"
   ./vsbt.exe --add Microsoft.VisualStudio.Workload.VCTools \
              --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 \
              --add Microsoft.VisualStudio.Component.Windows11SDK.22621 \
              --quiet --wait
   ```
   (Note: `winget install ... --override "--add ..."` reported "already
   installed" and skipped the VC components — the bootstrapper above is
   the reliable path.)
3. **The Git-Bash `link.exe` trap** (the #1 gotcha): MSYS ships
   `/usr/bin/link`, which shadows the MSVC `link.exe`. Rust's linker call
   fails with `link: extra operand`. Fix: put the MSVC bin dir FIRST on
   PATH before compiling:
   ```bash
   MSVC_BIN="/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/<ver>/bin/Hostx64/x64"
   WIN_SDK="/c/Program Files (x86)/Windows Kits/10/bin/10.0.22621.0/x64"
   export PATH="$MSVC_BIN:$WIN_SDK:$PATH"   # MSVC link.exe must win over /usr/bin/link
   ```
   (`vcvarsall.bat x64` does NOT chain reliably under Git Bash `cmd /c`;
   manual PATH prepend works.)
4. **Target the RIGHT Python ABI**. A PyO3 wheel is ABI-locked to the
   Python that built it. If you compile under a demo venv (e.g. py3.13) but
   the real app runs py3.11, the `.pyd` will NOT import. **Activate the
   real app's venv before `maturin develop`** so the wheel targets cp311:
   ```bash
   source "<APP>/venv/Scripts/activate"
   maturin develop --release
   ```
5. **Verify it actually loads in the real interpreter** (see below).

## No-maturin build path (when `maturin` is NOT installed)
If `uv tool install maturin` is unavailable/offline, you can still ship a
`.pyd` without maturin: compile a `cdylib` and rename the `.dll` to `.pyd`.
This reuses any already-downloaded pyo3 in the cargo registry cache (offline
build works if a sibling crate already resolved pyo3).
```bash
# Cargo.toml: [lib] crate-type=["cdylib"]; pyo3 = { version="0.23", features=["extension-module"] }
cd /c/fuzzy_norm_rs
export CARGO_NET_OFFLINE=true                         # reuse registry cache
export PYO3_PYTHON="$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/python.exe"
export PYTHON_SYS_EXECUTABLE="$PYO3_PYTHON"
cargo build --release
cp target/release/fuzzy_norm_rs.dll target/release/fuzzy_norm_rs.pyd
SP=$("$PYO3_PYTHON" -c "import site; print(site.getsitepackages()[0])")
cp target/release/fuzzy_norm_rs.pyd "$SP/fuzzy_norm_rs.pyd"   # importable by the app
```
The lib name in `Cargo.toml` `[lib] name = "fuzzy_norm_rs"` must equal the
desired import name (Python imports `fuzzy_norm_rs.pyd`).

### pyo3 0.23 API gotchas (compile breakers)
- `PyList` is now `Bound<PyList>`; use `PyList::new_bound(py, items)` (renamed
  to `PyList::new` — `.new_bound` only warns) and `.unbind()`.
- `val.into_py(py)` is **deprecated** → use `val.into_pyobject(py)?.into_any().unbind()`.
- `#[pymodule] fn name(m: &Bound<'_, PyModule>)` takes a `Bound`, not `PyModule`.
- `rustfmt` may be absent on the stable toolchain → `write_file` lint errors
  `rustfmt.exe is not installed`; that's a linter warning, NOT a compile error.
  Build with `cargo build` to get the real verdict.

### write_file drive-letter pitfall (Git Bash / MSYS)
Writing to a path like `/c/fuzzy_norm_rs/...` can resolve to
`C:\c\fuzzy_norm_rs\...` (a stray directory OUTSIDE the workspace, with the
literal `c` duplicated). This wastes a write and confuses later steps. ALWAYS
pass a **native Windows absolute path** (`C:\fuzzy_norm_rs\...`) to `write_file`,
and after creating crates, `rm -rf` any `C:\c\...` strays you spot.

## Integration pattern (safe fallback)
In the Python module, keep the original impl and wrap:
```python
try:
    from rust_mod import strip_ansi as _rs_strip_ansi
    _HAS_RUST_ACCEL = True
except Exception:   # ImportError, missing .pyd, ABI mismatch
    _HAS_RUST_ACCEL = False

def strip_ansi(text):
    if _HAS_RUST_ACCEL:
        return _rs_strip_ansi(text)
    return _PYTHON_IMPL(text)   # unchanged original
```
Behavior is identical either way; if the native module is absent the app
keeps working.

## Verification (ad-hoc, but rigorous)
Do NOT claim done on a green unit mock. Prove parity + speed + fallback:
- **Parity (helper level)**: same inputs vs the Python impl (incl. 8-bit C1,
  lone ESC, unicode/emoji, OSC/CSI, empty string, trailing `\n`, tabs, CRLF,
  multibyte UTF-8) → 0 differences.
- **Behavior parity (WHOLE-FUNCTION level — strongest check)**: when the Rust
  fn is only a *preprocessing* step inside a larger function (e.g.
  `fuzzy_find_and_replace` calls a Rust `stripped_lines`), call the WHOLE
  function with Rust ON and with Rust OFF (toggle the `_HAS_RUST_*` flag) over
  thousands of fuzz inputs and assert results are **identical**. This catches
  divergence in downstream position-mapping logic a helper test misses.
- **Speed**: realistic payload, ~300 runs, report ms/call + speedup.
  **Honest calibration**: when the Python hot path is already sub-ms (a 6000-line
  strip loop at ~1.5 ms), expect **1.5–2x**, not 3–10x. The 3–10x figure applies
  to genuinely heavy loops (ANSI strip of MB, regex over large text). Don't
  over-promise the user a 10x on a tiny op.
- **Fallback**: rename the `.pyd` and import in a FRESH process →
  `_HAS_RUST_ACCEL False` and `strip_ansi` still correct.

### Verification pitfalls (learned the hard way)
- Write checks as **separate `.py` files**, not `python -c "..."`. Raw
  `-c` strings mangle backslashes (`C:\Users` → unicodeescape error) and
  embedded `\n` breaks string literals.
- Pass paths via **env var** (`HERMES_SRC=... python check.py`), never
  interpolated into the code string.
- Test fallback in a **new subprocess**, not `importlib.reload` in the same
  process — a loaded `.pyd` stays cached and reload won't re-run the
  module-level `try/except`.
- Use `chr(27)` / `chr(155)` instead of `\x1b` literals inside generated
  check code to avoid escape surprises.

## Files in this skill
- `references/windows-msvc-maturin.md` — exact commands, paths, error→fix map.
- `references/ansi-rust-and-fuzzy-match-recipe.md` — full real-session recipe
  (no-maturin build, pyo3 0.23 code, behavior-parity tier, Hermes fuzzy_match
  case). Copy/adapt as a template for any new hot-path port.
- `templates/pyo3-skeleton/` — minimal Cargo.toml + pyproject.toml + lib.rs.
- `scripts/verify_parity_speed.py` — reusable ad-hoc verification scaffold.
