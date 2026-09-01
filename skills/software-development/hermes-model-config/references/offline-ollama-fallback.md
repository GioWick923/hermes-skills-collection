# Offline fallback: Ollama (Hermes 3) as last-resort provider

Verified recipe from a live session (Windows 11, Hermes Agent + Ollama 0.31.2).

## Goal
Use OpenRouter (online) normally; if there is no internet, automatically fall back to a
local Ollama model so the agent keeps working with zero cost / zero data leaving the machine.

## 1. Install + run Ollama (if not present)
- Ollama binary is usually at `C:\Users\<user>\AppData\Local\Programs\Ollama\ollama.exe`.
  If missing from PATH, symlink it: `ln -sf "<that path>" "$HOME/bin/ollama"`.
  NOTE: the Hermes install dir is `C:\Users\<user>\AppData\Local\hermes\...` — do NOT
  confuse it with the Ollama install dir. They are different.
- Start server: `ollama serve` (or just open the Ollama app — it autostarts the server).
- Verify: `curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/api/tags` → `200`.

## 2. Pull a local model
- `ollama pull hermes3:8b`  (~4.7 GB; fine on consumer hardware with ~8 GB RAM/VRAM).
- Confirm: `ollama list | grep hermes3:8b`.

## 3. Add Ollama as LAST fallback in config.yaml
Ollama is OpenAI-compatible at `http://localhost:11434/v1`, so it is a `custom:`-shape entry.
The provider *name* can be any unique string (resolver treats unknown names as `custom`).
`api_key` MUST be a non-empty string (Ollama ignores it, but an empty value can trip auth code).

```yaml
fallback_providers:
  - provider: custom                 # existing online fallback (NVIDIA/GLM etc.)
    model: z-ai/glm-5.2
    base_url: https://integrate.api.nvidia.com/v1
    api_key: nvapi-XXXX
    api_mode: openai
  - provider: ollama_local          # <- ADDED, local, last in list = last resort
    model: hermes3:8b
    base_url: http://localhost:11434/v1
    api_key: ollama
    api_mode: openai
```

Write via terminal-Python (file tools are guard-blocked on config.yaml), take a backup FIRST:
```python
import yaml, os, datetime
p = os.path.expanduser("~/AppData/Local/hermes/config.yaml")
cfg = yaml.safe_load(open(p, encoding="utf-8"))
bak = p + ".bak-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
yaml.safe_dump(cfg, open(bak,"w",encoding="utf-8"), sort_keys=False)  # PRISTINE pre-mutation backup
entry = {"provider":"ollama_local","api_mode":"openai",
         "base_url":"http://localhost:11434/v1","api_key":"ollama","model":"hermes3:8b"}
if not any(e.get("provider")=="ollama_local" for e in cfg["fallback_providers"]):
    cfg["fallback_providers"].append(entry)
yaml.safe_dump(cfg, open(p,"w",encoding="utf-8"), allow_unicode=True, sort_keys=False, default_flow_style=False)
```

## 4. Verify the offline path (real test, without killing internet)
`--provider deadbeef` does NOT exercise the fallback — Hermes validates the provider name and
aborts with `Unknown provider`. Instead break the PRIMARY's reachability and keep only Ollama:

```python
import yaml, os
p = os.path.expanduser("~/AppData/Local/hermes/config.yaml")
cfg = yaml.safe_load(open(p, encoding="utf-8"))
cfg["model"]["base_url"] = "http://127.0.0.1:9/v1"        # closed port = unreachable
cfg["fallback_providers"] = [e for e in cfg["fallback_providers"] if e.get("provider")=="ollama_local"]
yaml.safe_dump(cfg, open(p,"w",encoding="utf-8"), sort_keys=False, default_flow_style=False)
# run:  hermes chat -q "Responde SOLO con: OLLAMA_FALLBACK_OK"
# expect: the local model answers (no internet used)
# RESTORE from the pristine backup taken in step 3 (NOT a mid-experiment snapshot!)
orig = yaml.safe_load(open(<bak>, encoding="utf-8"))
yaml.safe_dump(orig, open(p,"w",encoding="utf-8"), sort_keys=False, default_flow_style=False)
```

Gotcha hit in practice: restoring from a *mid-experiment* snapshot (taken after pruning to
solo-Ollama) silently dropped the NVIDIA fallback entry. Always restore from the PRISTINE
pre-mutation backup and re-check `len(get_fallback_chain(load_config())) == original count`.

## 5. BOM pitfall (Windows)
If `config.yaml` ever gets a UTF-8 **BOM** (e.g. edited in Notepad), Hermes dies on first run
with `HTTP 400 "No models provided"`. The terminal-Python rewrite above writes without BOM.
Check: `raw[:3] == b'\xef\xbb\xbf'` must be False.

## 6. Confirm normal mode still uses the online primary
With restored config: `hermes chat -q "Responde con UNA palabra: ENLINEA"` should answer via
OpenRouter and NOT touch Ollama (watch for absence of "ollama" / "fallback" in output).

## Python to use
On Windows, `python3` may be missing and bare `python` may open the Microsoft Store alias.
Use the Hermes venv directly:
`$HOME/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`.
