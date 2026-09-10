# Hermes Config Snippets — Free Providers

Snippets ready-to-copy para configurar cada proveedor gratis en Hermes.

## Como Provider Primario

### Groq (sin CC, mejor para empezar)

```yaml
model:
  default: moonshotai/kimi-k2-instruct
  provider: custom
  base_url: https://api.groq.com/openai/v1
  max_tokens: 32000
```

.env: `GROQ_API_KEY=gsk_xxxxxxxx`

### Google Gemini (sin CC, 1M contexto, multimodal)

```yaml
model:
  default: gemini-3.6-flash
  provider: custom
  base_url: https://generativelanguage.googleapis.com/v1beta
  max_tokens: 65536
```

.env: `GEMINI_API_KEY=AIzaxxxxxxxx`

### Mistral AI (sin CC, 256K)

```yaml
model:
  default: mistral-medium-3-5-128b
  provider: custom
  base_url: https://api.mistral.ai/v1
  max_tokens: 32000
```

.env: `MISTRAL_API_KEY=xxx`

### Cohere (sin CC, 436K contexto)

```yaml
model:
  default: command-a-218b
  provider: custom
  base_url: https://api.cohere.com/v2
  max_tokens: 32000
```

.env: `COHERE_API_KEY=xxx`

### NVIDIA NIM (verif. teléfono, 125 modelos, 1M ctx)

```yaml
model:
  default: z-ai/glm-5.2
  provider: custom
  base_url: https://integrate.api.nvidia.com/v1
  max_tokens: 66000
```

.env: `NVAPI_KEY=nvapi-xxx`

### DeepSeek (sin CC)

```yaml
model:
  default: deepseek-chat-v3-2
  provider: custom
  base_url: https://api.deepseek.com/v1
  max_tokens: 32000
```

.env: `DEEPSEEK_API_KEY=sk-xxx`

## Como Fallbacks (cadena de respaldo) — OpenRouter

Para configurar fallbacks, **NO uses `hermes config set`** — no soporta listas.
Usa el script de la skill:

```bash
python skills/freellm-providers/scripts/write-fallbacks.py --all-free
```

O este script Python para OpenRouter con los modelos que **SÍ funcionan**:

```python
import yaml, shutil, os, time
from pathlib import Path

LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")
env_path = os.path.join(LOCALAPPDATA, "hermes", ".env")
with open(env_path) as f:
    openrouter_key = [l.strip().split("=",1)[1] for l in f if l.startswith("OPENROUTER_API_KEY=")][0]

cfg = os.path.join(LOCALAPPDATA, "hermes", "config.yaml")
bak = cfg + f".bak.{int(time.time())}"
shutil.copy2(cfg, bak)

with open(cfg, encoding="utf-8") as f:
    d = yaml.safe_load(f)

d["fallback_providers"] = [
    {"provider": "custom", "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
     "base_url": "https://openrouter.ai/api/v1", "api_key": openrouter_key, "api_mode": "openai"},
    {"provider": "custom", "model": "nvidia/nemotron-3-super-120b-a12b:free",
     "base_url": "https://openrouter.ai/api/v1", "api_key": openrouter_key, "api_mode": "openai"},
    {"provider": "custom", "model": "nvidia/nemotron-3-nano-30b-a3b:free",
     "base_url": "https://openrouter.ai/api/v1", "api_key": openrouter_key, "api_mode": "openai"},
]

with open(cfg, "w", encoding="utf-8") as f:
    yaml.safe_dump(d, f, sort_keys=False, default_flow_style=False)

print(f"✅ Fallbacks escritos. Backup: {bak}")
```

## Modelos GRATIS que SÍ funcionan en OpenRouter (verificado 2026-08-21)

| Modelo | Contexto | Latencia | Bueno para |
|--------|----------|----------|-----------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | **1M** 🏆 | 0.4s | ⭐ **MEJOR DEFAULT** — razonamiento, coding, todo |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262K | 0.4s | 🔧 Coding, análisis, builder |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256K | 0.5s | ⚡ Tareas rápidas, chat |
| `nvidia/nemotron-3.5-lightning:free` | — | 0.5s | Creativo, respuestas rápidas |
| `poolside/laguna-s-2.1:free` | 262K | 0.7s | ✍️ Escritura, texto creativo (reasoning) |
| `openrouter/free` | — | 0.5s | Auto-routing al mejor free disponible |

## Modelos que NO son gratis en OpenRouter (cuestan aunque sea poco)

| Modelo | Costo | Contexto | Alternativa gratis |
|--------|-------|----------|-------------------|
| `deepseek-v4-flash` | ⚠️ **PAGA** (~$0.0000002/token) | 1M | `nemotron-3-ultra:free` (1M ctx, gratis) |
| `deepseek/deepseek-v4-pro` | ⚠️ **PAGA** | 1M | `nemotron-3-ultra:free` |
| `tencent/hy3-free` | ❌ **Deprecado** (400 Bad Request) | — | `nemotron-3-super:free` |

## Modelos que fallan o requieren créditos extra

| Modelo | Problema |
|--------|---------|
| `cohere/command-a-218b:free` | ❌ 400 Bad Request |
| `google/gemini-3.6-flash:free` | ❌ 404 Not Found |
| `z-ai/glm-5.2:free` | ⚠️ 429 Too Many Requests (rate limit) |

## Sin Hermes — Clientes Externos

### Claude Code con provider gratis

```bash
export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
export ANTHROPIC_AUTH_TOKEN="sk-or-xxx"  # tu key de OpenRouter
export ANTHROPIC_API_KEY=""               # debe estar vacío
```

### Cursor

```
Settings → Models → Add Model
  Model name: moonshotai/kimi-k2-instruct
  Base URL: https://api.groq.com/openai/v1
  API key: gsk_xxx
```

### Codex CLI

```bash
export OPENAI_BASE_URL="https://api.groq.com/openai/v1"
export OPENAI_API_KEY="gsk_xxx"
codex --model "moonshotai/kimi-k2-instruct"
```

### aider

```yaml
# .aider.conf.yml
openai-api-base: https://api.groq.com/openai/v1
openai-api-key: gsk_xxx
model: moonshotai/kimi-k2-instruct
```

### Open WebUI

```
Settings → Connections → OpenAI
  URL: https://api.groq.com/openai/v1
  Key: gsk_xxx
```