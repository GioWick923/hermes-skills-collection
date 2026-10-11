# Migration backup layout & exact commands

## Outer archive shape
```
HermesMigration_YYYYMMDD_HHMMSS.tar.gz
├── appdata.tar      # plain tar (NOT gzipped) -> AppData\Local\hermes
├── home.tar        # plain tar (NOT gzipped) -> ~/.hermes, .gbrain, .agent-reach, .twitter-cli, .opencli, .mcporter
└── manifest.txt    # source host, generated time, claimed contents
```

## Inspect without extracting everything
```bash
# outer listing
tar -tzf "/c/Users/<USER>/Downloads/HermesMigration_20260805_032653.tar.gz"
# -> appdata.tar  home.tar  manifest.txt

# read manifest
tar -xzf "...tar.gz" manifest.txt -O

# extract ONLY the two inner tars + manifest to a temp dir
mkdir -p /c/Users/<USER>/Downloads/hermes_mig_work
cd /c/Users/<USER>/Downloads/hermes_mig_work
tar -xzf "/c/Users/<USER>/Downloads/HermesMigration_20260805_032653.tar.gz" appdata.tar home.tar manifest.txt
```

## CRITICAL: inner tars are PLAIN tar (no gzip)
```bash
# WRONG — yields empty output, no error:
tar -xzf appdata.tar            # -z expects gzip, inner is plain -> empty

# RIGHT:
tar -tf appdata.tar | head -60          # list
tar -xf appdata.tar -C compare hermes/  # extract (no -z)

# home.tar dotfiles:
tar -tf home.tar | head -150
tar -xf home.tar -C compare .gbrain .hermes
```

## Compare backup vs live (decide whether to restore)
```bash
du -sh compare/.gbrain  /c/Users/<USER>/.gbrain
du -sh compare/.hermes  /c/Users/<USER>/.hermes
find /c/Users/<USER>/.gbrain/brain.pglite -type f | wc -l   # 1412 in worked example
# skills count:
find "/c/Users/Agent G/AppData/Local/hermes/skills" -maxdepth 1 -type d | wc -l
find "/c/Users/Agent G/AppData/Local/hermes/skills" -maxdepth 2 -name SKILL.md | wc -l
```

## Post-migration drift fix A: cron model pin (via Hermes CLI)
The agent `cronjob` tool CANNOT set model/provider ("No updates provided"). Use the CLI:
```bash
hermes cron edit a01f52c4f2f6 --provider openrouter --model "tencent/hy3:free"
hermes cron edit 6b7b8c929d1d --provider custom    --model "deepseek-v4-flash-0731"
hermes cron edit ba036e0e832b --provider openrouter --model "nvidia/nemotron-3-ultra-550b-a55b:free"
# verify
grep -oE '"name": "[^"]*"|"model": "[^"]*"' jobs.json
# test-run the gbrain sync job:
# (cronjob action=run job_id=9f47c59472c8) -> expect last_status: ok
```
no_agent + --script jobs (teeth_reminder.sh, audit_hermes.sh) need NO pin.

## Post-migration drift fix B: gbrain database_path
File: `C:\Users\<NEWUSER>\.gbrain\config.json`
```json
{ "engine": "pglite",
  "database_path": "C:\\Users\\<USER>\\.gbrain\\brain.pglite",   // was OLDUSER
  "embedding_model": "ollama:nomic-embed-text", ... }
```
Patch only `database_path` to the NEW user's real brain location.

## Post-migration drift fix C: missing cron script
If `hermes cron list` shows `error: Script not found: ...\scripts\teeth_reminder.sh`,
create `scripts/teeth_reminder.sh` (e.g. `hermes send -t telegram "..."` wrapper, echo the message as stdout for no-agent delivery).

## Always back up before editing
```bash
TS=$(date +%Y%m%d_%H%M%S)
cp jobs.json jobs.json.bak.$TS
cp config.json config.json.bak.$TS
cp config.yaml config.yaml.bak.mcp.$TS    # before any MCP path sed
```

## Post-migration drift fix D: MCP paths + bins in config.yaml

### D.1 Replace OLDUSER -> NEWUSER in all MCP command paths
```bash
cd "/c/Users/Agent G/AppData/Local/hermes"
cp config.yaml config.yaml.bak.mcp.$(date +%Y%m%d_%H%M%S)
sed -i 's|<USER> GAMES|Agent G|g' config.yaml      # OLDUSER -> NEWUSER
grep -c "<USER> GAMES" config.yaml                  # expect 0
grep -nE "command:|executablePath:" config.yaml      # show the corrected paths
```

### D.2 Locate missing bins in migration staging and copy to live data-dir
The migration often leaves tool binaries in a staging dir WITHOUT copying them
to the live data-dir. staging lives under the NEW user's Temp:
`C:\Users\<NEWUSER>\AppData\Local\Temp\hermes-restore\hermes\`
```bash
SRC="/c/Users/<USER>/AppData/Local/Temp/hermes-restore/hermes"
DST="/c/Users/Agent G/AppData/Local/hermes"
# chrome-devtools-mcp.cmd + playwright-mcp.cmd
cp -r "$SRC/tools/mcp-bin" "$DST/tools/"
# obscura.exe
cp -r "$SRC/tools/obscura" "$DST/tools/"
# scrapling.exe (in the venv)
mkdir -p "$DST/hermes-agent/venv/Scripts"
cp "$SRC/hermes-agent/venv/Scripts/scrapling.exe" "$DST/hermes-agent/venv/Scripts/"
# bun.exe (lives at src/node/node_modules/bun/bin/bun.exe — copy to tools/)
cp "$SRC/node/node_modules/bun/bin/bun.exe" "$DST/tools/bun.exe"
```
Copy the big dirs in the background (obscura + mcp-bin can be hundreds of MB):
`terminal(background=true, notify_on_complete=true)`.

### D.3 Playwright chrome.exe version + user-dir fix
config.yaml may pin a chromium version the new PC does NOT have, and/or point at the
data-dir user (`Agent G`) while Playwright actually installed under `<USER>`.
```bash
# what's actually installed?
ls "/c/Users/<USER>/AppData/Local/ms-playwright/"           # e.g. chromium-1208
# sed the version AND the user dir in one pass:
sed -i 's|chromium-1228|chromium-1208|g' config.yaml          # version
sed -i 's|Agent G/AppData/Local/ms-playwright|<USER>/AppData/Local/ms-playwright|g' config.yaml
# verify the chrome.exe the config now points to actually exists:
ls -la "C:/Users/<USER>/AppData/Local/ms-playwright/chromium-1208/chrome-win64/chrome.exe"
```

### D.4 Disable orphan MCP server (e.g. gbrain cli.ts)
A server referencing a project that only existed on the old PC (example: gbrain as
a local TS build via `gbrain/src/cli.ts` — the new PC runs gbrain as pglite via
~/.gbrain, NOT via that cli.ts) must be disabled so the rest of the MCP block loads.
```bash
# find the server block's enabled: line (gbrain is at lines 755-764 in this example)
sed -n '755,770p' config.yaml
# flip ONLY that line to false:
sed -i '764s/enabled: true/enabled: false/' config.yaml
sed -n '764p' config.yaml    # confirm: "    enabled: false"
```
Don't delete the block — leave it for the user to rebuild later if they re-create
gbrain as a TS project on this PC.

### D.5 Verify all MCP bins exist (after copies)
```bash
# function wrapper is UNRELIABLE for paths with a space ("Agent G") — use ls -la directly.
for p in \
  "C:/Users/Agent G/tools/bun.exe" \
  "C:/Users/Agent G/AppData/Local/hermes/hermes-agent/venv/Scripts/scrapling.exe" \
  "C:/Users/Agent G/AppData/Local/hermes/tools/obscura/v0.1.10/obscura.exe" \
  "C:/Users/Agent G/AppData/Local/hermes/tools/mcp-bin/node_modules/.bin/chrome-devtools-mcp.cmd" \
  "C:/Users/Agent G/AppData/Local/hermes/tools/mcp-bin/node_modules/.bin/playwright-mcp.cmd" \
  "C:/Users/<USER>/AppData/Local/ms-playwright/chromium-1208/chrome-win64/chrome.exe"; do
    ls -la "$p" >/dev/null 2>&1 && echo "✅ $p" || echo "❌ $p"
done
```
If `bun.exe` shows ❌ via a `[ -f ]`/`&&` test but `ls -la` shows the 98MB file, that is
the git-bash-space-in-path false-negative (see SKILL.md pitfall) — the file IS there;
trust `ls -la` and `find`.

## Cleanup
```bash
rm -rf /c/Users/<USER>/Downloads/hermes_mig_work   # multi-GB temp
```
