#!/usr/bin/env python3
"""Download a TikTok video via mobile-UA page scrape + playAddr + same-session GET.

Usage:
    python tiktok_dl.py "<URL>" [-o OUTPUT_DIR]

Works when yt-dlp fails ("Unable to extract universal data for rehydration")
and Chrome cookies are DPAPI-encrypted (Chrome 127+ App-Bound Encryption).
Verifies with ffprobe if available. Prints the saved path + metadata.
"""
import argparse
import os
import re
import subprocess
import sys
import time

import requests

UA = ("Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36")


def extract_playaddr(text: str) -> str | None:
    m = re.search(r'"playAddr":"((?:[^"\\]|\\.)*)"', text)
    return m.group(1).encode().decode("unicode_escape") if m else None


def download(url: str, out: str) -> str | None:
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    page = s.get(url, timeout=30, allow_redirects=True)  # follows vt.tiktok.com -> www.tiktok.com/@user/video/<id>
    if page.status_code != 200:
        print(f"page error: HTTP {page.status_code}"); return None
    play = extract_playaddr(page.text)
    if not play:
        print("playAddr not found in page"); return None
    vr = s.get(play, headers={"Referer": "https://www.tiktok.com/", "User-Agent": UA}, timeout=120)
    if vr.status_code != 200 or len(vr.content) < 10000:
        print(f"video error: HTTP {vr.status_code} (len={len(vr.content)}) — token may be stale; retry re-fetches a fresh one")
        return None
    with open(out, "wb") as f:
        f.write(vr.content)
    return out


def verify(path: str) -> None:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error",
             "-show_entries", "format=duration",
             "-show_entries", "stream=codec_name,width,height",
             "-of", "default=noprint_wrappers=1", path],
            capture_output=True, text=True, timeout=60)
        print(r.stdout.strip() or r.stderr.strip())
    except Exception as e:
        print(f"ffprobe unavailable: {e}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Download a TikTok video")
    ap.add_argument("url", help="TikTok URL (vt.tiktok.com/... or www.tiktok.com/@user/video/<id>)")
    ap.add_argument("-o", "--output-dir", default=os.path.expanduser("~/Downloads"))
    a = ap.parse_args()
    os.makedirs(a.output_dir, exist_ok=True)
    out = os.path.join(a.output_dir, f"tiktok_video_{int(time.time())}.mp4")
    saved = download(a.url, out)
    if not saved:
        return 1
    print(f"SAVED: {saved} ({os.path.getsize(saved)} bytes)")
    verify(saved)
    return 0


if __name__ == "__main__":
    sys.exit(main())
