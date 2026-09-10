---
category: trading
name: orderflow-volume-profile
description: "Build volume profile analysis (POC, VAH/VAL) in Python."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [orderflow, volume-profile, footprint, poc, value-area, delta, imbalance, trading, pinescript]
    related_skills: [pine-script-indicators, timesfm-forecasting, alpha-orchestration, quant-research-cycle]
---

# Order-Flow / Volume Profile en Python

Analiza dónde se negoció el volumen por niveles de precio (POC, Área de Valor,
Delta, Imbalance diagonal, OVL, Balance tilt) **programáticamente con datos
reales** (yfinance), no solo visual en TradingView. Porta la lógica de
indicadores Pine de order-flow (ej. VFP-Intro de ata_sabanci) a un módulo
Python operativo que se integra con una estrategia.

## Cuándo usar
- El usuario quiere niveles de soporte/resistencia **basados en volumen** (POC, VAH/VAL).
- Necesitas presión compra/venta neta (delta) o desequilibrios (imbalance) sobre datos reales.
- Quieres portar/adaptar un indicador Pine de order-flow a Python reutilizable.

## Conceptos (explicación de alto nivel)
- **Perfil de volumen**: reparte el volumen de cada vela entre "filas" de precio.
  La fila con más volumen = **POC** (precio de control, el "lugar más concurrido").
- **VAH/VAL (Área de Valor)**: límites que contienen el 70% del volumen, expandiendo
  desde el POC. → soporte/resistencia basados en volumen real.
- **Delta**: compra − venta neta. **Imbalance**: desequilibrio relativo (−1 a 1).
- **OVL** (overlapping coefficient): cuánto compra/venta comparten precios, 0-1.
  ~1 = mercado balanceado/rotativo; →0 = direccional (cada lado en su territorio).
- **Balance tilt**: % de desequilibrio del volumen total, con umbral de neutralidad.

## Métricas portadas del Pine (definiciones exactas)
1. **Imbalance DIAGONAL (300% clásico)**: el desequilibrio se lee cruzando la
   frontera entre niveles vecinos. Nivel k tiene imbalance de compra si
   `buy[k] > sell[k-1] * ratio` (ratio = pct/100, pct=300 → 3x). De venta si
   `sell[k] > buy[k+1] * ratio`. La diagonal importa porque los traders leen
   la absorción en el límite entre dos precios.
2. **OVL** = `sum(min(norm_buy_k, norm_sell_k))` sobre niveles (norm = /total del lado).
3. **Balance tilt** = `100*(buy−sell)/(buy+sell)`; neutral si |tilt| < umbral (5% default)
   → no "vestir un volado como dirección".

## ⚠️ Honestidad (del análisis del Pine VFP-Intro)
- Motor **Geometric** del indicador original = "order flow fake": buy/sell sale de la
  FORMA de la vela (posición del close en el rango), no de transacciones reales. Educativo, no operativo.
- El valor operativo está en **Intrabar** (velas TF inferior reales) o **Footprint nativo** (Premium).
- En Python usamos **OHLCV real** (yfinance) con split direccional (close>=open → buy), que
  es un modelo honesto sobre datos reales.

## ⚠️ Robustez (bugs reales encontrados en auditoría 2026-09-01)
Un perfil de volumen ingenuo truena con datos límite. Corregido y verificado — aplicar SIEMPRE:
- **Serie de precio constante (rango = 0)**: `pmax - pmin = 0` → `n = 0` filas → `price_rows` vacío
  → `np.argmax` lanza `IndexError`. Fix: si `pmax <= pmin`, expandir `pmin/pmax ± 1`; y
  `n = max(int(ceil((pmax-pmin)/spread)), 1)`.
- **DataFrame vacío**: `lo.min()` lanza `ValueError`. Fix: guarda temprana
  `if df.empty or len(hi)==0 or isnan(lo).all(): return perfil vacío (1 fila, todo 0)`.
- **Una sola fila / volumen cero**: mismo `IndexError` del caso constante. Cubierto por las guardas.
- **NaN en OHLCV**: filtrar filas no finitas ANTES de construir filas de precio.
- **`analyze()` sobre df vacío**: `df["Close"].iloc[-1]` lanza IndexError. Fix: guarda que
  devuelve `ProfileAnalysis` neutral (close=0, location="sin datos") antes de leer el close.
El patrón de guardas (empty → NaN → rango cero → n>=1) es el orden correcto y probado.

## Verificación
Correr `scripts/orderflow_profile.py` — imprime POC/VAH/VAL/Delta/OVL/Balance/IMB
para SPY y BTC-USD. Comprobar que los valores son plausibles (ej. SPY POC ~744,
OVL ~0.90, Balance sell ~-6.7%).
**Test de robustez**: probar serie constante, 1 fila, df vacío y con NaN — los 4 deben
devolver un perfil sin excepción (6/6 casos límite OK en la auditoría).

## Referencias
- `scripts/orderflow_profile.py` — módulo completo y autoejecutable (demo incluida).
- Análisis del Pine VFP-Intro: vault `20-Proyectos/VFP-Intro-Analisis.md`.
- Skill hermana `pine-script-indicators` (verificación/port de Pine); `timesfm-forecasting`
  para forecast (volatilidad/sizing) que complementa los niveles del perfil.
