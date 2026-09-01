---
name: civitai-browser-publish
description: Publish content to Civitai via logged-in browser.
version: 1.0.0
author: Hermes Agent
license: internal
metadata:
  tags: [civitai, browser, article, publish, stealth-browser]
  related_skills: []
---

## When to Use
Use whenever Gio asks to publish/subir contenido a su cuenta de Civitai (<CIVITAI_USER>) vía navegador: publicar un ARTÍCULO/guía, un POST, o añadir imágenes a un modelo ya publicado. La API pública de Civitai es SOLO lectura (no crea modelos ni sube imágenes), así que todo esto se hace con stealth-browser logueado.

## Contexto
- Cuenta Civitai: **<CIVITAI_USER>** (ID 2836482)
- ⚠️ **PREFERENCIA DE GIO: NO usar stealth-browser temporal** (perfil descartable pierde la sesión y obliga a re-login cada vez). **Usar su Chrome REAL vía CDP con perfil persistente** — sesión guardada para siempre, login solo 1 vez.
- Navegador primario: Chrome real via CDP (ver "Chrome REAL via CDP" abajo)
- Navegador fallback (solo si CDP no disponible): `mcp__stealth_browser_mcp__spawn_browser(headless=false)`

## Chrome REAL via CDP (método RECOMENDADO)
**Lanzar Chrome con perfil persistente + civitai abierto:**
```bash
"C:/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir="C:/Users/<USER>/hermes-chrome" \
  --no-first-run --no-default-browser-check \
  "https://civitai.com"
```
- `--remote-allow-origins=*` es OBLIGATORIO (sin el, Chrome rechaza el WebSocket CDP con 403).
- `--user-data-dir="C:/Users/<USER>/hermes-chrome"` = perfil SEPARADO persistente (no toca el Chrome diario). La sesión <CIVITAI_USER> queda guardada ahí para siempre.
- `civitai.com/login` redirige a Google OAuth → la primera vez el usuario inicia sesión en la ventana visible. Solo una vez.
- Conectar: `ws://127.0.0.1:9222/devtools/page/{tabId}` (tabId de `http://127.0.0.1:9222/json/list`, buscar type=="page" con "civitai").
- Evaluar JS con `Runtime.evaluate` (expression, returnByValue:true).

**Verificar sesión (CLAVE):** NO buscar "<CIVITAI_USER>" en el header (está en el avatar, no como texto plano → falsos negativos). Usar fetch interno:
```js
await fetch('/api/v1/me').then(r=>r.json())  // -> {user:"<CIVITAI_USER>", id:2836482}
```

**Pitfalls CDP (aprendidos esta sesión):**
- `DOM.getDocument` con `depth:-1` + `pierce:true` puede WEDGEAR el tab en páginas con mucho DOM (Civitai): el buffer de eventos CDP se llena y el WebSocket deja de responder. Preferir `Runtime.evaluate` solo. Si el WS se cuelga, abrir conexión nueva.
- `webSocket-client` directo a Chrome se cuelga tras un `DOM.getDocument` pesado → usar `Runtime.evaluate` con timeout corto.
- El **chrome-devtools MCP apunta a SU PROPIO Chrome de desarrollo de Hermes, NO al Chrome de Gio** (perfil 9222). Verificar `list_pages` — si ves pestañas DevTools/github, es el equivocado.
- `DOM.setFileInputFiles` con ruta MSYS `/c/...` falla: usar ruta nativa `C:/...`.

## Stealth-browser (FALLBACK — solo si CDP no disponible)
- `mcp__stealth_browser_mcp__spawn_browser(headless=false)` — requiere que GIO haga login (Google OAuth) en la ventana visible CADA VEZ (perfil temporal)
- Subida de archivos: `file_upload` exige ruta en `BROWSER_FILE_UPLOAD_ALLOWED_DIRS`. Copiar a `C:/Users/<USER>/tools/stealth-browser-mcp/upload_tmp/` primero (allowlist) — el path nativo `F:/...` o `/c/...` da "outside allowed roots" / FileNotFoundError. PIL necesita ruta `C:/...` nativa.
- Sesión: el navegador mantiene la sesión entre navegaciones mientras la instancia vive (pero se pierde al cerrar — por eso Gio lo rechazó).

## ESTILO DE CONTENIDO (PREFERENCIA DEL USUARIO — obligatorio)
Gio quiere contenido **humanizado, extenso e informativo, con emoticons y formato con espacios** — NUNCA texto plano encimado. Estructura que funciona:
- Encabezados `##` por sección (Introducción, requisitos, pasos, seguridad, troubleshooting, resumen, conclusión).
- Emoticones por sección (🚀 🧩 🧰 🗝️ 🔍 🌐 🛡️ 📌 🎉).
- Listas con `-`/`1.` y blockquotes `>` para consejos/advertencias.
- Varios párrafos cortos, no un muro de texto.

## Editor de contenido de ARTÍCULOS (el punto que causa fallos)
El editor rich-text de artículos de Civitai:
- ✅ **Acepta `document.execCommand('insertText', false, <markdown>)`** — inserta el markdown y Civitai lo renderiza con formato. MÉTODO VALIDADO.
- ❌ **NO acepta `document.execCommand('insertHTML', false, <html>)`** — devuelve `false` y si antes hiciste `innerHTML=''`, borra el contenido. NO limpiar con `innerHTML=''` antes de insertar.
- Selector del editor: `[contenteditable]` que contenga el texto del título, o `[class*=RichTextEditorComponent]` / `.ProseMirror`. El hash de clase varía — usar selector por prefijo.

## Flujo para publicar ARTÍCULO
1. Ir a `/articles/create` (sesión iniciada).
2. Título: `input[name=title]` — set value + dispatch `input`/`change`.
3. Categoría: input con placeholder "categor" → click (mousedown+click) → esperar dropdown → click opción. Las opciones están en español ("Guía de herramientas" = Tool guide) o inglés según idioma de sesión. El hidden `input[name=categoryId]` recibe el id (Tool guide = 128648).
4. Contenido: `execCommand('insertText', false, md)`. Si falla, entregar el texto en un `.md` para que Gio haga Ctrl+V (el editor acepta pegado manual 100%).
5. Imagen de portada: `file_upload` al input correcto. Ver Pitfalls — el CDP de portada es poco fiable.
6. Publicar: botón "Publicar"/"Publish". Verificar redirección a `civitai.com/articles/<id>/<slug>`.

## Pitfalls (IMPORTANTE)
- **Error de portada BLOQUEA el Publicar.** Si `input_coverImage-error` = "Entrada no válida"/"Invalid input", el botón Publicar recarga la página y pierde el contenido (o muestra modal "¿Restaurar los cambios no guardados?"). No dar Publicar hasta que la portada no tenga error.
- **Upload de portada via CDP es poco fiable** — a veces da "sin error" pero el Publicar lo rechaza; o el input idx 0 no es el de portada. Si persiste tras 1-2 intentos, NO iterar en loop: pedir a GIO que suba la portada manualmente en el navegador, luego dar Publicar.
- **"Guardar borrador"/"Save Draft" puede no confirmar** si la portada tiene error (submit bloqueado). El borrador puede no aparecer en `user/<cuenta>/articles`.
- Botones en español ("Guardar borrador"/"Publicar") o inglés ("Save Draft"/"Publish") según la sesión — buscar ambos.
- **Imágenes dentro del contenido**: el input de imágenes del contenido es `input[type=file][multiple]`; la portada es un input imagen `:not([multiple])`. Subir cada una al input correcto. Subir las imágenes del contenido de una en una si el multiple falla.
- Stealth `execute_script` dispara "tool loop warning" FALSO (success true real) cuando se reusa mucho — ignorar, no es un fallo.

## Referencias
- `references/civitai-article-publish.md` — detalle del flujo de publicación de artículos y sus trampas.
