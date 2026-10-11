---
name: tiktok-download
description: "Download a TikTok video when yt-dlp and Chrome cookies fail."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [media, tiktok, video-download, web-scraping]
---

# TikTok Download (anti-bot workaround)

Download a TikTok video when the standard tools fail. This is the ONLY reliable
method on this Windows machine (verified 2026-08-29).

## When to Use
- The user gives a TikTok URL to download: short `vt.tiktok.com/<code>` links or
  full `www.tiktok.com/@user/video/<id>`.
- `yt-dlp` returns `Unable to extract universal data for rehydration`, and/or
  `--cookies-from-browser chrome` returns `Failed to decrypt with DPAPI`.

## Why the obvious paths fail
- `yt-dlp <tiktok_url>` → `Unable to extract universal data for rehydration`
  (known TikTok extractor breakage; happens even on latest yt-dlp).
- `yt-dlp --cookies-from-browser chrome <url>` → `Failed to decrypt with DPAPI`
  (Chrome 127+ App-Bound Encryption — yt-dlp can't decrypt, issue #10927).
- Direct-downloading an extracted `playAddr` URL with a fresh request → **403**:
  the CDN demands the SAME session (cookies + referer + matching UA).

## Working method (3 steps)
1. **GET the page with a mobile (Android) UA.** That page shape exposes the
   direct video URL in its embedded rehydration JSON.
   `UA = Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36`
2. **Parse `"playAddr":"..."`** from the HTML (value is JSON-escaped:
   `\u002F` = `/`). Unescape via `.encode().decode('unicode_escape')`.
3. **Download the playAddr in the SAME `requests.Session`** (keeps page cookies),
   with header `Referer: https://www.tiktok.com/` + the same mobile UA → 200 MP4.

Keep ONE session object for both the page fetch and the video GET.

## Script
Run the helper (re-runnable): see `scripts/tiktok_dl.py`.
```bash
python "C:/Users/<USER>/AppData/Local/hermes/skills/tiktok-download/scripts/tiktok_dl.py" "<URL>" -o "C:/Users/<USER>/Downloads"
```

## Pitfalls
- Short links (`vt.tiktok.com/...`) 302-redirect to `www.tiktok.com/@user/video/<id>` —
  just follow the redirect (requests does this automatically).
- Do NOT deliver without ffprobe verification:
  `ffprobe -v error -show_entries format=duration -show_entries stream=codec_name,width,height -of default=noprint_wrappers=1 file.mp4`
  Phone TikTok = h264 576x1024 + aac, ~60s, ~7MB.
- If the CDN still 403s, re-fetch the page (the signed token in playAddr can
  expire) and re-extract fresh.

## Reference
Full method + code: `references/tiktok.md`
