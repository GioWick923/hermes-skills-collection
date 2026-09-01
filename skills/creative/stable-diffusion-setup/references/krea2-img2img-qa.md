# Krea2 img2img + QA con VLM local (VERIFICADO 2026-08-26, RTX 3060 12GB)

Complementa `references/krea2-setup.md` (instalación). Este archivo cubre **generación a partir de imagen de referencia** y **verificación de calidad local**.

## img2img Krea2 (reinterpretar una imagen de referencia)

Workflow (API ComfyUI `:8188`):
`LoadImage` → `ImageScale` (lanczos, crop center) → `VAEEncode` → `UNETLoader` (fp8, weight_dtype=default) + `CLIPLoader type=krea2` + `VAELoader` → `KSampler` (8 steps, cfg=1.0, euler/simple) → `VAEDecode` → `SaveImage`.

**Denoise controla cuánto se parece a la referencia:**
| denoise | Efecto |
|---------|--------|
| 0.25-0.35 | Casi copia (misma composición/colores, retoque fino) |
| 0.4-0.55 | Variante clara con el estilo de la referencia |
| 0.6-0.75 | Reinterpretación libre (mismo tema, otro resultado) |

Reglas que funcionaron:
- **Subir la imagen del usuario primero**: `POST /upload/image` multipart (`image=@ruta`, `type=input`, `overwrite=true`). Devuelve `{"name": ...}` → ese nombre exacto va en `LoadImage`.
- **Aspect 9:16** pedido por el usuario: **720×1280** (múltiplos de 16, exacto). 1:1 → 768×768.
- Tema deseado en el positive (ej. "Bayonetta the Umbra Witch, silver-white hair updo, glasses, black leather catsuit, guns on heels...") + negative anti-deformación.
- Krea2 turbo: cfg=1.0, 8 steps (distilled), negative SIEMPRE anti-deformación (ver abajo).

## Bug "dos cabezas" / figuras duplicadas en img2img

**Causa:** denoise alto (0.66) + composición de referencia ambigua (figura superpuesta o segundo plano) → Krea2 inventa una segunda figura → parece 2 cabezas. Confirmado por análisis local.

**Fix verificado:**
1. Bajar denoise a **0.4-0.45**.
2. Positive: **"a single woman, one person only, solo portrait, centered composition"**.
3. Negative: **"two people, two heads, duplicate, second figure, double face, multiple persons, crowd"**.

## Negative prompt anti-deformación — OBLIGATORIO por defecto (preferencia del usuario)

El usuario lo pidió explícitamente: **SIEMPRE** agregar palabras concretas contra deformaciones, especialmente manos (el punto débil de todo modelo de difusión). Texto por defecto:

```
deformed hands, extra fingers, missing fingers, six fingers, malformed hands,
bad hands, twisted fingers, disfigured hands, extra hands, deformed, disfigured,
mutation, malformed limbs, bad anatomy, extra limbs, two people, two heads,
duplicate, second figure, distorted, ugly, blurry, low quality, watermark, text
```

Refuerzo opcional en positive: "perfect hands with five fingers on each hand".
Nota: aun con esto, el usuario puede ver desfiguros que un VLM pequeño no detecta — siempre reportar el QA y ofrecer denoise más bajo / otro seed.

## QA de imágenes con VLM local (no depender del modelo de chat sin visión)

El usuario preguntó "¿ya teníamos analizador de imagen local?" → **SÍ: `qwen25vl-ablit:latest` en Ollama (localhost:11434, 5.5GB)**. Loop verificado:

```python
import base64, json, urllib.request
b64 = base64.b64encode(open(img_path,"rb").read()).decode()
payload = {"model":"qwen25vl-ablit:latest",
  "messages":[{"role":"user","content":"¿Cuántas cabezas? ¿Manos normales?","images":[b64]}],
  "stream":False, "options":{"num_predict":150}}
resp = json.load(urllib.request.urlopen(urllib.request.Request(
  "http://127.0.0.1:11434/api/chat", data=json.dumps(payload).encode(),
  headers={"Content-Type":"application/json"}), timeout=120))
print(resp["message"]["content"])
```

**Reglas del QA:**
- Usar SIEMPRE después de generar: verificar cabezas, dedos, deformidades ANTES de entregar al usuario.
- El modelo de chat de Hermes (deepseek/hy3 vía orcarouter/bai) NO tiene visión conectada a rutas locales → `vision_analyze` con ruta local cae en fallback "no adjuntaste imagen". El VLM local SÍ ve el archivo. No gastar vueltas en vision_analyze para rutas locales.
- HTTP 500 ocasional del VLM (modelo recargando) → reintentar 1 vez con prompt corto.
- Otros modelos Ollama locales: `qwen3-moe-G`, `huihui_ai/qwen3-abliterated:30b-a3b` (texto), `nomic-embed-text`.
