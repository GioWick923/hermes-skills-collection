#!/usr/bin/env python3
"""
Digest matutino (Paso 8): lee zettels nuevos desde ayer en second-brain/zettel/,
genera un resumen y lo manda por Telegram al DM de Gio via el CLI de Hermes.

Uso (pensado para cron):
  python morning_digest.py
"""
from __future__ import annotations
import os, subprocess, sys, datetime
from pathlib import Path

HERMES = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes"
ZETTEL = HERMES / "second-brain" / "zettel"
HERMES_EXE = HERMES / "hermes-agent" / "venv" / "Scripts" / "hermes.exe"
TELEGRAM_TARGET = "Gio"  # nombre en channel_directory.json (dm)

def main():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    nuevos = []
    for f in sorted(ZETTEL.glob("*.md")):
        try:
            d = datetime.date.fromisoformat(f.name[:10])
        except Exception:
            continue
        if d >= yesterday:
            nuevos.append(f)
    if not nuevos:
        print("[digest] nada nuevo desde ayer")
        return
    bloques = []
    for f in nuevos:
        txt = f.read_text(encoding="utf-8", errors="ignore")
        bloques.append(f"### {f.stem}\n{txt[:800]}")
    resumen = "\n\n".join(bloques)
    mensaje = (f"🌅 Digest matutino ({today.isoformat()})\n"
               f"Tienes {len(nuevos)} nota(s) nueva(s) en tu segundo cerebro:\n\n{resumen}")
    if HERMES_EXE.exists():
        # Enviar por Telegram con 'hermes send -t telegram'
        try:
            r = subprocess.run([str(HERMES_EXE), "send", "-t", "telegram", mensaje],
                               capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                print("[digest] enviado por telegram")
                return
            print(f"[digest] send fallo rc={r.returncode}: {r.stderr[:200]}", file=sys.stderr)
        except Exception as e:
            print(f"[digest] error send: {e}", file=sys.stderr)
        print(mensaje)
    else:
        print(mensaje)

if __name__ == "__main__":
    main()
