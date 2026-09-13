---
name: krea2-face-swap
description: Krea2 face swap, photo→real, anime→real, RTX 3060 12GB.
---

# Krea2 Face Swap

## Rules
- Single reference only (dual-ref = thrashing)
- LoRA turbo always (unless 2048px+)
- Prompt photographic (Canon EOS R5 50mm f/1.4, film grain, raw photo)
- Resolution: 768-1024px width safe, 1024×1536 for detail
- Launch: --disable-highvram flag required

## Workflow A: Photo Real Person (max identity)
Use for real photo references.

**Pipeline:**
1. Pre-composite face with `face_clone.py` (OpenCV + InsightFace)
2. Submit img2img, denoise 0.75, 4 steps, LoRA yes

**JSON template:**
```json
{
  "1": {"class_type": "Krea2SVDQuantW4A4Loader", "inputs": {"model_name": "Krea2-Turbo-SVDQuant-W4A4-rank256-actaware.safetensors", "vram_management": "auto"}},
  "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
  "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
  "4": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "krea2_turbo_4step_rank_64_lora.safetensors", "strength_model": 1.0}},
  "5": {"class_type": "CLIPTextEncode", "inputs": {"text": "portrait photograph of [NAME]: [features], wearing [outfit], [setting], shot on Canon EOS R5 50mm f/1.4, film grain, natural skin tones, no retouching, raw photo, editorial fashion style", "clip": ["2", 0]}},
  "6": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["5", 0]}},
  "7": {"class_type": "LoadImage", "inputs": {"image": "<COMPOSITE>.jpg"}},
  "8": {"class_type": "VAEEncode", "inputs": {"pixels": ["7", 0], "vae": ["3", 0]}},
  "9": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "seed": 987654, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["8", 0], "denoise": 0.75}},
  "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["3", 0]}},
  "11": {"class_type": "SaveImage", "inputs": {"images": ["10", 0], "filename_prefix": "output"}}
}
```

## Workflow B: Anime/Illustration (style transform)
Use when input is anime/art (insightface can't detect faces).

**Params:** denoise 0.85, steps 6, NO LoRA (OOM risk at high res)

## Decision table
| Input | denoise | steps | LoRA | Time |
|-------|---------|-------|------|------|
| Photo + composite | 0.75 | 4 | Yes | 3-5 min |
| Photo no composite | 0.80 | 4 | Yes | 4-6 min |
| Anime → Real | 0.85 | 6 | No | 2-4 min |
| High-res (2048) | 0.75 | 4 | No | 20-25 min |

## Pitfalls
- Thrashing (>20min, GPU 100%): dual-ref or >1024px → single-ref + ≤1024px
- OOM: LoRA + 2048px → remove LoRA or drop to 1024px
- Plastic skin: add 'film grain', 'subtle pores' to prompt
- Nonsensical text: add 'no text', 'clean clothing' to prompt
- No face detected: input is anime → skip composite, use denoise 0.85+

## Paths
- Script: `C:/Users/<USER>/Downloads/face_clone.py`
- Launch: `C:/Users/<USER>/Downloads/launch_comfy.ps1`
- Output: `F:/ComfyUI/output/` → `C:/Users/<USER>/Pictures/modelos imag/`
- Logs: `C:/Users/<USER>/Downloads/user/*.log`

## Validated
- `angelina_realistic_00001_.png` — 2048px, denoise 0.80, 9/10 likeness
- `sadie_realistic_00001_.png` — 1024px, denoise 0.85, 8/10 likeness

See `references/workflow-details.md` for full docs.
