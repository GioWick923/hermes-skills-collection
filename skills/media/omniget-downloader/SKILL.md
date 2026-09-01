---
name: omniget-downloader
description: Use when the user asks to download media or links.
version: 1.0.0
author: hermes
license: MIT
metadata:
  tags: [download, video, youtube, tiktok, media, yt-dlp]
  related_skills: [torlink-downloader]
---

# OmniGet Downloader (first choice for downloads)

## When to Use
Trigger when the user asks to download any media/link: YouTube, TikTok, Instagram, X/Twitter, Reddit, Bilibili, courses (Udemy/Hotmart), audio/music, or a batch of URLs. OmniGet is the FIRST download option on this machine.

OmniGet v0.8.6 (tonhowtf/omniget) — universal downloader, 1,800+ sites via yt-dlp. GUI + CLI on Windows.

## Binary paths (Windows, MSYS/git-bash)
- GUI: `C:/Users/<USER>/Apps/OmniGet/omniget.exe` (portable, launch with `start` or background)
- CLI: `C:/Users/<USER>/Apps/OmniGet/cli/omniget-cli.exe`

## Priority
1. **OmniGet = FIRST** for any web media download (YT/TikTok/IG/X/Reddit/Bilibili, courses, audio).
2. torlink (:9161) = fallback/alternative for **torrents/magnets** (skill: torlink-downloader).
3. Ask user for output folder if not obvious; default `C:/Users/<USER>/Downloads`.

## Usage

### Single video
```bash
"C:/Users/<USER>/Apps/OmniGet/cli/omniget-cli.exe" download "<URL>" -o "C:/Users/<USER>/Downloads" -q 1080
```
Flags: `-q <height>` quality (720/1080), `--audio-only`, `--subs en,es`, `--format mp4/mkv/webm`, `--json`, `--proxy <url>`.

### Audio only
```bash
... download "<URL>" --audio-only -o "C:/Users/<USER>/Downloads"
```

### Preview before download (cheap, no download)
```bash
... info "<URL>"
```
Returns platform, title, duration, uploader, formats. Use for validation first.

### Batch (one URL per line in a file)
```bash
... batch "C:/path/list.txt" -o "C:/Users/<USER>/Downloads"
```

### Cookies (for logged-in content: Udemy/Hotmart/X/etc.)
```bash
... import-cookies "C:/path/cookies.txt"
```
cookies.txt must be Netscape format (export via browser extension).

## GUI hotkey
App GUI (if running): global hotkey `Ctrl+Shift+D` downloads whatever is in clipboard. Also accepts magnet links for torrents.

## Pitfalls
- CLI is native Windows exe: use forward-slash native paths, NOT MSYS converted paths.
- Do NOT pipe the command output to shorten it if exit code matters; run bare (Hermes auto-truncates).
- Long downloads: run with `background=true` + `notify_on_complete=true`, then poll.
- If a site needs login, import cookies first, otherwise 403/private errors.
- SmartScreen warning on first GUI run is normal (unsigned open source) — click "More info → Run anyway".
- Memory note: if the image/vision tool fails, ASK the user which tool before assuming by name (omnicat ≠ omniget).

## Verification
- `info` returns metadata → URL valid.
- After download: `ls -la` the output dir, confirm file exists and size > 0.
