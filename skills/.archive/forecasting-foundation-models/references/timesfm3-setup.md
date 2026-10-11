# TimesFM-3 (Google) — instalación y API reales

> Adquirido 2026-09-01. TimesFM-3 es el modelo de forecasting multivariado de Google
> (330M params, zero-shot, top-1 en Gift-Eval/FEV-Bench/Time vs Chronos-2, Toto-2.0).
> Blog: https://research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/

## PITFALL CRÍTICO (por esto se pierde tiempo)
**`pip install timesfm==3.0.0` desde PyPI NO trae la clase TimesFM-3.**
El wheel de PyPI 3.0.0 solo expone `ForecastConfig`, `configs`, `timesfm_2p5` — es el
código de la 2.5 reempaquetado. La clase 3.0 real vive en el **repo de GitHub**, no en PyPI.

- SÍNTOMA: `from timesfm import TimesFM_2p5_200M_torch` existe, pero no hay nada "3.0",
  y cargar el checkpoint `google/timesfm-3.0-pytorch` con la clase 2.5 falla.
- El README del repo aún marca "Latest: TimesFM 2.5" aunque la 3.0 ya salió (31-ago-2026);
  el código 3.0 está en `src/timesfm3/`.

## Instalación correcta (desde el repo, editable)
```bash
git clone --depth 1 https://github.com/google-research/timesfm.git
cd timesfm
uv venv .venv --python 3.11
uv pip install --python .venv/Scripts/python.exe torch --index-url https://download.pytorch.org/whl/cu126
uv pip install --python .venv/Scripts/python.exe -e .
```
El pyproject solo requiere numpy, huggingface_hub, safetensors (+ torch opcional).
Uso verificado: Windows + venv uv + torch 2.14.0+cu126 en RTX 3060.

## API (clase real: `TimesFM3Forecaster`)
```python
import sys, numpy as np, torch
sys.path.insert(0, r'<repo>/src')            # o pip install -e . y no hace falta
from timesfm3.timesfm3_forecaster import TimesFM3Forecaster

torch.set_float32_matmul_precision('high')
fc = TimesFM3Forecaster.from_pretrained("google/timesfm-3.0-pytorch", device="cuda")
# fc.global_context -> max context (~15360)

# predict() = una serie. context shape (n,) univariada O (k,n) multivariada.
out = fc.predict(context=ctx, horizon=30, return_quantiles=True)
# out.forecast shape (horizon,) univ / (k,horizon) multi
# out.quantiles shape (horizon,9) / (k,horizon,9)  -> [q0.1..q0.9]

# predict_batch(contexts=[...], horizon=..., ...) -> iterator de ForecastOutput
```

### Covariates (la ventaja multivariada de la 3.0)
`predict(..., past_only_covariates=arr, past_future_covariates=arr)`
- `past_future_covariates` = señales **conocidas en el futuro** (calendario de earnings,
  decisiones Fed, promociones). El modelo "mira" esas fechas y anticipa el bump.
- Formato: arrays, cada fila = una serie de covariable, alineada al context.

## Uso en trading (lectura honesta de la literatura)
- ❌ Zero-shot en **precios** → R² negativo, pierde contra buy-and-hold (papers alphaXiv,
  arXiv:2507.07296). NO es oráculo de precios.
- ✅ Forecast de **volatilidad** (|retorno|) y **correlación multi-activo** (SPY+QQQ+VIX
  juntos) → sí supera. Úsalo para sizing/risk y como input del grafo, no como señal única.
- 🟡 **Fine-tune con tus datos** (LoRA vía PEFT) es donde más gana.

## Estado verificado (máquina de Gio)
- Venv: `C:\Users\<USER>\AppData\Local\timesfm\.venv` (torch 2.14.0+cu126, CUDA ok)
- Script: `C:\Users\<USER>\AppData\Local\timesfm\test_market.py` (SPY+QQQ+VIX, 252d → 30d)
- Repo: `C:\Users\<USER>\AppData\Local\timesfm-repo`
- Modelo cacheado 1.3GB en `~/.cache/huggingface/hub/models--google--timesfm-3.0-pytorch`
- Test real: forecast multi shape (3,30,9) punto+cuantiles ✅

## Alternativa GPU-barata ya instalada (Chronos-2)
Para univariado simple en CPU, `chronos` (skill chronos-forecasting) sigue siendo la
opción sin GPU. TimesFM-3 es el upgrade cuando necesitas multivariado + covariables.
