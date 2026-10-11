---
name: web-console-iframe-automation
description: "Extraer IDs/datos de consolas SPA con contenido en iframes."
version: 1.0.0
author: Hermes curator
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [browser, iframe, shadow-dom, console, oracle, ocid, spa]
    related_skills: [browser-testing-with-devtools, dogfood]
---

# Web Console Iframe Automation

Clase de tarea: **automatizar consolas web modernas (SPA) cuyo contenido real vive
dentro de un `<iframe>` y/o Shadow DOM** — Oracle Cloud, Azure Portal, GCP Console,
paneles de admin. El patrón se validó extrayendo OCIDs de Oracle Cloud (2026-08-20).

## Cuándo usar
- Necesitas obtener IDs/valores (OCIDs, resource IDs, ARNs, tokens) de una consola web.
- `page_info()` devuelve texto vacío o solo el "shell" de la página (nav, footer, legal).
- El usuario está logueado en SU navegador pero el navegador controlado no comparte sesión.
- El contenido parece "no renderizar" aunque el título de la pestaña sí cargue.

## Síntoma clásico
```
page_info() → TITLE: "My profile | Oracle Cloud Infrastructure", TEXT_LEN: 0
```
La página cargó el shell (título, menú lateral) pero el contenido está en un iframe.

## Técnica (validada)

### 1. Detectar el iframe
```js
Array.from(document.querySelectorAll('iframe')).map(f => ({src: f.src, id: f.id}))
```
En Oracle Cloud el iframe se llama `sandbox-maui-preact-container`. Otras consolas usan
nombres similares (`app-frame`, `content-frame`, `main-frame`).

### 2. Acceder al contentDocument del iframe
```js
(() => {
  const iframe = document.getElementById('sandbox-maui-preact-container');
  if (!iframe || !iframe.contentDocument) return 'NO_ACCESS';  // cross-origin block
  return iframe.contentDocument.body.innerText.substring(0, 2000);
})()
```
- **Funciona solo si el iframe es same-origin** (mismo dominio). Oracle lo es.
- Si da `NO_ACCESS` → es cross-origin; entonces no puedes leerlo por JS. Alternativa:
  navegar directo a la URL que renderiza dentro del iframe (a veces funciona como página
  independiente) o pedir al usuario el dato.

### 3. Extraer IDs del DOM del iframe (incluyendo Shadow DOM)
```js
(() => {
  const iframe = document.getElementById('sandbox-maui-preact-container');
  if (!iframe || !iframe.contentDocument) return 'NO_ACCESS';
  const found = new Set();
  const walk = (root) => {
    root.querySelectorAll('*').forEach(el => {
      const t = (el.textContent || '').trim();
      const m = t.match(/ocid1\.(tenancy|user|compartment)\.oc1\.[\w.]+/);
      if (m) found.add(m[0]);
      if (el.shadowRoot) walk(el.shadowRoot);
    });
  };
  walk(iframe.contentDocument);
  return Array.from(found);
})()
```
- Buscar en `textContent` Y en atributos (`data-*`, `title`, `href`) — a veces el ID solo
  está en un atributo.
- El regex captura IDs concatenados con texto adyacente ("...Yes0Aug"); limpiar después.

### 4. Los IDs también están en el texto truncado de la UI
La consola muestra OCID truncados con "..." en la tabla, pero el DOM suele tener el
valor completo en un atributo o en el texto de una celda vecina. Probar ambas vías.

## Pitfalls
- **Sesión no compartida**: el navegador controlado (browser_exec) NO hereda la sesión
  del navegador del usuario. Si la consola requiere login y el controlado no lo tiene,
  verás solo el shell. El usuario debe loguearse UNA vez en el navegador controlado,
  o copiar el dato desde el suyo.
- **page_info vacío ≠ página rota**: casi siempre es contenido en iframe/Shadow DOM.
- **Cross-origin iframe**: `contentDocument` es null → no se puede leer por JS.
- **Clicks en menús laterales**: a veces el menú está en el iframe; hay que buscar el
  elemento dentro de `iframe.contentDocument` y hacer `.click()`, luego esperar 5-8s
  (SPA lenta).
- **Regex con anclas**: `\b` no funciona bien con OCIDs que empiezan en mitad de texto;
  usar captura directa `(ocid1\.\w+\.oc1\.[\w.]+)` y filtrar.

## Referencias
- `references/oracle-cloud-ocid-extraction.md` — caso validado: extraer tenancy + user OCID
  de Oracle Cloud Free Tier (2026-08-20), incluye el flujo completo y las URLs exactas.

## Verificación
- [ ] `page_info()` da título pero texto vacío → sospechar iframe
- [ ] `document.querySelectorAll('iframe')` encuentra el frame contenedor
- [ ] `iframe.contentDocument` es accesible (same-origin)
- [ ] El walker extrae los IDs (OCID/ARN/etc.) del DOM y sus atributos
- [ ] Si cross-origin → alternativa documentada (URL directa o pedir al usuario)
