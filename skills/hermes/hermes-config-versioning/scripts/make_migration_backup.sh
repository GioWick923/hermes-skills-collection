#!/usr/bin/env bash
# Hermes PC-migration backup builder — captures BOTH live locations.
# Run in BACKGROUND (skills dir is large, 2-5 min). Lands in ~/Pictures.
set -e
TS=$(date +%Y%m%d_%H%M%S)
OUT="$HOME/Pictures/HermesMigration_${TS}.tar.gz"
TMP="/tmp/hermes_mig_${TS}"
mkdir -p "$TMP"

echo "[1/4] AppData\\Local\\hermes ..."
tar -cf "$TMP/appdata.tar" -C "$LOCALAPPDATA" hermes 2>/dev/null || echo "  (some files skipped)"

echo "[2/4] ~/.hermes dotfiles (agent-reach, .opencli, .twitter-cli, .gbrain) ..."
tar -cf "$TMP/home.tar" -C "$HOME" \
  .hermes .agent-reach .opencli .twitter-cli .gbrain .blogwatcher-cli .mcporter 2>/dev/null || echo "  (some skipped)"

echo "[3/4] manifest ..."
cat > "$TMP/manifest.txt" <<EOF
Hermes Migration Backup
Generated: $(date)
Layout: AppData\\Local\\hermes (live) + ~/.hermes dotfiles
Restore: tar -xzf -> appdata.tar + home.tar; tar -xf appdata.tar -C /c/Users/<U>/AppData/Local/ ; tar -xf home.tar -C /c/Users/<U>/
EOF

echo "[4/4] compress ..."
tar -czf "$OUT" -C "$TMP" appdata.tar home.tar manifest.txt
rm -rf "$TMP"
echo "DONE: $OUT"; ls -lh "$OUT"
