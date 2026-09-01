# Pruning checklist — keep {Z-Image, Lumina, Anima, Flux}, drop the rest

Run from repo root (the mini-forge-neo fork). Assumes target = 4 models.

## 1. Delete engine files
```
rm -f backend/diffusion_engine/chroma.py backend/diffusion_engine/flux2.py \
      backend/diffusion_engine/qwen.py  backend/diffusion_engine/sd15.py \
      backend/diffusion_engine/sdxl.py backend/diffusion_engine/wan.py
```
Keep: `anima.py flux.py lumina.py zimage.py base.py`

## 2. Delete HuggingFace config folders for dropped models
```
rm -rf backend/huggingface/Chroma backend/huggingface/Qwen \
       backend/huggingface/Wan-AI backend/huggingface/circlestone-labs \
       backend/huggingface/runwayml
```
Keep folders for kept models (Tongyi-MAI, neta-art, black-forest-labs, lllyasviel, stabilityai, etc.).

## 3. Edit backend/loader.py
- Remove import lines for the deleted engines.
- Set: `possible_models = [Flux, Lumina2, ZImage, Anima]`

## 4. Delete NN modules (carefully)
```
rm -f backend/nn/chroma.py backend/nn/wan.py
```
- **DO NOT delete `backend/nn/qwen.py`** — `backend/nn/svdq.py` imports it (NunchakuQwen). It is inert without a Qwen model but must resolve.
- **DO keep `backend/nn/wan_vae.py`** — Anima's engine uses `is_wan=True` VAE loading.

## 5. Verify
```
python -m py_compile backend/loader.py backend/diffusion_engine/*.py backend/nn/*.py
# strict import search — must return ZERO real imports to deleted modules:
grep -rn "import backend\.\(diffusion_engine\|nn\)\.\(chroma\|flux2\|qwen\|sd15\|sdxl\|wan\)\b" --include=*.py . | grep -v "svdq.py"
```
Note: `loader.py` will still contain `if cls_name == "ChromaTransformer2DModel"` style strings
referencing deleted `nn` modules — these are inert dead branches (no `possible_models` entry reaches them). `py_compile` passes. Leave them.

## 6. Mini layer (new files, ~456 LOC)
- `mini/mini_core.py` — `mini_generate(MiniRequest)` reuses `process_images`.
- `mini/mini_bridge.py` — `MiniClient` HTTP client to `/sdapi/v1/txt2img` (+img2img). This is what the agent calls.
- `webui_mini.py` — entrypoint: `initialize.initialize()` + minimal `gr.Blocks` + mounts Forge `Api`.
- `mini/mini_config.yaml` — per-model defaults + checkpoint aliases + VRAM mode.
- `run_mini.bat` / `run_mini.sh` — `uv venv` + `uv pip install -r requirements.txt` + `python webui_mini.py`.
