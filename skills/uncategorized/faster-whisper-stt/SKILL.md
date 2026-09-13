---
name: faster-whisper-stt
description: "Use when you need STT. Transcribe audio with faster-whisper."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
---

# Faster Whisper STT — local speech-to-text

> Transcribe microphone or audio file audio to text using the `faster_whisper` library (a C++/Python binding of Whisper). Optimized for low latency and multilingual support, including Spanish.

## When to Use
- You need real-time or near-real-time transcription from a microphone.
- You want a fully local solution without API calls or external services.
- The spoken language is Spanish or any language supported by Whisper multilingual models.

## Setup
1. Ensure the Hermes environment has Python and the `faster_whisper` package installed.
   - Verify: `python -c "from faster_whisper import WhisperModel; print('OK')"`
2. If missing, install via pip:
   ```bash
   pip install faster-whisper
   ```
3. (Optional) For GPU acceleration, install a CUDA-enabled build:
   ```bash
   pip install faster-whisper[gpu]  # or compile from source with CUDA support
   ```
   Verify GPU detection with `torch.cuda.is_available()` if using torch.

## Procedure
1. **Select model size** – trade‑off between speed and accuracy.
   - `tiny` / `base`: fastest, lower accuracy.
   - `small`: good balance (recommended start).
   - `medium` / `large-v2`: higher accuracy, higher RAM/VRAM and latency.
2. **Initialize the model** once per session.
   ```python
   from faster_whisper import WhisperModel
   model = WhisperModel(
       model_size_or_path="small",  # change as needed; small on GPU is a good balance for Spanish
       device="cuda" if torch.cuda.is_available() else "cpu"
       compute_type="float16" if torch.cuda.is_available() else "int8",
   )
   ```
3. **Capture audio** (16 kHz mono, float32 in range [-1, 1]).
   Using `sounddevice`:
   ```python
   import sounddevice as sd
   import numpy as np
   samplerate = 16000
   duration = 5  # seconds to record
   recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
   sd.wait()
   audio = recording.flatten()
   ```
   Ensure the correct input device with `sd.query_devices()` and set `device=` if needed.
4. **Transcribe**.
   ```python
   segments, info = model.transcribe(
       audio,
       beam_size=5,
       language="es",          # set to None for auto-detection
       vad_filter=True,        # drop silence; set False to keep pauses
   )
   text = " ".join(seg.text for seg in segments)
   ```
5. **Output** – return or print `text`. Optionally include detected language and probability from `info`.

## Verification
- Run the procedure with a known phrase in Spanish.
- Measure wall‑clock time from start of transcription to result; aim for < 2 s on CPU with `small` model, < 1 s on GPU.
- Compare output to expected text; adjust model size or VAD settings if errors are systematic.

## Pitfalls
- Using a model too large for available RAM causes swapping or crashes; start with `small`.
- If the microphone is not configured or accessible, `sd.rec` will raise an error or capture silence. Verify with `sd.query_devices()` and grant app microphone permissions in Windows Settings.
- On Windows, the default `sounddevice` backend may require the latest audio drivers; outdated drivers can produce noisy or zero‑filled buffers.
- Forcing `language="es"` when the audio is another language reduces accuracy; omit the parameter or set `language=None` for auto‑detection.
- The VAD filter may cut off very soft speech; if you lose beginnings/ends of utterances, set `vad_filter=False` and post‑process silence.
- `faster_whisper` expects mono audio; stereo input must be averaged or one channel selected.

## Flujo probado en esta máquina (RTX 3060, Windows) — 2026-09-12
- Python con faster_whisper 1.2.1: `C:/Users/<USER>/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`.
- Micrófono: **device index 1** en sounddevice (`Micrófono (Logi USB Headset)`, MME). Verificar con `sd.query_devices()`; el default ya es 1.
- Modelo: `small` + `device='cuda'` + `compute_type='float16'`. Modelos ya descargados en `~/.cache/huggingface/hub`: tiny, base, small (Systran). Carga ~1.3s (cachear el modelo por sesión, NO recargar por clip). Transcripción de clip 7s: **0.1–1.1s**.
- Siempre `language='es'`, `beam_size=5`, `vad_filter=True` (recortar silencios).
- Grabar con `sounddevice` a 16 kHz mono float32 → guardar WAV temporal con módulo `wave` (int16) → pasar path a transcribe.
- Hermes config ya fijada: `stt.enabled: true`, `stt.provider: local`, `stt.language: es`, `stt.local.model: small` (antes estaba `language: en` = causa de malas transcripciones; backup en `config.yaml.bak.stt-es.*`). Cambios requieren reinicio de sesión Hermes.
- Granitespeech turboctc (skill granite-asr) es EN-only: NO usar para español.
- Fallback en config `openai whisper-1` sin GROQ/OPENAI key no sirve aquí: dejar provider=local.

## Dictado global F9 (herramienta construida 2026-09-12)
- Script: `C:/Users/<USER>/tools/stt-es/mic_hotkey.py` + `dictar_start.bat` / `dictar_stop.bat`.
- F9 toggle: graba → suelta → faster-whisper small/es CUDA → pega por Ctrl+V en la app activa. Pitos: agudo=grabando, doble agudo=pegado, grave=vacío.
- Dependencias ya en venv hermes: keyboard, pyperclip, sounddevice, faster-whisper. Modelo cacheado (carga solo 1ª vez).
- Hotkey Ctrl+B push-to-talk de Hermes es SOLO CLI/TUI — el desktop no lo tiene; por eso existe esta herramienta.
- Prueba E2E sin voz humana: lanzar servicio → keyboard.press_and_release('f9') desde otro proceso → log muestra ciclo completo. Transcript real verificado inyectando WAV TTS a transcribe_and_paste() (8.1s audio → texto correcto ES → clipboard).
- ⚠️ Gotcha: si el log dice `silencio (pico 0.0000)` en TODOS los devices (MME/DirectSound/WASAPI + meter WASAPI sistema = 0), el mic está muteado/a 0/interceptado a nivel Windows — NO es bug del script. Permisos ConsentStore deben estar Allow.
- Para autostart: Win+R → shell:startup → copiar dictar_start.bat.
- AUTOSTART con Hermes (preferido): hook en `~/.hermes/hooks/orbe-autostart/` con `HOOK.yaml` (events: [gateway:startup]) + `handler.py` que lanza `ptt_button.py` con pythonw del venv y flag DETACHED_PROCESS (0x8), previniendo duplicados (chequea Win32_Process por CommandLine '*ptt_button*'). El gateway emite `gateway:startup` en run_startup.py:1245. Verificar: al arrancar Hermes el orbe aparece; si ya corre dice 'ya corre'. El orbe TAMBIEN está en Windows Startup (orbe_start.bat) -> el chequeo anti-duplicado evita doble instancia; si se quiere SOLO con Hermes, borrar orbe_start.bat del Startup folder.

## Botón flotante PTT "Orbe" v3 (rewritten 2026-09-12, coreografía yui540)
- Archivo: `C:/Users/<USER>/tools/stt-es/ptt_button.py` (backup v1 en ptt_button_v1.bak.py). Launcher: `orbe_start.bat`. Autostart: copiar el .bat a `shell:startup`.
- Render: **ventana Win32 PURA** (CreateWindowExW + UpdateLayeredWindow, clase `HermesPTTOrb`) con alpha por-píxel REAL. NO usar tkinter+transparentcolor: tkinter pinta su ventana opaca encima del bitmap layered => cuadrado visible (probado, roto).
- Pil render: supersampling 2x; glow = cola gaussiana matemática; anillos y EQ reactivos.
- v4 (2026-09-12): cuerpo POR ESTADO (azul idle / ROJO rec-trans) + micro vintage marfil + rayos neón rojos dinámicos + aura casi invisible idle/roja rec.
- v7 (2026-09-12): micro ya NO se ve recortado/PNG. Extraído a `_make_mic(state)` (sprite aparte): volumen degradado vertical (arriba claro/abajo oscuro) + GLOW del color de estado (azul idle / rojo rec, blur R2*0.12, alpha 35%) + SOMBRA PORTADA oscura difuminada (blur R2*0.045, alpha 85%, desplazada +3SS/+5SS). Se compone ENCIMA del cuerpo (msize 0.88) para que la sombra caiga sobre el vidrio. Verificar: conteo numpy en sprite mic -> ~43% sombra oscura alrededor + glow presente.
- Estados visuales: idle = aurora glass tenue (aura casi invisible, alpha 45), rec/trans = ORBE ROJO + neón dual-tone (cuerpo+rim cian/magenta+anillos+aura rojos, rayos neón rojos que estallan con nivel de voz).
- Rayos neón rojos: 4 puntas (35/135/225/315°), zigzag animado, alpha piso 90+ en rec (se ven aunque hables bajito), casi invisibles (alpha 10) en idle.
- Micrófono VINTAGE: rejilla horizontal + yugo U + base, color marfil (245,238,215) — reemplaza el glifo blanco liso.
- Bug cazado: `render_frame` contaba azul porque el CUERPO de vidrio era azul siempre; fix = cuerpo por estado (`self.bodies[state]`). Verificar reparto de color con conteo numpy (azul vs rojo) ANTES de creer al vision model (los VL abliterados despistan en imágenes pequeñas).
- Gotchas py3.11/win32: `wintypes.LRESULT` NO existe → `ctypes.c_ssize_t`; `DefWindowProcW` necesita argtypes LPARAM o OverflowError en cada mensaje; beeps no-bloqueantes = WAV bytes en memoria + `PlaySound(SND_MEMORY|SND_ASYNC)` (winsound.Beep bloquea el render loop).
- Procesos: el shim del venv crea 2 procesos (pythonw+python); la VENTANA pertenece al python real — buscarla por CLASE `HermesPTTOrb` (EnumWindows+GetClassNameW), nunca por PID memorizado.
- Smoke test E2E sintético: `PostMessageW(hwnd, 0x0201/0x0202, ...)` down/up al hwnd de la clase → log muestra `grabado Xs` + transcripción. PowerShell inline `-Command` con delegates EnumWindows se corrompe: usar python ctypes o ps1 con `-File`.
- Rendimiento: 2.1-3.9 ms/frame (PIL+numpy, sprites pre-horneados, ULW 60fps sobra). Modelo precarga al arrancar (7-9s una vez).

## Lecciones aprendidas (pitfalls críticos)
- **NUNCA usar tkinter+transparentcolor para ventanas translúcidas**: pinta una ventana opaca encima del bitmap layered, creando un fondo cuadrado visible que rompe la estética (verificado empíricamente). Siempre usar ventana Win32 pura con `UpdateLayeredWindow` para alpha por-píxel real.
- **En Python 3.11, `wintypes.LRESULT` no existe**: usar `ctypes.c_ssize_t` como sustituto al definir `WNDPROC`.
- **`DefWindowProcW` requiere explícitos argtypes y restype**: sin ellos, `LPARAM` de 64 bits causa `OverflowError` en cada mensaje, generando spam en logs. Añadir: `user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]; user32.DefWindowProcW.restype = LRESULT`.
- **El shim del venv NO posee la ventana**: al lanzar con `pythonw.exe` se crean dos procesos; la ventana pertenece al intérprete real de Python (normalmente `python.exe`), no al shim. Buscar ventana por CLASE `HermesPTTOrb` (EnumWindows+GetClassNameW), nunca por PID asumido.
- **Smoke test sintético confiable**: usar `PostMessageW(hwnd, WM_LBUTTONDOWN, 1, (y<<16)|x)` seguido de `WM_LBUTTONUP` después de 1.5-2s simula mantener clic para hablar. Verificar en log la línea `grabado Xs pico=Y` y transcripción subsiguiente.
- **PowerShell inline `-Command` corrompe delegates de ctypes**: evitar definiciones complejas de callbacks en uno-liners. Para tareas que requieren `EnumWindows` o `WndProc`, usar un archivo `.ps1` con `-File` o escribir la lógica en Python con ctypes directamente.

## References
- faster‑whisper GitHub: https://github.com/SYSTRAN/faster-whisper
- sounddevice documentation: https://python-sounddevice.readthedocs.io/
- Whisper model sizes and language coverage: https://huggingface.co/openai/whisper-small
