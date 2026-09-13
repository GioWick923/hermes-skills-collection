# Changelog

## 1.0.0 (2026-06-09)

First standalone release.

- Initial port from bradautomates/claude-video to a self-contained skill
  package installable in Hermes, Codex, or any Claude/agent runtime.
- Linux installer: auto-installs `ffmpeg` (apt) and `yt-dlp` (pip --user)
  when running as root; falls back to printing exact commands otherwise.
- Native captions first, Whisper API fallback (Groq preferred, OpenAI
  compatible).
- Frame budget scales with video duration: 30-100 frames, capped at 2 fps
  and 100 total.
- Focused mode (`--start` / `--end`) for dense inspection of specific
  sections.
- 25 MB Whisper upload limit surfaced clearly with actionable guidance.
