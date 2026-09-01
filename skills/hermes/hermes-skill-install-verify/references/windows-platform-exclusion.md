# PITFALL: Windows platform exclusion (skill installed but invisible in `list`)

## Symptom
`hermes skills install official/research/searxng-search` says "Installed", but
`hermes skills list | grep searxng` returns NOTHING. The files exist on disk
(`%LOCALAPPDATA%\hermes\skills\searxng-search\SKILL.md`) yet the skill is not
shown as enabled.

## Root cause
The skill's SKILL.md frontmatter listed:
```
platforms: [linux, macos]
```
The Hermes skill loader filters out any skill whose `platforms` does not include
the current OS. On Windows the skill is silently excluded — it never reaches the
"enabled" bucket in `hermes skills list`.

## Diagnosis
Compare the installed skill against one that DOES show up:
```bash
sed -n '1,20p' "$LOCALAPPDATA/hermes/skills/searxng-search/SKILL.md"
sed -n '1,20p' "$LOCALAPPDATA/hermes/skills/duckduckgo-search/SKILL.md"
# duckduckgo shows: platforms: [linux, macos, windows]
# searxng showed:    platforms: [linux, macos]   <- missing windows
```

## Fix
Patch the frontmatter (use the `patch` tool, not a shell editor):
old: `platforms: [linux, macos]`
new: `platforms: [linux, macos, windows]`

Then confirm:
```bash
hermes skills list | grep -i searxng
# -> │ searxng-search │ official │ official │ enabled │
```

## Why this happens
Official/community skills authored on macOS/Linux often omit `windows` from
`platforms`, even when the underlying script (bash/curl/Python stdlib) runs fine
under Git-Bash on Windows. It is a metadata bug, not a capability gap.

## Verification note
After the patch, run the ad-hoc check in scripts/verify_skill_change.py adapted
to assert the skill appears in `hermes skills list`.
