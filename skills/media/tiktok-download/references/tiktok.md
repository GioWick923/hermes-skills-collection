# TikTok download — method detail + code (Windows/Hermes)

Verified working 2026-08-29 on this machine. Reference for the `tiktok-download`
skill. Handles short links (`vt.tiktok.com/<code>`) and full
`www.tiktok.com/@user/video/<id>` links.

## Why the obvious paths fail
- `yt-dlp <tiktok_url>` → `ERROR: [TikTok] ... Unable to extract universal data
  for rehydration`. Known TikTok extractor breakage; happens even on the latest
  yt-dlp (2026.08.19 at time of writing).
- `yt-dlp --cookies-from-browser chrome <url>` → `ERROR: Failed to decrypt with
  DPAPI` — Chrome 127+ encrypts cookies with **App-Bound Encryption**, which
  yt-dlp cannot decrypt (github.com/yt-dlp/yt-dlp/issues/10927).
- Desktop-UA page fetch still yields the rehydration error.
- Plain requests GET of an extracted `playAddr` → **403**. The TikTok CDN
  requires the SAME session (cookies + referer + matching UA).

## Working method (3 steps)
1. GET the TikTok URL with a **mobile (Android) User-Agent**. That page shape
   exposes the direct video URL in its embedded rehydration JSON.
   `UA = Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36`
2. Parse `"playAddr":"..."` from the HTML. The value is JSON-escaped
   (`\u002F` = `/`). Unescape with `.encode().decode('unicode_escape')`.
3. Download the playAddr URL **in the same `requests.Session`** (keeps the page
   cookies), header `Referer: https://www.tiktok.com/` + the same mobile UA.
   → 200, full MP4.

Keep ONE session object for both the page fetch and the video GET so the cookies
captured from the page are present on the CDN request.

## Reference snippet
```python
import re, requests
UA = "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
s = requests.Session(); s.headers.update({"User-Agent": UA})
r = s.get("https://vt.tiktok.com/<code>/", timeout=30, allow_redirects=True)  # follows 302 to www.tiktok.com/@user/video/<id>
m = re.search(r'"playAddr":"((?:[^"\\]|\\.)*)"', r.text)
url = m.group(1).encode().decode('unicode_escape')
vr = s.get(url, headers={"Referer":"https://www.tiktok.com/","User-Agent":UA}, timeout=120)
if vr.status_code == 200 and len(vr.content) > 10000:
    open("tiktok_video.mp4","wb").write(vr.content)
```

## Verify before delivering
```bash
ffprobe -v error -show_entries format=duration -show_entries stream=codec_name,width,height -of default=noprint_wrappers=1 file.mp4
```
Phone TikTok typical: h264 576x1024 + aac, ~60s, ~7MB.

## Pitfalls
- Signed token in `playAddr` can expire → if the CDN 403s, re-fetch the page and
  re-extract a fresh playAddr rather than retrying the stale URL.
- For the video GET, pass Referer AND the exact same mobile UA that fetched the page.
- Deliver over Telegram as `MEDIA:<native C:/ path>` (user preference).
