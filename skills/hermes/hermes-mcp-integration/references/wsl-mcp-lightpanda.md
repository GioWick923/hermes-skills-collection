# Lightpanda MCP via WSL — Full Installation Recipe

## What is it?
[Lightpanda](https://github.com/lightpanda-io/browser) is a headless browser
built from scratch in Zig (not a Chromium fork). 9× faster and 16× less RAM than
Chrome headless (123MB vs 2GB for 100 pages). It has a native MCP server mode
(`lightpanda mcp`) that exposes 31 tools via JSON-RPC over stdio.

## Prerequisites
- Windows with WSL2 + a distro (Ubuntu is fine)
- `wsl.exe` on Windows PATH (default at `C:/Windows/System32/wsl.exe`)

## Installation inside WSL

```bash
# 1. Install Homebrew (Linuxbrew) inside WSL
wsl -e bash -lc 'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'

# 2. Tap the Lightpanda formula
wsl -e bash -lc 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" && brew tap lightpanda-io/browser'

# 3. Install the nightly binary
wsl -e bash -lc 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" && brew install lightpanda-io/browser/lightpanda'

# 4. Verify
wsl -e bash -lc 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" && lightpanda version'
# → 1.0.0-nightly.8464+70bbdadf
```

## Hermes config.yaml block

See the SKILL.md "WSL-resident MCP servers" section for the config block.

## Verification

```bash
# Quick smoke test (fetch a page)
wsl -e bash -lc 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" && lightpanda fetch https://example.com --dump markdown --json'

# MCP handshake test (manual)
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}' | wsl -e bash -lc 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" && lightpanda mcp'

# Hermes MCP test (after config.yaml update)
hermes mcp test lightpanda
# → ✓ Connected, ✓ Tools discovered: 31
```

## Tools at a glance (31 total)

| Tool | Purpose |
|------|---------|
| `goto` | Navigate to URL |
| `search` | Web search, returns markdown |
| `markdown` | Page as GFM markdown |
| `html` | Raw HTML |
| `links` | Extract all links as JSON |
| `evaluate` | Execute JS in page context |
| `extract` | Structured data extraction |
| `tree` | Semantic DOM tree (LLM-optimized) |
| `nodeDetails` | Details for a DOM node |
| `interactiveElements` | Clickable/typeable elements |
| `structuredData` | JSON-LD, OpenGraph metadata |
| `detectForms` | Form structure detection |
| `click` / `fill` / `scroll` / `hover` / `press` | Interaction |
| `waitForSelector` / `waitForScript` / `waitForState` | Wait conditions |
| `selectOption` / `setChecked` / `findElement` | Form helpers |
| `consoleLogs` / `getUrl` / `getCookies` / `getEnv` | Inspection |
| `save` | Save session as reusable script |
| `session_new` / `session_list` / `session_close` | Session mgmt |

## Pitfalls

1. **Must use `-lc` (login shell)** in the wsl args — otherwise brew-installed
   binaries won't be on PATH because `.profile` isn't sourced. The `-lc` flag
   runs bash as a login shell.
2. **Homebrew is needed** — Lightpanda doesn't provide standalone Linux binaries
   on GitHub releases, only via Homebrew tap (which downloads nightly prebuilts).
3. **WSL must be running** — first invocation may take a few seconds to boot the
   distro. Subsequent calls are fast.
4. **Timeout**: set `timeout: 120` or more in config.yaml — page loads can be
   slow on first navigation.
5. **Hermes on Windows native, not WSL** — if Hermes itself runs inside WSL,
   the `wsl.exe` trampoline is unnecessary; use `command: lightpanda` directly.