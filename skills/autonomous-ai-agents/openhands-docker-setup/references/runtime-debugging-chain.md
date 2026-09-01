# OpenHands Runtime Debugging Chain — Session Transcript

Real errors and fixes encountered deploying OpenHands v0.59.0 on Windows/MSYS with Docker.

## Environment
- Host: Windows 10, MSYS/git-bash
- Docker Desktop
- OpenHands: `ghcr.io/all-hands-ai/openhands:latest` (v0.59.0)
- Runtime: `ghcr.io/all-hands-ai/runtime:latest` (7.24GB)
- LLM: OpenRouter

## The Error Chain (3 cascading failures)

### Error 1: micromamba not found
```
docker.errors.APIError: 400 Client Error for http+docker://localhost/v1.55/containers/.../start:
Bad Request ("failed to create task for container: failed to create shim task: OCI runtime
create failed: runc create failed: unable to start container process: error during container
init: exec: \"/openhands/micromamba/bin/micromamba\": stat /openhands/micromamba/bin/micromamba:
no such file or directory")
```

**Root cause**: Server v0.59.0 executes the runtime with entrypoint `/openhands/micromamba/bin/micromamba`, but the runtime image has `mamba` at `/openhands/miniforge3/bin/mamba` (v1.5.8) and `conda` at `/openhands/miniforge3/bin/conda` (v24.7.1). No `micromamba` binary exists.

**Fix**: Dockerfile overlay with symlink:
```dockerfile
FROM ghcr.io/all-hands-ai/runtime:latest
RUN mkdir -p /openhands/micromamba/bin && \
    ln -sf /openhands/miniforge3/bin/mamba /openhands/micromamba/bin/micromamba
```

### Error 2: conda env `openhands` not found
After fixing micromamba, runtime starts but exits immediately:
```
EnvironmentLocationNotFound: Not a conda environment: /openhands/miniforge3/envs/openhands
```

**Root cause**: The runtime image only has the `base` conda env. Server expects an `openhands` env at `/openhands/miniforge3/envs/openhands`.

**Fix**: Add to the Dockerfile overlay:
```dockerfile
RUN /openhands/miniforge3/bin/conda create -n openhands python=3.11 -y
```

### Error 3: Network unreachable (runtime dies before listening)
```
httpx.ConnectError: [Errno 101] Network is unreachable
Runtime initialization failed: Container openhands-runtime-<id> has exited.
```

**Root cause**: This is a symptom, not a cause. The server tries to connect to the runtime's action server, but the runtime already died from error 1 or 2 above. Fix the underlying runtime exit cause first.

## Combined patch Dockerfile
```dockerfile
FROM ghcr.io/all-hands-ai/runtime:latest
# Fix 1: symlink micromamba -> mamba (use -sf to not fail on rebuild)
RUN mkdir -p /openhands/micromamba/bin && \
    ln -sf /openhands/miniforge3/bin/mamba /openhands/micromamba/bin/micromamba
# Fix 2: create expected conda env
RUN /openhands/miniforge3/bin/conda create -n openhands python=3.11 -y
```

Build and force-replace:
```bash
docker build --no-cache -t ghcr.io/all-hands-ai/runtime:latest \
  -f /tmp/runtime-patch.Dockerfile /tmp
docker rm -f $(docker ps -a -q -f "name=openhands-runtime") 2>/dev/null
```

## Diagnostic commands (exact order)

```bash
# 1. Is server alive?
docker ps --filter "name=openhands" --format "{{.Names}} {{.Status}}"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/

# 2. Server logs — what error killed the runtime?
docker logs openhands 2>&1 | tail -30 | grep -iE "error|runtime|fail|sandbox|exception"

# 3. Dead runtime containers?
docker ps -a -f "name=openhands-runtime" --format "{{.Names}} {{.Status}}"

# 4. Runtime's own logs — why did it exit?
LATEST=$(docker ps -a -f "name=openhands-runtime" --format "{{.Names}}" | head -1)
docker logs "$LATEST" 2>&1 | tail -20

# 5. Inspect runtime image internals
docker run --rm --entrypoint sh ghcr.io/all-hands-ai/runtime:latest -c \
  "ls /openhands/micromamba/bin/ 2>&1; \
   ls /openhands/miniforge3/envs/ 2>&1; \
   /openhands/miniforge3/bin/conda env list 2>&1"

# 6. Check what entrypoint the server uses for runtime
docker inspect ghcr.io/all-hands-ai/runtime:latest --format '{{json .Config.Cmd}} {{json .Config.Entrypoint}}'
```

## LLM selection findings

### OpenRouter free models tested (July 2026)
24 free models available. ALL returned 429 after daily quota exhausted:
```
openai/gpt-oss-120b:free -> 429
meta-llama/llama-3.3-70b-instruct:free -> 429
qwen/qwen3-coder:free -> 429
nvidia/nemotron-nano-9b-v2:free -> 429
google/gemma-4-31b-it:free -> 429
```
Error message: `"Rate limit exceeded: free-models-per-day. Add 5 credits to..."`

### Reasoning model failure (hy3:free)
`tencent/hy3:free` returns `content=null` when `max_tokens` is low because the output goes to a `reasoning` field. OpenHands' CodeActAgent parses `content` for action JSON → gets null → agent never acts. This is NOT an OpenHands bug — it's a model architecture mismatch. Use instruct/chat models for any tool-calling agent.

### Recommended working model
`openrouter/deepseek/deepseek-chat` — paid but extremely cheap (~$0.27/M tokens), strong at code, stable, no daily quota issue.
