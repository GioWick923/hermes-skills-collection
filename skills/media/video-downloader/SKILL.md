---
category: video-downloader
name: video-downloader
description: Download videos from multiple social platforms without watermarks. Use when the user wants to download videos from Douyin, X (Twitter), Bilibili, YouTube, or Xiaohongshu, or provides a URL from any of those platforms. Supports MP4 download plus metadata extraction (title, author, duration, resolution, size). Triggers for "download video", "无水印下载", "抖音视频", "B站视频", "YouTube视频", "X视频", "Twitter视频", or any request involving these platforms.
---

# Multi-Platform Video Downloader

Ported to Hermes (Windows) from wxhou/video-downloader-skill. Downloads from
Douyin, X/Twitter, Bilibili, YouTube, Xiaohongshu in MP4 with metadata JSON.

## Why this skill

- X/Twitter: tries **vxtwitter API** first (no login/cookies needed), then falls
  back to `yt-dlp`, then Playwright. Can extract MULTIPLE videos from one tweet.
- Other platforms handled by `yt-dlp` / platform-specific extractors.
- Saves metadata (title, author, duration, resolution, size) as a sidecar `.json`.

## Environment (this machine)

- `yt-dlp` lives in: `C:\Users\<USER> GAMES\.venvs\media\Scripts\`
  It is NOT on the global PATH, so always run the script through the media venv
  python (below) so `yt-dlp`/`ffprobe`/`curl` resolve correctly.
- `ffprobe`/`ffmpeg` are available (WinGet links).
- `curl` is available (mingw64).
- Playwright is NOT installed — this is fine: Twitter falls back to yt-dlp/vxtwitter,
  and only Douyin/Xiaohongshu advanced paths need it. Those will degrade gracefully.

## How to invoke

Use the media venv python so `yt-dlp` is on PATH:

```bash
"$HOME/.venvs/media/Scripts/python.exe" \
  "$HOME/AppData/Local/hermes/skills/video-downloader/scripts/download.py" \
  "<VIDEO_URL>" -o "<OUTPUT_DIR>"
```

Examples:
```bash
# X / Twitter (auto: vxtwitter -> yt-dlp)
"$HOME/.venvs/media/Scripts/python.exe" \
  "$HOME/AppData/Local/hermes/skills/video-downloader/scripts/download.py" \
  "https://x.com/user/status/123456789" -o "$HOME/Downloads"

# YouTube / Bilibili
"$HOME/.venvs/media/Scripts/python.exe" \
  "$HOME/AppData/Local/hermes/skills/video-downloader/scripts/download.py" \
  "https://www.youtube.com/watch?v=xxxxx" -o "$HOME/Downloads"

# Batch from a file (one URL per line)
"$HOME/.venvs/media/Scripts/python.exe" \
  "$HOME/AppData/Local/hermes/skills/video-downloader/scripts/batch_download.py" \
  urls.txt -o "$HOME/Downloads"
```

Without `-o`, videos go to `./downloaded_videos` (relative to current dir).

## Supported URL formats

| Platform | Example URL |
|----------|-------------|
| Douyin | `https://www.douyin.com/video/123456789` or `https://v.douyin.com/xxxxx` |
| X / Twitter | `https://x.com/user/status/123456789` or `https://twitter.com/user/status/123456789` |
| Bilibili | `https://www.bilibili.com/video/BVxxxxxx` or `https://b23.tv/xxxxx` |
| YouTube | `https://www.youtube.com/watch?v=xxxxx` or `https://youtu.be/xxxxx` |
| Xiaohongshu | `https://www.xiaohongshu.com/discovery/item/xxxxx` |

## Report results

After running, report the downloaded file path(s), file size, and resolution.
Metadata (if saved) is in the sidecar `<name>.json`.

## Troubleshooting

- "Cookie required" / age-restricted X media: the vxtwitter path usually avoids this;
  if it still fails, fall back to the dedicated `twitter-video-downloader` skill which
  can pass `--cookies-from-browser chrome`.
- Douyin/Xiaohongshu advanced browser paths need Playwright (not installed here);
  they will report "playwright not available" and fall back to API/yt-dlp.
- Transcribe feature (`--transcribe`) needs OpenAI Whisper (`pip install openai-whisper`)
  with medium/large model; not set up by default.
