---
category: github
name: publish-sanitized-collection
description: "Publish sanitized Hermes skills to GitHub as showcase."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, skills, publish, sanitize, secrets, collection]
    related_skills: [hermes-config-versioning, hermes-skills-management, github-repo-management]
---

# Publish a Sanitized Collection to GitHub

## When to use
- User wants to publish their Hermes skill library (or SOUL.md / config) as a
  public GitHub repo — a "showcase" or "vitrina".
- User wants a mirror clone of skills to share with a friend/colleague WITHOUT
  their personal data.
- Any task that ships a folder of Hermes config/skills to GitHub publicly.

## Principle
Clone **architecture, not content**: copy SKILL.md + useful scripts, never the
raw tree. A public repo exposes everything you push — sanitize BEFORE committing.

## Why NOT push the raw tree
`$LOCALAPPDATA/hermes/skills` is huge and full of junk:
- ~1.8 GB (venvs, embedded git repos, binaries, caches)
- 34,000+ non-markdown files
- ~80 skills carrying personal data (usernames, account names, `C:\Users\<user>` paths)

## Build a curated package (script in `$HOME`)
1. **Catalog**: walk `skills/<cat>/<skill>/SKILL.md`, extract `name`+`description`
   from YAML frontmatter → `.catalog.json`.
2. **Copy sanitizing**: rewrite every file, swapping personal tokens for
   placeholders, into `$HOME/<collection>/skills/<cat>/...`.
3. **Exclude junk**: `.git`, `.venv`, `venv`, `node_modules`, `__pycache__`,
   `.curator_backups`, `.hub`, files >5MB, `*.pyc`.
4. **Generate README** (hero/"vitrina" page + badges + install instructions) and
   **CATALOG.md** (auto-generated per-category tables).

## Sanitization — critical
Use **literal `str.replace`**, NOT regex with backslashes:
- A pattern `C:\Users\...` written with a bare backslash inside a Python
  `r''`/string breaks with `SyntaxError: (unicode error) 'unicodeescape'`.
  Just replace the user token globally (`<USER>` → `<USER>`), which catches
  every path form.
- Placeholders: `<USER>`→`<USER>`, `<CIVITAI_USER>`→`<CIVITAI_USER>`,
  `<GITHUB_USER>`→`<GITHUB_USER>`.

## GitHub secret-scanning blocks the push (hard pitfall)
First push fails: `! [remote rejected] ... push declined due to repository rule
violations` + a secret-scanning URL. GitHub scans the WHOLE commit content, not
just real `.env`. It fires on:
- **Placeholders** like `ghp_xx...xxxx` / `sk-xxx...xxxx` in docs (match the pattern)
- **Real `.env`** files that leaked into the copy

### Diagnose what's blocking
1. The remote message may name the exact file (`path: skills/.../.env:1`).
2. `find skills -name ".env"` → delete any.
3. `grep -rniE "ghp_|sk-|AKIA" <dir>` → neutralize docs placeholders to `<TOKEN>`.
4. Note: `read_file` refuses `.env` (defense-in-depth) — inspect via `terminal`.

### Remove the secret from HISTORY
A committed `.env` still blocks even after deleting it from the working dir —
GitHub inspects history. If the push NEVER succeeded (remote empty), rewrite
history safely:

```bash
git update-ref -d HEAD          # discard local commits
git add -A                      # re-add all (now .env-free)
git commit -m "..."             # single clean commit
git push -u origin HEAD
```

Verify before pushing: `git ls-files | grep -i "\.env$"` empty, and
`git grep -il "<USER>\|<CIVITAI_USER>" -- .` empty.

### Harden .gitignore
```gitignore
.env
.env.*
!.env.example
*.pem
*.key
```

## Final verification (worked example 2026-08-31)
- Package: ~12 MB (from 1.8 GB), 260 SKILL.md, 915 files, 0 personal data.
- Repo: `gh repo create <name> --public --source=. --remote=origin` → push OK.
- 251 skills cataloged across 34 categories.

## Pitfalls
- Don't `git add -A` on the ORIGINAL huge tree (mmap failures) — work in the
  small curated package dir.
- Back up the original SOUL.md/skills before any edit; never edit originals to
  build the mirror — copy out, don't touch source.
- Always confirm public/private with the user before `gh repo create --public` —
  publishing is irreversible once pushed.
