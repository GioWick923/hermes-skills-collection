---
category: note-taking
name: obsidian-cli
description: Interactuar con vaults de Obsidian usando el CLI oficial `obsidian` para leer, crear, buscar y gestionar notas, tareas, propiedades y más. También soporta desarrollo de plugins/themes (reload, eval JS, screenshots, DOM). Usa cuando el usuario pida interactuar con su vault Obsidian, gestionar notas, buscar contenido, o hacer operaciones del vault desde la línea de comandos. Adaptado de kepano/obsidian-skills (MIT), 2026-09-01.
version: 1.0.0
author: Hermes Agent (port from kepano/obsidian-skills)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [obsidian, vault, notes, cli, plugin-development, markdown]
    related_skills: [obsidian, hermes-obsidian-ops]
---

# Obsidian CLI

Usa el CLI `obsidian` para interactuar con una instancia de Obsidian corriendo. **Requiere que Obsidian esté abierto.**

## Prerrequisito
- CLI oficial `obsidian` instalado y en PATH.
- Obsidian abierto (los comandos apuntan a la instancia corriendo).
- Verificar: `obsidian help`.

## Integración con Gio (2026-09-01)
- Port de kepano/obsidian-skills (MIT), solo la skill `obsidian-cli`.
- Tu vault canónico: `C:/Users/<USER>/Documents/Obsidian Vault/`.
- **Complementa** (no reemplaza) a `hermes-obsidian-ops` + bridge script (`hermes_obsidian_bridge.py`):
  - Bridge: operaciones por script (remember/recall/consolidate) — funciona sin que Obsidian esté abierto.
  - obsidian-cli: operaciones directas sobre la instancia abierta (search en vivo, eval JS, dev).
- Elegir según contexto: si Obsidian está cerrado → bridge; si está abierto y necesitas CLI → obsidian-cli.

## Sintaxis
**Parámetros** toman valor con `=`. Cita valores con espacios:
```bash
obsidian create name="Mi Nota" content="Hola mundo"
```
**Flags** son switches booleanos sin valor:
```bash
obsidian create name="Mi Nota" silent overwrite
```
Para contenido multilínea usa `\n` para nueva línea y `\t` para tab.

## File targeting
Muchos comandos aceptan `file` o `path`. Sin ninguno, usa el archivo activo.
- `file=<nombre>` — resuelve como wikilink (solo nombre, sin ruta ni extensión)
- `path=<ruta>` — ruta exacta desde la raíz del vault, ej. `carpeta/nota.md`

## Vault targeting
Comandos apuntan al vault más recientemente enfocado por defecto. Usa `vault=<nombre>` como primer parámetro:
```bash
obsidian vault="Mi Vault" search query="test"
```

## Patrones comunes
```bash
obsidian read file="Mi Nota"
obsidian create name="Nota Nueva" content="# Hola" template="Plantilla" silent
obsidian append file="Mi Nota" content="Nueva línea"
obsidian search query="término de búsqueda" limit=10
obsidian daily:read
obsidian daily:append content="- [ ] Nueva tarea"
obsidian property:set name="status" value="done" file="Mi Nota"
obsidian tasks daily todo
obsidian tags sort=count counts
obsidian backlinks file="Mi Nota"
```
Usa `--copy` en cualquier comando para copiar al portapapeles. Usa `silent` para evitar que se abran archivos. Usa `total` en comandos list para obtener un conteo.

## Desarrollo de plugins
### Ciclo develop/test
Tras cambios de código en un plugin o theme:
1. **Recargar** el plugin para tomar los cambios:
   ```bash
   obsidian plugin:reload id=mi-plugin
   ```
2. **Chequear errores** — si aparecen, arregla y repite desde el paso 1:
   ```bash
   obsidian dev:errors
   ```
3. **Verificar visualmente** con screenshot o inspección DOM:
   ```bash
   obsidian dev:screenshot path=screenshot.png
   obsidian dev:dom selector=".workspace-leaf" text
   ```
4. **Chequear consola** para warnings o logs inesperados:
   ```bash
   obsidian dev:console level=error
   ```

### Comandos de dev adicionales
Ejecutar JavaScript en el contexto de la app:
```bash
obsidian eval code="app.vault.getFiles().length"
```
Inspeccionar valores CSS:
```bash
obsidian dev:css selector=".workspace-leaf" prop=background-color
```
Alternar emulación mobile:
```bash
obsidian dev:mobile on
```
Corre `obsidian help` para ver comandos de dev adicionales incluyendo controles CDP y debugger.

## Verificación
- [ ] `obsidian help` disponible (CLI instalado)
- [ ] `obsidian search query="..."` funciona con Obsidian abierto
- [ ] Comandos daily/property/tasks operativos

## Nota
Si el CLI `obsidian` no está instalado en tu sistema, esta skill queda documentada como referencia; usa `hermes-obsidian-ops` (bridge) que no requiere Obsidian abierto. Para instalar el CLI oficial: https://help.obsidian.md/cli
