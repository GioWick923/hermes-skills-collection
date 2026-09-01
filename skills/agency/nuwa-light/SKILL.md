---
category: agency
name: nuwa-light
description: "Destilar el estilo de pensamiento de una persona en un skill instalable (marco conceptual ligero, sin multi-agente ni coste alto). Entrada: un nombre ('hazme un skill estilo Taleb') o un problema difuso ('quiero decidir mejor' → recomienda a quién destilar). Produce un skill de perspectiva con: mental models, decision heuristics, expresión DNA, anti-patterns, honest boundaries. Adaptado de alchaincyf/nuwa-skill (女娲, MIT), versión ligera 2026-09-01."
version: 1.0.0
author: Hermes Agent (port from alchaincyf/nuwa-skill)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [nuwa, persona, perspective, distillation, mental-models, thinking-framework, roleplay]
    related_skills: [civic-ai-engineer, agency-persona-conversion, agent-builder]
---

# Nuwa Light — Destilación de mental frameworks (marco conceptual)

> 「写不进去的那部分，才是你真正的护城河。」——但写得进去的部分，已经足够强大。

**Nuwa no copia a una persona — destila SU MARCO DE PENSAMIENTO.** Captura **HOW they think**, no **WHAT they said**. El resultado es un skill "de perspectiva" instalable: un sistema cognitivo operativo de esa persona.

## Cuándo usar
- Usuario da un nombre → "hazme un skill estilo [X]", "destila a [X]", "¿cómo pensaría [X]?", "[X] perspective"
- Usuario da un problema difuso → "quiero decidir mejor", "no sé escribir claro", "ayúdame a ver el negocio con otra cabeza" (→ recomiéndale quién destilar)
- Usuario quiere un "pensador" para consultar, un filtro de decisiones, o un personaje de rol

## Diferencia de la versión completa (por qué esta es ligera)
La nuwa original usa **6 agentes paralelos** de investigación + fases pesadas (500k+ tokens, coste de decenas de dólares). Esta versión ligera:
- ✅ Corre con **1 sola investigación web** (web_search) por dimensión, no 6 agentes
- ✅ Sin descargas masivas de libros/subtítulos (solo si el usuario los trae)
- ✅ Sin coste alto: una sesión normal
- ✅ Conserva el **núcleo conceptual**: triple verificación de mental models, expresión DNA, honest boundaries, y el fidelity scorecard

## Workflow ligero

### Paso 1: Entrada
- **Nombre claro** → ve al Paso 2
- **Problema difuso** → mapea a una dimensión de necesidad y recomienda 2-3 candidatos:
  | Necesidad | Dirección de framework |
  |-----------|------------------------|
  | Mejorar decisiones | Munger (inversión), Taleb (anti-frágil), Naval (apalancamiento) |
  | Expresión/escritura clara | Feynman (simplificación), Paul Graham (ensayo) |
  | Negocio/PMF | Musk (primera principios), Munger (círculo de competencia) |
  | Pensamiento crítico | Taleb (falsación), Kahneman (sesgos) |
  | Riesgo/incertidumbre | Taleb (convexidad), Howard Marks (riesgo) |
  | Diseño/producto | Jobs (minimalismo), Dyson (iteración) |
- Elegido → Paso 2

### Paso 2: Investigación (web_search, 3-5 consultas dirigidas)
Usa `web_search` con queries como:
- `"[persona]" filosofía ideas principales` / `"[persona]" mental models`
- `"[persona]" quotes citas clave`
- `"[persona]" writing style cómo escribe habla`
- `"[persona]" decisiones controversias críticas`
- `"[persona]" 2026 reciente` (para la parte actualizada)

**Regla de fuentes:** prioriza primarias (obras, entrevistas, cuentas propias). Descarta rumores. Si el usuario trae material propio (libro PDF, transcript, notas) → úsalo PRIMERO, es de mayor calidad.

### Paso 3: Triple verificación de mental models
Para cada candidato de mental model (deberías tener 15-30 crudos), aplica:
1. **Cross-domain** — ¿aparece en ≥2 áreas distintas de su pensamiento?
2. **Generativo** — ¿puedes inferir su postura sobre un tema nuevo?
3. **Exclusivo** — ¿no todos los inteligentes piensan así?
- ✅ 3 de 3 → **mental model** (mantén 3-7)
- 1-2 de 3 → **decision heuristic**
- 0 → descártalo
- **Regla:** 3 modelos profundos > 10 principios superficiales.

### Paso 4: Expresión DNA
De su estilo: sentence rhythm (largo/corto), vocabulary (high-frequency, términos propios, palabras tabú), cadence (conclusión-primero vs setup), humor (ironía/autocrítica/absurdo), certeza ("no estoy seguro" vs "obvio"), citation habits (a quién cita).

### Paso 5: Construir el skill de perspectiva
Crea un SKILL.md en `$LOCALAPPDATA/hermes/skills/<persona>-perspective/SKILL.md` usando la plantilla de `references/skill-template.md`. Estructura fija:
- Frontmatter (name, description con triggers: "usa el ángulo de [X]", "¿cómo lo vería [X]?")
- Rol: activar = responder COMO esa persona (primera persona), con disclaimers mínimos
- **Mental models** (3-7): nombre / una línea / evidencia ≥2 dominios / aplicación / límite
- **Decision heuristics** (5-10): regla + cuándo aplica + caso
- **Expresión DNA**: reglas de estilo
- **Valores y anti-patterns**: lo que persigue / rechaza / no ha resuelto (tensiones)
- **Honest boundaries**: qué NO puede hacer, info hasta cuándo
- **Fuentes**: primarias vs secundarias

### Paso 6: Quality check (versión ligera del fidelity scorecard)
Autoevalúa SIN idealizar (el paper SkillLens muestra que la autoevaluación LLM acierta solo 46% — por eso escribe los resultados, no los confíes):
- [ ] ¿Respondería igual en temas donde tiene postura pública? (3 preguntas de postura conocida)
- [ ] ¿Se le reconoce por el estilo sin el nombre?
- [ ] ¿Marca inferencia cuando NO ha hablado del tema (no inventa)?
- [ ] ¿Fuentes trazables, primarias > 50%?
- [ ] ¿Estructura completa (3-7 models, boundaries ≥3, tensiones ≥2)?
- Guarda resultado en `FIDELITY.md` junto al skill. Pasa si ≥70/100 en las 5 dimensiones (30/20/20/15/15).

## Fuentes originales (en `~/tools/nuwa-skill/references/`)
- `extraction-framework.md` — metodología completa de triple verificación
- `skill-template.md` — plantilla de SKILL.md para la persona
- `fidelity-scorecard.md` — rúbrica completa de calidad (skillLens)
Adapta de estos según necesites más profundidad en un caso concreto.

## Pitfalls
- **No idealizar**: preserva las contradicciones de la persona (son su profundidad), no las "arregles".
- **No sobre-imitar**: el expression DNA se usa con moderación; demasiado se vuelve parodia.
- **Honestidad de límites**: si hay poca info pública, escribe "dimensión especulativa" — un skill honesto de 60pts > uno que parece perfecto pero inventa.
- **Información fresca**: siempre incluye el estado reciente (últimos ~12 meses) — los frameworks caducan.

## Verificación
- [ ] Skill de perspectiva creado en `$LOCALAPPDATA/hermes/skills/<persona>-perspective/SKILL.md`
- [ ] Listado en `hermes skills list`
- [ ] FIDELITY.md generado con score ≥70
- [ ] Triggers del frontmatter funcionan (probar "usa el ángulo de [X]")
