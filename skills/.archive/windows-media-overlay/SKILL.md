---
name: windows-media-overlay
description: Use when building a Windows SMTC/PySide6 overlay.
---
# Windows Media Overlay (SMTC + PySide6)

Build a desktop overlay that reads what is playing on Spotify (or any media app) and shows it
translucently above other windows, external to the media app (no injection, no ban risk).

## When to use
- User wants a "now playing" / lyrics / karaoke overlay on Windows 11.
- Need playback state without OAuth/dashboard: Windows already exposes it via SMTC.

## Procedure
1. Install deps: `pip install winsdk PySide6 deep-translator` (Python 3.11).
2. Read media state via winsdk SMTC using references/smtc_snapshot.py. Keep ONE persistent
   asyncio loop on a daemon thread; submit snapshots with
   `asyncio.run_coroutine_threadsafe(...).result(timeout=3)` (see pitfall).
3. Pick the Spotify session by matching `"spotify"` in `source_app_user_model_id` (lowercased).
   STICKY: no Spotify session -> return None; never fall back to another app's session
   (see pitfall on transitions).
4. Build overlay in PySide6: `FramelessWindowHint | WindowStaysOnTopHint | Tool`,
   `WA_TranslucentBackground`, `setWindowOpacity`. See pitfall on the flag choice.
5. Drive UI from Qt signals emitted by worker threads (state tick ~0.4s, song-changed,
   lyrics-ready).
6. Lyrics fetch chain (references/lyrics-sources.md has the full recipe):
   a. LRCLIB synced `.lrc` (karaoke), trying title/artist VARIANTS;
   b. LRCLIB plain text;
   c. Genius scraped plain text (censored / unregistered / unpopular tracks are absent
      from LRCLIB entirely). Cache every result (including misses) in SQLite.
   Unsynced lyrics render as pages of N lines auto-advancing with playback time (~4s per
   line, freeze on pause); add a tray "search lyrics again" action that clears the cache
   and re-requests, so a cached miss is recoverable.
7. Translate via deep_translator once per track; skip when the text is already Spanish or
   the translation comes back identical to the original (see pitfall).
7b. Drive a separate fast QTimer (~30ms) for animation so ease-out line transitions are
   fluid — the 0.4s state tick alone makes them jump.
8. Package with PyInstaller per references/packaging.md (clean venv, bundled fonts,
   kill-running-app-first, artifact verification). Font recipe and the LRCLIB->Genius
   lyrics chain live in references/packaging.md and references/lyrics-sources.md.

## Pitfalls (generalizable)
- **`tl.last_updated_time` in winsdk is a `datetime.datetime`, NOT an object with
  `.ms_since_epoch`** — call `.timestamp()` on it. The original `.ms_since_epoch / 1000.0`
  raises AttributeError that a bare `except Exception: return None` swallows, so `get_state()`
  silently returns None and you burn time thinking SMTC is unavailable.
- **Always `import time` in the SMTC module** — the snapshot references `time.time()` for the
  fallback timestamp; a missing import raises NameError swallowed by the same broad except, again
  yielding None.
- **When `get_state()` returns None unexpectedly, run the raw snapshot with
  `traceback.print_exc()` instead of the swallowing wrapper** — the silent except hides the real
  AttributeError/NameError; the diagnostic reveals it in one shot.
- **For a floating always-on-top overlay use `Qt.Tool`, not `Qt.SubWindow`** — `SubWindow` does
  not stay above normal app windows reliably on Windows 11; `Tool` (+ `WindowStaysOnTopHint`) does.
- **Do not verify a Qt GUI app from the agent's own terminal on Windows** — the MSYS/git-bash
  runtime kills long-running or sleeping GUI processes and returns RC=127 with empty stdout, making
  it look like the app crashed. Have the user run `python app.py` from their own cmd/PowerShell
  while the media app is playing; read `%LOCALAPPDATA%/<App>/overlay.log` for diagnostics.
- **Keep ONE persistent asyncio loop on a daemon thread for all winsdk calls** — submit with
  `asyncio.run_coroutine_threadsafe(coro, loop).result(timeout=3)`. WinRT/COM wants thread
  consistency; a fresh loop per poll also works but adds create/teardown churn every 0.4s.
  Never run winsdk on the Qt main thread.
- **Select sessions STICKILY: if no Spotify session exists, return None — never fall back to
  `get_at(0)`** — during a track transition Spotify's SMTC session vanishes for a moment, and
  a fallback grabs another app's media session, producing a ghost track that breaks position,
  lyrics, and the song-change flow.
- **Never 'drift-correct' the interpolation anchor against `tl.last_updated_time`** — that
  timestamp only changes on seek/play/pause, NOT while playing, so treating it as a drift
  signal rewinds the estimated position on every poll and the karaoke stops advancing.
- **Import `QShortcut` from `PySide6.QtGui`, not `QtWidgets`** — in current PySide6 it lives in
  QtGui; the wrong import only surfaces at app launch (often first in the packaged exe) and
  crashes startup.
- **Package from a venv holding ONLY the app's dependencies** — PyInstaller follows transitive
  imports, so building from an env that also carries a data/ML stack inflates the exe from
  ~60MB to 600MB+ of dead weight.
- **Kill any running copy of the app before rebuilding** — a live exe locks `dist/<name>.exe`;
  the build then fails with WinError 5 at the final copy while the log still reads successful,
  leaving the stale binary in dist/.
- **After every build verify the artifact landed: timestamp AND size of the exe in dist/** —
  a BUILD_DONE line is not proof; a blocked copy leaves the previous binary in place.
- **After several patches to one file, compile AND grep every call site of any signature you
  changed** — a stale duplicate call unpacking the old tuple shape (or a Signal declared with N
  args but emitted with N+1) looks fine on re-read and crashes only at runtime; also re-read
  whole init blocks — a patch anchored on one CREATE TABLE line can drop its neighbor.
- **Search LRCLIB with title/artist VARIANTS and strip enhanced-LRC tags** — Spotify metadata
  (accents, 'feat.', parenthetical suffixes) fails exact match and the track silently degrades
  to plain unsynced lyrics; inline word-timing tags `<mm:ss.xx>` must be removed or they leak
  into displayed lines. Retry the fetch once or twice on network failure before storing a miss.
- **Render the translation as a smaller nested span under the ACTIVE line only** —
  `<br><span style='font-size:62%;font-style:italic'>` with RichText on the active label and
  PlainText on the rest; a full-size second line inside every label overlaps neighboring
  lines and destroys legibility.
- **`html.escape()` EVERY variable text placed inside RichText, and force
  `setTextFormat(PlainText)` on any label not carrying markup** — a QLabel that once rendered
  RichText keeps that mode; plain lyrics containing `&`, `<` or `>` then render BLANK, which
  reads as 'lyrics missing' and costs a false hunt for a fetch bug.
- **Skip the translation entirely when it equals the original line** — the es->es endpoint
  returns the input unchanged for Spanish songs, so nesting it duplicates the line on top of
  itself; compare case-insensitively before nesting and fall back to plain text.
- **Show an instant placeholder ('♪ Title — Artist') on song change and keep the
  no-session sleep short (~0.3s)** — LRCLIB+translation takes seconds; without the
  placeholder a track change looks like the app stopped recognizing songs.
- **Add a drop shadow (QGraphicsDropShadowEffect, small blur ~14, offset 1px, black alpha
  ~150) under overlay text** — translucent text over bright backgrounds is illegible
  without a subtle halo; keep it light or it looks smeared.
- **Expose per-element text colors (active vs side lines) via a color dialog persisted in
  config** — users tune overlay colors per wallpaper; hardcoding one accent color forces a
  rebuild for a cosmetic change.

## Verification (real, not theory)
- SMTC: `python -c "import smtc,json;print(json.dumps(smtc.get_state(),ensure_ascii=False,indent=1))`
  while media plays — must print title/artist/status/pos, not `None`.
- LRCLIB: fetch a known song; assert `len(sync) > 0`.
- Translation: assert returned list is non-empty Spanish.
- Genius fallback: call the scraper directly for a well-known song and assert >80 chars
  extracted; test an obscure title through the full chain.
- GUI: only the user can confirm visually (agent terminal can't host it) — give them the run
  command and the log path.
