<!-- Minimal PyO3 crate skeleton for a string-processing hot-path.
     Copy this dir, rename crate, implement the function, then build with maturin. -->

<!-- Cargo.toml -->
[package]
name = "ansi_strip_rs"
version = "0.1.0"
edition = "2021"

[lib]
name = "ansi_strip_rs"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.23", features = ["extension-module"] }

<!-- pyproject.toml -->
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[project]
name = "ansi_strip_rs"
version = "0.1.0"
description = "Rust-accelerated drop-in for a Python hot-path (PyO3)"
requires-python = ">=3.10"

<!-- src/lib.rs (skeleton: char-by-char state machine, iterate chars NOT bytes
     so multi-byte UTF-8 / emoji / CJK is preserved) -->
use pyo3::prelude::*;

#[pyfunction]
fn strip_ansi(text: &str) -> String {
    // Fast path: bail if no ESC (0x1B) and no 8-bit C1 (0x80-0x9F).
    let has_escape = text.bytes().any(|b| b == 0x1B || (0x80..=0x9F).contains(&b));
    if !has_escape {
        return text.to_string();
    }
    let chars: Vec<char> = text.chars().collect();
    let n = chars.len();
    let mut out: Vec<char> = Vec::with_capacity(n);
    let mut i = 0;
    while i < n {
        let c = chars[i] as u32;
        if c == 0x1B {
            // ESC sequence — implement CSI/OSC/DCS/nF handling here.
            // Unknown ESC (no valid sequence follows): KEEP the ESC and
            // advance 1, so output matches a regex that only strips full
            // sequences (matches Python re.sub behavior).
            out.push(chars[i]);
            i += 1;
            continue;
        }
        if (0x80..=0x9F).contains(&c) {
            // 8-bit C1 control: drop, EXCEPT 0x9B (8-bit CSI) / 0x9D
            // (8-bit OSC) which begin sequences — handle those explicitly.
            i += 1;
            continue;
        }
        out.push(chars[i]);
        i += 1;
    }
    out.iter().collect()
}

#[pymodule]
fn ansi_strip_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(strip_ansi, m)?)?;
    Ok(())
}
