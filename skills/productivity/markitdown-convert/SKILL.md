---
name: markitdown-convert
description: "Convert files to Markdown: PDF, DOCX, XLSX, PPTX, HTML, ZIP."
version: 1.0.0
author: Hermes Agent (wrapper de microsoft/markitdown v0.1.7, MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [conversion, markdown, pdf, docx, xlsx, pptx, office, zip, html, llm]
    related_skills: [pdf, docx, xlsx, pptx, ocr-and-documents, markdown-browser, youtube-content]
---

# MarkItDown — conversión de archivos a Markdown (microsoft/markitdown)

## When to Use

- Necesitas convertir un archivo (PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON, XML, ZIP, EPUB,
  imágenes, audio, YouTube) a **Markdown estructurado** para consumo LLM o análisis.
- Quieres un **CLI único** para cualquier formato (vs invocar skills separadas por tipo).
- El archivo es **audio** (transcripción) o **URL de YouTube** — formatos que read_file/anydoc NO cubre.
- Conversión por lotes o en scripts (API Python `MarkItDown().convert()`).

NO usar cuando: read_file de Hermes ya extrae bien el archivo (docx/xlsx/pdf/ipynb vía anydoc)
y no necesitas la salida markdown estructurado — los skills docx/xlsx/pptx/pdf son más ricos
para editar, no solo extraer.

## Instalación (ya hecho 2026-08-27)

```bash
python -m pip install "markitdown[pdf,docx,pptx,xlsx,xls]"   # extras ligeros
# OPCIONALES (NO instalados): [audio-transcription] (whisper, pesado), [youtube-transcription]
```

CLI: `markitdown` (exe en el venv). API: `from markitdown import MarkItDown`.

## Uso CLI

```bash
markitdown archivo.pdf                # imprime markdown en stdout
markitdown archivo.docx > salida.md   # redirige a archivo
markitdown archivo.html | head -40    # pipe normal
markitdown < stdin-input              # lee de stdin si no hay filename
```

## Uso API Python (script / execute_code)

```python
from markitdown import MarkItDown
md = MarkItDown()
res = md.convert("C:/ruta/archivo.xlsx")   # o .convert_stream(fh, stream_info=...)
print(res.text_content)
```

## Formatos verificados (2026-08-27, v0.1.7)

| Formato | Resultado | Estado |
|---|---|---|
| HTML | headings, tablas→markdown tables, links | ✅ probado |
| CSV | tabla markdown | ✅ probado |
| JSON | passthrough | ✅ probado |
| ZIP | itera contenidos (`## File: ...`) | ✅ probado |
| XLSX | nombre hoja→heading + tabla | ✅ probado |
| DOCX | headings, párrafos, tablas | ✅ probado |
| PDF | texto extraído (capa de texto; sin espaciado fino entre palabras — normal) | ✅ probado con paper real |
| PPTX | — | instalado, no probado |
| Audio / YouTube | NO instalado (extras pesados) | agregar solo si se necesitan |

## Pitfalls

- **Crear ZIP de prueba en git-bash**: `zip` NO existe en MSYS → usar Python `zipfile` (ver script abajo).
- **PDF con escaneos**: markitdown extrae solo capa de texto; imágenes escaneadas requieren OCR
  (`ocr-and-documents` / `vision_analyze`).
- **Seguridad (nota oficial)**: hace I/O con los privilegios del proceso actual. En entornos no
  confiables, sanitizar inputs y usar `convert_stream()`/`convert_local()` en vez de URLs arbitrarias.
- **Windows**: si `markitdown` no está en PATH, usar `python -m markitdown archivo`.
- **No reemplaza a los skills docx/xlsx/pptx/pdf** para edición — es para extracción/conversión.

## Script útil: crear ZIP de prueba en Windows

```python
import zipfile
with zipfile.ZipFile("sample.zip","w") as z:
    z.writestr("hola.txt","contenido")
```
