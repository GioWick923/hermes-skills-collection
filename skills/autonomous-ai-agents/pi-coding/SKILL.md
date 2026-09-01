---
name: pi-coding
description: "Use to delegate coding tasks to the Pi Agent CLI."
---

# Pi Coding Delegation (Hermes → Pi Agent)

Delegate coding work to **Pi** (earendil-works/pi), an open-source terminal
coding agent, driven through the **same inferx provider** Hermes uses — no
Anthropic/OpenAI key required. This is a third delegation option alongside
`claude-code` and `codex` for parallel or independent coding workstreams.

## When to use
- User asks for autonomous implementation of a coding task (feature, refactor, fix).
- You want a second, isolated implementation pass or a parallel workstream.
- A task benefits from a fresh agent context / independent verification.

## Setup (already done — verify only if broken)
- Pi installed globally at `C:/Users/<USER> GAMES/AppData/Local/hermes/node/`
  (CLI: `node_modules/@earendil-works/pi-coding-agent/dist/cli.js`, v0.83.x).
- Provider extension: `~/.pi/agent/extensions/inferx-provider.ts` registers
  inferx as an OpenAI-completions provider pointing at
  `https://model.inferx.net/endpoints/v1` with model `deepseek-v4-flash-0731`.
- Wrapper: `~/AppData/Local/hermes/scripts/pi-run.sh` — the ONLY path to invoke
  Pi. Handles the extension flag, provider selection, INFERX_API_KEY check, and
  a 300s timeout guard. Never call the raw CLI directly.

## Invocation (fluent, from Hermes)

One-shot task (clean text response on stdout):
```bash
bash "C:/Users/<USER> GAMES/AppData/Local/hermes/scripts/pi-run.sh" \
  "Your prompt here" [--cwd "/path/to/project"]
```

Examples:
- `bash pi-run.sh "Read src/main.py and fix the bug in the sort function"`
- `bash pi-run.sh "Write a pytest test suite for this module" --cwd "C:/Users/<USER> GAMES/projects/foo"`
- JSON mode (structured): pass `--print-json` to emit the full pi JSONL event
  stream instead of clean text.

Note: the shell is git-bash/MSYS. Pi works best on tasks rooted in an existing
directory — always pass `--cwd` for real repo work. Pi has `read`, `write`,
`edit`, `bash` tools and uses the model's tool-loop itself.

## Pitfalls
- **INFERX_API_KEY must be in env** — the wrapper exits 2 if missing. It is set
  in the Hermes environment, so this just works from agent tool calls.
- **Never call the CLI directly**; the wrapper handles the `-e <extension>`
  flag and the correct Windows path (the raw CLI arg needs a native
  `C:\...` path, and the bare `pi` shim can hang in git-bash).
- **Timeout guard (300s).** If a Pi task exceeds it, the wrapper kills it — pick
  `--print-json` or split the task for long-running work.
- Pi is a coding harness, not a general chat assistant — point it at concrete
  file/implementation tasks, not open-ended questions.
- Model is the same as Hermes' default (deepseek-v4-flash-0731) via inferx; to
  use a different inferx model, edit the `--model` arg in the wrapper.

## Verify it works
```bash
bash "C:/Users/<USER> GAMES/AppData/Local/hermes/scripts/pi-run.sh" \
  "Responde en una sola palabra: capital de Francia?"
# → "París"
```
