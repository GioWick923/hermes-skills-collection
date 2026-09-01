---
name: openai-compatible-api-testing
description: Test OpenAI-compatible API gateways (custom base_url, key).
---

# OpenAI-Compatible API Gateway Testing

How to verify that an OpenAI-compatible endpoint (custom `base_url` + `api_key`) actually works, and which model IDs are usable on a given key. Applies to TokenRouter, OpenRouter, InferX, NVIDIA NIM, and any provider exposing the OpenAI `/v1` shape.

## When to use
- User pastes an OpenAI SDK snippet with a custom `base_url` and wants it run/tested.
- Need to know whether a specific model ID is available on a key/account.
- Debugging 401/403/429 errors from an OpenAI-compatible gateway.

## Workflow
1. **Probe reachability without a key**: `curl -sS -m 20 https://HOST/v1/models -w 'HTTP %{http_code}\n'`. `401` = endpoint alive, auth required. Timeout/DNS failure = endpoint problem.
2. **Check the per-token model catalog WITH the key**: `curl -sS https://HOST/v1/models -H "Authorization: Bearer $KEY" -o /tmp/models.json`, then parse `data[].id`.
   - CRITICAL: catalogs are **per-token/plan**, not global. A model ID listed on the provider's site may 403 on a specific key.
   - Confirm `target_model in catalog_ids` BEFORE running inference.
3. **Run the user's real snippet** (don't just curl): write their exact code to a temp file, run with the local Python + `openai` SDK. Keep streaming + `stream_options={"include_usage": True}` if present. Capture the completion or the exact error JSON.
4. **Classify errors** — common taxonomy:
   - `401 Token not provided` → missing/malformed key.
   - `403 This token has no access to model X` → model not in this key's plan; check `/v1/models`.
   - `403 credit limit is insufficient / remaining credit: $0` → account has no balance; even available models fail.
   - `429` → rate limit / quota; retry or switch provider.
5. **Report a table**: each model tested → OK/error message; catalog contents; credit status when surfaced. Never claim success without a real streamed completion.
6. **Clean up secrets**: delete temp files containing keys; never persist keys in memory (SOUL §21.2).

## Pitfalls
- **Per-token catalogs vary**: two keys on the same provider can expose different model sets (observed: key A → `xiaomi/mimo-v2-flash`, key B → `qwen/qwen3.8-max-free`). Never generalize from one key.
- **Model name ≠ availability**: a `:free`-suffixed model may still be absent from the account's catalog.
- **Windows/MSYS path trap**: native `python.exe` cannot open MSYS `/tmp/x.py` (MSYS path conversion is disabled for native tools). Write test scripts via write_file to `$LOCALAPPDATA/Temp` (e.g. `C:/Users/<user>/AppData/Local/Temp/x.py`) and invoke with the native forward-slash path. Heredoc + `python /tmp/x.py` fails with `can't open file 'C:\\tmp\\x.py'`.
- **Empty 401 body**: some gateways return 401 with a near-empty body; use `curl -D -` to see headers/body before concluding the host is down.
- **Don't fabricate a pass**: if credit or access blocks inference, report the exact 403 message and offer alternatives (different key, recharge, another provider) — never invent a completion.

## Verification
- ✅ Endpoint returns HTTP 200 with key.
- ✅ Catalog queried; target model confirmed present OR absent (report which).
- ✅ At least one model actually streams a completion end-to-end.
- ✅ Temp files with keys deleted.

## References
- `references/tokenrouter.md` — TokenRouter-specific quirks, observed catalogs, and error taxonomy.
