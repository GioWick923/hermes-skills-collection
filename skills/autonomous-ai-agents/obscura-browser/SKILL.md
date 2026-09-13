---
category: autonomous-ai-agents
name: obscura-browser
description: "Use when Hermes needs fast scraping, JavaScript-rendered page extraction, browser automation, or MCP browser tools through the local Obscura Rust headless browser."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [obscura, browser, scraping, mcp, cdp, rust, automation]
    related_skills: [hermes-agent, hermes-closed-loop-engineering, hermes-browser]
---

# Obscura Browser

**Stack consolidado 2026-09-10 (benchmark real de arranque + tools/list):** obscura 0.02s/37 tools > chrome-devtools 1.2s/29 > playwright 0.6s/24 > stealth-browser 2.4s/97 > scrapling 2.2s/10 > browser-use 7.2s/6. Obscura = PRIMARIO (binario Rust, automation+extract+anti-detección), chrome-devtools = segundo (único con perf-trace/lighthouse/CDP). stealth/playwright/browser-use/scrapling DESHABILITADOS pero re-habilitables en `mcp_servers.<name>.enabled: true` (config.yaml). Re-benchmark antes de cambiar: `subprocess.Popen` + initialize JSON-RPC + tools/list. Backup config: config.yaml.bak3-20260910. for Hermes

## Overview

Obscura is the local Rust headless browser installed for Gio's Hermes setup. Use it as the preferred fast path for scraping, JavaScript-rendered extraction, link discovery, page markdown, and browser-agent automation when the built-in web extractors are insufficient or when a real browser context is useful.

Installed binary:

```text
C:/Users/<USER> GAMES/AppData/Local/hermes/tools/obscura/v0.1.10/obscura.exe
```

Worker binary for parallel scrape:

```text
C:/Users/<USER> GAMES/AppData/Local/hermes/tools/obscura/v0.1.10/obscura-worker.exe
```

Hermes MCP server name:

```text
obscura
```

MCP command configured:

```text
C:/Users/<USER> GAMES/AppData/Local/hermes/tools/obscura/v0.1.10/obscura.exe mcp
```

## When to Use

Use Obscura first for:

- Fast scraping of rendered pages.
- Extracting page markdown, links, text, HTML, cookies, or assets.
- Evaluating JavaScript such as `document.title` or DOM queries.
- Browser automation through MCP tools after a new Hermes session loads them.
- Sites where plain HTTP extraction misses client-rendered content.
- Agent workflows needing page state, forms, tabs, cookies, console, or network logs.

Prefer existing lightweight web/search tools for simple static pages, current facts, or quick search queries. Use full browser automation only when scraping/rendering/interaction matters.

## Direct CLI Commands

On this Windows host, terminal runs bash. Quote the path because the username contains spaces:

```bash
OB='C:/Users/<USER> GAMES/AppData/Local/hermes/tools/obscura/v0.1.10/obscura.exe'
"$OB" --version
"$OB" fetch https://example.com --eval 'document.title' --timeout 30 --wait 1
"$OB" fetch https://example.com --dump markdown --timeout 30 --wait 1
"$OB" fetch https://example.com --dump links --timeout 30 --wait 1
"$OB" fetch https://example.com --dump html --selector 'main' --timeout 30 --wait 1
```

Useful dump formats:

| Format | Use |
|---|---|
| `markdown` | Clean page content for summarization |
| `text` | Plain visible text |
| `links` | URL discovery |
| `html` | Rendered DOM inspection |
| `original` | Raw HTTP body, bypassing engine |
| `assets` | External resources / XHR assets |
| `cookies` | Cookie jar inspection |

For multi-statement JavaScript snippets starting with `const`, wrap in an IIFE:

```bash
"$OB" fetch https://example.com --eval '(function(){ const h=document.querySelector("h1"); return h && h.textContent; })()'
```

## MCP Usage in Hermes

After restarting Hermes or running `/reload-mcp`, Obscura MCP tools appear with the prefix:

```text
mcp_obscura_*
```

Expected important tools:

- `mcp_obscura_browser_navigate`
- `mcp_obscura_browser_snapshot`
- `mcp_obscura_browser_markdown`
- `mcp_obscura_browser_links`
- `mcp_obscura_browser_extract`
- `mcp_obscura_browser_click`
- `mcp_obscura_browser_fill`
- `mcp_obscura_browser_evaluate`
- `mcp_obscura_browser_network_requests`
- `mcp_obscura_browser_console_messages`

Typical MCP browser loop:

```text
1. Navigate to URL.
2. Snapshot or markdown the page.
3. Extract links/data or interact.
4. Verify output against visible page/source.
5. Close/reset tab when done.
```

## Verification Commands

Use these after installation or upgrade:

```bash
OB='C:/Users/<USER> GAMES/AppData/Local/hermes/tools/obscura/v0.1.10/obscura.exe'
"$OB" --version
"$OB" fetch https://example.com --eval 'document.title' --timeout 30 --wait 1
hermes mcp list
hermes mcp test obscura
```

Expected smoke result:

```text
obscura 0.1.10
Example Domain
MCP test: Connected; tools discovered: 35
```

## Safety Rules

- Keep MCP on stdio by default. Do not expose Obscura HTTP MCP unless explicitly requested.
- If HTTP MCP is ever used, bind to `127.0.0.1`; if exposed beyond loopback, require `OBSCURA_MCP_ALLOWED_ORIGINS` plus network auth.
- Do not use `--allow-private-network` unless the user explicitly wants local/RFC1918 access.
- Use `--stealth` only for legitimate automation where anti-fingerprinting is appropriate.
- Respect robots.txt, site terms, rate limits, and user intent.
- Prefer bounded scraping: set `--timeout`, constrain selectors, and avoid uncontrolled crawling.

## Troubleshooting

- Tools do not appear in the current chat: run `/reload-mcp` or start a new Hermes session; MCP discovery happens at startup/reload.
- `obscura-worker.exe` must stay next to `obscura.exe` for parallel `scrape`.
- If a page hangs, lower `--timeout`, use `--wait-until domcontentloaded`, or extract a narrower selector.
- For local URLs, remember private-network access is blocked unless `--allow-private-network` is set.
