#!/usr/bin/env python3
"""
tweet_reader.py — leer tweets X/Twitter al instante (sin auth ni browser).

Usa el endpoint público de syndication de X (cdn.syndication.twimg.com/tweet-result)
que devuelve texto + media de tweets PÚBLICOS SIN iniciar sesión — evita el 403 de los
browsers headless y no depende de cookies.

Entrada: URL de x.com/twitter.com (con o sin ?s=), un pic.x.com, o un ID numérico.
Salida: un JSON con texto, autor, fecha, metadata y todas las URLs de media (foto/video),
        listo para el agente (descargar imagen + vision_analyze, o yt-dlp para video).

Uso:
  python tweet_reader.py "https://x.com/user/status/1234567890"
  python tweet_reader.py 1234567890
  python tweet_reader.py "https://x.com/user/status/1234567890" --download-dir <dir>

Requiere: stdlib only (urllib, json, re, random). Sin dependencias externas.
"""
import argparse
import json
import random
import re
import string
import sys
import urllib.request

SYNDICATION = "https://cdn.syndication.twimg.com/tweet-result?id={tid}&token={token}"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120 Safari/537.36"}

_ID_RE = re.compile(r"(?:status|i/web|photo|video)/(\d{6,25})")
_TCO_RE = re.compile(r"(?:status|i/web)/(\d{6,25})")


def extract_id(text: str) -> str:
    """Extrae el ID numérico del tweet desde un URL/ID/t.co."""
    m = _ID_RE.search(text) or _TCO_RE.search(text)
    if m:
        return m.group(1)
    # URL t.co de media: pic.x.com/<code> no trae ID -> intenta como ID numérico directo
    clean = text.strip()
    if clean.isdigit():
        return clean
    # si es un t.co corto de un tweet, seguir redirect
    if "t.co/" in clean or "x.com/" in clean:
        raise ValueError("No se encontró ID de tweet en la URL: " + text[:120])
    raise ValueError("URL no parece un tweet: " + text[:120])


def fetch_tweet(tid: str) -> dict:
    token = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    req = urllib.request.Request(SYNDICATION.format(tid=tid, token=token), headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def summarize(d: dict) -> dict:
    user = d.get("user", {})
    text = (d.get("text") or d.get("full_text") or "").strip()
    # imágenes: photos[].url (la versión original)
    photos = []
    for p in d.get("photos", []):
        u = p.get("url")
        if u:
            # subir a tamaño completo si aplica (name=large / orig es default de url ya)
            photos.append(u)
    # si no hay photos pero hay media_url_https en mediaDetails
    if not photos:
        for m in (d.get("mediaDetails") or []):
            mu = m.get("media_url_https")
            if mu:
                photos.append(mu if mu.endswith(":orig") else mu + "?name=orig")
    out = {
        "id": d.get("id_str"),
        "author": user.get("screen_name"),
        "name": user.get("name"),
        "created_at": d.get("created_at"),
        "lang": d.get("lang"),
        "favorite_count": d.get("favorite_count"),
        "retweet_count": d.get("retweet_count"),
        "text": text,
        "photos": photos,
        "has_video": bool(d.get("extended_entities", {}).get("media")) or _has_video(d),
    }
    return out


def _has_video(d: dict) -> bool:
    for m in (d.get("mediaDetails") or []):
        if m.get("type") == "video" or m.get("video_info"):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Leer un tweet X/Twitter al instante (sin auth).")
    ap.add_argument("url", help="URL de x.com/twitter.com o ID numérico")
    ap.add_argument("--download-dir", default=None, help="Descargar las fotos a este dir (opcional)")
    ap.add_argument("--json", action="store_true", help="Print solo JSON")
    args = ap.parse_args()

    try:
        tid = extract_id(args.url)
        d = fetch_tweet(tid)
    except Exception as e:
        print("TWEET_READ_ERR:", e, file=sys.stderr)
        return 1

    s = summarize(d)
    if args.json:
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return 0

    # Salida legible para el agente/contexto
    print(f"AUTHOR: @{s['author']} ({s['name']})")
    print(f"DATE: {s.get('created_at','')[:16]}")
    print(f"FAV:{s.get('favorite_count')}  RT:{s.get('retweet_count')}  LANG:{s.get('lang')}")
    print(f"HAS_VIDEO: {s.get('has_video')}")
    print("=== TEXT ===")
    print(s["text"])
    print("=== PHOTOS ===")
    for i, u in enumerate(s["photos"], 1):
        print(f"{i}: {u}")

    # Descargar imágenes si se pidió (para luego vision_analyze)
    if args.download_dir and s["photos"]:
        import os
        os.makedirs(args.download_dir, exist_ok=True)
        paths = []
        for i, u in enumerate(s["photos"], 1):
            try:
                req = urllib.request.Request(u, headers=UA)
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = r.read()
                ext = ".jpg"
                p = os.path.join(args.download_dir, f"tweet_{s['id']}_{i}{ext}")
                with open(p, "wb") as f:
                    f.write(data)
                paths.append(p)
            except Exception as e:
                print(f"  DL_ERR {i}: {e}", file=sys.stderr)
        if paths:
            print("=== DOWNLOADED ===")
            for p in paths:
                print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
