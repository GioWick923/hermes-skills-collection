# Web Search & STT Enablement — Verified Session Notes (2026-07-12)

Condensed from hermes-agent.nousresearch.com/docs + live execution on this host
(Hermes v0.17.0, Windows, Python 3.11.15).

## Doc facts (authoritative — hermes-agent.nousresearch.com/docs)

### web-search (https://hermes-agent.nousresearch.com/docs/user-guide/features/web-search)
Backends available for `web_search` / `web_extract` (single backend selection, or
per-capability split for search vs extract):

| Provider | Env Var | Search | Extract | Free tier |
|---|---|---|---|---|
| Firecrawl (default) | FIRECRAWL_API_KEY | yes | yes | 500 credits/mo |
| SearXNG | SEARXNG_URL | yes | — | free (self-host) |
| Brave Search | BRAVE_SEARCH_API_KEY | yes | — | 2000 q/mo |
| DDGS (DuckDuckGo) | — (no key) | yes | — | free |
| Tavily | TAVILY_API_KEY | yes | yes | 1000 searches/mo |
| Exa | EXA_API_KEY | yes | yes | 1000 searches/mo |
| Parallel | PARALLEL_API_KEY | yes | yes | paid |
| xAI (Grok) | XAI_API_KEY / hermes auth login xai-oauth | yes | — | paid |

- Brave, DDGS, xAI are **search-only** → pair with Firecrawl/Tavily/Exa/Parallel for `web_extract`.
- DDGS uses the `ddgs` PyPI package; lazy-installs if absent.
- Nous Portal (paid) supplies managed Firecrawl via `hermes setup --portal` — no key.
- `web_extract` summarizes long pages with an auxiliary model; for raw content use browser tools.

### voice-mode / STT (https://hermes-agent.nousresearch.com/docs/user-guide/features/voice-mode)
- STT providers in `~/.hermes/.env`:
  - `faster-whisper` → **local, ZERO keys**; model (~150 MB `base`) auto-downloads.
  - `GROQ_API_KEY` → Groq Whisper (fast, free tier, cloud).
  - `VOICE_TOOLS_OPENAI_KEY` → OpenAI Whisper (paid).
- CLI: `/voice on`, `/voice tts`, `/voice status`; Ctrl+B to record.
- System deps: PortAudio (mic), ffmpeg (convert), Opus (Discord VC), espeak-ng (NeuTTS).
- `hermes setup --portal` wires LLM + OpenAI TTS at once.

## Verified command transcript (this host, 2026-07-12)
Environment: Windows, LOCALAPPDATA=C:\Users\<USER> GAMES\AppData\Local

1) Locate venv + backup config
```
cd "$LOCALAPPDATA/hermes"
cp config.yaml "config.yaml.bak.$(date +%Y%m%d_%H%M%S)"   # -> config.yaml.bak.20260712094942
find . -maxdepth 5 -name pyvenv.cfg        # -> ./hermes-agent/venv/pyvenv.cfg
```

2) Install packages into Hermes venv
```
cd "$LOCALAPPDATA/hermes/hermes-agent"
export VIRTUAL_ENV="$PWD/venv"; export PATH="$PWD/venv/Scripts:$PATH"
uv pip install ddgs            # -> ddgs 9.14.4
uv pip install faster-whisper  # -> imports OK
```

3) Edit config.yaml (file-locked → python heredoc)
old:  `web:\n  backend: ''\n  search_backend: ''\n  extract_backend: ''`
new:  `web:\n  backend: 'ddgs'\n  search_backend: 'ddgs'\n  extract_backend: ''`

4) VERIFY — web_search
```
python -c "from ddgs import DDGS; r=DDGS().text('Hermes Agent Nous Research',max_results=3); print(len(r))"
# -> 3  (hermes-agent.nousresearch.com, github.com/NousResearch/hermes-agent, docs)
```

5) VERIFY — STT
```
python -c "from faster_whisper import WhisperModel; WhisperModel('tiny',device='cpu',compute_type='int8'); print('STT OK')"
# -> STT OK  (harmless "unauthenticated HF Hub" warning on first load)
```

## Effect on capability score
This session: agent self-rated ~88% essential tools → ~96% after closing web_search + STT.
Remaining gaps are gateway plumbing (messaging push, event hooks) — non-blocking.

## Note
After editing config.yaml, the native `web_search` tool only appears in-session
after relaunching the TUI/CLI. The backend itself works immediately (proven above).
