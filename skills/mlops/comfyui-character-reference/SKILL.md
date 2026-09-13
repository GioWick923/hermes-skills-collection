---
category: mlops
name: comfyui-character-reference
version: "1.1.0"
description: "Crear hojas de modelo de personaje 3D realistas con ComfyUI."
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [comfyui, character-reference, image-generation, ultra-real, 3d, perfil]
    related_skills: [stable-diffusion-setup]
---

# ComfyUI Character Reference Sheet

Procedimiento para crear hojas de modelo de personaje 3D realistas (character reference sheets) usando ComfyUI con workflows ultrareal.

## Cuándo Usar

- El usuario pide un "perfil de imagen" o "character reference sheet"
- Se necesita generar vistas múltiples de un personaje consistente
- Workflow: ultrareal-krea2-flux.json o similar

## Template de Prompt

**Archivo canónico:** `references/template-perfil-imagen.md`

Cargar y adaptar el prompt base según la imagen de referencia del usuario.

### Estructura del Prompt

1. **Bloqueo de identidad** - Preservar apariencia exacta de la referencia
2. **Vistas del personaje** - Frontal, 3/4, lateral, trasera
3. **Primer plano cabeza** - Múltiples ángulos faciales
4. **Expresiones faciales** - Neutral, enojado, sonriente, sorprendido, triste, serio, relajado
5. **Detalle manos** - Gestos naturales
6. **Paleta colores/materiales** - Cabello, piel, telas, accesorios
7. **Paneles de detalle** - Ojos, cabello, tela, costuras, calzado, joyas
8. **Referencia altura/proporción** - Silueta + medidas

## Workflow ComfyUI Recomendado
1. **Bloqueo de identidad** - Preservar apariencia exacta de la referencia
2. **Vistas del personaje** - Frontal, 3/4, lateral, trasera
3. **Primer plano cabeza** - Múltiples ángulos faciales
4. **Expresiones faciales** - Neutral, enojado, sonriente, sorprendido, triste, serio, relajado
5. **Detalle manos** - Gestos naturales
6. **Paleta colores/materiales** - Cabello, piel, telas, accesorios
7. **Paneles de detalle** - Ojos, cabello, tela, costuras, calzado, joyas
8. **Referencia altura/proporción** - Silueta + medidas

## Workflow ComfyUI Recomendado

```
Imagen Referencia → CLIP Vision → IPAdapter → KSampler → Output
                       ↓
               FaceDetailer (consistencia facial)
```

### Nodes Esenciales

| Node | Función |
|------|---------|
| `IPAdapter Apply` | Preservar identidad facial |
| `CLIP Vision Encode` | Extraer features de referencia |
| `FaceDetailer` | Mantener consistencia facial |
| `Impact Pack` | Detalles y máscaras |
| `Krea2 Style Reference` | Estilos basados en referencia |

### Configuracion Recomendada

- **Checkpoint**: Krea2 Turbo o RealVisXL (fotorrealista)
- **Resolution**: 1024x1024 o 832x1472 (9:16)
- **Steps**: 25-30
- **CFG**: 4.5-6.0 (suave para realismo)
- **Sampler**: DPM++ 2M Karras

## Reglas Criticas

- **NO** embellecer/rediseñar al sujeto de referencia
- **NO** cambiar rostro, cuerpo, ropa entre vistas
- **SIN** anime, Pixar, Disney, estilo cartoon
- **MANTENER** misma identidad en TODAS las vistas
- **ULTRA-REAL** 3D, calidad AAA, fotorealismo humano

## ZSTD como Compresor por Defecto

**LEY:** Usar zstd para toda compresión (backups, logs, transfers, archives). Fallback a gzip solo si zstd no está disponible.

```
zstd -19 archivo.txt      # Máxima compresión
zstd -1 archivo.txt       # Más rápido
zstd -d archivo.txt.zst   # Descomprimir
```

Ubicación: `$LOCALAPPDATA/hermes/bin/zstd.exe` v1.5.7 ✅

## Backup de Workflows

Workflows de ComfyUI respaldados en: https://github.com/<GITHUB_USER>/hermes-comfyui-workflows (privado)
- Total: 203 archivos JSON
- Tamaño: 7.55 MB
- Incluye: blueprints, user_workflows, custom_nodes examples

## Archivos Relacionados

- Template: `templates/perfil-imagen-modelo-3d.md`
- Skill principal: `stable-diffusion-setup`
- Workflows: `<GITHUB_USER>/hermes-comfyui-workflows`

---
*Template creado: 2026-09-11*
*Versión: 1.0*
*Relacionado: ComfyUI, ANIME→ULTRAREAL, ultrareal-krea2-flux, zstd*
