# browser-harness → real-profile en Windows — transcript verificado (2026-09-03)

## Hallazgo central
github.com/browser-use/browser-harness (17.4k⭐, MIT, activo) NO se instala: es el backend
que Hermes ya integra como `browser_exec` (mismos helpers: page_info, new_tab, goto_url,
agent_helpers.py auto-importado, BH_AGENT_WORKSPACE, stub --dry-run). Señal de detección:
comparar `def`s del repo vs el docstring de browser_exec.

## Cadena de requisitos de browser_exec(local=true)
código: tools/browser_tool.py (~L1685) + hermes_cli/browser_connect.py
1. `browser.use_real_profile: true`
2. `browser.engine` != lightpanda
3. Default OS = Chromium estable. Windows: ProgId en
   `HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice`
   (leer: powershell Get-ItemProperty). FirefoxURL* → bloqueado. Beta/Dev/Canary → fail closed.
4. `browser.real_profile_pin` = DIR de perfil (`Default`/`Profile 2`), NO navegador
   (`_real_profile_pin()`); unset = last-used.
El error de browser_exec(local=true) NOMBRA la puerta que falló — leerla, no adivinar.

## Instalación Brave sin winget (ausente en bash Y powershell de este host)
```bash
curl -sL -o "$LOCALAPPDATA/Temp/BraveSetup.exe" \
  "https://github.com/brave/brave-browser/releases/download/<TAG>/BraveBrowserStandaloneSilentSetup.exe"
curl -sL "<misma URL>.sha256"   # echo "<hash> *BraveSetup.exe" | sha256sum -c -
powershell -NoProfile -ExecutionPolicy Bypass -Command \
  'Start-Process -FilePath "$env:LOCALAPPDATA\Temp\BraveSetup.exe" -PassThru -Wait'
# user-level OK (ExitCode 0) → $LOCALAPPDATA/BraveSoftware/Brave-Browser/Application/brave.exe
# --system-level → ExitCode -2147218431 (elevación)
```
`laptop-updates.brave.com/download/BRAVE` devuelve HTML, no binario — usar el asset de GitHub.

## Paredes de Win11 (handoff al usuario, 2 clics)
- `brave.exe --make-default-browser` → no-op silencioso (UserChoice hash protection).
  Usuario: `brave://settings/default-browser` → Set as default → Brave.
- `brave.exe --import --import-from=chrome --no-startup-window` → no importa headless.
  Usuario: `brave://settings/importData` → Chrome → passwords + cookies → Import.
- Abrir URL interna: `cmd.exe //c start "" "<ruta brave.exe>" "brave://settings/importData"`

## Verificación post-import (nunca asumir)
```bash
python -c "import sqlite3; print(sqlite3.connect(r'<Default>/Login Data').execute('select count(*) from logins').fetchall())"
python -c "import sqlite3; print(sqlite3.connect(r'<Default>/History').execute('select count(*) from urls').fetchall())"
# cookies: existe <Default>/Network/Cookies + tamaño
```

## Gotchas de shell
- `taskkill //IM brave.exe //F` vía git-bash → flag inválido; usar
  `cmd.exe //c "taskkill /IM brave.exe /F"`.
- `brave.exe --version` puede colgar la terminal (spawn navegador) → `tasklist | grep -i brave`.
- Powershell inline con `$m.'(default)'` se rompe por quoting bash → escribir .ps1 a
  $LOCALAPPDATA/Temp y `powershell -File`.
