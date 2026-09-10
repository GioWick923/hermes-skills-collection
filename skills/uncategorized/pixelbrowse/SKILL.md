---
category: pixelbrowse
name: pixelbrowse
description: "Renderiza cualquier URL, PDF o HTML a tiles de imagen (screenshot nativo) con pixelshot y léelos visualmente. Usa en lugar de scrapear HTML crudo cuando necesites VER el aspecto real de una página: leer contenido visual (tablas, gráficos, diagramas, infografías), verificar layouts/UI, o capturar páginas JS-heavy que el scraping de texto pierde. Dispara con: 'look at this page', 'screenshot', 'qué se ve en esta URL', 'verifica la UI', 'léelo visualmente', 'captura esta página'. Requiere pixelshot en PATH (uv tool install pixelrag)."
version: "1.0.0"
---

# PixelBrowse — Lectura visual de web vía screenshots (PixelRAG)

Usa `pixelshot` para capturar cualquier URL/documento como imágenes JPEG en tiles,
luego lee las imágenes visualmente (con el modelo multimodal del host, o vía OCR de
respaldo). Esto es RAG visual: el agente "ve" la página como la vería una persona,
no como texto parseado que pierde tablas/layout.

Requiere `pixelshot` en `PATH`. Si no está:
`uv tool install pixelrag` (o `pipx install pixelrag`). Luego reintenta.
No lo busques en venvs de proyecto.

> ⚠️ **EN ESTE HOST HERMES**: el host setea `PYTHONPATH` global apuntando a su venv
> (con PIL roto), y eso hace que `pixelshot` falle con
> `ImportError: cannot import name '_imaging' from 'PIL'`.
> **Usa el wrapper `pb-shot`** (ya en PATH, en `$LOCALAPPDATA/hermes/bin`) en lugar de
> `pixelshot` directo — limpia `PYTHONPATH` automáticamente. Mismos argumentos.
> (En otros hosts sin ese venv roto, `pixelshot` directo funciona.)

## Cómo usar

```bash
# URL optimizada para visión (tile-height 1568px = umbral de downscale de VLM)
pb-shot "<url>" --output "$LOCALAPPDATA/Temp/pixelbrowse" --tile-height 1568 --wait-network-idle

# Varias URLs en paralelo
pb-shot "<url1>" "<url2>" --output "$LOCALAPPDATA/Temp/pixelbrowse" --tile-height 1568 --wait-network-idle --workers 4

# Viewport más ancho para layouts desktop
pb-shot "<url>" --output "$LOCALAPPDATA/Temp/pixelbrowse" --tile-height 1568 --viewport-width 1280 --wait-network-idle

# PDF (requiere poppler; extra: pip install 'pixelrag[pdf]')
pb-shot document.pdf --output "$LOCALAPPDATA/Temp/pixelbrowse"
```

IMPORTANTE: siempre usa `--tile-height 1568` para screenshots que vas a leer visualmente.
El tile por defecto es 8192px y el VLM lo downscalea → texto ilegible.

IMPORTANTE: siempre usa `--wait-network-idle` en URLs. Sin eso, páginas JS-heavy
(SPA modernas) se capturan antes de renderizar y salen en blanco.

## Flujo

1. `pb-shot "<url>" --output "$LOCALAPPDATA/Temp/pixelbrowse" --tile-height 1568 --wait-network-idle`
2. Lee `$LOCALAPPDATA/Temp/pixelbrowse/<domain>.png.tiles/tile_0000.jpg` (el nombre es determinista)
3. Si la página es larga, lee tile_0001.jpg, tile_0002.jpg, etc.

Patrón de salida: `$LOCALAPPDATA/Temp/pixelbrowse/<url-sanitizada>.png.tiles/tile_NNNN.jpg`
- `https://news.ycombinator.com` → `.../news.ycombinator.com.png.tiles/tile_0000.jpg`
- `https://example.com/page` → `.../example.com_page.png.tiles/tile_0000.jpg`

## Leer los tiles (Hermes)

- Si el host model es multimodal: incluye el archivo de tile en la respuesta
  (`MEDIA:/ruta/tile_0000.jpg`) o úsalo directamente para razonar sobre la imagen.
- Si NO hay visión multimodal disponible: usa OCR de respaldo para extraer el texto
  del tile (skills `baidu-ocr` / `ocr-and-documents` ya instalados; o
  `python3 -c "from PIL import Image; ...crop..."` para recortar región y re-leer).
  Esto degrada a "texto de la imagen" pero mantiene la capacidad de capturar páginas
  que el scraping de HTML pierde.

## Crop & Zoom

Si el texto/detalle es muy pequeño, recorta la región y re-lee a full resolución.
Pillow siempre está disponible (dependencia de pixelshot):

```bash
python3 -c "from PIL import Image; Image.open('<tile_path>').crop((x1,y1,x2,y2)).save('$LOCALAPPDATA/Temp/pixelbrowse/crop.png')"
```

- Coordenadas en px desde la esquina superior-izquierda del tile.
- Recorta a ~800x800 o menos para máxima claridad.
- Lee la imagen recortada igual que cualquier otra.

## Tips

- Salida: JPEG en tiles — tile_0000.jpg es arriba, números mayores van hacia abajo.
- `--viewport-width 1280` para desktop; default 875 (ancho móvil/artículo).
- Soporta URLs (http/https), HTML local, PDFs e imágenes.
- Backends: `--backend cdp` (default, más rápido) o `--backend playwright`.
- En Windows: usa el Chrome del sistema auto-detectado. Si no lo encuentra,
  define `CHROME_PATH="C:/Program Files/Google/Chrome/Application/chrome.exe"`.
- Cada render corre en un perfil Chrome aislado/descartable → funciona aunque tengas
  Chrome abierto.

## Valor vs scraping MCP caído

Si los MCP de scraping (chrome-devtools, playwright, scrapling) están caídos o apuntan
a rutas rotas, `pixelshot` es una alternativa local robusta: usa tu Chrome del sistema,
no depende de bins externos. Recupera la capacidad de "ver" páginas web.
