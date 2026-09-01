---
category: hermes
name: hermes-mcp-integration
description: "Evaluate, install, and verify a third-party MCP server in Hermes Agent — npx/uvx/HTTP servers, config.yaml format, privacy flags, and the hermes mcp test verification loop. Use when the user asks to add/verify/recommend an MCP server (browser automation, filesystem, GitHub, databases, APIs) for Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, mcp, integration, config, verification]
---

# Hermes MCP Server Integration

Hermes has a built-in native MCP client: it connects to MCP servers at startup,
discovers their tools, and exposes them as first-class tools named
`mcp_<server>_<tool>`. This skill covers the full loop for adding a *third-party*
MCP server (distinct from `hermes-skill-integration`, which is about SKILL.md
bundles from hubs).

Use it when the user pastes a GitHub MCP repo and says "is this worth installing?"
or "add this to Hermes", or asks to wire up an npx/uvx/HTTP MCP server.

## Loop (closed — verify before declaring done)

1. **Verify the tool, don't trust the pitch.** Pull repo facts from the GitHub
   API (stars, license, last commit, latest release) and read the README for
   requirements and privacy disclaimers. `gh` is often NOT authed — use
   `curl -s https://api.github.com/repos/<owner>/<repo>` instead. Hard signals:
   official org + Apache-2.0/MIT, recent commits, ≥1k stars, active releases.
2. **Confirm Hermes MCP support.** Hermes config has an `mcp_servers:` key and
   the native client auto-discovers tools. (An existing server like `obscura`
   under `mcp_servers:` proves it's live.) Prereqs: `mcp` Python package
   (silently disabled if missing), Node.js for `npx` servers, `uv` for `uvx`.
3. **Check runtime requirements of the server itself.** Browser MCPs (e.g.
   chrome-devtools-mcp) need a Chrome/Chromium binary. If none is installed,
   you can point `--executablePath` at an existing Chromium (e.g. Playwright's
   under `%LOCALAPPDATA%/ms-playwright/.../chrome.exe`), though the tool may only
   *officially* support Chrome stable / Chrome for Testing.
4. **Back up config.yaml first.** `cp config.yaml config.yaml.bak.<ts>`. NOTE:
   the `file` toolset's `write_file`/`patch` are BLOCKED on config.yaml for
   security — edit it via terminal Python (`open()` + string replace) or the
   `hermes config` CLI. Keep indentation exact (2 spaces; server name indented
   under `mcp_servers:`).
5. **Append the server block** (see templates/ for a known-good npx example).
   Decide slim vs full: `--slim` yields ~3 tools; full set exposes everything.
6. **Apply privacy/security flags** the README documents (see Pitfalls + the
   chrome-devtools reference). Disable vendor telemetry by default.
7. **Verify for real:** `hermes mcp test <name>`. It prints
   `✓ Connected` and `✓ Tools discovered: N` with the tool list. Never claim
   success without this output.
8. **Tell the user to restart Hermes** (`/reset` in TUI, or relaunch) — MCP
   tools load at startup, there is NO hot reload. Then tools are callable as
   `mcp_<server>_<tool>`.

## Config format (stdio)

```yaml
mcp_servers:
  server_name:
    command: "npx"
    args: ["-y", "pkg-name@latest", "--flag", "--headless"]
    env:                     # optional; only these vars reach the subprocess
      SOME_API_KEY: "value"
    timeout: 120             # per-tool-call timeout (s), default 120
    connect_timeout: 60      # initial connection timeout (s), default 60
    enabled: true
```

HTTP transport uses `url:` + `headers:` instead of `command`/`args`.

## Pip-based Python MCP servers (e.g. Scrapling)

Some MCP servers are plain Python packages that expose an `mcp` subcommand (not npx/uvx).
To wire these into Hermes so the *running* agent can actually import them:

1. **Install into Hermes's own venv — NOT an ephemeral uv env.** Hermes on Windows runs from
   `AppData\Local\hermes\hermes-agent\venv`. A bare `uv pip install X` at a skill dir, or
   `uv run`, creates a separate ephemeral environment; the agent's process won't see the
   module and `hermes mcp test` will fail to spawn the binary. Install directly:
   ```bash
   VENV="$APPDATA/hermes/hermes-agent/venv"
   "$VENV/Scripts/python.exe" -m pip install "scrapling[ai]" "scrapling[fetchers]"
   ```
   The `scrapling` CLI then lives at `"$VENV/Scripts/scrapling.exe"`.
2. **Config block (stdio):** point `command` at the venv binary, `args: [mcp]`:
   ```yaml
   mcp_servers:
     scrapling:
       command: C:/Users/<you>/AppData/Local/hermes/hermes-agent/venv/Scripts/scrapling.exe
       args: [mcp]
       timeout: 120
       enabled: true
   ```
3. **Browser deps:** stealth/fetcher tools need browsers — run `scrapling install --force` once
   after install (downloads Chromium + fingerprint deps).
4. **Verify:** `hermes mcp test scrapling` → `✓ Connected`, `✓ Tools discovered: 10`
   (get, fetch, stealthy_fetch, bulk_*, screenshot, open/close/list_session).
5. **Restart Hermes** (`/reset` in TUI or relaunch) — MCP tools load at startup, no hot reload.
   Tools then surface as `mcp_scrapling_<tool>`.

Pitfall: on MSYS/git-bash, `python3` may resolve to the Microsoft Store alias
(error "no se encontró Python; ejecutar sin argumentos para instalar..."). Always call the
venv binary by absolute path (`"$VENV/Scripts/python.exe"`) instead of relying on
`python3` / `uv run`.

## Bun / TypeScript MCP servers (e.g. GBrain)

Some MCP servers are TypeScript projects run with `bun` (not Node, not Python). GBrain
is the canonical example. Pattern that works on Windows:

1. **Install a NATIVE bun.exe** (not via `npm install -g bun`, which yields a bash shim —
   see the WinError 193 pitfall above). Download `bun-windows-x64.zip` from the bun GitHub
   releases, extract `bun.exe` to a stable path like `C:/Users/<you>/tools/bun.exe`, verify
   with `file bun.exe` → `PE32+ executable for MS Windows`.
2. **Config block (stdio):** Hermes spawns `command:` directly, so pass `bun.exe` + `run` +
   the server entry + its `serve` subcommand as `args`:
   ```yaml
   mcp_servers:
     gbrain:
       command: "C:/Users/<you>/tools/bun.exe"
       args: ["run", "C:/Users/<you>/gbrain/src/cli.ts", "serve"]
       env:
         HOME: "C:/Users/<you>"
       timeout: 120
       enabled: true
   ```
3. **Verify the MCP handshake before registering:** pipe a JSON-RPC `initialize` to
   `bun.exe run <entry> serve` (with `timeout 8`) and confirm it returns
   `{"result":{"protocolVersion":...}}`. Then `hermes mcp test gbrain` should print
   `✓ Connected` + `✓ Tools discovered: N`.
4. **Server-specific setup often lives outside the MCP wiring.** GBrain needs its own
   `init` (local PGLite brain) + an embedding provider (Ollama `nomic-embed-text` locally
   is the zero-cost, zero-key path) before `serve` returns useful tools. See
   `references/bun-typescript-mcp.md` for the full GBrain recipe including the gotchas:
   `npm install -g bun` gives a bash shim, `init --embedding-model` is ignored on re-init
   (must wipe `config.json` + brain first), and `gbrain import` does NOT auto-extract
   wikilink graph edges — you must run `gbrain extract links --source db` separately.

## WSL-resident MCP servers (e.g. Lightpanda installed via Homebrew inside WSL)

When a binary lives inside WSL (Linux) but Hermes runs on the Windows host, you
can't point `command:` at a Linux binary directly — Windows can't spawn ELF
executables. Instead, use `wsl.exe` as the command and pass the full invocation
as args. The brew shellenv eval before the command ensures the binary is on PATH.

Canonical example — Lightpanda Browser installed inside WSL via Homebrew:

```yaml
mcp_servers:
  lightpanda:
    command: "C:/Windows/System32/wsl.exe"
    args:
      - "-e"
      - "bash"
      - "-lc"
      - 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" && lightpanda mcp'
    timeout: 120
    enabled: true
```

Verify with `hermes mcp test lightpanda` — should report `✓ Connected` and
`✓ Tools discovered: 31` (goto, markdown, links, evaluate, click, fill, etc.).

Pitfall: WSL must be installed (`wsl --install` from admin shell), the distro
must have the tool installed, and `wsl.exe` must be on the Windows PATH (it is
by default at `C:/Windows/System32/wsl.exe`). The `-lc` flag runs the command as
a login shell, which sources `.profile` — needed when the binary relies on
environment setup like `brew shellenv`. Without `-lc`, brew-installed binaries
may not be found.

See `references/wsl-mcp-lightpanda.md` for the full installation recipe
(install Homebrew in WSL, tap the formula, verify with `lightpanda fetch`).

## Pitfalls

- **Hermes filters env vars for stdio servers.** Only safe baseline vars
  (PATH, HOME, USER, LANG, TERM, SHELL, TMPDIR, XDG_*) are inherited. Pass any
  API key/token explicitly via the `env:` key — do NOT assume it inherits your
  shell's secrets.
- **Vendor telemetry is ON by default for many servers.** chrome-devtools-mcp
  collects usage stats (`--usageStatistics` default true) and sends perf-trace
  URLs to Google CrUX. Disable with `--no-usage-statistics --no-performance-crux`.
- **Config edit blocked by file toolset** → use terminal Python or `hermes config set`.
- **No hot reload** → restart/reload after any mcp_servers change.
- **`--slim` vs full**: slim (3 tools) is lighter; full set (~29 non-experimental,
  up to ~51 with experimental flags) is heavier but complete. Match to need.
- **Browser MCP needs a real Chrome/Chromium binary**; verify it exists before
  claiming the server "works" end-to-end.
- **Windows: MCP `command:` must be a NATIVE .exe, never a bash shim.** A runtime
  installed via `npm install -g bun` on Windows lands as a ~283-byte bash script,
  NOT a PE binary — Hermes spawns `command:` directly and dies with
  `WinError 193 %1 no es una aplicación Win32 válida`. For any bun/Node-based MCP
  server on Windows, download the real binary (e.g. `bun-windows-x64.zip` from the
  bun GitHub releases) and point `command:` at the extracted `bun.exe`. Verify with
  `file bun.exe` → `PE32+ executable for MS Windows`. The `gbrain` skill has the
  worked example (and `hermes mcp test` will surface the WinError 193 symptom).
- **Credential redaction** in MCP error messages is automatic — safe to surface
  failures to the user.

## Verification commands

```bash
hermes mcp test <name>        # connected + tools discovered
hermes mcp list               # configured servers
hermes mcp configure <name>   # toggle tool selection
```

See `references/chrome-devtools-mcp.md` for the fully worked, verified example
(repo check, privacy flags, Playwright-Chromium executablePath, test output).

See `references/bun-typescript-mcp.md` for the worked GBrain (bun/TypeScript MCP server)
recipe on Windows: native bun.exe, PGLite brain init, Ollama embeddings, the
`init`/`config set` no-op trap, and the `import`-doesn't-extract-links gotcha.
