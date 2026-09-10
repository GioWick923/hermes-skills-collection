# Instalacion manual de plugins Obsidian — detalle de sesion (2026-09-01)

Replicacion completa verificada con Templater v2.25.0 y Flexplorer v4.0.5 en
Windows. Estructura del vault: `C:/Users/<USER>/Documents/Obsidian Vault`.

## ID de plugins y repos
- Templater: id=`templater-obsidian`, repo `SilentVoid13/Templater`
- Flexplorer: id=`flexplorer`, repo `kh4f/flexplorer`

## Obtener la release (ambos traen main.js + manifest.json + styles.css)
```bash
curl -s https://api.github.com/repos/SilentVoid13/Templater/releases/latest
curl -s https://api.github.com/repos/kh4f/flexplorer/releases/latest
```
Filtrar assets con python: `[print(a['name']) for a in d['assets']]`.

## Descargar a estructura (comandos exactos)
```bash
VAULT="/c/Users/<USER>/Documents/Obsidian Vault"
PLUG="$VAULT/.obsidian/plugins"
mkdir -p "$PLUG/templater-obsidian" "$PLUG/flexplorer"
curl -sL -o "$PLUG/templater-obsidian/main.js" \
  "https://github.com/SilentVoid13/Templater/releases/download/2.25.0/main.js"
curl -sL -o "$PLUG/templater-obsidian/manifest.json" \
  "https://github.com/SilentVoid13/Templater/releases/download/2.25.0/manifest.json"
curl -sL -o "$PLUG/templater-obsidian/styles.css" \
  "https://github.com/SilentVoid13/Templater/releases/download/2.25.0/styles.css"
curl -sL -o "$PLUG/flexplorer/main.js" \
  "https://github.com/kh4f/flexplorer/releases/download/4.0.5/main.js"
# ... repetir para manifest.json y styles.css de flexplorer
```

## Activar
`community-plugins.json` (no existia antes en este vault):
```json
["templater-obsidian", "flexplorer"]
```

## Configs (data.json)
- templater-obsidian/data.json: templates_folder="Templates", folder_templates
  (10-Diario->Nota-Diaria, 20-Proyectos->Nota-Proyecto), enable_system_commands=false.
- flexplorer/data.json: {"debugMode":false,"showHidden":false,"pinnedFiles":[],"items":{}}

## Plantillas creadas en <vault>/Templates/
- Nota-Diaria.md, Nota-Proyecto.md, Nota-Idea.md (frontmatter type/tags/created + tp.*).

## Pitfall Windows/python
- `python -c` con ruta `/c/Users/...` falla (`FileNotFoundError`). Pasar ruta
  Windows nativa `C:\Users\...` o `C:/Users/...` a python.

## Pendiente manual
- Reiniciar Obsidian y aceptar "plugins de comunidad" (trust) en el primer dialogo.
