# Find → List → Integrate community agent Skills

Worked pattern from integrating Twitter/X video downloaders and vetting
`ponytail` / `agency-agents` into Hermes (Windows). Companion to the
"From radar to install" section in SKILL.md.

## When web_search tool is unavailable
Fall back to the GitHub Search API over curl (parse with Python stdlib):
```
curl -s "https://api.github.com/search/repositories?q=twitter+OR+x+video+download+skill&per_page=25" | python -c "import sys,json;d=json.load(sys.stdin);[print(r['full_name'],'|',r['stargazers_count'],'|',(r['description'] or '')[:80]) for r in d.get('items',[])]"
```
Swap the query for the task. Also check the catalogs in `references/sources.md`
(skills.sh, agentskills.to, ClawHub) via the browser/obscura tools.

## Verify the REAL SKILL.md before trusting a listing
Marketplace descriptions lie; inspect the canonical file:
```
for p in SKILL.md skills/SKILL.md; do
  code=$(curl -s -o /tmp/sk.md -w "%{http_code}" "https://raw.githubusercontent.com/OWNER/REPO/main/$p")
  [ "$code" = "404" ] && code=$(curl -s -o /tmp/sk.md -w "%{http_code}" "https://raw.githubusercontent.com/OWNER/REPO/master/$p")
  [ "$code" = "200" ] && { echo "PATH: $p"; head -30 /tmp/sk.md; break; }
done
```
Get the file tree to see bundled scripts:
```
curl -s "https://api.github.com/repos/OWNER/REPO/git/trees/main?recursive=1" | python -c "import sys,json;d=json.load(sys.stdin);[print(t['path']) for t in d.get('tree',[]) if t['type']=='blob']"
```

## List candidates BEFORE integrating (user preference)
When the user asks to "find a skill and integrate it," first return a ranked
candidate table (repo · method · platforms · caveats) and WAIT for the go-ahead.
Do NOT install on the first turn. Discard candidates that depend on untrusted
third-party APIs or paid keys unless the user explicitly wants them.

## Adapt to Hermes + Windows
- Write the SKILL.md into `$LOCALAPPDATA/hermes/skills/<name>/SKILL.md`
  (e.g. `C:\Users\<USER> GAMES\AppData\Local\hermes\skills\<name>\SKILL.md`).
- Rewrite macOS `brew` / `~/.claude` references to Windows/Hermes paths.
- If the skill calls `yt-dlp` as a subprocess, point it at the local binary:
  `C:\Users\<USER> GAMES\.venvs\media\Scripts\yt-dlp.exe` — run scripts with
  that venv's `python.exe` so `yt-dlp`/`ffprobe`/`curl` resolve on PATH.

## Close the loop — verify it actually runs
Don't declare success on a copied file. Exercise the core action on a real sample:
- Twitter downloader: run a real download of a public tweet that contains video
  (e.g. a SpaceX status), confirm the `.mp4` exists and is non-zero
  (`ffprobe` shows duration/size), then delete the test file.
- If a script reports "SUCCESS" but size 0B, the report is cosmetic — check the
  actual file with `ffprobe` / `ls -lh`.

## Vetting heuristics (should I integrate this?)
- Stars / license / recency from the GitHub API.
- Inspect scripts for hidden instructions, obfuscation, credential harvesting,
  destructive commands, unexplained remote execution.
- Multi-agent / low-context fit: prefer skills that lazy-load or scope narrowly
  (e.g. `agency-agents` installs a lazy-router plugin, not 150 always-on prompts)
  — matches a 4+ specialized-profile, low-context, low-cost setup.
- A skill that is only a "personality / system-prompt" (no real capability)
  complements, doesn't replace, capability skills.

## Worked example: Twitter/X video downloaders
Candidates: `HartreeWorks/skill--download-twitter-video` (yt-dlp, X-only, chosen),
`macrochen/yt-dlp-downloader-skill`, `wxhou/video-downloader-skill`
(multi-platform, vxtwitter→yt-dlp cascade, chosen #2), `grp06/get-x-video-transcript`
(external API + OpenAI key, discarded), `CiCi-Zen/...` (no SKILL.md, discarded).
Both chosen ones integrated; verified real download (35 MB MP4).
