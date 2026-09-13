# Face Swap & Portrait Realism - Decision Guide

> Para Krea2-Turbo-SVDQuant en RTX 3060 12GB. Actualizado sept 2026.

## Decisión: ¿Cómo lograr el mejor resultado?

### Escenario 1: Referencia facial REAL disponible (foto real de la persona)
```
Face Clone (OpenCV+InsightFace) → img2img denoise BAJO (0.15-0.25)
```
- **Resultado:** Identidad facial perfecta + cuerpo/pose/ropa preservados
- **Requisito:** Ambas imágenes deben tener caras reales detectables
- **Riesgo:** Si el composito falla (glitches), fallback a Escenario 2

### Escenario 2: No hay ref facial o el composito falló
```
img2img denoise MODERADO (0.55) + prompt descriptivo detallado
```
- **Resultado:** Rostro plausible basado en descripción textual
- **Ventaja:** No requiere composito previo
- **Limitación:** El parecido depende de la calidad del prompt

### Escenario 3: Transformar estilo (anime → real)
```
img2img denoise ALTO (0.80-0.85) + prompt fotográfico
```
- **Resultado:** Reconstrucción completa hacia realismo
- **Ventaja:** Cambia el estilo completamente
- **Limitación:** Pierde detalles finos de la referencia original

## Parámetros validados

| Parámetro | Valor recomendado | Nota |
|-----------|-------------------|------|
| steps | 4-6 | Krea2-Turbo es destilado, 4 bastan |
| cfg | 1.0 | Obligatorio (cfg-distilled) |
| sampler | euler | Simple y estable |
| scheduler | simple | "normal" genera ruido visible |
| denoise (face-swap preciso) | 0.15-0.25 | Preserva todo excepto rostro |
| denoise (transformación estilo) | 0.80-0.85 | Reconstruye todo |
| denoise (balance) | 0.55 | Mejor compromise |

## Checklist de validación post-generación

- [ ] ¿El rostro se parece a lacelebridad descrita? (usar vision_analyze)
- [ ] ¿La pose es idéntica a la referencia?
- [ ] ¿La ropa/orup = Identico? (colores, logos, ajuste)
- [ ] ¿El setting/fondo se preservo?
- [ ] ¿Hay glitches en el rostro (máscaras negras, artefactos)?
- [ ] ¿La textura de piel es aceptable o muy "plástica"?

## Templates de prompt validados

### Prompt para Sadie Sink
```
photorealistic portrait of Sadie Sink actress: strawberry-blonde wavy shoulder-length hair, distinctive freckles across nose and cheeks, green-blue almond-shaped eyes, natural skin texture with visible pores, wearing white raglan crop top with blue sleeves and cat logo, white low-rise pants with belt, standing in sunny pine forest with bright blue sky, golden sunlight rays, curvy voluptuous figure, shot on Canon EOS R5 50mm f/1.4, film grain, editorial fashion photography, no retouching, raw photo, cinematic lighting, photorealistic, 8k
```

### Prompt para Angelina Jolie
```
portrait photograph of a woman resembling Angelina Jolie: full natural lips, striking green-blue almond-shaped eyes, high defined cheekbones, pale smooth skin with natural texture and subtle pores, long dark straight hair, wearing black beanie cap, black off-shoulder cropped sweater, gray heathered sweatpants joggers with drawstring, seated on a bed in a cozy bedroom, large window with raindrops on glass showing overcast grey sky, warm fairy string lights on walls, soft diffused daylight mixed with warm indoor lighting, shot on Canon EOS R5 50mm f/1.4, film grain, natural skin tones, no retouching, raw photo, editorial fashion photography style
```

### Keywords esenciales de realismo
- `portrait photograph`
- `shot on Canon EOS R5 50mm f/1.4` (o lente similar)
- `film grain`
- `natural skin texture with visible pores`
- `no retouching`
- `raw photo`
- `editorial fashion photography`

## Scripts útiles

- `face_clone.py` - Composito facial con OpenCV+InsightFace
- `face_clone_v3.py` - Versión corregida con manejo de errores
- `launch_comfy.ps1` - Launcher con logs a archivo (evita OSError 22)

## Rutas de trabajo

- Imágenes base: `C:/Users/<USER>/Pictures/modelos imag/`
- Input ComfyUI: `F:/ComfyUI/input/`
- Output: `F:/ComfyUI/output/`
- Backup final: `C:/Users/<USER>/Pictures/modelos imag/`
- Workflows guardados: `C:/Users/<USER>/Downloads/*.json`
