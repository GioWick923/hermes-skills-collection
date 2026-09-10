---
category: hermes
name: mcp-verification
description: "Use when verifying MCP: prove auth, probe via JSON-RPC."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# MCP Verification (connectivity ≠ authentication)

When you wire an MCP server into Hermes (`config.yaml` `mcp_servers:`), the default
check `hermes mcp test <name>` is **necessary but NOT sufficient**. It only confirms:
1. the transport connects, and
2. the tool list is discoverable.

It does **NOT** validate that your API key / token actually authenticates. A revoked,
expired, or mistyped key still prints `✓ Connected` + `✓ Tools discovered: N`, then
every real tool call fails with *"API key was revoked or invalid"*.

## The closed verification loop

1. `hermes mcp test <name>` → expect `✓ Connected` + `✓ Tools discovered: N`.
2. **Prove auth with a live call** — invoke a `whoami` / `authenticate` / `login` /
   status tool. If it returns user data (not an auth error), auth is real.
3. If the `mcp_<server>_*` tools are NOT in your session schema (e.g. the server was
   just added and Hermes hasn't restarted, or you're mid-session), you CANNOT call them
   directly. Use the **direct JSON-RPC probe** below instead — it hits the endpoint with
   plain Python and bypasses the schema limitation.
4. Only declare the server "working" after step 2/3 returns real data, not just the handshake.

## Direct JSON-RPC probe (scripts/probe.py)

Use the standalone probe when the native `mcp_*` tools aren't callable in the current
session, or for a quick auth check without restarting Hermes. Key details learned the
hard way:

- **Set a browser `User-Agent` header.** Cloudflare-fronted MCP endpoints (e.g.
  `mcp.trader.dev`) return **HTTP 403 Forbidden** to Python's default `urllib`
  User-Agent. A real browser UA fixes it. (`curl` worked without it; `urllib` did not.)
- **Parse SSE framing.** HTTP MCP responses are `text/event-stream`: lines
  `event: message` followed by `data: {json}`. Read the body, split lines, and
  `json.loads` the `data:` payload.
- **Capture `mcp-session-id`** from the response header on `initialize` and echo it in
  subsequent requests (some servers require it).
- **Sequence:** `initialize` → `notifications/initialized` → `tools/call`.
- For HTTP transport the key goes in the `Authorization: Bearer <key>` header
  (NOT the URL query string — that leaks in logs/history).

See `scripts/probe.py` for a copy-paste template that runs `initialize`, `whoami`,
and a sample `tools/call` against an HTTP MCP server.

## Wrapper-MCP pattern (catalog behind a few dispatcher tools)

Some hosted MCPs (AgentKey, `https://api.agentkey.app/v1/mcp`) expose only 3-4
"dispatcher" tools that route to a large catalog (~2000 ops). Verified 2026-09-01:
AgentKey exposes `find_tools` / `describe_tool` / `execute_tool` / `list_tools`.

- `find_tools` returns ranked `Provider/Operation` names + per-call cost
- `describe_tool` (on that name) → the param schema
- `execute_tool` with `{"name": "<Provider/Op>", "params": {...}}` → live data
- Example that worked: `execute_tool(name="Serper/searchNews", params={"q":"Nvidia news"})`
  → real Google News results.

**PITFALL — canonical name ≠ direct `tools/call` name.** The name `find_tools`
returns (`Serper/searchNews`) is NOT a top-level MCP tool. Calling it directly via
raw `tools/call` → `unknown tool "Serper/searchNews"`. You must route through the
wrapper `execute_tool`, passing the canonical name inside its `arguments`. Don't
treat `find_tools` output as directly callable MCP tool names. Also note
`describe_tool` does NOT resolve dispatcher wrappers themselves (asking it for
`execute_tool` returns "tool not found: execute_tool") — it only resolves catalog ops.

## Pitfalls

- **`hermes mcp test` lies about auth.** Treat its success as "reachable", not "usable".
- **Key in URL `?key=` is a leak.** Put it in `headers.Authorization` in config.yaml.
- **Cloudflare 403 on probe?** Add the browser User-Agent (see above). Don't assume the
  server is down — `curl` may succeed where `urllib` fails.
- **Restart Hermes (`/reset`) after any config change** — MCP tools load at startup, no
  hot reload. Your in-session `mcp_*` tools reflect the OLD config until restart.
- **API keys in `config.yaml` are plaintext** (like other MCP servers). Redaction only
  applies to tool-output logs, not the on-disk file. Be careful sharing the machine/commits.
- **Don't claim a tool "works" from a GET-in-browser 502.** Browsers issue GET; MCP uses
  POST JSON-RPC. A browser 502 says nothing about MCP health — probe with POST.
