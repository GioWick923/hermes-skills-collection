# Ollama Custom Model Deployment (GGUF + mmproj)

Verified workflow for installing a HF GGUF model as a custom Ollama model, including multimodal (vision) support. Proven on Windows (git-bash) with Ollama 0.32.x, RTX 3060 12GB.

## 1. Download the files

Create a working dir, then download with curl (git-bash on Windows; use `$LOCALAPPDATA` paths for native tools):

```bash
mkdir -p "$LOCALAPPDATA/hermes/models/<model-name>"
cd "$LOCALAPPDATA/hermes/models/<model-name>"

# Main model GGUF (large — run in background with notify_on_complete)
curl -L -o <MODEL>.gguf "https://huggingface.co/<USER>/<REPO>/resolve/main/<MODEL>.gguf"

# Vision projector (small, ~0.6-0.9 GB) — only for multimodal models
curl -L -o <MODEL>.mmproj-f16.gguf "https://huggingface.co/<USER>/<REPO>/resolve/main/<MODEL>.mmproj-f16.gguf"
```

- Verify free disk first: `df -h /c`
- Verify download integrity by size: `ls -la` vs the tree API byte size
- Large downloads (10+ GB) → background curl with `notify_on_complete=true`; typical HF speed ~6-9 MB/s → 13.5GB ≈ 30-40 min

## 2. Create the Modelfile

```dockerfile
FROM C:\path\to\<MODEL>.gguf
PROJECTOR C:\path\to\<MODEL>.mmproj-f16.gguf

# Repo-recommended params (check the HF README — abliterated models often want these)
PARAMETER temperature 0
PARAMETER repeat_penalty 1.15
PARAMETER num_ctx 8192
PARAMETER num_predict 2048
```

Notes:
- **No `TEMPLATE` needed** — Ollama extracts the chat template from GGUF metadata. HF `chat_template.jinja` is NOT Ollama-compatible (Go template vs Jinja).
- `num_ctx 8192` balances VRAM for a 27B on 12GB. KV cache consumes extra VRAM.
- `temperature 0` = greedy decoding (recommended by OBLITERATUS for code-heavy output).
- For Qwen3 VL: image tokens (`<|vision_start|><|image_pad|><|vision_end|>`) are handled by the embedded template.

## 3. Create and verify

```bash
ollama create <model-name> -f Modelfile
ollama list                       # confirm it appears
ollama run <model-name> "hola, responde breve"   # smoke test, measure tok/s
```

Speed check: `ollama run` shows `eval rate: X tokens/s` at the end.

## Alternative: direct HF pull

Works for text-only GGUFs already on HF (no mmproj):

```bash
ollama pull hf.co/<USER>/<REPO>:<QUANT>
```

⚠️ This does NOT attach the mmproj. For vision, always use the manual Modelfile route.

## Windows-specific notes

- Native tools (ollama, curl) need `C:/Users/...`-style or `$LOCALAPPDATA` paths — MSYS `/c/...` paths are NOT translated for native programs.
- Modelfile `FROM` path: use Windows absolute path (`C:\...`) exactly as shown above.
- If Ollama can't find the model: `ollama rm <name>` then `ollama create` again after checking paths in the Modelfile.

## Example session (2026-08-20): Qwen3.8-27B-OBLITERATED

- Source: `OBLITERATUS/Qwen3.8-27B-OBLITERATED` (abliterated Qwen3.5 VL, arch `Qwen3_5ForConditionalGeneration`)
- Official repo ships only Q4_K_M..Q8_0; **mradermacher/Qwen3.8-27B-OBLITERATED-GGUF** has full ladder + mmproj
- Chosen: `Q3_K_M` (13.5GB) — 85% in 12GB VRAM → ~12-20 tok/s expected
- mmproj: `Qwen3.8-27B-OBLITERATED.mmproj-f16.gguf` (885 MB)
- Repo optimal params: `temperature=0`, `repeat_penalty=1.15`, `max_new_tokens≥2048`, thinking off
