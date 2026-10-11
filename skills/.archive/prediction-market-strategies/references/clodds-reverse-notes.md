# CloddsBot — Notas de ingeniería inversa (2026-08-27)

Fuente: `~/tools/clodds_ref` (clone read-only de github.com/alsk1992/CloddsBot, MIT, 740⭐, hackathon Colosseum 12 días).

## Veredicto (por qué NO correrlo con capital)
- Construido en 12 días para hackathon: mucho brillo, poca batalla; maneja SOL_PRIVATE_KEY + API keys con 119 skills lazy-loaded.
- Requiere ANTHROPIC_API_KEY (LLM decidiendo trades en vivo = no determinístico, costo recurrente).
- Sin track record auditable de rentabilidad de sus 118 "estrategias".
- Útil como MAPA de qué existe, no como vehículo. Nuestro bot se construye lean sobre Hermes.

## Arquitectura que sí vale (robada)
- **4 agentes separados**: Main / Trading (exec) / Research (data) / Alerts (monitor) — coincide con blast-radius del orquestador.
- **Trade Ledger** (`src/ledger/`): DecisionRecord con SHA-256 sobre campos ordenados (`hashDecision`), verificación contra tampering. Portado a `poly_core.py` (TradeLedger).
- **Whale tracker** (`src/feeds/polymarket/whale-tracker.ts`): CLOB WS para order flow + REST para posiciones + subgraph histórico. Copiar en fase Observatorio.
- **RTDS** (`src/feeds/polymarket/rtds.ts`): WebSocket oficial de Polymarket — topics `crypto_prices`, `crypto_prices_chainlink`, `comments`. Docs: docs.polymarket.com/developers/RTDS.

## Detalles de ejecución extraídos
- OrderMode: maker (GTC postOnly, 0 fee, se rechaza si cruza) / taker / fok / maker_then_taker (escalate tras makerTimeoutMs, buffer taker 1c).
- Fee taker: `fee_per_share = 0.125 * (price*(1-price))^2`.
- Config de ronda: roundDurationSec, minTimeLeftSec, minRoundAgeSec=120, forceExitSec, warmup tras start.
- Divergence detector: rolling buffer con búsqueda binaria temporal (`priceAt(secsAgo)`), ventanas 5s-120s, tags tipo "BTC_DOWN_s12-14_w15".
