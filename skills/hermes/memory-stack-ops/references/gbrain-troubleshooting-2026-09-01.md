# GBrain Troubleshooting — Auditoría 2026-09-01

## Problema: gbrain no respondía en puertos estándar

### Síntoma
- PID 9360 (bun.exe) corriendo pero no en :39867 ni otros comunes
- `gbrain sync` fallaba con: "a live gbrain serve (PID 9828) holds this PGLite brain's single-writer lock but exposes no sync IPC"
- `gbrain serve` salía inmediatamente sin abrir socket

### Diagnóstico
```bash
# Verificar proceso
tasklist | findstr bun
# Output: bun.exe PID 9360

# Ver configuración de sources
gbrain sources list
# Output:
# SOURCES
# ───────
#   default               federated          9 pages  never synced
#   obsidian-vault        unset             75 pages  last sync 2026-09-01T14:24:13.992Z
```

### Causa raíz
1. `sources.default` estaba vacío/federado, no apuntaba a `obsidian-vault`
2. Versión obsoleta (v0.47.9.0 vs v0.48.1.0 disponible)
3. Lock file huérfano de sesiones anteriores

### Solución aplicada
```bash
# 1. Matar procesos huérfanos
taskkill /PID 9360 /F
taskkill /PID 9828 /F

# 2. Actualizar versión
cd %USERPROFILE%\mcp-servers\gbrain-server
bun run src/cli.ts self-upgrade
bun install

# 3. Configurar source default
gbrain config set sources.default obsidian-vault

# 4. Extraer enlaces(stale)
gbrain extract --stale --source obsidian-vault
# Output: 38 link(s) from 84 page(s)

# 5. Reiniciar Hermes para recargar MCP
# /reset en el chat
```

### Verificación post-fix
```bash
# CLI recall funciona
gbrain recall --query "modelo principal"
# Muestra results de vault

# Bridge sync funciona
cd $LOCALAPPDATA\hermes\scripts
python hermes_obsidian_bridge.py sync-gbrain --source obsidian-vault
# status: ok, gbrain_available: true
```

### Lecciones
- **El bridge NO es un reemplazo del MCP**: Solo sincroniza, no indexa semánticamente
- **sources.default es crítico**: Sin él, gbrain no sabe qué source usar por defecto
- **Siempre verificar versión**: `gbrain --version` debe coincidir con el último release
- **Los locks son normales**: PGLite es single-writer; usar CLI solo cuando serve está detenido

## Logs de referencia
- `~/.gbrain/config.json` — configuración del brain
- `$LOCALAPPDATA/hermes/logs/mcp-stderr.log` — errores de MCP servers
- `$LOCALAPPDATA/hermes/logs/gateway.log` — actividad del gateway
