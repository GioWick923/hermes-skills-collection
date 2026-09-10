---
name: spotify-pc-control
description: "Controla Spotify local PC via SMTC: play/pause/next/status."
version: 1.0.0
---

# Spotify control local (SMTC)

Control de la app Spotify (Microsoft Store) via Windows System Media Transport Controls.
**Ventaja:** cero dashboard, cero OAuth, funciona YA. **Límite:** no hay búsqueda/playlists/cola (eso requiere Web API + app en developer.spotify.com/dashboard).

## Scripts
- `C:/Users/<USER>/spotify_ctl.py` — status | play | pause | toggle | next | prev
- `C:/Users/<USER>/spotify_smtc.py` — debug: lista TODAS las sesiones multimedia

Uso: `python "C:/Users/<USER>/spotify_ctl.py" pause`

## Requisitos
- `winsdk` instalado (pip install winsdk) — HECHO 2026-09-08 en python Hermes runtime.
- Spotify corriendo (versión Store: SpotifyAB.SpotifyMusic).

## Gotchas (no re-aprender)
1. `sessions.size` (property), NO `.count` (método que exige argumento en winsdk).
2. Estado 5 = "Cambiando pista" (transitorio, no es error). Mapear en STATUS_NAMES.
3. PlaybackInfo no tiene `repeat_mode`, solo `auto_repeat_mode`.
4. Tras enviar comando, esperar ~2s antes de verificar estado.
5. Winsdk decodifica stdout como utf-8: si taskkill/salida con acentos revienta, usar tasklist + grep.
6. taskkill via subprocess python (no bash) para matar procesos con salida cp1252.

## Para lo avanzado (playlists/search/queue)
Hermes trae toolset nativo `spotify` (plugin backend, 7 tools) + `hermes auth spotify` (PKCE loopback en http://127.0.0.1:43827/spotify/callback). Requiere que Gio cree app en developer.spotify.com/dashboard (Web API, redirect URI exacto) y pegue SPOTIFY_CLIENT_ID/SECRET en $LOCALAPPDATA/hermes/.env. Gio no completó este paso (2026-09-08); el dashboard mostraba login wall y su Brave no es Chromium para perfil real.