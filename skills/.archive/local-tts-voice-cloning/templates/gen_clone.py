# Template: generation script for local TTS voice cloning (Chatterbox, Spanish)
# Copy to the model's workdir, adjust REF/TEXT/OUT, run with the model's venv python.
# Proven on: C:/Users/<USER>/tools/chatterbox (gen_davy_es2.py), RTX 3060, torch cu126.

import sys, torch
sys.path.insert(0, r"C:/Users/<USER>/tools/chatterbox/src")
import soundfile as sf  # NOT torchaudio: ta.load/ta.save need torchcodec (not installed)

def save_wav(path, tensor, sr):
    a = tensor.detach().cpu().numpy()
    if a.ndim == 2: a = a[0]
    sf.write(path, a, sr)

REF = "refs/davy_ref2.wav"   # 10-15s clean voice clip of the target speaker
TEXT = ("Pregunto si temeis a la muerte porque la respuesta define lo que sois. "
        "Yo ame y me traicionaron; me cortaron el corazon para no sentir mas. "
        "Pero el miedo no se extirpa: ese quedo.")

from chatterbox.mtl_tts import ChatterboxMultilingualTTS  # Spanish ALWAYS multilingual, not turbo
model = ChatterboxMultilingualTTS.from_pretrained(device="cuda")

for name, ex in [("neutra", 0.3), ("amenazante", 0.8)]:
    out = model.generate(TEXT, language_id="es", audio_prompt_path=REF, exaggeration=ex)
    save_wav(f"outputs/clone_{name}.wav", out, model.sr)
    print("saved", name)

# Telegram delivery (run after generation):
#   ffmpeg -i outputs/clone_neutra.wav -c:a libopus -b:a 64k "$LOCALAPPDATA/hermes/cache/clone_neutra.ogg"
#   MEDIA:C:/Users/<USER>/AppData/Local/hermes/cache/clone_neutra.ogg   <- native C:/ path ONLY
