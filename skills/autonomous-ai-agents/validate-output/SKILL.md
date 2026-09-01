---
name: validate-output
description: Hallucination detection and confidence scoring for results.
---

# Validate Output

From `42-evey/hermes-plugins` `evey-validate` (MIT). Free/cheap models hallucinate more. Before trusting delegation or subagent results, run validation: confidence scoring, consistency check, source verification, format compliance.

Use after `delegate_task`, `self-reflect`, or any output you will report as fact.

## 4 check dimensions

1. **Confidence** — does the model hedge or claim certainty?
2. **Consistency** — do different parts contradict each other?
3. **Source verification** — does it cite checkable facts?
4. **Format compliance** — does it match what was asked?

## Red-flag regex patterns (hallucination signals)

```
(?i)as of my (last |knowledge )?cut.?off          → knowledge cutoff reference
(?i)I (don't|cannot|can't) (access|browse|search) → capability denial while giving specifics
(?i)(?:January|February|March|April|May) 20[0-9]{2} → specific date claim — verify
(?i)version \d+\.\d+\.\d+                          → specific version number — verify
(?i)according to (?:the|a) (?:official|latest)     → vague authority claim
(?i)it is (?:widely|generally|commonly) (?:known|accepted|believed) → weasel words
```

## Score prompt (cheap model, temperature 0)

```
Rate this AI-generated response on a scale of 0-10 for reliability.

TASK: {task}
MODEL: {model}
RESPONSE: {result}

Score criteria:
- 10: Verifiable facts with sources, no hedging
- 7-9: Mostly reliable, minor uncertainties acknowledged
- 4-6: Mix of facts and speculation, some claims unverifiable
- 1-3: Mostly speculation, contradictions, or hallucination signals
- 0: Complete fabrication

Respond with ONLY: SCORE: N | ISSUES: brief description
```

## Decision rule

- SCORE >= 7: trust, report
- SCORE 4-6: flag uncertainties, verify key claims before reporting
- SCORE <= 3: do NOT report as fact; re-run or verify externally

## Cost discipline

- Use cheap model (your cheapest tier) for validation — $0 marginal
- Regex pre-filter is free; run it always, LLM score only when regex passes

## Integration

- Run after `delegate_task` results (subagent summaries are self-reports, not verified)
- Run before `self-reflect` final pass
- Log score to autonomy-log.jsonl

## Source

Ported from https://github.com/42-evey/hermes-plugins (MIT). Plugin: `evey-validate/__init__.py` (137 lines). Original uses qwen35-4b; adapt model to your stack.
