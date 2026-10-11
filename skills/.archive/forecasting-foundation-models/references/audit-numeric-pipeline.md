# Auditoría de pipelines numéricos (trading) con subagentes

Patrón probado 2026-09-01: construir un pipeline de trading de muchos módulos
(TimesFM forecast + perfil de volumen + backtest + grafo + servidor web) y luego
**delegar a un subagente independiente** una auditoría de calidad. Encontró **7 bugs
reales** que el análisis estático (linter de sintaxis, `py_compile`, `new Function`)
NO detectó. Este archivo documenta por qué y cómo.

## Por qué el análisis estático no alcanza
- Los linters validan **sintaxis**, no **lógica numérica**. Un pipeline puede compilar
  perfecto y producir NaN, doble conteo, o una señal colapsada a ~0.
- Los bugs de este tipo solo aparecen con **ejecución real**: covarianza degenerada,
  serie con rango cero, ticker que falla al descargar, lista vacía.
- Una segunda vista (subagente) ve lo que el autor pasó por alto por estar "en el bosque".

## Cómo delegar (prompt efectivo)
- Instrucción explícita: **"no inventes bugs, solo reporta los verificables: compila y
  prueba casos límite con ejecución real"** — evita reportes de sospechas sin prueba.
- Dar rutas absolutas (C:/ no /c/ en Windows), el python del venv correcto, y el universo
  de activos reales (BTC-USD, ETH-USD, GC=F, EURUSD=X).
- Pedir formato: `BUG: [archivo:linea] descripción -> corrección`.
- Pedir verificación de casos límite (serie vacía, constantes, NaN, cov degenerada,
  lista vacía, ticker ausente).

## Los 7 bugs que atraparon (clases recurrentes de pipeline numérico)
1. **Doble conteo** — equity curve sumaba pnl dos veces al cerrar trade (equity ya lo tenía).
2. **NaN en solve** — risk parity dividía por contrib=0 (cov degenerada) → NaN.
3. **Escala mal propagada** — `n_obs` usaba el horizonte (5) no el contexto diario (≥32)
   → colapsaba la señal a ~0 en el shrinkage del grafo. **El más insidioso**: no truena,
   solo hace la señal irrelevante.
4. **Columna muerta** — factor_row con ticker que no existe (QQQ fuera del universo) → siempre 0.
5. **Posición fantasma** — targets en activo fuera del portfolio (SPY).
6. **Crash con entrada vacía** — `np.vstack([])` (la guarda debe ir ANTES del vstack).
7. **Error sin capturar** — RuntimeError de forecast crasheaba el subprocess del servidor.

## Verificación de coherencia post-fix (clave)
- **Backtest**: `equity_final` debe ≈ `10000 + net_usd`; la única diferencia legítima es la
  posición flotante abierta al final (mark-to-market), debe ser pequeña.
- **n_obs**: debe ser ~decenas (contexto diario) no 5 (horizonte). Un valor de horizonte = señal muerta.
- **NaN**: `risk_parity_budget(np.zeros((2,2)))` debe dar pesos finitos, no `[nan nan]`.
- **Entrada vacía**: `neutralize([])` debe devolver array vacío, no ValueError.

## Script de prueba temporal
El subagente usó `C:/Users/<USER>/AppData/Local/Temp/audit_test.py` para las pruebas de
casos límite; lo borró al terminar (solo reporte en el summary). Reutilizable si se recrea.
