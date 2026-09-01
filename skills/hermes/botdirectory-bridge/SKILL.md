---
category: hermes
name: botdirectory-bridge
description: "Evalúa prompts de botdirectory.ai para portar a Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [botdirectory, porting, prompts, discovery]
    related_skills: [port-external-pattern-to-hermes, bot-fleet-registry, hermes-skill-integration]
---

# BotDirectory Bridge

## Qué es

Puente de descubrimiento: trae el catálogo público de botdirectory.ai (prompts
listos para copiar de Grok Bot, Rakazo, etc.) y lo convierte en candidatos
evaluados para portar a Hermes como skills.

## API verificada (2026-08-26)

- Catálogo completo: `GET https://api.botdirectory.ai/api/bots.json`
- API paginada: `GET https://api.botdirectory.ai/api/bots?limit=N`
- Feed ligero de actualizaciones: `https://botdirectory.ai/updates.json`
- Sitio: `https://botdirectory.ai/` (respondió HTTP 200)
- Cada bot trae: `slug`, `name`, `category`, `integrations[]`, `prompt` (texto
  completo), `contributor`, `sourceUrl` (tweet original), `detailUrl`.

## Uso

```bash
python scripts/fetch_candidates.py --query "gmail calendar" --limit 10
python scripts/fetch_candidates.py --query "competitor pricing" --limit 5 --full
```

El script imprime: nombre, integraciones, contribuidor, y un snippet del prompt.

## Criterios de evaluación (anti-humo)

1. **Integraciones reales**: el prompt menciona MCPs/herramientas que existen
   (verificar con web_search: "refgrow MCP", "maxfusion MCP"...). Si la
   integración no se verifica → 🟡 sospechoso.
2. **Profundidad real**: prompts de 1 frase (#50-#100 del catálogo) = humo.
   Prompts con entrevista, dry-run, approval gates y pasos concretos = oro.
3. **Seguridad**: si pide autonomía sin supervisión, crear cuentas, o publicar
   sin aprobación → 🔴 NO portar tal cual; ver safe-autonomy-operations.
4. **Traducción**: el catálogo llega en inglés; nunca traducir nombres propios
   (Slack, Notion, Datadog...). Mapear con cuidado.
5. **Solape con Hermes**: antes de portar, buscar skill existente
   (email-inbox-triage, product-price-monitor, omh-morning-brief...). Si ya
   existe → 🟢 no duplicar.

## Workflow de porting

1. `fetch_candidates.py` → lista de candidatos.
2. Evaluar con los criterios de arriba → veredicto por candidato.
3. Portar los aprobados como skills siguiendo `port-external-pattern-to-hermes`
   (consultar al usuario ANTES de escribir; separar ya-tenemos / mejora-real /
   decoración).
4. Registrar cada porte en `bot-fleet-registry`.

## Pitfalls

- `web_extract` no lee JSON de API; usar `curl` o el script.
- El catálogo crece: usar `updates.json` para sync incremental (guardar slugs vistos).
- Los `sourceUrl` son tweets; X no deja extraer contenido → tratar como metadata,
  no como fuente verificable.
