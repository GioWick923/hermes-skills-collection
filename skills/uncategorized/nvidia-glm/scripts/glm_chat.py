#!/usr/bin/env python3
"""nvidia-glm: chat streaming contra z-ai/glm-5.2 vía NVIDIA Integrate API.

La API key se lee de NVAPI_KEY (variable de entorno) o de
~/.config/nvidia-glm/.env (NVAPI_KEY=...). NUNCA se hardcodea en este archivo.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_USE_COLOR = sys.stdout.isatty() and os.getenv("NO_COLOR") is None
_REASONING_COLOR = "\033[90m" if _USE_COLOR else ""
_RESET_COLOR = "\033[0m" if _USE_COLOR else ""


def _load_dotenv() -> None:
    """Carga NVAPI_KEY desde ~/.config/nvidia-glm/.env si no está en el entorno."""
    if os.getenv("NVAPI_KEY"):
        return
    env_path = Path.home() / ".config" / "nvidia-glm" / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key == "NVAPI_KEY" and not os.getenv("NVAPI_KEY"):
            os.environ["NVAPI_KEY"] = val


def main() -> int:
    _load_dotenv()

    api_key = os.getenv("NVAPI_KEY")
    if not api_key:
        sys.stderr.write(
            "ERROR: NVAPI_KEY no encontrada. Crea ~/.config/nvidia-glm/.env "
            "con la linea:\n  NVAPI_KEY=nvapi-...\n"
        )
        return 1

    # Prompt: argumento, o stdin si no hay argumento.
    prompt = " ".join(sys.argv[1:]).strip()
    if not prompt:
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
    if not prompt:
        sys.stderr.write("Uso: glm_chat.py \"tu pregunta\"\n")
        return 2

    try:
        from openai import OpenAI
    except ImportError:
        sys.stderr.write("ERROR: el paquete 'openai' no esta instalado en este Python.\n")
        return 1

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
    )

    completion = client.chat.completions.create(
        model="z-ai/glm-5.2",
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        top_p=1,
        max_tokens=16384,
        seed=42,
        stream=True,
    )

    for chunk in completion:
        if not getattr(chunk, "choices", None):
            continue
        if len(chunk.choices) == 0 or getattr(chunk.choices[0], "delta", None) is None:
            continue
        delta = chunk.choices[0].delta
        if getattr(delta, "content", None) is not None:
            print(delta.content, end="")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
