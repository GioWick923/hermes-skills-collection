---
name: local-ollama-vision-qwen3vl
category: mlops
description: "OCR/vision local Qwen3-VL-8B Q6_K via Ollama, bajo demanda."
version: 1.0.0
author: Gio + Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [vision, ocr, ollama, vlm, qwen3vl, local]
---

# Qwen3-VL-8B Q6_K para OCR/Visión local (bajo demanda)

## Cuándo usar
- OCR rapido de una captura/UI/imagen en este host, SIN subir a nube
- Describir/analizar una imagen local puntual (no lote)
- Cuando NO se necesita el pipeline pesado de DeepSeek-OCR-2 (para documentos/tablas usar ese)

## Modelo
`hf.co/noctrex/Huihui-Qwen3-VL-8B-Instruct-abliterated-GGUF:Q6_K` (7.9GB, abliterated)
Reemplaza al antiguo `qwen25vl-ablit`. Verificado: lee `ocr_test.png` -> "HERMES OCR TEST 12345 / VISION LOCAL QWEN3-VL" a 37 tok/s, 28s de carga.

## Config (para que SOLO corra cuando se usa visión)
- Ollama se arranca con `OLLAMA_CONTEXT_LENGTH=32768 ollama serve`
- El modelo vive en `~/.ollama/models` (ya descargado, no re-descargar)
- IMPORTANTE: es **bajo demanda** — carga con la request (28s carga) y se descarga
a los ~30min por keep-alive. No está fijo en VRAM. Ideal para no gastar llamadas API.

## Llamada (Python stdlib, sin dep)
```python
import base64, json, urllib.request
b64 = base64.b64encode(open(ruta_img,"rb").read()).decode()
payload = {"model": "hf.co/noctrex/Huihui-Qwen3-VL-8B-Instruct-abliterated-GGUF:Q6_K",
           "prompt": "Extrae TODO el texto de esta imagen de forma fiel, sin agregar nada.",
           "images": [b64], "stream": False, "options": {"temperature": 0}}
req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
    data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req, timeout=300) as r:
    print(json.loads(r.read().decode()).get("response"))
```

## Pitfalls
- **No confundir con DeepSeek-OCR-2** (Dogacel): ese es el pipeline transformers pesado para
documentos/tablas/PDF, este VLM Qwen3-VL es para imagenes/screenshots puntuales. Conviven.
- Imagen grande (PNG > ~370KB) -> HTTP 400. Reducir a JPEG primero: `im.convert('RGB').save(o,quality=70)` con thumbnail.
- Carga ~28s la primera vez + re-carga si está en RAM por otro request de otro modelo (Coder-30B). PAUSA normal.
- Ollama debe estar vivo: `curl -s http://127.0.0.1:11434/api/version`. Si no, `OLLAMA_CONTEXT_LENGTH=32768 ollama serve`.
- Si un request simultaneo (ej. dsh con Coder-30B) usa VRAM, el Q6 puede ir a CPU -> lento. Alternar con paciencia o cerrar el otro.

## Borrar el modelo viejo (dno usar qwen25vl ya)
```bash
ollama rm qwen25vl-ablit:latest
```