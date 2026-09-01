---
name: prediction-market-strategies
description: Build Polymarket bots; strategies, fees, audit ledger.
version: 1.0.0
author: Hermes Agent (curator)
license: MIT
tags: [polymarket, predictmarkets, trading, bots]
related_skills: [alpha-orchestration, polymarket]
---

# Prediction-Market Strategies (Polymarket bots)

## When to Use
- Building or extending trading bots for Polymarket / prediction markets (Gio's PredictMarkets section)
- Sizing orders against taker fees, or auditing bot decisions
- User mentions crypto rounds, BTC 15-min markets, paper-trading, or edge detection

## Estado del proyecto de Gio
- Hub vault: `20-Proyectos/PredictMarkets/00-README-PredictMarkets.md`
- Core runnable: `C:\Users\<USER>\trading\predictmarkets\poly_core.py` (4 estrategias + ledger, self-tests PASS)
- Repo de referencia (read-only): `~/tools/clodds_ref` (CloddsBot, ingeniería inversa 2026-08-27)
- Roadmap: Observatorio → Edge detection → Backtest → Ejecución (wallet EIP-712 solo al final)
- Regla de oro: NADA de capital real sin backtest + aprobación manual de Gio.

## Las 4 estrategias (umbrales reales del source de CloddsBot)
1. **Momentum** — spot se movió ≥0.4% (con scaling `0.50+move/100*5`, lag ≥2c requiere ≥0.4%, NO 0.15% como sugiere el default), poly atrasado ≥2c → maker_then_taker.
2. **Mean Reversion** — token ≤0.30 o ≥0.72, spot calmo (<0.08%), ronda >120s, OBI ≥ -0.1 (no pelear contra el flujo) → maker.
3. **Penny Clip** — ≥3 rebotes en 30s (step ≥1c), rango ≥3c, compra ≥1c bajo media con spot confirmando → maker (el edge ES postear en el spread, 0 fee).
4. **Expiry Fade** — 1-5 min para expirar, skew ≥15c del mid, spot plano (<0.06%) → taker (velocidad).

## Pitfalls
- Fee taker Polymarket: `0.125*(p*(1-p))^2` por share — máximo en p=0.50; estrategias maker lo evitan.
- Momentum con movimientos <0.4% nunca dispara con el scaling default — backtest honesto vs mentiroso depende de esto.
- Fee de ronda: primer y último minuto tienen spreads inestables (min_round_age=120s, force_exit antes de expiry).
- No pelear contra order flow: OBI negativo = no fade.

## Pitfall de implementación detectado en testing
- Un test del port atrapó que el lag de momentum escala con `move/100*5` — usar valores del dominio real en tests, no inventados (0.25% spot no genera lag de 2c).

## Referencias
- `references/clodds-reverse-notes.md` — notas de la ingeniería inversa (arquitectura Clodds, feeds RTDS, whale tracker, ledger hash).
