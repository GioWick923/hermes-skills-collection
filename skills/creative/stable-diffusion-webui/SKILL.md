---
category: creative
name: stable-diffusion-webui
description: Read Forge Neo/A1111 config via gradio_config extraction.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
tags: [stable-diffusion, forge, automatic1111, gradio, config, img2img]
related_skills: [comfyui]
---

# Stable Diffusion WebUI / Forge Neo Configuration Reader

## When to Use
- User asks to see current settings in a running Forge Neo or Automatic1111 WebUI instance
- Need to extract img2img/txt2img defaults programmatically
- Checking checkpoint, sampler, denoising_strength, or other generation parameters
- User says "what's my config?" or "check my settings"

## Architecture

Forge Neo and Automatic1111 both use Gradio as their UI layer. Key insight:
- **UI elements load dynamically** — many parameters aren't in static HTML
- **API endpoints are often hidden** — common paths like `/api/v1/img2img` return 404
- **`window.gradio_config` is the goldmine** — injected into the page HTML

## Core Technique: Extract gradio_config

The most reliable method is parsing `window.gradio_config` from the page source:

```bash
# Extract and parse the config JSON
curl -s "http://localhost:7860/" | python -c "
import sys, json, re
html = sys.stdin.read()
match = re.search(r'window\.gradio_config = ({.*?});', html, re.DOTALL)
if match:
    config = json.loads(match.group(1))
    state = config.get('state', {})
    # Print relevant keys
    for k in sorted(state.keys()):
        if any(x in k.lower() for x in ['i2i', 'img2img', 'denoising', 'sd_', 'xl_', 'flux_']):
            print(f'{k}: {state[k]}')
"
```

**Note:** This only works if the Gradio config is loaded at page render time. Forge Neo may lazy-load some components.

## API Endpoints to Try (in order)

| Endpoint | Method | Returns | Notes |
|----------|--------|---------|-------|
| `/` | GET | Full HTML with gradio_config | Primary source |
| `/queue/data` | GET | Queue status | May be 404 |
| `/internal/queue/jobs` | GET | Internal queue | Forge-specific |
| `/sd_api/v2/sd-models` | GET | Available models | Standard A1111 |
| `/api/v1/txt2img` | POST | Generation endpoint | May not exist |
| `/api/v1/img2img` | POST | Img2img endpoint | Often 404 |
| `/forge/api/info` | GET | Forge info | Forge Neo specific |
| `/gradio/api/info` | GET | Gradio API info | Often 404 |
| `/state` | GET | Current state | May be 404 |

**Pitfall:** Don't assume standard Gradio/SD WebUI API paths exist in Forge Neo. Many return "Not Found".

## Workflow: Reading Forge Neo Config

1. **Check if running:**
   ```bash
   curl -s http://localhost:7860/ | head -c 200
   # Should return HTML, not connection refused
   ```

2. **Extract gradio_config:**
   ```bash
   curl -s "http://localhost:7860/" | grep -o 'window\.gradio_config = {[^}]*}' | python -m json.tool
   ```

3. **Filter for relevant params:**
   ```bash
   curl -s "http://localhost:7860/" | python -c "
   import sys, json, re
   html = sys.stdin.read()
   match = re.search(r'window\.gradio_config = ({.*?});', html, re.DOTALL)
   if match:
       config = json.loads(match.group(1))
       state = config.get('state', {})
       
       # Checkpoint info
       print('=== CHECKPOINT ===')
       print(f'Model: {state.get(\"sd_model_checkpoint\", \"N/A\")}')
       print(f'VAE: {state.get(\"sd_vae\", \"N/A\")}')
       print(f'Clip skip: {state.get(\"CLIP_stop_at_last_layers\", \"N/A\")}')
       
       # Txt2img params
       print('\\n=== TXT2IMG ===')
       print(f'Sampler: {state.get(\"sd_samplers\", \"N/A\")}')
       print(f'Steps: {state.get(\"steps\", \"N/A\")}')
       print(f'Width: {state.get(\"sd_i2i_width\", state.get(\"width\", \"N/A\"))}')
       print(f'Height: {state.get(\"sd_i2i_height\", state.get(\"height\", \"N/A\"))}')
       print(f'CFG: {state.get(\"cfg_scale\", \"N/A\")}')
       
       # Img2img params
       print('\\n=== IMG2IMG ===')
       print(f'Denoising: {state.get(\"denoising_strength\", \"N/A\")}')
       print(f'Width: {state.get(\"i2i_width\", state.get(\"sd_i2i_width\", \"N/A\"))}')
       print(f'Height: {state.get(\"i2i_height\", state.get(\"sd_i2i_height\", \"N/A\"))}')
   "
   ```

4. **If gradio_config fails:** Try scraping visible UI via `drive_preview` or `bsk`:
   - Open the Forge Neo URL in preview
   - Click the tab (`tab-img2img`, `tab-txt2img`)
   - Scroll to reveal parameters
   - Use `elements` to find refs, then read values

## Known Limitations

- **Dynamic loading:** Forge Neo lazy-loads some UI components; params may not appear in initial gradio_config
- **No standardized API:** Unlike ComfyUI's `/api/prompt`, Forge Neo doesn't expose a clean config API
- **Browser automation fallback:** If API extraction fails, use `drive_preview` to visually inspect the UI
- **Session-specific:** Config values change per user; always query the live instance

## Common Parameters to Check

### Img2img Specific
| Parameter | Key Name | Default | Description |
|-----------|----------|---------|-------------|
| Denoising strength | `denoising_strength` | 0.75 | How much to transform the input image |
| Width | `i2i_width` / `sd_i2i_width` | varies | Output width |
| Height | `i2i_height` / `sd_i2i_height` | varies | Output height |
| Extra noise | `img2img_extra_noise` | 0 | Additional noise for variation |
| Color correction | `img2img_color_correction` | false | Apply color correction |

### Global Generation
| Parameter | Key Name | Description |
|-----------|----------|-------------|
| Sampler | `sd_samplers` | Euler a, DPM++ 2M SDE, etc. |
| Steps | `steps` | Number of denoising steps |
| CFG Scale | `cfg_scale` | Classifier-free guidance scale |
| Checkpoint | `sd_model_checkpoint` | Current model file |
| VAE | `sd_vae` | Variational autoencoder |
| Clip skip | `CLIP_stop_at_last_layers` | CLIP layer skip |

## Pitfalls

1. ❌ **Assuming API paths exist** — `/api/v1/img2img` often returns 404. Always try gradio_config first.
2. ❌ **Not handling empty state** — `window.gradio_config` may not have `state` key if page didn't fully load.
3. ❌ **Confusing Forge Neo with ComfyUI** — Different architectures. ComfyUI uses `/api/prompt`; Forge uses Gradio endpoints.
4. ❌ **Reading stale config** — Config is captured at page load. If user changed settings after load, they won't appear.
5. ✅ **Use grep for quick checks** — `curl -s localhost:7860/ | grep -i "denoise\|strength\|img2img"` can find parameter names quickly.

## Related Skills
- `comfyui` — For ComfyUI workflow execution (different tool, similar goal)

## Support Files
- `references/forge-api-endpoints.md` — Complete API endpoint reference for Forge Neo
- `scripts/extract-config.py` — Script to extract and format config from running instance
