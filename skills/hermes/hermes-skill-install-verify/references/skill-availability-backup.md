# Skill-availability backup (Pitfall 6)

## When
User asks to preserve a hub skill "por si ya no llega a estar disponible" — i.e.
insurance against the hub removing/renaming it. Real case: `mt5-trading-assistant-pro`
and `oanda-forex-trading` preserved into `~/skills-backup-forex/`.

## Steps
```bash
# 1) install (non-interactive)
echo y | hermes skills install "clawhub/<id>"

# 2) copy to an EXTERNAL dir, NOT under %LOCALAPPDATA%\hermes\skills\
BACKUP="$HOME/skills-backup-<topic>"
mkdir -p "$BACKUP"
cp -r "$LOCALAPPDATA/hermes/skills/<id>" "$BACKUP/"

# 3) verify the copy contains the key files
find "$BACKUP" -name SKILL.md
```

## Restore later
```bash
cp -r "$HOME/skills-backup-<topic>/<id>" "$LOCALAPPDATA/hermes/skills/<id>"
```
Then on Windows confirm `platforms:` in the copied SKILL.md frontmatter includes
`windows` (see Pitfall 1), or it won't appear as enabled in `hermes skills list`.

## Caveats
- A backup is just files. It does NOT keep the skill "enabled" on its own.
- For broker-connected skills (MT5/OANDA), the backup includes docs only — no
  credentials are stored in the skill folder. Never put API keys in the backup.
- Re-run `hermes skills list | grep -i <id>` after restore to confirm it loads.
