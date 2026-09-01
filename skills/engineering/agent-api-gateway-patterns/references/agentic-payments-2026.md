# Agentic Payments — Mapa del ecosistema (2026)

Investigación de 2026-08-20. Fuentes: Zuplo learning-center, blog de Alephant, Stellagent (Cloudflare), SatGate, SettleGrid State of MCP 2026.

## El problema que resuelven
- Los agentes no se registran con formularios ni leen pricing pages. Descubren APIs vía manifests/tool catalogs y deciden en milisegundos.
- El billing mensual post-hoc no funciona: un agente puede acumular una factura de 4 cifras en una tarde.
- La monetización debe vivir EN el protocolo (machine-readable), no en docs.

## Protocolos (fragmentados, marzo 2026: 10+ estándares)

| Protocolo | Backing | Estado |
|---|---|---|
| x402 | Coinbase | ~$28K/día (mitad gamificado según CoinDesk); adoptado por Cloudflare |
| Stripe MPP | Stripe + Tempo | Lanzado 18-mar-2026, 100+ servicios; "OAuth para dinero" (sessions con spending limit, micropagos streaming) |
| OpenAI ACP | OpenAI + Stripe | In-chat checkout sunset 24-mar; pivot a discovery-first |
| L402 | Lightning + macaroon | Token lleva budget caveat incrustado, sin billing central |
| Visa TAP | Visa | Pilot, enterprise |
| Mastercard Verifiable Intent / Agent Pay | Mastercard | Primer pago agente EU, mar-2026 |
| Google UCP / AP2 | Google + Shopify/Etsy/Target/Walmart | Commerce lifecycle para agentes |
| Circle Nanopayments | Circle | USDC, micropagos sub-cent |

- HTTP 402 = señal común (payment required → el agente puede elegir herramienta más barata, no reintenta como con 429).
- Convergencia esperada: gateways protocol-agnostic ganan.

## Datos de mercado (SettleGrid, mar-2026)
- 12,770+ MCP servers; 97M+ SDK downloads.
- <5% de MCP servers monetizan.
- Volumen global agent-to-tool: <$50K/día (x402 ~$28K, mitad artificial).
- Proyección agentic commerce: $385B por 2030.
- Benchmarks: Apify top devs ~$2K/mes (señal real más fuerte); RapidAPI tardó 5 años en llegar a $6M.

## Actores clave de infraestructura
- **Cloudflare Monetization Gateway** (anunciado 1-jul-2026): cobra cualquier página/dataset/API/MCP tool vía x402, settlement en stablecoins, sin stack de pagos propio, buyer sin cuenta. Reglas de pricing como expresiones (ej: $0.01/GET en /api/premium/*, $2 por generación de imágenes). Gestión como código (API + Terraform). Antecedente: Pay Per Crawl (jul-2025).
- **Zuplo**: gateway con metering por tokens/dimensiones, entitlements por plan, quotas por tiempo, keys con metadata de consumidor, MCP server handler desde OpenAPI.
- **Alephant** (open source, Rust, GPLv3): AI Agent Finance Gateway. BYO-keys, run-level attribution (agent/run/step/tool), Known Margin = ingreso del run − coste de modelo/herramientas (P&L por run, no por request).

## Modelos de pricing agent-native
1. Per-call flat (token incluye budget cap; gateway deduce y rechaza al agotarse).
2. Metered con tiered rates (volumen descuenta en real-time).
3. Outcome-based (paga solo si output cumple threshold; escrow con pre-auth).
- Per-request flat NO sirve para LLM APIs: 50 tokens vs 10,000 tokens cuestan distinto → metering por tokens.

## Implicaciones prácticas (resumen)
- Exponer pricing en el protocolo, no en docs.
- Budget por-call + tope duro por consumidor (no esperar a la factura).
- 402 (pagar o elegir otra) ≠ 429 (reintentar) — diseñar el signal correcto.
- Para vendedores: inventario de qué datos valen para agentes; diseñar pricing asumiendo tráfico de agentes.
- Ventana: infra recién construida (Cloudflare/Stripe/Visa/Mastercard/Coinbase/Anthropic), mercado sin monetizar → entrada barata ahora.
