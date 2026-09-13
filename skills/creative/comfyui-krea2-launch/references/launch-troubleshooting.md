# ComfyUI launch & Krea2 troubleshooting (RTX 3060, Windows)

## Launch (the ONLY reliable way)
PowerShell detached with stdout/stderr redirected to FILES (fixes OSError 22 from tqdm/colorama logger):
```powershell
Start-Process -FilePath 'F:\ComfyUI\venv\Scripts\python.exe' `
  -ArgumentList '-u','F:\ComfyUI\main.py','--listen','--port','8188','--disable-auto-launch' `
  -WorkingDirectory 'F:\ComfyUI' -WindowStyle Hidden `
  -RedirectStandardOutput 'F:\ComfyUI\user\comfyui_out.log' `
  -RedirectStandardError 'F:\ComfyUI\user\comfyui_err.log'
```
NOTE: bash mangles `$_.CommandLine` inside powershell -Command (becomes /f/ComfyUI.CommandLine). Use a .ps1 file instead (Downloads/launch_comfy.ps1).

## tqdm OSError 22 fix
`comfy/utils.py`: replace `from tqdm.auto import trange` with wrapper that forces `kw['disable']=True`. git-tracked, survives restarts.

## Krea2 SVDQuant SLOW (eager backend) — NOT a bug
Log warning: `convrot_w4a4 will dispatch to 'eager' backend, not 'cuda'` — torch cu121 < cu130 disables the CUDA backend. int4 unpacked to bf16 in Python => generation takes 15-25 min (GPU still 100%). It WORKS, just wait. Poll `/queue` until `queue_running` is empty, then check `/history/{pid}` for `status: success` + outputs.images.

## DANGER: never restore repo files with write_file
It REPLACES the entire file. Lost all of comfy/k_diffusion/sampling.py once. ALWAYS `cd /f/ComfyUI && git restore <file>` (it's a git repo).

## Dead server recovery
`taskkill //F //IM python.exe` in git-bash (NOT powershell Stop-Process — needs approval). Then relaunch via .ps1, poll /system_stats until 200.

## Port conflict
If second instance says `Port 8188 is already in use` + `Could not acquire lock on database`: the FIRST instance is still alive and is the real server — use it, don't kill blindly.