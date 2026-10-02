---
name: tk-toolkit-workflow
description: Use when creating ComfyUI workflows with TK Toolkit.
---
# TK Toolkit Workflow

> **Instalación verificada 2026-09-13**: `F:/ComfyUI/custom_nodes/comfyui-anima-toolkit/` · ComfyUI en `F:/ComfyUI` puerto 8188. Deps: `aiohttp>=3.9`, `requests>=2.31` (ya en el venv).

## Nombres REALES de nodos en /object_info (API)

| Nodo UI | class_type API | Categoría |
|---|---|---|
| TK Batch LoRA Loader | `TK Batch LoRA Loader` | TK/loaders |
| TK 3D Body Camera | `TK 3D Body Camera` | TK/camera |
| TK Prompt Batch | `TK Prompt Batch` | TK/batch |
| TK Prompt Cards | `TKPromptCards` | TK/prompt |
| TK Trigger Words | `TK Trigger Words` | TK/loaders |
| TK String Router | `TK String Router` | TK/text |
| TK Text Join | `TK Text Join` | TK/text |
| TK Image Select | `TK Image Select` | TK/image |
| Lighting Prompt | `AnimaTKLightingPrompt` | TK/prompt |
| Prompt Saver | `AnimaTKPromptSaver` | TK/prompt |
| Danbooru Tag Getter | `AnimaTKDanbooruTagGetter` | TK/Danbooru |
| Clothing Draw | `AnimaClothingDraw` | TK/prompt |
| Empty Latent (5D) | `AnimaPresetEmptyLatent` | TK/latent |

⚠️ Los nombres con espacios van URL-encodados en la API (`TK%20Batch%20LoRA%20Loader`).
⚠️ NO existe nodo "TK Camera Control" (retirado) ni "TK Danbooru Gallery" como nodo API — la galería Danbooru es solo widget/panel.

## Schema verificado — TK Batch LoRA Loader

```json
{"class_type": "TK Batch LoRA Loader", "inputs": {
  "model": ["<ckpt_node>", 0],
  "lora_syntax": "<lora:nombre:0.8> <lora:otro:0.6>",
  "clip": ["<ckpt_node>", 1],
  "output_trigger_words": true
}}
```
Outputs: `MODEL` (0), `CLIP` (1), `STRING/trigger_words` (2).

## Flujo de trabajo estándar (cuando el usuario pide un trabajo)

1. **Desglosar el pedido**: estilo (fotorreal/anime), personaje, escena, composición, LoRAs candidatos.
2. **Cadena base**: CheckpointLoader → `TK Batch LoRA Loader` (lora_syntax con pesos) → KSampler → VAEDecode → SaveImage.
3. **Trigger words**: output STRING del loader → concatenar con prompt vía `TK Text Join` o string directo.
4. **Prompt batch (multi-imagen)**: escribir archivo `input/prompts/*.txt` con bloques `## 组1 · título` + línea opcional `相机: from side`, conectar `TK Prompt Batch` al positive del sampler.
5. **Latent**: usar `AnimaPresetEmptyLatent` para Anima/Cosmos; para Krea2/SDXL usar EmptySD3LatentImage/EmptyLatentImage según modelo.
6. **Cámara**: `TK 3D Body Camera` → output `camera_prompt` para framing consistente.
7. **Panel de gestión**: `http://127.0.0.1:8188/extensions/ComfyUI-Anima-Batch-LoRA/app/` (verificado HTTP 200) — gestión visual de LoRAs (SHA256 match Civitai), prompt library, outputs gallery, Danbooru.

## Verificación post-instalación (ya ejecutada 2026-09-13)

- [x] 1845 nodos totales, 32 con TK/Anima registrados
- [x] 20 extensiones JS cargadas en `/extensions`
- [x] Panel app responde 200
- [x] Schema del Batch LoRA Loader validado vía `/object_info`

## Regla de oro
Cuando el usuario pida un trabajo de ComfyUI: invocar esta skill PRIMERO, desglosar el flujo completo (checkpoint → LoRAs → prompts → sampler → output), y ejecutar vía API `POST http://127.0.0.1:8188/prompt` con los class_type de la tabla superior.

## PRUEBA DE INTEGRACIÓN REAL (2026-09-13, Bayonetta selfie Krea2) ✅

El `TK Batch LoRA Loader` funciona **en cadena con Krea2 SVDQuant** sin modificaciones:

```json
{"10": {"class_type": "TK Batch LoRA Loader", "inputs": {
  "model": ["1", 0],
  "lora_syntax": "<lora:krea2_turbo_4step_rank_64_lora:1.0>"
}}}
```
- KSampler `model` apunta a `["10", 0]` (salida MODEL del TK loader). Sin error, genera igual que LoraLoaderModelOnly.
- No soporta `clip` opcional conectado en este test — funciona solo con `model` (CLIP va directo del CLIPLoader al CLIPTextEncode).
- Workflow probado completo: SVDQuant loader → TK Batch LoRA → KSampler(4 steps, cfg 1.0, euler/simple) → VAEDecode → SaveImage. 768² en ~70s.
- Fallback si TK loader diera error en algún workflow: `LoraLoaderModelOnly` con `strength_model` (mismo resultado).

## REGLA DEL USUARIO (corrección 2026-09-13, OBLIGATORIA)

**SIEMPRE que se use Krea2 → el LoRA turbo 4-step va en el workflow. Sin excepción.**

Además: el TK Batch LoRA Loader acepta MÚLTIPLES LoRAs en un solo nodo — para personajes/estilos
encadenarlos junto al turbo en el mismo `lora_syntax`:

```
<lora:krea2_turbo_4step_rank_64_lora:1.0> <lora:personaje_x:0.8> <lora:estilo_y:0.6>
```

- El turbo SIEMPRE a strength 1.0 (es el que permite 4 steps).
- Los LoRAs de personaje/estilo con pesos 0.5–0.9 según cuánta identidad aporten.
- Buscar LoRAs candidatos en `F:/ComfyUI/models/loras/` (o consultar `/object_info` → LoraLoaderModelOnly options).
- Si el usuario pide un personaje con LoRA disponible, usarlo; si no existe, lograr el parecido por prompt.

## Lecciones de generación Krea2 (aplicar siempre)
- Consultar `/object_info` para filenames EXACTOS antes de armar el workflow (no hardcodear).
- Poll de resultado: `GET /history/{pid}` hasta `status.completed` (~70s para 768² 4 steps en 3060).
- Selfies: el modelo pone el teléfono al revés (se ve la cámara trasera) — artifact típico; para evitarlo prompt "holding phone in front of her face, screen visible" o recortar la mano.