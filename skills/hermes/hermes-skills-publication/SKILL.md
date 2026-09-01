---
category: hermes
name: hermes-skills-publication
description: "Publish a sanitized public GitHub mirror of Hermes skills."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, skills, github, publication, sanitize, secrets, showcase]
    related_skills: [hermes-config-versioning, hermes-skills-management, github]
---

# Hermes Skills Publication (sanitized public mirror)

## When to use
- User wants to publish/mirror their skills library (or agent config) to a public GitHub repo.
- User wants a "showcase" repo that highlights every skill and its qualities.
- User wants to share the agent's capabilities with a friend without sharing personal data.
- Refreshing an already-published skills collection after skills changed.

**Mental model: "clone of architecture, not content."** Copy HOW the agent is
structured (skills, procedures, capabilities), NOT WHAT it contains (personal
data, credentials, account details, machine paths).

## THE critical rule (learned the hard way)
**NEVER push the raw skills tree.** It contains venvs, embedded `.git` repos,
binaries, caches, AND hidden `.env` files with REAL credentials. On a real run:
- skills tree was **1.86 GB**, 34,084 non-markdown files, and 80+ skills
  referenced personal data (`Gio`, `<CIVITAI_USER>`, `C:\Users\<user>`).
- A `.env` with a **live credential** was copied into the mirror → GitHub
  **rejected the push** via secret scanning (`push declined due to repository
  rule violations`).
- Even **placeholder** tokens (`ghp_xx...xxxx`, `sk-xxx...xxxx`,
  `«redacted:ghp_…»`) trip GitHub's scanner because the prefix pattern matches.

Build a **curated, sanitized package** and push only that. See
`references/sanitize-and-publish.md` for the full worked example.

## Workflow (closed loop)

### 1. Measure before touching
```
SK="$LOCALAPPDATA/hermes/skills"
find "$SK" -name SKILL.md | wc -l          # true skill count (includes sub-cats)
du -sm "$SK" | cut -f1                     # total size (expect GBs)
grep -rlE "<USER>|<CIVITAI_USER>|<USER>|C:\\\\Users" "$SK" --include=*.md | wc -l  # personal-data blast radius
```
Report these numbers to the user up front — it justifies the curation approach.

### 2. Build a curated, sanitized copy (into a fresh dir, NEVER touching live skills)
- Copy only SKILL.md + scripts + references; exclude venvs, `.git`, `node_modules`,
  `__pycache__`, binaries >~5MB, `site-packages`, dist/build.
- **Sanitize text:** literal `.replace()` of personal tokens (`<USER>`,
  `<GITHUB_USER>`, `<CIVITAI_USER>`) — NOT regex on `C:\...` paths (raw-string
  `\U` escape bug: use forward-slash replace or drop the path patterns entirely,
  since replacing the username token catches every path form).
- **Aggressively drop any `.env` / `.env.*` files** (they hold real secrets).
- A reusable builder lives in `scripts/build_showcase.py` (adapt SRC/OUT paths).

### 3. Generate the showcase docs
- `CATALOG.md`: auto-generate a per-category table (Skill | Description) from
  every SKILL.md frontmatter. Parse `name:` + `description:` from the YAML block.
- `README.md`: hero header with shields (skills count, categories, license), a
  "why extraordinary" table, category→coverage table, install instructions.
- Add MIT `LICENSE` and a hardened `.gitignore`.

### 4. Secret-scan the package BEFORE the first commit
```
grep -rniE "ghp_[A-Za-z0-9]|gho_[A-Za-z0-9]|sk-[A-Za-z0-9]{8,}|AKIA[0-9A-Z]|BEGIN (RSA|OPENSSH|EC) PRIVATE|github_pat_" \
  --include=*.md --include=*.py --include=*.sh --include=*.txt --include=*.yaml \
  --include=*.yml --include=*.json --include=*.cfg .
```
- Real tokens → remove the file AND scrub it from history (see step 6).
- Placeholder `ghp_`/`sk-` prefixes in docs → neutralize to `<TOKEN>`.
- Scripts that merely *define* token prefixes to detect them (e.g. a
  `_TOKEN_PREFIXES = ("ghp_", ...)` constant) are legit code, not secrets.

### 5. Init, commit, create repo, push
```
cd <pkg> && git init -q && git add -A
git -c user.name="<USER>" -c user.email="<EMAIL>" commit -q -m "..."
gh repo create <name> --public --source=. --remote=origin --description "..."
git push -u origin HEAD
```
Ask the user to **confirm public visibility** before creating the repo (public is
irreversible). Offer public / private / custom-name.

### 6. If push is rejected by secret scanning
- GitHub's error prints the exact `commit` + `path:line`. Read it.
- A hidden `.env` is the usual culprit — find all with `find . -name ".env"`.
- **Scrub from history:** since the remote is empty (push was blocked), rewrite
  clean: `git update-ref -d HEAD && git add -A && git commit ... && git push`.
  (Only safe because nothing reached the remote.)
- Blind `.gitignore` with `.env`, `.env.*`, `!.env.example`, `*.pem`, `*.key`.
- Re-scan, commit, push again.

## Pitfalls
- **`git add -A` vs `.`**: use `.` — large dirs can trigger `mmap failed` on MSYS.
- **Skills tree is huge** (GBs) — always build to a separate staging dir, never
  `cp -r` the live tree into the repo.
- **Raw string `\U` regex bug:** `re.sub(r'C:\Users...')` throws
  `incomplete escape \U`. Use literal `.replace()` with forward-slash or the
  username token only.
- **Placeholder tokens still trip the scanner.** `«redacted:ghp_…»` is NOT
  enough — the `ghp_` prefix alone matches. Replace the whole token.
- **Read-before-overwrite**: after multiple sed/patch attempts, re-read the file
  — sed and patch can disagree about whether a change landed (CRLF vs LF).
- **Confirm the repo is empty before rewriting history** (step 6). If something
  already pushed, use `git filter-branch`/`filter-repo` instead.

## Verification (before declaring done)
- `git grep -il "<USER>\|<USER>\|<CIVITAI_USER>" -- .` → 0 matches.
- `git ls-files | grep -i "\.env$"` → empty.
- `find . -name ".env"` (outside .git) → empty.
- `gh repo view <name> --json visibility,url` → `public` + live URL.
- `git ls-tree -r HEAD --name-only | wc -l` → matches `git ls-files | wc -l`.
- Report: repo URL, file count, personal-data scan = 0, secrets = 0.

## Support files
- `references/sanitize-and-publish.md` — full worked example (real run: 251
  skills / 34 categories / 918 files / 12 MB from a 1.86 GB tree; the `.env`
  incident and token-placeholder trap in detail).
- `scripts/build_showcase.py` — reusable curated-copy + sanitize + catalog
  builder (adapt SRC/OUT paths, then run).
