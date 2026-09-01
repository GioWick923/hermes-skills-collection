# Krea 2 Turbo (Krea2) — referencia de instalación y pitfalls (Windows RTX 3060 12GB)

## Resumen del caso (sesión 2026-08-26)
Usuario quiso Krea2 Turbo. Evaluamos FP8 (link Civitai MAMaliaTate) y SVDQuant W4A4 (link Civitai AlperKTS). Decisión final: **FP8 nativo** porque el W4A4 no da speedup en Windows.

## Versiones / entorno confirmado
- ComfyUI `0.33.0` (tiene soporte Krea2 nativo: `comfy/ldm/krea2/model.py`).
- torch `2.5.1+cu121`, GPU RTX 3060 sm_86 (Ampere).
- `comfy-kitchen 0.2.31` instalado (backend CUDA de SVDQuant).

## 🔴 Hallazgo crítico: W4A4 SVDQuant exige CUDA ≥ 13 — INEXISTENTE en Windows
- PyTorch publica build **cu130 solo para Linux**. En Windows lo máximo estable es **cu128** (torch 2.7.1+cu128 existe para win py311; verificado HTTP 200). cu130/cu129 → 403.
- ComfyUI core (`comfy/quant_ops.py`) deshabilita el backend CUDA de `comfy_kitchen` cuando `torch.version.cuda < 13`.
- Con fallback, W4A4 dequantiza int4→bf16 en **Python puro** → **MÁS LENTO que FP8**. El claim "2.42x" NO aplica a Windows; solo Linux/WSL2 con cu130.
- Nota: inspeccionar solo `comfy_kitchen` engaña — el check duro está en ComfyUI core, no en el paquete.

## Probe de verdad (Krea2SVDQuantEnvCheck)
Nodo output STRING, sin inputs. Enviar workflow `{"1":{"class_type":"Krea2SVDQuantEnvCheck","inputs":{}}}` a `POST /prompt`, luego leer `/history/{pid}` y el **log del server** (no el output string — a veces va al stdout del proceso).
Línea reveladora en log:
```
cuda     available=True  disabled=True  implements convrot_w4a4_linear=True  reason=-
ComfyUI disables comfy_kitchen's CUDA backend on torch built against CUDA < 13 (comfy/quant_ops.py).
cuda backend is NOT live. convrot_w4a4 will fall back to ['eager'] ... expect this checkpoint to be SLOWER than fp8.
```
Si aparece, el speedup W4A4 no es para esa caja.

## Descargas HF (rutas verificadas 2026-08-26)
- FP8 DiT (~13.14 GB): `https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_turbo_fp8_scaled.safetensors`
- W4A4 DiT (~9.78 GB): `https://huggingface.co/AlperKTS/Krea-2-SVDQuant-ComfyUI/resolve/main/checkpoints/Krea2-Turbo-SVDQuant-W4A4-rank256-actaware.safetensors`
- Text encoder Qwen3-VL 4B (~5.24 GB, AMBOS sabores): `https://huggingface.co/Comfy-Org/Qwen3-VL/resolve/main/text_encoders/qwen3vl_4b_fp8_scaled.safetensors`
- VAE Qwen-Image (~253 MB, AMBOS sabores): `https://huggingface.co/Comfy-Org/Krea-2/resolve/main/vae/qwen_image_vae.safetensors`
⚠️ `Comfy-Org/Qwen-Image` y `Comfy-Org/Qwen` responden **401** en API/HEAD. El VAE correcto está en `Comfy-Org/Krea-2/vae/`. Cree en la ruta que dice el README del node (`Comfy-Org/Krea-2/resolve/main/vae/...`).
⚠️ El repo `MAMaliaTate/Krea2-Turbo-FP8` responde 401 (gated). Usar `Comfy-Org/Krea-2` para el fp8.

Node W4A4: `git clone --depth 1 https://github.com/alperktt/Krea-2-SVDQuant-ComfyUI custom_nodes/krea2-svdquant` (sin deps pip: `dependencies = []` en pyproject).

## Workflow FP8 funcional (API ComfyUI)
Loaders:
- `UNETLoader` unet_name=`krea2_turbo_fp8_scaled.safetensors`, weight_dtype=`default`
- `CLIPLoader` clip_name=`qwen3vl_4b_fp8_scaled.safetensors`, type=`krea2`
- `VAELoader` vae_name=`qwen_image_vae.safetensors`
Regla cfg-distilled: **cfg=1.0**, 8 steps, sampler `euler`, scheduler `simple`. Anular negative con `ConditioningZeroOut` sobre el positive (NO codificar negative real). Template listo: `templates/krea2_fp8_workflow.json`.

## Pitfalls nuevos (no estaban en SKILL.md v4.0.0)
1. **`--medvram` removido en ComfyUI 0.33.** El flag ya no existe → `error: unrecognized arguments: --medvram`. Usar `--lowvram` (o `--highvram`/`--novram`/`--cpu`). Equivalente para 12GB: `--lowvram`.
2. **Ejecutar ComfyUI desde git-bash (MSYS) con `call`/`activate` falla.** `call: command not found` y `source venv/Scripts/activate` NO reescribe PATH (deja el python de Hermes). Usar SIEMPRE la ruta absoluta del python del venv: `/f/ComfyUI/venv/Scripts/python.exe main.py ...`. El `launch.bat` original usa `call` y solo funciona desde cmd.exe, no desde el terminal de Hermes.
3. **`ModuleNotFoundError: sqlalchemy` al lanzar mal el venv.** Síntoma de usar el python equivocado (Hermes en vez de ComfyUI). SQLAlchemy SÍ está en el venv de ComfyUI; el error desaparece usando `venv/Scripts/python.exe` directo.
4. **HF API 401 en repos gated** (`Comfy-Org/Qwen-Image`, `MAMaliaTate/*`). No asumir que la ruta del README es la correcta sin probar HEAD; usar `Comfy-Org/Krea-2` para VAE/DiT fp8.
5. **W4A4 en Windows = trampa.** No upgradear torch a cu128 esperando activar el backend: ComfyUI core corta en CUDA<13. El único speedup real es Linux/WSL2 cu130.

## Limpieza (lo que se borró esta sesión)
MiniMax H3 (user-data, autorizado): `custom_nodes/ComfyUI-MiniMax-H3-Turbo`, `models/text_encoders/qwen3vl_32b_minimax_h3-Q4_K_M.gguf` (14G), `models/unet/MiniMax-H3-FL2VA-Pruned-Q3_K_M.gguf` (8.3G), `models/vae/minimax_h3_audio_vae_fp32.safetensors` (578M), `models/vae/minimax_h3_video_vae_fp16.safetensors` (4.9G). Liberó ~27 GB en F:.
⚠️ NO borrar los archivos MiniMax que están dentro del código core de ComfyUI (`comfy/ldm/minimax/`, `comfy/text_encoders/minimax.py`, `venv/.../transformers/models/minimax*`) — son parte nativa de ComfyUI, pesan KB y borrarlos rompe el programa.
