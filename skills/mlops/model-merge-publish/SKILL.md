---
name: model-merge-publish
description: Merge/publish Civitai checkpoints for Gio.
version: 1.0.0
author: hermes
license: internal
metadata:
  tags: [comfyui, civitai, merge, checkpoint, sdqx, llustrious]
  related_skills: []
---

## When to Use
Use whenever Gio asks to: merge/mezclar checkpoints SDXL/Illustrious, reducir tamaño de un modelo (fp32→fp16), hornear VAE, o publicar/subir un modelo a su cuenta de Civitai (<CIVITAI_USER>).

# Merge + Publicar Checkpoints en Civitai (<CIVITAI_USER>)

Pipeline completo que Gio usa seguido: buscar modelos grandes, mezclarlos con pequeños, reducir tamaño, y publicar en su cuenta Civitai.

## Contexto del entorno
- Checkpoints en `F:/Modelos/checkpoints/`
- VAE SDXL en `F:/Modelos/vae/sdxl_vae.safetensors` (334MB)
- ComfyUI venv: `/f/ComfyUI/venv/Scripts/python.exe` (tiene safetensors+torch)
- Forge Neo en `F:/sd-forge/forge` (port 7860), outputs en `outputs/txt2img-images/<fecha>/`
- Cuenta Civitai: **<CIVITAI_USER>** (ID 2836482)
- Host Windows, terminal bash/MSYS. Rutas nativas para python: `F:/...`

## Paso 1: Buscar modelos en Civitai (API)
API publica es SOLO lectura (NO permite crear/subir modelos por API). Usar para busqueda/verificacion:
```python
import json, urllib.request, urllib.parse
params=urllib.parse.urlencode({"limit":100,"types":"Checkpoint","sort":"Newest","query":"..."})
d=json.load(urllib.request.urlopen(urllib.request.Request(
  f"https://civitai.com/api/v1/models?{params}",
  headers={"User-Agent":"Mozilla/5.0"})))
```
- Verificar arquitectura ANTES de mergear (SDXL/Illustrious usan `model.diffusion_model`; FLUX/Chroma usan `double_blocks`). NO mezclar arquitecturas.
- Tamano real: `sizeKB/1024/1024` GB. Cuidado: a veces la API devuelve valores absurdos (38,000GB) = bug, no fiarse; verificar por versionId.
- Gio prefiere modelos FRESCOS (Directiva Vigencia <=6 meses), no Juggernaut/RealVis viejos.

## Paso 2: Verificar arquitectura
```bash
/f/ComfyUI/venv/Scripts/python.exe -c "
import safetensors.torch as st
t=st.load_file('ARCHIVO.safetensors',device='cpu')
k=list(t.keys()); names=' '.join(k).lower()
print('SDXL' if 'model.diffusion_model' in names else ('FLUX' if 'double_blocks' in names else '?'))
"
```

## Paso 3: Merge ponderado (script safetensors+torch)
Escribir script en `F:/Modelos/checkpoints/merge_X.py` y correr en BACKGROUND:
```bash
cd /f/Modelos/checkpoints && /f/ComfyUI/venv/Scripts/python.exe merge_X.py
```
Script base: cargar A,B,C con `st.load_file(dev='cpu')`, para cada key comun: `out[k] = a.float()*wA + b.float()*wB + c.float()*wC`. Tensores solo en B/C se copian. `st.save_file(out, OUT)`.
- Correr con `background=true` + `notify=["..._DONE","Error","Traceback"]`.
- Cargar 3 modelos de 14GB ~= 35-42GB RAM (maquina tiene 98GB, OK).

## Paso 4: Convertir fp32 a fp16 (reducir tamano)
`fp32` 14.2GB a `fp16` 7.27GB (mitad). Igual calidad al generar. Script: tensores `first_stage_model` (VAE) se dejan, resto `.half()`.

## Paso 5: Hornear VAE SDXL
Para que colores/contraste salgan bien sin cargar VAE aparte: sobreescribir todos los tensores `first_stage_model.*` con los del `sdxl_vae.safetensors` (250 tensores). Resultado ~2765 tensores (2515 modelo + 250 VAE).

## Paso 6: Publicar en Civitai (via stealth-browser)
API NO permite crear modelos. Usar navegador logueado:
1. `spawn_browser(headless=false)` a civitai.com
2. Requiere que GIO inicie sesion (Google OAuth) en la ventana visible
3. Ir a `/models/create` y rellenar con `execute_script`:
   - `#input_name` = nombre; tipo Checkpoint; `#checkpointType-Merge` (Unir)
   - poi=false (No), `#input_attestation` check, `#input_allowNoCredit`/`allowDerivatives`/`allowDifferentLicense` default true
   - Desmarcar `Sell` (input checkbox value=Sell)
   - Descripcion: contenteditable DIV (`[contenteditable=true]`)
4. Next - version: `#input_baseModel` buscar y click "Illustrious" (teclear "Illus" filtra); `#input_skipTrainedWords` check; "Next"
5. Upload archivo: usar `mcp__stealth_browser_mcp__file_upload`. PERO requiere dir permitido. Copiar a `C:/Users/<USER>/tools/stealth-browser-mcp/upload_tmp/` primero (allowlist). Subida 7GB tarda.
6. Next - subir previews al input file de imagenes (mismo dir permitido)
7. Click "Publicar" y verificar URL `civitai.com/models/<id>/<nombre>`

## Pitfalls descubiertos (IMPORTANTE)
- `--listen 0.0.0.0` en Forge da "unrecognized arguments" - usar solo `--port 7860`
- `call webui.bat` no funciona en bash - usar `cmd //c webui.bat` o lanzar `venv/Scripts/python.exe webui.py --port 7860` con nohup
- Stealth `execute_script` produce "tool loop warning" FALSO (success true real). Ignorar.
- `file_upload` falla si path fuera de `BROWSER_FILE_UPLOAD_ALLOWED_DIRS` - copiar a `upload_tmp/`
- El dropdown de categoria en create muestra TIPOS DE ARCHIVO (LoRA/VAE/UNet), no categorias de modelo. No es obligatorio.
- `python -m huggingface_hub` no funciona; usar binario `hf`. Xet repos no bajan anonimo sin token HF.
- Disco F: se llena rapido con merges (14GB c/u). Verificar `df -h /f` antes; si >95%, liberar (preguntar antes de borrar).
- Modelo final favorito de Gio: `NDREAM_FINAL_60_20_20` (queda espectacular).

## Verificacion final
Siempre validar el safetensors resultante cargandolo (cuenta tensores, VAE presente). Y curl al modelo publicado.
