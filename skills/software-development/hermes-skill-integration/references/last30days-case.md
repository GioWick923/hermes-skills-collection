# Worked Case: integrating `last30days` (mvanhorn/last30days-skill)

Date: 2026-07-11 · Host: Windows 10 · Hermes v0.17.0 · Python host: 3.11.15 · uv: present

## What the skill is
`last30days` = multi-source "what people actually say in the last 30 days" research engine.
Free sources (no key): Reddit, HN, Polymarket, YouTube (yt-dlp), Digg.
Key sources: X/Twitter (XAI_API_KEY or browser cookies; Windows = Firefox only),
TikTok/Instagram (ScrapeCreators), web search (Brave). Has a `--diagnose` doctor.

## Install
```
hermes skills install mvanhorn/last30days-skill/skills/last30days --force
```
`--force` required: Hermes security scanner returns `caution` for reading API keys from env
and calling `subprocess` (yt-dlp / bird). `--force` accepts the verdict.

## BUG 1 — incomplete snapshot (the important one)
After install, `engine --help` crashed:
```
ModuleNotFoundError: No module named 'lib.query'
  at lib/github.py line 21:  from .query import extract_core_subject
```
Diff repo vs installed showed the install landed **76/78** `lib/*.py` files — missing exactly:
- `scripts/lib/query.py`
- `scripts/lib/reddit.py`

Fix (repair, NOT rewrite — hub skill is protected):
```bash
SRC=/tmp/last30days-skill/skills/last30days
DST="$LOCALAPPDATA/hermes/skills/last30days"
cp "$SRC/scripts/lib/query.py" "$DST/scripts/lib/query.py"
cp "$SRC/scripts/lib/reddit.py" "$DST/scripts/lib/reddit.py"
rm -rf "$DST/scripts/lib/__pycache__"     # drop stale bytecode from the failed import
```

## BUG 2 — Python 3.12 gate
Engine refused on 3.11.15 with `last30days v3 requires Python 3.12+.` Host had only 3.11.
Fix via uv (no system change):
```bash
uv python install 3.12
P312="$(uv python find '>=3.12')"    # -> .../uv/python/cpython-3.12-windows-x86_64-none/python.exe
```
Note: the skill's own preflight already does this uv fallback (sets LAST30DAYS_PYTHON), so just
having uv + 3.12 provisioned is enough; we invoked explicitly to verify.

## Proof it runs (mock, no network)
```bash
export LAST30DAYS_PYTHON="$(uv python find '>=3.12')"
cd "$LOCALAPPDATA/hermes/skills/last30days/scripts"
"$LAST30DAYS_PYTHON" last30days.py "AI video tools reaction" --mock --emit=compact
# exit 0; emits badge "🌐 last30days v3.11.1 · synced 2026-07-11" + canonical footer
```

## How the agent uses it for the user
On a request like "last30days what people say about Cursor vs Claude Code": load skill,
generate a JSON query plan (mandatory for named-entity topics — LAW 7), run the engine with
`LAST30DAYS_PYTHON`, pass the badge + footer through verbatim, synthesize the body in the
canonical voice (no trailing `Sources:` block — LAW 1). Free sources work immediately;
X/TikTok/Instagram need keys or Firefox cookies.
