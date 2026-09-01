---
category: creative
name: stable-diffusion-setup
description: "Install/tune ComfyUI & Forge Neo on Windows RTX 3060. Autonomous image generation, model merging, and user operational style."
version: 4.0.0
author: [hermes-agent]
license: MIT
platforms: [windows]
prerequisites:
  packages: [git, python3]
metadata:
  hermes:
    tags:
      - comfyui
      - forge
      - stable-diffusion
      - windows
      - rtx-3060
      - nvidia
      - image-generation
    related_skills: [comfyui]
    category: creative
---

# Stable Diffusion Setup (Windows + RTX 3060)

Install, configure, and optimize ComfyUI and SD WebUI Forge Neo on Windows with an RTX 3060 12GB.

## When to Use

- User asks to "install ComfyUI" on Windows (manual/portable path)
- User asks to "set up Forge" or "install Forge Neo"
- User asks about GPU tuning, VRAM optimization, or speed flags
- User wants to share models between ComfyUI and Forge
- User hits `list[int]` error or `pkg_resources` error or `huggingface_guess` error

## ComfyUI Portable Install (Manual Path)

Use this when `comfy --skip-prompt install` doesn't support `--workspace` or you want full control.

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git F:/ComfyUI/
cd F:/ComfyUI
python -m venv venv
venv/Scripts/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
venv/Scripts/pip install -r requirements.txt
```

### Custom Nodes (esenciales)

```bash
cd custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
```

Install their deps:

```bash
venv/Scripts/pip install -r custom_nodes/ComfyUI-Impact-Pack/requirements.txt
venv/Scripts/pip install -r custom_nodes/comfyui_controlnet_aux/requirements.txt
# stringzilla fix if build fails:
venv/Scripts/pip install stringzilla --only-binary=:all:
```

### Launch Script (launch.bat)

```batch
@echo off
cd /d F:\ComfyUI
call venv\Scripts\activate
python main.py --listen --port 8188 --use-split-cross-attention --cpu-vae
pause
```

## Forge Neo Setup

```bash
git clone https://github.com/lllyasviel/stable-diffusion-webui-forge.git F:/sd-forge/forge/
cd F:/sd-forge/forge
python -m venv venv
venv/Scripts/pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

### Forge webui-user.bat (flags óptimas)

```batch
set COMMANDLINE_ARGS=--xformers --opt-channelslast --pin-shared-memory --cuda-malloc --cuda-stream
```

## Operational Style (for this user)

⚠️ **This user expects autonomous, proactive behavior.** Do not wait to be asked to generate images — use ComfyUI and Forge APIs independently to illustrate concepts, express ideas, and enrich communication. The "pulpo" (octopus) philosophy: every skill, tool, and MCP is a tentacle — use them all without waiting for instructions. Generate images to demonstrate, explain, or beautify responses.

### Personality in Conversation

The user values when you express personality through well-placed quotes or observations — Bruce Lee ("Be water"), Dr. House (honest truth), Harvey Specter (confidence). **Do not** stay purely transactional. When the context fits, let the persona show. This is what makes the interaction feel like mentor/companion rather than tool. Don't force it, but don't lose it either. The user explicitly called this out as something they missed when it faded.

## Generating Images via API

### ComfyUI API (`:8188`)

Simple JSON workflow submission. Build a prompt dict with nodes (CheckpointLoader, CLIPTextEncode, KSampler, VAEDecode, SaveImage) and POST to `/prompt`. Wait for history then `/view` the output.

```python
# POST /prompt with {"prompt": workflow_dict}
# GET  /history/{prompt_id} → get output filename
# GET  /view?filename=X&type=output → download image
```

### Forge Neo API (`:7860`)

Standard AUTOMATIC1111-compatible endpoint at `/sdapi/v1/txt2img`. Returns base64 images + parameters. **Confirmed working** — this is the cleanest path for programmatic generation.

```bash
curl -X POST "http://localhost:7860/sdapi/v1/txt2img" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "...",
    "negative_prompt": "...",
    "steps": 20,
    "width": 1024,
    "height": 1024,
    "sampler_name": "DPM++ 2M Karras",
    "cfg_scale": 7,
    "seed": -1,
    "batch_size": 1
  }'
```

Response: `{"images":["base64..."], "parameters": {...}, "info": "..."}`

Extract base64 (fix padding: `4 - len % 4`), decode to PNG. 3MB images typical at 1024².

## Chrome Debug Remote Fix (for browser-use tool)

When the browser tool opens Chrome, it shows `chrome://inspect/` waiting for "Allow" click. Fix with registry:

```powershell
reg add "HKCU\Software\Policies\Google\Chrome" /v "RemoteDebuggingAllowed" /t REG_DWORD /d 1 /f
reg add "HKCU\Software\Policies\Google\Chrome" /v "RemoteDebuggingPort" /t REG_DWORD /d 9222 /f
taskkill /F /IM chrome.exe
```

Run once with admin — Chrome will never prompt for Allow again.

## Pitfalls

### 1. `ValueError: infer_schema(func): Parameter kernel_size has unsupported type list[int]`

**Context**: ComfyUI v0.33.0 + torch 2.5.1. `comfy-kitchen` usa `list[int]` que torch 2.5.1 rechaza.

**Fix**: Editar `venv/Lib/site-packages/comfy_kitchen/backends/eager/na.py`:

```python
from typing import List, Optional  # add at imports
# Replace: kernel_size: list[int] → kernel_size: List[int]
# Replace: is_causal: list[bool]  → is_causal: List[bool]
```

### 2. Forge Neo — numpy/scikit-image/opencv incompatibility cascade

Forge Neo's `launch.py` tries to install deps on first run but hits numpy ABI errors (`ValueError: numpy.dtype size changed, expected 96 from C header, got 88 from PyObject`). **Skip prepare env and pin exact versions:**

```bash
# After cloning and creating venv, install torch first:
venv/Scripts/pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121

# Fix numpy compat (pin to versions that match Forge's compiled deps)
venv/Scripts/pip install numpy==1.26.2 scipy==1.16.3 scikit-image==0.22.0
venv/Scripts/pip install opencv-python-headless==4.9.0.80
venv/Scripts/pip install setuptools huggingface-guess
```

Then **always use `--skip-prepare-environment`**:

```bash
venv/Scripts/python launch.py --listen --port 7860 --xformers --opt-channelslast --pin-shared-memory --api --skip-prepare-environment
```

Without `--skip-prepare-environment`, Forge's launch.py enters a pip install loop that crashes on `cv2.pyd` with permission errors.

### 3. xFormers no disponible en Windows + cu121 + torch 2.5.1

No hay wheel de xFormers con extensiones CUDA para Windows + cu121 + torch 2.5.1. Dejar `--xformers` en flags — Forge maneja fallback. PyTorch attention nativa funciona.

### 3. `ModuleNotFoundError: No module named 'pkg_resources'`

**Fix**: `pip install setuptools`

### 4. `ModuleNotFoundError: No module named 'huggingface_guess'`

**Fix**: `pip install huggingface-guess`

### 5. `ValueError: numpy.dtype size changed`

**Fix**:
```bash
pip uninstall scikit-image scipy -y
pip install scikit-image scipy --force-reinstall --no-deps
```

### 6. TAESD Preview extreme slowdown (Forge)

**Fix**: Settings → Preview Mode → **Approx NN**. TAESD causa 2-10x slowdown en RTX 3060.

### 7. GPU weights al 100% = 10x más lento

**Fix**: Settings → GPU weights → **80-85%**. Dejar 1-1.5GB VRAM libres.

## Tuning Flags (RTX 3060 12GB + 96GB RAM)

| Flag | Efecto | Applica a |
|------|--------|-----------|
| `--use-split-cross-attention` | ~15% speedup Ampere | ComfyUI |
| `--cpu-vae` | VAE en CPU, libera ~1.5GB VRAM | ComfyUI |
| `--opt-channelslast` | NHWC layout (~5%) | Forge |
| `--pin-shared-memory` | Swap rápido GPU/RAM | Forge |
| `--cuda-malloc` | cudaMallocAsync | Forge |
| `--cuda-stream` | Streams paralelos | Forge |

## Model Junctions (compartir modelos)

Fuente única `F:/Modelos/` con junctions NTFS:

```
# ComfyUI
mklink /J F:\ComfyUI\models\checkpoints F:\Modelos\checkpoints
mklink /J F:\ComfyUI\models\vae        F:\Modelos\vae
mklink /J F:\ComfyUI\models\loras      F:\Modelos\loras
mklink /J F:\ComfyUI\models\embeddings F:\Modelos\embeddings

# Forge Neo
mklink /J F:\sd-forge\forge\models\Stable-diffusion F:\Modelos\checkpoints
mklink /J F:\sd-forge\forge\models\VAE              F:\Modelos\vae
mklink /J F:\sd-forge\forge\models\Lora             F:\Modelos\loras
mklink /J F:\sd-forge\forge\models\ControlNet       F:\Modelos\controlnet
mklink /J F:\sd-forge\forge\embeddings               F:\Modelos\embeddings
```

Requiere `rmdir` previo si la carpeta destino existe y no es junction.

### ⚠️ extra_model_paths.yaml (alternativa a junctions para que ComfyUI vea F:/Modelos)

`F:/ComfyUI/extra_model_paths.yaml` es la vía oficial y NO destructiva para que ComfyUI lea una piscina externa de modelos (más limpia que jugar con junctions/symlinks en MSYS, donde `ln -s` no crea symlinks nativos sin `winsymlinks` y `cmd //c mklink` se corrompe en git-bash).

**Formato correcto** (raíz = base_path como string, subcarpetas como strings):
```yaml
F:\Modelos:
  checkpoints: checkpoints
  clip: clip
  clip_vision: clip
  configs: configs
  controlnet: controlnet
  embeddings: embeddings
  loras: loras
  upscale_models: upscale_models
  vae: vae
  ipadapter: ipadapter
  sams: clip
  gguf: gguf
```

**NO usar** `models:` como key raíz ni `type:` — ComfyUI v0.33.0 hace `for c in config: conf=config[c]` y luego `conf[x].split("\n")`; si `config[c]` es una lista de dicts, lanza `TypeError: list indices must be integers or slices, not dict` y **no arranca**. Ese error exacto es la firma de formato YAML incorrecto. Validar con `curl 127.0.0.1:8188` = 200 tras reiniciar.

### fp32 → fp16 (reducir tamaño de modelo 14GB → 7GB)

Para un modelo fp32 que ya se usa SOLO para generar (no para seguir mergeando/entrenando), convertirlo a fp16 lo reduce a la mitad sin pérdida visible:

```python
import safetensors.torch as st
t = st.load_file(SRC, device="cpu")
out = {k: (v if k.startswith("first_stage_model") else v.half()) for k, v in t.items()}
st.save_file(out, OUT)  # VAE se queda fp32 (no importa), modelo UNet/clip en fp16
```

Verificar: `t[k].dtype == torch.float16` tras recargar. Libera ~7GB por modelo y carga más rápido en RTX 3060.

## ComfyUI — Ejemplo de Workflow para Generación

Workflow JSON mínimo para generar una imagen vía API:

```python
workflow = {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "modelo.safetensors"}},
    "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "prompt", "clip": ["1", 1]}},
    "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "negativo", "clip": ["1", 1]}},
    "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
    "5": {"class_type": "KSampler", "inputs": {
        "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
        "latent_image": ["4", 0], "seed": 42, "steps": 25, "cfg": 7.0,
        "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
    "6": {"class_type": "VAEDecode", "inputs": {"vae": ["1", 2], "samples": ["5", 0]}},
    "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "output"}}
}
requests.post("http://localhost:8188/prompt", json={"prompt": workflow})
```

### Resoluciones comunes

| Relación | Resolución | Uso |
|----------|-----------|-----|
| 1:1 | 1024×1024 | Cuadrado, Instagram |
| 9:16 | 832×1472 | Vertical, móvil, retrato (Reijality/Volet Evergarden sweet spot) |
| 16:9 | 1472×832 | Horizontal, paisaje |
| 3:2 | 1152×768 | Fotografía estándar |

### Samplers recomendados

| Sampler | Velocidad | Calidad | Cuándo |
|---------|-----------|---------|--------|
| DPM++ 2M Karras | ⚡⚡ | 🏆 Excelente | **Default** — mejor calidad global |
| Euler a | ⚡⚡⚡ | 👍 Buena | Iteración rápida, exploración |
| Euler | ⚡⚡⚡ | 👍 Buena | Similar a Euler a, menos variación |
| DPM++ SDE Karras | ⚡ | 🏆 Excelente | Máxima calidad, más lento |

### CFG Scale según estilo

| CFG | Efecto | Cuándo |
|-----|--------|--------|
| 7.0 | Estándar | Default SDXL |
| 4.5-6.0 | Suave | Ilustración, estilos artísticos |
| 2.0-3.0 | Pictórico/pastel | Modelos Illustrious, Reijality — toque suave y onírico. CFG 2.0 es sweet spot para danbooru tags |
| 1.0 | Libre | Flux (distilled models) |

## Forge Neo — API

### Endpoint confirmado

```bash
POST http://localhost:7860/sdapi/v1/txt2img
```

Este endpoint (A1111-compatible) es **el camino correcto** para generación programática. No usar `/call/txt2img_1/` (Gradio interno, 136 parámetros impracticables).

### Respuesta típica

```json
{
  "images": ["base64_encoded_png"],
  "parameters": {
    "prompt": "...",
    "negative_prompt": "...",
    "seed": 1337,
    "sampler_name": "DPM++ 2M Karras",
    "cfg_scale": 7.0,
    "steps": 20,
    "width": 1024,
    "height": 1024
  },
  "info": "{...json string...}"
}
```

### Extraer imagen

```python
import base64
b64 = response.json()["images"][0]
# Fix padding
padding = 4 - len(b64) % 4
if padding != 4:
    b64 += "=" * padding
with open("output.png", "wb") as f:
    f.write(base64.b64decode(b64))
```

## Glosario Completo en Obsidian

El vault `Memorias/Agente/Glosario-ComfyUI-Forge-Neo.md` contiene:
- Arquitectura de carpetas detallada
- 9 pitfalls documentados con soluciones exactas
- Benchmarks RTX 3060 12GB
- Cheatsheet de diagnóstico rápido
- Fuentes comunitarias y creadores de referencia

## Publicar modelo en Civitai

Para subir un checkpoint a la cuenta de Gio (<CIVITAI_USER>) vía navegador:
la API de Civitai es **solo lectura** (no se crea modelo por API), requiere
sesión logueada en el browser (login Google manual) y llenar el formulario
de `/models/create`. Ver `references/civitai-publish-workflow.md`.

## Custom nodes requeridos por workflows Illustrious V38 (Civitai)

El pack "ComfyUI Image Workflows" de Legendaer (V38) usa estos custom nodes;
instalarlos juntos para que el workflow cargue sin "Node type not found":

```bash
cd /f/ComfyUI/custom_nodes
git clone --depth 1 https://github.com/rgthree/rgthree-comfy
git clone --depth 1 https://github.com/yolain/ComfyUI-Easy-Use
git clone --depth 1 https://github.com/kijai/ComfyUI-KJNodes
git clone --depth 1 https://github.com/cubiq/ComfyUI_IPAdapter_plus
git clone --depth 1 https://github.com/ssitu/ComfyUI_UltimateSDUpscale
git clone --depth 1 https://github.com/KohakuBlueleaf/z-tipo-extension   # TIPO
git clone --depth 1 https://github.com/willmiao/ComfyUI-Lora-Manager     # Lora Loader (LoraManager)
git clone --depth 1 https://github.com/crystian/ComfyUI-Crystools
git clone --depth 1 https://github.com/pythongosssss/ComfyUI-Custom-Scripts
# GLSLShader es BUILT-IN de ComfyUI (no requiere repo). Luego:
venv/Scripts/pip install -r <cada repo>/requirements.txt
```

TIPO usa GGUF `TIPO-v2.1-1B-A200M-f16.gguf` (KBlueLeaf) — requiere ComfyUI-GGUF.
**Krea2**: `krea2_turbo_fp8_scaled.safetensors` (~13GB) es el checkpoint propio;
el nodo es `krea2-svdquant`. Modelos Krea2 oficiales en `F:/ComfyUI/models/diffusion_models/`.

## Extraer workflow embebido en imagen

Si el usuario comparte una imagen de Civitai/tensor.art y quiere el workflow,
es casi seguro que está **embebido en el archivo** (chunk PNG `tEXt/workflow`),
aunque la URL diga `.jpeg`. Ver `references/extract-embedded-workflow.md`
para el extractor y las trampas (checkpoints del autor que no tienes, Xet de HF).


## Model Merging (Checkpoint Merger)

Cadena concreta de merges NDREAM que Gio aprobó y sus pesos en
`references/ndream-merge-session.md` (lineage completo + pitfall de disco lleno).


Both ComfyUI and Forge Neo support checkpoint merging, with different levels of control.

### ⚠️ Regla de oro: solo se mezclan arquitecturas iguales

| Arquitectura | Mergeable | Modelos ejemplo |
|-------------|-----------|----------------|
| SD 1.5 + SD 1.5 | ✅ Sí | realisticVision + DreamShaper |
| SDXL + SDXL | ✅ Sí | sd_xl_base + Reijality (Illustrious) |
| SDXL + Pony/Illustrious | ✅ Sí | Misma base SDXL |
| **SDXL + Flux** | **❌ NO** | Arquitectura diferente |
| **SD 1.5 + SDXL** | **❌ NO** | Parámetros distintos |

**⚠️ Fenómeno del archivo que "crece":** Si mezclas arquitecturas distintas (ej: Flux + SDXL), el archivo resultante aumenta de tamaño (ej: 6.9 GB → 7.01 GB) porque el merger arrastra pesos de ambas arquitecturas. Las capas con nombres distintos se agregan completas, las que coinciden (pocas) se mezclan. El resultado es un híbrido que **carga pero genera ruido/basura**. Confirmado por experiencia directa del usuario.

### ⚠️ Forge Neo Merger FALLA con checkpoints fp32 (dict metadata)

El merger nativo de Forge (pestaña Checkpoint Merger / API `modelmerger`) lanza:

```
Error merging checkpoints: argument 'metadata': 'dict' object cannot be converted to 'PyString'
```

cuando cualquier entrada es un checkpoint **fp32 moderno** (metadata en formato dict, ~13-14GB). **Fix:** no usar el merger de Forge para fp32 — usar el script Python `scripts/merge_checkpoints.py` (safetensors+torch, ver más abajo). El merger de Forge sí funciona para fp16 (~6.5GB) clásicos.

El orden conceptual sigue: A es base, B es inyección. M=0.3 = 70% A + 30% B.

### Script Python de merge (recomendado, control total + VAE bake)

`scripts/merge_checkpoints.py` (en este skill) hace merge ponderado de 2-3 modelos, con:
- **Chequeo de arquitectura** antes de mezclar (greppea `model.diffusion_model` = SDXL/Illustrious UNet vs `double_blocks` = Flux DiT).
- **Chequeo de espacio en disco** antes de guardar (cada merge fp32 ~14GB; aborta si no hay).
- **VAE bake opcional**: `VAE = r"F:/Modelos/vae/sdxl_vae.safetensors"` hornea los 248 tensores `first_stage_model.*` en el resultado — así no hay que cargar VAE aparte en Forge/ComfyUI.
- Pesos normalizados a 1.0 (ej. 0.50/0.25/0.25 = base dominante).

```bash
/f/ComfyUI/venv/Scripts/python.exe merge_checkpoints.py
```

**Validar siempre el resultado** (no confiar solo en que terminó):
```bash
/f/ComfyUI/venv/Scripts/python.exe -c "import safetensors.torch as st; t=st.load_file('MERGED_fp32.safetensors',device='cpu'); print(len(t)); print(sum(1 for k in t if k.startswith('first_stage_model')))"
```

### ⚠️ Pitfall: merges de merges degradan + disco lleno

- **Merge ≠ entrenamiento.** La suma ponderada de tensores promedia lo existente, NO crea nada nuevo. Para "entrenar" de verdad hay que hacer un entrenamiento de LoRA/finetune sobre la base (kohya/musubi-tuner). Decírselo al usuario cuando quiera "crear/entrenar".
- **Merges encadenados convergen al promedio**: mezclar modelos que YA son merges de los mismos componentes diluye la identidad de cada uno y los resultados finales se parecen entre sí. Para un modelo final, no encadenar merges de merges — elegir 1 base y quedarse.
- **Cada merge fp32 ~14GB en disco + ~28-42GB RAM** (carga de inputs). Con muchos merges el disco se llena (os error 112 "Espacio en disco insuficiente"). Revisar `df -h /f` antes y liberar intermedios.

### ComfyUI ModelMergeBlocks (más control)

El nodo `ModelMergeBlocks` permite controlar **cada bloque del UNet** individualmente:

```
input  → 0.1  (composición: casi puro A)
middle → 0.3  (iluminación: un poco de B)
out_03 → 0.5  (texturas/detalles: mitad y mitad)
```

Esto evita que B arrastre defectos de anatomía mientras aporta estilo donde importa.

### Técnica: "Base grande + inyecciones progresivas"

Merges concatenados con M decreciente para acumular calidad sin destruir la base:

```
Paso 1: A=SDXL base + B=Reijality M=0.3 → Merge1
Paso 2: A=Merge1 + B=NoobAI M=0.2 → Merge2
Paso 3: A=Merge2 + B=Pony V6 M=0.15 → Merge3
```

Cada iteración inyecta conocimiento sin crecer en GB. Archivo se mantiene en ~7 GB (fp16).

### FP32 como súper-base

Modelos fp32 (~13 GB) preserveran precisión completa. Al mezclar fine-tunes fp16 en base fp32, la base mantiene calidad mientras los fine-tunes aportan información — como RAW vs JPEG. Modelos fp32 SDXL recomendados: **2k Ultimate XL FP32** (12.92 GB), **ULtraReal 2k PONY FP32** (12.92 GB).

## CFG Scale — Control de adherencia al prompt

CFG controla qué tanto el modelo obedece el prompt literal:

| CFG | Comportamiento |
|-----|---------------|
| 1-3 | 🎨 Creativo/suelto — el modelo interpreta |
| 4-6 | ⚖️ Balanceado — sigue el prompt con matices |
| 7-12 | 📏 Estricto — obedece al máximo, puede saturar |
| 13+ | 🔥 Quemado — alto contraste, artefactos |

CFG bajo (2-3) da resultados pictóricos ideales para modelos Illustrious/Reijality.

## MiniMax H3 — Video Generation (RTX 3060 12GB)

### Hardware Reality

| Componente | Archivo | Tamaño | VRAM |
|-----------|---------|--------|------|
| UNet Pruned Q3_K_M GGUF | `MiniMax-H3-FL2VA-Pruned-Q3_K_M.gguf` | 8.9 GB | ✅ Cabe (~3GB libre) |
| Text Encoder Q4_K_M GGUF | `qwen3vl_32b_minimax_h3-Q4_K_M.gguf` | 14.6 GB | ❌ Offloading (96GB RAM ayuda) |
| Video VAE | `minimax_h3_video_vae_fp16.safetensors` | 5.2 GB | ❌ Swap con RAM |
| Audio VAE | `minimax_h3_audio_vae_fp32.safetensors` | 577 MB | ✅ |
| Turbo LoRA | `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | 1.8 GB | ✅ |

**Tiempos esperados** (480p, 124 frames, 3060 12GB + 96GB RAM):

| Config | Pasos | Tiempo |
|--------|-------|--------|
| Draft (Turbo LoRA) | 4 | ~4-5 min |
| Normal (Turbo LoRA) | 6-8 | ~7-10 min |
| Sin Turbo | 20 | ~25 min |

### ⚠️ Critical Fix: `--disable-pinned-memory`

El error más común en 12GB no es VRAM — es **pinned memory**. ComfyUI page-locks buffers de ~2× el tamaño del modelo (hasta 39 GB). En Windows con 32-96GB RAM, esto puede matar el proceso aunque haya VRAM libre. **Siempre usar estos flags para H3:**

```bash
--disable-pinned-memory --fast-disk
```

`--disable-pinned-memory` remueve el buffer page-locked. `--fast-disk` pone pesos en page cache reciclable. Reportes comunitarios muestran que `--fast-disk` solo reduce el pico de RAM residente de ~45 GB a ~12.6 GB.

### Real community data (12GB)

| Fuente | Config | Tiempo | Notas |
|-------|--------|--------|-------|
| Reddit RTX 3060 12GB | 864×480, Turbo 8 steps | **4.5 min** | Mejor tiempo reportado |
| YouTube (Q3KM) | 864×480, 20 steps | ~6-10 min | Benchmark estándar |
| Research compilation | ~0.4MP, 15-20 steps | ~6-10 min | Consenso comunitario |

### Ruta óptima para 12GB

Repositorios: `Abiray/MiniMax-H3-Pruned-GGUF` (UNet), `Abiray/MiniMax-H3-GGUF` (encoder), `Comfy-Org/MiniMax-H3` (VAEs + LoRA). Custom nodes: `ComfyUI-GGUF` + `ComfyUI-MiniMax-H3-Turbo`. Workflow desde Template Library → Video → MiniMax H3, reemplazar loaders por GGUF.

## Technology-Currency Directive

La información técnica tiene fecha de caducidad. Una fuente certificada de 2023 puede estar más obsoleta que un foro de 2026. **Priorizar:**

1. Documentación oficial actual (2025-2026) 🥇
2. Guías comunitarias de alta reputación recientes 🥇
3. Benchmarks independientes con fecha explícita 🥇
4. Documentación oficial de 2023-2024 🥈 (verificar cambios)
5. Tutoriales/blogs < 2024 🥉 (verificar con fuentes actuales)

**Señales de alerta:** menciones a PyTorch < 2.0, `--medvram` como estándar, "no se puede correr Flux en 12GB", guías que no mencionan Dynamic VRAM.

Archivo completo en Obsidian: `Memorias/Agente/Directiva-Vigencia-Tecnologica.md`.

## Verification Checklist

- [ ] ComfyUI arranca: `curl http://localhost:8188/system_stats` → JSON
- [ ] Forge arranca: `curl http://localhost:7860/` → HTML
- [ ] Modelos visibles en ambos UIs
- [ ] Generación de prueba funciona (SDXL 1024², ~25s en RTX 3060)