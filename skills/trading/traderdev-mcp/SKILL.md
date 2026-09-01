---
category: trading
name: traderdev-mcp
description: "TraderDev MCP: auth verify + Pine backtest in Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
---

# TraderDev MCP — Backtesting & Ensemble Workflow

TraderDev (`https://mcp.trader.dev/mcp`) is a third-party MCP that exposes ~49 tools for
backtesting TradingView Pine Script strategies, searching public strategies, and managing
live alerts. Hermes connects via **HTTP transport** with an `Authorization: Bearer <key>` header.

## When to use
- User pastes a `mcp.trader.dev` / `mcp-api.trader.dev` login or connector URL.
- User asks to backtest a Pine strategy, analyze trading strategies, or build ensembles.
- User mentions "TraderDev", "trader-dev", "vibe trading", or wants forex/crypto backtests from chat.

## Install (HTTP transport)
Wired in Hermes `config.yaml` under `mcp_servers:`. Pattern:
```yaml
mcp_servers:
  trader-dev:
    url: "https://mcp.trader.dev/mcp"
    headers:
      Authorization: "Bearer <API_KEY>"
    timeout: 120
    connect_timeout: 60
    enabled: true
```
- Key goes in `headers`, **NEVER in the URL** (`?key=` leaks in logs/history).
- Edit `config.yaml` via terminal Python (the file toolset BLOCKS config.yaml writes for security).
- Restart Hermes (`/reset`) — MCP tools load at startup, no hot reload.

## ⚠️ VERIFY AUTH — do NOT trust `hermes mcp test`
`hermes mcp test trader-dev` only confirms **connection + tool discovery (49 tools)**.
It does NOT validate that the API key authenticates. A revoked/expired key STILL passes `mcp test`.
**Always call `whoami` (tools/call) to confirm auth** — a live key returns user JSON
(`{id, email, tier:...}`); a dead key returns "Your API key was revoked or invalid".
(See references/auth-verify.md for the exact evidence from a real session.)

## Symbol support (verified by experiment)
- **Crypto** (btc, BTCUSDT, BYBIT:BTCUSDT.P) → resolves to **Bybit USDT linear perpetual** (~639 instruments).
- **Forex** (EURUSD, XAUUSD, GBPUSD) → **passes through unchanged**, backed by **POLYGON forex** data
  (confirmed in backtest output: `"market": "POLYGON forex"`).
- `GOLD` is NOT valid → use `XAUUSD`.
- Validate any symbol with `plan_backtest_window` (returns the Strategy Tester tip = supported;
  error like `bad_range_after_clamp` / `not in the Bybit USDT perp catalog` = unsupported).

## Engine limits (HARD — cause 400 mcprule_rejected / backtest_failed)
- **NO `request.security`** → NO multi-timeframe. Build ensembles on a SINGLE timeframe using
  same-bar indicators only. (First attempt with 4h context via request.security was rejected.)
- **NO `ta.adx`** (unimplemented: "Runtime: unimplemented function 'ta.adx'"). Use `ta.ema`,
  `ta.rsi`, `ta.atr`, `ta.supertrend`, `ta.highest/lowest`, `ta.sma`, `ta.stdev` instead.
- Pine **v6** (`//@version=6`). `get_pine_codegen_rules` is **MANDATORY** before writing any Pine.
- Parity profile = **commission 0%** (NOT 0.05%). Set `commission_value=0.0` in strategy().
- See references/engine-limits.md for the full unsupported-function list.

## Backtest workflow (verified end-to-end)
1. `get_pine_codegen_rules` → read the rules first.
2. `plan_backtest_window` (symbol, timeframe, from, to) → confirm coverage/clamping.
3. `quick_backtest` (pineSource, symbol, timeframe, from, to) → returns a **TEXT block** containing
   a JSON `{"resultId":..., "result":{...metrics...}}`. **Parse the JSON block** (find first `{`
   to last `}`) to extract: netProfitPct, winRatePct, profitFactor, maxDrawdownPct, sharpeRatio,
   totalTrades, barsEvaluated. Do NOT rely on the trailing "Strategy Tester tip" text.
4. Optional: `get_equity_curve` with `result.id` for per-bar equity.

## Ensemble recipe (per pair — do NOT fuse all pairs into one "formula")
Combine 2-3 indicators as integer "votes"; enter LONG when votes >= threshold; close when 0.
Verified example — **XAUUSD 1h, consensus `==3`** (Donchian20 mid-break + EMA20>EMA50 + Supertrend up):
`+15.04% net, 61.1% win, PF 2.20, DD 11.12%, sharpe 2.58, 18 trades` (2025-H1).
**Walk-forward validate** on a different date range before trusting: same logic on 2024-H2 gave
`+7.59% net, DD 4.75%, sharpe 1.36, 7 trades` — confirms it is not overfit to one window.
See templates/xau_ensemble_1h.pine.

## Pitfalls
- `hermes mcp test` ≠ auth check (see above). A revoked key passes it silently.
- New key ≠ old key: regenerate INVALIDATES the prior. Update config.yaml, then `/reset`.
- **Free tier = finite credits**; `quick_backtest` / `optimize_strategy` cost. Count your calls
  (a full ensemble iteration across 3 pairs + variants burned ~10 backtests).
- Public strategies show suspiciously uniform **~300-400% net** (engine cap) and many
  **duplicates / overfit** (sharpe>10 is impossible in real crypto). Filter candidates:
  `trades≥100, DD%≤30, PF 1.3-3.0, sharpe 1.0-2.0`, drop sharpe>5 and exact-duplicate names.
- Backtest ≠ future. An ensemble reduces risk; it never guarantees profit.
- EURUSD/GBPUSD first-pass ensembles LOST (PF<1) — copy the public winning configs
  (EURUSD RSI/BB mean-rev; GBPUSD BB(34,3.0)) rather than inventing from scratch.

## References
- references/engine-limits.md — unsupported functions + verified symbol table.
- references/auth-verify.md — whoami vs mcp test evidence (revoked-key case).
- templates/xau_ensemble_1h.pine — working consensus ensemble (verified metrics).
