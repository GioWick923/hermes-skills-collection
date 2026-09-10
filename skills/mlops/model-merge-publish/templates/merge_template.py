#!/f/ComfyUI/venv/Scripts/python.exe
"""Merge template: A*wA + B*wB + C*wC, VAE de C, salida fp16"""
import safetensors.torch as st
import os, time

BASE = "F:/Modelos/checkpoints"
OUT = f"{BASE}/NOMBRE_SALIDA.safetensors"

files = {
    "A": f"{BASE}/MODELO_A.safetensors",
    "B": f"{BASE}/MODELO_B.safetensors",
    "C": f"{BASE}/MODELO_C.safetensors",
}
WA, WB, WC = 0.40, 0.30, 0.30  # <-- AJUSTAR

print("Loading models...")
data = {tag: st.load_file(path, device="cpu") for tag, path in files.items()}

keys_all = set(data["A"].keys()) | set(data["B"].keys()) | set(data["C"].keys())
print(f"Unique keys: {len(keys_all)}")

out = {}
merged = copied = vae = 0
for k in sorted(keys_all):
    if k.startswith("first_stage_model."):  # VAE del modelo C
        out[k] = data["C"][k].clone()
        vae += 1
        continue
    in_a, in_b, in_c = k in data["A"], k in data["B"], k in data["C"]
    if in_a and in_b and in_c:
        out[k] = (data["A"][k].float()*WA + data["B"][k].float()*WB + data["C"][k].float()*WC).half()
        merged += 1
    elif in_a and in_b:
        t = WA+WB; out[k] = ((data["A"][k].float()*WA + data["B"][k].float()*WB)/t).half(); copied += 1
    elif in_a and in_c:
        t = WA+WC; out[k] = ((data["A"][k].float()*WA + data["C"][k].float()*WC)/t).half(); copied += 1
    elif in_b and in_c:
        t = WB+WC; out[k] = ((data["B"][k].float()*WB + data["C"][k].float()*WC)/t).half(); copied += 1
    elif in_a: out[k] = data["A"][k].clone(); copied += 1
    elif in_b: out[k] = data["B"][k].clone(); copied += 1
    elif in_c: out[k] = data["C"][k].clone(); copied += 1

print(f"Merged:{merged} Copied:{copied} VAE:{vae} Total:{len(out)}")
out_gb = sum(v.numel()*v.element_size() for v in out.values())/(1024**3)
print(f"Output: {out_gb:.1f}GB, fp16, VAE={'YES' if vae else 'NO'}")

print("Saving...")
st.save_file(out, OUT)

# Verify
v = st.load_file(OUT, device="cpu")
vae_ok = any(k.startswith("first_stage_model") for k in v.keys())
print(f"✅ Verified: {len(v)} tensors, {os.path.getsize(OUT)/1024**3:.1f}GB, VAE={'YES' if vae_ok else 'NO'}")
