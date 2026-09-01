---
name: civitai-article-publish
description: Publish humanized articles/guides to Civitai for Gio.
version: 1.0.0
author: Hermes Agent
license: internal
metadata:
  tags: [civitai, article, publishing, browser-automation, content]
  related_skills: [model-merge-publish]
---

## When to Use
Use whenever Gio asks to publish an ARTICLE, guía, guide, post, or tutorial on Civitai (account <CIVITAI_USER>), or to write humanized content for publication.

# Publicar ARTÍCULOS/GUÍAS en Civitai (<CIVITAI_USER>)

La API de Civitai es SOLO lectura — no publica artículos ni sube imágenes. La publicación se hace por NAVEGADOR logueado.

## Estado de ejecución (schema fijo — se actualiza, no se acumula historia)

> Patrón SKILL.state: en cada paso el agente ve solo `(spec + Estado + última observación de la página)`.
> No dependas del histórico del chat para saber "qué ya va". El navegador cambia de estado y el
> estado canónico debe reflejarlo, no reconstruirse de memoria.

Mantén un objeto JSON único entre pasos del publish:
```json
{
  "url_actual": null,
  "titulo": null,
  "contenido_md": null,
  "portada_lista": false,
  "categoria": null,
  "errores": [],
  "publicado": false,
  "url_final": null
}
```
Reglas:
- **`url_actual`**: la URL del navegador en cada paso (`spawn_browser` la da). Es la mejor señal de estado real: si sigue en `/create` → faltan campos; si está en `/articles/<id>` → publicado.
- **`portada_lista`**: `true` SOLO cuando subiste/imagen confirmada, no "intenté". Si no hay portada fiable, el paso siguiente lo sabe y no re-intenta a ciegas.
- **`categoria`**: dropdown obligatorio; si `null`, el submit rebotará.
- **`errores`**: lista de `.mantine-InputWrapper-error` detectados (ej. `input_coverImage-error`) → evitar re-intentar el mismo submit con el mismo error.
- **`publicado` / `url_final`**: solo `true`/con valor tras confirmar la URL final. Es la única condición para decir "publicado".

## Contexto
- Cuenta: **<CIVITAI_USER>** (ID 2836482). El navegador requiere que GIO haga el login Google manualmente en la ventana visible (el agente nunca maneja credenciales).
- Navegador: stealth-browser MCP, `spawn_browser(headless=false)`, `execute_script` para rellenar.
- Dir permitido para uploads: `C:/Users/<USER>/tools/stealth-browser-mcp/upload_tmp/` (allowlist de `file_upload`).
- ComfyUI venv (PIL) para generar portada: `/f/ComfyUI/venv/Scripts/python.exe`.

## Flujo
1. `spawn_browser(headless=false)` → navegar a `https://civitai.com/articles/create` (sesión de Gio).
2. Título: `input[name=title]` (placeholder "Por ejemplo: Cómo crear tu propio LoRA").
3. Contenido: editor rich (tiptap/ProseMirror). NO insertar por script — ver pitfall CRÍTICO abajo.
4. Imagen de portada: generar 850x400 con PIL, subir al input no-multiple (poco fiable por script — a menudo requiere que Gio lo suba manual).
5. Categoría (dropdown, obligatoria): para guías usar "Tool guide" o "Generation guide". Abrir con click en el input placeholder "Seleccione una categoría", click en la opción.
6. Botones alternan ES/EN: "Publicar"/"Publish", "Guardar borrador"/"Save Draft". Buscar ambos textos.
7. Tras Publicar debe redirigir a `/articles/<id>/<slug>`. Si sigue en `/create`, hay un campo inválido → buscar `.mantine-InputWrapper-error` (ej. `input_coverImage-error`).

## PITFALL CRÍTICO: el editor rich de Civitai BLOQUEA inserción programática
- `execCommand('insertHTML', false, html)` devuelve **false** (tiptap/ProseMirror lo bloquea).
- `el.textContent = guia` mete todo como texto plano SIN formato → Gio se queja "se ve todo encimado".
- `el.innerHTML = ''` borra el contenido definitivamente (irrecuperable). NO hacer esto.
- **Método fiable:** pegar **markdown real** con Ctrl+V — Civitai respeta markdown (##, listas, blockquotes, negritas). Preparar el texto como `.md`, pedir a Gio que lo pegue manualmente en el editor.
- Verificar el editor con selector por clase prefijo: `[class*=RichTextEditorComponent]`, no hardcodear el hash de clase.

## Estilo de Gio para contenido publicado (OBLIGATORIO)
> Fuente canónica de voz: **`civitai-voice`** skill. Léela ANTES de redactar — define la voz,
> tono y hooks de Gio. Este bloque es el resumen rápido; si difiere, manda `civitai-voice`.

- **Humanizado**: texto natural, no manual técnico. Explicar el PORQUÉ, no solo el CÓMO.
- **Emoticons** abundantes (🚀 🧠 🔎 🔒 ✅ ⚠️ 💡 🎉) en encabezados y bullets.
- **Espacio/estructura**: muchos saltos de línea, secciones con `---`, listas numeradas/punteadas, blockquotes, resumen final.
- **Extenso e informativo**: introducción → qué es y por qué → requisitos → pasos con detalle → troubleshooting → resumen → conclusión.
- No escribir texto plano pegado; siempre con formato y aire visual.

## Verificación
- `.mantine-InputWrapper-error` revela el campo que bloquea el submit (título, categoría, portada, contenido).
- El click en "Publicar" con campos inválidos NO navega — revisar errores, no re-intentar ciegamente.
