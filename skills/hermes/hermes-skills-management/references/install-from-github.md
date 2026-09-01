# Install a Hermes skill by direct GitHub download (fallback when `hermes skills install` hangs)

Use this when `hermes skills install <name>` blocks on a network fetch — no output,
shell timeout (60–240s), and the skill is NOT on disk afterward. The official skill
sources live in `NousResearch/hermes-agent` under `optional-skills/` (and the main
skills tree). Downloading the repo zip and extracting just the skill folder always works.

## Steps
1. Download the repo archive (large, ~75MB, but reliable):
   ```bash
   curl -sSL -o /tmp/skills.zip "https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip"
   ```
   (The `/tmp` here is MSYS; see path gotchas below for the absolute Windows path.)

2. Extract ONLY the target skill folder with Python (avoid `unzip` CLI path issues):
   ```python
   import zipfile, os
   zip_path = r"C:\Users\<USER> GAMES\AppData\Local\Temp\skills.zip"  # ABSOLUTE Windows path
   z = zipfile.ZipFile(zip_path)
   target = 'hermes-agent-main/optional-skills/security/1password'  # adjust category/name
   names = [n for n in z.namelist() if n.startswith(target + '/')]
   dest = os.path.join(os.environ['LOCALAPPDATA'], 'hermes', 'skills', 'security', '1password')
   os.makedirs(dest, exist_ok=True)
   for n in names:
       if n.endswith('/'):
           continue
       data = z.read(n)
       rel = n[len(target) + 1:]
       if not rel:
           continue
       out = os.path.join(dest, rel)
       os.makedirs(os.path.dirname(out), exist_ok=True)
       open(out, 'wb').write(data)
   print("Extracted", len(names), "entries to", dest)
   ```

3. Verify the frontmatter `platforms:` includes `windows` (see the Windows `platforms:`
   trap in SKILL.md pitfalls). If not, patch it or the skill stays invisible on this host.

4. Confirm: `ls "$LOCALAPPDATA/hermes/skills/<name>"` (SKILL.md present).

## Windows / MSYS path gotchas on this host
- Use `python` (Hermes venv, 3.11.15), NOT `python3` — `python3` triggers the
  Microsoft Store alias and fails with exit 49.
- Native Windows Python CANNOT resolve MSYS paths like `/tmp` or `/c/Users/...` inside
  `zipfile.open`. Pass absolute Windows paths (e.g. `C:\Users\<USER> GAMES\AppData\Local\Temp\skills.zip`).
- Avoid `%TEMP%`/`$TEMP` if it carries a stray control char (observed: a `\x01` prefix
  corrupts the path). Use the hardcoded absolute path instead.
- Destination is `%LOCALAPPDATA%\hermes\skills` (NOT `~/.hermes/skills`) — the loader
  reads that dir on this Windows host.
