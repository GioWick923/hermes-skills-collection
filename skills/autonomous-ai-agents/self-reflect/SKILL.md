---
name: self-reflect
description: Generate-critique-correct loop using a cheap model.
---

# Self-Reflect

Reflexion pattern from `42-evey/hermes-plugins` `evey-reflect` (MIT). Run important outputs through a critique loop before sending: **Generate → Critique → Correct** (max 3 iterations).

Use before reporting: research summaries, daily reports, delegation results, goal reviews, or any high-stakes output.

## Loop

```
1. GENERATE  — produce draft output for the task
2. CRITIQUE  — cheap model reviews draft against criteria
3. DECIDE    — if PASS (score >= 7/10): done. If FIX: correct and loop
4. REPEAT    — max 3 iterations, then force output with notes
```

## Critique prompt (adapt)

```
You are a quality reviewer. Critique this draft response.

ORIGINAL TASK: {task}
DRAFT RESPONSE: {draft}
CRITERIA: {criteria}

Review for:
1. Factual accuracy — are claims verifiable?
2. Completeness — does it answer the full question?
3. Actionability — can the reader act on this?
4. Conciseness — any unnecessary fluff?

If GOOD (score >= 7/10): respond PASS: [brief note]
If needs improvement: respond FIX: [specific issues to fix]
Keep critique under 100 words.
```

## Cost discipline

- Use a **cheap/free model** for critique (e.g. local, or your cheapest available). The point is $0 marginal cost.
- Default `CRITIQUE_MODEL` = your cheapest tier. For this environment use `tencent/hy3` (already active) or a local model if available.
- `MAX_ITERATIONS = 3`

## Integration

- Call this from `autonomy-engine` loop step 5 (REFLECT)
- Works with `gbrain` for storing critique learnings
- Do NOT skip for user-facing deliverables

## Source

Ported from https://github.com/42-evey/hermes-plugins (MIT). Plugin: `evey-reflect/__init__.py` (102 lines). Original uses qwen35-4b local; adapt model to your stack.
