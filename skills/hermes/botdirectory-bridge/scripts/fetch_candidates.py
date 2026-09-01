import argparse, json, urllib.request

API = "https://api.botdirectory.ai/api/bots"

def fetch(limit):
    req = urllib.request.Request(
        f"{API}?limit={limit}",
        headers={"User-Agent": "hermes-botdirectory-bridge", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def main():
    ap = argparse.ArgumentParser(description="Busca candidatos en botdirectory.ai")
    ap.add_argument("--query", default="", help="filtro por nombre/integraciones/prompt")
    ap.add_argument("--limit", type=int, default=10, help="cuantos bots traer del catalogo")
    ap.add_argument("--full", action="store_true", help="mostrar prompt completo (600 chars)")
    a = ap.parse_args()

    data = fetch(a.limit)
    bots = data.get("bots", data if isinstance(data, list) else [])
    q = a.query.lower()
    hits = []
    for b in bots:
        blob = " ".join([
            b.get("name", ""), b.get("category", ""),
            " ".join(b.get("integrations", []) or []), b.get("prompt", ""),
        ]).lower()
        if not q or q in blob:
            hits.append(b)

    print(f"Catalogo traido: {len(bots)} | Coinciden con '{a.query}': {len(hits)}")
    for b in hits:
        print("-" * 70)
        print(f"{b.get('name')}  [{b.get('category')}]")
        print(f"  integraciones: {', '.join(b.get('integrations', []) or ['-'])}")
        print(f"  contributor: {b.get('contributor')}  |  detalle: {b.get('detailUrl')}")
        prompt = b.get("prompt", "")
        print(f"  prompt: {prompt[:600] if a.full else prompt[:150]}...")

if __name__ == "__main__":
    main()
