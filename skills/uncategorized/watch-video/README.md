# Hermes watch-video skill

Give your AI agent the ability to **watch any video**. Point it at a
YouTube / TikTok / Vimeo / X / Loom URL (anything yt-dlp supports) or a
local `.mp4` / `.mov` / `.mkv` / `.webm` and ask a question — the agent
downloads the video, extracts frames at an auto-scaled rate, pulls a
timestamped transcript, and reads every frame as an image. By the time
it answers, it has *seen* the video and *heard* the audio.

> Adapted from
> [bradautomates/claude-video](https://github.com/bradautomates/claude-video)
> for [Hermes Agent](https://hermes-agent.nousresearch.com). Built on
> `yt-dlp`, `ffmpeg`, and the Whisper API (Groq preferred, OpenAI
> compatible).

## How it works

1. You paste a video URL or local path and ask a question.
2. `yt-dlp` downloads the video (URLs) or resolves the local file. Captions
   are pulled from the source if available — free, instant, accurate-ish.
3. `ffmpeg` extracts frames as JPEGs. The frame budget is duration-aware:
   - ≤30 s → ~30 frames
   - 30 s - 1 min → ~40 frames
   - 1 - 3 min → ~60 frames
   - 3 - 10 min → ~80 frames
   - &gt; 10 min → 100 frames (sparse, with a warning)
   - Hard ceiling: 2 fps, 100 frames total.
4. The transcript comes from one of two places. First try: native captions
   from `yt-dlp`. Fallback: extract a mono 16 kHz audio clip and ship it
   to Whisper via Groq (preferred — cheaper and faster) or OpenAI.
5. The skill prints a markdown report with frame paths and the transcript.
   The agent reads each frame (via `vision_analyze` in Hermes, or `Read`
   in Claude) and answers the question.

## Install

```bash
# Hermes
git clone https://github.com/MarcusGraetsch/hermes-watch-video-skill.git \
  ~/.hermes/skills/media/watch-video

# Codex
git clone https://github.com/MarcusGraetsch/hermes-watch-video-skill.git \
  ~/.codex/skills/watch

# Claude Code (development)
git clone https://github.com/MarcusGraetsch/hermes-watch-video-skill.git \
  ~/.claude/skills/watch

# Manual / dev — anywhere
git clone https://github.com/MarcusGraetsch/hermes-watch-video-skill.git \
  /your/path/watch-video
```

Then run the installer once:

```bash
python3 ~/.hermes/skills/media/watch-video/scripts/setup.py
```

The installer is idempotent and:
- On Linux: auto-installs `ffmpeg` via `apt-get` and `yt-dlp` via
  `pip install --user` when running as root; prints the exact commands
  otherwise.
- On macOS: auto-installs via `brew`.
- On Windows: prints the `winget` / `pip` commands.
- Creates `~/.config/watch/.env` (mode `0600`) with commented
  placeholders for `GROQ_API_KEY` (preferred) and `OPENAI_API_KEY`.

## API keys (optional, only for captionless videos)

Captions cover most public videos for free. Whisper only kicks in when
captions are missing (local files, TikToks, some Vimeos, the occasional
caption-less YouTube upload).

| Capability | What you need | Cost |
|------------|---------------|------|
| Download + native captions | `yt-dlp` + `ffmpeg` | Free |
| Whisper fallback (preferred) | [Groq API key](https://console.groq.com/keys) — `whisper-large-v3` | Cheap, fast |
| Whisper fallback (alt) | [OpenAI API key](https://platform.openai.com/api-keys) — `whisper-1` | Standard pricing |
| Disable Whisper entirely | `--no-whisper` | Free, frames-only when no captions |

Get a key, then add it to `~/.config/watch/.env`:

```bash
echo 'GROQ_API_KEY=*** >> ~/.config/watch/.env
chmod 600 ~/.config/watch/.env
```

## Use

The skill is auto-discovered by the agent. In Hermes you can either type
the slash command or just describe what you want:

```bash
# Slash command (Hermes / Codex)
/watch-video https://youtu.be/dQw4w9WgXcQ what happens at 2:30?
/watch-video ~/Movies/bug-repro.mov when does the UI break?
/watch-video https://www.tiktok.com/@user/video/123 summarize this

# Or natural language — the agent matches the description in SKILL.md
"schau dir das video an und sag mir was bei minute 3 passiert"
"watch this: https://vimeo.com/123 — what tools does she mention?"
"analyze https://youtu.be/abc and find the bug"
```

### Focused mode — zoom into a section

When you ask about a specific moment, pass `--start` and `--end` to get
a denser frame budget over the window you care about:

```bash
/watch-video video.mp4 --start 50 --end 60          # last 10s
/watch-video "$URL" --start 2:15 --end 2:45 --fps 3  # 30s at 3fps
/watch-video "$URL" --start 1:12:00                  # from 1h12m to end
```

The transcript is auto-filtered to the same range. Frame timestamps are
absolute (real video timeline, not offset-from-start).

## Limits

- **Best accuracy: under 10 minutes.** Past that, frame coverage is
  sparse. Re-run focused on the part you care about.
- **Hard caps: 2 fps, 100 frames total.** Frame count drives token
  cost.
- **Whisper upload limit: 25 MB.** At mono 16 kHz mp3 that's about 50
  minutes of audio. Longer videos need either captions or
  `--start`/`--end` to a smaller window.
- **No private platforms.** This skill doesn't log into anything. Public
  URLs and local files only.

## Token cost (rough order of magnitude)

- 80 frames at 512 px wide ≈ 50-80k image tokens
- Bumping `--resolution` to 1024 px roughly quadruples image tokens per
  frame — only do it when you need to read on-screen text (slides,
  terminals, code)
- Transcript is cheap (a few thousand tokens for a 10-min video)

If you've already watched a video in the same session and the user asks
a follow-up, **don't re-run the script** — the frames and transcript are
already in context.

## Security

- Runs `yt-dlp` locally to download public videos and pull native
  captions
- Runs `ffmpeg` / `ffprobe` locally to extract frames as JPEGs and a
  mono 16 kHz audio clip when Whisper is needed
- Sends extracted audio (not the video) to `api.groq.com` (preferred) or
  `api.openai.com` (fallback) when a key is configured
- Writes downloaded video, frames, audio, and an intermediate transcript
  to a working directory under the system temp dir
- Reads / creates `~/.config/watch/.env` (mode `0600`) for the API key
- Does **not** upload the video itself to any API
- Does **not** access any platform account (no login, no session
  cookies, no posting)
- Does **not** log or cache API keys

Review the scripts under `scripts/` to verify behavior before first use.

## License

MIT — see [LICENSE](LICENSE).

## Credits

Built on [bradautomates/claude-video](https://github.com/bradautomates/claude-video).
Whisper transcription via [Groq](https://groq.com) and
[OpenAI](https://openai.com).
