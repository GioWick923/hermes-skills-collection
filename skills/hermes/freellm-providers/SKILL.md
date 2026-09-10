---
category: hermes
name: freellm-providers
version: "1.0.0"
description: "Integra 444+ APIs LLM GRATIS de awesome-free-llm-apis / freellm.net en Hermes. Proveedores sin tarjeta, configs ready-to-copy, y router de fallbacks para maximizar uptime sin gastar."
argument-hint: "mejores proveedores gratis | config para [provider] | testear endpoint gratis"
allowed-tools: Bash, Read, Write, Python
homepage: https://freellm.net
author: <GITHUB_USER>
license: MIT
user-invocable: true
---

# freellm-providers

Integración de **444+ APIs LLM gratis de 31 proveedores** (awesome-free-llm-apis / freellm.net) en Hermes.

Datos actualizados **a diario** desde [freellm.net](https://freellm.net).

## ¿Por qué?

Tu stack local (Ollama, ablit, Ornith) cubre lo crítico. Pero tener **31 proveedores gratis** como respaldo significa:
- Si un modelo se cae o rate-limit → fallback automático
- Modelos gratuitos de última generación (GLM-5.2, Gemini 3.6 Flash, Nemotron 3 Ultra, etc.)
- Sin tarjeta de crédito para la mayoría
- 1M+ de contexto en varios

## Proveedores TOP sin tarjeta de crédito

| Proveedor | Modelos Gratis | Mejor Modelo | Contexto | Consigue Key |
|-----------|---------------|-------------|----------|-------------|
| **Groq** | 12 | `moonshotai/kimi-k2-instruct` | 131K | [console.groq.com/keys](https://console.groq.com/keys) |
| **Google Gemini** | 17 | `gemini-3.6-flash` | 1M | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **GitHub Models** | 16 | `Phi-4` | 1M | [github.com/marketplace/models](https://github.com/marketplace/models) |
| **Cloudflare Workers AI** | 40 | `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | 10M | [dash.cloudflare.com](https://dash.cloudflare.com/profile/api-tokens) |
| **Mistral AI** | 12 | `mistral-medium-3-5-128b` | 256K | [console.mistral.ai](https://console.mistral.ai/api-keys) |
| **Cohere** | 12 | `command-a-218b` | 436K | [dashboard.cohere.com](https://dashboard.cohere.com/api-keys) |
| **Hugging Face** | 7 | `meta-llama-3-1-8b-instruct` | 131K | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| **Cerebras** | 8 | `llama3.1-70b` | 131K | [cloud.cerebras.ai](https://cloud.cerebras.ai/) |
| **LLM7.io** | 16 | `deepseek-v3` | 131K | [token.llm7.io](https://token.llm7.io) |
| **DeepSeek** | 2 | `deepseek-chat-v3-2` | 128K | [platform.deepseek.com](https://platform.deepseek.com/api_keys) |
| **xAI** | 3 | `grok-4.3` | 1M | [console.x.ai](https://console.x.ai) |
| **AI21 Labs** | 2 | `jamba-large-1-7` | 256K | [studio.ai21.com](https://studio.ai21.com/account/api-key) |

## Proveedores con verificación (teléfono/registro) pero sin tarjeta

| Proveedor | Modelos | Mejor Modelo | Contexto | Verificación |
|-----------|---------|-------------|----------|-------------|
| **NVIDIA NIM** | 125 🏆 | `z-ai/glm-5.2` | **1M** | Teléfono |
| **Ollama Cloud** | 13 | `minimax-m3` | 1M | Registro |
| **ModelScope** | 56 | `MiniMax-M2.5` | 204K | Registro |
| **OVHcloud AI Endpoints** | 14 | `qwen3.5-397b-a17b` | 131K | Registro |
| **SambaNova** | 4 | `deepseek-v3-2-preview` | 128K | Registro |
| **SiliconFlow** | 3 | `deepseek-r1-distill-qwen-7b` | 131K | Registro |
| **Z AI (Zhipu AI)** | 4 | `glm-4.7` | 200K | Registro |

## ⚠️ REALIDAD vs CATÁLOGO — Modelos verificados en OpenRouter

El catálogo de freellm.net lista 444+ modelos gratis, pero **NO todos funcionan en OpenRouter**.
Testeamos 20+ modelos (2026-08-21) — estos son los que realmente jalan:

### ✅ Modelos GRATIS que SÍ funcionan en OpenRouter

| Modelo | Contexto | Rate Limit | Bueno para |
|--------|----------|-----------|------------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | **1M** | 200 req/día | Razonamiento pesado, coding |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262K | 200 req/día | Coding, análisis |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256K | 200 req/día | Tareas rápidas, chat |
| `nvidia/nemotron-3.5-lightning:free` | — | 200 req/día | Rápido, respuestas creativas |
| `poolside/laguna-s-2.1:free` | 262K | 200 req/día | Escritura, creatividad |
| `openrouter/free` | — | — | Auto-routing al mejor free disponible |
| `deepseek-v4-flash` | 1M | — | Razonamiento (modelo de razonamiento, content=null) |
| `deepseek/deepseek-v4-pro` | 1M | — | Razonamiento (modelo de razonamiento, content=null) |

> ℹ️ **deepseek-v4-flash y deepseek-v4-pro**: Son modelos de razonamiento — devuelven `content: None` con `reasoning` lleno. En Hermes funcionan porque el cliente maneja esto, pero en tests directos con curl/Python aparecen como "fallidos".

### ❌ Modelos que NO funcionan (deprecados / requieren créditos / wrong endpoint)

| Modelo | Problema |
|--------|---------|
| `tencent/hy3-free` | 400 Bad Request (deprecado definitivamente) |
| `cohere/command-a-218b:free` | 400 Bad Request |
| `cohere/command-a-111b:free` | 400 Bad Request |
| `cohere/north-mini-code:free` | content=None (no responde) |
| `google/gemini-3.6-flash:free` | 404 Not Found |
| `google/gemini-3.5-flash:free` | 404 Not Found |
| `z-ai/glm-5.2:free` | 429 Too Many Requests (rate limit) |
| `poolside/laguna-m.1:free` | 404 Not Found |
| `poolside/laguna-xs-2.1:free` | content=None |
| `openai/gpt-oss-20b:free` | content=None |
| `mistralai/mistral-medium-3-5-128b:free` | 400 Bad Request |
| `qwen/qwen-3-235b-a22b:free` | 400 Bad Request |

> ⚠️ Los modelos free de OpenRouter cambian constantemente. La lista actualizada de free models se obtiene así:
> ```bash
> curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models | python -c "
> import json, sys
> data = json.load(sys.stdin)
> for m in data['data']:
>     p = m.get('pricing', {})
>     if float(p.get('prompt', 1)) == 0 and float(p.get('completion', 1)) == 0:
>         print(m['id'])
> "
> ```

## OpenRouter (créditos renovables)

| Modelo | Contexto | Notas |
|--------|----------|-------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | **1M** | ✅ Verificado |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262K | ✅ Verificado |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256K | ✅ Verificado |
| `nvidia/nemotron-3.5-lightning:free` | — | ✅ Verificado |
| `poolside/laguna-s-2.1:free` | 262K | ✅ Verificado |

> ⚠️ OpenRouter requiere $10 top-up una vez para desbloquear free tier, luego los modelos gratis no cuestan.
> La mayoría de modelos free listados en catálogos externos NO funcionan en OpenRouter.
> Ver `references/hermes-configs.md` para la lista completa verificada.

## Configuración en Hermes

### Como provider primario (reemplaza tu modelo default)

```yaml
model:
  default: gemini-3.6-flash
  provider: custom
  base_url: https://generativelanguage.googleapis.com/v1beta
  max_tokens: 65536
```

Guarda la API key en `.env`:
```bash
echo 'GEMINI_API_KEY=AIza...' >> "$APPDATA/hermes/.env"
```

### Como fallback (cuando el primario rate-limitea)

```yaml
fallback_providers:
  - provider: custom
    model: gemini-3.6-flash
    base_url: https://generativelanguage.googleapis.com/v1beta
    api_key: AIza...
    api_mode: openai
  - provider: custom
    model: moonshotai/kimi-k2-instruct
    base_url: https://api.groq.com/openai/v1
    api_key: gsk_...
    api_mode: openai
  - provider: custom
    model: command-a-218b
    base_url: https://api.cohere.com/v2
    api_key: ...
    api_mode: openai
```

> ⚠️ `hermes config set` NO puede escribir listas/arrays. Usa el script `references/write-fallbacks.py` o edita `config.yaml` directamente con Python según el patrón en `hermes-model-config` skill.

## Test rápido de un endpoint gratis

```bash
python scripts/test-free-endpoint.py --provider groq --api-key gsk_xxx --model moonshotai/kimi-k2-instruct
```

## Estrategia de router recomendada (basada en verificación real)

Cuando solo tienes key de **OpenRouter** (sin Groq, Gemini, NVIDIA, etc.):

1. **Primario**: `deepseek-v4-flash` (1M ctx, razonamiento)
2. **Fallback 1**: `nvidia/nemotron-3-ultra-550b-a55b:free` (1M ctx, 200 req/día)
3. **Fallback 2**: `nvidia/nemotron-3-super-120b-a12b:free` (262K ctx)
4. **Fallback 3**: `nvidia/nemotron-3-nano-30b-a3b:free` (256K ctx)
5. **Local ultimate**: Ollama ablit/Ornith (si todo lo demás falla)

Si registras más providers sin CC:
- **Groq** (Kimi K2, 30 RPM, sin CC) — mejor primario alternativo
- **Gemini 3.6 Flash** (1M ctx, 15 RPM, sin CC) — mejor multimodal gratuito
- **NVIDIA NIM** (GLM-5.2, 1M ctx, 40 RPM, verif teléfono) — 125 modelos

## Configuración de perfiles con fallbacks en cadena

Para configurar MÚLTIPLES perfiles de Hermes con modelos distintos y la misma cadena de fallbacks, usa este patrón (verificado 2026-08-21):

```python
import yaml, shutil, os, time

LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")
env_path = os.path.join(LOCALAPPDATA, "hermes", ".env")
with open(env_path) as f:
    openrouter_key = [l.strip().split("=",1)[1] for l in f if l.startswith("OPENROUTER_API_KEY=")][0]

# Cadena de fallbacks común
fallback_chain = [
    {"provider": "custom", "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
     "base_url": "https://openrouter.ai/api/v1", "api_key": openrouter_key, "api_mode": "openai"},
    {"provider": "custom", "model": "nvidia/nemotron-3-super-120b-a12b:free",
     "base_url": "https://openrouter.ai/api/v1", "api_key": openrouter_key, "api_mode": "openai"},
    {"provider": "custom", "model": "nvidia/nemotron-3-nano-30b-a3b:free",
     "base_url": "https://openrouter.ai/api/v1", "api_key": openrouter_key, "api_mode": "openai"},
]

# Config por perfil
profiles = {
    "builder":       "nvidia/nemotron-3-super-120b-a12b:free",
    "orchestrator":  "deepseek/deepseek-v4-pro",
    "researcher":    "deepseek/deepseek-v4-pro",
    "reviewer":      "deepseek/deepseek-v4-pro",
    "writer":        "poolside/laguna-s-2.1:free",  # hy3-free está muerto
}

for name, model in profiles.items():
    path = os.path.join(LOCALAPPDATA, "hermes", "profiles", name, "config.yaml")
    bak = path + f".bak.{int(time.time())}"
    shutil.copy2(path, bak)
    
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    
    d.setdefault("model", {})["default"] = model
    d["model"]["provider"] = "openrouter"
    d["model"]["base_url"] = "https://openrouter.ai/api/v1"
    d["model"]["api_key"] = openrouter_key
    d["fallback_providers"] = fallback_chain
    
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(d, f, sort_keys=False, default_flow_style=False)
    
    print(f"✅ {name}: {model} + 3 fallbacks")
```

> ⚠️ `hermes config set` NO puede escribir listas/arrays (fallback_providers). Usa el script `scripts/write-fallbacks.py` o el patrón Python de arriba.

## Verificación

```bash
# Probar un endpoint específico
python scripts/test-free-endpoint.py --base-url https://api.groq.com/openai/v1 --api-key gsk_xxx --model moonshotai/kimi-k2-instruct

# Verificar que Hermes puede usarlo como fallback
python scripts/test-free-endpoint.py --hermes-test --provider groq
```

## Referencias

- 🌐 **Live site**: [freellm.net](https://freellm.net) — buscador, comparador, playground
- 📂 **Repo**: [github.com/open-free-llm-api/awesome-freellm-apis](https://github.com/open-free-llm-api/awesome-freellm-apis)
- 🔑 **Directorio API keys**: [freellm.net/free-llm-api-keys/](https://freellm.net/free-llm-api-keys/)
- ⚙️ **Config generator**: [freellm.net/config/](https://freellm.net/config/)

## Mantenimiento

Los datos se actualizan diario desde freellm.net vía monitoreo automatizado. Si un proveedor deja de ser gratis o cambia su base URL, actualiza la referencia en `references/providers-reference.md`.