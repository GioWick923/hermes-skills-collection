---
category: media
name: youtube-content
description: "Use when YouTube is or could be relevant — even if not mentioned: pasted video/channel/playlist links, video IDs, @handles, creator lookups, summaries, quotes, translations, topic research, tutorials, talks. Covers transcripts, search, channels, playlists, within-channel search. Not for uploads or account management."
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Also for: searching YouTube, browsing a channel's uploads, listing playlist contents, searching within a channel. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

## Recetas completas (todo LOCAL, sin API key — verificado 2026-09-03)

El stack local (yt-dlp del venv de Hermes + youtube-transcript-api) cubre el 100%
de lo que ofrece TranscriptAPI/skills-sh sin SaaS ni créditos. Usa el python del
venv: `$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/`.

```bash
V="$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts"

# Buscar videos (top N)
$V/yt-dlp 'ytsearch5:QUERY' --flat-playlist --print '%(title)s | %(url)s' --skip-download

# Ultimos videos de un canal (con vistas y duracion)
$V/yt-dlp 'https://www.youtube.com/@HANDLE/videos' --flat-playlist --playlist-end 15 \
  --print '%(title)s | %(view_count)s | %(duration)s' --skip-download

# Buscar DENTRO de un canal
$V/yt-dlp 'https://www.youtube.com/@HANDLE/search?query=TERMO' --flat-playlist \
  --playlist-end 10 --print '%(title)s' --skip-download

# Playlist completa
$V/yt-dlp 'PLAYLIST_URL' --flat-playlist --print '%(title)s | %(url)s' --skip-download

# Transcript (ver Helper Script abajo)
```

Workflows tipicos:
- **Research**: ytsearch → elegir videos → transcript de cada uno → sintetizar.
- **Channel monitoring**: /@handle/videos --playlist-end N → transcript del ultimo.
- **Bulk transcripts**: playlist → loop del helper script por video, append a JSON
  en workspace, agregar al final (no un solo call gigante).

Fallback: si YouTube bloquea la IP local (no es el caso en esta maquina),
TranscriptAPI (transcriptapi.com, free 100 creditos) es el plan B — requiere
`TRANSCRIPT_API_KEY` y header User-Agent de lo contrario Cloudflare 403/1010.

**Manejo seguro de tokens en Hermes**: los runtimes de agente redactan valores
`sk_`/`access_token` de la salida. Patrón correcto: escribir la respuesta HTTP
bruta a un archivo temporal y leer el valor DESDE el archivo al construir la
siguiente request — nunca imprimir el token como paso suelto. Limpiar el temp
despues.

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

Dependencias ya presentes en el venv de Hermes (`youtube-transcript-api`,
`yt-dlp`). En este host `uv run` esta roto (interpreta un python3.11.exe
inexistente en ~/.local/bin) — usa directo el python del venv:

```bash
"$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/python" SKILL_DIR/scripts/fetch_transcript.py ...
```

Si falta la libreria: `"$VENV/python" -m pip install youtube-transcript-api`.

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
"$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/python" SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
"$VENV/python" SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
"$VENV/python" SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
"$VENV/python" SKILL_DIR/scripts/fetch_transcript.py "URL" --language es,en
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps` via the venv python.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Error Handling

- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: `"$VENV/python" -m pip install youtube-transcript-api` and retry.
