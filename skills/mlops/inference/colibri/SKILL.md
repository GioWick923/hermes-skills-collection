---
category: mlops
name: colibri
description: "Evaluate and integrate the JustVugg/colibri local inference engine for GLM-5.2 MoE on constrained hardware."
---

# Colibrì / colibri

Use this skill when working with the **JustVugg/colibri** repository: a pure-C, zero-dependency inference engine for running **GLM-5.2 (744B MoE)** on consumer hardware by streaming experts from disk.

Repo: https://github.com/JustVugg/colibri

## What it is
Colibrì is not a general-purpose LLM framework. It is a highly specialized local inference engine focused on:
- running a very large MoE model on limited RAM,
- keeping the dense/shared part resident in memory,
- streaming routed experts from disk,
- offering a text-only OpenAI-compatible server,
- supporting advanced features like MTP speculative decoding, grammar-forced drafts, KV persistence, and optional CUDA hot-expert tiers.

## When it is worth considering
- You want to study extreme memory offloading for MoE models.
- You need a local/private text model path without Python runtime dependencies.
- You want to test whether a disk-streamed expert architecture is useful for Hermes-related local inference.
- You are comparing high-complexity local runtimes.

## When it is *not* a good default
- If you want a lightweight or simple backend.
- If you need image/video understanding.
- If you want a broadly supported runtime with easy setup.
- If you do not have large disk budget and patience for cold-start latency.

## Key facts to verify before adoption
- Disk requirements are very large.
- Cold performance depends heavily on cache warmth and storage speed.
- The project is highly experimental compared to mainstream runtimes.
- It is better treated as a research/benchmark integration than as a default Hermes dependency.

## Best Hermes use cases
- `researcher`: compare it against llama.cpp, vLLM, Ollama, and other local backends.
- `builder`: evaluate whether Hermes can call it as a backend or use its OpenAI-compatible API.
- `reviewer`: assess practicality, risk, cost, and maintainability.
- `orchestrator`: decide whether it belongs in the Hermes stack or stays as an optional niche engine.

## Recommended decision rule
If the goal is **raw feasibility research on very large local MoE inference**, colibri is interesting.
If the goal is **practical day-to-day Hermes usage**, it should stay optional, not primary.

## Output format
When using this skill, report:
1. What colibri is.
2. Why it matters.
3. Hardware/storage cost.
4. Operational risk.
5. Whether Hermes should adopt it or only reference it.
