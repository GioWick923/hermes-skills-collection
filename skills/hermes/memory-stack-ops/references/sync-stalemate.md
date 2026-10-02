# GBrain sync stalemate — stale lock + serve-delegated repo failure

## Symptom (two faces of the same blocked sync)
`gbrain sync --source <id>` fails with EITHER:
- `GBrain's local database is already open through gbrain serve (PID N)` even
  when NO bun/serve process is actually running, OR
- `[sync] delegated sync failed inside the serve: Not inside a git repository:
  <vault> ... requires a git-initialized repo` even though the vault IS a valid
  git repo (`git rev-parse` succeeds there).

The second is the trap: the vault being a repo does not help, because a live
serve resolves the repo from ITS OWN cwd/env, not the caller's. The serve was
spawned by the agent harness from a different directory, so its git detection
fails on the vault path.

## Root causes
- The MCP `gbrain serve` can exit (crash / harness restart) leaving
  `~/.gbrain/brain.pglite/.gbrain-lock/lock` holding a **dead PID**. gbrain
  refuses to self-reap (`will not remove ... automatically`), so every sync then
  reports `already open through serve (PID N)` with no serve running.
- A live serve holds the PGLite lock and `sync` **delegates** to it over IPC.
  The delegated run resolves the repo with the serve's own cwd/env → the
  misleading `Not inside a git repository`.

## Fix — run DIRECT, never delegated, from the vault cwd
```python
# 1. Reap a stale lock whose owner PID is dead (move aside; NEVER delete blindly,
#    and NEVER touch a live owner). Lock file: ~/.gbrain/brain.pglite/.gbrain-lock/lock
#    (JSON with "pid" field).
#    alive(pid) -> leave alone; dead -> lock_file.replace(backup_path)

# 2. Run sync DIRECTLY, with the vault as cwd + clean git env
cmd = [bun, "run", cli_ts, "sync", "--source", "obsidian-vault",
       "--no-delegate", "--no-pull"]
subprocess.run(cmd, cwd=vault_path, env=clean_env)
# clean_env: HOME set, OLLAMA_BASE_URL=http://localhost:11434/v1, and
# GIT_DIR / GIT_WORK_TREE popped (a contaminated parent env breaks git detection
# even from the right cwd).
```
- `--no-delegate` runs sync in the calling process instead of handing it to a
  live serve (which would re-trigger the repo-resolution bug).
- `cwd=vault` so `resolve_repo` sees the right git repo.
- `--no-pull` skips the network git pull → offline/deterministic.
- If a live serve IS running and blocks `--no-delegate` (fails fast with
  `already open through serve`), stop that serve via the sanctioned PID-locating
  helper (never by bare process name), then retry direct once.

## Subsequent syncs after a commit mid-sync
If a run reports `Sync blocked: repository history changed during sync` (a commit
changed HEAD mid-sync), gbrain has already **banked** the files and the NEXT sync
resumes from the checkpoint — run it again once or twice; it self-heals.

## Windows PID-alive check (do NOT trust os.kill)
`os.kill(pid, 0)` is unreliable on Windows and raises
`SystemError: <built-in function kill> returned a result with an exception set`
(WinError 87). Use tasklist:
```python
def pid_alive(pid):
    res = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                         capture_output=True, text=True)
    return "no tasks" not in (res.stdout or "").lower()
```

## Cron/bridge wrapper shape that self-heals
A scripted `sync-gbrain` wrapper should: (1) reap the stale lock, (2) run direct
(`--no-delegate`, vault cwd), (3) if a live serve blocks, kill by sanctioned
PID-locating helper then retry once. Verify the wrapper by its `status: ok` /
`exit_code 0` output before trusting it.

## Commit the vault first
`gbrain sync` imports only COMMITTED files; new/untracked notes are counted but
not imported. Review `git status --porcelain`, `git add -A && git commit` to get
new notes indexed. Scrub for non-note content before a blind `-A`.
