# Example: OpenRouter Fallback Configuration

Add the following to your `providers:` section:

```yaml
providers:
  openrouter:
    name: openrouter
    base_url: https://openrouter.ai/api/v1
    api_key: ${OPENROUTER_API_KEY}
    api_mode: openai
    default_model: tencent/hunyuan:free
```

Then ensure `fallback_providers:` includes OpenRouter as the first fallback:

```yaml
fallback_providers:
  - provider: openrouter
    model: tencent/hunyuan:free
    base_url: https://openrouter.ai/api/v1
    api_key: ${OPENROUTER_API_KEY}
    api_mode: openai
  - provider: ollama_cloud   # your existing fallbacks follow
    model: gpt-oss:120b
    # ... etc
```

Adjust timeouts for fast fallback:

```yaml
terminal:
  timeout: 15   # seconds
agent:
  api_max_retries: 2
```