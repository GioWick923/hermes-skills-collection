#!/usr/bin/env python3
"""
ornith_proxy_template.py — Puente harness-de-agentes ↔ llama.cpp local.

Inyecta chat_template_kwargs.enable_thinking=false en cada request (sin esto,
modelos Qwen3.5/DeepSeek-family gastan todos los tokens en reasoning y responden vacío)
y reenvía a llama.cpp. Soporta streaming SSE (los harnesses usan stream:true;
devolver JSON completo los cuelga).

Uso:
    python ornith_proxy_template.py [--port 8081] [--upstream http://127.0.0.1:8080]

Validado en 2026-08-20: DSH headless + Ornith-1.5-9B-uncensored Q5_K_M.
"""

import argparse
import json
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "http://127.0.0.1:8080"


class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass  # silencioso

    def _do_proxy(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else b""

        # Inyectar enable_thinking=false (crítico para Qwen3.5/DeepSeek-family)
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except json.JSONDecodeError:
            payload = {}
        payload.setdefault("chat_template_kwargs", {})["enable_thinking"] = False
        body = json.dumps(payload).encode("utf-8")

        is_stream = payload.get("stream", False)

        req = urllib.request.Request(
            UPSTREAM + "/v1/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": self.headers.get("Accept", "application/json"),
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                if is_stream:
                    # Reenviar SSE tal cual, chunk a chunk
                    self.send_response(resp.status)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache")
                    self.end_headers()
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
                else:
                    data = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
        except Exception as e:
            err = json.dumps({"error": {"message": str(e), "type": "proxy_error"}}).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)

    def do_POST(self):
        if self.path.rstrip("/").endswith("/chat/completions"):
            self._do_proxy()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        # /health y /models para que el harness pueda sondear
        if self.path.rstrip("/").endswith("/health"):
            data = json.dumps({"status": "ok"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif self.path.rstrip("/").endswith("/models"):
            data = json.dumps({"data": [{"id": "local-model"}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()


def main():
    global UPSTREAM
    ap = argparse.ArgumentParser(description="Proxy local-model con thinking-off")
    ap.add_argument("--port", type=int, default=8081)
    ap.add_argument("--upstream", default="http://127.0.0.1:8080")
    args = ap.parse_args()
    UPSTREAM = args.upstream

    server = ThreadingHTTPServer(("127.0.0.1", args.port), ProxyHandler)
    print(f"proxy: escuchando :{args.port} → {UPSTREAM} (enable_thinking=false inyectado)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
