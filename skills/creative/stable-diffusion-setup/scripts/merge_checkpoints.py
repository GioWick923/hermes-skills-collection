#!/usr/bin/env python3
"""Weighted checkpoint merger for SDXL/Illustrious (UNet) models.

Why this exists: Forge Neo's native Checkpoint Merger raises
`Error merging checkpoints: argument 'metadata': 'dict' object cannot be converted
to 'PyString'` when any input is a modern fp32 checkpoint with dict metadata
(verified with SDXL/Illustrious fp32 models). A Python safetensors merge avoids
the bug and gives full weight control + optional VAE baking.

USAGE: edit the 6 path/weight constants below, then run with a ComfyUI venv
python (needs safetensors + torch), e.g.:
    /f/ComfyUI/venv/Scripts/python.exe merge_checkpoints.py

Only merge models of the SAME architecture (all SDXL / all Illustrious / all
Flux). Merging SDXL + Flux produces a larger hybrid that loads but outputs noise.
Check architecture BEFORE merging by grepping tensor keys for
`model.diffusion_model` (SDXL/Illustrious UNet) vs `double_blocks`/`single_blocks`
(Flux DiT).
"""
import safetensors.torch as st
import torch
import time

# ===== EDIT THESE =====
A = r"F:/Modelos/checkpoints/model_A.safetensors"   # base model (or largest)
B = r"F:/Modelos/checkpoints/model_B.safetensors"   # second model
C = None  # optional third model, e.g. r"F:/Modelos/checkpoints/model_C.safetensors" or None
VAE = None  # optional VAE to bake in, e.g. r"F:/Modelos/vae/sdxl_vae.safetensors" or None
OUT = r"F:/Modelos/checkpoints/MERGED_fp32.safetensors"

# weights must sum to 1.0. For 2 models: 0.5/0.5 (a la par).
# For 3: e.g. 0.50/0.25/0.25 (base dominant). For "base .50 + two equal": 0.50/0.25/0.25
wA, wB, wC = 0.50, 0.50, 0.0
# =====================

def load(p):
    if p is None:
        return None
    print(f"Loading {p}...", flush=True)
    return st.load_file(p, device="cpu")

ta = load(A)
tb = load(B)
tc = load(C)

# Architecture sanity check (SDXL/Illustrious = UNet)
def arch(t):
    names = " ".join(t.keys()).lower()
    if "model.diffusion_model" in names:
        return "SDXL/Illustrious"
    if "double_blocks" in names or "single_blocks" in names:
        return "Flux/DiT"
    return "unknown"

for label, t in (("A", ta), ("B", tb), ("C", tc)):
    if t is not None:
        print(f"{label}: {len(t)} tensors, arch={arch(t)}", flush=True)

keys = list(ta.keys())
out = {}
comunes = 0
for k in keys:
    a = ta[k]
    if k in tb and tb[k].shape == a.shape and (tc is None or (k in tc and tc[k].shape == a.shape)):
        v = a.float() * wA + tb[k].float() * wB
        if tc is not None and k in tc and tc[k].shape == a.shape:
            v = v + tc[k].float() * wC
        out[k] = v
        comunes += 1
    elif k in tb and tb[k].shape == a.shape:
        out[k] = a.float() * wA + tb[k].float() * wB
        comunes += 1
    else:
        out[k] = a.float()

for t in (tb, tc):
    if t is not None:
        for k in t.keys():
            if k not in out:
                out[k] = t[k].float()

# Bake VAE (overwrites any first_stage_model.* already present)
if VAE:
    tvae = load(VAE)
    for k, v in tvae.items():
        out[k] = v

print(f"comunes={comunes} total={len(out)}", flush=True)
vae_n = sum(1 for k in out if k.startswith("first_stage_model"))
print(f"VAE tensors in output: {vae_n}", flush=True)

# Disk space check BEFORE writing (each fp32 merge is ~14GB on disk + RAM load of all inputs)
import os, shutil
need_gb = sum(os.path.getsize(p) for p in (A, B, C) if p and os.path.exists(p)) / 2**30
free_gb = shutil.disk_usage(os.path.dirname(OUT)).free / 2**30
print(f"inputs total ~{need_gb:.1f}GB, free on disk ~{free_gb:.1f}GB", flush=True)
if free_gb < need_gb + 3:
    raise SystemExit("ABORT: not enough free disk for merge + output (need ~14GB+). Free space first.")

print(f"Saving {OUT} ({len(out)} tensors)...", flush=True)
t0 = time.time()
st.save_file(out, OUT)
print(f"Saved in {time.time()-t0:.1f}s", flush=True)
print("DONE", flush=True)
