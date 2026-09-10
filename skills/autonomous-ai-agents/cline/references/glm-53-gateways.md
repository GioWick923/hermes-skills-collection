# GLM-5.3 availability across Gio's gateways (verified 2026-08-31)

Discovered while checking whether Cline CLI could use our GLM models.
Source: `$LOCALAPPDATA/hermes/scripts/models_query.py find glm` (live catalog query).

## glm-5.3 exact model names per gateway

| Gateway     | Model names available                          |
|-------------|------------------------------------------------|
| aihubmix    | `glm-5.3`, `glm-5.3-flash`, `coding-glm-5.3`, `coding-glm-5.3-free` |
| bai         | `glm-5.3`, `glm-5.3-flash`                    |
| openrouter  | `z-ai/glm-5.3`, `z-ai/glm-5.3-flash`, `z-ai/glm-5.3-flash:batch` |

Also present (older): glm-5.2 family, glm-5.1, glm-5, glm-5-turbo, glm-5v-turbo,
glm-4.7 family. aihubmix has coding-* variants (coding-glm-5.3, coding-glm-5.3-free).

## Querying the live catalog (do this, don't hardcode)

```bash
python "$LOCALAPPDATA/hermes/scripts/models_query.py" find glm     # all glm models
python "$LOCALAPPDATA/hermes/scripts/models_query.py" list         # per-gateway counts
```

`list` output: aihubmix 409, bai 44, openrouter 425, ollama-local 4 (orcarouter &
empero returned HTTPError on this run — transient/upstream).

## Using with Cline (or any OpenAI-compatible CLI)

OpenAI-compatible gates accept `-P <provider> -m <model> -k <key>`. Region
consistency matters (base URL + key + model from same gateway). Verify with a
real smoke prompt before relying on any combo.

**Verified gotcha (2026-08-31):** `cline auth -p openai-native -k <key> -m <model>
-b https://aihubmix.com/v1` succeeds (exit 0, "Provider configured"), but the
first real run fails with `Received a Chat Completions stream while using the
OpenAI Responses API` — because Cline's `openai-native` provider defaults to the
OpenAI **Responses** API while aihubmix/bai expose **Chat Completions**. To target
a Chat-Completions-compatible gate, use a Chat-Completions transport/provider
(e.g. `openai.chat('model')` or an openai-compatible provider), NOT `openai-native`'s
default Responses path. Also note `-free` models are quota-capped (aihubmix
coding-glm-5.3-free hit its 10-call unrecharged limit).

## Note on SenseNova (SenseTime)

Discovered same session: SenseNova (sensenova.ai) is a free-public-beta multimodal
API (SenseNova 6.8 Flash Lite, U1 Fast) with base URL `https://token.sensenova.ai/v1`
(international), ~1500 calls/5h per model, and direct Hermes Agent + OpenClaw
integration. Not yet wired into our gates — candidate free provider for
office/creation tasks (PPT, Excel, infographics). Repo: `OpenSenseNova/SenseNova-Skills` (MIT).
