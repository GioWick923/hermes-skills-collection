#!/usr/bin/env python3
# Helper del skill voice-idea-to-doc: guarda un documento markdown en docs/.
# Uso: python save_doc.py --title "Plan viaje" --body-file cuerpo.md [--date 2026-07-12]
import sys, os, argparse, datetime
BASE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", "docs")

def slugify(s):
    s = s.lower().strip()
    for c in " /\\:?*\"<>|":
        s = s.replace(c, "-")
    return s[:60].strip("-")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    args = ap.parse_args()
    os.makedirs(BASE, exist_ok=True)
    with open(args.body_file, encoding="utf-8") as f:
        body = f.read()
    fname = f"{args.date}-{slugify(args.title)}.md"
    path = os.path.join(BASE, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {args.title}\n\n{body}\n")
    print(path)

if __name__ == "__main__":
    main()
