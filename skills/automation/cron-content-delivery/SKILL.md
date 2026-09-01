---
name: cron-content-delivery
description: Deliver recurring daily/weekly content to the user via Hermes cron jobs — language-learning phrases, quotes, reminders, tips. Use when the user wants something sent on a schedule (especially to Telegram), with self-contained scripts, multiple fire times, date-seeded variety, and JSON history for spaced repetition. Covers the script-only (no_agent=true) cron pattern, Telegram-only delivery, the Windows path-duplication pitfall, and the clock-mock verification trap.
---

# Scheduled Content Delivery via Cron

Deliver educational/daily content (phrases, quotes, reminders, tips) to the user on a
schedule. The robust pattern is a **self-contained Python script** that prints UTF-8 to
stdout, run by a **script-only cron** (`no_agent=true`) that delivers stdout verbatim.

## When to use
- "Envíame frases de inglés cada día", "mandame un recordatorio a las 9am", "quiero X en mi Telegram a diario".
- Any recurring content the user wants pushed (not fetched on demand).

## Steps (the verified pattern)
1. **Write the script** to `~/AppData/Local/hermes/scripts/<name>.py`.
   It must print the final message to **stdout** (the cron delivers stdout verbatim).
   Keep it stdlib-only (no pip installs) so the cron always runs.
2. **Vary content per run** deterministically: seed the RNG with the date, and with the
   hour if you run multiple times per day:
   ```python
   import random, datetime
   today = datetime.date.today()
   random.seed(today.isoformat() + ":" + str(datetime.datetime.now().hour))
   ```
   This makes each day (and each schedule) distinct but reproducible for review.
3. **Persist a history JSON** next to the script for spaced repetition / reinforcement:
   append `{"en": phrase, "date": today.isoformat()}` on each run, then re-show items seen
   `>= N` days ago in a `🔁 REFUERZO` block ~50% of the time. Prune to last ~250 entries.
4. **Create the cron** with `cronjob action=create`:
   - `no_agent=true` (script-only; stdout delivered verbatim)
   - `script='<name>.py'`
   - `deliver='telegram'` for Telegram-only, or `'all'` for every connected channel
   - `schedule='0 9 * * *'` (cron expressions; see below)
5. **Multiple fire times = multiple cron jobs.** One cron entry fires ONCE per its
   schedule. For 3 daily times (09/14/20) create **three** cron jobs pointing at the same
   script. Because of step 2, each delivers different content.
6. **Verify before relying on it** (see Verification).

## Cron schedule cheat-sheet
- `0 9 * * *`  daily 09:00  · `0 9,14,20 * * *` daily 09/14/20 (single job, 3 fires)
  → NOTE: `0 9,14,20 * * *` IS valid and fires 3x/day from ONE job. Prefer this over 3
  separate jobs when you don't need per-time distinct seeds; use 3 jobs only when each
  time must be independently reviewable/managed.
- `*/30 * * * *` every 30 min · `0 9 * * 1` Mondays 09:00 · `0 8 * * 1-5` weekdays 08:00.

## Pitfalls (learned the hard way)
- **Windows path duplication.** Writing with a POSIX path like `/c/Users/<USER> GAMES/...`
  can resolve to `C:\c\Users\<USER> GAMES\...` (a duplicated `c`) and land OUTSIDE the
  workspace. ALWAYS use the **native form `C:/Users/...`** (forward slashes, NO leading
  `/c/`) for anything under the Windows user home. After writing, confirm with
  `search_files(target='files', pattern='english_phrases.py')` or `find` that the file is
  at the intended path, and remove any duplicate `C:\c\...` copy.
- **Clock-mock verification trap.** If the target script does `import datetime` and reads
  `datetime.datetime.now()`, patching the test's `mod.datetime = FakeDT` FAILS — the import
  rebinds to the real module, so the script sees real time and all runs are identical.
  Instead monkeypatch the REAL class: subclass `datetime.datetime`, reassign
  `datetime.datetime = FakeDT`, set `FakeDT._fake = datetime.datetime(Y,M,D,H,0)`, then
  `exec_module`. (See scripts/verify_cron_script.py.)
- **`deliver='telegram'` needs a connected gateway.** If nothing arrives, the Telegram
  gateway isn't linked. Use `deliver='all'` only when the user wants every channel.
- **`no_agent=true` + empty stdout = silent.** For content crons you WANT output every run;
  an empty print means nothing is sent (that's the watchdog pattern, not what you want here).
- **Cron jobs are local-only in the TUI.** Delivery only reaches the user via a gateway
  (`telegram`/`all`); the TUI itself is not a delivery channel.

## Content-design tip (for non-native-speaker audiences)
When the user reads a language other than English, render each item as:
`*English phrase*` (bold) · `🔊 /fonetica-en-sonidos-del-espanol/` · `🇪🇸 significado en gris`
· `💡 nota cultural`. Keep phonetics in sounds close to the reader's native language so they
are actually legible. End with a small action nudge ("di cada frase en voz alta 3 veces").

## Verification
Run the script directly first: `cd "<scripts dir>" && python <name>.py`.
Then use the harness in `scripts/verify_cron_script.py` to confirm distinct output per
schedule and required markers, with a mocked clock:
`python scripts/verify_cron_script.py <scripts>/<name>.py "🇪🇸" "🔊" "📂"`

## References
- `references/telegram-delivery.md` — deliver= behavior, gateway requirement, troubleshooting.
