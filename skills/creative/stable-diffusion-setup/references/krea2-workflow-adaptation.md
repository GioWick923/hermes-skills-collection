# Adaptación de workflow Krea2 comunitario — easyKREA2WorkflowLORA_v4 (sesión 2026-09-01)

Adaptación de un workflow Krea2 de Civitai (`easyKREA2WorkflowLORA_v4.json`, formato editor,
132KB, 84 nodos, 387 node_ids) para el setup local: RTX 3060 12GB, ComfyUI 0.33.0,
modelos FP8 en `F:/Modelos/` con junctions + `extra_model_paths.yaml`.

## Anatomía del workflow (para reconocerla en otros)

- **Componentes embebidos (UUID nodes)**: 3 nodos con type UUID definidos en
  `definitions.subgraphs`:
  - `527064ad-...` (id 254): UNETLoader + CLIPLoader + VAELoader (6 widgets: unet_name,
    weight_dtype, clip_name, type, device, vae_name).
  - `b645a6b8-...` (id 207): igual + EmptyLatentImage (width/height/batch_size) →
    outputs MODEL/CLIP/VAE/LATENT.
  - `eddf9fb8-...` (id 351): DOBLE UNET + merge value (Checkpoint Merger embebido) →
    outputs MODEL/VAE/LATENT/CLIP.
- **Samplers**: `ClownsharKSampler_Beta` ×2 por variante (Pass1 + Pass2):
  - Pass 1: eta 0.5, sampler `linear/euler`, scheduler `beta`, steps 6, cfg 1.0, denoise 1.0
  - Pass 2: eta 0.5, sampler `exponential/res_2s`, scheduler `bong_tangent`, steps 2, denoise 0.3
  (I2I: denoise 0.35 en ambos).
- **Variantes (grupos)**: V1 = single model txt2img; V2 = +Prompt Enhancer (TextGenerate);
  V3 = I2I (LoadImage → upscale → VAEEncode); V4 = Checkpoint Merger (2 modelos).
  Nota del autor: activar SOLO UNA variante a la vez (Fast Groups Bypasser).
- **Upscale**: 4x-UltraSharp.pth → ImageUpscaleWithModel → ImageScale 1440×2160 bilinear.
- **Prompts**: los CLIPTextEncode positive YA traen el prompt escrito (el TextGenerate es
  enhancer opcional). Negative es bypass por defecto (Krea2 es distilled, cfg 1.0).

## Instalaciones necesarias

```bash
# RES4LYF (ClownsharKSampler_Beta) — ~2.1s de import, 279 files
cd /f/ComfyUI/custom_nodes && git clone --depth 1 https://github.com/ClownsharkBatwing/RES4LYF
/f/ComfyUI/venv/Scripts/python.exe -m pip install -r RES4LYF/requirements.txt

# 4x-UltraSharp.pth (67MB) — lokCX/4x-Ultrasharp en HF
curl -sL --fail -o F:/Modelos/upscale_models/4x-UltraSharp.pth \
  "https://huggingface.co/lokCX/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth"
mkdir -p F:/ComfyUI/models/upscale_models   # copia física si no aparece en /object_info
cp F:/Modelos/upscale_models/4x-UltraSharp.pth F:/ComfyUI/models/upscale_models/
```

## Mapeo de modelos aplicado (10 reemplazos en widgets_values)

| Workflow pide (BF16) | Usado (FP8 local) |
|---|---|
| `Krea2\Krea2_Turbo_BF16.safetensors` | `krea2_turbo_fp8_scaled.safetensors` |
| `Krea2_qwen3vl_4b_bf16.safetensors` | `qwen3vl_4b_fp8_scaled.safetensors` |
| `KREA2_qwen_image_vae.safetensors` | `qwen_image_vae.safetensors` |
| `Krea2\Krea2_DarkBeast30BF16INT8.safetensors` | (no existe → placeholder FP8; V4 merge requiere 2 modelos reales distintos) |

Método: cargar JSON editor, recorrer `nodes[].widgets_values` y reemplazar strings
exactos del mapa. Los restos BF16 en MarkdownNote/Note son texto informativo — ignorar.

## Errores API encontrados y fixes (validados con ejecución real)

1. **`sampler_mode: 'randomize' not in [...]`** (HTTP 400 value_not_in_list):
   el editor guarda `randomize`/`fixed` como control de seed; la API solo acepta
   `['unsample','standard','resample']`. Fix: `sampler_mode="standard"` y seed aparte
   (Pass1: seed del widget, ej. 720079729677161; Pass2: -1).
2. **`ImageUpscaleWithModel: required_input_missing upscale_model`**:
   el input se llama `upscale_model` (no `model`).
3. **Parse de combos `/object_info`**: estructura real es
   `{"model_name": ["COMBO", {"multiselect": false, "options": [...]}]}` →
   leer `[1]["options"]`. Leer `[0]` devuelve el literal "COMBO" y confunde.
4. **Upscaler invisible**: `extra_model_paths.yaml` mapeaba `upscale_models: upscale_models`
   pero el server devolvía options vacío. Fix real: copia física a `F:/ComfyUI/models/upscale_models/`
   (reiniciar server tras copiar; el escaneo de modelos ocurre al arrancar).

## Workflows API reconstruidos (validados, ~4-5 min cada uno en 3060 lowvram)

**V1 txt2img (260s)** — UNETLoader(krea2_turbo_fp8_scaled) + CLIPLoader(qwen3vl_4b_fp8_scaled,
type=krea2) + VAELoader(qwen_image_vae) → 2× CLIPTextEncode (pos/neg) →
EmptyLatentImage(1440×2160) → ClownsharK Pass1 (seed 720079729677161) →
Pass2 → VAEDecode → SaveImage.

**V3 I2I (290s)** — LoadImage(v1_final.png subida vía POST /upload/image) →
UpscaleModelLoader(4x-UltraSharp) → ImageUpscaleWithModel(**upscale_model**) →
ImageScale(1440×2160) → VAEEncode → Pass1+Pass2 (denoise 0.35, seed 23434846479952) →
VAEDecode → SaveImage. Prompt del autor: "asian woman, blonde hair."

**V1+Upscaler default (270s)** — V1 + UpscaleModelLoader → ImageUpscaleWithModel →
ImageScale 1440×2160 → SaveImage (la config dejada como default).

## Timings RTX 3060 12GB (--lowvram --disable-pinned-memory, torch 2.5.1+cu121)

| Workflow | Resolución | Tiempo |
|---|---|---|
| Smoke test FP8 template (8 steps) | 768×768 | ~75s |
| V1 txt2img (6+2 steps Clownshark) | 1440×2160 | ~260s |
| V3 I2I (con upscale 4x) | 1440×2160 | ~290s |
| V1+Upscaler default | 1440×2160 | ~270s |

## Dejar variante default en JSON editor

Cadena V1+Upscaler activa = ids {116,117,121,123,124,125,126,127,128,189,207}
(loader 207 da MODEL/CLIP/VAE/LATENT a 128 LoRA y 121 VAE; 128 → 116/117 prompts → 123/124
samplers → 121 decode → 126 upscale(+125) → 127 scale → 189 save).
- Nodos de la cadena → `"mode": 0`; resto ejecutables → `"mode": 4`; notas/UI intactas.
- Verificación BFS: ningún nodo activo puede depender de uno bypassed (chequear inputs
  con link a nodo mode!=0).
- Copiar a `F:/ComfyUI/user/default/workflows/` para que aparezca en Workflow → Open.

## Notas de confianza

- El flujo completo quedó VERIFICADO con 3 generaciones reales (V1, V3, V1+Upscaler),
  no solo con validación de schema.
- Los componentes UUID cargan bien en el UI de ComfyUI 0.33 (feature subgraphs nativa);
  si un usuario los abre en versión más vieja, "Unpack Subgraph" los convierte a nodos normales
  (dice el MarkdownNote "Settings Node" del propio workflow).
