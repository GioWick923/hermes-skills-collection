---
category: mlops
name: local-model-install
description: "Inspect a HF model link, check fit, deploy to Ollama."
platforms: [windows, linux, macos]
---

# Local Model Install

Turn a HuggingFace model link into a running local model on the user's hardware.

## When to use

- User shares a specific HF repo URL (GGUF, MLX, safetensors) and asks "does this run on my PC?"
- User says "install this model" or "armalo" (assemble it — model + vision projector)
- You need to find what GGUF quantizations exist for a model, their sizes, and pick the right one for the user's VRAM/RAM
- User links an MLX repo and you need to find the GGUF equivalent

## Core workflow

### 1. Inspect the HF repo

Use the HF tree API to list actual files and sizes:

```
curl -s "https://huggingface.co/api/models/<REPO>/tree/main"
```

Extract GGUF files, their sizes, and detect cues:
- `.gguf` files → main model candidates
- `mmproj-*.gguf` → vision projector (multimodal)
- Config files (`preprocessor_config.json`, `video_preprocessor_config.json`) → vision-capable model
- `mlx-4bit/`, `mlx-8bit/` → MLX format (Apple Silicon only)
- `model-*.safetensors` → raw weights (not Ollama-ready)

Also search for related repos:
```
curl -s "https://huggingface.co/api/models?search=<MODEL_NAME>&limit=20"
```

### 2. Format compatibility check

| Format | Runs on Windows/NVIDIA? | Ollama-ready? |
|--------|------------------------|--------------|
| GGUF | ✅ Yes | ✅ Directly |
| MLX | ❌ No (Apple Silicon only) | ❌ Find GGUF |
| safetensors (raw) | ⚠️ Needs conversion | ❌ No |
| AWQ / GPTQ | ⚠️ Needs tool | ❌ No |

**Key gotcha**: MLX repos are Apple-only. When user shares an MLX link, search for the same model's GGUF version — often the same author has one, or `mradermacher`/`chimingw`/`JonathanColetti` mirrors it.

### 3. mradermacher pattern (full quant ladder)

Repos by `mradermacher/<model>-GGUF` typically carry the **complete** quantization set:
- Q2_K, Q3_K_S, Q3_K_M, Q3_K_L, Q4_K_S, Q4_K_M, Q5_K_S, Q5_K_M, Q6_K, Q8_0
- IQ1_S→IQ4_XS variants
- `mmproj-f16.gguf` and `mmproj-Q8_0.gguf` for multimodal models

Official repos often ship only Q4_K_M through Q8_0; use mradermacher when the user needs Q3/Q2 for tight VRAM or wants the projector.

### 4. Match quant to VRAM

For a ~27B model (like Qwen3.8-27B) on a 12GB dedicated GPU:

| Quant | Size | % in VRAM (12GB) | Speed est. | Verdict |
|-------|------|-------------------|------------|---------|
| Q2_K | ~10.9 GB | ~100% | 20–30 tok/s | 🟡 low quality |
| Q3_K_S | ~12.3 GB | ~95% | 15–25 tok/s | 🟢 fast, decent |
| Q3_K_M ⭐ | ~13.5 GB | ~85% | 12–20 tok/s | 🟢 best balance |
| Q4_K_M | ~16.8 GB | ~65% | 6–12 tok/s | 🟡 quality but slow |
| Q5_K_M | ~19.5 GB | ~55% | 4–8 tok/s | 🔴 too slow |

**Rule of thumb**: Q3_K_M = sweet spot for 12GB VRAM on 27B models. For smaller models (<10B), Q4_K_M works fully on-GPU.

### 5. Deploy as Ollama custom model

See `references/ollama-custom-model.md` for the full workflow. TL;DR:
1. Download the GGUF + mmproj from HF (curl -L resolve URLs)
2. Create Modelfile with `FROM`, `PROJECTOR`, `PARAMETER`
3. `ollama create <name> -f Modelfile`
4. Verify with `ollama run <name>`

Direct pull also works when the GGUF is on HF:
```
ollama pull hf.co/<USER>/<REPO>:<QUANT>
```

## Key concepts

- **Ollama infers chat template from GGUF metadata** — you do not need to put `TEMPLATE` in the Modelfile. The HF `chat_template.jinja` is NOT directly compatible with Ollama's Go template format.
- **mmproj is the vision projector**: a separate small GGUF (~0.6–0.9GB) that maps image embeddings into the LLM's token space. Without it, the model is text-only.
- **Qwen3.5 VL models** use `Qwen3_5ForConditionalGeneration` architecture and tokens `<|vision_start|><|image_pad|><|vision_end|>` for images. The template is complex; trust the GGUF-embedded one.

## Pitfalls

- **MLX ≠ GGUF**: MLX repos (Apple Silicon) do NOT run on Windows/NVIDIA. Always search for the GGUF version.
- **mradermacher full quant set**: when the official repo only has Q4–Q8, check mradermacher for Q3/Q2 + mmproj.
- **VRAM ≠ model size only**: the KV cache uses additional VRAM. With `num_ctx 8192`, a 27B model uses ~2GB extra for context. Reduce `num_ctx` if OOM.
- **Ollama `ollama pull hf.co/...`** works for HF repos with GGUF files, but does NOT pull the mmproj automatically. For multimodal, use the manual Modelfile approach.
- **Temperature 0 + repeat_penalty ≠ 1.0**: especially for abliterated models, the repo authors often specify exact params (e.g., OBLITERATUS: `temperature=0`, `repeat_penalty=1.15`). Always check the repo README for optimal settings.