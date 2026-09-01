# PITFALL: axiom-image-metadata-stripper — JPEG off-by-2 corrupts output

## Symptom
`strip_jpeg()` reports success ("✅ Stripped", correct byte counts) but the
output file is NOT a valid JPEG — `PIL.Image.open(out).load()` raises
`cannot identify image file`.

## Root cause (axiom_image_metadata_stripper.py, strip_jpeg)
When keeping a non-metadata segment, the loop advances the cursor wrong:
```python
segment = data[i-2:i+length]
if marker in METADATA_MARKERS:
    pass
else:
    output.extend(segment)
i += length - 2   # BUG: -2 double-subtracts the 2 length bytes
```
`length` (read via `struct.unpack(">H", data[i:i+2])`) already INCLUDES the two
length bytes. After consuming `segment` (which starts at `i-2`, i.e. the marker+
length), the cursor should advance by the full `length`, not `length - 2`.

## Fix
```python
i += length   # advance past full segment (length includes the 2 length bytes)
```

## Verification (ad-hoc, GENUINE image)
Use a real PIL-generated JPEG — do NOT hand-inject an APP1 segment, that makes
"unopenable" ambiguous. Recipe in scripts/verify_skill_change.py (jpeg case).
Assert: input openable -> rc=0 -> output openable AND any injected secret absent.
Result after fix: VERIFIED_OK.

## Collateral findings (doc vs code)
- SKILL.md claims GIF support ("strips comment extensions") but `detect_format`
  returns "unknown" for GIF and `strip_metadata` raises `Unsupported format: gif`.
  The code does NOT implement GIF. Treat the doc claim as wrong until implemented.
- PNG path uses a different (correct) chunk-walk and works as-is.

## Caution
`axiom-image-metadata-stripper` is a hub-installed (protected) skill. Only patch
the user's copy after explicit request. Keep this recipe for reproduction. A
`.bak` of the patched file should be left in place.
