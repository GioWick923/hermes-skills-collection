---
category: prompt-engineering
name: prompt-engineering-library
version: "1.0.0"
description: "Librería de prompts industriales (523 casos) extraída de awesome-gpt-image-2. Búsqueda por categoría/estilo/escena, composición de prompts desde plantillas, y inspiración aleatoria."
argument-hint: "buscar arquitectura | prompt producto zapatos | inspirame 3"
allowed-tools: Bash, Read, Write, Python
homepage: https://github.com/freestylefly/awesome-gpt-image-2
author: <GITHUB_USER>
license: MIT
user-invocable: true
---

# prompt-engineering-library

Tu **"libro memoria"** de prompt engineering industrial. Basado en **523 casos reales** de [awesome-gpt-image-2](https://github.com/freestylefly/awesome-gpt-image-2) — prompts reverse-engineered de GPT-Image-2, categorizados, con estilos y escenas.

## Qué tienes

| Recurso | Cantidad |
|---------|----------|
| Casos industriales | **523** |
| Categorías | 13 |
| Estilos | 19 |
| Escenas | 10 |
| Plantillas extraídas | 13 (una por categoría) |

## Instalación

```bash
# Ya está en ~/skills/prompt-engineering-library/
# Casos descargados en references/gpt-image-2-cases.json
```

## Scripts

### 1. Buscar casos

```bash
# Por categoría
python scripts/search-cases.py --category "Products & E-commerce" --count 3

# Por estilo
python scripts/search-cases.py --style "Realistic" --count 5

# Por escena
python scripts/search-cases.py --scene "Fashion" --count 3

# Por palabra clave en el prompt
python scripts/search-cases.py --keyword "volumetric lighting"

# Aleatorios para inspiración
python scripts/search-cases.py --random 5

# Listar todo
python scripts/search-cases.py --list-categories
python scripts/search-cases.py --list-styles
python scripts/search-cases.py --list-scenes
```

### 2. Componer prompts (build-prompt.py)

```bash
# Producto
python scripts/build-prompt.py --template product \
  --subject "zapatillas running" \
  --lighting "studio softbox" \
  --mood "premium" \
  --camera "macro 100mm f/2.8"

# Arquitectura
python scripts/build-prompt.py --template architecture \
  --subject "casa minimalista concreto" \
  --lighting "golden hour" \
  --mood "sereno" \
  --camera "wide angle 24mm"

# Personaje
python scripts/build-prompt.py --template character \
  --subject "mujer ejecutiva" \
  --lighting "cinematic rim light" \
  --mood "confident"
```

## Estructura de un prompt industrial (Prompt as Code)

Basado en los 523 casos, un prompt profesional se descompone en:

```
[SUJETO] + [ENTORNO] + [ILUMINACIÓN] + [CÁMARA] + [ESTILO] + [NEGATIVOS]
```

| Componente | Ejemplo |
|------------|---------|
| **Sujeto** | "zapatilla running Nike Air Zoom, colorway volt/black, detalles reflectantes" |
| **Entorno** | "estudio fotográfico, fondo blanco limpio, superficie reflectante sutil" |
| **Iluminación** | "key light softbox frontal-izquierda, fill light derecha, rim light trasero cálido" |
| **Cámara** | "macro 100mm f/2.8, ISO 100, 1/125s, enfoque en logo lateral" |
| **Estilo** | "hyperrealistic, 8K, commercial product photography, Octane render" |
| **Negativos** | "no texturas borrosas, no sobreeexposición, no fondos distractores, no deformaciones" |

## Categorías disponibles

| Categoría | Casos | Ideal para |
|-----------|-------|------------|
| Posters & Typography | 84 | Carteles, tipografía, diseño gráfico |
| Photography & Realism | 76 | Fotografía realista, retratos, producto |
| UI & Interfaces | 73 | Interfaces, dashboards, apps, web |
| Illustration & Art | 58 | Ilustración, arte conceptual, estilos |
| Charts & Infographics | 52 | Gráficos, visualización de datos |
| Products & E-commerce | 40 | **Producto, ecommerce, comercial** |
| Other Use Cases | 28 | Varios |
| Characters & People | 27 | Personajes, gente |
| Brand & Logos | 27 | Branding, logos, identidad |
| Scenes & Storytelling | 20 | Escenas narrativas |
| History & Classical Themes | 16 | Histórico, clásico |
| Architecture & Spaces | 12 | Arquitectura, interiores |
| Documents & Publishing | 10 | Documentos, editorial |

## Estilos más usados

| Estilo | Casos | Cuándo usarlo |
|--------|-------|---------------|
| UI | 238 | Interfaces, dashboards, apps |
| Realistic | 202 | Foto realista, producto, retrato |
| Poster | 187 | Carteles, composiciones gráficas |
| Character | 111 | Personajes, gente |
| Illustration | 99 | Ilustración artística |
| Brand | 82 | Branding, identidad visual |
| Infographic | 74 | Gráficos, datos visuales |
| Product | 55 | Fotografía de producto |
| 3D | 39 | Renders 3D, C4D, Blender |

## Ejemplos rápidos

### Producto e-commerce
```bash
python scripts/search-cases.py --category "Products & E-commerce" --style Realistic --count 2
```

### Arquitectura interior
```bash
python scripts/search-cases.py --category "Architecture & Spaces" --count 3
```

### UI Dashboard
```bash
python scripts/search-cases.py --category "UI & Interfaces" --style UI --count 3
```

### Inspiración aleatoria
```bash
python scripts/search-cases.py --random 5
```

## Integración con tu stack local

Como tienes **Forge / Stable Diffusion WebUI** en local (RTX 3060 12GB):

1. Buscas el caso: `python scripts/search-cases.py --category "Products & E-commerce" --count 1`
2. Copias el prompt
3. Lo pegas en Forge (txt2img o img2img)
4. Ajustas: steps=20-30, CFG=7, sampler=DPM++ 2M Karras
5. ¡Generas gratis e ilimitado!

## Mantenimiento

Para actualizar los casos:
```bash
curl -sL "https://raw.githubusercontent.com/freestylefly/awesome-gpt-image-2/main/data/cases.json" \
  -o skills/prompt-engineering-library/references/gpt-image-2-cases.json
```

## Próximos pasos

- [ ] Script `build-prompt.py` con plantillas por categoría
- [ ] Script `negative-prompts.py` — extraer negativos de los casos
- [ ] Templates YAML por categoría en `templates/`
- [ ] Integración directa con Forge API (`/sdapi/v1/txt2img`)

---

**Filosofía:** *Prompt as Code* — versiona, compone, itera. No copies, **entender y adapta**.