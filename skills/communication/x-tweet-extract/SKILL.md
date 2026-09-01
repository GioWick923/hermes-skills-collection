---
name: x-tweet-extract
description: "Extract X tweet text+image without login via syndication."
version: 1.0.0
author: Hermes Agent (curado 2026-08-31)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [twitter, x, tweet, extraction, syndication, scraping, image]
    related_skills: [twitter-video-downloader, youtube-content, markdown-browser]
---

# Extract X/Twitter Tweet Content (text + image) WITHOUT login

Cuando el usuario pasa un enlace `https://x.com/<user>/status/<id>` y hay que **leer el
tweet** (texto) o **extraer la imagen/media**, X bloquea scraping directo (403) y muchas
herramientas del stack no sirven. La vía fiable es el **endpoint público de syndication**
de X, que devuelve el JSON completo del tweet público SIN autenticación.

## When to use
- El usuario pasa un enlace de X/Twitter y quiere **leer el contenido** o **bajar la imagen**.
- El enlace "no extrajo contenido" en el contexto (warning `no content extracted`) — es NORMAL, X no se deja extraer por attachments.

## Vía que FUNCIONA (probada 2026-08-31)

Endpoint público de syndication (no requiere login, devuelve JSON del tweet):
```
https://cdn.syndication.twimg.com/tweet-result?id=<TWEET_ID>&token=<token-cualquiera>
```

1. **Obtener el TWEET_ID** (los números tras `/status/`).
2. **Llamar al endpoint** con un `token` aleatorio: `curl -s "https://cdn.syndication.twimg.com/tweet-result?id=<ID>&token=$(node -e 'console.log(Math.random().toString(36).slice(2))')"`.
3. **Parsear** con Python: texto en `full_text` o `text`; autor en `user.name`/`user.screen_name`; fecha, favs, lang.
4. **Imagen/media**: las URLs en `pbs.twimg.com` / `video.twimg.com`. Filtrarlas con regex del JSON:
   `https://(?:pbs|video)\.twimg\.com/[^"\ ]+`
5. **Descargar la imagen** con `curl -sL <url>`; verificar con `file` (JPEG/PNG) y `wc -c`.
6. **Leer la imagen** con `vision_analyze` para transcribir lo que muestra.

## Rutas que NO sirven (evitar, probado)
- **stealth-browser MCP**: a veces sale `chrome-error://chromewebdata/` y el body tiene `HTTP ERROR 403` (X bloquea sin sesión). Si la URL reportada es `chrome-error`, no confíes en ella — revisa `data.text`.
- **browser-exec (Browser Use)**: pide que el usuario apruebe "Allow remote debugging" en Chrome; requiere interacción manual.
- **firecrawl_scrape**: aquí dio `Unauthorized: Invalid token` (token no configurado). No fiable por defecto.
- **yt-dlp**: `No video could be found in this tweet` en tweets de texto/imagen. Sirve SOLO para video — usa `twitter-video-downloader` para eso.

## Script re-ejecutable
Usa `scripts/fetch_tweet.py` — toma el ID o URL del tweet y devuelve texto + media URLs:
```bash
python "$LOCALAPPDATA/.../x-tweet-extract/scripts/fetch_tweet.py" <ID_o_URL>
```
Detalle de la receta (parse puro, sin dependencias) en `references/fetch-recipe.md`.

## Pitfalls
- **Token**: el `token` del query param puede ser casi cualquier string corto; el endpoint lo acepta. Un token con `Math.random().toString(36)` funciona.
- **Tweet protegido / eliminado / age-restricted**: el endpoint puede devolver vacío o 404. No fuerces; reporta que no hay acceso público.
- **Redirección de URL corta**: si el enlace es `t.co/xxx`, expande primero o saca el ID del enlace original.
- **Verificar SIEMPRE** con `file` + `wc -c` la imagen descargada antes de pedirle a vision_analyze.

## Verificación
- [ ] JSON del tweet parseado (texto no vacío)
- [ ] URLs de media detectadas
- [ ] Imagen descargada y verificada (JPEG/PNG, tamaño > 0)
- [ ] `vision_analyze` devuelve transcripción
