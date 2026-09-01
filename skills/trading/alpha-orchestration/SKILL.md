---
name: alpha-orchestration
description: Combine trading strategies via a 5-node signal graph.
---

# Alpha Orchestration Layer (grafo de 5 nodos)

Fuente: "Graph Engineering to Build an Alpha Orchestration Layer" (Ruuj, ago-2026). Bitácora completa en vault `Memorias/Agente/` (busca "Bitacora alpha-orchestration").

## El problema
N estrategias buenas individualmente pierden dinero juntas si nada decide cómo se combinan. Momentum y mean-reversion correctos pueden anularse y quemar spread sin que nadie lo vea.

## Los 5 nodos (el ORDEN importa)

1. **Nodos de señal** — cada estrategia emite `{score, confidence, n_obs}`, NUNCA dirección sola.
   - Shrinkage: `score * confidence * min(1, n_obs/min_obs)` (min_obs≈250). Estrategia joven = menos voz hasta ganarse track record.
2. **Neutralización de factores** — `lstsq(factor_exposures, señal)` → usar residuo. Dos señales con corr 0.6 pueden ser EL MISMO trade (tilt común no intencional). Sin esto pagas la apuesta dos veces.
3. **Presupuesto de riesgo** — risk parity (aporte igual al riesgo total), NO dólares iguales.
4. **Optimizador** — restricciones DENTRO del solve (feasible set), no proponer→vetar. Lo que viola límites jamás se propone.
5. **Netting** — netear posiciones opuestas entre estrategias antes de ejecutar (si no: spread pagado doble, "netting risk").

## La capa invisible: SharedState con snapshot isolation
- Al inicio de cada ciclo: congelar UNA foto del estado; todos los nodos leen SOLO de la foto.
- Escrituras caen inmediato para el SIGUIENTE ciclo.
- Riesgo sin esto: dos nodos leen cov v41 vs v42 → portafolio nunca coherente en ningún instante, sin error. Problema de sistemas distribuidos, no de finanzas.

## Mapeo al stack de Gio
- **MACD v2.5 ES** (TradingView) = candidato a primer nodo de señal → envolver salida con score+confidence+n_obs.
- **MT5 / Oanda** = capa de datos y ejecución (nodo 5 se materializa ahí).
- **Scaffold runnable:** `C:\Users\<USER>\trading\orchestration\alpha_orchestrator.py` (numpy only).
- Escalar a optimizador real (cvxpy/scipy) SOLO cuando haya ≥3 señales vivas — YAGNI.

## Pitfalls
- Pasar solo dirección ("buy") aguas abajo = imposible ponderar con inteligencia.
- Dólares iguales ≠ riesgo igual: el más volátil se lleva el riesgo sin decisión consciente.
- Verificar señal neutralizada antes de asumir diversificación: la correlación baja de entrada no garantiza trades distintos.
