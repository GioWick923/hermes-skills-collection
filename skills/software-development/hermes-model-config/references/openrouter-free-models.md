---
title: OpenRouter Free Models for Hermes (Verified 2026-08-21)
description: Models verified FREE on OpenRouter that work with Hermes Agent — tested live this session
tags: [openrouter, free, models, hermes, verified]
---

# OpenRouter Free Models — Verified ✅

Models **100% gratis** en OpenRouter, verificados con llamadas reales.  
Actualizado: 2026-08-21 por benchmark directo contra la API.

## ✅ GRATIS — Funcionan

| Modelo | Contexto | Latencia | Bueno para |
|--------|----------|----------|-----------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | **1M** 🏆 | 0.4s | ⭐ **Mejor default** — razonamiento, coding, agente |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262K | 0.4s | 🔧 Coding, análisis, builder |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256K | 0.5s | ⚡ Tareas rápidas, chat |
| `nvidia/nemotron-3.5-lightning:free` | — | 0.5s | Creativo, respuestas rápidas |
| `poolside/laguna-s-2.1:free` | 262K | 0.7s | ✍️ Escritura (reasoning model) |
| `openrouter/free` | — | 0.5s | Auto-routing al mejor free disponible |

## ⚠️ PAGA (aunque sea barato) — NO gratis

| Modelo | Costo | Contexto | Alternativa gratis |
|--------|-------|----------|-------------------|
| `deepseek/deepseek-v4-flash` | ~$0.0000002/token | 1M | `nemotron-3-ultra:free` (1M ctx) |
| `deepseek/deepseek-v4-pro` | ~$0.000001/token | 1M | `nemotron-3-ultra:free` |
| `tencent/hy3-free` | ❌ **Deprecado** (400) | — | `nemotron-3-super:free` |

## ❌ Fallan / No disponibles

| Modelo | Problema |
|--------|---------|
| `cohere/command-a-218b:free` | 400 Bad Request |
| `google/gemini-3.6-flash:free` | 404 Not Found |
| `z-ai/glm-5.2:free` | 429 Too Many Requests (rate limit) |
| `tencent/hy3:free` / `tencent/hy3-free` | Deprecado — 400 Bad Request |
| `meta-llama/llama-3.1-8b-instruct:free` | Puede no estar disponible |

## Estrategia de router recomendada (free-first)

```yaml
model:
  default: nvidia/nemotron-3-ultra-550b-a55b:free   # GRATIS, 1M ctx
  provider: openrouter
  base_url: https://openrouter.ai/api/v1
  max_tokens: 66000

fallback_providers:
  - provider: custom
    model: nvidia/nemotron-3-super-120b-a12b:free   # GRATIS
    base_url: https://openrouter.ai/api/v1
    api_key: <openrouter_key>
    api_mode: openai
  - provider: custom
    model: nvidia/nemotron-3-nano-30b-a3b:free      # GRATIS
    base_url: https://openrouter.ai/api/v1
    api_key: <openrouter_key>
    api_mode: openai
  - provider: custom
    model: poolside/laguna-s-2.1:free                # GRATIS
    base_url: https://openrouter.ai/api/v1
    api_key: <openrouter_key>
    api_mode: openai
  - provider: custom
    model: deepseek/deepseek-v4-flash                # LAST RESORT (barato)
    base_url: https://openrouter.ai/api/v1
    api_key: <openrouter_key>
    api_mode: openai
```

## ⚡ Cómo verificar un modelo gratis

```bash
python -c "
import json, urllib.request
# Check pricing
req = urllib.request.Request('https://openrouter.ai/api/v1/models',
    headers={'Authorization':'Bearer \$OPENROUTER_API_KEY'})
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())
for m in data['data']:
    if 'nemotron' in m['id'] or 'deepseek' in m['id']:
        p = m.get('pricing', {})
        free = float(p.get('prompt',1))==0 and float(p.get('completion',1))==0
        print(f\"{'✅' if free else '💰'} {m['id']:55s} ctx={m.get('context_length','?'):>8s}\")
"
```

## Notas importantes

- **OpenRouter requiere $10 top-up una vez** para desbloquear el free tier. Después los modelos free no consumen ese saldo.
- **deepseek-v4-flash NO es gratis** en OpenRouter aunque sea barato (~$0.0000002/tok). Es un último recurso.
- **Nemotron 3 Ultra es el mejor default gratis** por su 1M contexto y velocidad consistente (~0.4s).
- Los modelos marcados como `:free` en OpenRouter pueden cambiar — verifica con `openrouter/free` como fallback general.