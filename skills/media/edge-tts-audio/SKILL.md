---
name: edge-tts-audio
description: "Use for TTS. Edge neural voices via edge_tts, no GPU/key."
version: 1.0.0
license: MIT
platforms: [windows]
---

# edge-tts — free neural TTS (no GPU, no key)

> Text-to-speech using Microsoft's edge neural voices through the `edge_tts` Python
> package. Already installed in the Hermes venv (`edge_tts` 7.2.7). No VRAM, no
> API key, just network to Microsoft. Voices sound far better than `pyttsx3`/`gTTS`.

## When to use
- You need the agent to SPEAK a reply (voice output), not just type it.
- Character/anime/roleplay voices (modulate rate, pick a young female ES voice).
- Quick narration, accessibility, or a TTS demo without standing up a GPU model.
- Do NOT use for: offline TTS (needs network), voice cloning (use omnivoice), or
  batch enterprise TTS (rate-limits apply).

## Basic usage (validated working call)
```python
import asyncio, edge_tts

async def say(text, voice="es-MX-DaliaNeural", out="out.mp3"):
    # rate is OPTIONAL; pitch is intentionally omitted (see pitfalls)
    comm = edge_tts.Communicate(text, voice, rate="+12%")
    await comm.save(out)

asyncio.run(say("¡Hola onii-chan, soy tu asistente anime!"))
```
- The Hermes venv python: `C:/Users/<USER>/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`
- Playback: `ffplay -nodisp -autoexit out.mp3` (ffplay lives in `hermes/tools/ffmpeg/bin/`).

## Pitfalls (costaron varios intentos fallidos — no repetir)
- **Never pass `pitch=` to `edge_tts.Communicate`.** It raises `ValueError: Invalid pitch '+15%'`
  (the validator expects the `^[+-]\d+Hz$` shape, e.g. `+20Hz`) — and `+20Hz` then fails with
  `NoAudioReceived`. The pitch control is broken in this lib; modulate ONLY with `rate`.
- **Avoid SSML / `xml:lang` wrappers.** Building `<speak><voice name=...><prosody...>` raises
  `NoAudioReceived`. Plain string + the `voice=`/`rate=` constructor args is the only reliable path.
- **`NoAudioReceived` is usually a BAD PARAM, not a network outage.** First isolate by running
  `edge_tts.Communicate("test", "en-US-AriaNeural").save("x.mp3")` with no extra args — if that
  succeeds, your network is fine and the failing call had a bad voice/param.
- **ES voices work fine** once you drop `pitch`. Confirmed-good: `es-MX-DaliaNeural`,
  `es-ES-ElviraNeural`, `es-US-PalomaNeural` (see references/voices.md).
- **Run each `Communicate().save()` in its own `asyncio.run`** (or `await` sequentially in one loop).
  Firing many in a tight loop occasionally drops connections; one-per-run is safest.

## Anime / character effect
- Use `rate="+12%"` for an energetic, slightly-fast delivery. Do NOT try `pitch` for "kawaii".
- Pick a young female ES voice (Dalia = warm MX, Elvira = expressive ES). See references/voices.md.
- For a live "she is talking" feel, play the mp3 the instant it finishes saving, then trigger the
  on-screen character animation (separate concern — see the orb PTT skill for animation patterns).
