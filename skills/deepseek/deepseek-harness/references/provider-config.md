# dsh provider configuration — verified layout

## Binary & home
- Installed binary: `$LOCALAPPDATA/hermes/node/dsh.cmd` (on PATH as `dsh`). Version with `dsh --version`.
- Harness home defaults to `~/.dsh` (env `DSH_HOME` overrides). Everything lives there:
  `settings.yaml` (user settings), `profiles/<name>/` (web, headless), `sessions/`, `credentials/`.
- Export `DSH_HOME="$HOME/.dsh"` before invoking dsh from MSYS bash.

## Profiles & defaults
- `dsh --profile headless "task"` runs one task and exits; `dsh --profile web` boots the UI on :3080.
- Each profile's default model is set by the `agent-default-model` entry. Override with a patch
  layer: a flat YAML array of `{id, config}` entries (see vendor/include PatchOptions: `id`,
  `config`, `insert`, `disabled` — there is NO nested `patch:` key).
- `dsh --profile <name> --patch C:/path/overlay.yml` applies a verified overlay. Pass NATIVE
  forward-slash paths (`C:/Users/...`), never MSYS `$HOME` paths — node reads them literally
  and fails with ENOENT.
- `--dump-config` composes bundle layers but does NOT reliably show the user patch layer; do
  not use it as proof an override applied. Prove by running: the error message changes when
  the default model actually changes.

## settings.yaml provider section (llm-pi-ai)
Top-level key `llm-pi-ai` → `providers:` dict. Profile schema requirements (enforced at
registration; an invalid section is refused with a warn and routes stay unregistered):
- `apiKeyEnv` (string, required), `displayName`, `api` ∈ {openai-completions, openai-responses,
  anthropic-messages}, `baseURL`, `models` list.
- Each model entry needs: `id`, `name`, `contextWindow`, `maxTokens`, and `input` (e.g.
  `[text]` or `[text, image]`). Omitting `input` on a model the installed catalog does not
  describe can fail the whole section.
- Do NOT set `provider` inside a provider profile (it moved to the dict key) or
  `maxRetries`/`maxRetryDelayMs` (removed; recovery goes through the llm-retry plugin).

Ollama example (verified against the runtime schema — resolves cleanly):

```yaml
llm-pi-ai:
  providers:
    ollama:
      displayName: Ollama Local
      apiKeyEnv: OLLAMA_API_KEY
      api: openai-completions
      baseURL: http://127.0.0.1:11434/v1
      models:
        - id: hf.co/mradermacher/Huihui-Qwen3-Coder-30B-A3B-Instruct-abliterated-i1-GGUF:IQ2_M
          name: Huihui Qwen3-Coder 30B-A3B abliterated (IQ2_M MoE)
          contextWindow: 32768
          maxTokens: 8192
          input: [text]
```

Set `agent-default-model: {provider: ollama, model: <model-id>}` at top level too, AND
export the key env (`export OLLAMA_API_KEY=ollama`) — credential resolution reads the env at
request time.

## Picking a local fallback model (12GB VRAM class)
User criteria for the local dsh fallback: uncensored/abliterated, agentic (tool-calling),
fast, fits VRAM. Ranked candidates verified on HF:
- `mradermacher/Huihui-Qwen3-Coder-30B-A3B-Instruct-abliterated-i1-GGUF` IQ2_M (10.2GB) —
  MoE 30B/3.3B-active: coder-quality + fast; fits 12GB VRAM whole. The community-standard
  GGUF (200K+ downloads); mradermacher `i1` = imatrix quants (best quality-per-bit).
- Same repo's IQ3_XXS (11.8GB) if IQ2_M underperforms — still (barely) VRAM-fit.
- Qwen3-Coder-30B-A3B quants ≥IQ4 need ~17-19GB → offload to RAM, not for the 12GB class.
- MoE rule: quant quality loss on MoE models is lower than on dense ones at the same size
  (only 3B params active per token) — IQ2/IQ3 MoE ≈ usable, IQ2 dense ≈ degraded.
Check the model card README for recommended sampling params (abliterated repos often
specify temperature/repeat_penalty).

## Verifying a provider actually works
1. `dsh --profile headless "Respond exactly with: DSH_SMOKE_OK"` — success means the string
   came back, exit 0.
2. Error taxonomy (escalating = progress): `MISSING_CREDENTIAL` = override did not apply (default
   model still on a keyless provider); `NO_ADAPTER: provider "X"` = override applied but pi-ai
   registered no routes (settings section invalid OR the settings-file→adapter runtime wiring did
   not deliver it); `AUTH: 401 <gateway error>` = the adapter registered correctly — only the
   key/gateway is wrong. Test the key independently with
   `curl <baseURL>/models -H "Authorization: Bearer $K"` before blaming dsh config.
3. Schema pre-check without booting: run node inside the dsh package dir, import `Config`
   from `@deepseek-ai/dsh-llm-pi-ai`, parse settings.yaml with `yaml`, call `Config(section)` —
   it prints resolved provider keys or the exact schema error. This isolates 'config bad'
   from 'runtime wiring bad'.
4. **If the schema resolves but runtime still says NO_ADAPTER**: bypass the settings-file
   delivery — patch the `llm-pi-ai` ENTRY config directly via `--patch` overlay (same providers
   dict under `id: llm-pi-ai`, `config: {providers: {...}}`). This registers the adapter at
   mount time and is the verified working path. Keep the settings.yaml section too so the web
   UI and hot-reload see it.
5. Credentials: export the key env AND/OR write `$DSH_HOME/.credentials.yaml`
   (`ORCAROUTER_API_KEY: sk-...`); resolution reads env at request time, the managed file feeds
   the Models page. If the gateway itself rejects the key on plain curl, no dsh config will fix
   it — the key is stale/rotated; get a new one from the provider.
6. Swap-in rule for local fallbacks: pull/verify the NEW model (list it via `ollama list`, run a
   real prompt) BEFORE deleting the current fallback. `ollama rm` of a model another config
   still references leaves dsh pointing at nothing — swap the default, smoke-test, then delete.

## Pitfalls
- Port 3080 occupied (EADDRINUSE at boot): a previous dsh web instance is still running —
  kill it (taskkill) before rebooting web; a stale instance also serves stale settings.
- Headless has NO `-c/--cwd` flag; `cd` to the target dir in the shell first.
- settings.yaml is hot-reloaded; a broken YAML at boot fails LOUD (crash) — that crash is the
  proof the file is being read, use it as a canary when debugging.
- Do not trust a dead server's log as evidence of life: llama.cpp logs persist after the
  process dies, and `model_manager.py` can point at a GGUF that no longer exists on disk.
  Verify liveness with `netstat` on the port plus a live `curl /v1/models` (or `:11434/api/tags`
  for Ollama) before declaring a local model usable as fallback.
