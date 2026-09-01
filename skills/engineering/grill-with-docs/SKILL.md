---
name: grill-with-docs
description: Relentless interview creating docs (ADRs, glossary) inline.
disable-model-invocation: true
---

# Grill with Docs

Run a `grilling` session (relentless interview), using the `domain-modeling` skill to build/sharpen the project's domain model as decisions crystallize.

## What it combines

- **Grilling** — interview the user one question at a time, walking each branch of the decision tree, providing recommended answers, waiting for confirmation before continuing
- **Domain Modeling** — actively build/sharpen `CONTEXT.md` (glossary) and `docs/adr/` (ADRs) inline as terms are resolved and trade-offs made

## Process

1. Start grilling session — ask one question at a time
2. For each decision that crystallizes:
   - If new term not in `CONTEXT.md` → add it (create file lazily)
   - If fuzzy term sharpened → update `CONTEXT.md` right there
   - If hard-to-reverse, surprising-without-context, real-trade-off decision → offer ADR in `docs/adr/`
3. Cross-reference with code: if user states how something works, check if code agrees. Surface contradictions.
4. Don't batch updates — capture inline as they happen
5. `CONTEXT.md` = glossary only (no implementation details, no spec, no scratchpad)

## ADR Criteria (all three must be true)

1. **Hard to reverse** — cost of changing mind later is meaningful
2. **Surprising without context** — future reader will wonder "why?"
3. **Result of real trade-off** — genuine alternatives existed, picked one for specific reasons

If any missing → skip ADR.

## Formats

- `CONTEXT.md` format: see `domain-modeling` skill references
- ADR format: see `domain-modeling` skill references