---
category: trading
name: forecasting-foundation-models
description: "Use when forecasting multivariate series with covariates."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [forecasting, timesfm, time-series, orderflow, volume-profile, poc, trading]
    related_skills: [chronos-forecasting, quant-research-cycle]
---

# Forecasting Foundation Models + Order-Flow Profile

Modelos base de forecasting (TimesFM-3 de Google) y análisis de order-flow (POC/VAH/VAL/Delta)
en Python con datos reales de mercado. El upgrade natural a Chronos-2 cuando se necesita
**multivariado** (varias series juntas) o **covariables conocidas en el futuro** (earnings, Fed).

## Cuándo usar
- El usuario quiere predecir **varias series a la vez** o usar **eventos futuros conocidos**
  como entrada (calendario de earnings, decisiones Fed, promociones).
- El usuario quiere niveles de **order-flow** (POC, Área de Valor, Delta, Imbalance) para trading.
- Complementar el ciclo quant-research-cycle con un forecast forward o un perfil de volumen.

## ⚠️ MERCADO DE GIO (aprender ANTES de construir)
Gio opera **forex, cripto y Polymarket** — NO acciones de EE.UU. En 2026-09-01 se construyó una
plataforma completa con SPY/QQQ/VIX y él no entendía nada: "dime qué estamos viendo, yo estoy en
forex/polymarket/cripto". **Nunca** asumas el universo de activos. Pregunta o usa su mercado real:
- Cripto: `BTC-USD`, `ETH-USD`
- Oro (yfinance): **`GC=F`** (futuros) — **`XAUUSD=X` NO existe** (404 "Quote not found")
- Forex: `EURUSD=X`
- Para correlación/diversificación: BTC↔ETH ~+0.88 (casi el mismo trade), BTC↔Oro ~+0.12
  (verdadero diversificador), BTC↔EUR ~-0.08. Los `.section`/tarjetas deben llevar **tooltip
  explicativo** (qué hace cada sección) y botones largos (como /api/run, ~60s) deben dar **feedback
  visible** de progreso — ambos fueron pedidos explícitos tras confusión.

## Dos skills hermanas (NO confundir)
- `chronos-forecasting` (user-owned): forecasting **univariado en CPU** (28M params, sin GPU).
  Útil para series simples; NO maneja covariables ni multi-serie.
- `quant-research-cycle` (user-owned): el ciclo completo idea→paper→backtest→veredicto.
- Esta skill: forecasting **multivariado con covariables** + **perfil de volumen** en Python.

## Ver la referencia técnica
`references/timesfm3-setup.md` — instalación y API reales de TimesFM-3, con el pitfall
crítico (el paquete PyPI no trae la clase 3.0; hay que usar el repo de GitHub).
`references/trading-dashboard-server.md` — cómo exponer el pipeline como dashboard web en
vivo (servidor ejecutor `/api/run` + fetch), micro-animaciones UI, y el patrón de auditoría
completa antes de entregar (Node linter, casos límite, accesibilidad, visual QA con VLM local).
Incluye las **lecciones de UX del usuario** (correcciones explícitas 2026-09-01): NO reinventar
el layout — tomar patrones de plataformas externas probadas; jerarquía de info = hero del
mercado → interpretación → gráfico → métricas; globos de ayuda (tooltip propios) en cada sección
y botón; la plataforma se adapta al usuario y a sus datos, no al revés.
`references/audit-numeric-pipeline.md` — el patrón de AUDITORÍA de pipelines numéricos con
subagentes independientes: los 7 bugs reales que el análisis estático NO vio (doble conteo,
NaN en solve, n_obs colapsado, columna muerta, posición fantasma, entrada vacía, error sin
capturar) + las verificaciones de coherencia post-fix. Aplicar SIEMPRE después de construir
un pipeline de trading multi-módulo.

## TimesFM-3 — resumen operativo (detalle en references/timesfm3-setup.md)
- **PITFALL**: `pip install timesfm==3.0.0` desde PyPI NO trae la clase 3.0 (solo 2.5).
  Hay que `git clone https://github.com/google-research/timesfm.git` + `pip install -e .`
  desde el repo; la clase vive en `src/timesfm3/timesfm3_forecaster.py`.
- **Clase**: `TimesFM3Forecaster.from_pretrained("google/timesfm-3.0-pytorch", device="cuda")`
- **API**: `out = fc.predict(context, horizon, past_only_covariates, past_future_covariates, return_quantiles=True)`
  → `out.forecast` (punto/mediana) y `out.quantiles` (shape (k,horizon,9)).
- **Covariables**: `past_future_covariates` = señales futuras conocidas → el modelo anticipa el "bump".
- **En trading** (honestidad): zero-shot en **precios** pierde vs buy-and-hold; gana en
  **volatilidad** (|retorno|) y **correlación multi-activo**; el **fine-tune** es donde más sube.

## Order-Flow Profile en Python (módulo propio)
`scripts/orderflow_profile.py` — perfil de volumen con datos reales (yfinance), no estimación geométrica:
- **POC** = nivel de mayor volumen (zona de aceptación/equilibrio)
- **VAH/VAL** = límites del 70% del volumen → soporte/resistencia basados en volumen real
- **Delta** = volumen compra − venta (presión neta)
- **Imbalance** = (buy−sell)/(buy+sell) en [-1,1]
- A diferencia del indicador de TradingView (que estima buy/sell por posición del close),
  este usa OHLCV real y corre programático → se integra a un grafo de señales.

```python
from orderflow_profile import get_ohlcv, analyze
a = analyze(get_ohlcv("SPY", period="3mo", interval="1h"))
print(a.summary())  # POC, VAH, VAL, Delta, Imbalance, close, ubicación vs VA
```

## Pitfalls
- **TimesFM-3 ≠ paquete PyPI 3.0.0**: no pierdas tiempo instalando desde PyPI; usa el repo.
- **Zero-shot en precios NO predice**: usa TimesFM-3 para volatilidad/correlación, y el
  perfil de volumen para niveles. Combinados = contexto, no oráculo.
- **Order-flow del indicador TradingView** ("Volume Footprint" de ata_sabanci): su motor
  Geométrico gratis estima buy/sell por posición del close (heurística, no dato real);
  solo el motor "Footprint" nativo usa datos reales y requiere plan Premium. El módulo
  Python de esta skill usa OHLCV real y no necesita Premium.
- **Fallo de un ticker al descargar → KeyError** (bug real encontrado en auditoría 2026-09-01):
  construir `ctx` iterando sobre `TICKERS` fijos rompe si un símbolo no descarga. Fix: filtrar
  solo tickers usables (`len(daily[t]["Close"]) >= 32`), y en `build_signal` elegir ticker
  principal dinámico con `.get()` para los datos de perfil (ACTUALIZADO: usar `"BTC-USD"` si
  existe, si no `next(iter(forecast))` — NO hardcodear `"SPY"`, que no está en el universo de
  cripto/oro/forex de Gio). Nunca asumas que todos los tickers de la lista están disponibles.
- **Shapes inhomogéneos al alinear multi-serie** (bug real 2026-09-01): al construir la matriz
  `ctx` para forecast multivariado, `n = min(len(d["Close"]) for d in daily.values())` calculaba
  sobre TODOS los tickers (incluidos los que fallaron o con longitudes distintas) → `np.array`
  daba `ValueError: setting an array element with a sequence`. Fix: calcular `n` SOLO sobre los
  tickers **usables** y truncar cada serie a esa misma longitud: `n = min(len(daily[t]["Close"]) for t in usable)`.
  Verificar `ctx.ndim==2` y `ctx.shape[1]>=32` después. Validar con un set real de cripto/oro/forex
  (que tienen longitudes y símbolos muy distintos) antes de dar el forecast por bueno.
- **`</script>` dentro de template JS inline** (bug real 2026-09-01 al incrustar el widget de
  TradingView): si inyectas HTML con `</script>` literal dentro de un template literal en el
  `<script>` principal del HTML, el parser corta el script ahí → "Unexpected end of input".
  Fix: escapar como `<\\/script>`. Es el clásico de JS inline; el linter de Node (`new Function`)
  lo detecta.
- **`.startsWith` sobre un número → pantalla en blanco** (bug real 2026-09-01): al conectar el
  backtest real, `Net USD` llega como número (438.38) y el código de animación de stats llamaba
  `s.val.startsWith(...)` (solo funciona en string) → `TypeError` no capturado → toda la página
  en blanco. Fix: `const valStr = String(s.val)` antes de usar `.startsWith`. **Regla general**:
  cuando un valor puede venir como número O string desde un JSON, coerce a string antes de
  métodos de string, y NUNCA dejes que un `TypeError` de render rompa el `boot()` completo.
- **Selector de activo sin variable global** (bug real 2026-09-01): un hero del mercado que
  recalcula su ticker principal con `prim = F['BTC-USD']?'BTC-USD':...` en CADA render vuelve
  siempre al primer activo aunque el usuario eligió otro — el click "no cambia nada". Fix: una
  variable global `heroCurrent` que persiste la selección, y TODAS las funciones que muestran
  el activo (hero, IA, lectura de mercado, gráfico) la leen. Cambiar el activo = actualizar la
  variable + re-render de todas las vistas sincronizadas.
- **Backtest: equity curve duplica el PnL en cierre** (bug crítico real 2026-09-01, hallado por
  subagente de auditoría): `equity_curve.append(equity + pnl_usd)` añade el pnl DOS veces cuando
  el trade se cierra, porque `equity` ya lo sumó (`equity += pnl_usd`). Infla la curva y corrompe
  `sharpe` y `max_dd`. Fix: al CERRAR → `append(equity)` (ya incluye pnl); en mark-to-market
  (trade abierto) → `append(equity + pnl_usd)`. La señal de que esto pasó: `equity_final` no
  coincide con `10000 + net_usd` (diferencia = solo posición flotante abierta, debe ser pequeña).
- **`risk_parity_budget` produce NaN con covarianza degenerada** (bug real 2026-09-01): el solve
  divide `target / contrib`; con `contrib=0` → `0/0 = nan`. Fix: añadir ridge a la diagonal
  (`cov = cov + 1e-8*np.eye(n)`) y guardar `contrib <= 0` antes de dividir (peso 0 en vez de NaN).
- **`n_obs` del horizonte en vez del contexto diario colapsa la señal a ~0** (bug real crítico
  2026-09-01): `n_obs = len(forecast[t]["point"])` devuelve el HORIZONTE (ej. 5), no la longitud
  del contexto diario (>=32). En el grafo, `shrink = min(1, n_obs/250) = min(1, 5/250) = 0.02`
  → la señal del pipeline pesa ~0. Fix: propagar `context_len` (la `n` real del contexto diario)
  desde `timesfm_forecast` dentro de cada forecast y usarlo en `build_signal`. Verificar que
  `n_obs` sea ~decenas (contexto) y no 5 (horizonte).
- **`factor_row` con activo que no existe = columna muerta** (bug real 2026-09-01): si copiaste
  un pipeline de una plantilla con `factor_row = [pct_move, profile["QQQ"]["imb"], ovl]` pero tu
  universo real es `["BTC-USD","ETH-USD","GC=F","EURUSD=X"]`, `QQQ` nunca existe → esa columna de
  la regresión de neutralización es siempre 0 (desperdiciada). Fix: elegir el 2º activo REAL del
  portfolio dinámicamente, no hardcodear tickers de plantilla.
- **Targets/posiciones en un ticker que no existe** (bug real 2026-09-01): al integrar el pipeline
  al grafo, `targets = {"timesfm3_volprofile": {"SPY": ...}}` coloca posiciones en SPY que no está
  en el portfolio → `net_positions` devuelve posiciones fantasma. Fix: usar un activo real del
  portfolio (ej. `BTC-USD`).
- **`neutralize([])` crashea** (bug real 2026-09-01): `np.vstack([])` lanza `ValueError: need at
  least one array`. Fix: `if not signals: return np.array([])` ANTES del `vstack` (la guarda debe
  ir antes, no después — vstack crashea al momento).
- **RuntimeError de forecast sin capturar crashea el servidor** (bug real 2026-09-01): si ningún
  ticker tiene ≥32 puntos, `timesfm_forecast` levanta RuntimeError que no se capturaba en `main()`
  → el `subprocess` del servidor reporta exit≠0 y la UI no da feedback. Fix: capturar y escribir
  un JSON de error (`{"ok":false,"error":...}`) para que la UI muestre el problema en vez de un
  fallo silencioso.
- **Auditar el backtest/pipeline con un SUBAGENTE independiente** (patrón probado 2026-09-01):
  después de construir un pipeline con muchos módulos, delegar a un subagente (harness de agentes)
  una auditoría de calidad con instrucción explícita de "no inventar bugs, solo los verificables,
  compila y prueba casos límite". Encontró 7 bugs reales que el análisis estático no vio (doble
  PnL, NaN en risk parity, n_obs colapsado, columna muerta). El análisis estático (linter,
  sintaxis) NO alcanza para pipeline numérico — se necesitan pruebas de ejecución y una segunda
  vista.

## Verificación
- [ ] TimesFM-3 instalado desde el repo (no PyPI), `forecaster.device` en cuda
- [ ] `predict()` devuelve forecast y quantiles con shapes correctos (k,horizon,9)
- [ ] `orderflow_profile.py` imprime POC/VAH/VAL/Delta/Imbalance con datos yfinance reales
- [ ] En trading: vol/correlación como input, no señal única de precio
