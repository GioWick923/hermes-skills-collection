---
category: data
name: langextract-structured
description: "Extract structured information from unstructured text using Google LangExtract with precise source grounding and interactive HTML visualization. Use when the user wants to pull entities/fields from documents, notes, reports, or transcripts (e.g. 'extract medications from this note', 'pull key facts from this text', 'structure this report')."
version: 1.0.0
author: Hermes Agent (google/langextract 1.6.0)
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [extraction, nlp, structured-data, grounding, langextract, data]
    homepage: https://github.com/google/langextract
---

# LangExtract Structured Extraction

Extracts structured data from unstructured text using `google/langextract` (installed in the
Hermes venv as `langextract[all]==1.6.0`). Every extracted value is **grounded** to its exact
span in the source text, and results render as an interactive HTML file for review.

## When to Use (trigger)
- User wants to extract entities/fields from free text: medical notes, legal docs, meeting transcripts,
  research papers, chat logs, scraped pages, OCR output.
- Phrases like "extract X from this text", "pull structured facts", "structure this report",
  "turn this into JSON fields", "extrae datos de este documento".
- As a post-step after `video-transcriber` (transcript → structured entities) or after any scraping.

## Requirements
- Module: `langextract` in Hermes venv (`C:\Users\<USER>\AppData\Local\hermes\hermes-agent\venv`).
- A model provider key in env:
  - `GEMINI_API_KEY` (Google Gemini, default provider) OR
  - `OPENAI_API_KEY` (OpenAI-compatible; usuario tiene pendiente esta key para video-transcriber también).
- Output dir: `C:\Users\<USER>\Documents\1hermes proyectos\extractions\`

## Usage

LangExtract v1.6.0 usa `lx.extract(text_or_documents=, prompt_description=, model_id=, api_key=, examples=)` 
— NO `text=`/`prompt=`. Requiere `examples=` (ExampleData+Extraction) o `output_schema`.

Minimal Python (run via Hermes venv python), KEY YA CONFIGURADA en `.env` de esta skill:

```python
import os
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")  # del .env
import langextract as lx
from langextract.data import ExampleData, Extraction

text = "<tu texto>"
examples = [ExampleData(
    text="Patient takes Aspirin 100mg daily.",
    extractions=[Extraction(extraction_class="medication", extraction_text="Aspirin 100mg daily")],
)]
result = lx.extract(
    text_or_documents=text,
    prompt_description="Extract medications with attributes name, dose, frequency.",
    model_id="gemini-3.6-flash",   # 2.5-flash YA NO disponible para usuarios nuevos
    api_key=os.environ["GEMINI_API_KEY"],
    examples=examples,
)
# result -> AnnotatedDocument(s) con .extractions (cada una tiene extraction_class, extraction_text, char_interval)
lx.visualize("extraction_results.jsonl")   # HTML interactivo
```

VERIFICADO 2026-08-18: smoke test real extrajo 3 medicamentos de un texto de prueba con `gemini-3.6-flash` + GEMINI_API_KEY del usuario. Funciona end-to-end.

## Output
- `extraction_results.jsonl` — structured entities + character-span grounding.
- `extraction_results.html` — interactive visualization (open in browser / show via MEDIA:).

## Notes
- Grounding is the key feature: each extraction links back to the exact source span (audit-friendly).
- For large docs, LangExtract chunks + extracts in parallel automatically.
- Pairs well with `video-transcriber` (transcript → entities) and `research/grounded-citations`.
- No MCP server bundled; invoked as a skill (Python) rather than a registered MCP tool.
