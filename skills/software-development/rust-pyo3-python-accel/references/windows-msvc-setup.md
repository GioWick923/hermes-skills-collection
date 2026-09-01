# Windows MSVC setup for Rust (PyO3 / maturin)

## Symptom: link.exe errors
On Git Bash, `which link` → `/usr/bin/link` (MSYS). Rust target
`x86_64-pc-windows-msvc` then fails:
```
error: linking with `link.exe` failed
note: link: extra operand '...rcgu.o'
```
This means the MSVC linker is shadowed by MSYS `link`.

## Verify MSVC presence
```bash
ls "/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/"
# EMPTY before fix -> components not installed
```

## Step 1 — install Build Tools with C++ workload
`winget install Microsoft.VisualStudio.2022.BuildTools` may say "already
installed" (exit 43) but leave `VC/Tools/MSVC/` empty. Force the components
with the official bootstrapper:
```bash
curl -sL -o vsbt.exe "https://aka.ms/vs/17/release/vs_BuildTools.exe"
./vsbt.exe --add Microsoft.VisualStudio.Workload.VCTools \
           --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 \
           --add Microsoft.VisualStudio.Component.Windows11SDK.22621 \
           --quiet --wait
```
After this, `VC/Tools/MSVC/<ver>/bin/Hostx64/x64/link.exe` and
`VC/Auxiliary/Build/vcvarsall.bat` exist. Example `<ver>`: `14.44.35207`.

## Step 2 — prepend MSVC bin to PATH (do NOT call vcvarsall via cmd.exe)
In Git Bash, `cmd.exe /c "call vcvarsall.bat x64 && maturin ..."` prints only
the cmd banner and swallows build output (silent failure). Instead, export
PATH directly in bash:
```bash
MSVC_BIN="/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64"
export PATH="$MSVC_BIN:$PATH"
which link   # should now point at MSVC link.exe
```
Then `maturin develop --release` works.

## maturin on PATH
`uv tool install maturin` installs to `$HOME/.local/bin` (not on PATH by
default on Windows). Prepend it:
```bash
export PATH="$HOME/.local/bin:$PATH"
```
