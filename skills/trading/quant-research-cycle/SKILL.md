---
name: quant-research-cycle
description: "Ciclo hedge fund: idea, paper, backtest, veredicto."
metadata:
  source: Post Horizon (2026-08-20) + lecciones de QuantMuse-G
---

# Quant Research Cycle

El ciclo que los hedge funds usan (Renaissance, Jane Street, Man Group).
Post Horizon (2026-08): "El ciclo es el juego completo. Dejó de ser caro."

## 📚 CATÁLOGO DE ESTRATEGIAS (fuente de ideas verificadas)
> Espejo local: `C:/Users/<USER>/trading/master_catalog.csv` (315K, 134 estrategias, 56 campos).
> Catálogo maestro de estrategias de trading diráid-as desde código open-source (freqtrade, Lean,
> StockSharp, quantstrat, DRADIS, vnpy, ta4j...). **131/134 verificadas desde código ejecutable.**
> Campos: family, category, entry/exit/stop/TP/trailing/sizing normalizados, indicadores, backtest
> claims, bias/martingale risk, scores (completeness/clarity/reproducibility/portability).
> Uso: para la fase IDEA/PAPER, filtrar por categoría/familia y leer las reglas normalizadas + risks.
> No es recomendación: son ideas verificadas estructuralmente, SIN claim de rentabilidad (la mayoría
> no reporta backtest independiente).

## El ciclo (6 pasos)

```
IDEA → PAPER → CÓDIGO → BACKTEST → VEREDICTO → REVIEW
```

## 1. IDEA
Una hipótesis de trading. Escribirla en lenguaje natural:
- ¿Qué activo? ¿Qué señal? (momentum, carry, value, etc.)
- ¿Qué período? ¿Qué régimen esperamos?
- ¿Qué riesgo aceptamos? (max drawdown, Sharpe mínimo)

## 2. PAPER (evidencia académica)
Antes de codear, buscar si la idea ya se estudió:
- Buscar papers académicos (Moskowitz, Koijen, Asness, AQR, etc.)
- Extraer: Sharpe reportado, período, régimen, tamaño de muestra
- Si el paper muestra Sharpe 0.61 en 1974-2012, pero tu backtest será 2015-2026, **esperar degradación** (el post: "el carry murió en régimen de tasas cero")

## 3. CÓDIGO
Implementar la estrategia en QuantMuse-G:
- Crear o modificar estrategia en `data_service/strategies/builtin_strategies.py`
- Usar `BacktestEngine` (data_service/backtest/backtest_engine.py)
- Parámetros: entrada, salida, sizing, risk controls

## 4. BACKTEST
Correr contra datos históricos con:
- `PerformanceAnalyzer` (métricas estándar)
- **`RegimeAnalyzer`** (nuevo módulo) — análisis por régimen + veredicto honesto
- Ideal: benchmark (SPY) para exceso de retorno

### 4b. RESULTADO Denso (patrón quant-buddy / SKILL.state) — SOLO resumen, NO el dataframe entero
> Lección de `pseudo-longinus/quant-buddy-skills` + SKILL.state (2026-08-31): **el agente NO debe
> recibir la tabla completa de miles de filas**. Si metes el dataframe al LLM, quemas contexto y
> el modelo pierde el foco. Calcula TODO en el script y devuelve solo el resumen denso.

**Qué devolver al agente (no el df entero):**
```json
{
  "resultado": "SOBREVIVE | MUERE | REGIME-DEPENDENT | DATOS INSUFICIENTES",
  "metrics": {"sharpe": 0.62, "max_drawdown": 0.28, "cagr": 0.14, "win_rate": 0.58},
  "benchmark": {"spy_sharpe": 0.45, "exceso": 0.17},
  "regimenes": [{"regimen": "trending", "sharpe": 0.71}, {"regimen": "crisis", "sharpe": -0.12}],
  "top_resultados": 10,
  "chart": "<path al .png>",
  "veredicto": "..."
}
```
Reglas:
- **`resultado`** siempre del RegimeAnalyzer (honest_verdict).
- **Métricas agregadas**, no series. El chart se guarda a archivo y se referencia por path (para que el agente lo muestre, no lo reconstruya).
- **`regimenes`**: el breakdown por régimen es lo que evita el "Sharpe global 0.61 pero 0.11 en 2015-26" (data snooping).
- Si necesitas más detalle, el agente lee el archivo, NO re-ejecuta el df en el prompt.

## 5. VEREDICTO (el filtro — tira 97/100)
Criterios del post: "Un buen engine te decepciona más de lo que te emociona".

| Resultado | Acción |
|-----------|--------|
| ✅ SOBREVIVE | Sharpe > 0.5, drawdown < 30%, pasa en ≥50% regímenes → pasa a REVIEW |
| ❌ MUERE | Sharpe < 0.5, no pasa en la mayoría de regímenes → **DESCARTAR** |
| 🟡 REGIME-DEPENDENT | Sharpe global ok pero colapsa en crisis → marcar régimen, operar condicional |
| ⚪ DATOS INSUFICIENTES | Menos de 2 regímenes clasificados → extender backtest o datos |

**Regla de disciplina**: si el veredicto es MUERE, **no** se guarda la estrategia. No es "tal vez mejore". Es "siguiente idea".

## 6. REVIEW
Si SOBREVIVE:
- Documentar qué régimen funciona y cuál no
- Guardar en `workspace/ref/strategies/` con reporte del veredicto
- Si se despliega en vivo, monitorear régimen actual (no operar carry en tasas cero)

## Pitfalls
- ❌ Sharpe global de 0.61 que oculta que 2015-2026 da 0.11 (como el carry del post). Usar **siempre** RegimeAnalyzer.
- ❌ No comparar con benchmark. Una estrategia puede tener Sharpe 0.8 y aun así perder contra SPY.
- ❌ Ajustar parámetros hasta que el backtest funcione (data snooping). Si el veredicto es MUERE, **muere**.
- ❌ Backtest que no respeta orden de eventos (look-ahead bias). El engine de QuantMuse-G usa event-driven — verificar que no se use iloc/shift hacia atrás.

## Verificación
- [ ] Idea escrita en lenguaje natural
- [ ] Paper encontrado con Sharpe de referencia
- [ ] Código en builtin_strategies.py
- [ ] Backtest con PerformanceAnalyzer
- [ ] RegimeAnalyzer con honest_verdict
- [ ] Verdict NO es MUERE → guardar en ref/strategies/
- [ ] Verdict es MUERE → descartar sin nostalgia