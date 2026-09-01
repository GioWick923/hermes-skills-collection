---
category: productivity
name: torlink-downloader
description: "torlink HTTP API for torrent search, add, monitor."
version: "1.0.0"
author: "Hermes Agent"
license: MIT
platforms: [windows]
---

# torlink-downloader

Use torlink (`torlnk`) as a headless torrent downloader integrated into Hermes. The HTTP API (`serve` mode) accepts magnets and tracks downloads; `files` mode serves completed files.

## Prerequisites

- Node.js v18+ (v22.23.2 confirmed)
- `torlnk` installed globally: `npm install -g torlnk --ignore-scripts && npm rebuild torlnk`
- Ports 9161 (serve) and 9160 (files) free

## Architecture

```
Agent → web_search (find magnets)
     → curl POST /add → torlnk serve (:9161) → downloads → ~/Downloads/torlink/
     → curl GET /downloads → check status
     → (optional) curl from torlnk files (:9160) → stream finished files
```

## Start daemons

### 1. Serve daemon (accept magnets via HTTP)

```bash
torlnk serve --daemon
# → torlink serve daemon started (pid NNNNN).
#   logs: C:\Users\<USER>\AppData\Local\torlink\Data\logs\serve.log
#   stop: kill NNNNN
```

### 2. Files daemon (serve completed downloads via HTTP)

```bash
torlnk files --daemon
# → torlnk files serving ~/Downloads/torlink on http://127.0.0.1:9160
```

## HTTP API (serve mode, port 9161)

### Health check
```bash
curl -s http://127.0.0.1:9161/health
# → {"ok":true,"version":"1.7.0"}
```

### Add a magnet / info hash
```bash
curl -s -X POST http://127.0.0.1:9161/add \
  -H "Content-Type: application/json" \
  -d '{"magnet":"magnet:?xt=urn:btih:<HASH>&dn=<NAME>"}'
# → {"ok":true,"outcome":"added"}

# Also accepts bare info hash:
curl -s -X POST http://127.0.0.1:9161/add \
  -H "Content-Type: application/json" \
  -d '{"magnet":"<40-char-hex-hash>"}'
```

### List active downloads and seeds
```bash
curl -s http://127.0.0.1:9161/downloads
# → {"downloads":[{"id":"...","name":"...","status":"downloading|done|seeding","progress":0.5,"peers":3,"speed":123456}],"seeds":[...]}
```

## Files API (files mode, port 9160)

### List completed files
```bash
curl -s http://127.0.0.1:9160/
# → JSON array of files
```

### Download / stream a file
```bash
curl -s http://127.0.0.1:9160/<filename>
# → file content (supports Range for seeking/resuming)
```

## Hermes workflow

1. **Search web** for magnet links
2. **Verify** daemons running (health check, start if not)
3. **POST** magnets to `/add`
4. **Poll** `/downloads` until status=done or seeding
5. **Report** to user: what was downloaded, size, status

### Stop daemons
```bash
kill $(cat "$LOCALAPPDATA/torlink/Data/logs/serve.pid")
kill $(cat "$LOCALAPPDATA/torlink/Data/logs/files.pid")
```

## Pitfalls

- ❌ **WebRTC warning**: TCP/UDP peers still work. Fix with `npm rebuild torlnk`.
- ❌ **Daemon doesn't persist across reboots**: Restart after system restart.
- ❌ **No programmatic search API**: Find magnets via web_search, then POST them.
- ❌ **Auth**: Loopback-only by default. Use `--host --token` for public binding.
- ❌ **`--ignore-scripts` needed**: `ip-set` dependency blocks npm with `only-allow pnpm`.

## Verification

```bash
# Check installed
torlnk --version

# Start and test
torlnk serve --daemon
curl -s http://127.0.0.1:9161/health
curl -s -X POST http://127.0.0.1:9161/add -H "Content-Type: application/json" \
  -d '{"magnet":"magnet:?xt=urn:btih:<HASH>&dn=test"}'
curl -s http://127.0.0.1:9161/downloads
```