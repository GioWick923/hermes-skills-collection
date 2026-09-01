#!/usr/bin/env bash
# audit_hermes.sh — Self-audit del ecosistema Hermes (watchdog pattern).
# Imprime un reporte markdown por stdout; Hermes lo entrega por Telegram.
# Diseñado para correr como cron no_agent (sin costo de tokens por run).
# Reusable desde el skill hermes-self-audit.
set -u

HERMES_DIR="${LOCALAPPDATA:-$HOME/AppData/Local}/hermes"
cd "$HERMES_DIR" || { echo "ERROR: no se pudo entrar a $HERMES_DIR"; exit 1; }

ts=$(date '+%Y-%m-%d %H:%M')
issues=0
warn=0

# --- 1. Git hygiene ---
dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [ "$dirty" -gt 0 ]; then
  git_state="SUCIO ($dirty archivos sin commitear)"
  warn=$((warn+1))
else
  git_state="LIMPIO"
fi

# --- 2. Config backup clutter ---
bak_count=$(ls config.yaml*.bak* 2>/dev/null | wc -l | tr -d ' ')
if [ "$bak_count" -gt 3 ]; then
  bak_state="ACUMULACION ($bak_count bak; limpiar)"
  warn=$((warn+1))
else
  bak_state="OK ($bak_count)"
fi

# --- 3. Skills integrity (cuenta SKILL.md reales, nivel 1 o 2) ---
# PITFALL: no usar -mindepth/-maxdepth fijos; eso da falsos positivos.
skill_ok=$(find skills -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$skill_ok" -gt 0 ]; then
  skill_state="OK ($skill_ok skills con SKILL.md)"
else
  skill_state="SIN SKILLS"
  issues=$((issues+1))
fi

# --- 4. Cron jobs ---
jobs_json=$(python - "$HERMES_DIR/cron/jobs.json" <<'PY'
import json,sys
try:
    data=json.load(open(sys.argv[1]))
    jobs=data if isinstance(data,list) else data.get('jobs',[])
    out=[]
    for j in jobs:
        nx=j.get('next_run_at') or 'n/a'
        sched=j.get('schedule','?')
        out.append(f"{j.get('name','?')}|{'ON' if j.get('enabled') else 'OFF'}|{sched}|{nx}")
    print("\n".join(out))
except Exception as e:
    print("ERR:"+str(e))
PY
)
job_lines=$(echo "$jobs_json" | grep -c '|' || true)
disabled=$(echo "$jobs_json" | grep -c '|OFF|' || true)
[ "$disabled" -gt 0 ] && warn=$((warn+1))

# --- 5. Memory usage ---
mem_file="$HERMES_DIR/memories/MEMORY.md"
if [ -f "$mem_file" ]; then
  mem_chars=$(wc -m < "$mem_file" | tr -d ' ')
  mem_pct=$((mem_chars*100/2200))
  if [ "$mem_pct" -ge 85 ]; then
    mem_state="CRITICO ($mem_chars/2200 chars, $mem_pct%)"
    issues=$((issues+1))
  else
    mem_state="$mem_chars/2200 chars ($mem_pct%)"
  fi
else
  mem_state="SIN MEMORY.md"
fi

# --- 6. State db size ---
db_size=$(du -m "$HERMES_DIR/state.db" 2>/dev/null | cut -f1)
db_state="${db_size}MB"

# --- 7. Second brain / gbrain ---
if [ -d "$HERMES_DIR/second-brain" ]; then
  sb_notes=$(find "$HERMES_DIR/second-brain" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  sb_state="$sb_notes notas"
else
  sb_state="no presente"
fi

# --- Veredicto ---
if [ "$issues" -gt 0 ]; then verdict="REVISAR (errores criticos: $issues)";
elif [ "$warn" -gt 0 ]; then verdict="OK CON ADVERTENCIAS ($warn)";
else verdict="SALUDABLE"; fi

# --- Reporte ---
echo "## 🔍 Auditoría Hermes — $ts"
echo
echo "**Veredicto:** $verdict"
echo
echo "| Área | Estado |"
echo "|------|--------|"
echo "| Git (versionado) | $git_state |"
echo "| Backups config | $bak_state |"
echo "| Skills | $skill_state |"
echo "| Cron jobs | $job_lines total / $disabled deshabilitados |"
echo "| Memoria | $mem_state |"
echo "| state.db | $db_state |"
echo "| Second brain | $sb_state |"
echo
if [ -n "$jobs_json" ]; then
  echo "**Crons:**"
  while IFS='|' read -r n e s nx; do
    [ -z "$n" ] && continue
    echo "- $n — $e — $s — próximo: $nx"
  done <<< "$jobs_json"
  echo
fi
echo "Generado por audit_hermes.sh (cron self-audit)."
