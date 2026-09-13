---
category: research
name: hyperresearch-hermes
version: "1.0.0"
description: "Adaptación de hyperresearch para Hermes — pipeline de investigación profunda con vault persistente, verificación adversarial y múltiples fuentes."
argument-hint: "investigar X | deep research sobre Y | hyperresearch Z"
allowed-tools: Bash, Read, Write, Python, browser_exec
homepage: https://github.com/jordan-gibbs/hyperresearch
author: <GITHUB_USER> (adaptado de hyperresearch)
license: MIT
user-invocable: true
---

# Hyperresearch-Hermes

**Adaptación de [hyperresearch](https://github.com/jordan-gibbs/hyperresearch) para Hermes Agent.**

Mantiene los principios clave:
- Vault persistente de fuentes (SQLite + Markdown)
- Pipeline adaptativo por tiers (light/full)
- Verificación adversarial de citas
- Búsqueda multi-perspectiva
- Análisis de contradicciones

**Diferencia:** Funciona con cualquier modelo (no requiere Claude Code). Usa subagentes Hermes para paralelización.

---

## Arquitectura

```
hyperresearch-hermes/
├── vault/              # Base de datos de fuentes
│   ├── sources.db      # SQLite con metadatos
│   └── documents/      # Markdown de cada fuente
├── runs/               # Runs actuales
│   └── <run-id>/
│       ├── query.md    # Query canónica
│       ├── corpus.md   # Resumen del corpus
│       └── report.md   # Reporte final
├── steps/              # Scripts por paso del pipeline
└── templates/          # Plantillas para subagentes
```

---

## Tiers de investigación

| Tier | Casos de uso | Tiempo estimado | Pasos |
|------|--------------|-----------------|-------|
| **light** | Consultas factuales, encuestas, comparaciones | 10-15 min | 1→2→9→11 |
| **full** | Análisis argumentativos, investigación profunda | 30-60 min | Todos |

---

## Uso

### Comando principal
```bash
python scripts/research.py --query "tu pregunta de investigación" --tier full
```

### Opciones
```bash
# Light tier (rápido)
python scripts/research.py --query "X vs Y" --tier light

# Full tier (profundo)
python scripts/research.py --query "impacto de IA en empleos 2024" --tier full

# Especificar modelo
python scripts/research.py --query "tema" --model "gpt-4o"

# Resume run anterior
python scripts/research.py --resume <run-id>
```

---

## Pipeline adaptativo (Hermes-style)

### Paso 1: Decompose
- Descompone query canónica en items atómicos
- Genera matriz de cobertura
- Clasifica tier (light/full)

### Paso 2: Width Sweep
- Búsqueda multi-perspectiva (3-5 ángulos)
- Fetch paralelo de fuentes (máx 10 simultáneos)
- Almacena en vault

### Paso 3-8: Análisis (full tier)
- Graph de contradicciones
- Loci analysis (puntos clave)
- Depth investigation
- Cross-locus reconcile
- Source tensions
- Corpus critic

### Paso 9: Evidence Digest
- Top claims + quotes verbatim
- Resumen ejecutivo

### Paso 10: Triple Draft
- 3 drafts paralelos desde ángulos distintos
- Cada uno con sus fuentes

### Paso 11: Synthesize
- Plan + outline
- Síntesis final con verificación cruzada

### Paso 12-14: Verificación (full tier)
- Critics (4 adversarios paralelos)
- Gap-fetch (buscar fuentes faltantes)
- Cite-check (verificar que cada cita sostiene la afirmación)

---

## Vault System

### Estructura de fuentes
```json
{
  "id": "src_001",
  "url": "https://...",
  "title": "Título de la fuente",
  "type": "paper|article|blog|report",
  " fetched_at": "2026-09-11T10:00:00Z",
  "word_count": 2500,
  "topics": ["IA", "empleo"],
  "summary": "...",
  "file_path": "documents/src_001.md"
}
```

### Ventajas
- **Persistente**: Fuentes se reusan entre sessions
- **Searchable**: Query SQLite para encontrar fuentes
- **Versionado**: Cada fuente tiene timestamp
- **Desduplicación**: Detecta fuentes duplicadas por URL o slug

---

## Adaptaciones de hyperresearch

| Original (Claude Code) | Hermes Adaptation |
|------------------------|-------------------|
| `/hyperresearch` command | `python scripts/research.py` |
| Claude Code skills | Subagentes via `delegate_task` |
| Claude Code tools | Tools nativos de Hermes |
| Anthropic models | Any OpenAI-compatible API |
| Run manifest JSON | Manifest en runs/<id>/ |

---

## Scripts

### research.py
Entry point principal. Orquesta el pipeline completo.

### vault.py
Gestión del vault: agregar, buscar, actualizar fuentes.

### fetcher.py
Fetcher paralelo con crawl4ai o requests + markdownify.

### analyzer.py
Análisis de texto: extract de claims, quotes, contradicciones.

### synthesizer.py
Síntesis de reportes con verificación de citas.

---

## Ejemplo de flujo

```
1. Usuario: "investiga el estado de la IA en salud 2024"
   ↓
2. Paso 1 (Decompose):
   - Items: diagnósticos, drug discovery, wearables, ética
   - Tier: full (tema complejo)
   ↓
3. Paso 2 (Width Sweep):
   - Búsqueda en 5 perspectivas
   - Fetch 30+ fuentes en paralelo
   - Almacena en vault
   ↓
4. Pasos 3-8 (Análisis):
   - Identifica contradicciones
   - Loci analysis
   - Depth investigation
   ↓
5. Paso 9 (Evidence Digest):
   - Top claims verificados
   ↓
6. Paso 10 (Triple Draft):
   - 3 drafts desde ángulos distintos
   ↓
7. Paso 11 (Synthesize):
   - Reporte final con citas verificadas
   ↓
8. Paso 12-14 (Verify):
   - 4 critics revisan
   - Gap-fetch si necesario
   - Cite-check final
   ↓
9. Output: report.md + vault actualizado
```

---

## Próximos pasos

- [ ] Implementar `fetcher.py` con crawl4ai
- [ ] Implementar `analyzer.py` con LLM local
- [ ] Agregar soporte para PDFs y papers académicos
- [ ] Integrar con Unpaywall para OA recovery
- [ ] Agregar UI web para visualizar el vault
- [ ] Soporte para `--resume` de runs caídos

---

**Nota:** Esta es una adaptación inicial. El pipeline completo de 16 pasos de hyperresearch original se implementará iterativamente.

**Filosofía:** *Investigar no es buscar, es construir un corpus verificable.*
