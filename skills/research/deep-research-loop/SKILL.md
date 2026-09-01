---
name: deep-research-loop
description: Multi-step autonomous research loop with role separation.
---

# Deep Research Loop

Autonomous deep-research pattern inspired by HKUDS/Auto-Deep-Research (AutoAgent framework). Use when the user wants thorough, multi-source research on a complex topic — not a single search.

## Architecture: 3 roles

Separate concerns into three agent roles (can be the same agent in sequence, or parallel subagents):

1. **Triage/Planner** — decomposes the question into sub-questions, identifies what sources/types of evidence are needed, tracks open threads
2. **Websurfer/Researcher** — fetches and reads sources (use `markdown-browser` for cheap reads, heavy browser for JS sites), extracts facts with citations
3. **Synthesizer** — merges findings, resolves contradictions, writes the final cited report

Inspired by Magentic-One's three-agent design (which AutoAgent cites).

## Loop

```
1. PLAN      — break question into 3-7 sub-questions
2. SEARCH    — for each sub-question: web_search / web_extract / markdown-browser
3. READ      — extract facts + citations (URL, date, author)
4. SYNTHESIZE — merge, flag contradictions, note confidence
5. GAP-CHECK — any sub-question unanswered? any contradiction unresolved?
6. ITERATE   — if gaps remain, loop back to SEARCH with refined queries
7. FINALIZE  — write cited markdown report
```

Stop when: all sub-questions answered OR 3 iterations without new info OR user says stop.

## Evidence discipline

- Every claim needs a citation (URL + date)
- Separate **facts** (sourced) from **inferences** (yours)
- Flag low-confidence or contradictory sources explicitly
- Prefer primary sources (papers, docs, official repos) over blogposts

## Token efficiency

- Use `markdown-browser` viewport paging for long pages
- Use `web_extract` for clean page pulls
- Summarize each source to 3-5 bullets before synthesizing

## When to use `delegate_task`

For large research, spawn parallel researchers:
- One per sub-question
- Each returns cited bullet summary
- Parent synthesizes

## Source

Pattern derived from https://github.com/HKUDS/Auto-Deep-Research (AutoAgent), which uses a 3-agent design inspired by Magentic-One. Adapted for Hermes toolset (web_search, web_extract, markdown-browser, delegate_task).
