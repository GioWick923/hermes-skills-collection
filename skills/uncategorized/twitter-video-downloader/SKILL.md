---
category: twitter-video-downloader
name: twitter-video-downloader
description: Download videos from Twitter/X posts (x.com and twitter.com) using yt-dlp. Use when the user asks to "download twitter video", "download tweet video", "dl twitter", "save twitter video", "download this tweet", or provides an x.com / twitter.com status URL with intent to download the video. Handles public tweets; may need browser cookies for age-restricted or protected media.
---

# Twitter / X Video Downloader

Download videos from Twitter/X posts using `yt-dlp`. This skill is a Hermes-adapted
port of HartreeWorks/skill--download-twitter-video, with Windows-correct paths and a
Hermes-native output directory.

## Prerequisites

`yt-dlp` must be available. On this machine it is installed at:
`C:\Users\<USER> GAMES\.venvs\media\Scripts\yt-dlp.exe`

Verify it works:
```bash
"$HOME/.venvs/media/Scripts/yt-dlp" --version
```
If missing, install with: `pip install yt-dlp` (or `uv pip install yt-dlp`).

## Workflow

### Step 1: Validate the URL

Accept URLs in these formats:
- `https://x.com/username/status/1234567890`
- `https://twitter.com/username/status/1234567890`

Extract the tweet ID (the numeric portion after `/status/`).

### Step 2: Create output directory

```bash
mkdir -p "$HOME/AppData/Local/hermes/skills/twitter-video-downloader/videos"
```

### Step 3: Download the video

Use yt-dlp to download the video:

```bash
"$HOME/.venvs/media/Scripts/yt-dlp" -f "best[ext=mp4]/best" \
  -o "$HOME/AppData/Local/hermes/skills/twitter-video-downloader/videos/%(id)s.%(ext)s" \
  "<TWITTER_URL>"
```

The video is saved as `<tweet-id>.mp4` in the videos directory.

### Step 4: Report results

After download, report:
- Full path to the downloaded file
- File size (use `ls -lh` or `du -h`)
- Confirmation message

Example output:
```
Downloaded: C:\Users\<USER> GAMES\AppData\Local\hermes\skills\twitter-video-downloader\videos\1774403827548242333.mp4
Size: 12.5 MB
```

## Troubleshooting

If yt-dlp fails, check available formats:
```bash
"$HOME/.venvs/media/Scripts/yt-dlp" --list-formats "<TWITTER_URL>"
```

If authentication is required (age-restricted or protected media), yt-dlp may need
cookies. Export cookies from your browser:
```bash
"$HOME/.venvs/media/Scripts/yt-dlp" --cookies-from-browser chrome "<TWITTER_URL>"
```

## Output location

All videos are saved to:
```
C:\Users\<USER> GAMES\AppData\Local\hermes\skills\twitter-video-downloader\videos\
```
