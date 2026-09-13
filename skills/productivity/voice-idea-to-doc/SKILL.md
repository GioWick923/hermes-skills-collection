---
category: voice-idea-to-doc
name: voice-idea-to-doc
description: "Toma ideas dictadas (texto desde Telegram/WhatsApp/DM) y las convierte en un documento estructurado (markdown) en docs/, con un paso de refinamiento en 2 etapas (no 1-shot)."
version: 1.0.0
author: Gio / Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [voice-notes, dictation, telegram, second-brain, drafting, productivity]
    related_skills: [note-taking, hermes-agent]
---

# Voice Idea → Structured Doc

Flujo para convertir ideas dictadas (llegadas por Telegram/DM como texto,
transcritas previamente por la app de dictado del usuario) en un documento
util, sin intentar "1-shot" todo de una vez.

Basado en el patrón de r/HermesAgent (post "I dictate messy ideas into my phone
and Hermes turns them into structured Proof documents") y su variante 2-shot.

## Cuándo usar
- El usuario manda un bloque de texto desordenado (dictado) y pide convertirlo
  en documento, nota, borrador, plan o "proof".
- El usuario dice "estructura esto", "hazme el doc de...", "pasa esto a limpio".

## Flujo (2-shot, NO 1-shot)
1. **Recibir + aclarar (opcional):** si el texto es ambiguo sobre el formato
   deseado (doc libre vs plan vs lista vs proof), pregunta SOLO el formato.
   No reescribas aún.
2. **Esqueleto:** genera primero un esqueleto (titulares/secciones) y confírmalo
   brevemente. Esto evita que el modelo "adivine" mal la intención.
3. **Redacción final:** una vez confirmado el esqueleto, rellena el documento.
4. **Guardar:** escribe el `.md` en `docs/` (ver rutas abajo).
5. **Enlazar (opcional):** si el usuario usa Obsidian, el archivo ya es
   compatible; menciona la ruta para abrirlo.

## Rutas de salida
- Carpeta base de docs: `C:\Users\<USER> GAMES\AppData\Local\hermes\docs\`
  (crear con `mkdir -p` si no existe).
- Nombre: `AAAA-MM-DD-<tema-corto>.md` (p. ej. `2026-07-12-plan-viaje.md`).
- Si el doc es un "segundo cerebro" reutilizable, además crea un zettel en
  `second-brain/zettel/` y añade línea al índice `second-brain/README.md`
  (ver regla en SOUL.md de cada perfil).

## Formato del documento
```markdown
# <Titulo>

## Contexto / por qué
<...>

## Puntos clave
- ...

## Detalles / pasos
1. ...

## Próximos pasos
- [ ] ...
```

## Scripts empaquetados e invocación del CLI de Hermes
Este skill trae `scripts/save_doc.py`, `scripts/ingest_url.py` (YouTube/URL ->
transcribe -> zettel) y `scripts/morning_digest.py` (digest por Telegram).
Cuando esos scripts llaman al CLI de Hermes, usar los comandos REALES:
- **Resumir/preguntar sin interacción:** `hermes chat -q "PROMPT" -Q`
  (NO existe `hermes ask`).
- **Enviar a Telegram:** `hermes send -t telegram "MSG"` — requiere home channel
  (`hermes config set TELEGRAM_HOME_CHANNEL <chat_id>`) o usar
  `hermes send -t telegram:<chat_id> "MSG"`. Ver targets: `hermes send --list telegram`.
  (NO existe `hermes message`.)
- yt-dlp va en venv aislado (`tools/ingest_venv`); su carpeta `Scripts/` debe ir
  al frente del `PATH` ANTES de importar `watch-video/download.py` (usa `shutil.which`).

## Anti-patrones
- No hagas 1-shot ciego si el formato importa: confirma esqueleto primero.
- No infles con jerga; el usuario dicta ideas, quiere claridad.
- No guardes secretos en docs/.
- No metas todo en memories/MEMORY.md; usa second-brain si es reutilizable.
- **`subprocess.run` sin chequear `returncode` da éxito falso:** un comando CLI
  inexistente sale rc!=0 pero NO lanza excepción. Validar siempre `r.returncode==0`
  antes de imprimir/reportar "enviado" u "OK".
