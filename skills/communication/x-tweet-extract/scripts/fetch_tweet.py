#!/usr/bin/env python3
"""
fetch_tweet.py — extrae texto y media URLs de un tweet público de X/Twitter
SIN login, usando el endpoint público de syndication.

Uso:
    python fetch_tweet.py <ID_o_URL_del_tweet>
    python fetch_tweet.py https://x.com/user/status/2094406418195702207
    python fetch_tweet.py 2094406418195702207

Requiere: Python 3 stdlib (urllib, json, re, sys, random, string).
Sin dependencias externas.
"""
import json
import re
import random
import string
import sys
import urllib.request

SYND = "https://cdn.syndication.twimg.com/tweet-result"


def get_tweet_id(arg: str) -> str:
    """Extrae el ID numérico de un enlace /status/<id> o de un ID puro."""
    arg = arg.strip()
    m = re.search(r"/status/(\d+)", arg)
    if m:
        return m.group(1)
    if arg.isdigit():
        return arg
    raise SystemExit(f"No se pudo extraer un tweet ID de: {arg!r}")


def make_token(n: int = 32) -> str:
    """Token aleatorio que el endpoint acepta (casi cualquier string corto)."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def fetch(tweet_id: str) -> dict:
    url = f"{SYND}?id={tweet_id}&token={make_token()}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def media_urls(data: dict) -> list:
    """Todas las URLs de media (pbs.twimg.com = imagen, video.twimg.com = video)."""
    blob = json.dumps(data, ensure_ascii=False)
    return sorted(set(re.findall(r"https://(?:pbs|video)\.twimg\.com/[^\"\s\\]+", blob)))


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Uso: python fetch_tweet.py <ID_o_URL>")
    tweet_id = get_tweet_id(sys.argv[1])
    try:
        d = fetch(tweet_id)
    except Exception as e:
        raise SystemExit(f"Error al extraer tweet {tweet_id}: {e}")

    user = d.get("user") or {}
    full_text = (d.get("full_text") or d.get("text") or "").strip()
    print("TWEET_ID:", tweet_id)
    print("AUTHOR:", f"{user.get('name')} @{user.get('screen_name')}")
    print("DATE:", d.get("created_at"))
    print("LANGS:", d.get("lang"))
    print("FAV:", d.get("favorite_count"), "| RT:", d.get("retweet_count"))
    print("TEXT:")
    print(full_text)
    print("\nMEDIA:")
    for u in media_urls(d):
        print(" -", u)


if __name__ == "__main__":
    main()
