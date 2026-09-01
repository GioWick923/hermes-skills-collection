# Build de crates Rust en Windows (git-bash + MSVC) — saga verificada 2026-08-26

Guía para `cargo install <crate>` / build de Rust en Windows 11 con shell MSYS (git-bash),
cuando no hay toolchain previo. Todo lo siguiente se verificó en una instalación limpia.

## Decisión clave: toolchain GNU vs MSVC

- **NO usar el target `x86_64-pc-windows-gnu` si no hay MSYS2 completo.** El toolchain GNU
  de Rust NO trae gcc/dlltool/ld: depende de un MinGW-w64 externo. Traer winlibs
  (zip standalone) funciona para `gcc.exe` pero su `dlltool.exe` GNU genera import-libs
  (`kernel32.dll_imports.lib`, `bcryptprimitives.dll_imports.lib`) que rustc no puede
  leer → `os error 1006` ("El volumen para un archivo ha sido alterado externamente").
  Error 1006 ≠ Defender, ≠ OneDrive: es el dlltool GNU corrompiendo el .lib.
- **Usar MSVC siempre que sea posible**: `rustup toolchain install stable-x86_64-pc-windows-msvc`
  + VS Build Tools (link.exe/lib.exe nativos). Requiere instalar el workload VCTools:
  ```bash
  vs_buildtools.exe --wait --quiet --norestart --nocache --includeRecommended \
    --add Microsoft.VisualStudio.Workload.VCTools \
    --add Microsoft.VisualStudio.Component.Windows11SDK.26100
  ```
- **El crate `windows-link` (dep de getrandom/windows-sys) busca literalmente `dlltool.exe`**
  en el PATH nativo, aunque sea target MSVC. Rustup 1.29 NO lo trae (ni llvm-dlltool con
  `llvm-tools-preview`). Solución verificada:
  1. Descargar LLVM release oficial (MSI): `https://github.com/llvm/llvm-project/releases/latest`
  2. Extraer sin instalar: `MSYS_NO_PATHCONV=1 cmd /c "msiexec /a C:\...\LLVM-...-win64.msi /qn TARGETDIR=C:\Users\<u>\llvm-extract"`
  3. Copiar `llvm-extract/LLVM/bin/llvm-dlltool.exe` → `~/.cargo/bin/dlltool.exe`
     (el nombre EXACTO `dlltool.exe` es lo que windows-link invoca).

## Invocación desde git-bash (pitfalls MSYS)

- `cmd //c "..."` NO ejecuta (abre prompt interactivo). Usar
  `MSYS_NO_PATHCONV=1 cmd /c "C:\\ruta\\build.bat"`.
- Para cargar entorno MSVC (`vcvars64.bat`) y correr cargo en el MISMO proceso, escribir un
  .bat a archivo con write_file:
  ```bat
  @echo off
  set PATH=C:\Users\<u>\.cargo\bin;%PATH%
  call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
  C:\Users\<u>\.cargo\bin\cargo.exe install <crate> --locked --target x86_64-pc-windows-msvc --target-dir C:\Users\<u>\cargo-target -j1
  ```
  y ejecutarlo con `MSYS_NO_PATHCONV=1 cmd /c "C:\...\build.bat"`.
- `export PATH="$PATH:C:/..."` en bash NO garantiza que un proceso nativo (rustc vía
  CreateProcess) encuentre binarios por nombre. Copiar el binario a `~/.cargo/bin` (ya en
  PATH nativo) o setear PATH dentro del .bat.
- Los binarios de winlibs aparecen como `REAL:` pero el `*` de `ls -F` = ejecutable, no symlink.

## Otros aprendizajes

- `cargo install` sin toolchain previo: primero `rustup-init.exe -y --default-host x86_64-pc-windows-gnu --profile minimal`.
- Tras instalar rustup, `$USERPROFILE/.cargo/env` puede no existir; invocar cargo por ruta
  absoluta `C:/Users/<u>/.cargo/bin/cargo.exe`.
- Compilar en `-j1` (serial) descarta race conditions al generar import-libs.
- `rustup target add` ≠ toolchain completo; para MSVC usar `rustup toolchain install ...-msvc`.
- Verificación real: `test -f ~/.cargo/bin/<bin>.exe` + ejecutar `--version`/`--status`.
