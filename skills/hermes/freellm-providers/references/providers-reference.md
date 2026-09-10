# Free LLM Providers — Referencia Completa

Fuente: [freellm.net](https://freellm.net) — datos actualizados al 2026-08-21
Repo: [awesome-free-llm-apis](https://github.com/open-free-llm-api/awesome-freellm-apis)

## Proveedores SIN Tarjeta de Crédito

| # | Proveedor | Base URL | Auth Header | Best Free Model |
|---|---|---|---|---|
| 1 | **Groq** | `https://api.groq.com/openai/v1` | `Authorization: Bearer gsk_...` | `moonshotai/kimi-k2-instruct` |
| 2 | **Google Gemini** | `https://generativelanguage.googleapis.com/v1beta` | `X-Goog-Api-Key: AIza...` | `gemini-3.6-flash` |
| 3 | **GitHub Models** | `https://models.github.ai/inference` | `Authorization: Bearer ghp_...` | `Phi-4` |
| 4 | **Cloudflare Workers AI** | `https://api.cloudflare.com/client/v4/accounts/{id}/ai/run` | `Authorization: Bearer ...` | `@cf/meta/llama-3.3-70b-instruct-fp8-fast` |
| 5 | **Mistral AI** | `https://api.mistral.ai/v1` | `Authorization: Bearer ...` | `mistral-medium-3-5-128b` |
| 6 | **Cohere** | `https://api.cohere.com/v2` | `Authorization: Bearer ...` | `command-a-218b` |
| 7 | **Hugging Face** | `https://router.huggingface.co/v1` | `Authorization: Bearer hf_...` | `meta-llama-3-1-8b-instruct` |
| 8 | **Cerebras** | `https://api.cerebras.ai/v1` | `Authorization: Bearer ...` | `llama3.1-70b` |
| 9 | **LLM7.io** | `https://api.llm7.io/v1` | `Authorization: Bearer ...` | `deepseek-v3` |
| 10 | **DeepSeek** | `https://api.deepseek.com/v1` | `Authorization: Bearer sk-...` | `deepseek-chat-v3-2` |
| 11 | **xAI** | `https://api.x.ai/v1` | `Authorization: Bearer ...` | `grok-4-3` |
| 12 | **AI21 Labs** | `https://studio.ai21.com/studio/v1` | `Authorization: Bearer ...` | `jamba-large-1-7` |
| 13 | **Z AI (Zhipu AI)** | `https://open.bigmodel.cn/api/paas/v4` | `Authorization: Bearer ...` | `glm-4.7` |
| 14 | **Kilo Code** | `https://api.kilo.ai/api/gateway` | `Authorization: Bearer ...` | `nvidia/nemotron-3-ultra-550b-a55b:free` |
| 15 | **OpenCode Zen** | `https://opencode.ai/zen/v1` | API Key header | `deepseek-v4-flash-free` |

## Proveedores con Verificación (Sin Tarjeta)

| # | Proveedor | Base URL | Verificación | Best Free Model |
|---|---|---|---|---|
| 16 | **NVIDIA NIM** | `https://integrate.api.nvidia.com/v1` | Teléfono | `z-ai/glm-5.2` |
| 17 | **Ollama Cloud** | `https://api.ollama.com` | Registro | `minimax-m3` |
| 18 | **ModelScope** | `https://api-inference.modelscope.cn/v1` | Registro | `MiniMax-M2.5` |
| 19 | **OVHcloud AI Endpoints** | `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1` | Registro | `qwen3.5-397b-a17b` |
| 20 | **SambaNova** | `https://api.sambanova.ai/v1` | Registro | `deepseek-v3-2-preview` |
| 21 | **SiliconFlow** | `https://api.siliconflow.cn/v1` | Registro | `deepseek-ai-deepseek-r1-distill-qwen-7b` |
| 22 | **Agnes AI** | `https://apihub.agnes-ai.com/v1` | Registro | `agnes-2.0-flash` |
| 23 | **Alibaba Cloud** | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | Registro | `qwen3-max` |
| 24 | **Chutes.ai** | `https://api.chutes.ai/v1` | Registro | `deepseek-ai/DeepSeek-R1` |
| 25 | **Glhf.chat** | `https://glhf.chat/api/openai/v1` | Registro | `meta-llama/Meta-Llama-3.1-70B-Instruct` |
| 26 | **Aion Labs** | `https://api.aionlabs.ai/v1` | Registro | `aion-2-5` |
| 27 | **Nscale** | `https://inference.api.nscale.com/v1` | Registro | `llama-3-3-70b-instruct` |
| 28 | **Nebius** | `https://api.studio.nebius.com/v1` | Registro | `qwen3-235b-a22b` |

## OpenRouter (Créditos Renovables)

| Modelo Free | Contexto | Base URL |
|---|---|---|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 1M | `https://openrouter.ai/api/v1` |
| `poolside/laguna-m.1:free` | 262K | `https://openrouter.ai/api/v1` |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262K | `https://openrouter.ai/api/v1` |
| `cohere/north-mini-code:free` | 256K | `https://openrouter.ai/api/v1` |
| `poolside/laguna-xs-2.1:free` | 262K | `https://openrouter.ai/api/v1` |
| `poolside/laguna-s-2.1:free` | 262K | `https://openrouter.ai/api/v1` |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256K | `https://openrouter.ai/api/v1` |

> ⚠️ OpenRouter: requiere $10 top-up one-time para activar free tier. Después los modelos free no consumen saldo.

## Top 10 Modelos Gratis por Uso Semanal

| Modelo | Proveedor | Contexto | Tokens/semana |
|---|---|---|---|
| `z-ai/glm-5.2` | NVIDIA NIM | 1M | **3.0 TRILLONES** |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | 1M | 2.3T |
| `poolside/laguna-m.1:free` | OpenRouter | 262K | 768B |
| `nvidia/nemotron-3-super-120b-a12b:free` | OpenRouter | 262K | 315B |
| `cohere/north-mini-code:free` | OpenRouter | 256K | 255B |
| `poolside/laguna-xs-2.1` | NVIDIA NIM | 262K | 171B |
| `z-ai/glm-5.1` | NVIDIA NIM | 202K | 158B |

## Mejores Modelos por Categoría

### 🧠 Razonamiento / Coding
- **DeepSeek-V4 Flash** (NVIDIA NIM / OpenCode Zen) — 1M ctx, gratis
- **Kimi K2** (Groq) — 131K ctx, sin CC
- **DeepSeek-V3.2** (SambaNova) — 128K ctx
- **DeepSeek-R1** (DeepSeek/Chutes.ai) — 128K ctx

### 🖼️ Visión / Multimodal
- **Gemini 3.6 Flash** (Google) — 1M ctx, sin CC, imagen+video+audio+pdf
- **MiniMax-M3** (NVIDIA NIM / Ollama Cloud) — 1M ctx, imagen+video
- **GLM-4.6V-Flash** (Zhipu AI) — 128K ctx
- **Qwen3-VL-Plus** (Alibaba Cloud) — 128K ctx

### 📄 Contexto ultra largo
- **Cloudflare Workers AI** — hasta 10M (modelos más pequeños)
- **Gemini 3.6 Flash** — 1M ctx, sin CC
- **z-ai/glm-5.2** — 1M ctx
- **Nemotron 3 Ultra** — 1M ctx
- **minimax-m3** — 1M ctx

### 🔊 Audio/Speech
- **Gemini 3.6 Flash** — entrada de audio
- **Google Gemini** — varios modelos con audio
- **Kilo Code** — modelos con audio

### 💰 Embeddings gratis
- **Cohere** — modelos embedding gratis
- **NVIDIA NIM** — modelos embedding gratis