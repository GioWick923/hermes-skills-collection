---
category: mlops
name: local-llm-picker
description: "Pick and recommend the right local LLM (GGUF quant, MoE, abliterated/uncensored) for the user's actual GPU/RAM, explain the concepts, and give runnable setup steps for llama.cpp / LM Studio on consumer hardware (incl. integrated GPUs)."
platforms: [linux, macos, windows]
---

# Local LLM Picker

## When to use
- User asks "can I run local AI on my laptop?", "what model fits my GPU?", "is there an uncensored/abliterated version?", "best local model for X".
- User shares a YouTube/video about local AI, CUDA moat, Vulkan, Mojo, etc. — follow up with hardware-matched model advice.
- You need to explain GGUF, Q4_K_M, MoE, abliterated, context windows, or tokens/sec to a non-expert.

## Core workflow
1. **Detect hardware** (see `references/hardware-detect.md` for per-OS commands). Capture: GPU model + whether dedicated or integrated, total RAM, CPU.
2. **Match to model size + quant** (rule of thumb):
   - Model weights in Q4 ≈ 0.55–0.6 GB per 1B params (dense). A 7B Q4_K_M ≈ 4.5 GB.
   - On **integrated GPU** (Intel Iris Xe, AMD iGPU, Apple), VRAM is **shared system RAM** — the model + OS + context all fight for the same pool. Keep 6–8 GB free for the OS.
   - On **dedicated GPU**, check VRAM; if model > VRAM, it offloads to CPU (slow) or you drop quant.
3. **Recommend** a GGUF file + quant. Start conservative (smaller/faster) then offer the "quality" option.
4. **Explain** the chosen model in plain Spanish/English: what the name parts mean, why it fits, expected tokens/sec.
5. **Setup tips**: LM Studio → runtime **Vulkan** (works on any vendor) → load .gguf. Cap context length low on small RAM (16k–32k) because the KV cache eats RAM.

## Key concepts to teach (one-liners)
- **GGUF**: single-file model format for llama.cpp; quantized to fit GPU RAM. No installer/account.
- **Q4_K_M**: 4-bit quantization, ~near-original quality, best size/quality tradeoff for local.
- **MoE (Mixture-of-Experts)**: e.g. Qwen3-30B-A3B has 30B total but activates only ~3.3B/token → runs like a small model, thinks like a big one. Needs ~18GB Q4 (too big for 16GB shared RAM unless Q3 + CPU).
- **Abliterated / Uncensored**: modified to remove the refusal/censorship vector. Keeps ~99% of quality. Legal in local-AI community. "abliterated-v2" is the common tag (QuantFactory).
- **Context window**: how much text fits in one session. 128k ≈ ~100k words (≈200 pages). 1M exists (Qwen2.5-7B-Instruct-1M) but the KV cache cost makes it impractical on 16GB — use 16k–32k in practice.
- **tokens/sec**: output speed; >10 is faster than comfortable reading. Integrated Iris Xe does ~6–10 tok/s on a 7B Q4 (still usable).

## Pitfalls
- **Windows `python3` store alias**: `python3` resolves to the Microsoft Store stub and fails ("no se encontró Python"). Use the Hermes venv Python directly:
  ```bash
  VENV_PY="$HOME/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
  "$VENV_PY" script.py ...
  ```
  (Or just `python` if UV-provided 3.11 is on PATH.)
- **Integrated GPU = shared RAM**: never recommend a 7B+ Q4 plus 128k context on 16GB — it OOMs/trashes. Cap context.
- **Abliterated version of 1M-context model may not exist**: the wide-context variant is usually base/censored only. Offer the abliterated 128k instead.
- **Top-end Nvidia CUDA still faster**: be honest — on flagship Nvidia cards raw CUDA beats Vulkan. The point is "not Nvidia-or-nothing", not "Vulkan wins everywhere".

## Curated model shortlist (see `references/models.md`)
Covers the common consumer cases: 3B starter, 7B workhorse, 7B abliterated, 7B-1M wide context, 30B MoE, and where to download each.

## Sources
Verified via web_search during a 2026 session: Qwen2.5-7B-Instruct-abliterated-v2 (QuantFactory), Qwen2.5-7B-Instruct-1M (Triangle104), Qwen3-30B-A3B MoE (Qwen official GGUF), Iris Xe benchmark ~8 tok/s on 7B Q4 (zenvanriel.com, 9bench.com).
