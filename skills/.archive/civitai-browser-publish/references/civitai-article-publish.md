# Publicar Artículos en Civitai (<CIVITAI_USER>) — via stealth-browser

Detalle del flujo de publicación de ARTÍCULOS (guías, noticias, tutoriales). Mismo navegador logueado que para modelos.

## Estilo de contenido (PREFERENCIA DEL USUARIO — obligatorio)
Gio quiere el contenido del artículo **humanizado, extenso e informativo, con emoticons y formato con espacios** — NO texto plano encimado. Estructura que funciona:
- Encabezados `##` por sección (Introducción, requisitos, pasos, seguridad, troubleshooting, resumen, conclusión).
- Emoticones por sección (🚀 🧩 🧰 🗝️ 🔍 🌐 🛡️ 📌 🎉).
- Listas con `-`/`1.` y blockquotes `>` para consejos/advertencias.
- Varios párrafos cortos, no un muro de texto.

## Editor de contenido (el punto que causa fallos)
El editor rich-text de artículos de Civitai:
- ✅ **Acepta `document.execCommand('insertText', false, <markdown>)`** — inserta el markdown y Civitai lo renderiza con formato (encabezados, listas, emojis). MÉTODO VALIDADO (probado con éxito en sesión, `execInsertText=true`, contenido renderizado).
- ❌ **NO acepta `document.execCommand('insertHTML', false, <html>)`** — devuelve `false` y borra el contenido si antes hiciste `innerHTML=''`. Deja el editor vacío. NO usar `innerHTML=''` antes de insertar.
- Selector del editor: `[contenteditable]` que contenga el texto del título/marca, o `[class*=RichTextEditorComponent]` / `.ProseMirror`. El hash de clase varía (`__6Qve9G` etc.) — usar selector por prefijo.

## Pasos
1. Ir a `/articles/create` (sesión iniciada).
2. Título: `input[name=title]` — setear value + dispatch `input`/`change`.
3. Categoría: input con placeholder "categor" → click (mousedown+click) → esperar dropdown → click opción. Opciones en español ("Guía de herramientas" = Tool guide) o inglés según idioma. El hidden `input[name=categoryId]` recibe el id (Tool guide = 128648).
4. Contenido: `execCommand('insertText', false, md)`. Si falla, entregar el texto en un `.md` y que Gio haga Ctrl+V (el editor acepta pegado manual 100%).
5. Imagen de portada: `file_upload` al input correcto. Ver Pitfalls.
6. Publicar: botón "Publicar"/"Publish". Verificar redirección a `civitai.com/articles/<id>/<slug>`.

## Pitfalls
- **Error de portada BLOQUEA el Publicar.** Si `input_coverImage-error` = "Entrada no válida"/"Invalid input", el botón Publicar recarga la página y pierde el contenido (o muestra modal "¿Restaurar los cambios no guardados?"). No dar Publicar hasta que la portada no tenga error.
- **Upload de portada via CDP es poco fiable** — a veces da "sin error" pero el Publicar lo rechaza; o el input idx 0 no es el de portada. Si persiste tras 1-2 intentos, NO iterar en loop: pedir a GIO que suba la portada manualmente en el navegador, luego dar Publicar.
- **"Guardar borrador"/"Save Draft" puede no confirmar** si la portada tiene error (submit bloqueado). El borrador puede no aparecer en `user/<cuenta>/articles`.
- Botones en español ("Guardar borrador"/"Publicar") o inglés ("Save Draft"/"Publish") según la sesión — buscar ambos.
- **Imágenes dentro del contenido**: el input de imágenes del contenido es `input[type=file][multiple]`; la portada es un input imagen `:not([multiple])`. Subir cada una al input correcto. Subir las imágenes del contenido de una en una si el multiple falla.
- Stealth `execute_script` dispara "tool loop warning" FALSO (success true real) cuando se reusa mucho — ignorar, no es un fallo.
- Después de varios intentos fallidos con el editor, la vía fiable de contenido es el Ctrl+V manual por Gio. No pelear con execCommand en loop.
