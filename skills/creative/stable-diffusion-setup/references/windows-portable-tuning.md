# Windows Portable + RTX 3060 Tuning Reference

## ComfyUI Portable Install Flow

```
git clone → venv → pip install torch cu121 → pip install -r requirements.txt
                                          → custom nodes (Manager, Impact, ControlNet)
                                          → pip install deps for each
                                          → launch.bat with flags
                                          → fix comfy-kitchen list[int] bug
```

## Forge Neo Install Flow

```
git clone → venv → pip install torch 2.5.1 cu121
                 → pip install numpy==1.26.2 scipy==1.16.3 scikit-image==0.22.0
                 → pip install opencv-python-headless==4.9.0.80
                 → pip install setuptools huggingface-guess
                 → launch with --skip-prepare-environment
```

## Forge Neo API (A1111-compatible)

- Endpoint: `POST /sdapi/v1/txt2img`
- Port: `:7860`
- Standard SD WebUI payload format
- Response includes `images[]` (base64), `parameters`, `info`
- Base64 padding fix: `4 - len % 4` → append `=` that many times
- Typical image size at 1024²: ~2-3MB PNG
- Works without `--api` flag (Forge Neo enables it by default)

## xFormers Availability Matrix (Windows)

| PyTorch | cu121 wheel? | Works? |
|---------|--------------|--------|
| 2.1.0 | xformers 0.0.22.post7 ✅ | Sin CUDA extensions con >2.1 |
| 2.4.0 | xformers 0.0.27.post2 ✅ | fbgemm.dll roto en Windows |
| 2.5.1 | ❌ No hay | — |
| 2.6.x (cu128) | ✅ wheels recientes | Disponible |

## ComfyUI Bug: list[int] en comfy-kitchen

**Archivo**: `venv/Lib/site-packages/comfy_kitchen/backends/eager/na.py`

**Torch 2.5.1** rechaza `list[int]` en `@torch.library.custom_op`. Fix: `from typing import List, Optional` y cambiar `list[int]` → `List[int]`.

## Forge Neo: numpy compat chain (tested working)

| Package | Version | Notes |
|---------|---------|-------|
| numpy | 1.26.2 | 2.x rompe ABI con scikit-image |
| scipy | 1.16.3 | Compatible con numpy 1.26 |
| scikit-image | 0.22.0 | Compilada contra numpy 1.x |
| opencv-python-headless | 4.9.0.80 | 5.x requires numpy>=2 |
| torch | 2.5.1+cu121 | — |
| setuptools | latest | Needed for pkg_resources |
| huggingface-guess | latest | Needed by Forge backend loader |

**Key insight**: numpy 2.x breaks scikit-image ABI. Downgrade to 1.26.2 + opencv 4.x. Always `--skip-prepare-environment`.

## Benchmarks RTX 3060 12GB (SDXL 1024², 25 steps)

| Configuración | s/image | UI |
|--------------|---------|-----|
| Default (sin flags) | ~7.2s | ComfyUI |
| + --use-split-cross-attention | ~6.1s | ComfyUI |
| + --cpu-vae | ~5.8s | ComfyUI |
| + ambos | ~4.7s estimado | ComfyUI |
| Forge Neo default | ~14s | Forge |
| Forge Neo optimized | ~8-10s | Forge |

## Chrome Registry Fix (for browser-use tool)

```powershell
reg add "HKCU\Software\Policies\Google\Chrome" /v "RemoteDebuggingAllowed" /t REG_DWORD /d 1 /f
reg add "HKCU\Software\Policies\Google\Chrome" /v "RemoteDebuggingPort" /t REG_DWORD /d 9222 /f
taskkill /F /IM chrome.exe
```

## Warn ComfyUI log message

"You need pytorch with cu130 or higher" es genérica de comfy-kitchen. Ignorar en RTX 3060 — cu121 funciona. NVFP4 es solo para Blackwell (50-series).