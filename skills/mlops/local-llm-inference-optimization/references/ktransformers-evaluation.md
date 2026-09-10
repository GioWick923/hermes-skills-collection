# ktransformers evaluation (RTX 3060 12GB + 96GB RAM, 2026-09-01)

Evaluated kvcache-ai/ktransformers (kt-kernel) as a local inference engine option on
Gio's hardware. Verdict: useful for **access to 5-10x larger MoE models**, NOT for
speeding up models that already fit in VRAM.

## Hardware verified
- GPU: NVIDIA RTX 3060, 12288 MiB, driver 591.86
- RAM: 96GB total (46GB free at check)
- CPU: Intel Xeon E5-2678 v3 @ 2.50GHz, 12c/24t, AVX2 only (NO AVX512/AMX/BF16)
- VS BuildTools 2022 present; **CUDA toolkit absent** (`nvcc` not found); torch 2.13 **CPU-only** (`torch.cuda.is_available()==False`)

## What ktransformers is
Heterogeneous CPU-GPU inference for MoE models. Hot experts → GPU, cold experts → CPU RAM.
Paper won SOSP'25 ("Unleashing the Full Potential of CPU/GPU Hybrid Inference for MoE Models").
Two user-facing capabilities from kt-kernel source tree: Inference + SFT (LLaMA-Factory).

## Fit matrix on this hardware
| Model | Params | Active | Fits 12GB? | Verdict |
|-------|--------|--------|-----------|---------|
| Qwen3-30B-A3B | 30B | 3B | ✅ | Already runs via Ollama; KT no faster (fits fully) |
| Qwen3-Next | 235B | 4B | ❌ | 🟢 Great target — only 4B active, ~15-30 tok/s |
| DeepSeek-R1-0528 | 671B | 37B | ❌ | 🟡 Usable ~5-10 tok/s (CPU-bound on Haswell) |
| Kimi-K2 / MiniMax | 100-200B | ~16B | ❌ | 🟡 Usable, slow |

## Conceptual rule (user correction)
User asked "¿No mejora nuestros modelos locales?" — the honest answer: **NO for models that
already fit in VRAM** (Ollama/llama.cpp with full offload is equal or better). ktransformers
adds VALUE only via access to models Ollama cannot load on 12GB. Frame as "más grande", not
"más rápido".

## Installation facts (from kt-kernel README, fetched 2026-09-01)
- **Option 1 PyPI**: `pip install kt-kernel`. Pre-built wheel ships static CUDA (SM 80/86/89/90
  = Ampere RTX 3000+/Ada/Hopper; Turing SM 7.5 NOT supported). **Linux x86-64 only**
  (manylinux_2_17). No compilation, no CUDA toolkit needed — but Linux-only.
- **Option 2 source**: needs conda env py3.11, `git submodule update --init --recursive`,
  `./install.sh` (auto-detects AMX/AVX512), cmake + libhwloc + pkg-config. Windows builds
  additionally need CUDA toolkit (nvcc in PATH) + torch CUDA + flash-attention.
- Backends: AMXINT4/INT8 (needs AMX), RAWINT4/FP8/BF16 (needs AVX512 variants), LLAMAFILE
  (GGUF, universal AVX2). **On this Haswell only LLAMAFILE (GGUF) is viable.**
- Verify: `kt version` or `python -c "from kt_kernel import KTMoEWrapper"`.
- SGLang integration via `sglang-kt` fork (uninstall official sglang first).

## Windows path recommendation
- **Native Windows**: source build, high risk (CUDA toolkit + torch CUDA + flash-attention on
  Windows), hours. NOT recommended.
- **WSL2**: the clean path. Already installed (v2) but only `docker-desktop` distro present —
  needs an Ubuntu distro (`wsl --install -d Ubuntu`). Native CUDA passthrough; the PyPI wheel
  (static CUDA) works there without a toolkit. Use LLAMAFILE backend for AVX2-only CPU.

## Decision flow
1. Does the model fit entirely in 12GB VRAM? → Ollama/llama.cpp, skip ktransformers.
2. Is it a huge MoE (100B+) with low active params that only fits in 96GB RAM? → ktransformers.
3. CPU has AVX512/AMX? → native backends. AVX2-only → LLAMAFILE (GGUF).
