---
name: anime-to-real
description: "Convert anime/manga images to photorealistic portraits using img2img + UltraReal workflow. Use when user wants to transform anime characters into real people preserving features."
metadata:
  hermes:
    tags: [anime, real, img2img, conversion, portrait]
    category: creative
---

# Anime to Real Converter

Convierte imágenes anime/manga a retratos fotorrealistas preservando características faciales.

## Pipeline

```
Anime Image → Img2Img (Realistic Vision) → Base Real → IP-Adapter FaceID → Flux 2 Klein → UltraReal Portrait
```

## Pasos

### 1. Convertir anime a real base
- Modelo: `Realistic_Vision_V5.1` o `EpicRealism`
- Denoising: 0.4-0.5 (preservar composición)
- Preservar: colores de pelo, ojos, rasgos faciales

### 2. Aplicar UltraReal
- Workflow: `ultrareal-krea2-flux.json`
- IP-Adapter FaceID para preservar identidad
- Flux 2 Klein para textura de piel ultra-realista

## Prompt para conversión

```
photorealistic portrait, detailed skin texture, 
pores visible, natural lighting, 
[COLOR] hair, [COLOR] eyes, 
professional headshot, 8k uhd, dslr, 
soft lighting, high quality, film grain
```

## Parámetros

| Parámetro | Valor | Razón |
|-----------|-------|-------|
| denoising | 0.45 | Balance entre realidad y preservación |
| steps | 30-40 | Calidad suficiente |
| cfg | 7.0 | Guía moderada |
| sampler | DPM++ 2M Karras | Buen balance calidad/velocidad |
| resolution | 1024x1024 | Compatibilidad con UltraReal |

## Output

- Imagen intermedia: `output/anime-to-real-base.png`
- Final: `output/anime-to-real-ultrareal.png`

## Nodes requeridos

- [ ] Checkpoint: Realistic_Vision_V5.1
- [ ] VAЕ: sdxl_vae (si usa SDXL)
- [ ] IP-Adapter FaceID
- [ ] Flux 2 Klein (para upscale final)
- [ ] Krea 2 Turbo (opcional, para quality boost)

## Variaciones

- **Más realista**: denoising 0.6
- **Más fiel al anime**: denoising 0.3
- **Diferente estilo**: cambiar checkpoint (PhotoReal, etc.)
