---
category: software-development
name: uv-run-helper
description: "Run a Python helper script whose dependencies are NOT in the active venv using uv. Covers the 'uv run' ephemeral-environment pitfall and MSYS/Windows path + python-vs-python3 conventions."
tags: [uv, python, helper-script, windows, msys]
---

# Run a Python helper script with uv

## When to use
A skill or task hands you a `.py` helper and says "run `uv run python3 script.py`",
but the script needs a package that lives outside the run environment. Common in
Hermes skills that ship a `scripts/` helper and assume a pre-provisioned venv.

## The core pitfall (verified this session)
`uv run python3 scripts/x.py` does NOT use the package you installed with
`uv pip install <pkg>` into the Hermes venv. `uv run` builds an **ephemeral**
environment per invocation and will error with `Error: <pkg> not installed`
even though `uv pip install` reported success.

**Fix — pass the dependency inline with `--with`:**

```bash
uv run --with youtube-transcript-api python scripts/fetch_transcript.py "URL" --text-only --timestamps
```

`--with` makes the package available in the run environment without a persistent
install. Chain multiple deps with comma or repeated flags:
`uv run --with a --with b python script.py`.

## Windows / MSYS conventions (this user's host)
- Use **MSYS-style paths**, not Windows drive paths:
  `cd "/c/Users/<USER> GAMES/AppData/Local/hermes/skills/media/youtube-content"`
  NOT `cd "C:\Users\<USER> GAMES\..."` (fails: "No such file or directory").
- Use **`python`**, not `python3` — `python3` is missing on this host;
  `python` resolves to 3.11.x.
- `tempfile` is NOT available in MSYS `bash`. For ad-hoc temp scripts, write to a
  fixed path under `$APPDATA/Local/Temp/` (e.g. `.../Temp/hermes-verify-x.sh`)
  and `rm -f` it after.

## Verification pattern (ad-hoc, not suite green)
When a script has a side effect you must prove (e.g. sends a message), do not
claim success from syntax checks alone:
1. `bash -n script.sh` — syntax.
2. `command -v <cli>` — confirm the external tool exists in PATH.
3. Run a REAL but marked test action (e.g. send a "TEST, ignore" message) and
   read the tool's own confirmation (`Sent to ... chat_id: ...`, exit 0).
That closes the only real gap: that the effect actually delivers.
