---
name: granite-asr
description: "Transcribir audio a texto local con Granite Speech 5.0."
version: 1.0.0
author: Hermes Agent (instalado 2026-08-31)
license: Apache-2.0
platforms: [windows]
metadata:
  hermes:
    tags: [asr, speech-to-text, transcripcion, granite, whisper, local, gpu]
    related_skills: [youtube-content, watch-video, tiktok-download]
---

# Granite ASR (Granite Speech 5.0) — transcripción local

> ASR (voz → texto) local con **RTX 3060** usando `ibm-granite/granite-speech-5.0-470m-turboctc`.
> Apache-2.0, 470M params, arquitectura CTC turbo-rápida. Sin cloud, sin API.

## When to Use
- Transcribir un audio/video a texto (subs, notas, análisis) cuando quieres **local + rápido**.
- Flujo de ASR en el stack de audio (junto a chatterbox/xtts TTS).

## Instalación (ya hecha)
- **Venv:** `C:/Users/<USER>/tools/granite-asr/venv` (dedicado — NO toca chatterbox/xtts).
  - torch 2.13.0+cu126 (CUDA), transformers 5.16.1 (requiere `granite_speech5_ctc`), librosa, soundfile.
- **Modelo:** `C:/Users/<USER>/models/asr/granite-speech-5.0-470m-turboctc` (~904MB).
- **Script:** `C:/Users/<USER>/tools/granite-asr/transcribe.py`.

## Uso (1 comando)
```bash
PY="C:/Users/<USER>/tools/granite-asr/venv/Scripts/python.exe"
"$PY" "C:/Users/<USER>/tools/granite-asr/transcribe.py" "audio.wav|flac|mp3" [--out salida.txt]
```
- Carga audio a 16kHz mono (librosa, evita FFmpeg) → modelo en CUDA → `TRANSCRIPT: <texto>`.

## IMPORTANTE — límite de idioma (honestidad)
- ⚠️ **Granite Speech 5.0 `turboctc` está optimizado para INGLÉS** (tag "English").
- Con audio en **español u otro idioma** la precisión baja notablemente (probado con voz clonada ES → texto aproximado).
- **Para español puro** → mejor usar **Whisper** (multilingüe) o un modelo `granite-speech` multilingüe.
- Usa Granite para **inglés** o donde la velocidad/latencia importe más que la exactitud.

## Por qué NO uso torchaudio aquí
- torchaudio nuevo requiere **torchcodec + FFmpeg** (full-shared DLLs en Windows) → fricción.
- `librosa.load(sr=16000, mono=True)` da el numpy array que el processor/CTC espera, sin FFmpeg.

## Verificación (probado 2026-08-31)
- [x] Modelo descargado (~904MB, ruta canónica)
- [x] Venv dedicado con CUDA (`torch 2.13.0+cu126`, cuda available=True)
- [x] `AudioProcessor` → key `input_features` (no input_values) — model CTC usa features
- [x] Transcripción real en GPU (devolvió texto; precisión baja en ES por modelo English-only)
- [ ] (para ES) cambiar a Whisper o modelo multilingüe

## Pitfalls
- `input_features` vs `input_values`: GraniteSpeaker usa `input_features` (corregido).
- `transformers` DEBE ser >=5.16 (el 5.2 no reconoce `granite_speech5_ctc`).
- torch CUDA con `uv` instala CPU por default → usar `--index-url https://download.pytorch.org/whl/cu126` + `--reinstall`.
- `librosa` decodifica wav/flac/mp3 sin FFmpeg; para códecs raros, convertir antes.
