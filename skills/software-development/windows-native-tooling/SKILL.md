---
name: windows-native-tooling
description: "Windows nativo en git-bash: rutas, codepage, taskkill."
version: 1.0.0
author: Hermes Agent (curador)
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [windows, git-bash, msys, subprocess, encoding, taskkill, netstat]
    related_skills: [hermes-reliability, vram-watchdog]
---

# Windows Native Tooling desde git-bash / Python

Cómo invocar herramientas NATIVAS de Windows (python, git, netstat, tasklist, taskkill)
cuando el shell del agente es git-bash/MSYS. Los fallos aquí no son bugs del código:
son diferencias de traducción de rutas y encoding entre el mundo MSYS y el mundo nativo.

## When to Use
- Llamas a un binario nativo de Windows (python.exe, git.exe, node.exe, curl.exe) con una ruta
- Usas `subprocess` en Python para correr netstat/tasklist/taskkill u otro comando de Windows
- Un comando falla con "cannot change to", "No such file or directory", o UnicodeDecodeError
  sin razón obvia — sospechar interop Windows primero.
- `docker compose up` falla con "failed to connect to the docker API at npipe://" — Docker Desktop
  está instalado pero el daemon no ha arrancado; no es un bug de tu código.

## Regla 1: Rutas — MSYS NO traduce para binarios nativos
`cd /c/Users/x` funciona (builtin bash). Pero `python /c/Users/x/a.py`, `git -C /c/Users/x`,
`node /tmp/a.js` FALLAN con "cannot change to" / "No such file or directory".

- Pasar rutas estilo Windows con forward slashes: `C:/Users/<USER>/...`
- Para archivos temporales que un binario nativo deba leer, usar `$LOCALAPPDATA/Temp`,
  NO `/tmp` (MSYS lo mapea a otra ubicación que el binario nativo no ve igual).
- Ejemplo:
  ```bash
  # FALLA: python -m py_compile /c/Users/<USER>/workspace/code/a.py
  # OK:    python -m py_compile "C:/Users/<USER>/workspace/code/a.py"
  ```

## Regla 2: Codepage — netstat/tasklist NO emiten UTF-8
`netstat -ano` y `tasklist` en Windows devuelven texto en el codepage del sistema
(p. ej. cp437/cp850 en consolas latinas). Si usas `subprocess.run(..., text=True)` sin
`encoding`, Python asume UTF-8 y lanza `UnicodeDecodeError: 'utf-8' codec can't decode byte`.

- SIEMPRE pasar `encoding="latin-1"` (acepta cualquier byte) cuando captures salida de
  netstat, tasklist, wmic u otros comandos nativos de consola:
  ```python
  out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                       encoding="latin-1", timeout=15).stdout
  ```
- Para parsear tasklist CSV, el formato es `"nombre.exe","PID",...` — regex `"(\d+)"`
  extrae el PID.
- No usar `sys.stdout` con encoding distinto para escribir: escribir a archivo con
  `encoding="utf-8"` explícito cuando mezcles salida nativa con texto propio.

## Regla 3: Matar procesos nativos — taskkill /F /PID
- `taskkill /F /PID <pid>` funciona desde git-bash, exit 0 = matado.
- Capturar con `encoding="latin-1"` también aquí (mensaje localizado puede tener bytes altos).
- `wmic process where "name='x.exe'" get ProcessId,CommandLine /format:list` también es
  útil para descubrir cómo se lanzó un proceso — pero la salida puede venir truncada o con
  codepage; parsear defensivamente.

## Regla 4: Fondo con Popen en Windows — creationflags
Para lanzar un server/daemon que sobreviva al script (p. ej. llama-server):
```python
DETACHED = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
with open(log_path, "w", encoding="utf-8") as flog:
    subprocess.Popen(cmd, stdout=flog, stderr=subprocess.STDOUT,
                     stdin=subprocess.DEVNULL,
                     creationflags=DETACHED | CREATE_NEW_PROCESS_GROUP,
                     close_fds=True)
```
Sin `creationflags`, el proceso hijo muere cuando el padre termina o queda ligado a la
consola del padre.

## Regla 5: Docker Desktop — el daemon NO está corriendo aunque `docker` exista
En Windows, `docker`/`docker compose` están instalados pero el **daemon de Docker Desktop arranca
bajo demanda o tras login**, no en boot. `docker compose up` falla con:
`failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine ... El sistema no puede encontrar el archivo especificado`
Eso NO significa que Docker esté roto — solo que el daemon no ha arrancado.

- Arrancar el daemon (path por defecto):
  ```bash
  "/c/Program Files/Docker/Docker/Docker Desktop.exe" &
  ```
- Esperar a que responda con un poll loop, NO con sleep ciego:
  ```bash
  for i in $(seq 1 30); do docker info >/dev/null 2>&1 && { echo "DAEMON READY"; break; }; sleep 2; done
  ```
- Verificar con `docker info` (Server Version + "Operating System: Docker Desktop") antes de `compose up`.

## Pitfalls
- **subprocess bajo el runner de cron (Windows): stdin=DEVNULL SIEMPRE.** El runner (libuv) puede pasar al hijo un stdhandle no-nulo INVÁLIDO (emite `warning: Making stdin inheritable failed`). Con `stdin=None`, subprocess incluye ese handle en el handle-list del nieto → `CreateProcess` falla con WinError 6 ('Controlador no válido'). Fix: `subprocess.run(..., stdin=subprocess.DEVNULL)` en todo script Python que lance binarios nativos desde cron. Caso real 2026-09-07: gbrain-sync-vault streak=4 (bridge → bun). El fix no cambia comportamiento interactivo (los CLIs no leen stdin).
- **`docker compose up -d` dispara el guard de "servidor de primer plano"**: aunque `-d` es modo
  daemon y el comando retorna al terminar, el detector de la herramienta `terminal` lo marca como
  proceso largo. Ejecutarlo con `background=true` + `notify=true`, luego verificar readiness con
  `docker ps` (busca `(healthy)`) y un `curl` al puerto mapeado en una llamada separada.
- **`&` en comando heredoc**: el detector del terminal interpreta `&` como backgrounding.
  Si el código Python usa `&` (p. ej. máscaras numpy), escribir el script a archivo con
  write_file y ejecutarlo — no heredoc inline.
- **`ls`/`find`/`grep`**: son builtins/utilities MSYS, funcionan con `/c/...`. Solo los
  binarios NATIVOS necesitan rutas `C:/...`. No aplicar la regla 1 a comandos de shell puro.
- **netstat TIME_WAIT**: cuenta como "actividad reciente" (~2 min) — útil para watchdogs
  que no deben matar un modelo recién usado, pero no como señal de uso continuo.

## Verificación
- [ ] Comando nativo con ruta: usa `C:/...` (forward slashes, con letra de unidad)
- [ ] subprocess capturando netstat/tasklist: `encoding="latin-1"`
- [ ] Matar proceso: `taskkill /F /PID` verificado con exit 0
- [ ] Daemon en background: `creationflags=DETACHED|CREATE_NEW_PROCESS_GROUP` + log file
- [ ] Instalación desde GitHub releases: descarga → extrae → copia a `$LOCALAPPDATA/hermes/bin/`
- [ ] Paths MSYS: usar `$HOME/...` o rutas completas `C:/...`, nunca `/tmp/` sin verificar