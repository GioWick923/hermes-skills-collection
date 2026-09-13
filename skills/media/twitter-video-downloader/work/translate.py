import sys, json, os

en_srt = sys.argv[1]
es_srt = sys.argv[2]
model = sys.argv[3] if len(sys.argv) > 3 else "google/gemma-4-31b-it:free"

from openai import OpenAI
from openai import RateLimitError, APIError
import time

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)

def translate_batch(lines, attempt=0):
    joined = "\n".join(f"{i}|{t}" for i, t in enumerate(lines))
    sys_prompt = (
        "You are a professional English->Spanish translator. "
        "Translate each line faithfully, preserving tone and meaning. "
        "Return EXACTLY the same number of lines, in the same order, "
        "each as 'index|translated text'. Do not add commentary. "
        "Keep it natural Spanish suitable for video subtitles."
    )
    user = f"Translate these subtitle lines (index|text):\n{joined}"
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user},
            ],
            temperature=0.1,
        )
    except (RateLimitError, APIError) as e:
        if attempt < 5:
            wait = 4 * (attempt + 1)
            print(f"rate-limit, retry in {wait}s", flush=True)
            time.sleep(wait)
            return translate_batch(lines, attempt + 1)
        else:
            raise
    out = r.choices[0].message.content.strip()
    # parse "index|text"
    result = {}
    for line in out.splitlines():
        if "|" in line:
            idx, txt = line.split("|", 1)
            try:
                result[int(idx)] = txt.strip()
            except ValueError:
                pass
    return result

# parse EN srt
def parse_srt(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read().strip().split("\n\n")
    blocks = []
    for blk in raw:
        parts = blk.split("\n")
        if len(parts) < 3:
            continue
        idx = parts[0].strip()
        timing = parts[1].strip()
        text = "\n".join(parts[2:]).strip()
        blocks.append((idx, timing, text))
    return blocks

blocks = parse_srt(en_srt)
texts = [b[2] for b in blocks]

# translate in batches of 20
B = 20
translated = {}
for i in range(0, len(texts), B):
    batch = texts[i:i+B]
    res = translate_batch(batch)
    for j, t in enumerate(batch):
        key = i + j
        translated[key] = res.get(j, t)
    print(f"batch {i//B+1}/{(len(texts)+B-1)//B} done", flush=True)

# write ES srt
with open(es_srt, "w", encoding="utf-8") as f:
    for key, (idx, timing, _) in enumerate(blocks):
        f.write(f"{idx}\n{timing}\n{translated[key]}\n\n")

print(f"DONE translated={len(translated)}", flush=True)
