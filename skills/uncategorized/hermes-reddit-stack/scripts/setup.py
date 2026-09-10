#!/usr/bin/env python3
"""
Setup idempotente del skill hermes-reddit-stack.
Recrea las rutas vivas de Hermes desde los scripts empaquetados:
- tools/ingest_venv + yt-dlp (uv)
- ~/.hermes/scripts/morning_digest.py  (para el cron)
- docs/ y second-brain/ si faltan
Es seguro correr varias veces.
"""
from __future__ import annotations
import os, shutil, subprocess, sys
from pathlib import Path

HERMES = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes"
HOME = Path(os.environ.get("USERPROFILE", "") or Path.home())
SKILL = HERMES / "skills" / "hermes-reddit-stack"
SCRIPTS = SKILL / "scripts"

def run(cmd, **kw):
    print(">", " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, **kw)

def main():
    # 1) venv aislado + yt-dlp
    venv = HERMES / "tools" / "ingest_venv"
    if not (venv / "Scripts" / "yt-dlp.exe").exists():
        run([sys.executable, "-m", "venv", str(venv)], check=False)
        run(["uv", "pip", "install", "--python", str(venv / "Scripts" / "python.exe"), "yt-dlp"], check=False)
    else:
        print("[setup] yt-dlp venv ya existe, skip")

    # 2) copiar morning_digest.py a ~/.hermes/scripts para el cron
    home_scripts = HOME / ".hermes" / "scripts"
    home_scripts.mkdir(parents=True, exist_ok=True)
    dst = home_scripts / "morning_digest.py"
    if not dst.exists() or dst.read_text(encoding="utf-8", errors="ignore") != \
       (SCRIPTS / "morning_digest.py").read_text(encoding="utf-8", errors="ignore"):
        shutil.copy(SCRIPTS / "morning_digest.py", dst)
        print(f"[setup] copiado {dst}")
    else:
        print("[setup] morning_digest.py ya actualizado, skip")

    # 3) carpetas de datos
    for d in [HERMES / "docs", HERMES / "second-brain" / "zettel"]:
        d.mkdir(parents=True, exist_ok=True)
        print(f"[setup] asegura {d}")

    # 4) backup-state.sh a la raiz de hermes si falta
    bs = HERMES / "backup-state.sh"
    if not bs.exists():
        shutil.copy(SCRIPTS / "backup-state.sh", bs)
        print("[setup] copiado backup-state.sh")

    print("[setup] OK. Falta crear el cron (requiere auth):")
    print('  cronjob(action="create", name="Hermes morning digest", schedule="0 8 * * *", script="morning_digest.py", prompt="Corre morning_digest.py")')

if __name__ == "__main__":
    main()
