---
category: watch-video
name: watch-video
description: Watch a video — URL or local path. Downloads with yt-dlp, extracts auto-scaled frames with ffmpeg, pulls a transcript from captions (or Whisper API fallback), and hands the result to the agent so it can answer questions about what's in the video. Trigger phrases: "watch this video", "schau dir das video an", "analyze this video", "what happens in this video", "summarize this video", YouTube/TikTok/Vimeo URL, .mp4/.mov local path.
allowed-tools: Bash, Read, vision_analyze
---

# watch-video — Watch a video

This skill gives you a video input. A Python script downloads the video,
extracts frames as JPEGs, gets a timestamped transcript (native captions
first, then Whisper API as fallback), and prints frame paths. You then
`vision_analyze` each frame path to see the image and combine it with the
transcript to answer the user.

Adapted from [bradautomates/claude-video](https://github.com/bradautomates/claude-video)
for Hermes. Differences from upstream:
- Linux/apt installer (no Homebrew) — auto-installs ffmpeg via apt and yt-dlp
  via `pip install --user` when running as root; prints exact commands otherwise.
- Reads frames via `vision_analyze` (Hermes tool) instead of Claude's `Read`.
- Whisper User-Agent identifies as `hermes-agent` instead of `claude-code`.

## Installation

`${SKILL_DIR}` in the examples below is the directory where this SKILL.md
lives. For a standard Hermes install that's
`~/.hermes/skills/media/watch-video/`. For Codex it's
`~/.codex/skills/watch/`. Adjust to taste:

```bash
# Hermes
git clone https://github.com/MarcusGraetsch/hermes-watch-video-skill.git \
  ~/.hermes/skills/media/watch-video

# Codex
git clone https://github.com/MarcusGraetsch/hermes-watch-video-skill.git \
  ~/.codex/skills/watch

# Anywhere else
git clone https://github.com/MarcusGraetsch/hermes-watch-video-skill.git \
  /path/to/skills/watch-video
export SKILL_DIR=/path/to/skills/watch-video
```

Then run `python3 ${SKILL_DIR}/scripts/setup.py` once to install ffmpeg /
yt-dlp and scaffold `~/.config/watch/.env`. The examples below assume
`SKILL_DIR` is set in your shell, or you can paste the full path.

## When to use

- User pastes a video URL (YouTube, Vimeo, X, TikTok, Twitch clip — anything
  yt-dlp supports) and asks about it.
- User points at a local video file (`.mp4`, `.mov`, `.mkv`, `.webm`, etc.).
- User asks to summarize a video, analyze its structure, find a moment,
  read on-screen text, or describe what's happening visually.

## Step 0 — Setup preflight

Before the first watch in a session, verify that dependencies and an API
key are in place. Use `skill_dir` to find the script path. Hermes exposes
the skill directory via the SKILL.md location — resolve it like this:

```bash
python3 ${SKILL_DIR}/scripts/setup.py --check
```

This is a <100ms lookup. On exit 0 the script emits nothing — proceed
straight to Step 1 without comment. Do NOT announce "setup is complete"
to the user on every turn.

On non-zero exit, run the full installer:

```bash
python3 ${SKILL_DIR}/scripts/setup.py
```

The installer is idempotent — safe to re-run. It auto-installs missing
binaries (apt + pip --user on Linux) and scaffolds `~/.config/watch/.env`
with placeholder API keys (mode `0600`).

If an API key is still missing after install, ask the user which provider
they have (Groq preferred — cheaper and faster; OpenAI is the compatible
fallback), then write it to `~/.config/watch/.env`:

```bash
echo 'GROQ_API_KEY=gsk_...*** ~/.config/watch/.env && chmod 600 ~/.config/watch/.env
echo 'SETUP_COMPLETE=true' >> ~/.config/watch/.env
```

Within a single session, you can skip Step 0 on follow-ups — once
`--check` returned 0, nothing about the environment changes.

Structured mode for branching on specifics:
```bash
python3 ${SKILL_DIR}/scripts/setup.py --json
```
Emits `{status, first_run, missing_binaries, whisper_backend, has_api_key,
config_file, platform}` where `status` is one of
`ready | needs_install | needs_key | needs_install_and_key`.

## Step 1 — Parse the user input

Separate the video source (URL or path) from any question the user asked.

Example: "kannst du das video schauen und mir sagen was bei 2:30 passiert?
https://youtu.be/abc" → source = `https://youtu.be/abc`, question = "what
happens at 2:30?". When in doubt, the URL/path is usually the last token
in the message.

## Step 2 — Run the watch script

```bash
python3 ${SKILL_DIR}/scripts/watch.py "<source>"
```

Optional flags:
- `--start T` / `--end T` — focus on a section. Accepts `SS`, `MM:SS`, or
  `HH:MM:SS`. When either is set, fps auto-scales denser.
- `--max-frames N` — lower the cap for a tighter token budget (e.g. `--max-frames 40`).
- `--resolution W` — change frame width in px (default 512; bump to 1024
  only if the user needs to read on-screen text).
- `--fps F` — override auto-fps (clamped to 2 fps max).
- `--out-dir DIR` — keep working files somewhere specific (default: an
  auto-generated tmp dir under `/tmp/watch-XXXX`).
- `--whisper groq|openai` — force a specific Whisper backend (default:
  prefer Groq, fall back to OpenAI).
- `--no-whisper` — disable the Whisper fallback entirely (frames-only if
  no captions).

### Focusing on a section (higher frame rate)

When the user asks about a specific moment — "what happens at the 2 minute
mark?", "zoom into 0:45 to 1:00", "the first 10 seconds" — pass
`--start` and/or `--end`. Focused-mode budgets are denser than
full-video budgets (still capped at 2 fps):

| Duration | Frame budget |
|----------|--------------|
| ≤5s      | 2 fps (up to 10 frames) |
| 5-15s    | 2 fps (up to 30 frames) |
| 15-30s   | ~2 fps (up to 60 frames) |
| 30-60s   | ~1.3 fps (up to 80 frames) |
| 60-180s  | ~0.6 fps (100 frames, capped) |

Focused mode is the right call for any moment/range the user names
explicitly, any video longer than ~10 minutes where the user's question
is about a specific part, and re-runs after a full scan didn't have
enough detail in some region. Transcript is auto-filtered to the same
range. Frame timestamps are absolute (real video timeline, not
offset-from-start).

Examples:
```bash
# Last 10 seconds of a 1 minute video
python3 ${SKILL_DIR}/scripts/watch.py video.mp4 --start 50 --end 60

# Zoom into 2:15 → 2:45 at 3 fps
python3 ${SKILL_DIR}/scripts/watch.py "$URL" --start 2:15 --end 2:45 --fps 3

# From 1h12m to the end of the video
python3 ${SKILL_DIR}/scripts/watch.py "$URL" --start 1:12:00
```

## Step 3 — vision_analyze every frame

The script prints a markdown report to stdout with frame paths and a
transcript. For each frame path printed in the report, call
`vision_analyze` (Hermes tool) with the question "What is shown in this
frame?" or a more targeted question. Call them in parallel — the script
prints frames in chronological order with `t=MM:SS` markers, so you can
align them to the transcript.

If a follow-up question is about a specific timestamp, prioritize
`vision_analyze` on the frames closest to that timestamp.

## Step 4 — Answer the user

You now have two streams of evidence:
- **Frames** — what's on screen at each timestamp.
- **Transcript** — what's said at each timestamp. The report's header
  shows the source: `captions` = yt-dlp pulled native subs;
  `whisper (groq)` or `whisper (openai)` = transcribed by API.

If the user asked a specific question, answer it directly citing
timestamps. If they didn't ask anything, summarize what happens in the
video — structure, key moments, notable visuals, spoken content.

If the script's report shows a "sparse scan" warning (video > 10 min
full-scan), acknowledge it in your answer and offer to re-run focused on
a specific section with `--start`/`--end`.

## Step 5 — Clean up

The script prints a working directory at the end. If the user isn't
going to ask follow-ups about this video, delete it:

```bash
rm -rf /tmp/watch-XXXX
```

If they might, leave it in place so a follow-up `--start`/`--end` run can
reuse the downloaded source if the original URL is still valid (note: the
script re-downloads on each run, so cleanup is mostly about disk space
on the extracted frames — typically 5-50 MB per video).

## Limits

- **Best accuracy: under 10 minutes.** Frame coverage scales inversely
  with duration.
- **Hard caps: 100 frames total, 2 fps.** Frame count drives token cost.
- **Whisper upload limit: 25 MB.** At mono 16 kHz mp3 that's about 50
  minutes of audio. Longer videos need either captions or a smaller
  window.
- **No private platforms.** This skill doesn't log into anything. Public
  URLs and local files only.

## Token efficiency

Order of magnitude: 80 frames at 512px is roughly 50-80k image tokens
depending on aspect ratio. Transcript is cheap (a few thousand tokens at
most for a 10-minute video). Bumping `--resolution` to 1024 roughly
quadruples image tokens per frame — only do it when necessary (slides,
terminals, code on screen).

If you already watched a video this session and the user asks a
follow-up, do **not** re-run the script — you already have the frames
and transcript in context. Just answer from what you have.

## Failure modes

- **Setup preflight failed** → run `python3 .../scripts/setup.py` (auto-installs on Linux, scaffolds the `.env`). For the API key, ask the user and write it to `~/.config/watch/.env`.
- **No transcript available** → captions missing AND (no Whisper key OR Whisper API failed). Proceed frames-only and tell the user.
- **Long video warning printed** → acknowledge it. Offer to re-run focused.
- **Download fails** → yt-dlp's error goes to stderr. If it's login-required or region-locked, tell the user plainly; do not keep retrying.
- **Whisper request fails** → error printed to stderr (likely: invalid key, rate limit, or 25 MB upload limit on a long video). You can retry with `--whisper openai` if Groq failed (or vice versa).

## Security

- Runs `yt-dlp` locally to download public videos and pull native captions.
- Runs `ffmpeg` / `ffprobe` locally to extract frames as JPEGs and a mono 16 kHz audio clip when Whisper is needed.
- Sends extracted audio (not the video) to `api.groq.com` (preferred) or
  `api.openai.com` (fallback) when a key is configured.
- Writes downloaded video, frames, audio, and an intermediate transcript
  to a working directory under the system temp dir.
- Reads / creates `~/.config/watch/.env` (mode `0600`) to store Whisper
  API keys. As a fallback, also reads `.env` in the current working directory.
- Does not upload the video itself to any API. Does not access any
  platform account (no login, no session cookies). Does not log or
  cache API keys.
