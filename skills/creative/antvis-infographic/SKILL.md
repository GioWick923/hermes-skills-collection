---
category: creative
name: antvis-infographic
description: "Render professional infographics from AntV Infographic DSL using @antv/infographic (276 built-in templates). Use when the user wants a data/info graphic, visual summary, or infographic with real SVG output."
version: 1.0.0
author: Hermes Agent (installed @antv/infographic 0.2.19)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [infographic, visualization, antv, svg, visual-summary, creative]
    homepage: https://github.com/antvis/Infographic
---

# AntV Infographic Generator

Renders high-quality **SVG infographics** from the AntV Infographic declarative DSL, using the
installed `@antv/infographic@0.2.19` npm package. No browser required — runs headless in Node via a
linkedom DOM shim (already bundled in the runner).

This complements (does NOT replace) `baoyu-infographic`. Use this skill when you want:
- Real, editable **SVG** output (not an image render),
- Access to **276 built-in AntV templates** (lists, hierarchies, comparisons, timelines, pyramids, etc.),
- Data-driven infographics with icons, palettes, and themes,
- A deterministic, scriptable pipeline you can re-run.

Use `baoyu-infographic` instead when the user wants the 21-layout × 21-style hand-crafted aesthetic
or a more "designed poster" look. Both can coexist.

## When to Use (trigger)
- User asks for an "infographic", "info graphic", "visual summary", "data graphic", "resumen visual",
  "infografía", or wants to turn bullet points / data into a shareable graphic.
- User provides structured content (title, items, values, comparisons) and wants a clean SVG.
- As an automatic fallback when a request clearly maps to a known AntV template shape.

## Environment (already installed)
- Package: `@antv/infographic@0.2.19` in `C:\Users\<USER>\AppData\Local\hermes\tools\antv_infographic\node_modules`
- Runner: `tools/antv_infographic/render_infographic.js` (Node 22, npm 10)
- 276 templates available via `getTemplates()`.

## How to Use

### Step 1 — Pick a template
List available templates:
```bash
cd "C:/Users/<USER>/AppData/Local/hermes/tools/antv_infographic" && node -e "console.log(require('./render_infographic.js').getTemplates().join('\n'))"
```
Choose by shape (NOT by habit):
- `list-*` → bullet / item lists (icons, values, badges)
- `compare-*` → side-by-side comparisons
- `list-pyramid-*` → hierarchy / pyramid
- `sequence-*` / `timeline-*` → steps over time
- `tree-*` / `hierarchy-*` → org / mind structures

### Step 2 — Write the DSL
First line MUST be `infographic <template-name>`. Use 2-space indents. Key-value = `key value`.
Object arrays use `-` prefix. Fill `icon` semantically (e.g. `document text`, `cpu`, `rocket launch`).

Example DSL:
```
infographic list-row-horizontal-icon-arrow
data
  title Rendimiento del Sistema
  desc Resumen mensual de metricas
  lists
    - label CPU
      value 78%
      desc Uso promedio
      icon cpu
    - label RAM
      value 64%
      desc Disponible
      icon memory
theme
  palette #3b82f6 #8b5cf6 #f97316
```

### Step 3 — Render to SVG
```bash
cd "C:/Users/<USER>/AppData/Local/hermes/tools/antv_infographic" && node render_infographic.js <dsl-file-or-string> <out.svg>
```
Or from Node:
```js
const { renderInfographic } = require('C:/Users/<USER>/AppData/Local/hermes/tools/antv_infographic/render_infographic.js');
renderInfographic(dslString, 'C:/Users/<USER>/Pictures/1hermes proyectos/2026-08-18 - mi infografia.svg');
```

### Step 4 — Deliver
Per user rule (MEMORY.md 2026-08-18): save deliverables to the typed Windows library and SHOW inline.
- Save SVG to `C:\Users\<USER>\Pictures\1hermes proyectos\YYYY-MM-DD - <titulo corto>.svg`
- Present it in chat with `MEDIA:/absolute/path.svg` so the user sees it immediately.
- SVG is editable: user can open in browser / Inkscape / the AntV online editor.

## Notes / Constraints
- Language lock: if user writes Spanish, keep `title`/`desc`/`label` in Spanish (do not auto-translate).
- Icons: use semantic phrases with spaces (`rocket launch`), not hyphens (`rocket-launch`), unless using exact IDs like `mingcute/server-line`.
- `render()` takes the **DSL string**, NOT the parsed object. The runner handles the DOM shim.
- Output is SVG (vector). If a raster PNG is needed later, convert with a separate tool (e.g. rsvg-convert / sharp / browser).

## Reference
- Official skills (for deeper DSL rules): https://github.com/antvis/Infographic/tree/main/skills
- Docs: https://infographic.antv.vision/learn
- Gallery: https://infographic.antv.vision/gallery
