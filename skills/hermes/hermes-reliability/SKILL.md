---
category: hermes
name: hermes-reliability
description: "Reliability Gate for Hermes: audit configured/reachable/operational/verified states, collect metrics, snapshot before changes, verify cron/MCP/model behavior, and fail closed. Use before or after modifying Hermes infrastructure."
version: 1.0.0
author: <USER> + Hermes
license: MIT
metadata:
  hermes:
    tags: [hermes, reliability, observability, rollback, cron, mcp, verification]
---

# Hermes Reliability Gate

## Core rule
Never call a component healthy because a process exists, a binary exists, a CLI returns zero, or a catalog lists a model. Evidence must progress through:

1. **configured** — declared in the active profile;
2. **reachable** — process/endpoint can be contacted;
3. **operational** — real capability responds;
4. **verified** — positive operation plus negative/timeout/recovery test passes.

## Standard workflow

```bash
python "$LOCALAPPDATA/hermes/scripts/reliability_audit.py" audit
python "$LOCALAPPDATA/hermes/scripts/reliability_audit.py" snapshot
```

Before changing config, create a snapshot. After changing it, run the audit, YAML parse, and the smallest real operation that proves the change. Never expose secret values.

## Self-evolution gates
Self-evolution follows Observer → Diagnostician → Proposer → Critic → Verifier → Apply. The proposer must not be the verifier. Changes to providers, MCPs, cron, SOUL.md, or canonical memory require a diff and rollback path. Prefer canary/profile-local changes before default-profile changes.

## Metrics
Append one JSON object per run to `audits/metrics.jsonl`. Track success, failure, timeout, duration, model/provider, and evidence path. Historical failures do not override a fresh verified run.

## Memory
Durable facts belong in `second-brain/zettel/` with provenance. Store preferences/identity in `memories/MEMORY.md`; store structural changes in `EVOLUTION.md`. Never store secrets or tokens.

## Failure policy
A failed check must remain visible. Do not convert `Connection failed`, missing vaults, timeouts, or partial delivery into PASS. Use `operational` or `unverified` until a real recovery test succeeds.

## Pitfall: cron HTTP 403 "API key does not have access to model z-ai/glm-5.3" (OrcaRouter)
Sintoma: un cron con `model: nvidia/glm-5.2` / `provider: nvidia` muere con `HTTP 403: This API key does not have access to model z-ai/glm-5.3`
y `ref=block_key_scope` en api.orcarouter.ai/console/token (ej. 2026-09-20, jobs `Hermes morning brief` 9b210d7bd566 y `Hermes self-audit` 177292cf0b20, streak creciente).

Diagnostico: `nvidia/glm-5.2` NO es la NVIDIA Integrate API de la skill nvidia-glm; se resuelve via OrcaRouter y
la key de ese provider (HERMES_ALIASES_API_KEY / ORCAROUTER_FREE_API_KEY) solo cubre el tier free, no z-ai/glm-5.3.
`provider: nvidia` no existe en `providers:` del config.yaml (solo experiential/bai/orcarouter/empero/agnes/free/tokenharbor).

Remediacion (requiere aprobacion humana — toca config de cron + credencial, FUERA del alcance autónomo del ciclo de autoevolución):
- Repuntar el cron a un modelo que la key cubra (p.ej. alias `binary`/`hy3-free` tier free) O
- Re-asignar la key OrcaRouter a con scope glm-5.3 O
- Fijar `model: nvidia/nemotron-3-ultra-550b-a55b:free` (provider free, OpenRouter).

NO intentar arreglarlo con parches de skill/script: la causa es el scope de la key + mapeo de modelo, no el codigo del runner.
Registrar diagnostico en EVOLUTION.md y dejar la decision al humano.
