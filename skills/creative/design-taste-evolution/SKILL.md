---
name: design-taste-evolution
description: "When designing UIs, routes ui-ux-pro-max and taste-skill."
version: 1.0.0
author: Hermes (evolución de Leonxlnx/taste-skill + ui-ux-pro-max)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ui, ux, design, design-system, frontend, taste-skill, anti-slop]
    related_skills: [ui-ux-pro-max, design-taste-frontend, high-end-visual-design, claude-design, popular-web-designs]
---

# Design Taste Evolution

Ruta unificada para diseño de UI en Hermes. **Evoluciona** la colisión entre
`ui-ux-pro-max` (inteligencia de diseño basada en datos) y los skills de
`taste-skill` (dirección anti-slop) en un solo flujo. No duplica: **selecciona el
skill correcto según la fase**.

## Por qué existe (colisión resuelta)

| Aspecto | ui-ux-pro-max | design-taste-frontend | Veredicto evolución |
|--------|----------------|------------------------|---------------------|
| Datos (estilos/paletas/fonts/UX) | ✅ 79 estilos, 192 paletas, 74 fonts | ❌ no tiene | **ui-ux-pro-max** gana |
| Dirección anti-slop / leer el brief | ❌ genérico | ✅ BRIEF INFERENCE + anti-defaults | **design-taste-frontend** gana |
| Diale "varianza" | `--variance 1-10` | `DESIGN_VARIANCE 1-10` | **mismos valores**, usar indistintamente |
| Diale "movimiento" | `--motion 1-10` | `MOTION_INTENSITY 1-10` | **mismos valores**, usar indistintamente |
| Diale "densidad" | `--density 1-10` | `VISUAL_DENSITY 1-10` | **mismos valores**, usar indistintamente |
| Implementación código | ✅ stacks (react/next/tailwind...) | ⚠️ esqueleto GSAP | **ui-ux-pro-max** para stack |

## Flujo único (evolución)

```
1. LEER EL BRIEF  → design-taste-frontend §0 (BRIEF INFERENCE)
   → output: "Reading this as: <kind> for <audience>, <vibe> language"
2. SET DIALES     → los 3 diales 1-10 (compartidos entre ambos)
   DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY
3. DIRECCIÓN      → design-taste-frontend (anti-slop, layout, motion, spacing)
   anti-defaults: NO purple-gradients, NO centered-hero-over-mesh, NO 3 equal cards
4. DATOS CONCRETOS → ui-ux-pro-max: `python scripts/search.py "<query>" --design-system`
   - paletas → --domain color
   - fonts   → --domain typography / --domain google-fonts
   - layout  → --domain landing / --domain style
   - a11y/UX → --domain ux (ui-ux-pro-max)
5. IMPLEMENTAR   → ui-ux-pro-max --stack <react|nextjs|tailwind...> + snippets GSAP
6. REDESIGN (opcional) → redesign-existing-projects (audita primero)
```

## Regla de oro

- **Dirección / estética / anti-slop** → skills de taste (design-taste-frontend,
  high-end-visual-design, minimalist-ui, industrial-brutalist-ui según el read).
- **Datos / paleta / font / a11y / stack / checklist final** → ui-ux-pro-max.
- Los **3 diales son los mismos** en ambos — no los configures dos veces.
- Para **imágenes de referencia** (no código) → imagegen-frontend-web /
  imagegen-frontend-mobile / brandkit, y luego image-to-code si toca implementar.

## Checklist de selección rápida

| Petición | Skill a cargar |
|----------|----------------|
| "haz una landing" | design-taste-frontend (dirección) + ui-ux-pro-max (datos/stack) |
| "mejora mi web existente" | redesign-existing-projects |
| "quiero referencia visual" | imagegen-frontend-web / brandkit |
| "estilo premium caro" | high-end-visual-design |
| "estilo minimalista" | minimalist-ui |
| "estilo brutalista" | industrial-brutalist-ui |
| "paleta/font/stack concreto" | ui-ux-pro-max |

## Verificación

- Tras un deliverable de UI: revisar anti-defaults de taste + checklist pre-entrega
  de ui-ux-pro-max (contraste ≥4.5:1, touch targets ≥44pt, no emoji como icono).
