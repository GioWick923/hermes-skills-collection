# Integración FCC↔Hermes — sesión 2026-08-20 (Windows, RTX 3060 12GB)

Transcript resumido de la integración real, con comandos verificados.

## Instalación selectiva (no-interactiva)
1. `curl -sL https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/scripts/install.ps1 -o fcc-install.ps1`
2. Editar defaults en el script: `$script:InstallClaudeCode=$false`, `$InstallCodex=$false`,
   `$InstallPi=$true`, `$InstallOpenCode=$false`, `$InstallCline=$false`, `$InstallHermes=$true`,
   `$InstallDsh=$true`, `$InstallGrok=$false`.
3. `powershell.exe -NoProfile -ExecutionPolicy Bypass -File fcc-install.ps1 < /dev/null` (background)
4. Resultado: `free-claude-code 5.11.0`, atajos en Desktop + Start Menu, `~/.fcc/` con `.env`, `config.lock`, `logs/`.

## Key de OpenRouter (sin exponer)
```bash
OR_KEY=$(grep -E "^OPENROUTER_API_KEY=" "$LOCALAPPDATA/hermes/.env" | head -1 | cut -d= -f2-)
printf '\nOPENROUTER_API_KEY=%s\n' "$OR_KEY" >> "$USERPROFILE/.fcc/.env"
```
Log esperado tras reinicio: `Provider model discovery cached: provider=open_router models=348`.

## Cambiar modelo por defecto
- GET `http://127.0.0.1:8082/admin/api/config` → campo `MODEL = 'nvidia_nim/nvidia/nemotron-3-super-120b-a12b'`.
- POST `http://127.0.0.1:8082/admin/api/config/apply` `{"MODEL":"open_router/openrouter/free"}`
  → `{"applied":true,"valid":true,...}`. NOTA: este apply NO persistió en `.env` en runtime;
  se añadió `MODEL=open_router/openrouter/free` manualmente al `.env` + reinicio de `fcc-server`.

## Errores vistos y resolución
- `API call failed after 3 retries: HTTP 503: NVIDIA_NIM_API_KEY is not set` → modelo default
  apuntando a NIM sin key. Fix: cambiar `MODEL` (arriba).
- Endpoints equivocados: `POST /admin/api/config` y `PUT /admin/api/config` → `405 Method Not Allowed`.
  El correcto es `POST /admin/api/config/apply`.
- `fcc-hermes` arranca Hermes con `Warning: Unknown toolsets: omh` (cosmético, inofensivo).

## Prueba final
```bash
export PATH="$PATH:/c/Users/<USER>/.local/bin"
fcc-hermes chat -q "Responde solo: OK2" -Q        # → OK2 (usa MODEL del .env)
fcc-hermes chat -q "hola" -m "open_router/openrouter/free" -Q   # override explícito
```

## Estado del server
`fcc-server` corre en background; Admin UI `http://127.0.0.1:8082/admin`; log `~/.fcc/logs/server.log`.
