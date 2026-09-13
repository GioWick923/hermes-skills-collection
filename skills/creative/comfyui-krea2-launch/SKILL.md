---
name: comfyui-krea2-launch
description: Use when launching ComfyUI or generating Krea2 images.
---

# Lanzar ComfyUI + generar imagen con Krea2 (RTX 3060 12GB)

## 1. Lanzar el servidor

```bash
# terminal(background=true) — SIN --dont-print-server (causa error tqdm
# 'Invalid argument' en KSampler en Windows). SIN --medvram (obsoleto).
cd F:/ComfyUI && venv/Scripts/python.exe main.py --listen --port 8188 --disable-auto-launch
```

- Arranca en ~8s. Verificar: `curl http://127.0.0.1:8188/system_stats` → VRAM ~11GB libre.
- Si el puerto responde pero history no registra prompts, el server viejo sigue vivo: matar python (usar `taskkill /F /PID <pid>` en cmd, `//F` falla en git-bash) y relanzar.

## 2. Modelos correctos (12GB VRAM)

| Rol | Archivo | Carpeta |
|---|---|---|
| DiT (RECOMENDADO) | `Krea2-Turbo-SVDQuant-W4A4-rank256-actaware.safetensors` (9.2GB) | `models/diffusion_models/` |
| DiT alternativo | `krea2_turbo_fp8_scaled.safetensors` (13GB, más lento) | `models/diffusion_models/` |
| CLIP | `qwen3vl_4b_fp8_scaled.safetensors` | `models/text_encoders/` |
| VAE | `qwen_image_vae.safetensors` | `models/vae/` |
| LoRA | `krea2_turbo_4step_rank_64_lora.safetensors` (418MB) | `models/loras/` |

## 3. Workflow API (formato exacto que funciona)

CRÍTICO:
- SVDQuant usa **Krea2SVDQuantW4A4Loader** (NUNCA UNETLoader con este modelo).
- Latent: **EmptySD3LatentImage** (no EmptyLatentImage).
- KSampler: steps 4, **cfg 1.0**, euler, scheduler **simple** ("normal" genera ruido), **denoise 1.0** explícito (si falta → error de validación).
- Positive = CLIPTextEncode directo. Negative = **ConditioningZeroOut**(positive) — Krea2 Turbo es cfg-distilled, el negativo real se ignora.
- Links SIEMPRE `"node_id"` string + slot: `["2", 0]`. Un link `[5]` solo → error 400 'length-2 list'.
- CLIPLoader type: `"krea2"`.

```json
{
  "1": {"class_type": "Krea2SVDQuantW4A4Loader", "inputs": {"model_name": "Krea2-Turbo-SVDQuant-W4A4-rank256-actaware.safetensors", "vram_management": "auto"}},
  "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
  "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
  "4": {"class_type": "CLIPTextEncode", "inputs": {"text": "<prompt>", "clip": ["2", 0]}},
  "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
  "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 768, "height": 768, "batch_size": 1}},
  "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "seed": 999999, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0], "denoise": 1.0}},
  "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
  "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "salida"}}
}
```

Workflow oficial de referencia: `F:/ComfyUI/custom_nodes/krea2-svdquant/workflows/krea2_turbo_svdquant_w4a4_t2i.json`.

## 4. Enviar y verificar

```python
r = requests.post('http://127.0.0.1:8188/prompt', json={'prompt': workflow})  # 200 = encolado, 400 = ver r.text
# Poll: GET /queue hasta queue_running == [] (~50s para 768x768 4 pasos)
# Luego: GET /history → status 'success' + outputs[].images[].filename
# Archivo: F:/ComfyUI/output/<filename_prefix>_00001_.png  (~610KB)
# Verla: vision_analyze(file:///F:/ComfyUI/output/...)
```

Si status es 'error': leer `history/<pid>` → messages[-1]['execution_error'] trae traceback completo.

## 5. Diagnóstico rápido de errores vistos

- **KSampler 'Invalid argument'** al arrancar con flags de silencio → relanzar sin `--dont-print-server`.
- **Imagen de ruido blanco** → scheduler era 'normal' o se usó UNETLoader con SVDQuant. Usar 'simple' + Krea2SVDQuantW4A4Loader.
- **400 'length-2 list'** → links mal formateados.
- **400 'denoise missing'** → agregar `denoise: 1.0` al KSampler.
- **'string index out of range' en KSampler** → negative era texto plano en vez de ConditioningZeroOut.
- **SVDQuant lento** → PyTorch 2.5.1+cu121 cae a fallback Python; ideal cu130+ + triton-windows (pendiente, no bloquea).
## 6. Face Clone / Style Reference (img2img)

Para clonar un rostro específico (ej: Angelina Jolie) sobre una imagen de referencia.

### Método ÚNICO que funciona: VAEEncode + img2img
El IPAdapter FaceID y Krea2ImageNode fallan en este setup (error de logging tqdm, backend CUDA no disponible con torch 2.5.1+cu121).

1. Copiar imagen ref a `F:/ComfyUI/input/` (es `C:\Users\<USER>\Pictures\modelos imag\` la carpeta de origen)
2. Workflow:

```json
{
  "1": {"class_type": "Krea2SVDQuantW4A4Loader", "inputs": {"model_name": "Krea2-Turbo-SVDQuant-W4A4-rank256-actaware.safetensors", "vram_management": "auto"}},
  "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
  "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
  "4": {"class_type": "CLIPTextEncode", "inputs": {"text": "Angelina Jolie face, green almond eyes, high cheekbones, full lips, pale skin, dark hair, <DESCRIBIR_ESCENA_COMPLETA>", "clip": ["2", 0]}},
  "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
  "6": {"class_type": "LoadImage", "inputs": {"image": "<NOMBRE_ARCHIVO>"}},
  "7": {"class_type": "VAEEncode", "inputs": {"pixels": ["6", 0], "vae": ["3", 0]}},
  "8": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "seed": 987654, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["7", 0], "denoise": 0.75}},
  "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
  "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": "angelina_face"}}
}
```

3. ARCHIVO CLAVE: guardar workflow como JSON en `C:/Users/<USER>/Downloads/`. Siempre enviar con POST a `http://127.0.0.1:8188/prompt` desde execute_code o terminal.
4. VERIFICAR: GET `/queue` hasta vacío, luego `/history` y chequear `status.success` + `outputs[node_id].images[]`. Archivo en `F:/ComfyUI/output/`.
5. MOSTRAR resultado con `vision_analyze(file:///F:/ComfyUI/output/...)` y luego `MEDIA:/path`

### Pitfalls
- **Error 'OSError: [Errno 22]' en KSampler**: bug de tqdm+colorama+ComfyUI-Manager al interceptar stdout. NO parchear archivos manualmente — la indentación se rompe. Workaround: reiniciar ComfyUI con `powershell Start-Process` (no `start /B` desde git-bash). Si persiste, el logger se corrompió y hay que restaurar `app/logger.py` y `k_diffusion/sampling.py` desde git.
- **NO usar Krea2ImageNode** con el modelo SVDQuant local: pide argumento 'model' de tipo COMFY_DYNAMICCOMBO_V3 (API cloud), incompatible con nuestro setup.
- **NO cambiar EmptySD3LatentImage por EmptyLatentImage** con Krea2.
- **NO olvidar denoise explícito**: si falta, ComfyUI da error de validación.
- **Prompt debe describir AMBOS**: el rostro Angelina + toda la escena de la ref. Si solo pones el rostro, la escena se pierde.
- **VRAM**: ~12GB total, ~2.3GB libre después de cargar modelo. Funciona para 768x768, 768x1024 puede fallar.

### Cómo arrancar ComfyUI
Solo funciona con PowerShell:
```bash
powershell -Command "Start-Process -NoNewWindow ..."
```
Cualquier `start /B` desde git-bash falla silenciosamente (el proceso no escucha en ningún puerto).
