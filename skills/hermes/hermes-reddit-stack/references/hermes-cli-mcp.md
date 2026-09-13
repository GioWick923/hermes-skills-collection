# Hermes CLI real + MCP integration (verified this session)

Comandos reales contra `hermes-agent/venv/Scripts/hermes.exe`. Validados ejecutando
los binarios, no inferidos.

## Command surface (lo que SÍ existe)
- **Preguntar/resumir sin interacción** (no existe `hermes ask`):
  `hermes chat -q "PROMPT" -Q`
  (`-Q` = quiet/non-interactive; `-q` = single query)
- **Enviar a plataforma de mensajería** (no existe `hermes message`):
  `hermes send -t telegram "MSG"`
  - Requiere home channel: `hermes config set TELEGRAM_HOME_CHANNEL <chat_id>`
    → luego `-t telegram` resuelve solo al DM.
  - O explícito: `hermes send -t telegram:<chat_id> "MSG"`.
  - Listar targets: `hermes send --list telegram`.
- **Exponer Hermes como MCP server** (stdio, 10 tools):
  `hermes mcp serve`
  Cliente MCP (Claude Code / Cursor / VS Code) lo consume con:
  ```json
  { "mcpServers": { "hermes": { "command": "hermes", "args": ["mcp", "serve"] } } }
  ```
  Tools expuestos (de `hermes-agent/mcp_serve.py`): conversations_list,
  conversation_get, messages_read, attachments_fetch, events_poll, events_wait,
  messages_send, permissions_list_open, permissions_respond, channels_list.
- **Gestionar cron**: `hermes cron ...` (el tool `cronjob` lo envuelve; el script
  del cron debe vivir en `~/.hermes/scripts/`, no ruta absoluta).

## Pitfall crítico (costó 1 bug falso)
`subprocess.run([...])` SIN chequear `returncode` reporta éxito falso: un comando
CLI inexistente sale rc!=0 pero NO lanza excepción. SIEMPRE validar `r.returncode == 0`
antes de imprimir "enviado"/"ok". Esto es por qué el digest "enviado por telegram"
decía OK pero nunca llegaba (usaba `hermes message`, que no existe).

## MCP integration research (condensed, authoritative)
- **Hermes lado**: puede SER MCP server (`hermes mcp serve`, stdio, 10 tools,
  superficie tipo OpenClaw bridge). Clientes tipo Claude Code lo consumen nativo.
- **Pi (pi.dev) lado**: README oficial dice literal **"No MCP."** — Build CLI tools
  with READMEs (Skills), or build an extension that adds MCP support. Es anti-MCP
  por filosofía (véase post de mariozechner "what if you don't need mcp").
  → Pi NO puede consumir Hermes vía MCP. Integración Pi↔Hermes requiere puente por
  CLI (`hermes send` / `hermes chat -q`) o un extension TS custom, no MCP.
- **Conclusión práctica**: usa `hermes mcp serve` para conectar Hermes a
  Claude Code / Cursor / VS Code (donde MCP SÍ funciona). Para Pi, usarlo como
  coding agent autónomo sin acoplar, o puentear por shell.
