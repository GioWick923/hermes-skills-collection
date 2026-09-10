---
name: image-combine
description: Combine still images side-by-side or stacked.
---

# image-combine

Combine multiple still images into a single output. Horizontal by default.

## Procedure

1. **Confirm inputs** — ask which images if ambiguous; list candidates with sizes. When directory has many files, ask user to specify or number them (e.g., "imagen 1", "imagen 2").
2. **Confirm orientation** — horizontal (default), vertical, or grid layout.
3. **Align dimensions** — match by height (portrait photos) or width (landscape). All images should be same orientation for clean results.
4. **Run PIL/Pillow** — `execute_code` with Python, not ffmpeg.
5. **Save as JPG** by default (quality 90), unless transparency/lossless needed.
6. **Deliver via MEDIA:** path + confirm file exists with `ls -lh`.

## Code template

```python
from PIL import Image
import glob
imgs = [Image.open(f).convert("RGB") for f in sorted(glob.glob("/path/to/*.jpg"))]
max_h = max(i.height for i in imgs)
resized = [i.resize((int(i.width * max_h / i.height), max_h), Image.LANCZOS) for i in imgs]
result = Image.new("RGB", (sum(i.width for i in resized), max_h), (255,255,255))
x = 0
for i in resized: 
    result.paste(i, (x, 0))
    x += i.width
result.save("/output/path.jpg", "JPEG", quality=90)
```

## Pitfalls

- **Windows paths**: use forward slashes in bash context (`/c/Users/...`) or raw strings (`r"C:\..."`). Backslashes break in MSYS.
- **Spaces in paths**: quote with double quotes or use `glob.glob()`.
- **Orientation**: always confirm horizontal vs vertical — don't assume.
- **Large outputs**: high-res images (2K+) can create huge files. Suggest compression if >10MB.
- **Verify output**: run `ls -lh` on output path to confirm it exists and has non-zero size.
- **Order matters**: if images have numbers or sequence, confirm order with user before combining.

## When to ask

- Which files to combine (if directory has many)
- Orientation (horizontal/vertical/grid)
- Output format (JPG default, PNG if transparency needed)
- Order of images (especially if numbered)
