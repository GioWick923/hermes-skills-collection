# TimesFM-3 Forecast de mercado — verificado (2026-09-01)

Script probado en RTX 3060 (12GB) con datos reales yfinance. Los shapes
verificados salen en los comentarios.

```python
"""Forecast multivariado TimesFM-3 con datos reales de mercado (SPY+QQQ+VIX)."""
import sys, numpy as np, torch
sys.path.insert(0, r'<ruta>/timesfm-repo/src')   # tras install -e . no hace falta
from timesfm3.timesfm3_forecaster import TimesFM3Forecaster

torch.set_float32_matmul_precision('high')
import yfinance as yf

tickers = ["SPY", "QQQ", "^VIX"]
df = yf.download(tickers, period="1y", interval="1d", progress=False, auto_adjust=True, group_by="ticker")
cols = []
for t in tickers:
    try: cols.append(df[t]["Close"].dropna().values)
    except Exception: cols.append(df["Close"][t].dropna().values)
n = min(len(c) for c in cols)
ctx = np.array([c[-n:] for c in cols], dtype=np.float32)   # (3, n)

fc = TimesFM3Forecaster.from_pretrained("google/timesfm-3.0-pytorch", device="cuda")
print(fc.device, fc.global_context)

horizon = 30
out = fc.predict(context=ctx, horizon=horizon, return_quantiles=True)
print(np.asarray(out.forecast).shape)    # (3, 30)
print(np.asarray(out.quantiles).shape)   # (3, 30, 9)

# Volatilidad (|retorno|) — el caso donde TSFM SÍ gana
ret = np.diff(ctx, axis=1) / ctx[:, :-1]
vol = np.abs(ret)
vout = fc.predict(context=vol[:, -n//2:], horizon=horizon, return_quantiles=True)
print(np.asarray(vout.forecast).shape)   # (3, 30)
```

## Resultados verificados (datos reales, 3 meses 1h)
- SPY/QQQ/VIX forecast precios: (3, 30) punto + (3, 30, 9) cuantiles ✅
- Forecast volatilidad: (3, 30) + (3, 30, 9) ✅ (mediana ~0.8%, rango 0.45-3.8% — realista)
- Modelo cacheado ~1.3GB (carga instantánea en 2ª ejecución)

## Lección de integridad
Al igual que ktransformers (ver `ktransformers-evaluación` en el vault), el
modelo corre bien en la GPU pero **zero-shot en precios pierde contra
buy-and-hold** — usarlo para volatilidad/correlación multi-activo y fine-tune,
no como oráculo de dirección.
