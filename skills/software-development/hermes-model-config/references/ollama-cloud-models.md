# Ollama Cloud — model-access probe & role-based model policy

## 1. Live-test a model before trusting it
Ollama Cloud gates models by subscription. A model can appear in `/v1/models` yet
be rejected at call time with `requires a subscription`. Probe every candidate:

```python
import urllib.request, json
KEY = "<your OLLAMA_API_KEY>"   # from Hermes .env, never paste in chat
def test(mdl, prompt="say hi", max_tokens=8, timeout=40):
    body = json.dumps({"model":mdl,"messages":[{"role":"user","content":prompt}],"max_tokens":max_tokens}).encode()
    req = urllib.request.Request("https://ollama.com/v1/chat/completions", data=body,
        headers={"Content-Type":"application/json","Authorization":f"Bearer {KEY}"}, method="POST")
    try:
        out = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
        return "OK", out["choices"][0]["message"]["content"].strip()[:60]
    except urllib.error.HTTPError as e:
        return "FAIL", e.read().decode()[:80]
```

Observed (account-dependent — verify YOUR account, don't assume): `glm-5.2`,
`glm-5.1`, `glm-5` were REJECTED as "requires a subscription" despite being
listed; `gpt-oss:120b`, `devstral-2:123b`, `qwen3-coder:480b`, `glm-4.7`
answered OK. `gpt-oss:120b` returned EMPTY on a 1-word prompt but answered a
real sentence prompt in ~1.6s. `qwen3-coder:480b` took ~33s (too slow for
quick use). **`devstral-2:123b` (~1.3s) is the best "quick deep" candidate.**

## 2. Role-based model policy (organize multiple models)
Define roles so you never burn the expensive model on trivial traffic:

| Role | When | Example |
|------|-------|----------|
| Principal (day-to-day) | ~80% of traffic, free | OpenRouter `hy3:free` |
| Deep / heavy (on-demand) | reasoning, big context, 2nd opinion | Ollama Cloud `devstral-2:123b` |
| Code (scoped) | dev ONLY — features, refactors, PRs | ChatGPT Codex |
| Offline (last resort) | no internet | local `hermes3:8b` |

Wire Deep as `fallback_providers[0]` (right after the principal) and Offline as
the last entry. Expose Deep via a `~/bin/hermes-deep` wrapper:
`exec hermes "$@" --provider ollama_cloud --model devstral-2:123b`.
Keep Codex OUT of the auto-loop (manual / delegate-only) to protect its tokens.

## 3. Windows autostart note (Ollama)
Ollama's `Ollama.lnk` in the user **Startup** folder (`AppData\Roaming\Microsoft\
Windows\Start Menu\Programs\Startup`) already auto-launches the server on logon —
no Task Scheduler needed. `schtasks.exe /Create` needs admin and chokes on
spaces in the path (use 8.3 `<USER>~1` paths or PowerShell `Register-
ScheduledTask` only when elevated). Verify the server is up with
`curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/api/tags` → `200`.
