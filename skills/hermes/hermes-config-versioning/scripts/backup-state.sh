#!/usr/bin/env bash
# ============================================================
# Hermes Agent - backup de ESTADO y SECRETOS (no versionables en git)
# Uso:  bash backup-state.sh
# Crea un .tar.gz en ./backups/ con config.yaml, .env, auth.json,
# kanban.db, state.db, memories y caches volatiles.
# Esta carpeta backups/ esta en .gitignore (NO va a git).
# ============================================================
set -euo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
OUT="$BASE/backups"
mkdir -p "$OUT"
STAMP="$(date +%Y%m%d_%H%M%S)"
ARCH="$OUT/hermes-state-$STAMP.tar.gz"

# Lista de rutas a respaldar (solo las que existan)
paths=()
for p in config.yaml .env auth.json kanban.db state.db \
         memories MEMORY.md USER.md; do
  [ -e "$BASE/$p" ] && paths+=("$p")
done

echo "Respaldando: ${paths[*]}"
tar -czf "$ARCH" -C "$BASE" "${paths[@]}" 2>/dev/null || {
  # fallback sin compression si tar falla (mmap en MSYS)
  tar -cf "${ARCH%.gz}" -C "$BASE" "${paths[@]}"
  ARCH="${ARCH%.gz}"
}
echo "Backup listo: $ARCH  ($(du -h "$ARCH" | cut -f1))"
echo "Recuerda copiar ./backups/ a tu nube/disco externo. NO esta en git."
