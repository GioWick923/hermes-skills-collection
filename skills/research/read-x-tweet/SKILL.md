---
name: read-x-tweet
description: "Leer tweets al instante sin auth (syndication): texto+media."
version: 1.0.0
author: Hermes Agent (resuelve el 403 de X; 2026-08-31)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [x, twitter, tweet, scrape, syndication, fast]
    related_skills: [twitter-video-downloader, scrape-structured-json]
---

# Leer tweets X/Twitter AL INSTANTE (sin auth, sin browser)

> PROBLEMA RESUELTO: los browsers headless contra X devuelven **403** y me hacía perder
> tiempo. La solución NO es un browser con login (frágil, riesgo de baneo). Es el **endpoint
> público de syndication** `cdn.syndication.twimg.com/tweet-result` que devuelve texto + media
> de tweets públicos **sin iniciar sesión, en <1 segundo.**

## When to Use (SIEMPRE primero)
El usuario pasa un link de x.com / twitter.com / pic.x.com / t.co, o un tweet ID, y quiere
leer/entender su contenido (texto, imagen, video). **Usa este método ANTES de cualquier browser.**

## MÉTODO RÁPIDO (1 sola llamada)

```bash
python "$LOCALAPPDATA/hermes/skills/research/read-x-tweet/scripts/tweet_reader.py" "<URL o ID>" [--download-dir <dir>]
```
- Imprime: autor, fecha, favs, texto completo, y URLs de fotos (y si hay video).
- Con `--download-dir`, DESCARGÁ las imágenes para luego `vision_analyze`.
- `--json` para salida estructurada.

## FLUJO PARA EL AGENTE (cómo entregar contexto al usuario)
1. **Extraer texto** → `tweet_reader.py <url>` (lee la parte TEXT).
2. **Si hay fotos** → `--download-dir` y luego `vision_analyze` en la(s) imagen(es) para describirlas.
3. **Si hay video** (`HAS_VIDEO: True`) → usar la skill `twitter-video-downloader` (yt-dlp) para el clip; el thumbnail captura el contexto si solo se necesita la idea.
4. **Responder en español** con el texto completo + resumen de la imagen/video.

## por qué NO usar browser para X
- X (x.com) **bloquea bots/sesiones headless con 403** (probado: stealth-browser → "HTTP ERROR 403").
- El endpoint de syndication NO requiere login ni cookies → **determinista, rápido, sin baneos**.

## VERIFICADO (prueba real 2026-08-31)
| Caso | Resultado |
|---|---|
| Tweet imagen (0x0SojalSec) | ✅ texto + foto descargada + autor/fecha/favs |
| Tweet video (StartupArchive_) | ✅ texto + `HAS_VIDEO: True` + thumbnail |

## Límites
- **Tweets privados / protegidos**: syndication no los sirve → ahí sí toca browser con sesión o pedir al usuario.
- **Video**: syndication da el thumb y detecta video; para el clip real, `yt-dlp`.
- Si el ID no se extrae (t.co corto de un tweet requiere redirect), pasar el ID numérico directo.

## Pitfalls
- Usar `User-Agent` de navegador real (el script ya lo pone). 
- `photos[].url` es la fuente correcta de imágenes (NO `entities.media.media_url_https`, que sale null).
- El token de syndication es aleatorio cada request — NO cachear el token; el script lo genera solo.

## Verificación del skill
- [ ] `tweet_reader.py <url>` devuelve texto en <2s
- [ ] Imágenes descargadas con `--download-dir` (si las hay)
- [ ] `vision_analyze` sobre la imagen en el siguiete paso
- [ ] Video → yt-dlp si el usuario quiere el clip
