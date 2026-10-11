---
name: agent-api-gateway-patterns
description: "Cliente API con keys: allowlist, retries, sandbox con tope."
metadata:
  source: xapi-labs/xapi-cli (revisado 2026-08-20) + investigación agentic payments (Zuplo, Alephant, x402/MPP, Cloudflare)
---

# Agent API Gateway Patterns

Patrones extraídos de xapi-cli (xAPI gateway) y del ecosistema agentic payments 2026.
Objetivo: clientes API seguros para agentes autónomos que manejan dinero, keys y efectos no reversibles (bots de trading, cron, integraciones).

## Cuándo usar
- Construir un cliente API con API key (bots de trading, integraciones, cron jobs).
- Auditar scripts que envían keys o ejecutan operaciones no idempotentes (pagos, órdenes, posts).
- Exponer una herramienta propia como API para agentes (monetización).

## Patrón 1: Host allowlist (protege la key)
La key NUNCA debe salir a un host no autorizado. Validar antes de cada request, con el MISMO parser que usa fetch (WHATWG URL), no con strings.

```ts
const ALLOWED_HOST_EXACT = ['api.mi-servicio.com'];
const ALLOWED_HOST_SUFFIXES = ['.mi-servicio.com'];

function hostnameOf(hostOrUrl: string): string {
  const raw = hostOrUrl.includes('://') ? hostOrUrl : `http://${hostOrUrl}`;
  try { return new URL(raw).hostname.toLowerCase(); } catch { return ''; }
}

// ¡OJO! prefijo /^127\./ es INSECURO: matchea 127.attacker.com o 127.0.0.1.nip.io
function isLoopbackIPv4(h: string): boolean {
  const m = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/.exec(h);
  if (!m) return false;
  const o = m.slice(1).map(Number);
  return o.every(x => x <= 255) && o[0] === 127;
}

export function assertAllowedHost(hostOrUrl: string): void {
  const h = hostnameOf(hostOrUrl);
  if (!h || !(ALLOWED_HOST_EXACT.includes(h) || ALLOWED_HOST_SUFFIXES.some(s => h.endsWith(s)) || isLoopbackIPv4(h))) {
    throw new Error(`refusing to contact untrusted host "${h || hostOrUrl}": API key may only be sent to allowlisted hosts`);
  }
}
```

## Patrón 2: Retries SOLO idempotentes
- GET/lecturas → se pueden reintentar (backoff exponencial con jitter + Retry-After).
- POST no idempotente (pagar, crear orden, postear) → NUNCA reintentar por defecto: un gateway 5xx no prueba que el upstream no ejecutó; el retry puede DUPLICAR el efecto (doble orden, doble pago).
- El caller de una acción conocida como idempotente (poll, status) puede opt-in a retries explícitos.

```ts
function isRetryableStatus(s: number): boolean {
  return s === 408 || s === 429 || s === 502 || s === 503 || s === 504; // NO 500/501
}
// retries param: default 0 para escrituras, N para GETs idempotentes.
```

## Patrón 3: Rechazar redirects
fetch reenvía headers custom (incluida la key) a través de redirects → la key se fugaría a un host fuera del allowlist.

```ts
const res = await fetch(url, { ...opts, redirect: 'manual', signal });
if (res.status >= 300 && res.status < 400) {
  throw new Error(`refusing to follow redirect to "${res.headers.get('location') ?? '?'}" (key would leak past allowlist)`);
}
```

## Patrón 4: Errores de negocio con status 200
Algunas APIs devuelven HTTP 200 con `{success:false, data:{statusCode:401}}`. Detectar y traducir a mensaje accionable:

```ts
const body = JSON.parse(text);
if (body && typeof body === 'object' && body.success === false) {
  if (body.data?.statusCode === 401 || body.data?.error === 'Unauthorized') {
    throw new Error('Authentication failed: ' + (body.data.message || 'invalid key') + '. Run config set apiKey=<key>');
  }
  if (body.data?.error === 'OAuth Required' || (body.data?.statusCode === 403 && body.data?.message?.includes('OAuth'))) {
    throw new Error((body.data.message || 'OAuth required') + '. Run oauth bind');
  }
}
```

## Patrón 5: Sandbox/cómputo efímero con tope de precio
Para ejecutar código no confiable o caro: alquilar, correr, TERMINAR EN `finally`, con price ceiling.

- `try { create + wait + exec } finally { terminate }` — siempre limpia, incluso en fallo.
- Tope por defecto (p.ej. $0.20/h) salvo que el usuario pida explícitamente `--keep`.
- Antes de ejecutar una acción facturable, verificar que el archivo de salida NO exista (`open(target,'wx')` → EEXIST = abortar antes de gastar).

## Patrón 6: GET antes de CALL (schema discovery)
El agente SIEMPRE lee el esquema de la acción antes de ejecutarla: `get <action_id>` → ver parámetros requeridos → `call`. Reduce errores de parámetros y llamadas facturadas fallidas.

## Patrón 7: Config segura
- Guardar key en `~/.<tool>/config.json` con permisos `0600` (archivo) y `0700` (directorio); en Windows los permisos POSIX no aplican — no fallar por eso.
- Enmascarar en output: `apiKey.slice(0,8) + '...'`.
- Preferir key vía env var (más seguro en CI); aceptar stdin para evitar shell history: `config set apiKey=-`.
- Tras registrar una cuenta con bindUrl que contiene la key: nunca loguearla/compartirla.

## Patrón 8: Descubribilidad = skills + MCP
Una herramienta que un agente no puede descubrir NO existe:
- Empaquetar una `SKILL.md` en el package/producto (con comandos, ejemplos, workflow).
- Exponer endpoint MCP (`https://mcp.mi-servicio.com/mcp?apikey=...`) para Cursor/Claude Code/Hermes.
- Catálogo de acciones con schema JSON accesible por `list`/`search`/`get` (gateway con catálogo).

## Patrón 9 (negocio): monetizar para agentes
Estado 2026: <5% de 12,770+ MCP servers monetizan; volumen global <$50K/día. Infra recién construida:
- x402 (Coinbase) — HTTP 402 + prueba de pago; adoptado por Cloudflare Monetization Gateway (jul 2026).
- Stripe MPP (mar 2026) — "OAuth para dinero", sesiones con spending limit, micropagos streaming.
- L402 (Lightning + macaroon) — token lleva el presupuesto (caveat) incrustado, sin billing central.
- Para exponer: pricing machine-readable en el protocolo (no en docs), presupuesto por-call, tope duro por consumidor.
- Métrica clave: "Known Margin" (Alephant) = ingreso del run − coste de modelo/herramientas, por run.

## Pitfalls documentados
- ❌ Prefijo `127.` para loopback → matchea dominios atacantes (`127.attacker.com`). Usar regex IPv4 completo + validar octetos.
- ❌ Parser manual de hostname → WHATWG trata `\` como `/`: `evil.example\@api.legal.com` tiene hostname `evil.example`. Usar `new URL()`.
- ❌ Reintentar POSTs tras timeout → operaciones duplicadas (doble pago/orden).
- ❌ `redirect: 'follow'` con key en headers → fuga a host externo.
- ❌ Precio flat por request para LLM APIs → un request 50 tokens vs 10,000 tokens cuestan distinto. Metering por tokens/dimensiones.
- ❌ 429 rate limit vs 402 payment required: 429 el agente reintenta (empeora el problema); 402 el agente puede elegir herramienta más barata o pedir presupuesto.

## Verificación
- [ ] Tests de allowlist: `evil.example\@api.legal.com` → rechazado; `127.0.0.1.nip.io` → rechazado; `127.0.0.1` → permitido.
- [ ] Test de retry: simular 503 en POST → no retry; 503 en GET → retry con backoff.
- [ ] Test de redirect: servidor que responde 302 con Location externo → excepción con mensaje claro.
- [ ] Test de error negocio: mock 200 + success:false/401 → mensaje "Authentication failed" con hint.
- [ ] Sandbox: verificar terminate en finally tras fallo del comando.
