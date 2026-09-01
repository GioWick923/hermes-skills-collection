---
category: creative
name: opentoonz
description: "Use when installing OpenToonz or generating .tnz projects."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [animation, opentoonz, 2d, tnz, ghibli, install, windows]
    related_skills: [manim-video, p5js]
---

# OpenToonz (2D Animation)

OpenToonz is the open-source 2D animation software from the Studio Ghibli lineage (Toonz Studio Ghibli Version). This skill covers (a) installing it silently on Windows and (b) generating complete `.tnz` animation projects programmatically — cels + scene file — so the user can open and press Play without manual steps.

## When to use
- User asks to install OpenToonz ("INSTALA ESTO" with the GitHub URL).
- User wants an OpenToonz example/project generated ("dame un ejemplo a verlo", "crea una animación").
- Any 2D animation deliverable where OpenToonz is the target app.

## Install (Windows, silent)

1. **Only the official source** — the README insists there are NO mirrors: `https://opentoonz.github.io/` or the GitHub repo releases. Download from `https://github.com/opentoonz/opentoonz/releases/download/<tag>/OpenToonzSetup.exe`.
2. Identify installer type by scanning the binary for `Inno Setup` (OpenToonz uses Inno Setup 6.x) vs `Nullsoft` (NSIS). This picks the silent flags.
3. **Run the .exe DIRECTLY from bash — do NOT wrap in `cmd //c start /wait`.** The wrapper swallows the arguments: the installer exits 0 but installs NOTHING (no files, no log). Verified failure mode.
4. Silent flags (Inno): `./OpenToonzSetup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /LOG=inno2.log`
5. **`/LOG=` is the diagnostic key**: if no log file appears after running, the installer never executed its install logic — your invocation was wrong (see pitfall 3), not the installer.
6. Installs to `C:\Program Files\OpenToonz` (binaries) + `C:\OpenToonz stuff` (projects/plugins). The installer also sets registry keys (`TOONZLIBRARY`, etc.).
7. Verify: log ends with `Installation process succeeded.`; `OpenToonz.exe` present; launch it and confirm the process stays alive with a real window title.

## Generating a .tnz project programmatically

Key format facts (discovered by cloning the official sample — do NOT trust "it's a zip" descriptions):

- **`.tnz` is plain XML**, not a zip. Root: `<tnz framecount="N" version="71.0">` with sections `<generator>`, `<properties>` (cameras/outputs/cleanup), `<levelSet>` (level definitions + Cast/Audio folders), `<xsheet>` (columns/cells + pegbars + fxnodes), `<history>`.
- **Levels reference image sequences by frame pattern**: a level path `$scenefolder\\pelota..png` maps to files `pelota0001.png`, `pelota0002.png`, … — `..` = 4-digit zero-padded frame number, no separator before the digits.
- **Cells**: `<cell>0 1 <level id='1'/>0001 1</cell>` = (start_frame, duration, level_ref, drawing_name, flag). One cell per frame for a sequence (frame i → drawing `%04d` of i+1).
- **Best approach: clone an official sample and regex-modify it**, not build from scratch. Sample: `https://github.com/opentoonz/opentoonz_sample/raw/master/cleanup.tnz`. Modify: framecount, generator version, fps, cameraRes/Size, level path, output path, cells.
- **CRLF + escaped-backslash trap**: the sample file has CRLF line endings and paths with 4 literal backslashes (`$scenefolder\\\\dwanko`). Exact string replace fails. Use regex with `re.S` and tolerant patterns, e.g. `re.sub(r'\$scenefolder[^"]*?A\.\.tif', r'$scenefolder\\\\pelota..png', x)`.
- fps 12 with 12 frames = 1s loop; add squash (wide/flat) on the impact frame and stretch on drop/rise for a classic bounce.

## Verification without a vision model

The vision model may fail to load local screenshots ("no image provided"). Verify renders by **PIL pixel analysis**: count pixels matching the expected color in the expected region (e.g. red ball → `r>170, g<120, b<120`). Also confirm via the process `MainWindowTitle` (contains the scene name + `[sandbox]`).

## Script

`scripts/gen_bounce_project.py` — complete working generator: 12 bouncing-ball cels (`pelota0001..0012.png`), `preview_bounce.gif`, and `mi_bounce.tnz` built by cloning + regex-modifying the official sample. Run: `python gen_bounce_project.py [output_dir]` (defaults to `C:\OpenToonz stuff\projects\mi_bounce`).

## Pitfalls
- `cmd //c start /wait` breaks Inno Setup silent install → exits 0, nothing installed. Always invoke the .exe directly.
- Missing `/LOG` makes silent-install failure opaque.
- `.tnz` is XML, not a zip (some docs/web results say zip — they are wrong for scene files; zipped project *packages* are a different, manual workflow).
- Sample `.tnz` has CRLF + 4-backslash paths → regex, never literal replace.
- Vision may not load local files → pixel-analyze with PIL instead.
