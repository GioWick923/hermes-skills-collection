---
category: autonomous-ai-agents
name: cline
description: "Delegate coding to Cline CLI (acts/plans, ACP editor mode)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Cline, Autonomous, Refactoring]
    related_skills: [opencode, codex, claude-code, hermes-agent]
---

# Cline CLI

Use [Cline](https://cline.bot) as an autonomous coding worker orchestrated by
Hermes terminal/process tools. Cline CLI is an AI coding assistant with an act
mode (auto-approve on), plan mode, TUI, and ACP editor integration.

## When to Use

- User explicitly asks to use Cline
- You want an external coding agent to implement/refactor/review code
- You need long-running sessions with session resume (`--id`)
- Parallel execution in isolated workdirs

## Installation / Binary Location (this host)

Cline CLI is **already installed** in the Hermes node dir (not global PATH):

```
C:\Users\<USER>\AppData\Local\hermes\node\cline.cmd      (Windows .cmd shim)
$LOCALAPPDATA/hermes/node/cline.cmd
```

Version: `3.0.55` (verified 2026-08-31). It is NOT on `which cline` PATH — call it
by absolute path or add the node dir to PATH when shelling out.

## Prerequisites

- Cline CLI installed (see above — already present on this host)
- Auth / provider configured: `cline auth [provider]`, or pass `-P` + `-k` overrides
- Git repo for code tasks (recommended)

## Common Flags

| Flag | Use |
|------|-----|
| `prompt` (positional) | Default starts in **act mode with auto-approve enabled** |
| `-p, --plan` | Plan mode (no execution) |
| `--auto-approve <bool>` | Tool auto-approval for all tools (default true) |
| `-c, --cwd <path>` | Working directory |
| `--thinking <level>` | Reasoning effort: none\|low\|medium\|high\|xhigh |
| `-i, --tui` | Interactive TUI |
| `--id <session-id>` | Resume an existing session |
| `-P, --provider <id>` | Provider id (default: cline) |
| `-k, --key <api-key>` | API key override for this run |
| `-m, --model <model-id>` | Model for the selected provider |
| `-s, --system <prompt>` | Override system prompt |
| `-z, --zen` | Background hub session |
| `--acp` | Agent Client Protocol (editor integration) |
| `--config <path>` | Config dir (default ~/.cline) |
| `--data-dir <path>` | Isolated local state (default ~/.cline/data) |
| `--retries <n>` | Max consecutive mistakes before exit (default 6) |
| `-t, --timeout <sec>` | Timeout (0 = none) |

## Pointing Cline at Our Gates (glm-5.3 etc.)

Cline default provider is `cline` (its own paid sub). To use our gateways
(aihubmix / bai / openrouter — all OpenAI-compatible), pass provider + model +
key overrides:

```bash
C="$LOCALAPPDATA/hermes/node/cline.cmd"
"$C" "your prompt" -P <provider> -m glm-5.3 -k <gate-api-key> --auto-approve true
```

glm-5.3 is available across our gates (see `references/glm-53-gateways.md`).
Default provider needs a key; verify with a real prompt before relying on it.

## One-Shot Task

```bash
"$C" "Add retry logic to API calls and update tests" -c ~/project --auto-approve true
```

## Interactive / Background (TUI)

```bash
"$C" -i -c ~/project           # foreground interactive
# or in Hermes: terminal(..., background=true, pty=true)
```

Drive with process submit/poll/log; exit with Ctrl+C (`\x03`) or kill.

## Procedure

1. Resolve the binary: `"$LOCALAPPDATA/hermes/node/cline.cmd" --version`
2. Confirm provider/model: `cline auth [provider]` or pass `-P/-m/-k`.
3. One-shot → positional prompt; iterative → `-i` TUI or `-z` background.
4. Monitor via process(poll/log); report files changed / tests / risks.

## Pitfalls

- Cline CLI is NOT on the global PATH on this host — use the absolute path.
- Default provider is `cline` (paid). For free gateway use, override `-P`/`-k`.
- **`openai-native` uses the OpenAI *Responses* API by default** — our gates
  (aihubmix, bai, openrouter) expose *Chat Completions* endpoints, so a run fails
  with `Received a Chat Completions stream while using the OpenAI Responses API`.
  `auth -p openai-native -k KEY -m MODEL -b <gate-baseurl>` *succeeds* at config
  time (exit 0, "Provider configured") but the first real run then errors on the
  protocol mismatch. When targeting a Chat-Completions-compatible gate, use a
  Chat-Completions provider/transport, not `openai-native`'s default Responses path.
- **`*-free` gateway models are quota-capped** — e.g. aihubmix `coding-glm-5.3-free`
  responds "accounts that have not been recharged can only try 10 times". Verify a
  model has real quota before relying on it; prefer the paid `glm-5.3` on a
  credit-loaded gate.
- Verify with a real smoke prompt before claiming Cline + a provider works.
- Match provider/model/region — a working combo on one gateway may 401 on another.

## Verification

Smoke test:

```bash
"$LOCALAPPDATA/hermes/node/cline.cmd" "Respond with exactly: CLINE_SMOKE_OK" --auto-approve true
```

Success: output includes `CLINE_SMOKE_OK`, exits 0, no provider/model errors.

## Rules

1. Prefer one-shot positional prompt for bounded tasks.
2. Use `-P`/`-k` overrides to point at our gates instead of the paid default.
3. Scope sessions to a single repo/workdir.
4. Report concrete outcomes (files changed, tests, remaining risks).
5. Never claim a provider works until a real prompt returned output.
