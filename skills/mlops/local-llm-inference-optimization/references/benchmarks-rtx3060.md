# Benchmarks: RTX 3060 12GB + Qwen3.8-27B 3.69bpw-MTP (12.6GB GGUF)

Hardware: RTX 3060 12GB, 96GB RAM, AMD Ryzen, Windows 11, CUDA 13.1
Runtime: llama.cpp b10517 CUDA build (cudart-llama-bin + llama-bin)
Model: soyaakinohara/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf (AEON-7 Ultimate Uncensored)

## Config comparison

### Default (4 slots, no flash attn, no mlock)
```
llama-server.exe -m model.gguf --spec-type draft-mtp --spec-draft-n-max 3 -c 8192 -ngl 99 -ctk q4_0 -ctv q4_0
```
- Short gen (40 tok): ~10 t/s
- Long gen (900 tok): 6.74 t/s
- Prompt eval: 53.6 t/s (122 tok prompt)
- Draft acceptance: 27.7%

### Optimized (1 slot, flash attn, mlock, prio, batch)
```
llama-server.exe -m model.gguf --spec-type draft-mtp --spec-draft-n-max 3 -c 8192 -ngl 99 -fa on -np 1 -lm mmap+mlock --prio 2 -b 2048 -ub 1024 -ctk q4_0 -ctv q4_0
```
- Short gen (43 tok): 9.8 t/s
- Long gen (900 tok): 8.7 t/s (+29%)
- Prompt eval: 41.6 t/s (41 tok prompt)
- Draft acceptance: 41.6% (499/1198)

### Ollama (same GGUF, no MTP control)
```
ollama run qwen3.8-27b-abliterated-mtp
```
- Short gen: 7.35 t/s
- Poll: Ollama ignores MTP entirely; figure it adds ~10% overhead vs bare llama.cpp

## Key observations
- MTP draft acceptance drops from 40%+ to 27% when two slots are active (client timeout leaves generation running).
- Prompt eval is faster with larger batch: -b 2048 -ub 1024 vs defaults.
- The model does NOT fully fit in 12GB VRAM even with these optimizations → CPU spill is the bottleneck.
- Flash attention (`-fa on`) frees enough KV cache to fit more model layers, directly improving acceptance.
- 1 slot (`-np 1`) is the single biggest gain: it frees KV memory reserved for 3 other slots.