---
category: autonomous-ai-agents
name: model-fallback-optimizer
description: Try free models first, then fall back to paid GLM 5.3.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# Model Fallback Optimizer Skill

This skill iterates through a list of free model aliases, testing each one
until it finds a working model. If all free models fail/exhausted, it falls
back to the paid GLM 5.3 model.

## When to Use

- "Quiero usar modelos gratuitos primero y solo pagar cuando sea necesario"
- "Agota todas las opciones free antes de usar el modelo de pago"
- "Optimiza costos usando modelos gratuitos disponibles"

## How It Works

1. Defines an ordered list of free model aliases to try
2. For each model, performs a lightweight test (simple chat query)
3. On first successful response, sets that model as default
4. If all free models fail, sets paid GLM 5.3 as default
5. Can be run manually or scheduled via cron

## Free Models List (Prioritized)

The skill tries these models in order (all should be free/tier-free):

1. `deepseek-v4.1-flash` (DeepSeek V4.1 free)
2. `deepseek-v4-flash` (DeepSeek V4 free)
3. `mimo-v2.5` (Mimo V2.5 free)
4. `hy3-free` (Tencent Hy3 free)
5. `orcarouter` (OrcaRouter GLM 5.3 flash free)
6. `aihubmix-glm` (AIHubMix GLM 5.3 free)
7. `bai-glm` (BAI GLM 5.3 flash)
8. `experiential` (Experiential GPT-6 Astra)
9. `bai-hy3` (BAI Hy3)
10. `bai-mimo` (BAI Mimo V2.5)

## Paid Fallback

If all above fail, falls back to:
- `glm-5.3` (Paid GLM 5.3 via OrcaRouter with dedicated key)

## Usage

```bash
# Run the optimizer interactively
hermes -s model-fallback-optimizer

# Or run as a one-shot command
hermes chat -q "Optimize model selection" -s model-fallback-optimizer

# Schedule via cron (runs every 6 hours)
hermes cron create "0 */6 * * *" -p "Run model fallback optimizer" -s model-fallback-optimizer
```

## Implementation Details

The skill uses Python to:
1. Read current config to get API keys
2. Iterate through free model aliases
3. For each, test with `hermes chat -q "test" -m <alias> --timeout 10`
4. Check for successful response (non-error, reasonable output)
5. On success, set `model.default` via `hermes config set`
6. If all fail, set `model.default` to `glm-5.3`
7. Reload configuration to apply changes

## Configuration Notes

- Requires valid API keys for all providers in `.env` or credential pool
- Works best when free models have available quota/rate limits
- Paid GLM 5.3 uses its own API key (`sk-orc...gIPJ` alias)
- Skill respects existing `fallback_providers` but overrides `model.default`

## Example Output

After running, you might see:

```
🔍 Testing free model: deepseek-v4.1-flash
✅ Success! Setting model.default to deepseek-v4.1-flash
```

Or if all free fail:

```
🔍 Testing free model: deepseek-v4.1-flash
❌ Rate limited or error
🔍 Testing free model: deepseek-v4-flash
❌ Service unavailable
... (all free models tested)
💰 All free models exhausted. Setting model.default to glm-5.3 (paid)
```
