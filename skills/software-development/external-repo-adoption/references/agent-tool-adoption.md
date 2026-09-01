# Agent-Tool Adoption (CLI + extension/skill, no repo port)

Clase distinta de `port-recipes.md`: NO se porta data/scripts a una skill nueva.
Se adopta una **herramienta de agente** que el ecosistema ya empaqueta: CLI nativo
+ (opcionalmente) su propia skill/plugin por harness. Se instala tal cual y se
verifica con ejecución real. Ejemplo verificado (2026-09-01): **Tencent/BrowserSkill**.

## Cuándo
- El repo es un producto de agente (CLI Rust/Go + extensión de navegador o plugin),
  no una librería de data/scripts ni una skill knowledge pura.
- El repo declara soporte para Hermes Agent (lista de harnesses en su README).
- El usuario pide "instálalo, hazlo primera opción, regístralo en el índice Pulpo".

## Recipe verificada — BrowserSkill (Tencent)
- Repo: `github.com/Tencent/BrowserSkill` (MIT, ~1.5k⭐). CLIs: `bsk` + daemon + extensión.
- **Instalar CLI (Windows)** — PowerShell; va a `~/.local/bin/bsk.exe`, verifica checksum:
  ```bash
  powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Tencent/BrowserSkill/main/install.ps1 | iex"
  export PATH="$HOME/.local/bin:$PATH"; bsk --version
  ```
- **Instalar la skill dentro de Hermes** (el repo trae SKILL.md por harness):
  ```bash
  bsk install-skill --list                 # ver harnesses (Hermes = id `hermes`)
  bsk install-skill --harness hermes --yes # escribe $LOCALAPPDATA/hermes/skills/browser-skill/
  ```
  NO usar el número de lista como id (`--harness 11` falla); usar el slug `hermes`.
- **Verificar**:
  ```bash
  bsk status   # daemon pid, WS port, browsers connected, active sessions
  bsk doctor   # ok/FAIL por check
  ```
  Estado esperado tras instalar CLI+skill: todo `ok` EXCEPTO `extension connected`
  = FAIL (`0 browsers connected`) — ese check es el único que solo el humano cierra
  (instalar la extensión en Chrome/Edge y esperar popup verde). `bsk doctor` puede
  tardar >60s esperando la extensión → dar timeout generoso o background.
- **Ciclo de uso obligatorio** (la skill instalada lo exige): `bsk session start`
  (captura id de 4 letras) → cada comando con `--session <id>` → `bsk session stop <id>`
  SIEMPRE al terminar, incluso en errores (finally-style).
- **Registrar adopción** (convención del usuario Gio): sección en el índice Pulpo
  del vault (`50-Indice/Indice de Capacidades Pulpo.md`) + entrada en `EVOLUTION.md`
  + nota en memoria. Para "primera opción", poner la herramienta en la tabla de reglas
  de decisión del índice y marcar alternativas (CDP 9222 Civitai, TV-MCP :9223, stealth).

## Pitfalls
- **La skill instalada por la herramienta es user-owned**, no curator-managed: no
  editarla en curaduría autónoma; el recipe durable va en este reference.
- El instalador del repo agrega `~/.local/bin` a PATH en `.bashrc`; en la sesión actual
  hay que `export PATH="$HOME/.local/bin:$PATH"` antes de `bsk`.
- La extensión es el único paso no automatizable por el agente (instalación de addon);
  dejar el prompt claro al usuario y volver a correr `bsk doctor` tras que confirme.
- `bsk doctor` bloquea esperando la extensión → no lanzarlo en foreground sin timeout.

## Verificación mínima (nunca "validado" sin prueba real)
- `bsk --version` imprime versión → CLI ok.
- `bsk install-skill --harness hermes --yes` reporta ruta escrita → skill ok.
- `bsk status` muestra daemon corriendo → runtime ok.
- Prueba end-to-end real SOLO después de que el usuario instale la extensión
  (abrir página → leer contenido → cerrar sesión); hasta entonces reportar
  "pendiente de extensión", no "validado".
