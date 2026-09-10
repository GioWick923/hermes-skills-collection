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
