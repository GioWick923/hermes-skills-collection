---
name: portrait-ultrareal
description: "Generate ultra-realistic portraits from reference images. Uses ComfyUI + UltraReal workflow with IP-Adapter FaceID to preserve identity. Use when user wants photorealistic portrait from their photo."
metadata:
  hermes:
    tags: [portrait, ultra-real, face, generation, comfyui]
    category: creative
---

# Portrait UltraReal Generator

Genera retratos ultra-realistas a partir de imágenes de referencia, preservando la identidad facial.

## Workflow

```
Foto referencia → Vision analysis → Prompt generation → IP-Adapter FaceID → Flux 2 Klein upscale → Ultra-real portrait
```

## Uso

### Opción 1: Generar desde imagen
1. Pasar imagen de referencia (selfie, foto)
2. Yo analizo características faciales
3. Genero prompt optimizado
4. Ejecuto workflow en ComfyUI
5. Resultado: retrato ultra-realista

### Opción 2: Desde cero
- Describir persona (edad, género, estilo)
- Generar con atributos específicos

## Parámetros

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `style` | "photorealistic" | Estilo (photorealistic, cinematic, editorial) |
| `quality` | "high" | Calidad (standard, high, ultra) |
| `resolution` | 1024x1024 | Resolución de salida |
| `steps` | 30 | Steps de denoising |

## Requisitos

- ComfyUI corriendo en `http://localhost:8188`
- Nodes: Krea 2 Turbo, Flux 2 Klein, IP-Adapter FaceID
- GPU: RTX 3060+ (12GB VRAM recomendado)

## Archivos

- **Workflow:** `C:\Users\<USER>\Documents\comfy\ComfyUI\workflows\ultrareal-krea2-flux.json`
- **Skill:** `~/.hermes/skills/comfyui-ultrareal/SKILL.md`

## Output

Las imágenes se guardan en:
```
C:\Users\<USER>\Documents\comfy\ComfyUI\output\
```
