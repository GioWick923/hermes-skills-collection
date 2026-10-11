#!/usr/bin/env python
"""Weighted additive merge of N SDXL/Illustrious checkpoints (CPU) + optional VAE bake.

Edit the A/B/C paths, weights, and OUT below, then run with the ComfyUI venv python:
    /f/ComfyUI/venv/Scripts/python.exe merge_checkpoints.py

Weights must sum to 1.0. Keys present in only one model carry through unmerged.
To bake an SDXL VAE, set BAKED_VAE to the sdxl_vae path (overwrites first_stage_model.*).
"""
import safetensors.torch as st
import torch
import time

A = r"F:/Modelos/checkpoints/MODEL_A.safetensors"   # primary / base
B = r"F:/Modelos/checkpoints/MODEL_B.safetensors"   # secondary
C = r"F:/Modelos/checkpoints/MODEL_C.safetensors"   # tertiary (set C=None for a 2-model merge)
OUT = r"F:/Modelos/checkpoints/MERGED.safetensors"
BAKED_VAE = None  # or r"F:/Modelos/vae/sdxl_vae.safetensors"

wA, wB, wC = 0.50, 0.25, 0.25  # sum == 1.0

print("Cargando A...", flush=True)
ta = st.load_file(A, device="cpu")
print("Cargando B...", flush=True)
tb = st.load_file(B, device="cpu")
tc = st.load_file(C, device="cpu") if C else None

out = {}
comunes = 0
for k in ta.keys():
    a = ta[k]
    if tc is not None and k in tb and k in tc and tb[k].shape == a.shape and tc[k].shape == a.shape:
        out[k] = a.float() * wA + tb[k].float() * wB + tc[k].float() * wC
        comunes += 1
    elif k in tb and tb[k].shape == a.shape:
        out[k] = a.float() * wA + tb[k].float() * wB
        comunes += 1
    else:
        out[k] = a.float()

for k in tb.keys():
    if k not in out:
        out[k] = tb[k].float()
if tc is not None:
    for k in tc.keys():
        if k not in out:
            out[k] = tc[k].float()

if BAKED_VAE:
    print("Horneando VAE...", flush=True)
    tvae = st.load_file(BAKED_VAE, device="cpu")
    for k, v in tvae.items():
        out[k] = v

print(f"comunes={comunes} total={len(out)}", flush=True)
vae_n = sum(1 for k in out if k.startswith("first_stage_model"))
print(f"VAE tensores={vae_n}", flush=True)
print(f"Guardando {OUT}...", flush=True)
t0 = time.time()
st.save_file(out, OUT)
print(f"Guardado en {time.time()-t0:.1f}s", flush=True)
print("MERGE_DONE", flush=True)
