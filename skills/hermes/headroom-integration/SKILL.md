---
category: hermes
name: headroom-integration
description: "Use Headroom proxy to compress tool outputs and save tokens."
---

# Headroom ↔ Hermes Integration

Headroom (headroomlabs-ai/headroom) es un proxy compresor inteligente que se mete entre Hermes y el LLM, comprimiendo tool outputs, logs, JSON, código y texto antes de enviarlo al modelo. Ahorra 15-95% de tokens según el contenido.

## Setup

1. **Instalar Headroom:**
   ```bash
   pip install "headroom-ai[all]"
   ```

2. **Iniciar proxy:**
   ```bash
   headroom proxy --port 8787 --mode token --openai-api-url https://openrouter.ai/api/v1 --code-aware
   ```

3. **Perfil de Hermes para proxy:**
   Crear en `~/.hermes/profiles/headroom/config.yaml`:
   ```yaml
   model:
     default: deepseek/deepseek-v4-flash
     provider: custom
     base_url: http://127.0.0.1:8787/v1
   ```
   Usar: `OPENAI_API_KEY=$OPENROUTER_API_KEY hermes --profile headroom`

4. **Auto-start (cron cada 10 min):**
   ```bash
   hermes cron create "*/10 * * * *" "Check Headroom proxy health, restart if dead" --script check_headroom.sh --name headroom-proxy-monitor
   ```

## Modos de operación

| Modo | Flag | Cuándo usar |
|------|------|-------------|
| Token (máximo ahorro) | `--mode token` | Tareas con JSON pesado, logs, tool outputs grandes |
| Cache (máximo cache hit) | `--mode cache` | Sesiones largas con muchos turns repetitivos |
| Lossless | `--lossless` | Cuando NO quieres pérdida, solo compactación estructural |

## Compressors disponibles

- `smart_crusher` — JSON arrays (60-95% ahorro)
- `kompress` — ML-based text/prose compression (30-50%)
- `code_aware` — AST-based code compression (40-70%, requiere `--code-aware`)
- `log` — Build/test logs (80-95%)
- `search` — Search results (60-80%)

## Output Token Reduction

Headroom también puede reducir tokens de OUTPUT (lo que el modelo responde), recortando ceremonia, código repetido y reasoning innecesario. Habilitar vía `HEADROOM_OUTPUT_SHAPER=on`.

## Verificación

```bash
# Health check
curl http://127.0.0.1:8787/health

# Stats / savings
curl http://127.0.0.1:8787/stats | python -m json.tool

# Dashboard (browser)
headroom dashboard
```

## Pitfalls

- **OpenRouter + --backend openrouter** causa error litellm → usar `--openai-api-url` en su lugar
- **API key**: con `provider: custom`, setear `OPENAI_API_KEY=$OPENROUTER_API_KEY` en el entorno
- **Kompress** necesita descargar modelo (~500MB) en primer uso; es opcional, proxy funciona igual sin él
- **DeepSeek reasoning** puede devolver `content: null` en pruebas directas; en Hermes funciona normal