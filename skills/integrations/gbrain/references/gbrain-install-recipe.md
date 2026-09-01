# Verified GBrain → Hermes install recipe (Windows)

All commands below were executed successfully in session 2026-07-12. Paths use
`C:/Users/<USER> GAMES` — substitute your home.

## 1. Clone + install deps
```bash
cd /c/Users/<USER>\ GAMES
git clone --depth 1 https://github.com/garrytan/gbrain.git
cd gbrain
bun install            # postinstall may error on Windows shell quirk; ignore
bun run src/cli.ts --version   # → gbrain 0.42.58.0
```
Note: `bun` here = native bun.exe (see references/windows-native-bun.md).

## 2. Ollama (local embeddings, no key)
```bash
curl -sL -o OllamaSetup.exe https://ollama.com/download/OllamaSetup.exe
./OllamaSetup.exe /S
OLLAMA="/c/Users/<USER> GAMES/AppData/Local/Programs/Ollama/ollama.exe"
"$OLLAMA" serve &          # background; listens :11434
"$OLLAMA" pull nomic-embed-text
# verify:
curl -s http://localhost:11434/api/embeddings -d '{"model":"nomic-embed-text","prompt":"hi"}'
# → {"embedding":[...]}
```

## 3. Init brain (PGLite, no server)
```bash
# WIPE any prior brain/config first (embedding_model is init-only):
rm -f ~/.gbrain/config.json
rm -rf ~/.gbrain/brain.pglite
bun run src/cli.ts init --pglite --embedding-model ollama:nomic-embed-text
# → "Brain ready", "Embedding: ollama:nomic-embed-text (768d)"
bun run src/cli.ts config get embedding_model   # → ollama:nomic-embed-text
```

## 4. Health + smoke import
```bash
bun run src/cli.ts doctor          # → all checks OK
mkdir -p /tmp/test-brain
printf '# T\n\nHermes + GBrain.\n' > /tmp/test-brain/a.md
bun run src/cli.ts import /tmp/test-brain   # → "2 chunks created"
bun run src/cli.ts search "hermes"          # → ranked hits
```

## 5. Register in Hermes (config.yaml via Python — file toolset blocked)
```yaml
mcp_servers:
  gbrain:
    command: "C:/Users/<USER> GAMES/tools/bun.exe"
    args: ["run", "C:/Users/<USER> GAMES/gbrain/src/cli.ts", "serve"]
    env: { HOME: "C:/Users/<USER> GAMES" }
    timeout: 120
    enabled: true
```

## 6. Verify
```bash
hermes mcp test gbrain
# → ✓ Connected (1750ms)
# → ✓ Tools discovered: 102
```
Then `/reset` Hermes (MCP loads at startup, no hot reload). Tools surface as
`mcp_gbrain_<tool>`.

## Enable LLM synthesis layer (`think`)
Set `ANTHROPIC_API_KEY` or `OPENROUTER_API_KEY` (env reachable by the serve
process). Raw `search`/`query` work without it; `think` needs a chat model.
