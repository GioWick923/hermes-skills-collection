# Curated local-LLM shortlist (verified 2026)

GGUF files ready for llama.cpp / LM Studio. Quant noted. "Works on 16GB shared RAM + integrated GPU" = yes if context capped at 16-32k.

## Starter (fast, tiny)
- **Qwen2.5-3B-Instruct** Q4_K_M (~2 GB) — arranca aqui si tu GPU es integrada. ~12-15 tok/s en Iris Xe.
  - bartowski/Qwen2.5-3B-Instruct-GGUF

## Workhorse 7B (censored, base)
- **Qwen2.5-7B-Instruct** Q4_K_M (~4.5 GB) — calidad alta, multilingue (espanol natural).
  - bartowski/Qwen2.5-7B-Instruct-GGUF
  - archivo: Qwen2.5-7B-Instruct-Q4_K_M.gguf

## 7B abliterated / uncensored (sin censura)
- **Qwen2.5-7B-Instruct-abliterated-v2** Q4_K_M (~4.5 GB) — RECOMENDADO para uso general sin refusals.
  - QuantFactory/Qwen2.5-7B-Instruct-abliterated-v2-GGUF
  - archivo: Qwen2.5-7B-Instruct-abliterated-v2.Q4_K_M.gguf
- **Qwen2.5-7B-Instruct-Uncensored** Q4_K_M — alternativa fine-tune (no abliteration).
  - QuantFactory/Qwen2.5-7B-Instruct-Uncensored-GGUF
  - mradermacher/Qwen2.5-7B-Instruct-Uncensored-i1-GGUF (imatrix, mejor calidad)

## Wide-context 7B (1M tokens) — SOLO censored
- **Qwen2.5-7B-Instruct-1M** Q4_K_M (~4.5 GB) — contexto de 1 millon; NO existe version abliterada.
  - Triangle104/Qwen2.5-7B-Instruct-1M-Q4_K_M-GGUF
  - En 16GB usa contexto 16-32k en la practica (el KV cache de 1M no cabe).

## MoE big-thinker (rinde como grande, corre como chico)
- **Qwen3-30B-A3B** — 30B total / ~3.3B activos por token. Q4 ~18 GB -> no entra en 16GB compartida (usa Q3 + CPU o 24GB+).
  - Qwen/Qwen3-30B-A3B-GGUF
  - abliterada: huihui-ai/Qwen3-30B-A3B-abliterated

## Small-but-mighty (velocidad)
- **Qwen3-4B** (dense) — dicen rinde como 72B previo; muy rapido en integrada; existe abliterada.

## Otros uncensored populares
- Dolphin, Heretic (basados en Qwen/Llama) — muy usados en LM Studio.
