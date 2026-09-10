# Windows + WSL setup para hermes-self-evolution (verificado 2026-07-13)

Problema raíz: `dspy>=3.0.0` depende de `litellm`, y en **Windows litellm no tiene
wheel precompilado** (solo sdist → requiere Rust/Cargo para compilar). `pip install dspy`
falla en Windows sin Rust. En **Linux/WSL litellm trae wheel** y dspy instala limpio.

## Ruta recomendada: WSL/Ubuntu (sin Rust)

```bash
# 1) Instalar distro (puede tardar >3 min; el timeout del terminal NO aborta la
#    instalación — verificar con wsl --list --verbose, no reintentar a ciegas)
wsl --install -d Ubuntu

# 2) El primer login pide usuario/contraseña de forma interactiva y se CUELGA en
#    terminal no-PTY. Saltarlo creando usuario como root:
wsl -u root -e bash -c '
  id hermes 2>/dev/null || useradd -m -s /bin/bash hermes
  echo "hermes ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/hermes
  printf "[user]\ndefault=hermes\n" > /etc/wsl.conf
  apt-get update -qq && apt-get install -y -qq gcc python3-venv python3-pip
'

# 3) Crear venv e instalar deps (litellm/dspy con wheel, sin Rust)
wsl -u hermes -e bash -c '
  REPO=/mnt/c/Users/<USER>\ GAMES/AppData/Local/hermes/skills/hermes-self-evolution/repo
  cd "$REPO"
  python3 -m venv .venv-wsl
  . .venv-wsl/bin/activate
  pip install --upgrade pip -q
  pip install "dspy>=3.0.0" "openai>=1.0.0" "pyyaml>=6.0" "click>=8.0" "rich>=13.0" gepa
  python -c "import dspy, openai, yaml, click, rich; print(\"IMPORTS OK\")"
'
```

## Ruta alternativa: Rust en Windows (Opción 1)

```bash
# Descarga rustup-init para x86_64-pc-windows-msvc y ejecuta -y
rustup-init.exe -y --default-toolchain stable --default-host x86_64-pc-windows-msvc --profile minimal
# cargo/rustc quedan en %USERPROFILE%\.cargo\bin (verificado: cargo 1.97.0)
```
NOTA: bajo MSYS/git-bash el archivo `~/.cargo/env` NO existe; invocar cargo por
ruta completa (`"$USERPROFILE/.cargo/bin/cargo.exe" --version`), no `source ~/.cargo/env`.

## Gotchas de WSL (no triviales, reproducidos en sesión)
- `wsl --install -d Ubuntu` puede superar timeout de 180s del terminal pero la
  instalación continuó en background → al comprobar, distro apareció `Running`.
- Primer arranque wedgeado: `wsl -u root -e echo` devolvía timeout 150s. Causa:
  setup interactivo de usuario. Se resolvió matando `wslhost.exe`
  (`taskkill //IM wslhost.exe //F`) y reintentando; `net stop LxssManager` da
  "Acceso denegado" sin admin — no es necesario reiniciarlo.
- Para correr el motor luego: dentro del venv-wsl, `python -m evolution.skills.evolve_skill ...`

## Verificación post-instalación
- WSL: `wsl -u hermes -e bash -c 'cd <repo> && . .venv-wsl/bin/activate && python -c "import dspy; print(dspy.__version__)"'`
- Windows+Rust: `"$USERPROFILE/.cargo/bin/cargo.exe" --version` → `cargo 1.97.0`
