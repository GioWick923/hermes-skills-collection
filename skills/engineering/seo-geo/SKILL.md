---
category: engineering
name: seo-geo
description: SEO & GEO (Generative Engine Optimization) para webs — optimiza para motores IA (ChatGPT, Perplexity, Gemini, Copilot, Claude) y búsqueda tradicional (Google, Bing). Usa cuando se quiera mejorar visibilidad de búsqueda, ranking IA, citas en motores generativos, indexación, JSON-LD, meta tags o keyword research. Adaptado de ReScienceLab/opc-skills (MIT), port 2026-09-01.
version: 1.0.0
author: Hermes Agent (port from ReScienceLab/opc-skills)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [seo, geo, generative-engine-optimization, ai-search, schema, json-ld, meta-tags, keyword-research, ai-visibility]
    related_skills: [civitai-article-publish, web-search, markdown-browser, humanizer]
---

# SEO/GEO Optimization Skill

**GEO = Generative Engine Optimization** — optimizar contenido para que sea **citado** por motores de búsqueda IA.

> Insight clave: los motores IA no "rankean" páginas — **citan fuentes**. Ser citado es el nuevo "ser #1".

## Cuándo usar
- Mejorar visibilidad de búsqueda de una web/artículo/landing (tradicional o IA).
- Optimizar contenido para ser citado por ChatGPT, Perplexity, Gemini, Copilot, Claude.
- Keyword research, schema markup (JSON-LD), meta tags, robots.txt, sitemap.
- Revisar que los bots de IA puedan rastrear el sitio.

## Workflow

### Paso 1: Audit técnico (gratis, sin API)
```bash
python "$LOCALAPPDATA/hermes/skills/seo-geo/scripts/seo_audit.py" "https://ejemplo.com"
```
Revisa: title, meta description, H1, OG tags, JSON-LD, load time, robots.txt, sitemap.

Checks manuales rápidos:
```bash
curl -sL "https://ejemplo.com" | grep -E "<title>|<meta name=\"description\"|<meta property=\"og:|application/ld\+json" | head -20
curl -s "https://ejemplo.com/robots.txt"
curl -s "https://ejemplo.com/sitemap.xml" | head -50
```

**Verificar que los bots IA estén permitidos en robots.txt:**
Googlebot, Bingbot, PerplexityBot, ChatGPT-User, ClaudeBot/anthropic-ai, GPTBot.

### Paso 2: Keyword research
Usar `web_search`:
- `"{keyword} keyword difficulty site:ahrefs.com OR site:semrush.com"`
- `"{keyword} search volume 2026"`
- `"site:{competidor.com} {keyword}"`

Analizar: volumen/dificultad, estrategia de competidores, long-tail, conflictos internacionales.

### Paso 3: GEO Optimization (motores IA) — los 9 métodos de Princeton
| Método | Boost visibilidad | Cómo aplicarlo |
|--------|-------------------|----------------|
| **Citar fuentes** | +40% | Añadir citas y referencias autoritativas |
| **Añadir estadísticas** | +37% | Números y datos concretos |
| **Añadir citas/quotations** | +30% | Citas de expertos con atribución |
| **Tono autoritativo** | +25% | Lenguaje seguro, de experto |
| **Fácil de entender** | +20% | Simplificar conceptos |
| **Términos técnicos** | +18% | Terminología específica del dominio |
| **Palabras únicas** | +15% | Diversidad de vocabulario |
| **Fluidez** | +15-30% | Legibilidad y flow |
| ~~Keyword stuffing~~ | **-10%** | **EVITAR** — daña la visibilidad |

**Mejor combo:** Fluidez + Estadísticas.

**Schema FAQPage** (+40% visibilidad IA): ver `references/schema-templates.md`.

**Estructura de contenido:**
- Formato "answer-first" (respuesta directa arriba)
- Jerarquía clara H1 > H2 > H3
- Bullets y listas numeradas
- Tablas para datos comparativos
- Párrafos cortos (2-3 frases máximo)

### Paso 4: SEO tradicional
Template de meta tags (title 60 chars, description 150-160 chars) + Open Graph + Twitter Cards + JSON-LD — ver `references/schema-templates.md`.

Checklist de contenido: H1 con keyword primaria, alt text en imágenes, links internos, `rel="noopener noreferrer"` en externos, mobile-friendly, carga <3s.

### Paso 5: Validar y monitorear
- Validar schema: Google Rich Results Test + Schema.org Validator
- Indexación: `site:{dominio}` en Google/Bing
- Generar reporte (plantilla abajo)

## Optimización por plataforma (detalle en `references/platform-algorithms.md`)

| Plataforma | Factor clave |
|------------|--------------|
| **ChatGPT** | Autoridad de dominio con marca (+11%), actualizar <30 días (3.2x citas), backlinks |
| **Perplexity** | PerplexityBot permitido, FAQ schema, PDFs hospedados (priorizados) |
| **Google AI Overview** | E-E-A-T, structured data, autoridad topical, citas autoritativas (+132%) |
| **Copilot/Bing** | Indexación Bing, ecosistema Microsoft, velocidad <2s |
| **Claude** | Indexación Brave Search, densidad factual alta, claridad estructural |

## Skill Dependencies
- **NO** requiere las skills `twitter`/`reddit` del paquete OPC original (fallan en este entorno — Reddit da 403, Twitter necesita key).
- Para research de tendencias usar las skills Hermes propias: `last30days`, `social-platform-trend-research`, `web-search`, `markdown-browser`.

## Verificación
- [ ] `seo_audit.py <url>` corre y da salida estructurada (probado real: example.com OK)
- [ ] Reporte generado con métricas + recomendaciones
- [ ] Schema JSON-LD válido (validator.schema.org)

## Pitfalls
- **Windows**: usar `python`, NO `python3` (no existe).
- Los scripts de dataforseo/backlinks/competitor requieren API key DataForSEO (`DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD`) — solo se usan si el usuario tiene cuenta; el audit gratis no necesita nada.
- Reddit da 403 en este entorno → no usar el script de reddit del paquete OPC.

## Fuente
- Repo original: https://github.com/ReScienceLab/opc-skills (MIT)
- Research GEO: Princeton (references/geo-research.md)
