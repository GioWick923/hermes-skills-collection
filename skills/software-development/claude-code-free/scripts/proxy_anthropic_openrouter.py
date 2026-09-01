#!/usr/bin/env python3
"""Proxy local: traduce el protocolo Anthropic (Claude Code) -> OpenRouter OpenAI.
Uso:
  OPENROUTER_KEY=sk-or-... python proxy_anthropic_openrouter.py
Luego en Claude Code:
  ANTHROPIC_BASE_URL=http://localhost:8081 ANTHROPIC_API_KEY=*** claude
"""
import os, json, httpx, uvicorn
from fastapi import FastAPI, Request

KEY = os.environ.get("OPENROUTER_KEY", "")
MODEL = os.environ.get("OPENROUTER_MODEL", "tencent/hy3:free")
OR_URL = "https://openrouter.ai/api/v1/chat/completions"

app = FastAPI()

@app.post("/v1/messages")
async def messages(req: Request):
    body = await req.json()
    sys_text = ""
    if body.get("system"):
        sys_text = body["system"] if isinstance(body["system"], str) else body["system"][0].get("text","")
    msgs = []
    if sys_text:
        msgs.append({"role": "system", "content": sys_text})
    for m in body.get("messages", []):
        role = m.get("role")
        content = m.get("content")
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            text = "".join(c.get("text","") for c in content if c.get("type")=="text")
        else:
            text = str(content)
        msgs.append({"role": role, "content": text})
    payload = {"model": MODEL, "messages": msgs,
               "max_tokens": body.get("max_tokens", 1024),
               "temperature": body.get("temperature", 0.7)}
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
               "HTTP-Referer": "https://localhost/claude-code", "X-Title": "claude-code-free"}
    r = httpx.post(OR_URL, json=payload, headers=headers, timeout=120)
    od = r.json()
    out = od["choices"][0]["message"]["content"]
    return {
        "id": od.get("id","proxy"), "type": "message",
        "role": "assistant", "model": MODEL,
        "content": [{"type": "text", "text": out}],
        "stop_reason": "end_turn", "usage": {"input_tokens": 0, "output_tokens": 0}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)
