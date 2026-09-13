---
name: face-clone-imagegen
description: Use when cloning a face onto another image via img2img.
---

# Face clone por imagen (identity transfer en generación local)

## Regla del usuario (SIEMPRE)

El rostro se clona con IMAGEN: detectar → alinear por landmarks → pegar → integrar. NUNCA describir el rostro en el prompt — descripción textual produce parecidos genéricos y artefactos (texto garabateado en ropa). El prompt de todo el pipeline se reduce a `"photorealistic"`.

## Pipeline (3 pasos, validado RTX 3060 12GB)

1. **ESCENA/CUERPO** — img2img de la imagen de referencia en Krea2: LoadImage → VAEEncode → KSampler (denoise 0.75, steps 4, cfg 1.0, euler/simple, prompt `photorealistic`) → VAEDecode → SaveImage. El rostro que salga es la fuente del clon. Workflow base: skill `comfyui-krea2-launch` §3 (cambiar EmptySD3LatentImage por LoadImage+VAEEncode).
2. **CLON** — `scripts/face_clone.py SRC DST OUT`
   - SRC = imagen con el rostro a clonar; DST = imagen con el cuerpo destino; OUT = compuesto en `F:/ComfyUI/input/`.
   - Setup (una vez): `F:/ComfyUI/venv/Scripts/python.exe -m pip install insightface onnx` (pesos buffalo_l se descargan solos).
3. **INTEGRACIÓN** — img2img final sobre el compuesto: denoise **0.25**, prompt `photorealistic`. Unifica piel/luces sin cambiar estructura.

Ajustes finos y parámetros: `references/face-clone.md`.

## Pitfalls (qué NO usar)

- **Krea2StyleReferenceNode NO sirve para face swap**: su salida KREA_STYLE_REF no la consume KSampler ni ningún otro nodo (solo se encadena entre StyleReferenceNodes) — es decorativo. Parecido aparente = venía del texto del prompt.
- **IPAdapterFaceID / InstantID**: nodos SD1.5/SDXL-only, incompatibles con el DiT Krea2 SVDQuant — no perder tiempo ahí.
- **Krea2ImageNode**: pide COMFY_DYNAMICCOMBO_V3 (API cloud), incompatible con setup local.
- Copiar siempre las imágenes de trabajo a `F:/ComfyUI/input/` antes de cualquier LoadImage.
- onnxruntime sin CUDA EP cae a CPU — funciona (~2-3s/imagen), no es bloqueante.
- Generación Krea2 con backend eager (torch cu121): 15-25 min a 2048x3072. GPU al 100% = trabajando, NO matar. Poll `/queue` vacío → `/history/{pid}`.