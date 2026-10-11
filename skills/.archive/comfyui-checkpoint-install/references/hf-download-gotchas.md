# HF Download Gotchas (ComfyUI models)

## Gated repos → API 401, but files serve fine
The HF *API* (`https://huggingface.co/api/models/<repo>`) returns **401 Unauthorized** for
gated repos (e.g. `Comfy-Org/Qwen-Image`, `Comfy-Org/Qwen`). Do NOT use it to list files or
sizes. Use the `resolve/main/...` URL directly — it serves the file (possibly after a
xet-bridge redirect).

## Get real file size with curl -sIL
```
curl -sIL "https://huggingface.co/<repo>/resolve/main/<path>"
```
- First `Location` line = a tiny xet-bridge URL (length ~1000 bytes, ignore).
- The eventual `HTTP/1.1 200 OK` block has the REAL `content-length` (bytes).

## Krea2 SVDQuant — known-good URLs (verified 2026-08)
Repo: `AlperKTS/Krea-2-SVDQuant-ComfyUI` (checkpoints) + `Comfy-Org/Qwen3-VL` (encoder) + `Comfy-Org/Krea-2` (VAE)

| File | URL | Size | Destination |
|------|-----|------|-------------|
| Checkpoint rank256-actaware | `https://huggingface.co/AlperKTS/Krea-2-SVDQuant-ComfyUI/resolve/main/checkpoints/Krea2-Turbo-SVDQuant-W4A4-rank256-actaware.safetensors` | 9.78 GB | `models/diffusion_models/` |
| Text encoder Qwen3-VL 4B fp8 | `https://huggingface.co/Comfy-Org/Qwen3-VL/resolve/main/text_encoders/qwen3vl_4b_fp8_scaled.safetensors` | 5.24 GB | `models/text_encoders/` |
| VAE qwen_image_vae | `https://huggingface.co/Comfy-Org/Krea-2/resolve/main/vae/qwen_image_vae.safetensors` | 253 MB | `models/vae/` |
| All-in-One (alt) rank256-actaware-TEW4A4 | `https://huggingface.co/AlperKTS/Krea-2-SVDQuant-ComfyUI/resolve/main/checkpoints/Krea2-Turbo-AllInOne-SVDQuant-W4A4-rank256-actaware-TEW4A4.safetensors` | 12.77 GB | `models/checkpoints/` |

NOTE: VAE at `Comfy-Org/Qwen-Image` or `Comfy-Org/Qwen` → 401. Use `Comfy-Org/Krea-2/vae/`.

## MiniMax H3 cleanup (what was deleted, 2026-08)
User-data only (do NOT delete core ComfyUI code that mentions MiniMax):
- `custom_nodes/ComfyUI-MiniMax-H3-Turbo`
- `models/text_encoders/qwen3vl_32b_minimax_h3-Q4_K_M.gguf` (14 GB)
- `models/unet/MiniMax-H3-FL2VA-Pruned-Q3_K_M.gguf` (8.3 GB)
- `models/vae/minimax_h3_audio_vae_fp32.safetensors` (578 MB)
- `models/vae/minimax_h3_video_vae_fp16.safetensors` (4.9 GB)
Freed ~27 GB on F:.
