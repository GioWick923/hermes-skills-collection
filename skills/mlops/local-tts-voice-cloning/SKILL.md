---
category: mlops
name: local-tts-voice-cloning
description: "Use when running local TTS voice cloning on Windows CUDA."
version: 1.0.0
license: MIT
platforms: [windows]
---

# Local TTS Voice Cloning (Windows CUDA)

Class-level workflow: install + run open-weight TTS voice-cloning models locally (Gio's RTX 3060 12GB), clone a reference voice, deliver audio to Telegram.

## Golden rule: model ↔ language match BEFORE generating

Verify the target language is actually supported by the chosen model variant BEFORE generating, not after delivering. Delivering wrong-language audio = wasted GPU cycle + user correction.

## Installed stacks (2026-08, both live side-by-side, do NOT delete either)

### Chatterbox (`C:/Users/<USER>/tools/chatterbox`, venv `venv/`)
- torch cu126 CUDA. Dos variantes:
- **Español: SIEMPRE `ChatterboxMultilingualTTS` con `language_id='es'`** — `ChatterboxTurboTTS` es anglocéntrico y produce 'portugués' con texto español. Solo un código `es` (genérico, sin variante es-MX local; el acento lo domina el clip de referencia).
- Turbo API: `generate(text, audio_prompt_path=ref, exaggeration=0..1)` (exaggeration = drama; 0.3 neutro, 0.8 amenazante)
- Multilingual API: `generate(text, language_id='es', audio_prompt_path=ref, exaggeration=ex)`
- torchaudio 2.11 requiere torchcodec para load/save → usar `soundfile` (`sf.read`/`sf.write`, tensors a numpy) en su lugar.
- Validar idiomas: `from chatterbox.mtl_tts import SUPPORTED_LANGUAGES` (23 códigos).

### XTTS-v2 (`C:/Users/<USER>/tools/xtts`, venv `xtts/`)
- Fork mantenido: `pip install coqui-tts` (idiap, MPL-2.0, wheels Windows). Desde 0.27.4 torch NO viene incluido: instalar torch+cu126 aparte en ese venv.
- 17 idiomas, español incluido; segunda alternativa para acento latino (duelo A/B contra Chatterbox con el MISMO clip y texto).

## Reference clips (calidad = clonación)
- Clip de 10–15 s de voz PURA del objetivo (sin música/fx/silencios largos). Verificar energía por segundo con soundfile antes de usar.
- Un clip enviado por el usuario directamente vale más que un segmento extraído a ciegas de un video largo (lección: el seg 30-45 a ciegas clonó mal).

## Descarga de audio fuente
- Para scripting usar `uvx yt-dlp -x --audio-format wav` directo. NO usar `omniget.exe` en comandos no interactivos: lanza su GUI y bloquea el shell indefinidamente.

## Entrega por Telegram
- `MEDIA:` exige ruta Windows NATIVA (`C:/Users/...`); rutas MSYS `/c/Users/...` se rechazan con "Skipping unsafe MEDIA directive path" (silencioso, solo en gateway.log).
- Convertir WAV→OGG/Opus para reproducción nativa: `ffmpeg -i x.wav -c:a libopus -b:a 64k x.ogg`. Copiar a `$LOCALAPPDATA/hermes/cache/` antes de emitir MEDIA.
- Confirmar entrega con el usuario; si falla, verificar `logs/gateway.log` (`grep -a "MEDIA directive"`).

## Plantilla
Ver `templates/gen_clone.py` — script base de generación (leer ref con soundfile, generar 2 tomas con exaggeration distinto, guardar).

## Pitfalls
- `python3` no existe en Windows; usar el binario del venv por ruta absoluta.
- Generación larga → background + notify_on_complete; verificar con `nvidia-smi` que el modelo cargó en GPU.
- Frases del texto: escribir español neutro/latino si se busca ese acento (el modelo genérico tiende a castellano).
