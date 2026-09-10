---
name: supercookie-favicon-tracking
description: "Tracking via favicon/caché: Supercookie demo y defensa."
version: 1.0.0
author: Gio + Hermes
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [supercookie, favicon, tracking, cache-side-channel, privacy, fingerprinting, educative]
    related_skills: [local-ablit-delegation, ornith-code-audit]
---

# Supercookie — tracking por favicon (cache side-channel)

Técnica demostrada por jonasstrehle/supercookie (2021, MIT, 7.3k⭐, ARCHIVADO):
asignar un ID persistente al visitante usando el **caché de favicons del navegador**,
sin cookies, sin localStorage, sin red. Uso educativo/demostrativo.

## Qué demuestra
- El caché del navegador es un **canal lateral**: qué favicons tienes cacheados
  revela tu identidad, incluso en incógnito, tras borrar caché/cookies, con VPN
  y con AdBlockers.
- El ID se codifica como un **vector de bits** (N=32 → hasta 2^32 ≈ 4.3 mil millones IDs):
  - Escribir: el server entrega solo los favicons que corresponden a tu ID (max-age=1 año)
  - Leer: el server pide todos; los que responden 200 = tu caché = tu ID; los 404 no
- Sobrevive a: incógnito, limpiar caché (los favicons no se borran igual), cerrar
  navegador, reiniciar OS, VPN, AdBlockers.

## Repo local
- Ruta: `C:/Users/<USER>/seguridad/supercookie/`
- Original: https://github.com/jonasstrehle/supercookie
- Paper original (Univ. Illinois Chicago): https://par.nsf.gov/servlets/purl/10268961
- Artículo heise: https://heise.de/-5027814

## Correr demo local
```bash
cd "C:/Users/<USER>/seguridad/supercookie/server"
cp .env.localhost .env 2>/dev/null || true
node --experimental-json-modules main.js
# HTTP 1: http://localhost:10080 (página principal)
# HTTP 2: http://localhost:10081 (demo tracking)
# API: http://localhost:10080/api (estado)
```

## Cómo funciona el código (main.ts, 520 líneas)
- `createRoutes(CACHE_IDENTIFIER, N)` → 32 rutas secretas por hash MD5
- `/l/:ref` y `/f/:ref` → sirven/niegan favicon según el bit del ID
- `/read` + `/t/:ref` → proceso de lectura: reconstruye vector por favicons cacheados
- `/identity` → calcula y muestra el ID o "browser not vulnerable"
- `/write/:mid` → asigna nuevo ID a visitante nuevo
- Storage en `data.json` (JSON en disco)

## Pitfalls
- **Proyecto ARCHIVADO** (2021): navegadores modernos han mitigado parcialmente
  (Chrome limita caché de favicons; FF partitionea HTTP cache). El valor es EDUCATIVO.
- **Node 22+**: `--experimental-json-modules` se ignora (warning) pero funciona.
- **No es para uso real**: POC educativa. Rastrear sin consentimiento viola GDPR/CCPA.
- **Cache side-channel class**: esta técnica representa una familia de ataques
  (CSS history sniffing, cache probing, timing attacks). Entender Supercookie =
  entender el patrón, no solo la herramienta.

## Defensa
- **Particionado de caché** (Chrome/FF desde 2020-2021): cada sitio tiene su propio
  caché → los favicons de sitio A no se ven desde sitio B. Es la mitigación principal.
- Firefox: `privacy.partition.network_state` = true por defecto.
- uBlock Origin con filtros de red: bloquea requests de terceros.
- Probar la demo local para ver si tu navegador actual es vulnerable.

## Verificación
- [ ] `node main.js` arranca ambos webservers (10080 + 10081)
- [ ] `curl http://localhost:10080/api` devuelve JSON con index/bits/N
- [ ] Demo en navegador → te asigna ID → recargar → te reconoce
- [ ] Incógnito debería reconocerte igual (si el navegador no particiona caché)