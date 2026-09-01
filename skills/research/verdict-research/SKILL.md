---
category: research
name: verdict-research
description: "Use when the user asks to research or investigate any topic."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, social-intelligence, verdict, reddit, twitter, expert-analysis, community-sentiment, fact-checking]
    related_skills: [social-platform-trend-research, arxiv, youtube-content, blogwatcher, grounded-citations]
---

# ⚖️ Verdict Research — Dictamen Social-Experto

Scans social platforms (Reddit, X/Twitter, Facebook, YouTube, Discord, TikTok, HN, SO) for real opinions, then cross-references with expert engineering sources and official docs to deliver a structured, opinionated verdict. Social-first, expert-backed.

## Filosofía

La gente real sabe cosas que los docs no dicen. Los docs saben cosas que la gente no entiende. Este skill las une en un dictamen con opinión clara.

> **La voz de la comunidad es el corazón del dictamen. La ingeniería experta es la columna vertebral.**

No entregamos "depende". Entregamos un veredicto.

---

## Cuándo Activar

Cuando el usuario use frases como:
- "investiga esto...", "¿qué tal es...?", "busca información sobre..."
- "quiero saber sobre...", "dictamen...", "veredicto..."
- "¿qué dice la gente de...?", "¿es bueno...?"
- O cualquier petición de investigación donde la opinión colectiva importe

**NO usar para**: preguntas factuales simples con respuesta de 1 línea, ni cuando el usuario ya dio la fuente exacta a analizar.

---

## Fases del Flujo

### FASE 0 — TRIAGE INTELIGENTE

Antes de buscar nada, entender qué se busca realmente.

1. **Identificar el tema central**: ¿Qué producto/herramienta/tecnología/concepto?
2. **Determinar el tipo de dictamen**: ¿Técnico? ¿Producto? ¿Comparativo? ¿Concepto abstracto?
3. **Calcular profundidad**: Tema técnico/controversial → búsqueda profunda (más capas). Tema simple → search rápido.
4. **Generar queries por plataforma** — Cada plataforma tiene su propio lenguaje:
   - Reddit: natural language, problemas, "what do you think about..."
   - X/Twitter: corto, directo, hashtags, handles
   - YouTube: reviews, tutoriales, "honest opinion"
   - HN/SO: técnico, específico, error messages
   - arxiv: académico, formal
5. **Determinar recencia crítica**: Tema técnico → priorizar últimos 6-12 meses. Tema atemporal → hasta 3 años.

> **Output interno**: lista de queries optimizadas + nivel de profundidad + ventana temporal.

---

### FASE 1 — INTELIGENCIA SOCIAL (corazón del dictamen)

Esta es la fase más importante. Aquí es donde se escucha a la gente.

#### Plataformas a escanear (en paralelo cuando sea posible):

| Plataforma | Qué Extraer | Herramienta |
|---|---|---|
| **Reddit** | Threads, comentarios, debates, upvotes | `social-platform-trend-research` skill + `web_search` + `terminal` (old.reddit.com HTML) |
| **X/Twitter** | Opiniones de devs, threads técnicos, debates | `web_search` con `site:x.com` + `site:twitter.com` |
| **Facebook** | Grupos técnicos, debates públicos | `web_search` con `site:facebook.com/groups` |
| **YouTube** | Comentarios de videos, reviews, opiniones honestas | `youtube-content` skill para transcripts + `web_search` para comentarios |
| **Discord** | Mensajes públicos, comunidades | `web_search` con `site:discord.com/channels` + invitaciones públicas |
| **TikTok** | Opiniones rápidas, demos, reacciones | `web_search` con `site:tiktok.com` (limitado) |
| **Hacker News** | Discusiones técnicas profundas | `web_search` con `site:news.ycombinator.com` |
| **Stack Overflow** | Problemas técnicos reales, soluciones | `web_search` con `site:stackoverflow.com` |
| **GitHub Issues** | Bugs reales, feature requests, discusiones de diseño | `web_search` con `site:github.com` + `repo:owner/name issues` |
| **Foros especializados** | Dev.to, Medium, blogs técnicos | `web_search` con `site:dev.to` + `site:medium.com` |

#### Estrategia de búsqueda social:

```
PARA CADA PLATAFORMA:
  1. search con query optimizada para esa plataforma
  2. Extraer: opiniones, quejas, trucos, controversias, sentimiento
  3. Taggear evidencia: DIRECT / INDIRECT / INFERRED
  4. Notar: timestamp (recencia), autor (¿es dev senior o usuario casual?)
  5. Contar: ¿cuántas fuentes independientes dicen lo mismo?
```

#### Peso de evidencia social:

| Nivel | Qué significa | Peso |
|---|---|---|
| 🔴 DIRECT | Leído de post/comentario público real | Alto |
| 🟡 INDIRECT | Snippet de search, cita en otra página | Medio |
| 🔵 INFERRED | Síntesis de múltiples señales débiles | Bajo |
| ⚪ NO-ACCESS | Plataforma bloqueada, no hay datos | N/A (decirlo) |

> **Output interno**: matriz de datos sociales consolidados con patrones, controversias y sentimiento.

---

### FASE 2 — MINERÍA DE PATRONES SOCIALES

De toda la data social, extraer:

1. **CONSENSO POPULAR** — En qué coincide la mayoría
   - "Todo el mundo dice que X es difícil de configurar"
   - "Nadie menciona Y como problema" (también es data)

2. **CONTROVERSIAS ACTIVAS** — Dónde hay división
   - "Un lado dice que es revolucionario, otro dice que es hype"
   - "Reddit ama X, HN lo odia"

3. **PROBLEMAS REALES REPORTADOS** — Dolores concretos
   - "Memory leaks en producción después de 48h"
   - "Docs dicen X pero el comportamiento real es Y"

4. **TRUCOS Y WORKAROUNDS** — Sabiduría callejera
   - "Usa esta config alternativa que no está en los docs"
   - "Skip el tutorial oficial y haz esto en su lugar"

5. **SEÑALES DE RECENCIA** — ¿Ha cambiado la opinión con el tiempo?
   - "En 2025 todos se quejaban de X, en 2026 ya no"
   - "La versión 2.0 solucionó todo lo que la gente odiaba"

6. **WEIGHTED SENTIMENT** — Distinguir ruido de señal
   - Queja de usuario casual → nota informativa
   - Advertencia de ingeniero senior con repos públicos → alerta seria
   - Múltiples ingenieros confirmando el mismo problema → bandera roja

> **Output interno**: lista de hallazgos sociales con peso, recencia y nivel de evidencia.

---

### FASE 3 — VERIFICACIÓN EXPERTA (columna vertebral)

Ahora se contrasta con ingeniería real. La comunidad dijo su verdad; los expertos dicen la suya.

#### Fuentes expertas:

| Fuente | Qué Buscar | Herramienta |
|---|---|---|
| **Docs oficiales** | Specs, comportamiento documentado, changelogs | `web_extract` + `web_search` con `site:docs.X.com` |
| **Ingenieros reales** | Blogs técnicos, post-mortems, deep dives | `web_search` con `site:medium.com` + blogs personales |
| **GitHub Issues/PRs** | Bugs confirmados, decisiones de diseño | `web_search` con `site:github.com` + `gh` CLI si disponible |
| **arXiv / Papers** | Estado del arte, research académico | `arxiv` skill |
| **RFCs / Specs** | Decisiones formales, trade-offs | `web_search` con `RFC` + `specification` |
| **Conferencias / Talks** | Presentaciones técnicas, reveals | `web_search` + `youtube-content` skill para transcript |
| **Stack Overflow (answers técnicas)** | Soluciones verificadas con upvotes | `web_search` con `site:stackoverflow.com` |
| **Changelogs / Release notes** | Qué cambió realmente entre versiones | `web_extract` de changelog URLs |

#### Estrategia de búsqueda experta (Counter-Query Generation):

Por CADA patrón social encontrado, generar una query experta específica:
- Social: "X tiene memory leaks" → Experta: `site:github.com X issue memory leak`
- Social: "X es más rápido que Y" → Experta: `X vs Y benchmark site:benchmark.game OR arxiv`
- Social: "La doc de X está desactualizada" → Experta: `X changelog site:github.com X/releases`
- Social: "X no escala en producción" → Experta: `X production scalability site:engineering.blog OR medium`

> **Output interno**: lista de verificaciones expertas mapeadas 1:1 a cada hallazgo social.

---

### FASE 4 — CRUCE Y CONTRASTE

Aquí es donde la magia sucede. Se cruzan los datos sociales con los expertos.

Para cada hallazgo, clasificar en:

| Categoría | Significado |
|---|---|
| ✅ **CONFIRMA** | La comunidad dice X, los expertos confirman X. Es verdad. |
| ⚠️ **MATIZA** | La comunidad tiene razón en parte, pero le falta contexto que el experto añade. |
| ❌ **CORRIGE** | La comunidad se equivoca. El experto desmiente con evidencia. |
| 💎 **REVELA** | La comunidad sabe algo que los docs NO dicen. Sabiduría callejera confirmada. |
| 🔄 **EVOLUCIONA** | La comunidad se basa en info antigua; el experto muestra que cambió. |
| ❓ **INCONCLUSO** | Ni la comunidad ni los expertos tienen respuesta clara. Decirlo honestamente. |

> **Output interno**: matriz de cruce completa con veredicto por hallazgo.

---

### FASE 5 — DICTAMEN FINAL

El output que el usuario recibe. Estructurado, opinado, sin miedo a tomar posición.

#### Template del DICTAMEN:

```markdown
# ⚖️ DICTAMEN: [TEMA]

## 📊 RESUMEN EJECUTIVO (3 oraciones máximo)
[Conclusión clara, posicionada, sin rodeos. "X es/ no es / depende de...]

## 🌐 EL TERRENO SOCIAL

### 📈 Consenso Popular
- [Punto donde la mayoría coincide] — *(N fuentes, recencia)*

### 🔥 Controversias Activas  
- [Puntos de división] — *"Un lado dice X, el otro Y"*

### ⚠️ Problemas Reales Reportados
- [Dolores concretos con evidencia] — *(ej: 12 hilos de Reddit, 5 issues en GitHub)*

### 💡 Trucos de la Comunidad (que los docs no mencionan)
- [Workaround/insight callejero]

### 📅 Línea de Tiempo de Opinión
- [Cómo ha evolucionado la percepción si aplica]

## 🔬 VERIFICACIÓN EXPERTA

### ✅ Lo que los ingenieros confirman
- [Puntos donde comunidad y expertos coinciden]

### ⚠️ Lo que los ingenieros corrigen
- [Puntos donde la comunidad se equivoca parcialmente]

### ➕ Lo que los ingenieros añaden (que la gente no sabe)
- [Contexto técnico que la comunidad no discuss]

### 📄 Fuentes técnicas verificadas
| Fuente | Tipo | Verificado |
|---|---|---|
| [Doc oficial] | Official | ✅ |
| [Blog ingeniero] | Expert | ✅ |
| [Paper arxiv] | Academic | ✅ |

## ⚖️ CRUCE: Social vs Experto

| Hallazgo | La Gente Dice | El Experto Dice | Veredicto |
|---|---|---|---|
| [Punto 1] | "X es lento" | "X tiene O(n²) worst case" | ✅ Confirma |
| [Punto 2] | "X no funciona en prod" | "Requiere tuning específico" | ⚠️ Matiza |
| [Punto 3] | "X es mejor que Y" | "Depende del caso de uso" | ❌ Corrige |

## 🏆 DICTAMEN FINAL

### Posición: [VEREDICTO CLARO]

[Razonamiento de 3-5 párrafos que integra todo lo anterior.
El veredicto NO es "depende". Es una posición clara basada en evidencia.
Si hay matices, se dicen después del veredicto principal, no como escape.]

### Nivel de Confianza: [ALTO / MEDIO / BAJO]
- Fuentes sociales: N plataformas, M datos
- Fuentes expertas: N verificadas
- Convergencia: X% de fuentes independientes coinciden

### 🎯 Recomendación Práctica
[Si el usuario está evaluando usar/comprar/adoptar X, qué le recomendamos
basado en TODO lo anterior. Acción concreta, no abstracta.]

### ⚡ Si decides usarlo/evitarlo:
- **Haz esto primero**: [Acción #1 crítica]
- **Evita esto**: [Pitfall #1 más common]
- **Configura así**: [Setup óptimo según comunidad + expertos]

## 📚 FUENTES (verificadas, no inventadas)

### Fuentes Sociales
| # | Plataforma | URL | Tipo | Recencia |
|---|---|---|---|---|
| 1 | Reddit r/X | url | Direct | 2026-07 |
| 2 | X/Twitter @dev | url | Indirect | 2026-06 |

### Fuentes Expertas
| # | Fuente | URL | Tipo |
|---|---|---|---|
| 1 | Doc oficial | url | Official |
| 2 | Blog ingeniero | url | Expert |
| 3 | Paper arxiv | url | Academic |
```

---

## Adaptabilidad por Tipo de Tema

| Tipo de Tema | Enfoque Social | Enfoque Experto | Recencia |
|---|---|---|---|
| **Tecnología/Framework** | Reddit, HN, SO, GitHub | Docs, changelogs, benchmarks | Últimos 6 meses |
| **Lenguaje de programación** | Reddit, HN, SO | Specs, RFCs, papers | Últimos 12 meses |
| **Producto/SaaS** | Reddit, X, Facebook, YouTube | Docs, reviews técnicas, comparativas | Últimos 3 meses |
| **Concepto técnico/Ciencia** | Reddit, HN, YouTube comments | arxiv, papers, academic blogs | Últimos 24 meses |
| **Controversia pública** | X, Reddit, Facebook, TikTok | Fact-checkers, sources primarias | Últimos 3 meses |
| **Herramienta de dev** | Reddit, HN, SO, GitHub Issues | Docs, benchmarks, engineering blogs | Últimos 6 meses |

---

## Reglas Críticas

### 🔴 LO QUE SIEMPRE SE HACE:

1. **Social PRIMERO, experto DESPUÉS.** El orden importa. La comunidad te dice QUÉ buscar; los expertos te dicen SI es verdad.
2. **Mínimo 3 plataformas sociales** escaneadas por investigación.
3. **Mínimo 2 fuentes expertas** para verificar hallazgos clave.
4. **Cada claim tiene evidencia** con link o tag de "no accesible".
5. **El DICTAMEN toma posición.** No "depende". No "se podría argumentar". Posición clara.
6. **Confidence Score** siempre incluido. Si la confianza es baja, decirlo.
7. **Links reales verificados.** Si una URL no se pudo acceder, se marca como indirect.

### 🟡 LO QUE NUNCA SE HACE:

1. ❌ Inventar URLs, citas, o datos que no se encontraron
2. ❌ Dar "depende" como veredicto principal (es cobardía analítica)
3. ❌ Solo usar Google sin tocar plataformas sociales
4. ❌ Solo usar docs oficiales sin escuchar a la comunidad
5. ❌ Mezclar opiniones antiguas con actuales sin aclarar
6. ❌ Presentar snippets de búsqueda como si fueran lecturas directas
7. ❌ Omitir que una plataforma estaba bloqueada si lo estaba

---

## Manejo de Bloqueos y Limitaciones

| Problema | Solución |
|---|---|
| Reddit API 403 | Usar `old.reddit.com` HTML con User-Agent de navegador |
| X/Twitter bloquea | `web_search` con `site:x.com` y marcar como INDIRECT |
| Facebook requiere login | `web_search` con `site:facebook.com/groups` + snippets |
| YouTube comentarios inaccesibles | Transcript del video = opinión del creador; buscar videos de review |
| TikTok search limitado | `web_search` con `site:tiktok.com "TEMA"` (mínimo) |
| Discord requiere invite | `web_search` con `site:discord.com` para servidores públicos indexados |

**Siempre reportar** qué se pudo acceder y qué no. La transparencia es parte del dictamen.

---

## Integración con otros Skills

Este skill orquesta otros skills disponibles:

- `social-platform-trend-research` → escaneo inicial de Reddit/X
- `arxiv` → papers académicos cuando el tema es técnico/científico
- `youtube-content` → transcripts de videos de review/opinión
- `blogwatcher` → monitoreo de blogs técnicos
- `grounded-citations` → verificación de citas y fuentes

No se reemplazan; se combinan en un flujo coherente.

---

## Verificación Final del Dictamen

Antes de entregar el dictamen al usuario, verificar:

- [ ] ¿Mínimo 3 plataformas sociales fueron escaneadas?
- [ ] ¿Mínimo 2 fuentes expertas verificaron hallazgos clave?
- [ ] ¿El veredicto toma una posición clara (no "depende")?
- [ ] ¿Cada claim tiene fuente o tag de acceso?
- [ ] ¿El Confidence Score es honesto?
- [ ] ¿Las plataformas bloqueadas están reportadas?
- [ ] ¿La recencia de las fuentes es apropiada para el tema?
- [ ] ¿Los links son reales (no inventados)?

---

## Notas del Autor

Este skill fue diseñado para responder a una pregunta filosófica:
"¿Qué sabe la gente que los docs no dicen, y qué saben los docs
que la gente no entiende?"

El resultado no es un resumen. Es un **dictamen**.
