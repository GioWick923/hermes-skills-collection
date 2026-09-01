---
name: character-ref-sheet-krea
description: Character reference sheet pipeline for Krea2.
version: 1.0.0
author: Hermes Agent
license: internal
metadata:
  tags: [krea2, comfyui, character-sheet, pipeline]
  related_skills: []
---

## When to Use
Use when Gio wants to generate a **professional CHARACTER REFERENCE SHEET** (9-section character/model reference board) from a reference image, using Krea2 in ComfyUI. Based on the viral prompt by @meAsifAi (Krea AI + ChatGPT 2.0).

## Qué produce
Una board de 9 secciones de un personaje, con consistencia de identidad total:
1. FULL BODY (front, side, back, 3/4 front, 3/4 back)
2. FACE (front, profile, 45°, from above, from below)
3. EXPRESSIONS (neutral, smiling, serious, surprised, shy, worried, thinking, sad, calm)
4. DETAILS (eyes, brows, nose, mouth, ears, jawline, skin, hands)
5. HAIR (bangs, side, back, ends, flow)
6. HAIR & FACE different angles
7. FEATURE NOTES (black bob, thin bangs, small face, fair skin, slim figure, natural skin)
8. COLOR SWATCHES (hair, eyes, skin, lips, clothing, shadow)
9. FIXED POINTS (face shape, black bob, skin texture, outfit, body type, age fixed)

## Workflow de ComfyUI
- Archivo: `F:/ComfyUI/user/default/workflows/Character_Ref_Sheet_Gio.json`
- Checkpoint: `krea2_turbo_fp8_scaled.safetensors`
- Resolución recomendada: 1152x1536 (retrato, alta res)
- Sampler: dpmpp_2m, steps 20, CFG 4.5, denoise 0.9

## Prompt positivo (clave, humanizado)
```
professional CHARACTER REFERENCE SHEET, 9 section layout, same character identity across all panels,
white neutral background, thin gray borders, organized rectangular panels, clean studio lighting,
high-detail photography. FULL BODY (front, side, back, 3/4 front, 3/4 back). FACE (front, profile, 45°,
above, below). EXPRESSIONS (neutral, smiling, serious, surprised, shy, worried, thinking, sad, calm).
DETAILS (eyes, brows, nose, mouth, ears, jawline, skin, hands). HAIR (bangs, side, back, ends, flow).
COLOR SWATCHES (hair, eyes, skin, lips, clothing, shadow). professional AI character turnaround,
high facial consistency, clean editorial presentation, English text only
```

## Prompt negativo
```
blurry, low quality, deformed, distorted anatomy, extra limbs, watermark, logo, chinese, japanese,
korean text, captions, messy layout, inconsistent character, extra details, cluttered
```

## Para mantener consistencia con una imagen de referencia
Para lograr que el personaje sea SIEMPRE el mismo, añadir un **IPAdapter** con la imagen de referencia:
- Nodo: IPAdapterAdvanced (de ComfyUI_IPAdapter_plus, instalado)
- Modelo: `noobIPAMARK1_mark1.safetensors` (ya descargado)
- CLIP Vision: `CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors` (ya descargado)
- Conexión: IMAGE de LoadImage → IPAdapter; ipadapter_model → IPAdapterModelLoader; clip_vision → CLIPVisionLoader; MODEL del checkpoint → IPAdapter; salida IPAdapter → KSampler
- Peso IPAdapter ~0.8, start 0.1, end 1.0

## Pasos de uso
1. Coloca tu imagen de referencia como `ref_image.png` en la carpeta input de ComfyUI (o usa LoadImage).
2. Abre `Character_Ref_Sheet_Gio.json` en ComfyUI.
3. (Opcional para consistencia) conecta el IPAdapter con la imagen de referencia.
4. Queue Prompt.
5. Revisa que las 9 secciones estén presentes y el personaje sea consistente.

## Pitfalls
- La firma exacta de IPAdapterAdvanced varía por versión. Si da "input not found", revisar los nombres de inputs de la versión instalada.
- Resoluciones muy altas (2048+) pueden fallar en RTX 3060 12GB; usar 1152x1536 y upscale después.
- Krea2 Turbo usa 8-20 steps; 20 con CFG 4.5 da buen detalle sin sobreprocesar.
- El texto sale mejor en inglés (el modelo maneja inglés; evita CJK).
