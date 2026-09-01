---
name: darkweb-osint
description: "Buscar info via Tor cuando la web normal bloquea."
version: 1.0.0
author: Hermes Agent (instalado 2026-08-31)
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [tor, darkweb, onlion, osint, anonimo, proxysocks]
    related_skills: [wireguard-vpn, blocked-page-recovery, domain-intel]
---

# Dark Web OSINT (via Tor) — cuando la web normal bloquea

> Alternativa de búsqueda/consulta cuando el contenido no está en la web normal, está
> censurado, o la web pública te bloquea (cloudflare/geo). Usa Tor (SOCKS5) para consultar
> servicios `.onion` y buscar de forma anónima. **Uso educativo/lícito (OSINT).**

## When to Use
- El usuario necesita info que la web normal bloquea o no tiene (dark web, .onion, censura).
- "web normal coaccionada", "no encuentro esto", "psst esto solo está en .onion".
- Verificar si un contenido existe/está accesible en la red Tor.

## Arquitectura
```
[agente] → darkosint.py → SOCKS5 (127.0.0.1:9050) → Tor daemon → red .onion
                           ↑ tor.exe (tools/tor/Browser/TorBrowser/Tor/tor.exe)
```

## Tor (daemon) — instalado en C:/Users/<USER>/tools/tor
- Tor 0.4.9.11 extraído en `tools/tor/Browser/TorBrowser/Tor/tor.exe`.
- Config: `tools/tor/torrc` (SocksPort 9050, solo loopback).
- Data dir: `tools/tor/data`.

### Arrancar Tor (si no está corriendo)
```bash
T="C:/Users/<USER>/tools/tor/Browser/TorBrowser/Tor/tor.exe"
"$T" -f "C:/Users/<USER>/tools/tor/torrc" &     # en background
# verificar: netstat | grep :9050  (LISTENING)
```
> Tor tarda ~30-60s en bootstrap la primera vez. Verifica con `darkosint.py status`.

## Script (tools/granite-asr/darkosint.py)
Requiere venv con pysocks+requests (granite-asr venv ya lo tiene).
```bash
VPY="C:/Users/<USER>/tools/granite-asr/venv/Scripts/python.exe"
"$VPY" .../darkosint.py status                     # TOR UP/DOWN
"$VPY" .../darkosint.py probe "<url o .onion>"      # consulta por Tor (200=accesible)
"$VPY" .../darkosint.py search "<query>" --engine ddg|ahmia|torch   # busca en buscadores .onion
```

## Buscadores .onion (OSINT, por defecto ddg)
- `ddg` (DuckDuckGo onion — el más fiable, status 200 probado)
- `ahmia` (ahmia.fi — buscador de dark web clásico)
- `torch` (xmh57jrzrnw6insl.onion)

## VERIFICADO (2026-08-31)
- [x] Tor daemon arranca, SOCKS 9050 LISTENING
- [x] Bootstrap completo → red Tor operativa
- [x] `probe` a DDG.onion → **status 200** (acceso OSINT real)
- [x] pysocks+requests instalados en venv granite-asr

## ⚠️ LÍMITES LEGALES (obligatorios — honestidad House)
- **Solo OSINT lícito / educativo.** El propio disclaimer de Dark: acceder a ciertos contenidos
  dark web puede ser ILEGAL según jurisdicción. NO para comprar/vender cosas ilícitas.
- No basta con anonimato: **no usar Tor para violar leyes**.
- Tor NO es infalible (no 100% anónimo). No lo uses para cosas que no harías en claro.
- Verifica siempre que consultas contenido LEGAL (OSINT, info pública, leaks filtrados por
  periodismo, foros de investigación, CTF).

## Alternativas antes de Tor
Antes de saltar a dark web, probar la web normal con herramientas anti-bloqueo que ya tienes:
`stealth-browser`, `scrapling`, `obscura`, `firecrawl`, `blocked-page-recovery` skill.
Tor es para contenido que REALMENTE no está en la web clara.

## Pitfalls
- **Permiso .exe en git-bash**: "Permission denied" al correr exe → usar `cmd.exe` o `powershell Start-Process`.
- **NSIS no se extrae con 7zr** (básico): usar 7-Zip completo (instalado en C:/Program Files/7-Zip).
- **Bootstrap lento la 1ra vez** (~30-60s): no asumir que falló; esperar y `status`.
- **Tor con puerto ocupado**: matar tor.exe previo antes de re-arrancar.

## Verificación del skill
- [ ] `darkosint.py status` → TOR UP
- [ ] `probe` a un .onion válido → status 200
- [ ] Uso SIEMPRE lícito/OSINT (nunca ilegal)
- [ ] Tor arrancado en background cuando se necesita (y se detiene cuando no)
