---
name: comfyui-ultrareal
description: "Ultra-realistic portrait workflow using Krea 2 Turbo + Flux 2 Klein. Use when user wants photorealistic portraits, skin texture restoration, or high-quality headshots."
metadata:
  hermes:
    tags: [comfyui, image-generation, ultra-real, krea, flux]
    category: creative
---

# ComfyUI UltraReal Workflow

Workflow para retratos ultra-realistas combinando Krea 2 Turbo y Flux 2 Klein.

## Qué hace

- **Krea 2 Turbo**: Generación inicial de imagen
- **Flux 2 Klein**: Upscale y refinamiento de textura de piel
- **Resultado**: Retratos fotorrealistas de alta calidad

## Instalación

El workflow ya está instalado en:
```
C:\Users\<USER>\Documents\comfy\ComfyUI\workflows\ultrareal-krea2-flux.json
```

## Uso

### Opción 1: Desde ComfyUI Web UI
1. Abrir ComfyUI: `http://localhost:8188`
2. Drag & drop del archivo `.json` al canvas
3. Adjust parameters (prompt, seed, etc.)
4. Click "Queue Prompt"

### Opción 2: Línea de comandos
```bash
cd ~/Documents/comfy/ComfyUI
python main.py --input workflows/ultrareal-krea2-flux.json
```

## Parámetros principales

| Parámetro | Valor default | Descripción |
|-----------|---------------|-------------|
| `positive_prompt` | "" | Prompt descriptivo |
| `negative_prompt` | "" | Lo que NO quieres |
| `seed` | random | Seed para reproducibilidad |
| `steps` | 30 | Steps de denoising |
| `cfg` | 7.5 | Classifier-free guidance |
| `width` | 1024 | Ancho de salida |
| `height` | 1024 | Alto de salida |

## Requisitos

- ComfyUI instalado
- Nodes requeridos:
  - Krea 2 Turbo (node personalizado)
  - Flux 2 Klein (node personalizado)
  - Uploaders para output

## Check nodes

```bash
cd ~/Documents/comfy/ComfyUI
./install.sh  # O manual: pip install -r requirements.txt
```

## Output

Las imágenes se guardan en:
```
~/Documents/comfy/ComfyUI/output/
```

## Variaciones

Puedes modificar el workflow para:
- Diferentes aspect ratios
- Menos steps (más rápido)
- Plus quality (más steps)
- Diferentes styles (adjust prompt)

## Links

- [Repo original](https://github.com/paxvel1/ComfyUI-UltraReal-Workflows)
- [Krea AI](https://krea.ai)
- [Flux](https://blackforestlabs.ai)
