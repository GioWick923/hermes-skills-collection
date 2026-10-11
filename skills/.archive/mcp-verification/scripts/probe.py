"""
Direct JSON-RPC probe for HTTP MCP servers.
Lets you verify connectivity AND authentication even when the
native mcp_<server>_* tools are not yet in the session schema
(Hermes hasn't been restarted after adding the server, or you're mid-session).

Usage:
    python probe.py
Edit URL / KEY / TOOL below.
"""
import json, urllib.request

URL = "https://mcp.trader.dev/mcp"          # <-- MCP endpoint
KEY = "REPLACE_WITH_YOUR_API_KEY"           # <-- Bearer token; never put in URL
TOOL = "whoami"                             # auth check tool; or "list_strategies"

H = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "Authorization": "Bearer " + KEY,
    # Cloudflare-fronted endpoints 403 Python's default UA. Use a browser UA.
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
}

def rpc(method, params=None, rid=1):
    body = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        body["params"] = params
    if not method.startswith("notifications/"):
        body["id"] = rid
    data = json.dumps(body).encode()
    req = urllib.request.Request(URL, data=data, headers=H, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        sid = r.headers.get("mcp-session-id")
        if sid and "mcp-session-id" not in H:
            H["mcp-session-id"] = sid          # echo for subsequent calls
        raw = r.read().decode()
    for line in raw.splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:].strip())
    return None

def main():
    init = rpc("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "mcp-verification-probe", "version": "1.0"},
    }, rid=1)
    print("INIT server:", init["result"]["serverInfo"])
    rpc("notifications/initialized")
    res = rpc("tools/call", {"name": TOOL, "arguments": {}}, rid=2)
    print("AUTH CALL", TOOL, "=>")
    print(json.dumps(res.get("result", res), indent=2)[:1200])

if __name__ == "__main__":
    main()
