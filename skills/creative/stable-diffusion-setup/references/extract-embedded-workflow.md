# Extraer workflow de ComfyUI embebido en una imagen

ComfyUI guarda el grafo embebido en imágenes PNG (chunk `tEXt` con claves
`workflow`, `prompt` o `comfyui`). Esto aplica a imágenes descargadas de
Civitai, tensor.art, Discord, etc. — **aunque la URL diga `.jpeg`**, el
archivo real puede ser un PNG con el workflow dentro (Civitai re-etiqueta a
`.jpeg` por calidad pero sirve PNG).

## Cómo detectarlo y extraerlo

```python
import struct, zlib

data = open("imagen.ext", "rb").read()
print("Es PNG:", data[:8] == b"\x89PNG\r\n\x1a\n")   # el .jpeg puede ser PNG de verdad

i = 8
found = {}
while i < len(data):
    length = struct.unpack(">I", data[i:i+4])[0]
    ctype = data[i+4:i+8].decode("latin1", "ignore")
    cdata = data[i+8:i+8+length]
    if ctype == "tEXt":
        sep = cdata.find(b"\x00")
        key = cdata[:sep].decode("latin1", "ignore")
        if key.lower() in ("workflow", "prompt", "comfyui"):
            found[key] = cdata[sep+1:].decode("utf-8", "ignore")
    i += 12 + length

for k, v in found.items():
    open(f"extracted_{k}.json", "w", encoding="utf-8").write(v)
    print(k, len(v), "chars")
```

## Puntos clave

- El workflow embebido es el **JSON del grafo de UI** (con `nodes`/`links`),
  no el formato API. Al recargarlo en ComfyUI funciona tal cual.
- **No asumas el modelo grande:** el workflow embebido referencia checkpoints
  (ej. `krea2TurboOfficialComfy_krea2TurboMxfp8`) que el autor usó. Puede que
  NO los tengas — el grafo carga pero el checkpoint queda marcado missing.
  Verificar con `object_info` que los node types existan y que los modelos
  referenciados estén en disco antes de prometer que "jala".
- `vision_analyze` puede fallar (401 / API key del modelo de visión inválida)
  para "ver" la imagen; la extracción por chunks PNG es más fiable que depender
  del modelo de visión.
- Si el repo de modelos está en HuggingFace con **Xet** (pointer de ~268 bytes,
  no el binario real), `curl`/`hf download` anónimo NO baja el archivo real —
  requiere `HF_TOKEN` autenticado. `huggingface-cli` está deprecado (usar `hf`),
  y `hf download` no acepta `--local-dir-use-symlinks`.
