---
name: memory-stack-ops
description: "Audit the Hermes memory stack (Obsidian + gbrain + bridge)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [memory, gbrain, obsidian, audit, mcp, second-brain]
    related_skills: [gbrain, hermes-mcp-integration, hermes-obsidian-ops, hermes-health-check]
---

# Memory Stack Operations (Hermes ↔ Obsidian ↔ gbrain)

Operational playbook for auditing and repairing the 3-layer memory stack:
Obsidian vault (canonical) → `hermes_obsidian_bridge.py` → gbrain (semantic index / graph).
Use when the user asks to audit gbrain, check why the brain has few pages, fix
memory sync, or diagnose why notes aren't reaching the semantic index.

## When to Use
- User asks to **audit gbrain** or "what needs fixing" in the memory stack.
- Brain has few pages while the vault has many, or notes "aren't reaching gbrain".
- Memory sync looks broken: `sync-gbrain` runs but the brain never grows.
- Any `Not Found` on gbrain embedding, or a CLI `doctor`/`import` lock error.

## Architecture (who writes what)
- **Obsidian vault** = canonical visible layer. `hermes_obsidian_bridge.py remember`
  writes notes here.
- **gbrain** = semantic index + knowledge graph over a PGLite DB. Writes reach it
  ONLY via MCP `put_page`/`capture` (agent calls the tools), NOT by the bridge
  scanning a folder.
- **The bridge's `sync-gbrain` is REAL since 2026-09-10** — it runs `gbrain sync
  --source obsidian-vault` through the live serve (IPC-delegated) and extracts the
  trailing JSON payload. The old stub description above is obsolete. Verify with
  `get_stats` page_count; do not trust a bare exit code alone.

## Audit sequence (diagnosis-first)
1. **Config:** `cat "$HOME/.gbrain/config.json"` → check engine=pglite,
   database_path, embedding_model. Confirm local, not cloud.
2. **Brain state:** `hermes mcp list | grep gbrain` (server enabled) + call MCP
   `get_stats` (page_count, chunk_count, embedded_count) + `get_health` (embed
   coverage, stale, orphans, brain_score).
3. **The doctor trap:** run the CLI `doctor` will FAIL with a PGLite lock message
   while `serve` is running (see pitfalls). Use MCP `run_doctor` for a real
   health score; the MCP doctor reports the authoritative status.
4. **Compare:** brain `page_count` vs vault note count (`find <vault> -name '*.md'`
   minus `.obsidian`). A big gap = sync problem, not corruption.

## The #1 silent killer: env-inherited provider URL
gbrain's MCP server inherits Hermes' `.env`. If `.env` has
`OLLAMA_BASE_URL=https://ollama.com/v1` (cloud) — often set for Hermes' own model
routing — the gbrain server inherits it and every embed hits the cloud endpoint,
failing with `[embed(ollama:nomic-embed-text)] Not Found` even though local Ollama
is healthy. Result: put_page/capture fail silently and the brain stays tiny.

**Fix:** force the local URL in the MCP `env:` block (config.yaml, edit via
terminal Python — file toolset is blocked):
```yaml
mcp_servers:
  gbrain:
    command: "${USERPROFILE}/tools/bun.exe"
    args: ["run", "${USERPROFILE}/mcp-servers/gbrain-server/src/cli.ts", "serve"]
    env:
      HOME: "${USERPROFILE}"
      OLLAMA_BASE_URL: "http://localhost:11434/v1"
    timeout: 120
    enabled: true
```
Verify the embed provider resolves (needs local env set):
`OLLAMA_BASE_URL=http://localhost:11434/v1 bun run src/cli.ts providers test --model ollama:nomic-embed-text`
→ expect `✓ <N>ms, 768 dims`. Then `/reset` Hermes so the serve reloads the env.
Diagnose the culprit first with `grep OLLAMA_BASE_URL "$LOCALAPPDATA/hermes/.env"`.

## Pitfalls (verified 2026-09-01)
- **PGLite is single-writer.** While `gbrain serve` runs, a separate CLI
  `doctor`/`import`/`capture` errors: "local database is already open through
  `gbrain serve` (MCP, PID …)". This is NORMAL, not corruption. Read health via
  MCP tools, not CLI. Writes go through MCP put_page/capture only. The CLI
  `doctor` under the lock is a false-negative (reports FAIL on connection).
- **Migraciones "pending" in `get_health` are usually the historical ledger**, not
  a real problem — confirm with MCP `run_doctor` (schema_version = latest) before
  acting on them.
- **Do not kill the gbrain serve mid-session** — it feeds the MCP tools you're
  using. Applying an env fix in config.yaml is not enough until Hermes reloads
  the MCP (`/reset`). Verify the embed provider fix with the CLI `providers test`
  BEFORE `/reset` so you know it will work.
- **The bridge never ingests into gbrain** — don't rely on `sync-gbrain`; only
  agent MCP writes (put_page/capture) grow the brain. If you want the whole vault
  indexed, an agent must call put_page per note (or fix the bridge stub).
- **sources.default debe apuntar a obsidian-vault explícitamente** (fix 2026-09-01):
  `gbrain sources list` mostró `default` vacío y `obsidian-vault` con 75 páginas.
  El fix: `gbrain config set sources.default obsidian-vault`. Sin esto, las
  búsquedas fallan aunque el servidor esté corriendo.
- **gbrain CLI recall funciona, pero la bridge no lo usa** (2026-09-01): El bridge
  solo llama a `gbrain sync`, no a `gbrain recall`. Las búsquedas semánticas deben
  hacerse directamente con la CLI: `bun run src/cli.ts recall --query <texto>`.
- **Upgrade requerido** (2026-09-01): v0.47.9.0 → v0.48.1.0. Correr
  `bun run src/cli.ts self-upgrade` y luego `bun install` en el servidor.

## See also
- `gbrain` (user-owned): full install/wiring recipe.
- `hermes-mcp-integration` (user-owned): generic MCP server config + env pitfalls.
- `hermes-obsidian-ops`: safe Obsidian capture layer.
- `references/gbrain-troubleshooting-2026-09-01.md`: Caso práctico completo de auditoría y fix de gbrain (diagnóstico, solución, verificación).
