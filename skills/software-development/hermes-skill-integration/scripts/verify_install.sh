#!/usr/bin/env bash
# verify_install.sh — list runtime files present in the cloned repo skill but MISSING
# from the installed skill dir. Catches incomplete `hermes skills install` snapshots.
#
# Usage:
#   ./verify_install.sh <repo_skill_root> <installed_skill_dir>
#
#   repo_skill_root     : path to the skill root in your git clone (the dir holding SKILL.md)
#   installed_skill_dir : path under ~/.hermes/skills/<name>
#
# Exit code 0 if nothing missing; 1 if any runtime file is missing (printed to stdout).
set -euo pipefail

REPO="${1:-}"
INST="${2:-}"
if [ -z "$REPO" ] || [ -z "$INST" ]; then
  echo "Usage: verify_install.sh <repo_skill_root> <installed_skill_dir>" >&2
  exit 2
fi

repofile="$(mktemp)"
instfile="$(mktemp)"
trap 'rm -f "$repofile" "$instfile"' EXIT

( cd "$REPO" && find . -type f -not -path './.git/*' | sort ) > "$repofile"
( cd "$INST" && find . -type f | sort ) > "$instfile"

missing="$(comm -23 "$repofile" "$instfile")"
if [ -z "$missing" ]; then
  echo "OK: installed tree contains all repo files."
  exit 0
fi

echo "MISSING from install (present in repo):"
echo "$missing"
echo
echo "Copy these into: $INST"
exit 1
