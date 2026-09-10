# Infra/Plataforma → NO adoptar (recipe verificada 2026-09-01)

Cómo reconocer y manejar repos que son **infraestructura o plataforma**, no skills
adoptables. Los dos casos reales que lo establecieron.

## Señal de decisión (2 preguntas)
1. ¿Esto es un **skill/procedimiento** o un **servicio/runtime**? (¿despliega un
   daemon, un sandbox, un control-plane, un scheduler?)
2. ¿El stack de Hermes **ya lo resuelve**? (MCP, skills, cron, webhooks, memoria,
   delegación, BrowserSkill, Docker, DSH)

Ambas respuestas "servicio" + "ya lo tengo" → **NO adoptar**; extraer solo el patrón
de diseño como skill de conocimiento.

---

## Caso A: CubeSandbox (TencentCloud) — sandbox MicroVM por KVM
- Qué: "instant, concurrent, secure & lightweight sandbox service for AI agents",
  RustVMM + KVM, <60ms cold start, <5MB overhead, 100% E2B-SDK-compatible. Apache-2.0,
  productivo en Tencent Cloud, v0.6.0 (K8s, snapshot/rollback, AutoPause, ARM64).
- Stack real: CubeAPI (Rust/Axum) → CubeMaster (Go) → Cubelet → CubeShim (containerd
  v2) → CubeHypervisor (RustVMM) + CubeCoW (FICLONE) + CubeVS (eBPF) + CubeEgress
  (OpenResty) + CubeProxy + Redis. Control-plane stateless sobre Redis.
- Por qué NO: requiere KVM/Linux (no corre en Windows nativo), containerd, eBPF,
  OpenResty, Redis — infra pesada que duplica Docker + ejecución local Hermes. No es
  una skill, es un runtime para código no-confiable a escala.
- Qué extraer: el concepto **snapshot + rollback + fork a nivel de estado** (CubeCoW,
  checkpoints O(1) vía FICLONE) — idea de producto poderosa, no portable a este setup.
- Cuándo SÍ: si algún día se monta un VPS Linux con agents ejecutando código arbitrario
  a escala, es la elección natural como runtime E2B-compatible. Marcar "candidato futuro".
- Repo: `~/tools/cubesandbox` (clonado).

## Caso B: OpenHands Agent Canvas — control-center web de agents
- Qué: superficie de control self-hosted para agentic work; conecta múltiples backends
  (local/Docker/VM/Modal/Cloud), corre cualquier agente ACP (Claude Code, Codex, Gemini),
  Automation Server (schedule/webhooks) con prebuilts (GitHub Repo Monitor, Slack
  Channel Monitor), integraciones Slack/GitHub/Linear. `npm i -g @openhands/agent-canvas`,
  corre en :8000.
- Por qué NO: casi todo ya cubierto por Hermes (MCP nativo, skills, cronjob, webhooks,
  delegate_task, BrowserSkill). Instalarlo duplica Hermes+Telegram como superficie.
- Qué extraer (el único valor neto): el patrón **Automation Server / script-bundle** —
  separar lógica determinista (polling, dedup, API fijas) del juicio de agente, y que el
  cronjob haga `exit(0)` cuando no hay novedad → cero gasto de tokens en vacío. → skill
  `automation-workflow-patterns`.
- Cuándo SÍ: montar un VPS con agents always-on auto-triggereados (Slack/GitHub).

## Regla de oro
Evaluar un repo impresionante NO obliga a adoptarlo. "Impresionante" y "útil para tu
stack" son cosas distintas. Si el stack ya lo resuelve, extrae el patrón, no el paquete.
