---
category: research
name: technical-comparative-research
description: "Compare hardware options with metrics, deliver visual docs."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, technical, comparative, expert-verdict, hardware, electronics, svg-diagram, bom, pinout, html-deliverable]
    related_skills: [verdict-research, architecture-diagram, grounded-citations]
---

# 🔬 Technical Comparative Research — Veredicto Experto + Documento Visual

Investiga un tema **técnico físico** (hardware DIY, electrónica, energía, circuitos, módulos, automotriz), compara opciones con **métricas reales** extraídas de fuentes verificadas (datasheets, BOM, tutoriales, foros técnicos), emite un **veredicto de experto fundamentado**, y entrega un **documento HTML autocontenido** con esquema SVG + BOM + tablas técnicas + guía de montaje.

Es el skill correcto cuando el usuario dice: *"busca info de X, analiza cuál es mejor en potencia/rendimiento/calentamiento, y dame links de lo que encontraste"* y X es hardware físico, no software/SaaS.

## Cuándo usar

- **Trigger phrases**: "busca info de...", "investiga transformadores/inversores/circuitos...", "analiza cuál es mejor en [métrica física]...", "compara estos chips/topologías...", "dame links de lo que encontraste" + tema técnico hardware.
- **Dominio**: electrónica, circuitos, inversores, transformadores, módulos, energía solar, automotriz, motores, audio DIY, Arduino/Raspberry wiring, power supplies.
- **Entregable esperado**: links verificados + tabla comparativa + veredicto + (opcional) documento HTML con esquema.

## Cuándo NO usar

- **Social-first research** (sentimiento de producto, opiniones de usuarios, adopción de framework) → `verdict-research`.
- **Papers académicos de 30-40 páginas** → `deep-researcher`.
- **Diagramas de arquitectura software/cloud** → `architecture-diagram`.
- **Pregunta factual de 1 línea** → basta `web_search` directo.

## Flujo

### FASE 1 — Búsqueda técnica dirigida (paralelo)

Lanzar **3-4 `web_search` en paralelo** con queries optimizadas al dominio:

1. **Query general en español** (el tema suele tener más contenido en español si el usuario hispanohablante lo pide): `"<tema> <especificación> casero DIY tutorial"`
2. **Query técnica en inglés** (datasheets, comparativas, foros técnicos angloparlantes): `"<topic> <spec> schematic comparison efficiency 2024"`
3. **Query de comparativa específica** (si hay topologías/chips candidatos): `"CD4047 vs SG3525 vs NE555 <topic> efficiency power"`
4. **Query de limitaciones/seguridad** (clave para el veredicto): `"<topic> heating limitations power output waveform`

**Fuentes prioritarias para hardware DIY**:
- Foros técnicos: electronics.stackexchange.com, forosdeelectronica.com, eevblog.com
- Tutoriales paso a paso: instructables.com, how2electronics.com, homemade-circuits.com
- Videos: YouTube (con fechas para recencia), TikTok técnicos
- Datasheets: siempre que se mencione un chip, buscar su datasheet para pines, corrientes máximas, dead-time

> **Output interno**: matriz de fuentes con URL, tipo (foro/tutorial/video/datasheet), recencia, y datos extraíbles.

### FASE 2 — Verificación de fuentes (browser_navigate + read_file)

**No confiar solo en snippets de búsqueda.** Para las 2-3 fuentes más relevantes:

1. `browser_navigate` a la URL del artículo
2. Leer el snapshot completo (includes tables, BOM, pinout, valores de componentes)
3. Si el snapshot se trunca, usar `read_file` al path del snapshot cacheado con `offset` para paginar
4. **Extraer datos verificables**: valores de resistencias, capacitores, número de pines, conexión pin-a-pin, potencias declaradas, limitaciones documentadas

Esta fase es la que diferencia un dictamen "de internet" de un dictamen **experto fundamentado**. El usuario valora "verifiqué el BOM en la fuente real" sobre "encontré un link que dice X".

### FASE 3 — Comparativa técnica con métricas físicas

Construir tabla comparativa con **columnas de métricas físicas reales**, no opiniones:

| Opción | Potencia real | Rendimiento | Calentamiento | Métrica clave (topología) | Seguridad |
|---|---|---|---|---|---|
| Diseño A | 30-100W | ~60% | Alto | sin dead-time | peligrosa |
| Diseño B | 300-1000W | ~85% | Bajo | dead-time integrado | estable |

**Las métricas se sacan de las fuentes verificadas**, no se inventan. Si una métrica no se encontró, se marca "no documentado" — NUNCA se completa con un número plausible.

### FASE 4 — Veredicto de experto

El veredicto NO es "depende". Es una posición clara:

1. **Seleccionar el ganador** con justificación técnica (no "es más popular" sino "gana porque dead-time integrado + etapa totem-pole + RDS(on) baja = menos conmutación lineal = menos calor").
2. **Explicar la física del porqué** — el usuario quiere entender, no solo la conclusión. Ej: "los MOSFETs nunca conducen a la vez → elimina el cortocircuito momentáneo que es la causa #1 de calor en inversores sin dead-time".
3. **Descartar las opciones perdedoras con razón técnica** — no "es peor" sino "sin dead-time su techo honesto son ~200W, por eso se queda corto".
4. **Advertir limitaciones de seguridad** — a 220V hay riesgo real de muerte; a 1000W/12V hay 83A que requieren cable ≥10mm².

### FASE 5 — Entregable: documento HTML autocontenido (opcional pero valioso)

Si el usuario quiere el esquema o dice "dame el documento/armá el esquema":

Generar un `.html` standalone con:
- **Esquema SVG inline** (dark theme, self-contained, sin JS) — ver `references/electronic-circuit-diagrams.md` para el patrón de renderizado y verificación
- **BOM (Bill of Materials)** en tabla con cantidad, componente, referencia
- **Pinout table** (pin → función → conectar a) para ICs
- **Guía de montaje** paso a paso
- **Bloque de seguridad** obligatorio para alta tensión/corriente
- **Links a fuentes verificadas** al final

Guardar con `write_file` al Escritorio del usuario (o donde pida). Sugerir `open_preview` para verlo en el panel de Hermes.

## Técnica clave: verificación de SVG por DOM (cuando browser_vision falla)

`browser_vision` puede fallar si el modelo activo no soporta visión o el endpoint está saturado. La verificación por DOM es un fallback confiable:

```javascript
// browser_console expression
(() => {
  const s = document.querySelector('svg');
  if(!s) return JSON.stringify({hasSvg:false});
  const r = s.getBoundingClientRect();
  return JSON.stringify({
    hasSvg: true,
    svgW: Math.round(r.width),
    svgH: Math.round(r.height),
    textElements: s.querySelectorAll('text').length,
    viewBox: s.getAttribute('viewBox')
  });
})()
```

- `hasSvg: true` + `textElements > 0` → el SVG está en el DOM con labels
- `svgW/svgH` dentro del viewBox → renderizado al tamaño esperado
- Los "overflow" de `getBBox()` en elementos dentro de `<g transform>` son **falsos positivos** — sus coordenadas son locales al grupo, no globales
- Si `hasSvg: false` tras `browser_navigate`, el browser reseteó a `about:blank` — re-navegar al file URL antes del console check

## Pitfalls

- **Confiar en snippets de búsqueda como verificación**: un snippet que dice "300W output" no confirma que el circuito entrega 300W — leer el artículo real, buscar el BOM y la tabla de componentes.
- **web_extract fallando en DuckDuckGo backend**: si `web.extract_backend=ddgs`, `web_extract` devuelve error ("search-only backend"). Usar `browser_navigate` + leer el snapshot cacheado.
- **browser_vision fallando con "not a multimodal model"**: el modelo activo (e.g. deepseek-v4-flash) puede no soportar visión. Usar la verificación por DOM de arriba — no bloquear el entregable esperando análisis visual.
- **browser_console devolviendo `about:blank`**: el browser se resetea entre llamadas. Siempre `browser_navigate` inmediatamente antes de `browser_console` al verificar un file local.
- **Inventar métricas físicas**: si no se encontró el rendimiento exacto de una topología, poner "no documentado" — nunca completar con un número plausible. El usuario confía en que las cifras vienen de fuentes reales.
- **Omitir la aclaración conceptual**: el usuario quiere entender la física (por qué un diseño se calienta más que otro), no solo la conclusión. Siempre explicar el porqué técnico del veredicto.
- **No distinguir "transformador" de "inversor"**: en hardware DIY, aclarar conceptos mal usados. Un transformador solo no convierte DC→AC; necesita un oscilador. Esto es valor experto.

## Integración con otros skills

- **`grounded-citations`**: si el entregable requiere citas inline con ledger, usar `sources.py` para registrar URLs y renderizar el bloque Sources.
- **`verdict-research`**: para la dimensión social del mismo tema (qué dice la comunidad en Reddit/X), complementa este skill. No reemplaza — se combina.
- **`architecture-diagram`**: si el esquema es de software/cloud, no de electrónica. Para circuitos, usar el patrón de `references/electronic-circuit-diagrams.md`.

## Verificación final del entregable

- [ ] ¿Mínimo 2-3 fuentes verificadas con `browser_navigate` (no solo snippets)?
- [ ] ¿Los datos técnicos (BOM, pinout, métricas) vienen de la fuente real leída?
- [ ] ¿La tabla comparativa tiene métricas físicas (potencia, rendimiento, calentamiento)?
- [ ] ¿El veredicto toma posición clara (no "depende")?
- [ ] ¿La justificación técnica explica la física del porqué?
- [ ] ¿Las opciones perdedoras se descartan con razón técnica?
- [ ] ¿Las limitaciones de seguridad están documentadas (voltaje/corriente peligrosos)?
- [ ] ¿Los links son reales y verificados?
- [ ] (Si HTML entregable) ¿El SVG se verificó por DOM (hasSvg + textElements + viewBox)?
- [ ] (Si HTML entregable) ¿El archivo es standalone (CSS+SVG inline, sin JS, sin deps externas)?

## Referencias

- `references/electronic-circuit-diagrams.md` — Patrón detallado de esquemas electrónicos SVG, tabla BOM, tabla pinout, bloque de seguridad, y técnica de verificación de SVG por DOM cuando browser_vision falla.
