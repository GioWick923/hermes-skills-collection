---
name: website-downloader-delegate
description: Delega descargas de sitios web al server Website-downloader.
version: 1.0.0
platforms: [windows]
---

# Website-downloader — delegación de mirrors de sitios

## When to Use

- Gio pide descargar/bajarse/mirrar un sitio web completo (HTML+CSS+JS+imgs offline).
- Instalado 2026-09-14 desde Ahmadibrahiim/Website-downloader (5.4k⭐, MIT) en `~/Website-downloader` (C:/Users/<USER>/Website-downloader).

## Qué está instalado

- App Node.js (Express + socket.io v2) que envuelve wget `--mirror --convert-links --adjust-extension --page-requisites --no-parent`.
- **wget.exe YA viene dentro del repo** (`wget.exe` en la raíz, build eternallybored 1.21.4 con cert-store de Windows). NO está en PATH global; el server se lanza con PATH local:
  ```bash
  cd "$HOME/Website-downloader" && PATH="$HOME/Website-downloader:$PATH" node bin/www
  ```
- Puerto: **3000** (env `PORT` para cambiar). UI web en http://localhost:3000 si Gio quiere usarla a mano.

## Cómo delegar (protocolo verificado)

1. Server vivo: `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/` → 200. Si no, lanzarlo en background (comando de arriba).
2. Cliente de test ya escrito: `test_e2e.js` en la raíz del repo. Uso:
   ```bash
   cd "$HOME/Website-downloader" && TEST_SITE="https://sitio.com" node test_e2e.js
   ```
   Imprime `SUCCESS: file=<nombre>` o `FAIL(error): <motivo>`. Timeout interno 120s.
3. Protocolo socket (para clientes propios): `emit('request', {token, website})` → eventos en el token propio: `{error}` / `{progress: chunks-wget}` / `{progress:'Converting'}` / `{progress:'Completed', file}`.
4. El zip queda en `public/sites/<hostname>-<jobid>.zip`. Mover al workspace y entregar con MEDIA:. Verificar con `python -m zipfile -l <zip>`.

## Límites (env-overridables)

- `DOWNLOAD_QUOTA` (default `100m`) y `DOWNLOAD_TIMEOUT_MS` (default 300000 = 5 min). Sitios grandes: subir ambos ANTES de lanzar el server.
- wget escribe el log en stderr; `200 OK` por archivo = progreso.

## Pitfalls (leídos del código, verificados 2026-09-14)

- `localhost.zip` en public/sites/ es un artefacto commiteado del upstream, no es una descarga.
- wget NO está en PATH de git-bash; solo funciona con el PATH local del repo al lanzar el server.
- Si el sitio bloquea bots (403/robots), wget no escribe nada → el app reporta error honesto, no zip vacío (fix upstream 2026-08).
- git clone con ruta MSYS `/c/...` aterrizó en `C:\c\...` (binario nativo Windows): usar siempre `$HOME` para clonar.
- El server es de un solo job por conexión; para varios sitios, un cliente por vez o conexiones nuevas.

## Verificación hecha (2026-09-14)

- E2E real: `TEST_SITE=https://example.com node test_e2e.js` → SUCCESS, filesDownloaded=1, zip 629B con index.html verificado vía `python -m zipfile -l`.
- wget standalone: HTTPS a example.com exit=0.
