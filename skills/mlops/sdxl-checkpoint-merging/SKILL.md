---
name: sdxl-checkpoint-merging
description: >-
  Merge SDXL/Illustrious checkpoints; shrink fp32 to fp16.
---

# SDXL / Illustrious Checkpoint Merging

Merge several SDXL-class checkpoints (Illustrious, NoobAI, custom merges) into
one combined model, and optionally bake a VAE or convert to fp16. All local, on
the user's ComfyUI/Forge stack (`F:/Modelos/checkpoints`, RTX 3060 12GB, 98GB RAM).

## When to use
- User wants to combine models: "merge", "mezclar modelos", "haz una merge",
  combine base + small models for a broader/better model.
- User wants to shrink a 14GB fp32 checkpoint to ~7-8GB (fp16).
- User wants to "train" a model — merge is a STARTING POINT, not training.
  A merge is a weighted tensor sum (algebra), NOT learning. Real training =
  LoRA/finetune on top of the merged base. Say this clearly (House honesty).

## Environment facts (validated on this rig)
- Checkpoints live in `F:/Modelos/checkpoints/*.safetensors`.
- Merge with the ComfyUI venv python: `/f/ComfyUI/venv/Scripts/python.exe`.
- fp32 SDXL ≈ 13.8-14.2GB; fp16 ≈ 7.27GB; sdxl_vae.safetensors = 334MB.
- RAM is ample (98GB) — loading several 14GB models + merging is fine in CPU.

## Estado de ejecución (schema fijo — se actualiza, no se acumula historia)

> Patrón SKILL.state: en cada paso el agente ve solo `(spec + Estado + última observación)`.
> El razonamiento intermedio se descarta tras validar. NUNCA dejes que el merge dependa
> de reconstruir el contexto desde el historial del chat.

Mantén un objeto JSON único como estado canónico. Cada paso del merge:
1. LEE el estado actual → 2. Decide el siguiente paso viendo `(Este skill + Estado + última observación)` → 3. VALIDA la actualización → 4. Actualiza y descarta la traza.

```json
{
  "archivos": {"A": null, "B": null, "C": null},
  "pesos": {"wA": 0.50, "wB": 0.25, "wC": 0.25},
  "arq_verificada": false,
  "vae": null,
  "fp16": false,
  "salida": null,
  "disco_libre_gb": null,
  "pasos_completados": []
}
```

Reglas del estado:
- **`archivos`**: rutas FINALES confirmadas de lo que existe en disco (listar con `ls` antes, no asumir).
- **`disco_libre_gb`**: `df -h /f` ANTES de escribir — un merge 14GB llena `F:` y `save_file` muere con `os error 112`. Si < 25GB libres, parar y pedir liberar.
- **`arq_verificada`**: la inspección de keys es PRECONDICIÓN obligatoria (Step 1). No marcar `true` sin haber corrido la inspección.
- **`pasos_completados`**: lista de strings con los pasos ya hechos (`arch_verify`, `merge`, `bake_vae`, `fp16`, `validate`). Sirve como "qué falta" sin re-leer todo.

## Step 1 — Verify architecture compatibility FIRST
Never merge blind. Different architectures (SDXL-UNet vs FLUX/Chroma-DiT vs
Krea2) cannot be merged (garbage or error). Inspect keys:
```bash
/f/ComfyUI/venv/Scripts/python.exe -c "
import safetensors.torch as st
for f in ['MODEL_a.safetensors','MODEL_b.safetensors']:
    t=st.load_file(f, device='cpu'); keys=list(t.keys())
    names=' '.join(keys).lower()
    arch = 'SDXL/Illustrious' if 'model.diffusion_model' in names else ('FLUX/DiT' if 'double_blocks' in names else '?')
    print(f, len(keys), arch)"
```
- SDXL/Illustrious: has `model.diffusion_model.input_blocks.*`, 2515 tensors (fp32) / 2765 with VAE.
- FLUX/Chroma: `double_blocks`/`single_blocks` → NOT compatible with SDXL smalls.
- If user mentions "Chroma" as a base for SDXL merges, it is FLUX-arch — incompatible.
  Correct them (they often mistake it for SDXL).

## Step 2 — Weighted additive merge (N models)
Write a script (see `scripts/merge_checkpoints.py` for a ready 3-model version).
Core pattern: load all on CPU, sum per-key `a.float()*wA + b.float()*wB + c.float()*wC`
where weights sum to 1.0. Weights come from the user (e.g. base 0.50, rest 0.25/0.25).
Keys present in only one model carry through unmerged.

## Step 3 — Bake an SDXL VAE (optional)
To bake `F:/Modelos/vae/sdxl_vae.safetensors` into the result, overwrite every
`first_stage_model.*` key in the merged dict with the VAE's tensors. Result gains
~248 tensors (2515→2765) and the file grows slightly. User then does NOT need a
separate VAE in Forge/ComfyUI.

## Step 4 — fp32 → fp16 conversion (halve size)
For a ~7GB result: reload fp32, `.half()` every key EXCEPT `first_stage_model.*`
(keep VAE fp32 or as-is; it is small). Output ≈ 7.27GB. Visually identical for
generation; only loses a little theoretical precision. User's target range 7-9GB.

## Step 5 — Validate before reporting success (validador determinista = anti-corrupción)
El validador NO es opcional: lo que no se valida aquí no se reporta como éxito.
Al cargar el resultado, confirma TODAS estas condiciones, no solo "que cargue":
```bash
/f/ComfyUI/venv/Scripts/python.exe -c "
import safetensors.torch as st
t=st.load_file('OUT.safetensors', device='cpu'); keys=list(t.keys())
vae=[k for k in keys if k.startswith('first_stage_model')]
m=[k for k in keys if not k.startswith('first_stage_model')][0]
print(len(keys), len(vae), t[m].dtype)"
```
- [ ] Archivo existe en disco (`ls -lh OUT.safetensors`) y tamaño coherente (fp32≈14GB / fp16≈7.3GB).
- [ ] Tensor count esperado (2515 sin VAE / 2765 con VAE) — un número menor = merge corrupto.
- [ ] dtype correcto (fp32 o fp16 según lo pedido).
- [ ] PAUSA final: en lugar de marcar "validado" a ciegas, pregúntate (regla staff-engineer) — ¿lo aceptaría yo si fuera el que genera imágenes con esto? Si hay duda, NO es válido.
Run in background (loading 14GB takes >60s — foreground curl/python timeouts).
Use `terminal(background=true, notify=["DONE","VALIDADO","ERROR"])`.

## Pitfalls (learned the hard way)
- **Disk fills fast**: every 14GB fp32 merge eats ~14GB. Merging 8+ times leaves
  `F:` at 94-97% and `save_file` dies with `os error 112 (Espacio en disco)`.
  Check `df -h /f` BEFORE each merge. Merging merges-of-merges bloats disk fast;
  offer to delete intermediate 13-14GB files (never delete without explicit OK).
- **Forge UI merge button errors**: "Error merging checkpoints: argument 'metadata':
  'dict' object cannot be converted to 'PyString'" — a stale safetensors in Forge's
  native merger. Do NOT fight it; use the standalone python script instead.
- **Merges-of-merges converge to the mean**: each weighted average dilutes identity.
  After 3-4 iterations the "final" models look alike. Once the user likes one,
  recommend stopping merges and training a LoRA on that base.
- **Varios modelos "ULTRA AIO" / same file under two names**: before merging, list
  the directory and confirm which exact files exist — users often name the same
  file twice. Verify before assuming 3 distinct inputs.
- Rename final file with a clean name (e.g. `NDREAM_ULTRA.safetensors`) after
  conversion — user prefers Civitai-style short names, not the technical merge suffix.

## Verification / honest reporting
Report sizes and tensor counts from real `ls`/`load_file` output, never claimed.
State clearly: merge ≠ training. Recommend LoRA finetune as the next real step.
