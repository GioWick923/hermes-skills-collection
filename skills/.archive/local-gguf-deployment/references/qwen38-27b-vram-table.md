# Ejemplo verificado: Qwen3.8-27B en RTX 3060 12GB (2026-08-20)

## Tabla de cuantizaciones (mradermacher/Qwen3.8-27B-OBLITERATED-GGUF, tamaños reales)

| Quant | Tamaño | % en GPU (12GB) | Velocidad est. | Veredicto |
|---|---|---|---|---|
| Q2_K | 10.9 GB | ~100% | 20-30 tok/s | 🟡 calidad baja |
| Q3_K_S | 12.3 GB | ~95% | 15-25 tok/s | 🟢 rápida |
| Q3_K_M | 13.5 GB | ~85% | 12-20 tok/s | 🟢 **balance** |
| IQ4_XS | 15.4 GB | ~70% | 8-14 tok/s | 🟡 |
| Q4_K_M | 16.8 GB | ~65% | 6-12 tok/s | 🟡 calidad pero lenta |
| Q5_K_M | 19.5 GB | ~55% | 4-8 tok/s | ❌ |
| Q6_K | 22.4 GB | ~45% | 3-6 tok/s | ❌ |
| Q8_0 | 29.0 GB | — | <3 tok/s | ❌ |

Mismo repo incluye `mmproj-f16.gguf` (0.93GB) y `mmproj-Q8_0.gguf` (0.63GB) → modelo multimodal
(vista) si se resuelve el mmproj (Ollama 0.32.14 no soporta PROJECTOR).

## Modelo alternativo probado: 3.69bpw-MTP (12.6GB)
`soyaakinohara/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf`:
- Cuantización mixta Ridge-style (Q4_K/IQ2_S/IQ3_S/Q5_K/Q6_K + F32/Q8_0 sensibles) → mejor
  calidad que flat Q3 a mismo tamaño.
- Cabe 100% en 12GB VRAM → sin offload CPU.
- MTP nativo: llama.cpp `--spec-type draft-mtp --spec-draft-n-max 3` → hasta ~37 tok/s
  reportado (RTX 5060 Ti 16GB + 3070 8GB). En 3060 12GB estimado 15-30 tok/s.
- ⚠️ Arquitectura Gated-DeltaNet/hybrid-attention → Ollama 0.32.14 puede NO cargarla;
  usar llama.cpp server (binarios CUDA en `$LOCALAPPDATA/hermes/llama-cpp/`).
- SHA256 esperado: `17ef7767533efd039d13594603bb0d9a787965759ec653b42f9221b50318e4d7`
  (verificar tras descarga).

## Config óptima (repo OBLITERATUS)
temperature=0, repeat_penalty=1.15, max_new_tokens≥2048, system prompt vacío, thinking off
para code-heavy.

## Resultado de instalación (Q3_K_M vía Ollama)
- `ollama create` OK: modelo `qwen3.8-27b-obliterated`, 13GB, ~3-5 min de copia.
- Medición real: `eval rate: 6.34 tokens/s`, `load duration: 37.9s` (primera carga).
- El modelo responde con `<think>`; `ablit` corta el bloque automáticamente.

## Test de abliteración (mini-benchmark)
6 prompts (2 control + malware/phishing/exploits/contraseñas) → 0 refusals = abliterado confirmado.
Script de test: `$LOCALAPPDATA/Temp/test-obliteration.py` (usa /api/chat + strip <think>).
Refusal markers usados: no puedo/lo siento/no es apropiado/i cannot/i can't/i'm sorry, etc.
