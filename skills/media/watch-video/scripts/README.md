# scripts /

Bundled Python modules for the watch-video skill. Pure stdlib where
possible — only the runtime dependencies are `yt-dlp` and `ffmpeg` /
`ffprobe` (installed by `setup.py`).

| File | Purpose |
|------|---------|
| `watch.py` | Entry point — orchestrates download → frames → transcript. |
| `download.py` | `yt-dlp` wrapper for URLs and local file resolution. |
| `frames.py` | `ffmpeg` frame extraction with auto-scaled fps. |
| `transcribe.py` | WebVTT parser with YouTube auto-sub dedupe. |
| `whisper.py` | Groq / OpenAI Whisper clients (pure stdlib). |
| `setup.py` | Preflight + installer (apt/pip on Linux). |

Run `python3 setup.py --check` before each invocation (silent on
success) and `python3 setup.py` once to install missing dependencies
and scaffold `~/.config/watch/.env`.
