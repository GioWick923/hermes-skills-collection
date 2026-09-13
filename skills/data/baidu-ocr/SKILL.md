---
name: baidu-ocr
description: "OCR y parsing de documentos con baidu/Unlimited-OCR (modelo multimodal generativo). Usa cuando el usuario pida OCR, extraer texto de imagen/PDF, o parsing de documentos con estructura (tablas, layout, markdown). Requiere GPU solo en Linux; en Windows corre en CPU (torch 2.10+cpu). Auto-descarga pesos en primer uso."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [OCR, Documents, PDF, Image-Parsing, Baidu, Unlimited-OCR]
    related_skills: [ocr-and-documents]
---

# Baidu Unlimited-OCR

Wrapper sobre `baidu/Unlimited-OCR` (modelo multimodal que hace one-shot long-horizon parsing:
imagen/PDF -> texto + tablas + layout + markdown).

## Entorno
- venv: `C:/Users/<USER>/AppData/Local/hermes/venvs/baidu-ocr` (Python 3.12)
- torch 2.10.0+cpu, transformers 4.57.1
- IMPORTANTE: el PYTHONPATH global contamina el venv con numpy del agente. Siempre correr con `env -u PYTHONPATH`.

## Uso rapido (script)

```bash
env -u PYTHONPATH "C:/Users/<USER>/AppData/Local/hermes/venvs/baidu-ocr/Scripts/python.exe" \
  "C:/Users/<USER>/AppData/Local/hermes/skills/baidu-ocr/scripts/run_ocr.py" \
  --image ruta/a/imagen.png --out ruta/out --config gundam
```
El modelo ya esta descargado en `C:/Users/<USER>/AppData/Local/hermes/models/baidu` (permanente).
No hace falta pasar `--model-dir` a menos que quieras usar otro.

Para PDF multipagina usa `--pdf` y `--multi`.

## Alternativa rápida: Ollama VLM local (para extraer texto de una imagen)

Cuando solo necesitas leer el texto de una imagen (ej. una captura de pantalla) y el modelo
CPU de arriba es demasiado lento, usa el VLM de Ollama (`qwen25vl-ablit`, ya instalado) vía
`/api/generate` con la imagen en base64. Mucho más rápido y suficiente para extraer texto:

```python
import base64, json, urllib.request
b64 = base64.b64encode(open("ruta/imagen.png","rb").read()).decode()
payload = {
    "model": "qwen25vl-ablit:latest",
    "prompt": "Extrae TODO el texto de esta imagen de forma fiel y devuélvelo.",  # ajusta
    "images": [b64],
    "stream": False,
    "options": {"temperature": 0},
}
req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
    data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
resp = json.loads(urllib.request.urlopen(req, timeout=180).read().decode())
print(resp.get("response",""))
```

- Usa `temperature=0` para extracción fiel (no inventa formato).
- Para texturas repetitivas/long documents el VLM puede saturarse; si ves output repetido,
  recorta la pregunta a lo específico (qué texto/valores necesitas) en vez de "todo".
- Este es el camino correcto cuando `vision_analyze` no devuelve el contenido de un archivo
  local válido (p.ej. "no image attached") — en vez de descartar la imagen, pásala al VLM local.

## Notas
- Primera ejecucion descarga pesos (~varios GB) desde HuggingFace. Tarda.
- En Windows es CPU (lento). En Linux con GPU cambiar torch_dtype a 'cuda' y el venv a una version cu.
- El skill ocr-and-documents (pymupdf/marker) es alternativa mas liviana para PDFs con texto.
