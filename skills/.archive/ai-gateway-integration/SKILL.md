---
name: ai-gateway-integration
description: "Integrate AI gateways: triage, deploy, wire, verify."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ai-gateway, provider, llm-router, integration, omniroute, openrouter, self-host]
    related_skills: [external-repo-adoption, openrouter-fallback-setup, hermes-model-config, freellm-providers, openai-compatible-api-testing]
---

# AI Gateway Integration (router → Hermes provider)

## When to Use

- El usuario pide "integra esto" con un repo/endpoint de **gateway AI** (OmniRoute, OrcaRouter,
  OpenRouter, aihubmix, LiteLLM, TokenRouter…).
- Añadir un proveedor OpenAI-compatible a Hermes (base_url + api_key + model alias).
- Evaluar si un gateway nuevo **aporta** vs los que ya hay (anti-duplicación).

## Disciplina (heredada de external-repo-adoption, 2026-08-27 — 3 ocurrencias)

1. **Consulta ANTES de ejecutar**: leer → aprender → informe con veredicto 🟢/🟡/🔴 → esperar "ejecuta".
2. **Interrupción MID-instalación**: aunque el usuario ya aprobó ("a"), puede mandar NUEVOS links en
   mitad de la instalación ("analiza estos antes de instalar"). PAUSA todo el wiring (crear keys,
   conectar providers), analiza, reporta y espera re-aprobación. El paquete/server ya arrancado puede
   quedar idle; lo que no se hace es configurar sin el nuevo OK.
3. **Revisar existente primero** (regla usuario): `hermes config get model`, `hermes config get
   providers`, nombres de keys en `$LOCALAPPDATA/hermes/.env` — no duplicar gateways.

## Workflow

1. **Triage** del gateway (si es repo: GitHub API → pushed_at, releases, license, actividad; si es
   endpoint: web_search reciente).
2. **Inventario actual**: providers + aliases + keys ya configurados (paso 3 de disciplina).
3. **Veredicto de valor**: tabla 🟢 already-have / 🟡 real-improvement / 🔴 decoration. Preguntar
   siempre: ¿qué hace este gateway que los míos no hacen? (p.ej. auto-fallback entre free tiers,
   compresión de tokens, keyless providers).
4. **Elegir despliegue**:
   - **Hosted**: base_url + api_key → provider custom.
   - **Self-hosted local** (preferido por usuario): npm global / docker / source → `localhost:<port>/v1`,
     modelo especial (p.ej. `auto` / combo).
5. **Wire**: provider `custom`, `api_mode: openai`, alias de modelo (sintaxis exacta: ver skill
   `hermes-agent`).
6. **Verificar con request REAL**: `curl <base>/v1/models` + un chat completion contra el endpoint
   que corre el proceso real. Nunca "validado" sin prueba directa (regla SOUL §22).

## Pitfalls

- **npm embebido de Hermes (Windows)**: `npm i -g <tool>` instala bajo
  `$LOCALAPPDATA/hermes/node/node_modules/`; bin en `$LOCALAPPDATA/hermes/node/<tool>.cmd`.
  `which` lo encuentra vía el PATH del prefix.
- **Links cortos (t.co)**: HEAD no sigue redirects (exit 23). Usar
  `curl -sL -o /dev/null -w "%{url_effective}" --max-redirs 10 -A "Mozilla/5.0 ..." <url>`.
- **Modelo `auto`/combo**: necesita ≥1 provider conectado en el dashboard del gateway; un log tipo
  "[AUTO] matched no connected models" es ESPERADO hasta conectar el primero (p.ej. Kiro/OpenCode
  Free/Pollinations).
- **Servidor Node local**: arrancar con background=true + watch_patterns del puerto; datos
  persistentes en `~/.<tool>/` (OmniRoute genera STORAGE_ENCRYPTION_KEY al primer boot).
- **Auditar el hosted antes de decidir**: `npx @jkup/whoiz <domain>` (Node 20+) → fingerprint
  CDN/hosting (edge+origin); respeta robots, sin telemetría.

## Support files
- `references/omniroute.md` — caso completo 2026-08-27: OmniRoute (gateway self-host, 357 providers,
  90+ free tiers, fallback 4 niveles, compresión RTK+Caveman; integración validada hasta boot).
