#!/usr/bin/env python3
"""
Paso 8 (nivel medio): ingiere URL/YouTube, transcribe (VTT) y resume a markdown,
guardando un zettel en second-brain/zettel/ y registrando en el indice.

Reusa scripts del skill watch-video (download.py, transcribe.py).
No instala nada en el venv de Hermes; usa tools/ingest_venv (yt-dlp).

Uso:
  python ingest_url.py "<URL>" [--model tencent/hy3:free] [--no-summary]
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, datetime
from pathlib import Path

HERMES = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes"
WATCH = HERMES / "skills" / "watch-video" / "scripts"
YTDLP = HERMES / "tools" / "ingest_venv" / "Scripts" / "yt-dlp.exe"
SECOND = HERMES / "second-brain"
ZETTEL = SECOND / "zettel"

def slug(s: str) -> str:
    s = s.lower().strip()
    for c in " /\\:?*\"<>|":
        s = s.replace(c, "-")
    return s[:60].strip("-")

def download(url: str, tmp: Path) -> dict:
    # Poner el venv aislado (yt-dlp) al frente del PATH para que watch-video lo encuentre
    venv_scripts = str(YTDLP.parent)
    os.environ["PATH"] = venv_scripts + os.pathsep + os.environ.get("PATH", "")
    sys.path.insert(0, str(WATCH))
    import download as dl
    return dl.download(url, tmp)

def transcribe_vtt(vtt_path: str) -> str:
    sys.path.insert(0, str(WATCH))
    import transcribe as tr
    return tr.format_transcript(tr.parse_vtt(vtt_path))

def summarize(text: str, model: str) -> str:
    """Resume usando el CLI de Hermes (modelo por defecto del agente)."""
    prompt = ("Resume el siguiente contenido en markdown breve para un 'segundo cerebro'. "
              "Formato:\n## Qué dice\n- ...\n## Puntos clave\n- ...\n## Conexiones / accionable\n- ...\n\nCONTENIDO:\n")
    # Usa el ejecutable hermes para no acoplar a un modelo especifico
    hermes_exe = HERMES / "hermes-agent" / "venv" / "Scripts" / "hermes.exe"
    if hermes_exe.exists():
        try:
            out = subprocess.run([str(hermes_exe), "chat", "-q", prompt + text[:12000], "-Q"],
                                 capture_output=True, text=True, timeout=180)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except Exception as e:
            print(f"[ingest] hermes chat fallback: {e}", file=sys.stderr)
    return text[:2000]  # fallback: recorte si no hay CLI

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--model", default="tencent/hy3:free")
    ap.add_argument("--no-summary", action="store_true")
    args = ap.parse_args()

    tmp = HERMES / "cache" / "ingest_tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    print(f"[ingest] descargando {args.url} ...")
    info = download(args.url, tmp)
    transcript = ""
    if info.get("subtitle_path"):
        print("[ingest] transcribiendo subtitulos ...")
        transcript = transcribe_vtt(info["subtitle_path"])
    title = (info.get("info", {}) or {}).get("title") or args.url
    url = (info.get("info", {}) or {}).get("url") or args.url

    if args.no_summary or not transcript:
        body = transcript or f"Enlace guardado sin transcripcion: {url}"
    else:
        print("[ingest] resumiendo ...")
        body = summarize(transcript, args.model)

    ZETTEL.mkdir(parents=True, exist_ok=True)
    date = datetime.date.today().isoformat()
    fname = f"{date}-ingest-{slug(title)}.md"
    path = ZETTEL / fname
    path.write_text(f"# {title}\n\n- Fuente: {url}\n- Ingestado: {date}\n\n{body}\n",
                    encoding="utf-8")

    # registrar en indice
    idx = SECOND / "README.md"
    with idx.open(encoding="utf-8") as f:
        lines = f.read().splitlines()
    lines.append(f"- {date}-ingest-{slug(title)}.md — ingest de {url}")
    idx.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[ingest] zettel creado: {path}")

if __name__ == "__main__":
    main()
