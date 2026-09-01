---
name: comfyui-checkpoint-install
description: Install a ComfyUI checkpoint; checks GPU fit, verifies run.
---

# ComfyUI Checkpoint / Quantized Model Install

Use when the user wants to install, run, or evaluate a ComfyUI diffusion checkpoint
(from Civitai or HuggingFace) — especially quantized variants (FP8, W4A4/SVDQuant, GGUF).

## When to use
- User pastes a Civitai/HF model link and asks "can we run this?" or "install it".
- User wants to free disk by removing an old model stack before adding a new one.
- User asks to set up a specific architecture (Krea2, Flux, SDXL, MiniMax, etc.).

## Workflow

### 1. GPU-fit diagnosis (BEFORE downloading)
Check three things in parallel:
- VRAM: `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits`
- Disk free on target drive (usually F: for this user): `df -h` (look for /f)
- ComfyUI version + native model support: read `comfyui_version.py`; grep source for the
  model family (e.g. `grep -ril "krea" /f/ComfyUI/comfy`).

Key rule — quant vs architecture:
- **RTX 30-series (Ampere) and 20-series (Turing) have NO FP8 tensor cores.** FP8 advice
  from model pages often runs *slower* than BF16 on these. Prefer **SVDQuant W4A4** (activation-
  aware INT4) which is built for exactly these GPUs and is ~2.4x faster.
- **RTX 40/50 (Ada) / server Hopper** have FP8 cores → native FP8 is fine.
- Always compare the model's declared minimum VRAM against the actual GPU. If below, plan
  `--medvram` / `--lowvram` and a real test at low resolution (768²) before promising it works.

### 2. Check what already exists (user hates re-downloading)
`ls` the relevant `models/checkpoints|text_encoders|vae|unet` and `custom_nodes` BEFORE
downloading. If the user already has the encoder/VAE, reuse it. Report what's present.

### 3. Resolve correct download URLs
The HF *API* (`https://huggingface.co/api/models/<repo>`) returns **401** for gated repos
(e.g. Comfy-Org/Qwen-Image). Do NOT trust it for size/file listing. Instead:
- Find the exact resolve URL from the model page or the custom node's README
  (the node README is the most reliable source — it lists checkpoint + encoder + VAE paths).
- Verify size with: `curl -sIL "<resolve-url>"` and read the **final** `content-length`
  after following the xet-bridge redirect (the first `Location` shows a tiny length; the
  eventual `HTTP/1.1 200 OK` has the real one).
- Known-good URLs for Krea2 SVDQuant: see `references/hf-download-gotchas.md`.

### 4. Cleanup to free space (only user-data, never core)
When the user says "delete the old model stack":
- DELETE only the user-data files: `custom_nodes/<OldStack>`, `models/text_encoders/*old*.gguf`,
  `models/unet/*old*.gguf`, `models/vae/*old*.safetensors`.
- NEVER delete core framework code that merely *mentions* the model (e.g. `comfy/ldm/minimax/`,
  `comfy/text_encoders/minimax.py`, `venv/.../transformers/models/minimax*`). Those are part of
  ComfyUI's native support and weigh KB, not GB. Deleting them breaks the app.
- Verify with `df -h /f` before/after to report space freed.

### 5. Download + install
- Clone custom node: `git clone <url> custom_nodes/<name>` (restart ComfyUI after).
- Download files with `curl -sL --retry 3 -o <dest> <url>` in background for big files.
- Place files in the folders the model page / node README specifies
  (Krea2 SVDQuant: checkpoint → `models/diffusion_models/`, encoder → `models/text_encoders/`,
  VAE → `models/vae/`; All-in-One → `models/checkpoints/`).

### 6. VERIFY IT ACTUALLY RUNS (staff-engine bar)
Never declare done on "installed". Prove it:
- Launch ComfyUI with VRAM flags: `python main.py --medvram` (or `--lowvram` if 12GB GPU).
- Load the model's example workflow JSON from the node.
- Generate **one real image** at 768² and report VRAM used + seconds. That is the "¿qué tal?"
  answer the user wants — not "files are present".

## Pitfalls
- `python3` is NOT on PATH in the terminal shell on this host — use the ComfyUI venv:
  `/f/ComfyUI/venv/Scripts/python.exe` for any python one-liner.
- HF API 401 ≠ file missing. Gated repos still serve via `resolve/main/...` URLs.
- VAE path confusion: for Krea2 the VAE lives at `Comfy-Org/Krea-2/resolve/main/vae/...`,
  NOT `Comfy-Org/Qwen-Image` or `Comfy-Org/Qwen` (both 401).
- User may misstate a version (said "H4", meant "H3"). Check what's actually installed before
  deleting; report the discrepancy and proceed with the real one.
- The custom node README may reveal an **All-in-One** combined file (DiT+TE+VAE in one
  checkpoint) — simpler 1-click setup. Offer it as an alternative to separate files.

## References
- `references/hf-download-gotchas.md` — exact URLs, sizes, 401 handling, Krea2 file map.
