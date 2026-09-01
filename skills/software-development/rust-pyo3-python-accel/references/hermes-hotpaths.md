# Hot-path candidates found by introspecting the Hermes agent

Source tree: `C:\Users\<USER> GAMES\AppData\Local\hermes\hermes-agent\`
(the agent is 100% Python; the repo also ships a Rust Tauri installer, but
the agent core uses no PyO3/maturin yet).

## Top candidates (CPU-bound, high frequency)
| Module | Lines | Why | Frequency |
|--------|-------|-----|-----------|
| `tools/ansi_strip.py` | 44 | regex ANSI strip over ALL terminal output | every shell command |
| `tools/fuzzy_match.py` | 865 | 9-strategy match, difflib, regex, loops over whole file | every file edit (`patch`) |
| `trajectory_compressor.py` | 1574 | `tokenizer.encode()` in a loop (HF tokenizers is already Rust/C++, so the Python loop is the cost) | each trajectory compaction |
| `agent/context_compressor.py` | 2683 | re.compile, json.loads, token estimates in loops | each context compaction |

## Skip (correctly)
- `tools/session_search_tool.py` (880) — SQLite FTS5 queries: I/O-bound.
- `agent/prompt_builder.py` (1908) — string concat before LLM send; real cost is the send.
- Context compressors: most time is waiting on the aux LLM (I/O), not compute.

## Proven result
Porting `ansi_strip` to Rust/PyO3 gave **parity 100% (20/20 cases)** and
**3.3x faster** on a ~2.8 MB realistic terminal payload (73 MB/s vs 22 MB/s),
and the no-escape fast path was **5x cheaper** than Python's. The port lives
in `C:\ansi_rust_demo\` (external, Hermes source untouched).
