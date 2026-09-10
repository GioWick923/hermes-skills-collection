---
category: mlops
name: local-llm-inference-optimization
description: "Use when tuning local LLM speed: llama.cpp flags, gotchas."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [llama.cpp, ollama, inference, optimization, gguf, mtp, vram]
    related_skills: [llama-cpp, local-llm-picker, hermes-local-fallback]
---

# Optimización de inferencia local (llama.cpp / Ollama)

## When to Use
- User wants a local LLM (GGUF) to run **faster** on limited VRAM (e.g. RTX 3060 12GB, 27B model).
- Choosing between Ollama and llama.cpp server for a model.
- Tuning a llama-server launch for max tokens/s on NVIDIA Windows.
- Any "model is slow" report where the fix is flags, runtime choice, or memory/VRAM coordination.

## Engine options: Ollama vs llama.cpp vs ktransformers
The engine choice is **3-way**, not 2-way. The deciding question is whether the model **fits in VRAM**:

| Engine | Best for | When |
|--------|----------|------|
| **Ollama** | Models that fit in VRAM | Convenience, full offload, air-gapped |
| **llama.cpp server** | Models that fit (~) + need MTP/speculative + full control | Speed tuning on a card |
| **ktransformers** | **Models that DON'T fit** — huge MoE (100-400GB) on small VRAM + big RAM | Access to Qwen3-Next 235B, DeepSeek-R1 671B, Kimi-K2 |

> **Key conceptual rule (user correction, 2026-09-01):** ktransformers does **NOT** speed up
> models that already fit in VRAM — for those, Ollama/llama.cpp with full offload is equal or
> better. ktransformers is about **access to 5-10x larger models**, not speed of existing ones.
> When the user asks "does this improve our models?" the honest answer for fitting models is NO.

### ktransformers (kvcache-ai) — heterogeneous CPU-GPU inference
Runs MoE models by keeping **hot experts on GPU** (12GB) and **cold experts in CPU RAM** (96GB),
via CPU-optimized MoE kernels. Windows native possible but heavy; see pitfalls below.

- **Fits in VRAM** → Ollama/llama.cpp (don't reach for ktransformers)
- **MoE that fits only in RAM** (Qwen3-Next 235B, DeepSeek-R1 671B) → ktransformers. Expect **~15-30 tok/s** for Qwen3-Next on 12GB+96GB Haswell; **~5-10 tok/s** for DeepSeek-R1 (CPU-bound).
- **CPU bottleneck warning**: old server Xeons (Haswell E5-2678 v3, AVX2-only, no AVX512/AMX) cap decode speed. The marquee 227 tok/s benchmark uses 8×L20 + modern Xeon — NOT representative.

Pitfalls (verified 2026-09-01):
1. **PyPI wheel (`pip install kt-kernel`) is Linux-only** (manylinux_2_17). No Windows wheel.
2. **Windows source build requires**: CUDA toolkit (nvcc), torch CUDA build, flash-attention (painful on Windows), MSVC. High risk / hours. **Not recommended on native Windows.**
3. **Clean path on Windows = WSL2** (installed, v2, but only docker-desktop distro present — needs an Ubuntu distro). CUDA passthrough is native; the officially-supported `pip install kt-kernel` route works there (wheel ships static CUDA, no toolkit needed). Use the **LLAMAFILE backend** (GGUF) for AVX2-only CPUs — no weight conversion.
4. **AMX/AVX512 native backends are useless on Haswell** (needs AMX or AVX512+BVNNI/BF16). Fall back to AVX2/LLAMAFILE.

See `references/ktransformers-evaluation.md` for the full hardware-fit analysis and decision flow.

## Core decision: Ollama vs llama.cpp server
- **Ollama**: convenient (`ollama create/modelfile`). Key Ollama parameters for speed:
  - `num_gpu <N>` — how many transformer layers to offload to GPU (default = all). Lower = more CPU, less VRAM for KV cache. Critical for 65K context on 12GB cards.
  - `num_ctx <N>` — context window. Higher = more VRAM needed for KV cache.
  - `num_batch <N>` — prompt processing batch size. 512 is sweet spot.
  - Balance triangle: **quantization_size × GPU_layers × context_window = VRAM_budget**.
    To hit 20 tok/s on 12GB with 65K ctx: Q4_K_M + 35 GPU layers + 16GB spill to RAM.
- **llama.cpp server** (`llama-server.exe`): the way to get MTP (`--spec-type draft-mtp`) and full control. Use it when speed matters.

## Ollama GPU/VRAM balance for MoE + 65K context (RTX 3060 12GB)
When Hermes requires 65K min context but VRAM is 12GB:

| Config | GPU layers | VRAM | tok/s | Notes |
|--------|------------|------|-------|-------|
| Q4_K_M + all GPU | 59/66 | 🔴 >99% | 30 (cold) | KV cache saturates → 0.3 tok/s after context fills |
| Q4_K_M + 35 GPU | 35/66 | 🟢 ~70% | 21.1 | ✅ Sweet spot. Rest in 96GB RAM |
| Q3_K_M + 20 GPU | 20/66 | 🟢 ~50% | ~15 | More RAM, slower |

**Rule**: For 65K context on 12GB VRAM, offload ~50% of layers to CPU (`num_gpu ~35`).
The KV cache for 65K consumes ~3-4GB VRAM on Q4_K_M. Subtract that from 12GB → ~8GB for model weights.
- Verify the runtime actually loads the GGUF: exotic architectures (Gated-DeltaNet/hybrid attention on Qwen3.8-27B) need a recent llama.cpp build; Ollama 0.32.x accepted this one, but check `ollama create` output.

## Proven optimized launch (Windows + NVIDIA + 12GB VRAM, 12.6GB GGUF)
```bash
powershell.exe -NoProfile -Command "& 'C:\path\to\llama-server.exe' -m 'C:\path\to\model.gguf' --spec-type draft-mtp --spec-draft-n-max 3 --host 127.0.0.1 --port 8080 -c 8192 -ngl 99 -fa on -np 1 -lm mmap+mlock --prio 2 -b 2048 -ub 1024 -ctk q4_0 -ctv q4_0"
```
| Flag | Why |
|---|---|
| `--spec-type draft-mtp` | MTP draft (model's native speculative decoding) |
| `--spec-draft-n-max 3` | draft length; 3 is the sweet spot |
| `-fa on` | Flash Attention — smaller KV, more layers fit in VRAM |
| `-np 1` | ONE slot (default 4) — frees KV VRAM → more model layers on GPU → less CPU spill |
| `-lm mmap+mlock` | keep model in RAM (huge RAM machines: no pageouts) |
| `--prio 2` | high process priority |
| `-b 2048 -ub 1024` | prompt batch — faster prompt eval |
| `-ctk q4_0 -ctv q4_0` | quantized KV cache |
| `-ngl 99` | all layers to GPU (llama.cpp warns if it can't fit; that's expected with 12GB) |

Measured on RTX 3060 12GB / 96GB RAM / Qwen3.8-27B 3.69bpw-MTP:
- Short generation (40-60 tok): **~10-13 t/s**
- Long generation (500-900 tok): **~8.7 t/s** (was 6.7 before -fa/-np 1/-lm → +29%)
- Prompt eval: **~40-53 t/s**
- MTP draft acceptance: 27% (slow config) → 41% (optimized) — better acceptance = faster.

## Gotchas (all hit in real sessions)
1. **Client timeout does NOT kill llama.cpp generation.** A curl/python request that times out leaves the server generating in its slot. Two concurrent long generations halve speed (~3-5 t/s each). Fix: restart the server to clear slots, and keep `max_tokens` modest for long tasks.
2. **Windows Defender flags llama-server.exe as PUA** (false positive on unsigned GitHub builds). Fix: `Add-MpPreference -ExclusionPath "C:\...\llama-cpp"` (admin/UAC). Without it the exe won't run at all.
3. **git-bash/MSYS gives "Permission denied" running .exe** even after `chmod +x`. Fix: launch via `powershell.exe -NoProfile -Command "& 'C:\...\llama-server.exe' ..."` — never `./exe` in git-bash.
4. **UTF-8 mangling with curl -d on Windows git-bash**: accented chars in a JSON body break with parse errors. Fix: `curl --data-binary @-` with a file, or use Python `urllib` with `json.dumps(...).encode('utf-8')`.
5. **Model thinking eats the token budget.** Qwen3.x emits `<think>` by default; a creative prompt can spend all `max_tokens` on reasoning and return an empty/final answer. Fix: send `"chat_template_kwargs": {"enable_thinking": false}` in the llama.cpp chat completion request (or strip `<think>...</think>` from output).
6. **MTP acceptance collapses on long generations** (draft acceptance 27-41%); MTP shines on short outputs. Don't promise 13 t/s for essay-length work on 12GB VRAM.

## VRAM math (12GB card, 27B model)
- 12.6GB GGUF + 8192 KV cache does NOT fully fit in 12GB → CPU spill unavoidable → ~9-13 t/s ceiling.
- Lowering context (`-c 4096`) frees VRAM for layers → small speed gain, shorter prompts.
- Real step change needs 24GB VRAM (RTX 3090/4090) → full-GPU ~20-25 t/s with MTP.

## Ollama daemon optimization on Windows (env vars + alias + verified setup)
Proven 2026-09-03 on RTX 3060 12GB / Xeon 12-core / 96GB RAM with
RootMonsteR/Qwen3-14B-Abliterated-GGUF:Q5_K_M (agent brain, tool-calling):

**1. Set daemon env vars (User scope), then RESTART — they are read only at daemon start:**
```powershell
[Environment]::SetEnvironmentVariable('OLLAMA_FLASH_ATTENTION','1','User')      # less KV mem + faster
[Environment]::SetEnvironmentVariable('OLLAMA_KV_CACHE_TYPE','q8_0','User')     # compressed KV → more ctx fits
[Environment]::SetEnvironmentVariable('OLLAMA_MAX_LOADED_MODELS','2','User')    # e.g. 14B + vision co-resident
[Environment]::SetEnvironmentVariable('OLLAMA_KEEP_ALIVE','30m','User')         # no cold reload between uses
# Restart (taskkill //F fails through git-bash; use PowerShell):
Stop-Process -Name 'ollama app','ollama' -Force; Start-Process 'C:\Users\<user>\AppData\Local\Programs\Ollama\ollama app.exe'
```

**2. Modelfile alias with agent-tuned params** (keeps source pull untouched):
```
FROM hf.co/RootMonsteR/Qwen3-14B-Abliterated-GGUF:Q5_K_M
PARAMETER num_ctx 16384
PARAMETER num_gpu 99        # all layers to GPU
PARAMETER num_thread 12     # PHYSICAL cores, not logical (Xeon E5-2678v3: 12c/24t)
PARAMETER temperature 0.6
PARAMETER top_p 0.95
PARAMETER top_k 20
PARAMETER min_p 0.0
```
`ollama create qwen14-agent -f Modelfile` — temp/top_p/top_k/min_p are the RootMonsteR
author's recommended tool-call sampling set.

**3. Verify with a REAL tool-call, not just chat** — POST `/api/chat` with a `tools` array
and measure `eval_count/eval_duration` (tok/s), `prompt_eval` speed, `load_duration`;
then `GET /api/ps` for `size_vram` and `nvidia-smi` for actual occupancy.
Measured result: 21.9 tok/s gen, 192.9 tok/s prompt eval, 8.5s cold load, 11.8/12.3GB VRAM,
structured tool JSON ✅.

**VRAM reality:** 10GB Q5_K_M weights + 16K KV (q8_0) ≈ 12.8GB total → ~1GB spills to RAM
on a 12GB card; that is the 21.9 (not 30+) tok/s ceiling. Options to squeeze more: drop
num_ctx to 8K, or accept it — Q4 restores fit but the author warns tool-call JSON fidelity
degrades below Q5, which is worse for agents than 8 tok/s.

**Pitfall — interrupted `ollama pull` leaves NOTHING installed** (no partial blob to resume
from in `ollama list`): after any timeout/interrupt, verify with `ollama list` and re-pull
in background before assuming the model exists.

## Support files
- `references/benchmarks-rtx3060.md` — measured numbers per config, draft-acceptance details.
