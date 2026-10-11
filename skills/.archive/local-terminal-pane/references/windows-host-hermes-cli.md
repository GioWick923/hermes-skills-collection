# Windows host `hermes` CLI — worked example

Context: agent's execute_code/terminal backend is a Linux Docker sandbox that does NOT
mount the Windows host and has no `hermes` CLI on PATH. Host administration must run
in the USER's PowerShell. The CLI binary lives at:

```
C:\Users\<USER>\AppData\Local\hermes\hermes-agent\bin\hermes.exe
```

## 1. Locate the binary (one line, no hermes needed)
```powershell
Get-ChildItem "$env:LOCALAPPDATA\hermes" -Recurse -Filter hermes.exe -ea SilentlyContinue | %{$_.FullName}
```

## 2. Drive it with full path (avoids PATH lookup)
```powershell
$cli = "$env:LOCALAPPDATA\hermes\hermes-agent\bin\hermes.exe"
& $cli cron list
& $cli mcp list
& $cli status --all
```

## 3. Extract cron job IDs (12-hex) and re-pin all LLM jobs
```powershell
$cli = "$env:LOCALAPPDATA\hermes\hermes-agent\bin\hermes.exe"
& $cli cron list 2>&1 | Tee-Object -FilePath "$env:TEMP\cl.txt"
$ids = (Get-Content "$env:TEMP\cl.txt" | Select-String '\b[a-f0-9]{12}\b' | %{$_.Matches.Value} | Sort -Unique)
foreach ($id in $ids) { & $cli cron edit $id --provider nvidia --model nvidia/glm-5.2 2>&1 | Tee-Object -Append "$env:TEMP\cl.txt" }
```
NOTE: `cron edit --provider/--model` is a no-op on no-agent/script jobs (model ignored) — harmless noise.

## 4. Verify before acting on old memory
Jobs that memory claimed "failed on 2026-08-16" were already `ok` by 2026-08-20.
Always re-run `cron list` / `mcp list` / `status --all` live first.

## 5. Preferred delivery: ONE self-verifying script
Do backups, patch, self-verify (`hermes doctor`), dump to a log, ask user to paste ONCE.
Do NOT run a 6-turn "paste this / what did it say?" loop — user reads it as useless.
If `computer_use` is installed (`hermes computer-use install`), drive the desktop directly instead.

## 6. Gotcha — read_terminal
`focus_pane(pane='terminal')` can report success while `read_terminal` still returns
"No in-app terminal is open" (pane not wired when Docker backend is down). Treat that
as "no host shell" and fall back to a one-shot script or computer_use.
