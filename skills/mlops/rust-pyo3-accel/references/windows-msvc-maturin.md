# Windows MSVC + maturin + PyO3 — exact commands and error→fix map

## Environment
- Windows 10/11, Git Bash (MSYS) as shell (NOT PowerShell/cmd for the agent).
- Rust toolchain default = `x86_64-pc-windows-msvc` (needs MSVC `link.exe`).
- Python shipped by the app in its own venv (e.g. Hermes: `AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`).

## Install commands (run once)
```bash
# Rust + cargo
rustup default stable-x86_64-pc-windows-msvc

# maturin via uv (lands in ~/.local/bin — remember to add to PATH)
uv tool install maturin
export PATH="$HOME/.local/bin:$PATH"

# MSVC C++ build tools — the bootstrapper is the reliable path.
# winget's --override often reports "already installed" and skips VC components.
curl -sL -o vsbt.exe "https://aka.ms/vs/17/release/vs_BuildTools.exe"
./vsbt.exe --add Microsoft.VisualStudio.Workload.VCTools \
           --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 \
           --add Microsoft.VisualStudio.Component.Windows11SDK.22621 \
           --quiet --wait
```

## Compile + install (per build)
```bash
# 1) Put MSVC link.exe BEFORE /usr/bin/link (the MSYS shadow).
MSVC_BIN="/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64"
WIN_SDK="/c/Program Files (x86)/Windows Kits/10/bin/10.0.22621.0/x64"
export PATH="$MSVC_BIN:$WIN_SDK:$PATH"

# 2) Activate the REAL app venv so the wheel targets the right ABI (cp311, not cp313).
source "<APP>/venv/Scripts/activate"

# 3) Build + install editable into that venv.
cd /c/path/to/rust_crate
maturin develop --release
```

## Error → Fix map
| Symptom | Cause | Fix |
|---|---|---|
| `link: extra operand '...rcgu.o'` | `/usr/bin/link` (MSYS) shadows MSVC `link.exe` | Prepend MSVC bin dir to PATH (see step 1) |
| `winget ... EXIT 43 / already installed` | winget thinks BuildTools present, skips VC components | Use the `vsbt.exe` bootstrapper with explicit `--add` |
| `Couldn't find a virtualenv` (maturin) | maturin needs an active venv | `source <app>/venv/Scripts/activate` |
| `.pyd` imports in demo venv but NOT in app | ABI mismatch (built cp313, app runs cp311) | Rebuild with the app's venv activated |
| `rustfmt.exe not installed` (lint warning) | rustfmt component missing | Harmless for build; ignore or `rustup component add rustfmt` |
| Python import `SyntaxError: unicodeescape` | backslashes in `-c` code / interpolated path | Use separate `.py` file + env var for paths |

## ABI note
PyO3 wheels are locked to the CPython version that built them
(`cp311-win_amd64` vs `cp313-win_amd64`). If the app upgrades Python,
rebuild the module against the new venv or the accelerator silently
disables (fallback to Python).
