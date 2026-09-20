# 🖥️ CUA — Computer-Use completo para Hermes

> **El upgrade de capacidades más grande desde el navegador:** Hermes controla TODO el escritorio Windows de forma nativa, precisa y sin robar el foco del usuario.

## ¿Qué es?

Integración completa de [trycua/cua](https://github.com/trycua/cua) con Hermes Agent. Convierte a Hermes en un agente **computer-use real**: ve pantallas, lanza apps, lee árboles de accesibilidad, hace clic en elementos exactos, escribe texto, controla el clipboard, navega el navegador y graba trayectorias repetibles.

## Arquitectura instalada (4 capas)

```
HERMES
├── 1. MCP cua-driver (57 herramientas nativas)  ← acción directa, sin código
├── 2. Skills (conocimiento experto del fabricante)
│     ├── cua-driver      (SKILL.md 68KB + WINDOWS/BROWSER/RECORDING.md)
│     ├── cua-computer-use (API Python + pitfalls verificados)
│     ├── gui-automation   (patrón Look→Act→Verify)
│     └── jev-use          (loop de decisión acotado)
├── 3. Driver cua-driver-rs 0.28.2 (autostart Windows)
└── 4. Python: cua_sandbox 0.8.0 + cua-s1 + modelo cua-s1-forms.pt
```

## Instalación

### Driver (Windows)
```powershell
irm https://cua.ai/driver/install.ps1 | iex
```
Auto-arranca con Windows (tarea `cua-driver-serve`, RunLevel=Highest).

### MCP en Hermes
```bash
hermes mcp add cua-driver --command "C:/Users/<user>/AppData/Local/Programs/Cua/cua-driver/bin/cua-driver.exe" --args mcp
```

### Python (respaldo)
```bash
pip install cua-sandbox cua-s1
```

## Uso principal — herramientas MCP (57)

**Flujo canónico: `snapshot → act → verify`**

| Categoría | Herramientas clave |
|---|---|
| Apps | `list_apps`, `launch_app` (oculto, sin foco), `kill_app`, `bring_to_front`, `list_windows`, `set_window_frame` |
| UIA nativo | `get_window_state` (árbol UIA), `click` (element_token), `set_value`, `invoke_menu`, `type_text`, `hotkey`, `scroll` |
| Verificación | `verify_state` (predicados deterministas), `zoom`, `get_desktop_state` (screenshot nativo) |
| Clipboard | `clipboard_read`, `clipboard_write` (texto/imagen/archivo) |
| Navegador | `get_browser_state`, `browser_navigate/click/type/pointer/download/set_input_files` |
| Trayectorias | `start_recording`/`stop_recording` (JSON + video + PNG antes/después), `replay_trajectory` |
| Sesiones | `start_session`, `end_session`, cursor overlay visible (`set_agent_cursor_theme`) |

### Pitfalls verificados (lecciones reales)

- `import cua_sandbox as cua` — el paquete `cua` exige Python ≥3.12 (Hermes usa 3.11)
- `keypress()`, no `press()` · shell → `.stdout`, no `.output`
- JSON en `cua-driver call`: pipe vía stdin (PowerShell 5.1 rompe las comillas)
- `set_value` requiere `element_token` del snapshot (no `element_index` solo)
- `zoom`: región máx 500px, formato `x1,y1,x2,y2`
- `kill_app` solo mata procesos lanzados por el propio runtime de CUA
- `start_recording`: campo `output_dir` (no `directory`)

## Uso Python (respaldo / sesión actual)

```python
import cua_sandbox as cua

async def main():
    async with cua.localhost() as host:
        shot = await host.screenshot()          # screenshot del escritorio
        await host.mouse.click(100, 200)         # clic
        await host.keyboard.type("hola")         # escribir
        await host.keyboard.keypress("enter")    # tecla
        res = await host.shell.run("dir")        # comando → res.stdout
```

## Test de verificación (ejecutado 2026-09-19, todo ✓)

```
✓ list_apps (detectó Hermes, Zen Browser, procesos)
✓ start_session + start_recording → 27 turnos grabados con before/after.png
✓ launch_app notepad oculto (sin robar foco) → pid 1356
✓ type_text en background (PostMessage WM_CHAR)
✓ get_window_state → árbol UIA (11 elementos, element_tokens)
✓ verify_state con predicados estructurados
✓ clipboard_write + clipboard_read (privacidad preservada)
✓ hotkey con diagnóstico UIA experto (detectó app XAML/UWP)
✓ Trayectoria: turn-00001..27 con action.json + evidence.json + screenshots
✓ kill_app con safety check (denegó proceso ajeno — correcto)
✓ Screenshot escritorio vía Python localhost
```

## Ventajas vs. solo navegador/vision

1. **UIA nativo** — clic por elemento exacto, no adivinando coordenadas con screenshots
2. **Sin robar foco** — `launch_app` oculto + input en background: opera mientras usas la PC
3. **Verificación determinista** — `verify_state` prueba predicados, no "parece que sí"
4. **Trayectorias repetibles** — graba pasos exitosos y re- ejecútalos (macros autónomas)
5. **Clipboard completo** — pegar imágenes/archivos en apps nativas
6. **Navegador por pid exacto** — más preciso que CDP genérico
7. **Cursor overlay** — el usuario VE qué hace el agente (temas + física)

## Fuentes
- Repo: https://github.com/trycua/cua
- Docs: https://cua.ai/docs
- Modelo forms: https://huggingface.co/cua-ai/cua-s1-forms
