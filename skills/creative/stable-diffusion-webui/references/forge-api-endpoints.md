# Forge Neo API Endpoints Reference

## Base URL
Typically: `http://localhost:7860`

## Standard Endpoints (Often 404)

| Path | Method | Status | Notes |
|------|--------|--------|-------|
| `/` | GET | ✅ | Main UI, contains gradio_config |
| `/queue/data` | GET | ❌ | Not implemented in Forge |
| `/internal/queue/jobs` | GET | ❌ | Forge-specific, often missing |
| `/sd_api/v2/sd-models` | GET | ⚠️ | May exist in some versions |
| `/api/v1/txt2img` | POST | ❌ | Not exposed |
| `/api/v1/img2img` | POST | ❌ | Not exposed |
| `/forge/api/info` | GET | ❌ | Not implemented |
| `/gradio/api/info` | GET | ❌ | Gradio API not exposed |
| `/forge/settings` | GET | ❌ | No settings endpoint |
| `/api/v1/config/img2img` | GET | ❌ | Non-existent |
| `/state` | GET | ❌ | No state endpoint |
| `/queue/` | GET | ❌ | Queue not accessible |

**Conclusion:** Forge Neo does NOT expose a clean REST API for configuration or generation. The primary access method is:
1. Parse `window.gradio_config` from the HTML page
2. Use Gradio's internal WebSocket protocol (not documented)
3. Interact via the web UI (browser automation)

## How Config is Stored

Forge Neo stores settings in:
- **Memory:** `window.gradio_config.state` (runtime, lost on restart)
- **Files:** `config.json` in the Forge Neo installation directory
- **Command line:** Startup flags in `webui-user.bat` or launch script

## File Locations (Windows)

Typical Forge Neo installation:
```
C:/Users/<user>/Downloads/forge/
├── webui-user.bat      # Launch script with startup flags
├── config.json         # Persistent settings
├── models/
│   ├── Checkpoints/    # SD models
│   └── VAE/            # VAE files
└── user.js             # Custom JS (if any)
```

## Reading config.json Directly

If you have filesystem access:

```bash
# Find the config file
ls -la "C:/Users/$USER/Downloads/forge/config.json"

# Read it
cat "C:/Users/$USER/Downloads/forge/config.json" | python -m json.tool
```

Common keys in `config.json`:
- `sd_model_checkpoint` — Default model
- `sd_vae` — Default VAE
- `sd_hypernetwork` — Hypernetwork setting
- `samples_save` — Whether to save samples
- `samples_format` — Image format (png/jpg)
- `img2img_dimensions` — Default img2img size
- `return_grid` — Whether to show grid
- `enable_quantization` — Quantization setting

## Alternative: Parse from Running Instance

When the instance is running, the most reliable method is:

```python
import requests
import json
import re

resp = requests.get("http://localhost:7860/")
html = resp.text

# Extract gradio_config
match = re.search(r'window\.gradio_config = ({.*?});', html, re.DOTALL)
if match:
    config = json.loads(match.group(1))
    print(json.dumps(config, indent=2))
```

## Troubleshooting

### Problem: gradio_config not found
**Cause:** Page is still loading or using a different template
**Solution:** Wait for full page load, check network tab for `/` response

### Problem: Config doesn't show img2img params
**Cause:** Tab hasn't been selected yet (lazy loading)
**Solution:** Use browser automation to click the Img2img tab first, then extract

### Problem: API returns 404
**Cause:** Forge Neo doesn't expose these endpoints
**Solution:** Use gradio_config extraction instead
