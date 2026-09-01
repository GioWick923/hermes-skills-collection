---
category: autonomous-ai-agents
name: hermes-closed-loop-engineering
description: "Use when designing or executing non-trivial Hermes work as a closed feedback loop: verifiable goals, bounded iterations, independent verification, clean memory/skill updates, and evidence-backed completion."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, loops, multi-agent, verification, memory, skills, orchestration]
    related_skills: [hermes-agent, autonomous-ai-agents, systematic-debugging, requesting-code-review, plan]
---

# Hermes Closed-Loop Engineering

## Overview

Closed-loop engineering turns a broad request into a bounded feedback system:

```text
DISCOVER -> PLAN -> EXECUTE -> VERIFY -> ITERATE
```

The loop stops only when a measurable condition passes, not when the executing agent feels satisfied. For important work, the agent that builds is not the agent that judges. A fresh verifier, test command, rubric, or external evidence decides whether the loop is complete.

Use this skill to make Hermes behave less like a one-shot prompt responder and more like a loop engineer: define the stop condition, run real tools, verify independently, iterate on failure, and distill reusable learning into memory or skills only when it is durable.

## When to Use

Use this skill when the task is any of the following:

- Complex enough to need 3+ steps or multiple tools.
- About Hermes configuration, profiles, skills, cron, gateway, MCP, worktrees, or multi-agent orchestration.
- Coding, debugging, research, content, sales, or automation work where success can be evaluated.
- A request to "improve", "optimize", "integrate", "make autonomous", "build a workflow", or "set up agents".
- Any task where self-approval would be risky and an independent check would materially improve quality.

Do **not** use the full loop for simple factual answers, tiny edits, or low-risk one-shot transformations. For those, answer directly and verify only what needs grounding.

## Core Rule

Before doing substantial work, convert the request into this compact contract:

```markdown
Objective:
  <what must be true at the end>

Done when:
  <observable pass condition: command, file, test, source-backed claim, or reviewer approval>

Limit:
  <max turns, attempts, time, cost, or scope>

Rubric:
  - <criterion 1>
  - <criterion 2>
  - <criterion 3>

Evidence:
  <what will be shown to the user at the end>
```

If the pass condition cannot be checked, narrow the task until it can. A non-verifiable objective is a wish, not a loop.

## The Five-Stage Loop

### 1. Discover

Load relevant skills first. Inspect live state instead of guessing: files, config, docs, tests, tools, sessions, or original sources. For Hermes itself, load `hermes-agent` and treat official docs as source of truth.

Done when:
- Required context is loaded or explicitly marked unavailable.
- The agent knows which files/tools/sources can prove success.
- Hidden assumptions are written down before execution.

### 2. Plan

Create a short plan with acceptance criteria and a stop condition. Use `todo` for visible multi-step work. Prefer closed loops before open exploration.

Done when:
- The plan has one active step.
- Each step has a checkable completion criterion.
- A budget/limit exists for iterations, time, or attempts.

### 3. Execute

Act with tools. Keep changes narrow. For code, config, or files, edit the actual artifact and read it back. For long autonomous work, prefer `cronjob`, kanban, worktrees, or background processes over fragile manual loops.

Done when:
- The requested artifact exists or the requested action has been performed.
- Side effects are within the requested scope.
- Intermediate failures are captured as feedback, not hidden.

### 4. Verify

Use the strongest available verifier:

| Work type | Preferred verifier |
|---|---|
| Code | tests, lint, typecheck, build, reproducible command |
| Hermes config | `hermes config`, `hermes tools list`, `hermes profile list`, `hermes doctor`, read-back of files |
| Research | primary sources, cross-checks, contradiction scan |
| Content | rubric, target audience criteria, independent critique |
| Multi-agent | subagent reviewer, kanban/task state, isolated profile output |
| Automation | dry run, job listing, script stdout, bounded test execution |

For important work, spawn an independent verifier subagent with only the objective, rubric, and evidence. The verifier should not share the executor's full reasoning unless necessary.

Done when:
- A real command/source/reviewer produced a pass/fail signal.
- The final answer cites the evidence actually observed.
- If verification was impossible, the blocker is stated plainly.

### 5. Iterate

If verification fails, do not restart from scratch. Feed the failure back into the next pass:

```text
Failure -> cause hypothesis -> smallest corrective action -> re-run verifier
```

Escalate only when the loop hits the stated limit, needs a human decision, or risks unwanted side effects.

Done when:
- The verifier passes, or
- the limit is reached with a clear failure report and next options.

## Independent Verifier Pattern

Use this structure when delegating review:

```text
Goal: Verify whether the work satisfies the rubric. Do not improve it.
Context: Objective, files changed or artifact path, command outputs, constraints.
Rubric:
- Criterion A
- Criterion B
- Criterion C
Return:
- PASS or FAIL
- evidence for each criterion
- smallest fix needed for each failure
```

Rules:
- The verifier judges; it does not rewrite unless explicitly asked.
- The verifier should be context-light to avoid inheriting the executor's bias.
- The main agent decides whether to iterate, not the executor.
- A self-review is acceptable only for low-risk work; high-risk work needs a separate check.

## Memory and Skill Discipline

Hermes has three different storage layers. Use the right one.

| Layer | Use for | Do not store |
|---|---|---|
| `memory` | Durable user preferences, environment facts, stable conventions | Task progress, PR numbers, temporary TODOs |
| `skills` | Reusable procedures discovered through work | One-off results or project state |
| session/todo/kanban/files | Current progress, open tasks, experiment logs | Cross-session rules that should guide future agents |

Before saving memory, pass this test:

```text
Will this still be useful in 7+ days and reduce future user steering?
```

Before creating or patching a skill, pass this test:

```text
Did we discover a reusable procedure, pitfall, command sequence, or rubric?
```

For long-running experiments, maintain a task-local `MEMORY.md` with:

```markdown
## PROBADO
- Experiment/result pairs.

## VERIFICADO
- Confirmed facts only, with evidence.

## ABIERTO
- Remaining hypotheses or next attempts.
```

Do not confuse that task-local file with Hermes persistent memory.

## Closed vs Open Loops

Start closed:

```text
specific objective + defined path + verifier + stop condition
```

Open the loop only after quality gates exist:

```text
broad exploration + budget + periodic verifier + explicit stop/continue decision
```

If a loop starts producing generic output, narrow the objective, add a better verifier, or lower the iteration budget.

## Hermes Implementation Recipes

### `/goal` Loop

Use for standing objectives inside an interactive Hermes session.

```text
/goal <verifiable objective>. Stop after <limit>. Done only when <verification passes>.
```

Include the verification command or evidence requirement in the goal text. Clear with `/goal clear` when no longer wanted.

### `delegate_task` Verifier

Use for independent review within the current turn.

```text
Spawn a verifier with: objective, rubric, artifacts, observed evidence.
Ask for PASS/FAIL, evidence, and smallest fixes.
```

Do not pass the full conversation unless needed; keep the verifier fresh.

### Cron Loop

Use for durable recurring checks.

- Put the prompt in self-contained form.
- Add a script when data collection is mechanical.
- Use `no_agent=True` only when stdout is already the final message.
- In TUI sessions, remember default cron delivery is local-only; do not promise live notification unless a gateway target is configured.

### Multi-Profile Loop

Use profiles when roles need isolation:

```text
orchestrator -> researcher/builder -> reviewer -> writer/finalizer
```

Route only the minimum context each profile needs. Keep reviewer independent from builder. Use kanban for durable projects and worktrees for parallel code edits.

## Common Pitfalls

1. **Vague stop condition.** "Make it better" is not a loop. Rewrite as a measurable pass condition.
2. **Self-approval.** The executing agent tends to be generous with itself. Use tests or a fresh verifier.
3. **No iteration limit.** Every loop needs a time, attempt, turn, or cost boundary.
4. **Memory pollution.** Do not save temporary progress or stale artifacts to persistent memory.
5. **Verifier with too much context.** A reviewer that reads the executor's whole narrative may inherit its assumptions.
6. **Open loop too early.** Exploration without quality gates becomes token-heavy slop.
7. **Stopping after writing.** File creation is not completion; read back and verify the artifact.
8. **Skipping structural validation.** For Markdown skills or config-like artifacts, read-back is necessary but not sufficient. Run a parser/validator for frontmatter, YAML, JSON, or TOML when the artifact format supports it. Quote YAML strings that contain colons before validating.
9. **Ignoring failed evidence.** A failed test is useful feedback, not an inconvenience to summarize away.

## Verification Checklist

Before finalizing substantial work, check:

- [ ] Objective was converted into a verifiable condition.
- [ ] Loop had an explicit limit or scope boundary.
- [ ] Relevant skills/docs/files were loaded before action.
- [ ] Actual tools were used for side effects or grounding.
- [ ] Verification produced real evidence.
- [ ] Independent reviewer/test was used when self-approval was risky.
- [ ] Failures fed into at least one correction attempt, unless blocked.
- [ ] Durable learning was saved to memory or a skill only if reusable.
- [ ] User-facing summary includes what changed, how it was verified, and any remaining limits.
