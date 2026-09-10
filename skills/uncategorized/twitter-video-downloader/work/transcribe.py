import sys, json

video = sys.argv[1]
out_json = sys.argv[2]
out_srt = sys.argv[3]
model_size = sys.argv[4] if len(sys.argv) > 4 else "small"

from faster_whisper import WhisperModel
print(f"Loading model {model_size}...", flush=True)
model = WhisperModel(model_size, device="cpu", compute_type="int8")
print("Transcribing (language=en)...", flush=True)
segments, info = model.transcribe(
    video, language="en", beam_size=5, vad_filter=True,
    condition_on_previous_text=True,
)
segs = []
for s in segments:
    segs.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip()})

with open(out_json, "w", encoding="utf-8") as f:
    json.dump(segs, f, ensure_ascii=False, indent=2)

def fmt(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); ms = int((t % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

with open(out_srt, "w", encoding="utf-8") as f:
    for i, seg in enumerate(segs, 1):
        f.write(f"{i}\n{fmt(seg['start'])} --> {fmt(seg['end'])}\n{seg['text']}\n\n")

print(f"DONE segments={len(segs)} lang={info.language} dur={info.duration:.1f}s", flush=True)
