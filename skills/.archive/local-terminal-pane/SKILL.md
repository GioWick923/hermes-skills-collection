---
category: desktop
name: local-terminal-pane
description: Read the user's local terminal pane when Docker is down.
version: 1.0.0
metadata:
  hermes:
    tags: [desktop, terminal, host, docker, windows, read_terminal]
    category: desktop
    related_skills: [computer-use]
---

# Local Terminal Pane (host shell access)

## The two execution surfaces (critical distinction)
Hermes exposes TWO distinct terminal surfaces. Confusing them causes wrong
"I can't access your machine" claims and reverted-to-forbidden-channel errors.

1. **Docker-backed sandbox** — powers the `terminal` and `execute_code` tools.
   Runs Linux in a container. Shared kernel means `/proc/cpuinfo` once showed the
   host CPU as a side-effect, but this is NOT a host-inspection channel and the
   user may forbid it (see Architecture rule below). Fails hard when the Docker
   daemon is down: `EnvironmentConnectionError: Docker command is available but 'docker version' failed`.
2. **Embedded GUI terminal pane** — the panel you open with
   `focus_pane(pane='terminal')` / read with `read_terminal`. This is the
   **USER'S LOCAL shell** (Windows PowerShell on Windows). It is NOT Docker.
   It stays alive when the Docker daemon is down. You can READ it; you do not
   type into it unless `computer_use` is installed.

## Workflow: user asks about host / "read the terminal" / "run it yourself"
1. If they say "read the terminal" or "look at my terminal" → call `read_terminal`
   immediately. The pane may already show their local PowerShell output. Capture
   the text. NOTE: `read_terminal` (no args) returns only the visible viewport and
   can TRUNCATE long lines (e.g. `Intel(R) Xeon(R) CPU E...`). If truncated, ask
   the user to widen the pane, re-run with output to a file you can `read_file`, or
   paste the full line.
2. If they ask you to RUN something on their machine:
   - You cannot type into their local terminal unless `computer_use` is installed
     (`hermes computer-use install`) — check availability via `tool_search('computer_use')`.
   - You CANNOT run Windows-only cmdlets (e.g. `Get-CimInstance`) through the
     Linux Docker backend — they don't exist there.
   - So: (a) the user runs it and you read the result via `read_terminal`, or
     (b) you provide a one-liner for them to paste, or (c) if `computer_use` is
     available, drive their desktop to run it.
3. Do NOT revert to a forbidden channel (e.g. Docker) after the user told you not
   to use it. Respect the architecture split below.

## Architecture rule (this user, stated 2026-08-20)
- **Docker / sandbox** = EXECUTE PROGRAMS only (scripts, tests, builds, isolated code).
- **Hermes + gbrain** = CONVERSATION and PERSISTENT MEMORY, independent of Docker.
- Do NOT use Docker to inspect host hardware. For host specs (CPU/RAM/GPU), get
  them from the user or a host-side script that pushes to gbrain; read them from
  memory, not the host.
- Persisted in gbrain as fact #233.

## Pitfalls (all hit in one session — encode to avoid repeat)
- ❌ Declaring "I can't see your screen / terminal" BEFORE calling `read_terminal`.
  The embedded pane IS their local shell — check it first.
- ❌ Giving up after the Docker backend fails and saying "I cannot execute anything."
  Search alternatives: local `read_terminal`, `computer_use`, or ask the user to paste.
- ❌ Re-running a forbidden channel (Docker) after the user explicitly said not to.
- ❌ Assuming `read_terminal` shows full output — it returns the visible viewport;
  long lines truncate. Verify completeness before reporting.
- ❌ Trying to run Windows PowerShell cmdlets through the Linux Docker backend.

## Verification
- After `read_terminal`, confirm captured text matches the user's described output
  (e.g. CPU model). If truncated, ask to widen the pane or re-run writing to a file
  you can `read_file`.
- Before declaring "I cannot run this," confirm you checked: (1) `read_terminal` of
  the local pane, (2) `computer_use` availability, (3) whether the user can paste output.
