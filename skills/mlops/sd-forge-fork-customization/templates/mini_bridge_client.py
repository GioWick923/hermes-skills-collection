"""TEMPLATE — headless bridge client for a pruned Forge-Neo mini build.

Copy into your fork's `mini/` dir, fill in MODEL_ALIASES with YOUR real
checkpoint names, and run `python mini_bridge_client.py "prompt" --model Z-Image`.
The agent (Hermes) imports `MiniClient` and calls `.txt2img(...)` to drive
generation without opening Gradio.
"""
import base64, io, os, sys, time
from typing import Optional
from PIL import Image
import requests

# Make sibling mini_core importable if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class MiniClient:
    def __init__(self, base_url: str = "http://127.0.0.1:7860"):
        self.base = base_url.rstrip("/")

    # EDIT: alias-friendly -> EXACT checkpoint name in Forge
    MODEL_ALIASES = {
        "Z-Image": "z-image-turbo",
        "Lumina":  "lumina-image-2.0",
        "Anima":   "anima",
        "Flux":    "flux.1-dev",
    }
    DEFAULTS = {
        "Z-Image": dict(steps=25, cfg=4.0, width=1024, height=1024, sampler="euler", scheduler="simple"),
        "Lumina":  dict(steps=30, cfg=4.0, width=1024, height=1024, sampler="dpmpp_2m", scheduler="simple"),
        "Anima":   dict(steps=25, cfg=4.5, width=1024, height=1024, sampler="euler", scheduler="simple"),
        "Flux":    dict(steps=20, cfg=3.5, width=1024, height=1024, sampler="euler", scheduler="simple"),
    }

    def _resolve(self, model):
        return self.MODEL_ALIASES.get(model, model)

    def _post(self, endpoint, payload, timeout=600):
        r = requests.post(f"{self.base}{endpoint}", json=payload, timeout=timeout)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
        return r.json()

    def _save(self, b64_list, model, prompt):
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "mini")
        os.makedirs(out, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        paths = []
        for i, b in enumerate(b64_list):
            Image.open(io.BytesIO(base64.b64decode(b))).save(os.path.join(out, f"hermes_{model.lower()}_{stamp}_{i}.png"))
            paths.append(os.path.join(out, f"hermes_{model.lower()}_{stamp}_{i}.png"))
        return paths

    def txt2img(self, prompt, model="Z-Image", negative="", steps=None, cfg=None,
                 width=1024, height=1024, seed=-1, batch_size=1, save=True):
        d = self.DEFAULTS.get(model, self.DEFAULTS["Z-Image"])
        payload = {
            "prompt": prompt, "negative_prompt": negative,
            "steps": steps or d["steps"], "cfg_scale": cfg or d["cfg"],
            "width": width, "height": height, "seed": seed, "batch_size": batch_size,
            "sampler_name": d["sampler"], "scheduler": d["scheduler"],
            "override_settings": {"sd_model_checkpoint": self._resolve(model)},
            "send_images": True, "save_images": False,
        }
        out = self._post("/sdapi/v1/txt2img", payload)
        return self._save(out.get("images", []), model, prompt) if save else out.get("images", [])


if __name__ == "__main__":
    import json, argparse
    a = argparse.ArgumentParser()
    a.add_argument("prompt"); a.add_argument("--model", default="Z-Image")
    a.add_argument("--url", default="http://127.0.0.1:7860")
    ns = a.parse_args()
    c = MiniClient(ns.url)
    print(json.dumps({"ok": True, "paths": c.txt2img(ns.prompt, model=ns.model)}, indent=2))
