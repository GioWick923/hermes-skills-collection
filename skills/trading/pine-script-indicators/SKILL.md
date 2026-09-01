---
category: trading
name: pine-script-indicators
description: "Use when working with TradingView Pine Script indicators."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tradingview, pine-script, indicator, pinescript, verification, trading]
    related_skills: [quant-research-cycle, hermes-model-config]
---

# Pine Script Indicators (TradingView)

Análisis, corrección, traducción y verificación de indicadores Pine Script v4/v5
**sin compilador local**. Patrones extraídos de producción (MACD v2.4 → v2.5,
2026-08-27): el bug #1 de Pine, la trampa de traducción de `input.string`, y el
verificador estructural que sustituye al compilador que no existe.

## Cuándo usar
- El usuario envía un indicador `.pine`/`.txt` de TradingView y pide análisis, fix,
  traducción o adaptación (forex, MTF, divergencias, etc.).
- Antes de declarar que un indicador "funciona" o está "verificado" (sin haberlo
  compilado en TradingView).

## Pitfalls críticos

1. **`var` dentro de función = estado GLOBAL compartido** (bug #1 de Pine):
   ```pine
   f_ema(src, length) =>
       var float ema = na
       ema := na(ema) ? src : alpha * src + (1 - alpha) * ema[1]
   ```
   TODAS las llamadas comparten la misma variable → `f_ema(src, 12)` y
   `f_ema(src, 26)` se corrompen entre sí, y peor dentro de `request.security`
   (4 timeframes distintos compiten por el mismo estado). El MACD sale mal aunque
   la lógica parezca correcta.
   **Fix: usar built-ins `ta.ema(src, length)` / `ta.sma(src, length)`** (wrappers
   de una línea; `f_sma` con loop `for` sin `var` es correcto).

2. **Traducir labels de `input.string` rompe las comparaciones** — en Pine el valor
   de la opción ES el string visible. Si cambias "Otomatik (Adaptif)" → "Automático
   (Adaptativo)", TODAS las `== "Otomatik (Adaptif)"` del código dejan de matchear.
   Traducir opciones = traducir cada comparación a la vez. Verificar con el script.

3. **No existe compilador Pine local** — la verificación estructural
   (`scripts/verify_pine.py`: tokens residuales, opciones vs comparaciones, balance
   de paréntesis) es lo máximo que podemos hacer; la prueba final es que el usuario
   pegue el código en TradingView (Pine Editor → Guardar → 0 errores). Decirlo
   explícito, no marcar "validado" sin esa prueba.

4. **Divergencias con pivots repintan** (normal en este tipo de indicadores): las
   líneas y condiciones aparecen al confirmarse el pivot, con `lookbackRight` velas
   de retraso. Declararlo siempre; no es un bug pero el usuario debe saberlo para
   no operar ciego.

5. **`request.security` + lookahead**: para TF mayores, `barmerge.lookahead_on`
   cuando `timeframe.in_seconds(tf) > timeframe.in_seconds()` es la convención
   estándar (evita el retraso de la alineación). No "arreglarlo" sin motivo.

## Flujo recomendado
1. Leer el archivo completo; mapear componentes (motor, filtros, MTF, screener, alertas).
2. Detectar y corregir bugs ANTES de traducir (el fix toca código, la traducción solo strings).
3. Fixes con impacto mínimo: resolver la causa (regla estándar senior), no el síntoma.
4. Traducir strings de UI manteniendo opciones y comparaciones sincronizadas.
5. `python scripts/verify_pine.py <archivo> [--residual "Turco1 Turco2"]`.
6. Guardar junto al proyecto (ej. `trading/`) y persistir la decisión en el vault
   (nota canónica con bugs detectados + estado de la versión).
7. Entregar: ruta + MEDIA del archivo + pasos para compilar en TradingView + nota
   honesta de que la compilación final es del usuario.

## Verificación
```bash
python scripts/verify_pine.py MACD_v2.5_Ultimate_Edition_ES.pine --residual "Otomatik Kurumsal Sadece"
```

## Referencias
- `scripts/verify_pine.py` — verificador estructural reutilizable (residual, opciones, paréntesis).
- Proyecto real: `C:\Users\<USER>\trading\MACD_v2.5_Ultimate_Edition_ES.pine` + nota
  `20-Proyectos/MACD-v2.4-Ultimate-Indicador.md` en el vault.
