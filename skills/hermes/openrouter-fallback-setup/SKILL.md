---
name: openrouter-fallback-setup
description: Set up OpenRouter fallback for Hermes model failures.
---
# OpenRouter Fallback Setup

Configure Hermes to automatically switch to a free OpenRouter model when the primary model exhausts tokens or becomes unresponsive.

## Triggers
- Want automatic model switching on token exhaustion or latency.
- Need to reduce wait times and avoid errors when primary model fails.

## Steps
1. Ensure a provider entry for OpenRouter exists under `providers:` in config.yaml.
2. Add OpenRouter as the first (or second) entry in `fallback_providers:` list, directly after the primary provider.
3. **Use verified free models** — see `references/openrouter-free-models.md` in `hermes-model-config` for the full list. Best defaults:
   - Primary: `nvidia/nemotron-3-ultra-550b-a55b:free` (1M ctx, best quality)
   - Fallback 1: `nvidia/nemotron-3-super-120b-a12b:free` (262K)
   - Fallback 2: `nvidia/nemotron-3-nano-30b-a3b:free` (256K)
   - Last resort: `deepseek/deepseek-v4-flash` (barato, ~$0.0000002/tok)
4. Reduce timeouts for fast fallback: set `terminal.timeout` to 10-15 seconds, `agent.api_max_retries` to 1-2.
5. Optionally enable strict tool use enforcement (`tool_use_enforcement: strict`).
6. Reload configuration with `hermes config reload` or restart Hermes.
7. Test with a long prompt; verify fallback appears in logs/status.

## Pitfalls
- Avoid timeouts <5s to prevent premature fallback.
- Ensure `OPENROUTER_API_KEY` is set as env var or in config.
- Bundled skills like `hermes-model-config` are protected; this skill complements them.

## References
- See `references/openrouter-fallback-example.md` for a ready-to-copy snippet.
- See `templates/model-fallback-config.yaml` for a full example.