---
name: krea2-face-swap-workflow
description: Krea2 celebrity face-swap workflow with denoise strategy.
---

# Krea2 Face Swap Workflow

Procedimiento para generar face-swaps realistas usando Krea2 SVDQuant con RTX 3060 12GB.

## Cuándo Usar

- El usuario quiere clonar un rostro específico (celebridad) sobre una imagen de referencia
- Se requiere preservar pose y outfit exactos de la imagen base
- El resultado debe parecer foto real (no ilustración AI)

## Procedimiento

### 1. Preparar Referencias

**Base/Reference Image** (pose, outfit, setting):
- Debe ser imagen JPG/PNG en `F:/ComfyUI/input/<nombre>.jpg`
- Verificar que existe antes de usar: `test -e "F:/ComfyUI/input/<nombre>.jpg"`

**Face Reference Image** (para describir el rostro):
- Buscar en web: `ddgs images -q "<celebrity> portrait authentic" -m 10`
- Descargar 2-3 fotos reales del sujeto
- Usar `vision_analyze` para confirmar que son fotos REALES (no AI-generated)

### 2. Workflow API

```json
{
  "1": {"class_type": "Krea2SVDQuantW4A4Loader", "inputs": {"model_name": "Krea2-Turbo-SVDQuant-W4A4-rank256-actaware.safetensors", "vram_management": "auto"}},
  "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
  "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
  "4": {"class_type": "CLIPTextEncode", "inputs": {"text": "<FACE_DESC>+<SCENE_DESC>", "clip": ["2", 0]}},
  "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
  "6": {"class_type": "LoadImage", "inputs": {"image": "<BASE_FILENAME>"}},
  "7": {"class_type": "VAEEncode", "inputs": {"pixels": ["6", 0], "vae": ["3", 0]}},
  "8": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "seed": <SEED>, "steps": 6, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["7", 0], "denoise": <DENISOISE>}},
  "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
  "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": "<PREFIX>"}}
}
```

### 3. Denoise Strategy

| Objetivo | Denoise | Steps | Resultado Esperado |
|----------|---------|-------|-------------------|
| Preservar pose exacta | 0.05-0.25 | 4-6 | Estructura perfecta, rostro genérico AI |
| Balance realismo/estructura | 0.55-0.70 | 6-8 | Good likeness + pose preserved |
| Full style transfer | 0.80+ | 6-8 | Anime→Real, pierde pose original |

**RECOMMENDED**: denoise 0.65-0.75 para mejor balance entre parecido facial y preservación de pose.

### 4. Prompt Formula

**Para celebrity face swaps**, el prompt debe incluir:

1. **Face description**: "<Name> face, <hair_color> <hair_style> hair, <eye_color> eyes, <freckles/moles>, <specific_features>"
2. **Camera/photography terms**: "Canon EOS R5 85mm f/1.4", "RAW photograph", "natural lighting"
3. **Scene description**: outfit, setting, pose details

Ejemplo:
```
Sadie Sink, strawberry-blonde wavy hair, blue-green eyes, freckles across nose, natural makeup, photorealistic skin texture, Canon EOS R5 85mm f/1.4, professional portrait photography, white blue raglan top, white pants, sunny forest background
```

### 5. Debug Pattern: Verificar Salida

**CRITICAL**: SIEMPRE verificar `/history` antes de asumir rutas de archivos:

```python
h = requests.get('http://127.0.0.1:8188/history').json()
for pid, data in sorted(h.items(), key=lambda x: x[1].get('execution_start', 0), reverse=True)[:10]:
    st = data.get('status', {}).get('status_str', '?')
    for nid, nd in data.get('outputs', {}).items():
        if isinstance(nd, dict) and 'images' in nd:
            for img in nd['images']:
                print(f"{img.get('filename', '?')}")
```

**ERROR COMÚN**: Asumir que `filename_prefix + "_00001_.png"` existe sin verificar el historial primero.

### 6. Copiar a Destino

Una vez confirmado el nombre real del archivo:
```python
import shutil
src = f'F:/ComfyUI/output/<real_filename>.png'
dst = f'C:/Users/<USER>/Pictures/modelos imag/<name>.png'
shutil.copy(src, dst)
```

## Pitfalls

- **Krea2StyleReferenceNode** puede estar disponible pero no funciona correctamente con SVDQuant local; usar descripción textual del rostro en vez.
- **Insightface falla** en imágenes anime/semi-real; nunca intentar face clone directo desde base ilustración.
- **Piel plástica**: Krea2 SVDQuant alcanza máximo ~6/10 realismo fotográfico por defecto. Para más realismo, usar denoise 0.65-0.75 + términos "RAW photograph", "skin pores visible", "no retouching".
- **Rótulos con espacios**: evitar labels como "v1 skin texture" en filename_prefix; usar formato simple "v1_skin" para evitar errores de path.
- **Rate limiting DuckDuckGo**: después de varias búsquedas rápidas, puede bloquear. Esperar 5-10 segundos entre searches o usar fuentes alternativas (Wikipedia Commons con User-Agent header).

## Referencias

- Skill principal: `comfyui-krea2-launch`
- Modelo: `Krea2-Turbo-SVDQuant-W4A4-rank256-actaware.safetensors` en `models/diffusion_models/`
- LoRA turbo: `krea2_turbo_4step_rank_64_lora.safetensors` en `models/loras/`
