#!/usr/bin/env python3
"""
extract_structured.py — scrape → markdown limpio → JSON estructurado vía LLM local.

Patrón AnyCrawl "LLM extraction" adaptado al stack local (Ollama + markdownify):
  1. Fetch una URL (User-Agent de navegador real) → markdown, o leer un --markdown ya scrapeado.
  2. Limpiar (saltar nav si --skip-nav) y recortar a --max-chars.
  3. Llamar al LLM local con format=<schema> para que devuelva SOLO el JSON (denso, no relleno).
  4. Validar json.loads + claves required. Imprimir el JSON parseado o un error claro.

Uso:
  python extract_structured.py --url "https://example.com" \
      --schema-json '{"type":"object","properties":{"title":{"type":"string"}},"required":["title"]}'
  python extract_structured.py --markdown page.md --schema-json '{"type":"object"}' \
      --skip-nav --max-chars 5000

Requiere: requests, markdownify (pip install requests markdownify). Ollama corriendo :11434.
"""
import argparse
import json
import os
import re
import sys
import urllib.request

DEFAULT_OLLAMA = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen3-moe-G"
DEFAULT_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120 Safari/537.36")
DEFAULT_MAX_CHARS = 6500


def _fetch_md(url: str) -> str:
    """Fetch URL con UA real y convertir a markdown."""
    import requests
    from markdownify import markdownify
    r = requests.get(url, headers={"User-Agent": DEFAULT_UA}, timeout=25)
    r.raise_for_status()
    md = markdownify(r.text, heading_style="ATX")
    return re.sub(r"\n{3,}", "\n\n", md)


def _clean_nav(md: str) -> str:
    """Salta hasta el primer header real (# / ##) para evitar nav/footer boilerplate."""
    m = re.search(r"^#{1,3}\s+\S", md, re.MULTILINE)
    if m:
        return md[m.start():]
    return md


def _extract_prompt(md: str) -> str:
    return (
        "Extract structured info from the page markdown below. "
        "Return ONLY a valid JSON object matching the schema. No extra text.\n\n"
        "PAGE CONTENT:\n" + md
    )


def _call_llm(prompt: str, schema: dict, model: str, num_ctx: int) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "format": schema,
        "stream": False,
        "options": {"temperature": 0, "num_ctx": num_ctx},
    }
    req = urllib.request.Request(
        DEFAULT_OLLAMA, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=240) as resp:
        return json.loads(resp.read()).get("message", {}).get("content", "")


def main() -> int:
    ap = argparse.ArgumentParser(description="Scrape → JSON estructurado vía LLM local.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", help="URL a scrapear")
    src.add_argument("--markdown", help="Archivo .md ya scrapeado")
    ap.add_argument("--schema-json", required=True, help="JSON schema (objeto) como string")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="Modelo chat de Ollama")
    ap.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS, help="Recorte de markdown")
    ap.add_argument("--skip-nav", action="store_true", help="Saltar hasta el primer header real")
    ap.add_argument("--num-ctx", type=int, default=8192, help="context window del LLM")
    args = ap.parse_args()

    try:
        schema = json.loads(args.schema_json)
    except Exception as e:
        print("SCHEMA_JSON_INVALID:", e)
        return 2

    if args.url:
        try:
            md = _fetch_md(args.url)
        except Exception as e:
            print("FETCH_ERR:", e)
            return 1
    else:
        md = open(args.markdown, encoding="utf-8").read()

    if args.skip_nav:
        md = _clean_nav(md)
    md = md[: args.max_chars]

    prompt = _extract_prompt(md)
    try:
        raw = _call_llm(prompt, schema, args.model, args.num_ctx)
    except Exception as e:
        print("LLM_ERR:", e)
        return 1

    try:
        parsed = json.loads(raw)
    except Exception as e:
        print("JSON_PARSE_FAIL:", e)
        print("RAW:", raw[:400])
        return 1

    # verificar required
    required = schema.get("required", [])
    missing = [k for k in required if k not in parsed]
    if missing:
        print("MISSING_REQUIRED:", missing)
        print("PARSED:", json.dumps(parsed, ensure_ascii=False)[:800])

    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
