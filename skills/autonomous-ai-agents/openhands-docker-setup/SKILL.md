---
name: openhands-docker-setup
description: Deploy and debug OpenHands (all-hands-ai) in Docker on Windows/MSYS. Covers the runtime-version-mismatch debugging chain (micromamba, conda env, network), runtime-image patching via Dockerfile overlay, LLM model selection for tool-calling agents (reasoning models like hy3 break OpenHands), and the OpenRouter free-tier daily-limit gotcha. Use when the user asks to set up, deploy, debug, or run OpenHands locally via Docker.
---

# OpenHands Docker Setup & Debugging

## When to use
- User asks to install/run/debug OpenHands locally via Docker
- OpenHands runtime containers fail to start (Exited, Created, no agents acting)
- LLM connected to OpenHands doesn't produce actions (agent stuck in `loading`)
- User wants to connect OpenHands to free/cheap LLM providers (OpenRouter, Ollama)

## Architecture (3 layers)
1. **Server** (`openhands:latest`) — the web UI + agent orchestrator at `localhost:3000`
2. **Runtime** (`runtime:latest`) — sandboxed container where the agent executes commands/code
3. **LLM** — external API (OpenRouter, Ollama, Anthropic, etc.) that powers the agent's decisions

## Step-by-step deployment

### 1. Pull and run the server
```bash
docker pull ghcr.io/all-hands-ai/openhands:latest
docker pull ghcr.io/all-hands-ai/runtime:latest

docker run -d --name openhands \
  -p 3000:3000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands:/root/.openhands \
  ghcr.io/all-hands-ai/openhands:latest
```

### 2. Verify the server is up
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/  # expect 200
```

### 3. Configure the LLM via REST API
```python
import urllib.request, json, os

BASE = "http://localhost:3000"
ENV = os.path.expandvars(r"%LOCALAPPDATA%/hermes/.env")
key = ""
with open(ENV, encoding="utf-8", errors="ignore") as f:
    for line in f:
        if line.strip().startswith("OPENROUTER_API_KEY"):
            key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
            break

# POST /api/settings
payload = json.dumps({
    "llm_model": "openrouter/deepseek/deepseek-chat",
    "llm_api_key": key,
    "llm_base_url": "https://openrouter.ai/api/v1",
    "agent": "CodeActAgent",
}).encode()
req = urllib.request.Request(f"{BASE}/api/settings", data=payload, method="POST")
req.add_header("Content-Type", "application/json")
urllib.request.urlopen(req)
```

### 4. Send a task to the agent
```python
# Create conversation
st, body = req("POST", "/api/conversations", {})
cid = json.loads(body)["conversation_id"]

# Send message
req("POST", f"/api/conversations/{cid}/message",
    {"message": "Create /workspace/hello.py with print('Hello!') and run it."})

# Poll for completion
import time
for i in range(12):
    time.sleep(10)
    st, body = req("GET", f"/api/conversations/{cid}/events")
    evs = json.loads(body).get("events", [])
    state = None
    for e in evs:
        if e.get("observation") == "agent_state_changed":
            state = (e.get("extras") or {}).get("agent_state")
    if state in ("idle", "finished", "awaiting_user_input"):
        break
```

## Debugging chain: runtime won't start

This is the most common failure mode. OpenHands server version and runtime image version can drift, causing cascading errors. Follow this exact diagnostic order:

### Step 1: Check server logs for the runtime error
```bash
docker logs openhands 2>&1 | tail -30 | grep -iE "error|runtime|fail|sandbox|exception"
```

### Step 2: Check for dead runtime containers
```bash
docker ps -a -f "name=openhands-runtime" --format "{{.Names}} {{.Status}}"
```

### Step 3: Read the dead runtime's own logs
```bash
LATEST=$(docker ps -a -f "name=openhands-runtime" --format "{{.Names}}" | head -1)
docker logs "$LATEST" 2>&1 | tail -20
```

### Step 4: Inspect the runtime image for missing binaries/envs
```bash
docker run --rm --entrypoint sh ghcr.io/all-hands-ai/runtime:latest -c \
  "ls /openhands/micromamba/bin/ 2>&1; ls /openhands/miniforge3/envs/ 2>&1; /openhands/miniforge3/bin/conda env list 2>&1"
```

### Step 5: Patch the runtime image (Dockerfile overlay)
If the server expects a binary/env that the runtime image doesn't have, create a patched image:

```dockerfile
FROM ghcr.io/all-hands-ai/runtime:latest
# Symlink micromamba -> mamba if server expects micromamba path
RUN mkdir -p /openhands/micromamba/bin && \
    ln -sf /openhands/miniforge3/bin/mamba /openhands/micromamba/bin/micromamba
# Create expected conda env if missing
RUN /openhands/miniforge3/bin/conda create -n openhands python=3.11 -y
```

Build with `--force-rm` to avoid stale-layer conflicts:
```bash
docker build --no-cache -t ghcr.io/all-hands-ai/runtime:latest \
  -f /tmp/runtime-patch.Dockerfile /tmp
```

### Step 6: Clean dead runtimes and retry
```bash
docker rm -f $(docker ps -a -q -f "name=openhands-runtime") 2>&1
# Then send a new message to create a fresh conversation
```

## Pitfalls

### Pitfall 1: Reasoning models break OpenHands tool-calling
Models like `tencent/hy3:free` (and other reasoning models) put their output in a `reasoning` field and return `content=null` when `max_tokens` is low. OpenHands needs `content` with the action JSON. **Use instruct/chat models, not reasoning models, for the OpenHands agent.**

### Pitfall 2: OpenRouter free-tier daily limit
All `:free` models on OpenRouter share a daily request quota. Once exhausted, ALL free models return 429 with the message `"Rate limit exceeded: free-models-per-day. Add 5 credits to..."`. This is NOT a transient rate-limit — it's a daily cap that resets every 24h. Adding $5 credits lifts the limit. Workaround: use a cheap paid model (e.g., `deepseek/deepseek-chat` at ~$0.27/M tokens) or use a local model via Ollama.

### Pitfall 3: `ln -s` fails on rebuild ("File exists")
When patching the runtime image over the same tag, `ln -s` fails if the symlink already exists from a previous build layer. Use `ln -sf` (force) to overwrite cleanly.

### Pitfall 4: MSYS path mangling with docker exec grep
On Windows/MSYS, `docker exec openhands grep -r "pattern" /openhands/poetry/` can have its path mangled to a Windows path. Always use `docker exec <container> sh -c '...'` to keep paths inside the container.

### Pitfall 5: Agent stuck in `loading` forever
If the agent stays in `loading` state indefinitely with only 2 events (agent_state_changed + user message), the runtime container is dying on startup. Check server logs (`docker logs openhands`) — NOT just the events endpoint. The events endpoint won't show runtime init failures.

## LLM model recommendations for OpenHands

| Model | Cost | Why | Caveat |
|-------|------|-----|--------|
| `deepseek/deepseek-chat` | ~$0.27/M tok | Cheap, strong at code, stable | Paid (avoids free-tier limit) |
| `openai/gpt-oss-120b:free` | Free | Strong at code, 120B params | Rate-limited, may 429 |
| `meta-llama/llama-3.3-70b-instruct:free` | Free | Good generalist | Rate-limited |
| Ollama local (gpt-oss:120b) | Free, local | No rate limits, private | Needs GPU/RAM, on-demand startup |
| `tencent/hy3:free` | Free | ⚠️ DON'T use | Reasoning model, `content=null` breaks tool-calling |

## Verification checklist
- [ ] `docker ps` shows openhands as `Up`
- [ ] `curl localhost:3000` returns 200
- [ ] `POST /api/settings` returns 200 `{"message":"Settings stored"}`
- [ ] `POST /api/conversations` returns a conversation_id
- [ ] `POST /api/conversations/<cid>/message` returns `{"success":true}`
- [ ] After polling events, agent reaches `idle`/`finished` state (not stuck in `loading`)
- [ ] At least 1 event with `source=agent` containing action text

## References
- `references/runtime-debugging-chain.md` — Full error transcript and patch recipes for the micromamba/conda-env mismatch chain
