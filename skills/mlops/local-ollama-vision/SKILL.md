---
name: local-ollama-vision
description: "Use when reading/OCR an image with the local Ollama VLM."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [Vision, OCR, Ollama, VLM, Image, Local]
    related_skills: [baidu-ocr, minicpm-v]
---

# Local Ollama Vision (leer imagenes con VLM local)

Lee, describe o extrae texto de una imagen con un **modelo de vision local vía Ollama**
usando el endpoint `POST /api/generate`. Es el **camino rapido y gratuito** para OCR de
screenshots y UI en Windows — verificado: devuelve texto util en ~55s donde el path CPU
de baidu/Unlimited-OCR tarda >300s (timeout).

## Cuando usar
- `vision_analyze` no logra cargar/leer la imagen (modelo auxiliar devuelve "no image attached").
- OCR rapido de una captura de pantalla (repo de GitHub, UI, error) en este host.
- Describir/analizar una imagen local sin subirla a la nube.

## Requisito previo
Verifica que Ollama esta vivo y que hay un modelo de vision:
```bash
curl -s http://127.0.0.1:11434/api/tags   # busca un modelo con "vision" en capabilities
```
En este host el VLM de vision es **`qwen25vl-ablit:latest`** (7.6B Q4, family qwen2vl).

## Llamada (Python, stdlib)
```python
import base64, json, urllib.request
b64 = base64.b64encode(open(ruta_img, "rb").read()).decode()
payload = {"model": "qwen25vl-ablit:latest",
           "prompt": "Extrae TODO el texto de esta imagen de forma fiel: ...",
           "images": [b64], "stream": False, "options": {"temperature": 0}}
req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
    data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=180) as r:
    print(json.loads(r.read().decode()).get("response"))
```

Alternativa con curl:
```bash
B64=$(base64 -w0 ruta_img.jpg)   # en git-bash: base64 -w0
curl -s http://127.0.0.1:11434/api/generate \
  -d "{\"model\":\"qwen25vl-ablit:latest\",\"prompt\":\"Extrae el texto\",\"images\":[\"$B64\"],\"stream\":false}"
```

## Pitfalls (verificados)
- **Salida ciclica/repetitiva**: si el VLM repite la misma linea muchas veces
  (ej. una lista de items iguales), baja `temperature` a 0 y acota el prompt a
  "devuelve solo el texto extraido", o recorta la imagen a la region util.
- **Modelos 7.6B**: buenos para texto/extracto; no esperes razonamiento fino.
  Para estructura compleja (tablas/layout) prefiere baidu/Unlimited-OCR si tienes
  paciencia para CPU.
- Imagen como **data URL** en `vision_analyze` a veces tampoco la carga; el path
  Ollama con base64 crudo es el fallback mas confiable en este host.
- **HTTP 400 Bad Request en `/api/generate` con imagenes grandes** (verificado
  2026-09-01): screenshots altos de ~370KB PNG superan el limite del payload de
  Ollama → `urllib.error.HTTPError: HTTP Error 400`. **Fix: downscale la imagen
  ANTES de mandarla** — `im.convert('RGB').save(out, quality=70)` con
  `im.thumbnail((900,1200))` reduce un PNG de 368KB a ~73KB JPEG y el request pasa.
  El problema no es la resolución en píxeles sino el tamaño del base64; un JPEG
  comprimido siempre lo resuelve.

## Relacionado
- `baidu-ocr`: parsing pesado con estructura (tablas/layout/PDF) — CPU lento en Windows.
- `minicpm-v`: otro VLM local eficiente para imagenes.
