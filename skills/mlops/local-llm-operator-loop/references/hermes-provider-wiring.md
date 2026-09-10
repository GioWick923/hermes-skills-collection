# Wiring a local Ollama model as a Hermes backend — verified recipe (2026-09-03)

Host: Windows, RTX 3060 12GB, Ollama 0.33.2, Hermes desktop. Model: `qwen14-agent` = alias of `hf.co/RootMonsteR/Qwen3-14B-Abliterated-GGUF:Q5_K_M`.

## 1. Known-good Modelfile (agent-tuned)
```dockerfile
FROM hf.co/RootMonsteR/Qwen3-14B-Abliterated-GGUF:Q5_K_M
PARAMETER num_ctx 65536
PARAMETER num_gpu 99
PARAMETER num_thread 12
PARAMETER temperature 0.6
PARAMETER top_p 0.95
PARAMETER top_k 20
PARAMETER min_p 0.0
```
`ollama create qwen14-agent -f Modelfile` — num_ctx MUST be ≥64K or Hermes refuses the model (see §3). num_thread = physical cores (Xeon E5-2678 v3 = 12).

## 2. config.yaml provider block (edit via terminal+python, file tools blocked; backup first; no BOM)
```yaml
providers:
  ollama_local:
    provider: custom
    api_mode: chat_completions
    base_url: http://127.0.0.1:11434/v1
    api_key: ollama          # dummy non-empty; Ollama ignores it
    context_length: 65536    # THIS is what Hermes reads for the 64K gate
```
Fallback chain entry (last resort): same shape inside `fallback_providers:` list with `model: qwen14-agent`.
Delegation routing (subagents run local, $0):
```yaml
delegation:
  provider: ollama_local
  model: qwen14-agent
  base_url: http://127.0.0.1:11434/v1
  api_key: ollama
```

## 3. The 64K gate (exact error)
```
Failed to initialize agent: Model qwen14-agent has a context window of 16,384
tokens, which is below the minimum 64,000 required by Hermes Agent.
```
Both fixes are required: `providers.<name>.context_length` (clears the gate) and Modelfile `num_ctx` (server actually allocates it). Setting only the provider key passes the gate but the server still truncates at its own num_ctx.

## 4. Invocation + verification traps
- `hermes chat -q "..." --provider ollama_local -m qwen14-agent -Q` works.
- `-m qwen14` (alias form) silently falls back to the fallback chain — no error. ALWAYS confirm the answering model: `hermes sessions export --format jsonl --session <id> file.jsonl` → check the `model` field of the session record.
- Raw tool-call probe (before touching config): `curl http://127.0.0.1:11434/v1/chat/completions` with a `tools` array → expect structured `tool_calls` in `choices[0].message`, not JSON leaked into `content`.

## 5. Measured performance (real, not estimated)
| Metrica | Valor |
|---|---|
| Generacion | 21.9 tok/s (Q5_K_M, 12GB) |
| Prompt eval | 192.9 tok/s → ~40K system prompt ≈ 6 min primera llamada |
| Carga modelo | 8.5s (luego residente por KEEP_ALIVE) |
| VRAM | 11.8/12.3 GB usada, ~1GB spill a RAM |
Implication: use local for delegation/fallback/one-shot batch; keep an API model as interactive primary.

## 6. Ollama env tuning (Windows)
```powershell
[Environment]::SetEnvironmentVariable('OLLAMA_FLASH_ATTENTION','1','User')
[Environment]::SetEnvironmentVariable('OLLAMA_KV_CACHE_TYPE','q8_0','User')
[Environment]::SetEnvironmentVariable('OLLAMA_MAX_LOADED_MODELS','2','User')
[Environment]::SetEnvironmentVariable('OLLAMA_NUM_PARALLEL','1','User')
[Environment]::SetEnvironmentVariable('OLLAMA_KEEP_ALIVE','30m','User')
```
Restart: `Stop-Process -Name 'ollama app','ollama' -Force; Start-Process '...\ollama app.exe'` then `curl localhost:11434/api/version`. From git-bash, `taskkill //F` fails (arg mangling) — use PowerShell. Check residency: `curl localhost:11434/api/ps` (size_vram vs size shows GPU vs RAM split).

## 7. VRAM-fit table learned this session (12GB card)
| Model | Fits 12GB? |
|---|---|
| 30B Q4 (18.6GB) | NO — CPU swap, unusable speed |
| 27B dense IQ2_M | NO — ~13-14GB real VRAM |
| 14B Q5_K_M (10.5GB) | YES — ~1GB spill, 22 tok/s |
| 14B Q4_K_M (9GB) | YES but author warns tool-JSON fidelity drops below Q5 for agents |
| 8B / 2.6B | YES — plenty of headroom |
Rule: weights + KV cache + ~0.8GB overhead must fit; for agent/tool work prefer Q5+ over Q4.
