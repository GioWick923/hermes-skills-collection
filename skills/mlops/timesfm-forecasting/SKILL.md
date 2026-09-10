---
category: mlops
name: timesfm-forecasting
description: "Forecast time series with Google TimesFM-3 for market data."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [timesfm, forecasting, timeseries, multivariate, trading, quant, timeseries-foundation-model]
    related_skills: [chronos-forecasting, alpha-orchestration, quant-research-cycle]
---

# TimesFM Forecasting (Google)

Zero-shot time series foundation model. **TimesFM-3** (2026-08) is the current
multivariate generation: 330M params, pre-trained on >1T time points, Nº1 on
GIFT-Eval / FEV-Bench / TIME, 9 quantiles per step, single-pass decode.

## Cuándo usar
- Necesitas forecast de series temporales, sobre todo **multivariado** (varias
  series que coevolucionan: SPY+QQQ+VIX, etc.).
- Quieres probabilidad (cuantiles 10-90%), no solo una línea.
- Trabajas con datos de mercado/quant y necesitas un modelo zero-shot local
  que corra en una GPU de consumo (12GB basta).

## ⚠️ Pitfall #1 — CRÍTICO: PyPI `timesfm==3.0.0` NO es TimesFM-3
`pip install timesfm` (o `uv pip install timesfm`) instala un paquete **3.0.0
que solo contiene las clases de la 2.5** (`TimesFM_2p5_200M_torch`). NO expone
el modelo 3.0 multivariado de 330M. El código 3.0 real vive en el repo:
`google-research/timesfm` → `src/timesfm3/timesfm3_forecaster.py`
(clase `TimesFM3Forecaster`).

**Fix — instalar desde el repo (editable):**
```bash
git clone --depth 1 https://github.com/google-research/timesfm.git
cd timesfm
uv pip install --python <venv>/Scripts/python.exe -e .   # instala timesfm==3.0.0 desde repo
# el paquete del repo sí trae timesfm3; el de PyPI no
```
Verificar: `from timesfm3.timesfm3_forecaster import TimesFM3Forecaster` debe importar.
Dependencias mínimas del paquete: numpy, huggingface_hub, safetensors (+ torch).

## Setup verificado (Windows + RTX 3060)
```bash
uv venv --python 3.11                    # 3.10/3.11/3.12
uv pip install --python .venv/Scripts/python.exe torch --index-url https://download.pytorch.org/whl/cu126
uv pip install --python .venv/Scripts/python.exe timesfm yfinance pandas
uv pip install --python .venv/Scripts/python.exe -e <ruta-repo-timesfm>   # el paso crítico
```
Nota: al instalar `-e .` del repo, reemplaza el paquete PyPI por el del repo.
torch cu126 con `torch.cuda.is_available()==True` en RTX 3060 → confirmado.

## API (TimesFM3Forecaster)
```python
import sys; sys.path.insert(0, "<repo>/src")   # o tras instalación editable no hace falta
import torch, numpy as np
torch.set_float32_matmul_precision("high")
from timesfm3.timesfm3_forecaster import TimesFM3Forecaster

fc = TimesFM3Forecaster.from_pretrained("google/timesfm-3.0-pytorch", device="cuda")
print(fc.device, fc.global_context)   # context máx = 15360

# Multivariado: context shape (n_series, context_len)
ctx = np.array([close_spy, close_qqq, close_vix], dtype=np.float32)  # (3, 252)
out = fc.predict(context=ctx, horizon=30, return_quantiles=True)
f, q = out.forecast, out.quantiles
# f.shape = (n_series, horizon); q.shape = (n_series, horizon, 9)

# Covariables:
#   past_only_covariates      -> solo histórico
#   past_future_covariates    -> eventos FUTUROS conocidos (earnings, CPI, Fed) — el modelo "ve el bump"
# predict_batch(contexts=[...], horizon=N) para varias series independientes
```
ForecastOutput: `.forecast` (mediana) y `.quantiles`. La mediana está en el
índice 4 de las 9 cuantiles (10-90%).

## Datos de mercado
Usar `yfinance`: `yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)`.
Alinear múltiples tickers a la longitud mínima antes de formar la matriz (3, n).

## ⚠️ Pitfall #2 — honestidad: zero-shot en PRECIOS pierde
La literatura es clara: TSFM aplicados directo (zero-shot) a precios dan
**R² negativo** y pierden contra buy-and-hold. DÓNDE SÍ ganan:
- **Forecast de volatilidad** (ej. |retorno|) — su punto fuerte, alta señal.
- **Correlación multi-activo** como UNA entrada de un grafo de señales, no la única.
- **Fine-tune** con tus datos (TimesFM-FT / LoRA) — ahí se vuelve rentable.
No lo vendas como oráculo de precios; úsalo como contexto/riesgo (sizing).

## Verificación
Correr un predict y comprobar shapes `(n_series, horizon)` y `(n_series, horizon, 9)`.
Modelo cacheado ~1.3GB en `~/.cache/huggingface/hub/models--google--timesfm-3.0-pytorch`.

## Referencias
- `references/market-forecast.md` — script de forecast SPY/QQQ/VIX verificado.
- Repo oficial: https://github.com/google-research/timesfm · Modelo: `google/timesfm-3.0-pytorch`
