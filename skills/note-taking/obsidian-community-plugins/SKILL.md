---
name: obsidian-community-plugins
description: "Use when installing/configuring Obsidian community plugins."
version: 1.0.0
author: Hermes (curador)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [obsidian, plugins, templates, templater, markdown]
    related_skills: [obsidian, hermes-obsidian-ops]
---

# Obsidian Community Plugins & Templates

Instalar, activar y configurar plugins de la comunidad de Obsidian de forma
manual (sin UI interactiva) y crear plantillas de Templater. Verificado
2026-09-01 con Templater v2.25.0 y Flexplorer v4.0.5 en Windows.

## Cuando usar
- El usuario pide un plugin de la comunidad de Obsidian y no hay flujo UI.
- Quieres prefijar la config de un plugin (data.json) o crear plantillas.
- Necesitas activar plugins ya presentes en disco (community-plugins.json).

## Flujo de instalacion manual (determinista, scriptable)

1. **Obtener release.** Los plugins publican 3 assets por release: `main.js`,
   `manifest.json`, `styles.css`. Consulta la ultima release del repo GitHub:
   ```bash
   curl -s https://api.github.com/repos/<owner>/<repo>/releases/latest
   ```
   (lista `assets[].name`). Sin esos 3 archivos el plugin no funciona.

2. **Colocar en estructura** `$VAULT/.obsidian/plugins/<plugin-id>/`:
   ```bash
   PLUG="$VAULT/.obsidian/plugins"; mkdir -p "$PLUG/<id>"
   curl -sL -o "$PLUG/<id>/main.js"       ".../download/<tag>/main.js"
   curl -sL -o "$PLUG/<id>/manifest.json" ".../download/<tag>/manifest.json"
   curl -sL -o "$PLUG/<id>/styles.css"    ".../download/<tag>/styles.css"
   ```
   El `manifest.json` trae el `id` real — la carpeta DEBE llamarse igual o
   Obsidian no lo reconoce.

3. **Activar.** Obsidian lee `$VAULT/.obsidian/community-plugins.json` (lista de
   IDs habilitados). Si no existe, crearlo. Sin este archivo el plugin esta en
   disco pero NO carga:
   ```json
   ["templater-obsidian", "flexplorer"]
   ```

4. **Config por plugin (`data.json`).** En `$PLUG/<id>/data.json`. Extraer las
   keys reales de `this.settings.*` del main.js:
   ```bash
   grep -oE "this\.settings\.[a-zA-Z]+" "$PLUG/<id>/main.js"
   ```

5. **Reiniciar Obsidian + trust.** El usuario debe reiniciar y aceptar
   "plugins de comunidad" (primer dialogo). Sin ese paso nada carga.

## Config verificada

**Templater (v2.25.0):**
```json
{
  "templates_folder": "Templates",
  "folder_templates": [
    {"folder": "10-Diario", "template": "Templates/Nota-Diaria.md"},
    {"folder": "20-Proyectos", "template": "Templates/Nota-Proyecto.md"}
  ],
  "trigger_on_file_creation": true,
  "enable_system_commands": false
}
```
`enable_system_commands: false` es el default SEGURO (Templater puede ejecutar
child_process/curl; solo activar por peticion explicita).

**Flexplorer (v4.0.5):**
```json
{"debugMode": false, "showHidden": false, "pinnedFiles": [], "items": {}}
```

## Plantillas Templater
Crear plantillas markdown en `<vault>/Templates/` con frontmatter + `tp.date.now()`
y `tp.file.title`. El plugin las aplica automaticamente por carpeta mapeada.
Ejemplo minimo:
```
---
type: daily
tags: [diario]
created: <% tp.date.now("YYYY-MM-DD") %>
---
# <% tp.date.now("dddd, DD [de] MMMM YYYY") %>
```

## Pitfalls
- **JSON valido** en community-plugins.json (coma final fuera, sin romper).
- **El `id` del manifest es la verdad**: carpeta con nombre distinto no carga.
- Falta de `main.js` = plugin muerto aunque exista manifest.
- Python en git-bash no lee rutas MSYS `/c/...` en `open()` — pasar rutas Windows
  `C:/Users/...` al invocar python.
- El paso de "trust de plugins de comunidad" en Obsidian es manual obligatorio.

## Verificacion
- `community-plugins.json` contiene el id.
- `$PLUG/<id>/manifest.json` existe y su `id` == nombre de carpeta.
- Tras reinicio: el plugin aparece activo en la UI.

Detalle de sesion: `references/community-plugin-install.md` (replicable completo
con los comandos exactos y configs verificadas).
