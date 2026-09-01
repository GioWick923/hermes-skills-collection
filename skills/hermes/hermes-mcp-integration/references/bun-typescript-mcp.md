# Bun / TypeScript MCP servers — worked GBrain recipe (Windows)

Verified end-to-end on Windows 10 / Hermes desktop TUI. GBrain is a TypeScript MCP server
that needs `bun` (NOT Node, NOT Python) and its own local datastore before `serve` is useful.

## 0. Hermes side: the MCP block

Hermes spawns `command:` directly (no shell), so it MUST be a native `.exe`. The
`npm install -g bun` path on Windows produces a ~283-byte **bash shim**, which fails with
`WinError 193 %1 no es una aplicación Win32 válida`. Download the real binary instead:

```bash
curl -sL -o bun.zip "https://github.com/oven-sh/bun/releases/download/bun-v1.3.14/bun-windows-x64.zip"
unzip -o bun.zip -d bun-dist
mkdir -p C:/Users/<you>/tools
cp bun-dist/bun-windows-x64/bun.exe C:/Users/<you>/tools/bun.exe
file C:/Users/<you>/tools/bun.exe   # -> PE32+ executable for MS Windows
```

`config.yaml` block (edit via terminal Python — file toolset blocks config.yaml):

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

## 1. Install GBrain + PGLite brain

```bash
git clone --depth 1 https://github.com/garrytan/gbrain.git C:/Users/<you>/gbrain
cd C:/Users/<you>/gbrain
bun install --frozen-lockfile   # postinstall script may error on Windows shell quirks; harmless, deps still install
bun run src/cli.ts --version    # -> gbrain 0.42.x.x
```

## 2. Embedding provider (zero-cost path: Ollama local)

No API key needed. Install Ollama for Windows (`OllamaSetup.exe /S`), then:

```bash
# Ollama CLI lives at C:/Users/<you>/AppData/Local/Programs/Ollama/ollama.exe
ollama serve &            # background; listens on http://localhost:11434
ollama pull nomic-embed-text   # 768-dim embeddings, ~85MB
curl -s http://localhost:11434/api/embeddings -d '{"model":"nomic-embed-text","prompt":"hi"}'  # -> {"embedding":[...]}
```

## 3. Init the brain — TRAP: `init --embedding-model` is ignored on re-init

`embedding_model` is a "file-plane" field applied only at `init`. `gbrain config set
embedding_model X` is a hard-refused no-op (printed explicitly). And `init --embedding-model`
reuses an existing `config.json` value on re-init, silently ignoring the flag. Fix: wipe first.

```bash
rm -f ~/.gbrain/config.json
rm -rf ~/.gbrain/brain.pglite
bun run src/cli.ts init --pglite --embedding-model ollama:nomic-embed-text
bun run src/cli.ts config get embedding_model   # -> ollama:nomic-embed-text (confirm!)
bun run src/cli.ts doctor                        # all checks OK
```

## 4. Seed + import + TRAP: `import` does NOT extract graph links

```bash
bun run src/cli.ts import /path/to/notes          # creates chunks (embedded via Ollama)
bun run src/cli.ts stats                           # Links: 0  <-- wikilinks NOT auto-linked
bun run src/cli.ts extract links --source db      # populates the typed-edge graph
bun run src/cli.ts graph concepts/gbrain --depth 2   # verify edges exist
bun run src/cli.ts search "..."                   # hybrid search works once embedded
```

`think` (LLM synthesis w/ citations) additionally needs `ANTHROPIC_API_KEY` or
`OPENROUTER_API_KEY` — retrieval works without it.

## 5. Verify the MCP wiring

Handshake probe (should echo a JSON-RPC `initialize` result):
```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}\n' \
  | timeout 8 C:/Users/<you>/tools/bun.exe run C:/Users/<you>/gbrain/src/cli.ts serve
```
Then from the Hermes dir:
```bash
hermes mcp test gbrain   # -> ✓ Connected, ✓ Tools discovered: 102
```
Restart Hermes (`/reset`) — MCP tools load at startup, no hot reload. Tools surface as
`mcp_gbrain_<tool>`.
