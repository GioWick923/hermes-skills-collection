#!/usr/bin/env bash
# AD-HOC VERIFICATION for Hermes git-config work (not a test suite).
set -uo pipefail
REPO="${LOCALAPPDATA:-$HOME/AppData/Local/hermes}/hermes"
cd "$REPO" 2>/dev/null || { echo "FAIL: no repo"; exit 1; }
rm -f .git/index.lock 2>/dev/null

echo "=== A) working tree limpio? ==="
st="$(git status --porcelain)"
[ -z "$st" ] && echo "PASS: limpio" || { echo "FAIL: sucio"; echo "$st"; }

echo "=== B) cron ticker runtime EXCLUIDO ==="
for f in cron/ticker_heartbeat cron/ticker_last_success; do
  git check-ignore -q "$f" && echo "PASS ignorado: $f" || echo "FAIL NO ignorado: $f"
done

echo "=== C) secretos excluidos ==="
for f in .env config.yaml auth.json state.db kanban.db tools/x sessions/x backups/z.tar.gz; do
  git check-ignore -q "$f" && echo "PASS: $f" || echo "FAIL: $f"
done

echo "=== D) lo util NO ignorado ==="
for f in skills/creative/SKILL.md profiles/builder/SOUL.md memories/MEMORY.md backup-state.sh .gitignore; do
  git check-ignore -q "$f" && echo "FAIL mal: $f" || echo "PASS: $f"
done

echo "=== E) backup-state.sh produce tar valido ==="
arch="$(ls -t backups/hermes-state-*.tar.gz 2>/dev/null | head -1)"
if [ -n "$arch" ] && tar -tzf "$arch" >/dev/null 2>&1; then echo "PASS backup valido $(du -h "$arch"|cut -f1)"; else echo "FAIL backup"; fi

echo "=== FIN VERIFICACION AD-HOC (no suite) ==="
