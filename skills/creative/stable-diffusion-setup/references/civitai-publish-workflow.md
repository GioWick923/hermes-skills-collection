# Publicar checkpoint en Civitai (workflow probado)

Para subir un modelo (`NDREAM_ULTRA.safetensors` u otro) a la cuenta de Civitai de Gio
(<CIVITAI_USER>, id 2836482). Verificado por sesión real.

## ⚠️ Regla de oro: la API de Civitai es SOLO LECTURA

- `POST /api/v1/models` → **405 Method not allowed**. No existe endpoint para crear/subir modelos.
- La API solo hace `GET` (info de modelos/imágenes/creadores).
- **Publicar requiere el navegador con sesión logueada.** El token API NO sirve para el navegador
  (es un token distinto de las cookies de sesión).

## Flujo real (stealth-browser MCP)

1. **Spawn browser NO headless** (el usuario debe poder ver e interactuar):
   `mcp__stealth_browser_mcp__spawn_browser` con `headless:false`.
2. Navegar a `https://civitai.com` y **revisar si hay sesión** (`<CIVITAI_USER>` en el menú de usuario,
   no "Sign In"). Si no hay, el login es **Google OAuth** → NO pedir credenciales al agente;
   el usuario se loguea a mano en la ventana visible. La sesión SI queda activa en la misma instancia
   del browser (persiste entre navigations).
3. Ir a `https://civitai.com/models/create` → "Comparte tus modelos".
4. Rellenar con `execute_script` (los clicks puros en Mantine a veces no setean value):

```javascript
// Nombre
const set=(sel,val)=>{const el=document.querySelector(sel);if(el){const s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;s.call(el,val);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));return true}return false};
set('#input_name','NDREAM ULTRA');
// poi=No (no representa persona real): click en input[name=poi][value=false]
// attestation: click en #input_attestation (obligatorio)
// checkpointType=Merge: click en #checkpointType-Merge (vs Trained)
```

5. **Descripción** es un `[contenteditable=true]` DIV (no textarea): setear `ce.textContent=...` + input/change.
6. **Categoría** (`#input_category`) es un combobox Mantine: hacer click para abrir y elegir.
7. **Licencia/comercial**: los checkboxes `#input_allowNoCredit`, `#input_allowDerivatives`,
   `#input_allowDifferentLicense` ya vienen marcados. `Sell` (vender modelo) viene marcado —
   **es decisión del usuario**, preguntar antes de publicar.
8. Botón "Próximo" avanza al paso 2 (agregar versión) → 3 (subir archivo) → 4 (publicar).

## Checklist previa a publicar (no saltar)

- [ ] Confirmar **licencia** de los modelos fuente del merge (Illustrious permite remix; Flux no siempre).
- [ ] Confirmar con el usuario **categoría** y **permiso comercial (Sell)** — es publicación irreversible.
- [ ] Tener **imagen de preview** lista (Civitai la pide) — generarla con ComfyUI/Forge antes.
- [ ] El archivo a subir existe y está validado (safetensors leible).

## Pitfall: ¿cómo se verifica la sesión?

`get_page_content` devuelve JSON grande (~220-250K tokens). Parsear el `.json` guardado y buscar
`<CIVITAI_USER>` en `data.text`; si aparece en el menú de usuario, hay sesión. "Sign In" = no hay sesión.

## Pitfall: login Google

`/login` redirige a `accounts.google.com`. El agente NO debe manejar credenciales Google.
El usuario completa el login en la ventana visible; luego navegar de nuevo a civitai.com y
re-verificar la sesión (a veces el redirect no la carga hasta navegar otra vez).
