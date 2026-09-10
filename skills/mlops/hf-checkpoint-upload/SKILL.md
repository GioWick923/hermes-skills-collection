---
category: mlops
name: hf-checkpoint-upload
description: "Upload checkpoints to HF Hub. Auth, create repo, upload."
version: 1.0.0
author: hermes
tags: [huggingface, hf, models, checkpoints, upload, sdxl, illustrious]
---

# Upload Checkpoints to Hugging Face Hub

Workflow for uploading Gio's model checkpoints (safetensors, 6-14 GB) to HF Hub.

## Prerequisites
1. `hf` CLI installed (in Hermes venv)
2. Token from https://huggingface.co/settings/tokens (type Fine-grained, permission Write)

## Auth
```bash
hf auth login --token hf_xxxxx
```
Saves to `~/.cache/huggingface/token` and `stored_tokens`. Verify:
```bash
hf auth whoami --format json
# → {"user": "GWick923", ...}
```

## Workflow

### 1. Create repo (private first)
```bash
hf repos create --private GWick923/descriptive-kebab-name
```

### 2. Write README.md model card
Minimal frontmatter + short description stating:
- What the model is (merge components)
- Base architecture (SDXL / Illustrious)
- Format: safetensors
- Usage: ComfyUI / Forge / A1111

### 3. Upload model file + README in parallel
```bash
# Model file — large, run in background with notify
cd /f/Modelos/checkpoints && hf upload GWick923/repo file.safetensors file.safetensors

# README instantly
cd /f/Modelos/checkpoints && hf upload GWick923/repo README_local.md README.md --revision main
```

### 4. For multiple models, upload concurrently
Start each `hf upload` as a separate background terminal session. Expect ~1-3 min per 7GB file.

### 5. Make public later
```bash
hf repos update GWick923/repo --public
```
Or via web: Settings > Make public

## Tips for Naming
- Use kebab-case: `nexusdream-infinity-ultra-aio`
- Short, descriptive

## Related
- `mlops/model-merge-publish` — Civitai publishing (complementary)
- `mlops/huggingface-hub` — general hf CLI reference