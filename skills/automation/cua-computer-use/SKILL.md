name: cua-computer-use
description: |
  Provides computer-use capabilities via the CUA (Computer Use Agent) framework.
  Enables controlling the host machine (via cua-driver) or sandboxed environments
  to take screenshots, type text, click, and run commands.
  Requires: cua-driver installed and running, and the Python packages `cua-sandbox` and `cua-s1`.
dependencies:
  - cua-sandbox>=0.8.0
  - cua-s1>=0.0.0
  - cua-driver-rs (installed via https://cua.ai/driver/install.ps1)
  - torch (for cua-s1 model)
  - huggingface_hub (to load cua-s1-forms model)
# When to use
Use when you need to:
- Automate GUI tasks on the host machine (Windows, macOS, Linux)
- Take screenshots of the desktop or specific windows
- Fill forms, click buttons, type text programmatically
- Run commands in a shell and capture output
- Use the cua-s1 form-filling model to score and select options in forms
# MCP Integration (PREFERRED — Hermes has these tools natively now)

cua-driver is registered as an MCP server in Hermes config (57 tools enabled). In a NEW Hermes session, these tools are available directly by name, no Python needed:

- Desktop control: `list_apps`, `launch_app` (hidden, no focus steal), `kill_app`, `bring_to_front`, `list_windows`, `set_window_frame`
- UI automation: `click` (prefer element_index over coords), `double_click`, `right_click`, `drag`, `type_text`, `press_key`, `hotkey`, `set_value` (UIA ValuePattern), `scroll`, `invoke_menu`
- Vision/inspection: `get_window_state` (UIA tree structured + Markdown), `get_accessibility_tree`, `get_desktop_state` (full-res screenshot), `zoom`, `verify_state` (bounded predicates)
- Clipboard: `clipboard_read`, `clipboard_write` (text/image/file)
- Browser: `get_browser_state`, `browser_navigate`, `browser_click`, `browser_type`, `browser_pointer`, `browser_download`, `browser_set_input_files`, `browser_dialog`
- Sessions/cursor: `start_session`, `end_session`, `get_session`, `move_cursor`, `set_agent_cursor_theme` (agent cursor overlay visible to user)
- Recording: `start_recording`/`stop_recording` (trajectory export), `replay_trajectory` (re-run recorded turns)
- Diagnostics: `health_report`, `check_permissions`, `get_screen_size`, `get_cursor_position`

Typical workflow: `list_apps` → `launch_app` → `get_window_state` (find element_index) → `click`/`type_text`/`set_value` → `verify_state`.

# Python API (alternative, works in current session)

```python
import cua_sandbox as cua

async def example():
    async with cua.localhost() as host:
        screenshot = await host.screenshot()
        await host.mouse.click(100, 200)
        await host.keyboard.type("Hello")
        await host.keyboard.keypress("enter")
        result = await host.shell.run("dir")
        print(result.stdout)
```
# Notes
- The cua-driver must be running as a background service. On Windows, you can start it with:
  `cua-driver.exe serve` (ensure it's in your PATH or use the full path).
- For security, the driver should be granted appropriate permissions (accessibility, screen recording).
- The cua-s1 model can be loaded from Hugging Face (`cua-ai/cua-s1-forms`) to score form options.
- This skill does not start the driver automatically; assume it's already running or started via a separate mechanism (e.g., Hermes cronjob).