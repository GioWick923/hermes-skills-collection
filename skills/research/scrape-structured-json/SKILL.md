---
name: scrape-structured-json
description: "Scrape → markdown → JSON vía LLM local (format)."
version: 1.0.0
author: Hermes Agent (adaptado de AnyCrawl LLM-extraction)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [scrape, markdown, llm-extraction, json, schema, ollama, structured-output]
    related_skills: [markdown-browser, local-llm-constrained-output, dogfood]
---

# Scrape → JSON estructurado (LLM extraction, patrón AnyCrawl)

> Adaptado de **AnyCrawl** (`any4ai/anycrawl`) pero con TU stack: sin server nuevo.
> El flujo: **scrape (markdown-browser/obscura/playwright) → clean markdown → LLM local
> con `format`=schema → JSON estructurado denso + validado.** Verificado de punta a punta
> con `qwen3-moe-G` (Ollama) el 2026-08-31.

## When to Use
Convertir una página (o un batch de páginas scrapeadas) en **JSON estructurado con schema**
usando tu modelo local — el "LLM extraction" de AnyCrawl, sin el peso de un server. Aplica
cuando necesitas extraer campos/candidatos/entidades de contenido web para luego procesarlos.

## Flujo completo (una sola secuencia)

1. **SCRAPE** → markdown. Usa una de estas (de menor a mayor peso):
   - `markdown-browser` skill (requests + markdownify, sin JS, rápido) — página estática.
   - `obscura` / `scrapling` MCP — requiere JS o anti-bot.
   - `stealth-browser-mcp` / `playwright` — SPA/login/dinámico.
   > Ya probado: `requests` SIN User-Agent real lo bloquean (Wikipedia → error de robot policy).
   > **SIEMPRE** mandá un User-Agent de navegador real (`Mozilla/5.0 ... Chrome/120`).

2. **LIMPIA el markdown**: quita nav/footer/boilerplate y líneas repetidas, y **recorta** a un
   tamaño razonable (~6-8k chars máx para el LLM local). Enviar demasiado = tokens quemados o
   el LLM extrae de la navegación en vez del cuerpo. Consejo: saltar a la sección del primer
   header real (p.ej. `## What is...`, `# Foo`) antes de cortar.

3. **DEFINE el schema** (una vez por dominio, no por página): `{type: object, properties, required}`.

4. **EXTRAE con el LLM local vía `format`**: prompt = markdown + "solo el JSON". `format`=schema
   garantiza claves completas y densas (ver skill `local-llm-constrained-output`). `num_ctx` >= 8192.

5. **VALIDA**: `json.loads` + verificar claves `required` presentes. Si no pasó, reintenta
   con prompt más corto o schema más simple (no envuelve en ```json con `format`).

## Helper (scripts/extract_structured.py)

Genera markdown limpio → LLM local → JSON. Uso:
```bash
python skills/research/scrape-structured-json/scripts/extract_structured.py \
  --url "https://example.com" --schema-json '{"type":"object",...}' \
  [--model qwen3-moe-G] [--max-chars 6500] [--num-ctx 8192]
```
O desde un markdown ya scrapeado: `--markdown page.md`. Imprime el JSON parseado.

## Parámetros del script (para el prompt)
- `--max-chars`: recorte de markdown antes de enviar (default 6500). Muy grande → el LLM local
  pierde foco y extrae boilerplate.
- `--skip-nav`: salta hasta el primer header `#`/`##` para evitar la navegación de wikis/sites.
- `--model`: por defecto `qwen3-moe-G` (tu MoE 30B-A3B). Otro: `nomic-embed-text` NO sirve (embbedings, no chat).
- `--required`: lista de claves a verificar tras el parse (default = las `required` del schema).

## Verificado (prueba real 2026-08-31)
- Scrape `https://en.wikipedia.org/wiki/Vector_database` con UA real → 200, ~60KB markdown. ✅
- LLM `qwen3-moe-G` con `format`=schema → JSON PARSE OK, claves completas y densas, en español. ✅
- Sin `format`, el modelo envuelve en ```json y rellena claves (NO usar si pides JSON).

## Pitfalls
- **User-Agent**: siempre navegador real, o los sites (especialmente wikis) responden robot-policy.
- **Boilerplate**: la navegación lateral de wikis contamina la extracción si no saltas al cuerpo.
- **`num_ctx`**: para 6-8k chars de markdown, 8192 basta; si el LLM corta, sube a 16k (RAM libre 96GB).
- **JSON con `format`**: nunca envuelve en backticks; si aparece raw sin parse, revisa que el
  schema no esté anidado de más (puede dar 500 en Ollama).
- **Modelo de embeddings**: `nomic-embed-text` es para embeddings, NO para chat/extract.

## Verificación del skill
- [ ] URL scratch accesible con UA real (200)
- [ ] Markdown limpio (sin nav) recortado a <= max-chars
- [ ] Schema definido con `required`
- [ ] `format`=schema presente (no texto libre)
- [ ] `json.loads` pasa + claves required presentes
- [ ] Resultado denso (no relleno) — si rellena, recalibra prompt/corte
