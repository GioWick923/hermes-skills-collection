---
name: python-version-provisioning
description: "Proyecto exige Python más nuevo que el host: usa uv run."
version: 1.0.0
author: Hermes curator
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [python, uv, version, provisioning, 3.12, f-string]
    related_skills: [uv-run-helper, local-model-install]
---

# Python Version Provisioning con uv

Cuando un proyecto (clonado de GitHub, skill con helper, herramienta) exige una
versión de Python MÁS NUEVA que la del host, no parchees el código: deja que
**uv provisione la versión correcta automáticamente**.

## When to Use
- Clonaste un repo y `pip install -e .` falla con `ModuleNotFoundError: No module named 'cx_Freeze'`.
- Un `main.py` da `SyntaxError: unterminated string literal` en f-strings con saltos de línea.
- `pyproject.toml` declara `requires-python = ">=3.12"` pero el host tiene 3.11.
- Cualquier proyecto con sintaxis 3.12+ (f-strings multilínea, `type` statements).

## Workflow (verified 2026-08-20 con TikTokDownloader)

```bash
cd <proyecto>
uv run --no-sync python main.py --help   # uv descarga CPython 3.12.x SOLO si falta
                                          # (log: "Using CPython 3.12.13")
uv pip install -r requirements.txt        # deps en el .venv del proyecto (NO global)
uv run python main.py --help              # corre con la versión correcta
```

- `uv` está en `~/.local/bin/uv` (o `which uv`).
- `uv run` sin `--no-sync` puede intentar sync del pyproject; con `--no-sync`
  evitas sorpresas si no quieres instalar todo el proyecto editable.

## Señales de "este proyecto necesita Python más nuevo"

| Síntoma | Causa real | Fix |
|---------|-----------|-----|
| `SyntaxError: unterminated string literal` en línea con `f"` y `{` | f-strings multilínea = sintaxis 3.12+ | `uv run` (no parchear) |
| `ModuleNotFoundError: cx_Freeze` al `pip install -e .` | setup.py con build hooks modernos; pip 3.11 intenta build | `uv run`/`uv pip install -r` |
| `requires-python = ">=3.12"` en pyproject | declaración explícita | `uv run` |

## Pitfalls
- **No parchear f-strings uno por uno**: si el proyecto es 3.12+, habrá muchos.
  Parchear el primero da falsa sensación de progreso; el próximo archivo falla igual.
- **`pip install -r` con python 3.11 del sistema** contamina el venv global y puede
  romper otras herramientas (choca con rich de hermes-agent). Usar SIEMPRE
  `uv pip install` dentro del proyecto (uv crea su propio `.venv` aislado).
- **El primer `uv run` descarga el intérprete** (~30-60s) — no es un error.
- Verificar la versión usada: `uv run python --version` → 3.12.x, no 3.11.

## Verificación
- [ ] `uv run python --version` muestra la versión requerida (no la del host)
- [ ] `main.py --help` arranca sin SyntaxError
- [ ] Dependencias en `.venv` del proyecto, no en el global
