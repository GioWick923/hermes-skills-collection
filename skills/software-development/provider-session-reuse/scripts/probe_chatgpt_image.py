#!/usr/bin/env python
"""
Ad-hoc probe for the ChatGPT web image-generation route via reused session.
Prints ONLY structure/status - never the token or cookie values.

Usage:
  python scripts/probe_chatgpt_image.py                 # bearer-only probe (shows 404/500)
  python scripts/probe_chatgpt_image.py --with-cookies COOKIES_TXT
        # pass a Cookie-Editor export (JSON or Netscape) to test the real route

What it proves:
  - bearer-only: confirms session is LIVE (non-401) but shows image endpoint 404/500
  - with-cookies: attempts the real /backend-api/f/conversation route

This is reverse-engineering of an anti-automation backend. Each network call can
consume the user's ChatGPT quota. Use sparingly.
"""
import json, os, sys, uuid, urllib.request, urllib.error, re

HERMES_HOME = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUTH_PATH=os.pat...OME, "auth.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"

def get_token():
    try:
        with open(AUTH_PATH, encoding="utf-8") as f:
            d = json.load(f)
        return d.get("providers", {}).get("openai-codex", {}).get("tokens", {}).get("access_token")
    except Exception as e:
        print(f"[auth] cannot read token: {e}", file=sys.stderr)
        return None

def load_cookies(path):
    with open(path, encoding="utf-8") as f:
        txt = f.read().strip()
    try:
        data = json.loads(txt)
        if isinstance(data, list):
            return "; ".join(f"{c['name']}={c['value']}" for c in data)
    except Exception:
        pass
    out = []
    for line in txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 7:
            out.append(f"{parts[5]}={parts[6]}")
        elif "=" in line:
            out.append(line)
    return "; ".join(out)

def req(method, url, headers, data=None, timeout=60):
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return None, {}, str(e).encode()

def main():
    with_cookies = False
    cookie_path = None
    if "--with-cookies" in sys.argv:
        with_cookies = True
        cookie_path = sys.argv[sys.argv.index("--with-cookies") + 1]
    token = get_token()
    if not token:
        print("FAIL: no openai-codex token"); return 1
    print(f"[auth] token present len={len(token)}")

    base = {
        "Authorization": f"Bearer {token}",
        "User-Agent": UA, "Origin": "https://chatgpt.com",
        "Referer": "https://chatgpt.com/", "oai-device-id": str(uuid.uuid4()),
    }
    if with_cookies:
        base["Cookie"] = load_cookies(cookie_path)
        print(f"[auth] cookies loaded len={len(base['Cookie'])}")

    st, sh, sb = req("GET", "https://chatgpt.com/backend-api/requirements", base, timeout=30)
    print(f"[req] /requirements status={st}")
    rt = ""
    if st == 200:
        try:
            rt = json.loads(sb.decode()).get("token", "")
            print(f"[req] requirements-token len={len(rt)}")
        except Exception:
            pass

    h = dict(base)
    h["Content-Type"] = "application/json"
    h["Accept"] = "text/event-stream"
    if rt:
        h["openai-sentinel-chat-requirements-token"] = rt
    msg_id = str(uuid.uuid4()); parent_id = str(uuid.uuid4())
    payload = json.dumps({
        "action": "next",
        "messages": [{"id": msg_id, "author": {"role": "user"},
                      "content": {"content_type": "text", "parts": ["a small red balloon, flat illustration"]},
                      "metadata": {}}],
        "parent_message_id": parent_id, "conversation_id": None,
        "model": "gpt-image-1", "history_and_training_disabled": False, "force_paragen": True,
    }).encode()
    st2, sh2, sb2 = req("POST", "https://chatgpt.com/backend-api/f/conversation", h, data=payload, timeout=120)
    text = sb2.decode(errors="replace")
    urls = re.findall(r'https://[^\s"\\]+\.(?:png|jpg|jpeg|webp)', text)
    print(f"[conv] /f/conversation status={st2} img_urls={len(urls)}")
    if urls:
        for u in urls[:5]:
            print("  IMG:", u)
        return 0
    print(f"[conv] muestra: {text[:300]!r}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
