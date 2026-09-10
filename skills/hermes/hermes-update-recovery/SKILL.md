---
category: hermes
name: hermes-update-recovery
description: "Fix broken Hermes venv after failed update on Windows."
version: 1.0.0
author: <USER> + Hermes
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [hermes, update, recovery, venv, windows, cron, yaml, certifi]
    related_skills: [hermes-health-check, hermes-self-audit, bot-fleet-registry, hermes-mcp-integration]
---

# Hermes Update Recovery (Windows venv repair)

## When to use
- `hermes update` exits with code 2 and prints "failed to remove file ... _yaml.cp311-win_amd64.pyd: Acceso denegado" or "Early interrupted-install completion failed".
- `hermes --version` / any `hermes` command throws `ModuleNotFoundError: No module named 'hermes_cli'`.
- Tool calls or cron jobs fail with SSL errors (`Invalid SSL_CERT_FILE ... No default certificates will be trusted`) — certifi was half-removed.
- Cron jobs die with `RuntimeError: 'NoneType' object has no attribute 'build_kwargs'` AFTER an update that was supposed to fix it (venv still mid-recovery).

## Root cause (Windows-specific)
`hermes update` upgrades the code (git pull) AND the venv. The venv reinstall runs while the **Desktop app + headroom proxy** hold native `.pyd` files open → uv cannot overwrite them → it wipes the Python `.py` files (yaml `__init__.py`, the editable `hermes_cli` link) but leaves the locked `.pyd` behind, producing a half-installed venv. A `.update-incomplete` marker in `hermes-agent/` then makes EVERY `hermes` launch retry the broken reinstall (which re-wipes yaml and crashes `cron`/`main.py`).

## Golden rules
1. **The `.update-incomplete` marker is the trap.** While it exists, each `hermes` invocation re-runs the failed reinstall and re-breaks yaml. Clear it ONLY after you have manually restored yaml + the editable link (step 5).
2. **Compare `.pyd` hashes before deciding to swap.** In #57828 the recovery force-reinstalls yaml even when the installed `.pyd` is byte-identical to the wheel — the swap adds nothing and only fails because the app has the file open. If `sha256(installed .pyd) == sha256(wheel .pyd)`, skip the swap; just restore `__init__.py` + `dist-info`.
3. **The app Desktop must be CLOSED** for the auto-recovery to finish the venv cleanly. If you must repair with the app open, do it by hand (steps below) and clear the marker yourself.
4. **Never `pip install --upgrade` the whole venv** mid-session — it re-triggers the lock race. Restore packages individually from wheels.

## Repair sequence (app open, manual)

Variables:
```
CLI="$LOCALAPPDATA/hermes/hermes-agent/bin/hermes.exe"
VENV="$LOCALAPPDATA/hermes/hermes-agent/venv"
WHEELDIR="$LOCALAPPDATA/Temp/yamlfix"
```

1. **Backup config + kill headroom lockers** (headroom holds yaml/venv open):
   ```bash
   cp "$LOCALAPPDATA/hermes/config.yaml" "$LOCALAPPDATA/hermes/config.yaml.bak.$(date +%Y%m%d_%H%M%S)_preupdate"
   # headroom shows as 1 exe + 2 python wrappers — kill all 3
   powershell -NoProfile -Command "Get-Process | Where-Object { \$_.ProcessName -like '*headroom*' } | Stop-Process -Force"
   # (taskkill //PID fails under MSYS path conversion — use powershell)
   ```
2. **Run `hermes update` once** (it will likely still fail on the `.pyd` lock — that's fine, code is pulled).
3. **Restore certifi** (SSL broken):
   ```bash
   uv pip install --python "$VENV/Scripts/python.exe" certifi
   # verify: "$VENV/Scripts/python.exe" -c "import urllib.request,ssl,certifi; ssl.create_default_context(cafile=certifi.where())"
   ```
4. **Download the EXACT yaml wheel** (read version from error or `PyYAML-*.dist-info`):
   ```bash
   mkdir -p "$WHEELDIR"
   # get wheel URL from https://pypi.org/pypi/PyYAML/<ver>/json  (urls[].filename ends cp311-cp311-win_amd64.whl)
   curl -sL -o "$WHEELDIR/PyYAML-<ver>-cp311-cp311-win_amd64.whl" "<url>"
   ```
   Restore `yaml/__init__.py` + `dist-info` WITHOUT touching the `.pyd`:
   ```bash
   "$VENV/Scripts/python.exe" - <<'PY'
   import zipfile, os, shutil
   VENV = os.environ['LOCALAPPDATA'] + r'\hermes\hermes-agent\venv\Lib\site-packages'
   with zipfile.ZipFile(os.path.join(os.environ['LOCALAPPDATA'],'Temp','yamlfix','PyYAML-<ver>-cp311-cp311-win_amd64.whl')) as z:
       for n in z.namelist():
           if n.endswith('.pyd'): continue
           z.extract(n, 'out')
   for root,_,files in os.walk('out'):
       rel=os.path.relpath(root,'out'); dest=os.path.join(VENV,rel) if rel!='.' else VENV
       os.makedirs(dest,exist_ok=True)
       for f in files:
           if f.endswith('.pyd'): continue
           shutil.copy(os.path.join(root,f),os.path.join(dest,f))
   PY
   # verify: import yaml; yaml.__version__; hasattr(yaml,'SafeDumper')
   ```
5. **Restore the editable `hermes_cli` link** (CLI dead without it):
   ```bash
   cd "$LOCALAPPDATA/hermes/hermes-agent" && uv pip install -e . --no-deps
   ```
6. **Clear the recovery marker** (only now — yaml + link are whole):
   ```bash
   rm -f "$LOCALAPPDATA/hermes/hermes-agent/.update-incomplete"
   rm -f "$LOCALAPPDATA/hermes/hermes-agent/.lazy-refresh-incomplete"
   ```
7. **Restart headroom** (was killed in step 1):
   ```bash
   "$VENV/Scripts/headroom.exe" proxy --port 8787 --mode token --openai-api-url https://openrouter.ai/api/v1 --code-aware --log-file="$LOCALAPPDATA/hermes/headroom-proxy.log"
   # verify: curl -s -o /dev/null -w "%{http_code}" http://localhost:8787/health  -> 200
   ```

## Post-update cron repair
- `build_kwargs` deaths after an update mean the job's `provider`/`model` snapshot points at a dead provider (e.g. `nvidia/glm-5.2`, `openrouter/tencent/hy3`, `orcarouter/tencent/hy3-free`). Re-pin each agent job:
  ```bash
  "$CLI" cron edit <job_id> --provider orcarouter --model deepseek/deepseek-v4-flash-0731
  ```
- `drift_skip` deaths: same `cron edit` with the current global provider/model unblocks them.
- Jobs stuck with a `fire_claim` from a dead run: clear it by editing `cron/jobs.json` (`fire_claim: null`) — the scheduler reclaims "unknown" runs every tick.

## Verification
- `"$CLI" --version` → prints `Hermes Agent vX.Y.Z` (no ModuleNotFoundError, no recovery retry spam).
- `"$VENV/Scripts/python.exe" -c "import hermes_cli, yaml, certifi"` → all import.
- `curl localhost:8787/health` → 200.
- `cron run <agent_job_id>` → job reaches API call #1 with the pinned model (check `logs/agent.log` for `model=deepseek/deepseek-v4-flash-0731`).

## Pitfalls
- **`taskkill //PID` fails under MSYS** (bash on Windows) — the `//` becomes a path. Use `powershell -NoProfile -Command "Stop-Process -Id <pid> -Force"`.
- **The recovery retry re-breaks yaml** every launch while the marker lives — clear the marker LAST, after manual restore.
- **Do NOT delete the locked `.pyd`** — the app has it open; just restore the `.py` siblings. Force-reinstalling yaml wholesale will fail on the same lock and re-wipe `__init__.py`.
- **gbrain MCP "Connection closed"** after update is usually a ZOMBIE duplicate server (old PID holding the PGLite DB). Kill the stray `bun` PID, let Hermes relaunch its own. The gbrain server only stays alive while Hermes holds the stdio pipe — `mcp test` connecting then exiting will close it; that's normal, not a bug.
- **lightpanda** configured as `wsl -e bash -lc "lightpanda mcp"` fails when the default WSL distro is `docker-desktop` (no bash in PATH). Remove it if unused; it silently hangs the MCP connect loop.
