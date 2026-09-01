# OmniRoute — caso de integración (2026-08-27)

## Qué es
Gateway AI auto-hostable (MIT, `diegosouzapw/OmniRoute`, ~57k⭐, branch `release/v3.8.x`, muy activo —
push diario). Un endpoint local OpenAI-compatible que:
- Apila ~90 free tiers (455 entradas catalogadas, ~1.51B tokens/mes gratis, deduplicado por pool).
- Auto-fallback de 4 niveles: Subscription → API → Cheap → Free (quota-aware).
- Compresión de tokens RTK + Caveman: 15-95% (~89% avg).
- MCP server con 110 tools, A2A, guardrails; compatible con 35 CLIs **incl. Hermes Agent**.
- Dashboard web/PWA con analytics de uso/coste.

**Diferencial vs gateways típicos del usuario (orcarouter/bai/empero/aihubmix)**: auto-fallback entre
free tiers + providers **keyless** (no necesitan API key upstream: Kiro, OpenCode Free, Pollinations,
Felo). Los gateways actuales no hacen eso.

## Instalación local (validada en sesión)
- Pre-requisitos: node ≥20 (host: v22.23.2), puerto 20128 libre, ~1 GB disco.
- `npm i -g omniroute` (~4 min, 1193 paquetes; warning `EPERM cleanup` benigno) → bin en
  `$LOCALAPPDATA/hermes/node/omniroute.cmd` (npm embebido de Hermes).
- `omniroute` → boot ~2 min, dashboard `http://localhost:20128` (auto-abre).
  - Primer arranque genera `~/.omniroute/.env` con `STORAGE_ENCRYPTION_KEY`.
  - Log `[AUTO] auto/coding:pro matched no connected models` = ESPERADO (aún sin providers).
  - `OMNIROUTE_AUTO_FREE_FALLBACK_TO_FULL_POOL=true` restaura el pool completo legacy.
- Free providers sin key (dashboard → Providers → Add Provider): **Kiro** (Claude gratis), **OpenCode
  Free**, **Pollinations** (GPT-5/Claude/Gemini), **Felo**. Modelo `auto` usa keyless por defecto.

## Wiring a Hermes (pendiente de completar en sesión — NO ejecutado)
1. Dashboard → API Keys → crear key local (es key para tools, no upstream).
2. Provider Hermes `custom`: `base_url: http://localhost:20128/v1`, `api_mode: openai`, `model: auto`.
3. Verificar con request real: `curl http://localhost:20128/v1/models -H "Authorization: Bearer <key>"`
   + un chat completion.

## Auditoría del hosted (antes de elegir hosted vs local)
- `npx @jkup/whoiz omniroute.online` → fingerprint CDN/hosting (edge + origin: CNAME, ASN Team Cymru,
  emisor TLS, headers `cf-ray`/`x-vercel-id`/…). Respeta robots.txt, sin telemetría, read-only.
  Node 20+; MIT (jkup/whoiz, ~17⭐).

## Alternativas consideradas
- **Docker**: `docker run -d --name omniroute -p 20128:20128 diegosouzapw/omniroute:latest`
  (host tiene Docker v29.7.2 activo). Descartado por preferencia del usuario a local npm.
- **Hosted omniroute.online**: requiere signup; auditar con whoiz antes.

## Estado al cierre de sesión
Instalado (v3.8.49) y servidor corriendo idle en proc background; **sin API key, sin wiring a Hermes** —
pausado por petición del usuario para analizar otros 2 links (jkup/whoiz, OpenHands) antes de continuar.
