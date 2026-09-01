#!/usr/bin/env python
"""
AD-HOC verifier for a pruned Forge-Neo fork (NO GPU required).

Checks:
 (A) target engines deleted, kept engines present
 (B) possible_models contents correct
 (C) no REAL `import` statements to deleted modules
     (string literals like `if cls_name == "ChromaTransformer2DModel"` are OK)
 (D) every Forge symbol referenced by the mini wrapper exists in the fork
 (E) py_compile of changed files is clean

Run:  python verify_forge_prune.py  <repo_path>
This is a temporary check, not a committed test suite.
"""
import os, re, subprocess, sys

REPO = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\<USER> GAMES\mini-forge-neo"
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))

# (A) engines
eng = set(f for f in os.listdir(os.path.join(REPO, "backend", "diffusion_engine")) if f.endswith(".py"))
deleted = {"chroma.py","flux2.py","qwen.py","sd15.py","sdxl.py","wan.py"}
kept = {"anima.py","flux.py","lumina.py","zimage.py","base.py"}
check("6 motores borrados", deleted.isdisjoint(eng), f"presentes:{deleted & eng}")
check("4+base quedan", kept.issubset(eng), f"faltan:{kept - eng}")

# (B) possible_models
loader = open(os.path.join(REPO, "backend", "loader.py")).read()
pm = re.search(r"possible_models = \[(.*?)\]", loader).group(1)
for w in ["Flux","Lumina2","ZImage","Anima"]:
    check(f"possible_models tiene {w}", w in pm)
for n in ["Chroma","Flux2","QwenImage","StableDiffusion","Wan"]:
    check(f"possible_models SIN {n}", n not in pm)

# (C) real imports only (exclude svdq.py which legitimately imports nn.qwen)
bad = []
for r, _, fs in os.walk(REPO):
    if ".git" in r:
        continue
    for fn in fs:
        if not fn.endswith(".py"):
            continue
        p = os.path.join(r, fn)
        if p.endswith("nn\\svdq.py") or p.endswith("nn/svdq.py"):
            continue
        try:
            s = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        if re.search(r"^\s*(from backend\.(?:diffusion_engine|nn)\.(?:chroma|flux2|qwen|sd15|sdxl|wan)\b(?!\.)|import backend\.(?:diffusion_engine|nn)\.(?:chroma|flux2|qwen|sd15|sdxl|wan)\b)", s, re.M):
            bad.append(p)
check("sin imports REALES colgando (svdq excluido)", len(bad) == 0, str(bad[:2]))

# (D) symbol wiring vs real fork
def gc(pat, path):
    try:
        return len(re.findall(pat, open(path, encoding="utf-8", errors="ignore").read()))
    except Exception:
        return 0

api = os.path.join(REPO, "modules", "api", "api.py")
proc = os.path.join(REPO, "modules", "processing.py")
sd = os.path.join(REPO, "modules", "sd_models.py")
syms = {
    "Api": (api, r"class Api\b"),
    "forge_model_reload": (sd, r"def forge_model_reload\b"),
    "get_closet_checkpoint_match": (sd, r"def get_closet_checkpoint_match\b"),
    "checkpoints_list": (sd, r"checkpoints_list"),
    "process_images": (proc, r"def process_images\b"),
    "StableDiffusionProcessingTxt2Img": (proc, r"class StableDiffusionProcessingTxt2Img\b"),
    "StableDiffusionProcessingImg2Img": (proc, r"class StableDiffusionProcessingImg2Img\b"),
    "distilled_cfg_scale": (proc, r"distilled_cfg_scale"),
    "route txt2img": (api, r"sdapi/v1/txt2img"),
    "route img2img": (api, r"sdapi/v1/img2img"),
}
for n, (f, p) in syms.items():
    check(f"simbolo existe: {n}", gc(p, f) > 0, f"c={gc(p, f)}")

# (E) py_compile changed files
for f in ["mini/mini_core.py", "mini/mini_bridge.py", "webui_mini.py"]:
    fp = os.path.join(REPO, f)
    if not os.path.exists(fp):
        continue
    rr = subprocess.run([sys.executable, "-m", "py_compile", fp], capture_output=True, text=True)
    check(f"py_compile {f}", rr.returncode == 0, rr.stderr[:150])

# (F) whole-repo syntax check — BATCH-SAFE.
# Do NOT do `py_compile *.py` with 1000+ files as argv: Windows throws
# WinError 206 (command line too long). Use compileall.compile_dir instead.
import io, contextlib, compileall
_buf = io.StringIO()
with contextlib.redirect_stdout(_buf):
    _ok = compileall.compile_dir(REPO, quiet=1, rx=re.compile(r"[\\/]\.git[\\/]"))
check("sintaxis: TODO el repo compila", _ok, "" if _ok else _buf.getvalue()[-300:])

allpass = all(results)
print(f"\nPASS={sum(results)}/{len(results)}  === RESULT: {'ALL PASS' if allpass else 'FAILURES'} ===")
print("NOTE: real image generation needs GPU CUDA + torch (unavailable in many sandboxes).")
sys.exit(0 if allpass else 1)
