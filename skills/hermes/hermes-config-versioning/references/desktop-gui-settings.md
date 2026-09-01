# Hermes Desktop GUI Settings ≠ config.yaml

## Core gotcha
Many "change the X in Hermes" requests from a **desktop-app (Electron GUI)** user
are about settings that live in the app's `localStorage` — a **LevelDB** — NOT in
`config.yaml`. `config.yaml` only governs the **CLI/TUI** path. Editing the
wrong layer silently does nothing for a GUI user.

## Two different "finish" sounds (real example that bit us)
- `display.bell_on_complete: true` in `config.yaml` → emits a terminal `\a`
  bell from the **CLI/TUI** when a turn finishes. Works over SSH. Does NOT apply
  to the desktop GUI.
- The desktop GUI's "turn finished" cue is a **14-variant preset bank**
  defined in `apps/desktop/src/lib/completion-sound.ts`
  (`COMPLETION_SOUND_VARIANTS`, ids 1–14, default 1 = "Two-note comfort").
  Variant ids:
  1 Two-note comfort (default) · 2 Glass ping · 3 Soft marimba ·
  4 Tri-tone message · 5 Airy whoosh · 6 Discovery cluster · 7 Systems online ·
  8 IBM terminal · 9 Modem chirp · 10 Wind chimes · 11 Singing bowl ·
  12 Harp lift · 13 Sonar ping · 14 Music box
  - Persisted as `localStorage["hermes.desktop.completionSoundVariantId"]`,
    value is the string id (e.g. `"9"`).
  - UI: **Settings → Appearance → Completion sound** ("Plays when an agent turn
    finishes"). Auto-saves on select; no restart needed.

## Where the GUI store lives (Windows)
`%APPDATA%\hermes\Local Storage\leveldb`
(e.g. `C:\Users\<user>\AppData\Roaming\hermes\Local Storage\leveldb`)
The app also keeps a partition db at
`%APPDATA%\hermes\Partitions\hermes-embed\Local Storage\leveldb`.

Note: this is the SAME `Roaming\hermes` dir the parent skill says "do NOT
version" — but the *reason* there is "it's Electron cache." The persistence
mechanism detail (LevelDB + localStorage keys) lives here.

## The LOCK constraint (why you can't just edit it)
Electron holds an **exclusive LOCK** on the LevelDB while the app runs. Any
external open fails:
- `classic-level` (node) → `LEVEL_DATABASE_NOT_OPEN` / `LEVEL_ITERATOR_NOT_OPEN`.
- Opening requires the app to be fully closed. BUT closing the desktop app also
  **terminates the current chat session** (the TUI runs inside that Electron
  process) — so you cannot kill-it / edit / relaunch from within a live session.

## Safe change paths (in order of preference)
1. **In-app Settings UI (recommended).** For any GUI setting that has a
   Settings control, just tell the user the 2–3 click path. Zero risk.
2. **CDP injection.** Relaunch Hermes with `--remote-debugging-port=9222`
   (requires closing + reopening the app once), then drive `localStorage` via
   Chrome DevTools Protocol:
   `Runtime.evaluate` → `localStorage.setItem('hermes.desktop.completionSoundVariantId','9')`
   then reload. Only worth it when there is NO Settings control or the user
   explicitly wants automation.
3. **Do NOT** hand-edit the LevelDB `.ldb`/`.log` files — format is
   Electron-internal and corruption is likely.

## Reading it (read-only, for diagnosis)
`node` ships with Hermes at `C:\Users\<user>\AppData\Local\hermes\node\node.exe`.
`classic-level` opens the db but WILL fail with the LOCK error above while the
app runs. Use it only after the app is closed (separate session):
```js
const { ClassicLevel } = require('classic-level');
const db = new ClassicLevel('C:/Users/<user>/AppData/Roaming/hermes/Local Storage/leveldb', { createIfMissing:false });
await db.open();
for await (const [k,v] of db.iterator()) {
  const ks = Buffer.from(k).toString('utf8');
  if (ks.toLowerCase().includes('completion')||ks.toLowerCase().includes('sound'))
    console.log(ks, '=', Buffer.from(v).toString('utf8'));
}
```

## User preference embedded here
When the user says "cambialo tu" / "hazlo tu" / "ponle X" for a config
change, **execute the edit (with a backup first), do not just hand back steps.**
For `config.yaml` changes: `cp config.yaml backups/config.yaml.bak.<ts>` then edit
via a `python` heredoc (the file is locked against write_file/patch for
security). For GUI-localStorage settings: prefer the in-app path and tell them
exactly what to click, OR do CDP if they relaunch with a debug port. Never claim
a GUI setting is "done" without the user confirming the visible effect (you
cannot observe the Electron localStorage from outside).
