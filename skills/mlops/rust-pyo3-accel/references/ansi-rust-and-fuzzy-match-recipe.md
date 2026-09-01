# Real session recipe: Rust-accelerating Hermes `tools/fuzzy_match.py` (strategy 2)

Goal: speed up the line-normalization hot path of `fuzzy_find_and_replace`
(the `line_trimmed` strategy, ~6 ms on a 6000-line file) with a Rust
preprocessing step, WITHOUT changing matching behavior.

## Environment
- Windows 11 + Git Bash (MSYS). Rust 1.97, MSVC BuildTools 2022 (cl present).
- Hermes runs on a venv: `C:\Users\<USER> GAMES\AppData\Local\hermes\hermes-agent\venv` (Python 3.11.15, cp311 ABI, `.cp311-win_amd64.pyd`).
- `maturin` NOT installed -> used the no-maturin `.cdylib`->`.pyd` path.
- `python311.lib` located at `C:\Users\<USER> GAMES\AppData\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\libs\python311.lib` (PyO3 finds it via `PYO3_PYTHON`).

## 1. Profiling first (find the real bottleneck)
Ad-hoc `terminal` script run with the venv python:
- `exact` strategy: ~0.5 ms.
- `whitespace-drift` (hits `line_trimmed`): ~6.3 ms -> 11x the cost.
Bottleneck = `content.split('\n')` + `[line.strip() for line]` per call.
Decision: accelerate ONLY `stripped_lines`; do NOT port the whole
`fuzzy_match` (9 strategies + `difflib` + fragile position maps, NO existing
tests -> too risky).

## 2. Crate (C:\fuzzy_norm_rs)
Cargo.toml:
```toml
[package]
name = "fuzzy_norm_rs"
version = "0.1.0"
edition = "2021"
[lib]
name = "fuzzy_norm_rs"
crate-type = ["cdylib"]
[dependencies]
pyo3 = { version = "0.23", features = ["extension-module"] }
```
lib.rs (parity contract):
```rust
use pyo3::prelude::*;
use pyo3::types::PyList;

#[pyfunction]
fn stripped_lines(py: Python, content: &str) -> PyResult<Py<PyList>> {
    let mut out: Vec<PyObject> = Vec::with_capacity(content.len() / 40 + 1);
    for raw in content.split('\n') {
        out.push(raw.trim().into_pyobject(py)?.into_any().unbind());
    }
    Ok(PyList::new_bound(py, out).unbind())
}

#[pyfunction]
fn collapse_ws(_py: Python, s: &str) -> PyResult<String> {
    let mut out = String::with_capacity(s.len());
    let mut in_ws = false;
    for ch in s.chars() {
        if ch == ' ' || ch == '\t' {
            if !in_ws { out.push(' '); in_ws = true; }
        } else { out.push(ch); in_ws = false; }
    }
    Ok(out)
}

#[pymodule]
fn fuzzy_norm_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(stripped_lines, m)?)?;
    m.add_function(wrap_pyfunction!(collapse_ws, m)?)?;
    Ok(())
}
```
Build (offline, reuses pyo3 from registry cache of a sibling crate):
```bash
cd /c/fuzzy_norm_rs
export CARGO_NET_OFFLINE=true
export PYO3_PYTHON="$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/python.exe"
export PYTHON_SYS_EXECUTABLE="$PYO3_PYTHON"
cargo build --release
cp target/release/fuzzy_norm_rs.dll target/release/fuzzy_norm_rs.pyd
SP=$("$PYO3_PYTHON" -c "import site; print(site.getsitepackages()[0])")
cp target/release/fuzzy_norm_rs.pyd "$SP/fuzzy_norm_rs.pyd"
```

## 3. Python integration (tools/fuzzy_match.py) - safe fallback
```python
try:
    import fuzzy_norm_rs as _fuzzy_norm_rs
    _HAS_RUST_NORM = True
except Exception:
    _fuzzy_norm_rs = None
    _HAS_RUST_NORM = False

def _stripped_lines(content):
    if _HAS_RUST_NORM:
        return list(_fuzzy_norm_rs.stripped_lines(content))
    return [line.strip() for line in content.split('\n')]
```
Then in `_strategy_line_trimmed` replace the two list comprehensions with
`_stripped_lines(content)` / `_stripped_lines(pattern)`. All matching and
position-mapping stays in Python -> byte-identical output.

## 4. Verification
- helper parity: `parity_test.py` - 2012 fuzz+edge cases, `stripped_lines` and
  `collapse_ws` Rust vs `re.sub`/`.strip` -> 0 divergences, ~2.0x speedup.
- behavior parity: call `fuzzy_find_and_replace(c,o,nw)` with `_HAS_RUST_NORM=True`
  then `=False` over 3000 fuzz cases (indents 0/2/4/6, multi-line blocks) ->
  0 divergences. This is the strongest proof that the integration didn't
  shift match positions.
- fallback: `.pyd` present -> `_HAS_RUST_NORM True`; rename it -> `False` and
  function still correct (must test in a fresh subprocess).

## Results
- 6000-line file: ~1.5 ms (py) -> ~0.8 ms (rust) in `_stripped_lines` = 2x.
- Whole `fuzzy_find_and_replace` drift case: behavior identical.
- Zero risk: dropping the `.pyd` reproduces the pure-Python path exactly.
