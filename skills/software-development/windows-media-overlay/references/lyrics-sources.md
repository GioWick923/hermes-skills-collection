# Lyrics sources: LRCLIB -> Genius fallback recipe

## Source chain
1. **LRCLIB synced** (`https://lrclib.net/api/search?track_name=&artist_name=`) — pick the
   first result with `syncedLyrics`; also keep `plainLyrics` as a fallback field.
   Try title/artist VARIANTS (raw, strip parenthetical/bracket suffixes, first artist on
   `&`/`,`, cross-combine). Stop at the first variant yielding sync.
2. **LRCLIB plain** — results without sync still give usable text.
3. **Genius** — tracks that are censored, unregistered, or simply unpopular are absent
   from LRCLIB entirely; Genius almost always has them.

Cache EVERY result in SQLite (including misses) keyed by `artist||title` lowercased, and
retry the LRCLIB fetch 1-2 times on network failure before storing. Expose a manual
"clear cache and search again" action so a cached miss is recoverable.

## Genius scraping (no API key)
1. Build candidate URLs from slugged artist-title (`/Artist-Title-lyrics`, plus
   `-remix-lyrics`, `-acoustic-lyrics`). Slug = strip parenthetical suffixes, keep
   alnum+dash, spaces to dashes.
2. Slugs often don't match (feat. credits, punctuation). Resolve the real page via
   DuckDuckGo HTML endpoint: `https://html.duckduckgo.com/html/?q=<artist title genius lyrics>`
   with a browser User-Agent; regex out `href="...genius.com...-lyrics..."` links,
   unescape, strip tracking params, dedupe against the guessed slugs.
3. Fetch with a desktop Chrome User-Agent (default urllib UA gets blocked/empty).
4. Extract: split HTML on `<div ... data-lyrics-container="true" ...>`, take up to the
   matching `</div>`, convert `<br>` to newlines, close tags to newlines, strip all
   remaining tags, `html.unescape`, collapse 3+ newlines. Reject chunks starting with
   login prompts; require total length > ~80 chars.
5. Clean the header junk Genius prepends: `N Contributors` through the next blank
   line/section, the word `Translations`, and the glued language list
   (`EspañolPortuguêsPolski...`) — match it as 3+ glued Capitalized words. Keep
   `[Verse 1]` / `[Chorus]` section markers; they are useful orientation.
6. Accept only if the cleaned text is still > ~60 chars.

## Rendering unsynced lyrics (plain mode)
- No timestamps exist, so drive the view from playback position: page of N lines
  (the overlay's line count), advancing every ~4s per line (`page = pos // (4*N)`),
  clamped to the last page, frozen when playback is paused.
- Render as PlainText, side-line styling (Light weight, low alpha), so plain mode
  never competes visually with synced karaoke mode.
- First paint can be seconds behind the song start; an instant '♪ Title — Artist'
  placeholder on song change covers the gap.
