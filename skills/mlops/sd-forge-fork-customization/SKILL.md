---
name: sd-forge-fork-customization
description: Prune, customize, and wrap a Stable Diffusion WebUI Forge / Forge-Neo fork (e.g. gi0baro/forge-neo) into a minimal personal build, and expose it headlessly so an agent (Hermes) can drive image generation without a browser. Use when the user wants a "mini" / "ligero" Forge with fewer models, a lighter UI, or agent-operated generation over an existing fork.
---

# SD Forge Fork Customization (mini + headless bridge)

## When to use
- User has a Forge / Forge-Neo fork and wants only some models kept ("mini", "ligero", "pocos parámetros").
- User wants the WebUI operable by an agent (Hermes) without opening Gradio.
- User wants to clone parts of forge-neo and adapt them to a personal fork.

## Architecture map (forge-neo)
- `backend/loader.py` — **THE registry.** Imports each engine class AND lists them in `possible_models = [...]`. Edit BOTH together.
- `backend/diffusion_engine/<model>.py` — one file per engine (Flux, ZImage, Lumina2, Anima, Chroma, Qwen, Wan, Sd15, Sdxl, Flux2). Each subclasses `ForgeDiffusionEngine` with `matched_guesses`.
- `backend/nn/<model>.py` — NN module defs. `svdq.py` holds Nunchaku (SVDQ) variants; `wan_vae.py` is reused by Anima (keep it).
- `backend/huggingface/<Model>/` — tokenizer/VAE/scheduler config folders per model family.
- `modules/api/api.py` — **FastAPI already exposes** `/sdapi/v1/txt2img` and `/sdapi/v1/img2img`. REUSE it; do NOT reimplement the engine.
- `modules/processing.py` — `StableDiffusionProcessingTxt2Img` / `Img2Img` dataclasses + `process_images(p)`.
- `modules/sd_models.py` — `forge_model_reload()`, `get_closet_checkpoint_match()`, `checkpoints_list`.

## Pruning steps (keep e.g. Z-Image, Lumina, Anima, Flux)
1. Delete engine files you don't want: `backend/diffusion_engine/{chroma,flux2,qwen,sd15,sdxl,wan}.py`.
2. Delete their config folders: `backend/huggingface/{Chroma,Qwen,Wan-AI,circlestone-labs,runwayml}/` (keep folders for kept models).
3. Edit `backend/loader.py`: remove the `from backend.diffusion_engine.X import Y` lines AND set `possible_models = [Flux, Lumina2, ZImage, Anima]` (your kept set).
4. Delete `backend/nn/{chroma,wan}.py`. **Do NOT delete `backend/nn/qwen.py`** if `svdq.py` imports it (NunchakuQwen is inert without a Qwen model, but the import must resolve). Keep `nn/wan_vae.py` (Anima uses it).
5. `python -m py_compile backend/loader.py backend/diffusion_engine/*.py backend/nn/*.py` — must be clean.

## Model reload pattern (Forge-specific — NOT A1111)
Forge has NO `shared.reload_model_weights(op=...)`. Switch checkpoint at runtime with:
```python
import modules.sd_models as sd_models
info = sd_models.get_closet_checkpoint_match(alias)   # alias = checkpoint folder/.safetensors name
sd_models.model_data.forge_loading_parameters = dict(
    checkpoint_info=info,
    additional_modules=shared.opts.forge_additional_modules,
    unet_storage_dtype=None,
)
sd_models.forge_model_reload()
```

## Headless bridge (agent operates the mini)
- Reuse the existing Forge REST API. A client POSTs to `/sdapi/v1/txt2img` with `override_settings: {"sd_model_checkpoint": <name>}` and `send_images: true`; save returned base64 PNGs.
- Mount the API on a custom entrypoint via `from modules.api.api import Api; Api(app, queue_lock)` on a FastAPI app, OR just launch `webui.py --api` and hit the endpoints.
- **FastAPI app construction (copy webui.py exactly):** `from fastapi import FastAPI` + `from modules.api.api import handle_exception` → `app = FastAPI(exception_handlers={Exception: handle_exception})` → `api = Api(app, queue_lock)` → `api.launch(server_name, port, root_path)`. **The handler is named `handle_exception` in `modules/api/api.py`** — NOT `_handle_exception` (that name only exists as a local def inside `webui.py`). `Api(None, ...)` won't work; you must pass a real FastAPI app.
- For a minimal Gradio UI, imitate `webui.py`'s sequence: `initialize_forge(); initialize.imports(); initialize.initialize();` then build your own `gr.Blocks` calling `process_images` (wrap the callback in `wrap_gradio_call` from `modules.call_queue`).

## Preferred integration: `--mini` flag on the existing launcher (cleaner than a standalone entrypoint)
Rather than a self-initializing `webui_mini.py` that duplicates env prep, hook into forge-neo's own launcher so the mini inherits ALL environment preparation (torch/CUDA/xformers the user already installed):
1. Register the flag in `modules/cmd_args.py`: `_parser.add_argument("--mini", action="store_true", help="...")` (add right after the `parser = _parser.add_argument_group(...)` line).
2. In `modules/launch_utils.py` `start()`, branch before the default `import webui`:
   ```python
   if "--mini" in sys.argv:
       import webui_mini
       webui_mini.main()
   else:
       import webui
       webui.api_only() if "--nowebui" in sys.argv else webui.webui()
   ```
3. `webui_mini.main()` then **assumes initialization already ran** (launch.py called `initialize.initialize()` before `start()` dispatches) — it must ONLY mount FastAPI+Api and the Gradio UI, then return so `launch.py` runs `main_thread.loop()`. **Do NOT call `initialize.initialize()` again inside `main()`** (double-init). Keep a `if __name__ == "__main__":` block that DOES self-initialize, only for standalone debug runs.
4. `run_mini.bat` / `run_mini.sh` just call `python launch.py --mini --port 7860` — no manual `uv pip install torch`; `prepare_environment()` handles deps.

## Pitfalls
- **`process()` crashes on missing model folders after pruning (FileNotFoundError on tokenizer.json).** `backend/huggingface/__init__.py` runs `process()` at startup (called from `initialize_forge()`), which decompresses bundled `*.tokenizer.json.xz` into per-model dirs like `Wan-AI/Wan2.1-T2V-14B/tokenizer/tokenizer.json`. When you deleted that model's folder during pruning, `decompress()` does `open(target, "wb")` on a path whose parent dirs don't exist → `FileNotFoundError: ...tokenizer.json`. **Robust fix (keeps all models, one line):** add `os.makedirs(os.path.dirname(target), exist_ok=True)` as the first line inside `decompress()`. This auto-creates the destination tree for Wan AND every other family (z-image, flux2, anima) whose folder is absent. Alternative if you truly dropped a family: comment out its `if not os.path.isfile(Token.X): decompress(...)` block in `process()`. Note several families (z_image, f2_4b, f2_9b, anima) share `Token.z_compress` as source — verify the `.xz` sources exist (`wan/neta/z.tokenizer.json.xz`) before assuming a source-file problem.
- **Stale absolute paths in tracebacks.** A traceback showing an old drive path (e.g. `D:\1\ag\mini-forge-neo\...`) while the live repo is elsewhere (e.g. `C:\Users\<user>\mini-forge-neo`) means the user launched from a moved/deleted copy or a shortcut pointing at the old location. Locate the real repo (`dir /s /b <drive>\*mini-forge*`) and edit/run THAT, not the path in the traceback. On slow/external drives `ls`/`search_files` may time out — use `cmd //c "dir /s /b ..."` instead.
- **Don't port non-Forge-native models.** Ernie Image (Baidu) is a DiT served via `sglang`, not a diffusion_engine checkpoint — it won't fit the Forge pattern. If a target model isn't in the fork and needs external porting, confirm with the user; **default to dropping it** ("olvida X y continua").
- **Dead-code false alarms:** after pruning, `loader.py` still has `if cls_name == "ChromaTransformer2DModel"` branches referencing deleted `nn` modules. These are inert (no `possible_models` entry reaches them) and `py_compile` passes. Cleaner to delete the whole `elif cls_name ==` branch for pruned families, but it's optional — leaving them is harmless.
- **`svdq.py` depends on `nn/qwen.py`.** If you deleted `backend/nn/qwen.py` and `svdq.py` has `from backend.nn.qwen import ...` (NunchakuQwen classes span ~180 lines), the import breaks. Two fixes: (a) **restore it with `git checkout -- backend/nn/qwen.py`** — it's small, self-contained, and the code path is inert without a Qwen model (SIMPLEST, chosen this session); or (b) surgically delete the NunchakuQwen class block from `svdq.py`. Prefer (a).
- **Checkpoint alias must match `checkpoints_list` keys** (folder/`.safetensors` name). Validate at runtime with `list(sd_models.checkpoints_list.keys())`.
- **Shallow-clone gaps ≠ your deletions.** `git status` after `git clone --depth 1` may show `D` for tokenizer/VAE config folders (Anima, Wan-AI, runwayml) you never touched — the shallow tree didn't fetch them. Engines load these from the real checkpoint in `models/` at runtime via `huggingface_guess.model_list`, not from `backend/huggingface/<Model>/`, so a kept model (e.g. Anima) still works. Verify the engine's actual imports (`backend.nn.<model>`, `backend.patcher.*`) rather than panicking over the `huggingface/` folder.
- **No-GPU sandbox:** you cannot generate here. Verify via `py_compile` + symbol-existence grep + strict `import` search. State the GPU blocker honestly; never fabricate image output.

## Verification (no GPU)
Use `scripts/verify_forge_prune.py` — checks: (a) target engines deleted & kept present, (b) `possible_models` contents, (c) **no REAL `import` statements** to deleted modules (string literals in `if cls_name ==` are OK), (d) every Forge symbol your wrapper calls exists in the fork, (e) `py_compile` of changed files.

### Verifier gotchas (learned the hard way)
- **Whole-repo syntax check: use `compileall`, NOT `py_compile *.py`.** Passing 1300+ files as argv on Windows throws `WinError 206 (filename or extension too long)`. Instead: `compileall.compile_dir(REPO, quiet=1, rx=re.compile(r"[\\/]\.git[\\/]"))` in Python, or `find . -name '*.py' -not -path './.git/*' -print0 | xargs -0 python -m py_compile` in bash (xargs batches to stay under the limit).
- **Keep the "deleted modules" list in sync with what you actually deleted.** If you restore `nn/qwen.py` (per the svdq pitfall above), REMOVE `qwen` from the verifier's deleted-modules regex — otherwise it FAILs on a legitimate restored import. This produced a spurious `19/20 FAIL` this session.
- **`check()` must record a real bool.** A helper like `def check(n,c): results.append(bool(c))` then `all(results)` — do NOT do `ok = ok and check(...)` when `check` returns `None`; that silently forces the aggregate to falsy and every run reports FAILURES despite all-PASS lines.

## Support files
- `references/forge-neo-architecture.md` — repo map + reload snippet + REST endpoints.
- `references/pruning-checklist.md` — exact delete/edit commands.
- `scripts/verify_forge_prune.py` — corrected ad-hoc verifier (check() returns bool; distinguishes real imports from string literals).
- `scripts/verify_decompress_makedirs.py` — re-runnable probe for the `decompress()` makedirs fix; reproduces the missing-model-folder FileNotFoundError and asserts the patched function creates the dir tree. Pass the repo's `backend/huggingface/__init__.py` path as arg.
- `templates/mini_bridge_client.py` — MiniClient headless-bridge pattern.
