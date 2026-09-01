# Windows: native `bun.exe` for MCP `command:`

## Symptom
`hermes mcp test gbrain` fails with:
```
✗ Connection failed (7140ms): [WinError 193] %1 no es una aplicación Win32 válida
```

## Root cause
`npm install -g bun` on Windows installs a ~283-byte **bash shim** at
`AppData/Local/hermes/node/bun`, NOT a PE binary. Hermes spawns `command:`
directly (no shell), so it cannot execute the shim → WinError 193.

## Verify the bad shim
```
$ file "AppData/Local/hermes/node/bun"
... bash script, ASCII text   ← NOT a valid Win32 exe
```

## Fix — get the real binary
```bash
cd /c/Users/<you>
curl -sL -o bun.zip "https://github.com/oven-sh/bun/releases/download/bun-v1.3.14/bun-windows-x64.zip"
unzip -o bun.zip -d bun-dist
mkdir -p tools
cp bun-dist/bun-windows-x64/bun.exe tools/bun.exe
file tools/bun.exe          # → PE32+ executable for MS Windows ...
./tools/bun.exe --version   # → 1.3.14
```
Then point config.yaml `mcp_servers:<name>.command:` at
`C:/Users/<you>/tools/bun.exe`.

## Note
Hermes's own bundled `bun` (`AppData/Local/hermes/node/bun`) is also the bash shim.
Do not reuse it as an MCP `command:`. The npm-global install and Hermes's node dir
both carry the shim; only the GitHub-release zip has the real `.exe`.
