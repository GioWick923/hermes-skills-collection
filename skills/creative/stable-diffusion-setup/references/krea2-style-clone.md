# Clon de imagen con Krea2 (sin auth de ComfyAPI)

**Fecha**: 2026-09-02 | **Usuario**: Gio | **Contexto**: Clonar referencia con variación mínima

## Problema
El nodo `Krea2StyleReferenceNode` requiere credenciales de ComfyAPI:
- `auth_token_comfy_org` (hidden input)
- `api_key_comfy_org` (hidden input)

Si no hay auth configurada, el nodo falla silenciosamente o requiere login manual.

## Solución: UNETLoader + denoising controlado

### Workflow alternativo (sin auth)
```python
{
  "1": {"class_type": "UNETLoader", "inputs": {
    "unet_name": "krea2_turbo_fp8_scaled.safetensors",
    "weight_dtype": "default"
  }},
  "2": {"class_type": "CLIPLoader", "inputs": {
    "clip_name": "qwen3vl_4b_fp8_scaled.safetensors",
    "type": "krea2"
  }},
  "3": {"class_type": "VAELoader", "inputs": {
    "vae_name": "qwen_image_vae.safetensors"
  }},
  "4": {"class_type": "CLIPTextEncode", "inputs": {
    "text": "<prompt describiendo la referencia>",
    "clip": ["2", 0]
  }},
  "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
  "6": {"class_type": "LoadImage", "inputs": {"image": "reference.jpg", "type": "input"}},
  "7": {"class_type": "VAEEncode", "inputs": {"pixels": ["6", 0], "vae": ["3", 0]}},
  "8": {"class_type": "KSampler", "inputs": {
    "model": ["1", 0],
    "seed": <semilla>,
    "steps": 8,
    "cfg": 1.0,
    "sampler_name": "euler",
    "scheduler": "simple",
    "positive": ["4", 0],
    "negative": ["5", 0],
    "latent_image": ["7", 0],
    "denoise": 0.45  # <-- CLAVE: baja denoising = mínima variación
  }},
  "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
  "10": {"class_type": "SaveImage", "inputs": {
    "images": ["9", 0],
    "filename_prefix": "krea2_clone"
  }}
}
```

### Parámetros validados
| Parámetro | Valor | Efecto |
|-----------|-------|--------|
| `denoise` | **0.45** | Variación mínima, preserva composición/pose/ropa |
| `steps` | 8 | Rápido para Turbo distillado |
| `cfg` | 1.0 | Modelo distilled — cfg alto quema |
| `sampler` | euler | Funciona bien con scheduler simple |

### Limitaciones de este approach
1. **No replica rostro exacto** — Krea2 genera personas nuevas
2. **Sí preserva**: pose, composición, ropa, colores, fondo, iluminación general
3. **Prompt debe describir referencia** — la IA no "ve" la imagen sin text encoder descriptivo

### Para auth de ComfyAPI (cuando esté disponible)
```bash
# Login manual en ComfyUI Manager o vía CLI:
comfy login
# O configurar en nodos Krea2 como inputs ocultos
```

## Recursos
- Modelos locales: `F:/ComfyUI/models/diffusion_models/krea2_turbo_fp8_scaled.safetensors`
- Text encoder: `F:/ComfyUI/models/text_encoders/qwen3vl_4b_fp8_scaled.safetensors`
- VAE: `F:/ComfyUI/models/vae/qwen_image_vae.safetensors`

## Sesión previa
- `references/krea2-setup.md` — instalación y configuración
- `references/krea2-workflow-adaptation.md` — adaptación de workflows comunitarios
