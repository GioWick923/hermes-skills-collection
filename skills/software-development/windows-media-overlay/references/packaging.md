# Packaging the overlay as a Windows exe (PyInstaller)

## One-time setup
```bash
python -m venv venv-build
venv-build/Scripts/pip install PySide6 winsdk deep-translator pyinstaller
```
Rule: the build venv holds ONLY the app's dependencies — PyInstaller follows transitive
imports, so a shared env with a data/ML stack inflates the exe ~10x.

## Build procedure (in order)
1. **Kill any running copy first**: `taskkill /F /IM <App>.exe` (single-slash Windows syntax;
   some MSYS shells reject the `//F` form). A running exe locks `dist/<name>.exe` -> the build
   fails with WinError 5 at the final copy step while the log still looks successful.
2. Build:
   ```bash
   venv-build/Scripts/python -m PyInstaller --noconfirm --onefile --windowed \
       --name <App> --add-data "fonts;fonts" app.py
   ```
   `--add-data "fonts;fonts"` bundles TTFs; onefile extracts them to `sys._MEIPASS`.
3. **Verify the artifact landed**: check the exe's timestamp AND size in dist/ (`ls -la
   --time-style=+%H:%M:%S dist/`). A BUILD_DONE line is not proof — a blocked copy leaves the
   previous binary.
4. If the build dies silently mid-hooks inside the agent terminal (log tail frozen, no
   PyInstaller process), write the steps into a `build.bat` and launch detached:
   `cmd /c "start \"\" /min build.bat"`, then poll the log file. Foreground with a generous
   timeout (600s+) is the first choice; detached is the fallback.
5. Hand the dist path to the user — the GUI can only be verified by them (agent terminal
   cannot host windowed apps).

## onefile vs onedir
- **onefile**: single portable exe; 5-10s startup from self-extraction to %TEMP% every launch.
  Tell the user this delay is normal, not a hang.
- **onedir**: instant startup, folder of files. Prefer when startup speed matters more than
  a single file.

## Typography (bundled fonts)
- Commercial faces (Gotham, Avenir) cannot be bundled legally. Bundle free clones
  (Montserrat ~= Gotham, Mulish ~= Avenir) and probe at startup:
  `QFontDatabase.addApplicationFont` for every TTF under `sys._MEIPASS/fonts`, then pick the
  first preferred family present in `QFontDatabase.families()` — so if the user later
  installs the real commercial face, it is used with zero code changes.
- Install fonts per-user without admin: copy TTFs to
  `%LOCALAPPDATA%\Microsoft\Windows\Fonts\` and register each under
  `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Fonts` with value name
  `<Family> <Style> (TrueType)` -> full file path.
- Overlay styling preference: side lines Light weight with a heavy vanish (alpha ~40 base,
  decaying with distance from the active line); active line ~+18% scale, weight 600.
