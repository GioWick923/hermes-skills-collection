---
name: rust-pyo3-python-accel
description: Accelerate CPU-bound Python hot paths by porting them to Rust exposed via PyO3 + maturin. Covers candidate selection, the build workflow on Windows (MSVC linker shadowing pitfalls), UTF-8-correct string processing, and parity + benchmark verification. Use when the user wants to speed up Python code, especially repetitive/small hot paths in an agent, CLI, or tool.
---

# Rust / PyO3 Python Acceleration

## When to use
- The user wants to speed up Python ("port this to Rust", "make X faster", "rewrite in Rust").
- You identify a *CPU-bound, repetitive* hot path: tight loops over strings/bytes, regex over large inputs, token counting, fuzzy matching, compression pre-passes.
- Do NOT port I/O-bound code (network, DB, waiting on an LLM) — Rust gives no speedup there.

## Decision framework (what is worth porting)
**Worth it:** small functions called constantly on data — ANSI stripping, fuzzy find/replace, token estimation, parsers, diff-ish loops.
**Marginal:** code that mostly waits on external calls (context compressors that call an LLM).
**Skip:** one-off scripts, code deep inside Python-only libs (pandas/numpy internals already call into C).

Real example: introspecting the Hermes agent found `tools/ansi_strip.py` (runs on EVERY terminal command) and `tools/fuzzy_match.py` (runs on every file edit) as the top candidates — both small, CPU-bound, high-frequency. `session_search` (SQLite) and `prompt_builder` (string concat before LLM send) were correctly skipped.

## Build workflow (PyO3 + maturin)
1. `uv tool install maturin` — NOT on PATH by default on Windows; prepend `$HOME/.local/bin`.
2. `uv venv .venv` then `source .venv/Scripts/activate` (Git Bash). `maturin develop` REQUIRES an active venv.
3. `Cargo.toml`: `crate-type = ["cdylib"]`, `pyo3 = { version = "0.23", features = ["extension-module"] }`.
4. `src/lib.rs`: `#[pyfunction] fn name(...)` + `#[pymodule]`.
5. `maturin develop --release`.

## Pitfalls (Windows / Git Bash) — CRITICAL
**Linker shadowing.** On Git Bash, `which link` resolves to `/usr/bin/link` (MSYS), NOT MSVC's `link.exe`. Rust (target `x86_64-pc-windows-msvc`) fails to link with cryptic "link: extra operand" errors. FIX: prepend the MSVC bin dir to PATH *manually* before building:
```bash
MSVC_BIN="/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/<ver>/bin/Hostx64/x64"
export PATH="$MSVC_BIN:$PATH"
```
Do NOT rely on `cmd.exe /c "call vcvarsall.bat x64 && maturin ..."` — in Git Bash the `.bat` chaining printed only the cmd banner and swallowed all build output (silent failure). Manual PATH prepend works reliably.

**MSVC Build Tools missing the C++ workload.** `winget install Microsoft.VisualStudio.2022.BuildTools` may report "already installed" (exit 43 / "no update available") while `VC/Tools/MSVC/` stays EMPTY (no `link.exe`). FIX: download the bootstrapper and add components explicitly:
```bash
curl -sL -o vsbt.exe "https://aka.ms/vs/17/release/vs_BuildTools.exe"
./vsbt.exe --add Microsoft.VisualStudio.Workload.VCTools \
           --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 \
           --add Microsoft.VisualStudio.Component.Windows11SDK.22621 \
           --quiet --wait
```
Then verify `VC/Tools/MSVC/<ver>/bin/Hostx64/x64/link.exe` and `.../VC/Auxiliary/Build/vcvarsall.bat` exist. The `<ver>` dir appears only after this step (e.g. `14.44.35207`).

## Pitfalls (correctness)
**UTF-8: iterate `char`s, not bytes.** If you process text, `let chars: Vec<char> = text.chars().collect();` and preserve multi-byte chars (emoji, CJK) as single units. Iterating raw bytes and dropping `0x80..=0x9F` corrupts UTF-8 sequences whose trailing bytes fall in that range (e.g. `🚀` = bytes `F0 9F 9A 80` ends in `0x80`). Handle 8-bit C1 controls (`\u{9b}` = 8-bit CSI, `\u{9d}` = 8-bit OSC) as their own `char`s inside the loop.

**Match reference semantics exactly.** A regex-based stripper only removes *complete* escape sequences; a lone `ESC` (or `ESC` followed by a byte that is NOT a sequence introducer, e.g. a C0 control or `0x80`) must be KEPT. Build parity tests against the ORIGINAL implementation before claiming success — an ad-hoc verify script caught this exact bug (lone `ESC` was being deleted).

## Verification (required — not just "it builds")
Run an ad-hoc parity + speedup script: import the ORIGINAL function and the Rust function, compare outputs on a broad case list (empty string, plain text, CSI, OSC/BEL, OSC/ST, 8-bit CSI/OSC, DCS, emoji, CJK, lone ESC, ESC+0x80, ESC+newline), assert 0 differences, then benchmark MB/s on a realistic ~2-3 MB payload. Report explicitly as **ad-hoc verification, not a green suite**. See `scripts/verify_parity.py` and `references/verification-example.md`.

## References
- `references/windows-msvc-setup.md` — exact commands + how to locate the MSVC version dir.
- `references/hermes-hotpaths.md` — hot-path candidates found by introspecting the Hermes agent source.
- `scripts/verify_parity.py` — reusable parity + benchmark harness skeleton.
- `templates/Cargo.toml`, `templates/pyproject.toml`, `templates/lib.rs` — starter scaffolding.
