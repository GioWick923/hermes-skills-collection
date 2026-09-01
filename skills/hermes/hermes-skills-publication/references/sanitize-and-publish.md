# Sanitize & Publish — full worked example

Real run that produced this skill (verified, 2026-08-31).

## Source state (before anything)
```
$LOCALAPPDATA/hermes/skills/
  SKILL.md files (recursive): 368
  total tree size:            1.86 GB
  non-markdown files:         34,084  (venvs, embedded .git, binaries, caches)
  skills w/ personal data:    80      (matched Gio, <CIVITAI_USER>, C:\Users\<user>)
```
→ Raw push would be a 1.8 GB repo full of junk that leaks personal data.

## What the curated package looked like after build
```
SKILL.md in package:  260
total files:          918
package size:         12 MB    (from a 1.86 GB tree)
catalogued skills:    251      (deduped, unique paths)
categories:           34
```

## The .env incident (GitHub push rejected)
- `git push` → `! [remote rejected] HEAD -> master (push declined due to
  repository rule violations)`.
- GitHub's error names the exact offender: `commit: <sha> path: skills/data/
  langextract-structured/.env:1`. The skill folder carried a **live `.env`**
  with a real credential into the mirror.
- Fix:
  1. `rm -f skills/data/langextract-structured/.env`
  2. Check history: `git log --oneline -- skills/data/langextract-structured/.env`
  3. Since the remote was empty (push blocked), rewrite clean:
     `git update-ref -d HEAD && git add -A && git commit ... && git push`
     (this drops the polluted commit entirely — safe only when nothing reached remote).
  4. Blind `.gitignore`:
     ```
     .env
     .env.*
     !.env.example
     *.pem
     *.key
     ```
  5. Re-verified `git ls-files | grep -i "\.env$"` → empty → push succeeded.

## The placeholder-token trap
- Even redacted/placeholder tokens trip GitHub's scanner because the PREFIX
  matches:
  - `ghp_xx...xxxx`, `sk-xxx...xxxx`, `«redacted:ghp_…»`, `sk-xxxxxxxxxxxxxxxxxxxx`.
- `«redacted:ghp_…»` is NOT enough — replace the whole token with `<TOKEN>`.
- Neutralize all forms:
  ```
  sed -i 's/ghp_[A-Za-z0-9_\.…]*/<TOKEN>/g; s/sk-[A-Za-z0-9_\.…]*/<TOKEN>/g' <file>
  ```
  or a python pass with regex `ghp_[A-Za-z0-9_\.…]{2,}` / `sk-[A-Za-z0-9_\.…]{2,}`.
- Legit exception: a script that DEFINES token prefixes to detect them
  (`_TOKEN_PREFIXES = ("ghp_", "github_pat_", ...)`) is code, not a secret —
  GitHub does not block it.

## Sanitization approach that worked
Replace the **username token** literally (catches every path form), not regex on
`C:\...` paths:
```
SENSITIVE = [
    ('<CIVITAI_USER>', '<CIVITAI_USER>'),
    ('<GITHUB_USER>', '<GITHUB_USER>'),
    ('<USER>', '<USER>'),
    ('<USER>', '<USER>'),
]
def sanitize_text(text):
    for pat, rep in SENSITIVE:
        text = text.replace(pat, rep)
    return text
```
Why not regex on `C:\Users\<USER>`: a raw-string `r'C:\Users\<USER>'` in a
`re.sub` throws `re.error: incomplete escape \U`. Literal `.replace()` on the
username token sidesteps the whole backslash class.

## What the user approved / asked
- "publish my skills to GitHub as a showcase, highlight each skill, in mirror
  without breaking my skills."
- Explicitly: **don't touch the live skills** (build a copy in a fresh dir).
- Repo: `hermes-skills-collection` (public, <GITHUB_USER>). Final: 918 files,
  personal-data scan = 0, secrets = 0.
- User later wants to REFRESH the repo as skills grow → git add + push, offer
  to update the mirror.
