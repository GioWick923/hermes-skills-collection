---
category: mlops
name: chronos-forecasting
description: "Forecasting de series temporales con Chronos-2 Small (Amazon, 28M params, 100% local en CPU). Predice valores futuros de series numéricas con bandas de probabilidad. Usa cuando una tarea del usuario requiera predecir tendencias numéricas: precios, volumen, métricas de uso, costos, demanda, señales de trading, consumo, o cualquier serie de números en el tiempo. NO es para predicción de comportamiento humano ni de texto."
version: 1.0.0
author: Hermes Agent (Chronos-2 de Amazon Science / Hugging Face)
license: Apache-2.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [forecasting, time-series, chronos, prediction, probabilistic, trading, metrics]
    related_skills: [quant-research-cycle, local-gguf-deployment, model-router]
---

# Chronos Forecasting

Herramienta de **forecasting probabilístico de series temporales** (Chronos-2 Small, 28M params,
de Amazon Science). Corre **100% local en CPU** — no gasta tokens, no requiere GPU, no sube datos a la nube.

## Cuándo usar (disparadores para el agente)
- El usuario pide predecir/proyectar/estimar valores futuros de una serie numérica
- Predecir **precios/volumen** (trading), **métricas de uso** (VRAM, tokens, costos), **demanda**, **consumo**, **tendencias de datos**
- Complementar un backtest con forecast forward, o anticipar un pico de recurso
- Cualquier "¿cómo seguirá esta serie de números?"

## Cuándo NO usar
- ❌ Predecir comportamiento humano, reacciones, o "qué querrá el usuario" (eso es perfilado, no forecasting)
- ❌ Series sin datos numéricos previos (necesita historia para predecir)
- ❌ Clasificación / texto / generación — NO es un LLM de propósito general, es solo forecasting

## Uso (comando global `chronos`)
```bash
# Pronóstico por defecto (12 pasos, quantiles 0.1/0.5/0.9, serie de ejemplo)
chronos

# Pronóstico de una serie concreta
chronos --series "[100,105,102,110,115,112,120]" --prediction-length 5

# Con quantiles personalizados
chronos --series "[...]" --quantiles 0.1,0.5,0.9

# Modelo alternativo (default autogluon/chronos-2-small 28M)
chronos --model "amazon/chronos-2"   # 0.1B, más preciso, algo más lento
```

Salida JSON: `{model, series_length, prediction_length, quantiles, last_actual, forecast:[{timestamp, q0.1, q0.5, q0.9}, ...]}`
- **q0.5** = mediana (mejor estimación)
- **q0.1/q0.9** = banda de 80% de incertidumbre

## Detalles técnicos
- Venv: `~/tools/chronos/venv` (CPU, `uv`). Script: `~/tools/chronos/chronos_forecast.py`
- Modelo: `autogluon/chronos-2-small` (28M, cache en `~/.cache/huggingface`). Ya descargado y verificado.
- Torch CPU 2.13.0. Forecast de 12 pasos en ~segundos.

## Pitfalls (aprendidos en la integración 2026-09-01)
- **API Chronos-2**: usar `predict_df` (con DataFrame) para obtener quantiles; `predict()` plano requiere `inputs` posicional y devuelve muestras crudas.
- **Columna de quantile = string**: acceder `row[str(ql)]`, no `row[ql]` (KeyError 0.1).
- **Frecuencia `ME`**: pandas moderno rechaza `M` → usar `ME`.
- **Modelo small vs base**: el tweet dice "Chronos-2 Small" = `autogluon/chronos-2-small` (28M). `amazon/chronos-2` es 0.1B.
- Windows: sin symlinks en HF cache (aviso inofensivo); corre con python.exe del venv.

## Integración con el flujo del agente
Cuando el usuario pida pronósticos de series numéricas:
1. Recolectar la serie histórica (datos, CSV, salida de backtest, métricas)
2. Llamar `chronos --series "[...]" --prediction-length N`
3. Interpretar el resultado (q0.5 + banda de incertidumbre) y presentarlo al usuario
4. Para trading: alimentar el forecast al análisis (quant-research-cycle) como input forward

## Verificación
- [ ] `chronos --series "[100,105,102,110,115,112,120]" --prediction-length 3` devuelve JSON con forecast (probado real ✅)
- [ ] El resultado se puede parsear (JSON válido)
- [ ] Los quantiles q0.1 < q0.5 < q0.9 en cada paso

## Fuente
- Modelo: https://huggingface.co/autogluon/chronos-2-small (Apache-2.0, Amazon Science)
- Paper: "Chronos-2: From Univariate to Universal Forecasting" (arXiv:2510.15821)
- Package: `chronos-forecasting>=2.0`
