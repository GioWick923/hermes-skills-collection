---
category: build-grade-loop
name: build-grade-loop
description: "Use when user wants automated build→grade→improve loops until quality target is met. Two-agent orchestrator: Agent A builds, Agent B scores via rubric, feedback loops until score reaches target or max iterations. Chinese: 做评改循环. Integrates with skill-project-review for scoring."
version: 1.1.0
author: apich
license: MIT
metadata:
  hermes:
    tags: [orchestrator, iteration, review, quality, multi-agent, feedback-loop]
    related_skills: [skill-project-review, skill-testing-and-iteration, skill-authoring, delegate-task]
---

# Build-Grade Loop（做评改循环）

## Overview

Automated quality improvement loop between two agents: a **Builder** (Agent A) that builds/improves a project, and a **Grader** (Agent B) that scores it against a rubric. The orchestrator cycles feedback until the score reaches the target or iteration limits are hit.

**Core loop:**
```
Orchestrator (主 Agent)
  ├── round 1: Agent A builds → Agent B grades → score X
  ├── round 2: Agent A improves (based on B's feedback) → Agent B re-grades → score Y
  ├── round 3: ... → score Z
  └── done when score >= target OR max_rounds OR plateau
```

This is NOT a replacement for human judgment. It's a force multiplier that automates the tedious "fix → recheck" cycle. The orchestrator remains under user control and can intervene at any round boundary.

**Architectural reality:** `delegate_task` creates ephemeral subagents — Agent A and Agent B are NOT persistent sessions with memory. Each round spawns fresh workers that die after returning. The "shared memory" between rounds is `feedback.md` on disk. This means:
- Agent A doesn't remember what it built last round → it reads feedback.md to recover context
- Agent B doesn't remember what it scored last round → previous scores are passed via context
- The orchestrator (main session) is the only persistent entity across all rounds

## When to Use

- User says "实现完自动评审改进直到满分" or "做评改循环"
- User asks for "build grade loop" or "agent feedback cycle"
- User wants to push a skill project from 80→95 through automated iteration
- User has a rubric and wants systematic improvement against it

Don't use for:
- Tasks that need human-in-the-loop judgment each step (use manual iteration)
- Open-ended creative work without clear scoring criteria
- Single-pass tasks (just use delegate_task once)
- Debugging a specific bug (use systematic-debugging)

## Prerequisites

Before starting the loop, the orchestrator must have:

1. **Project path** — the working directory where the project lives (or will be created)
2. **Requirements/spec** — what Agent A should build or improve (text, file, or skill definition)
3. **Rubric** — how Agent B scores (default: `skill-project-review`'s 7-dimension rubric)
4. **Target score** — when to stop (default: 90)
5. **Max rounds** — hard stop (default: 5)

### ⚠️ Path Rules (CRITICAL — e2e tested, 2026-07-12)

**必须使用确定的绝对路径。** Windows 上 `/tmp/`、`~/` 等路径在不同工具间可能解析到不同位置。MSYS `/tmp/` → `C:\Users\st\AppData\Local\Temp\`，但 Agent 可能解析为 `C:\tmp\`。Agent A 和 state_manager 写到不同目录会导致整个循环断裂。

- ✅ 正确：`C:/Users/st/Desktop/my-project/`
- ✅ 正确：`D:/projects/skill-test/`
- ❌ 错误：`/tmp/my-project/`（Windows 路径歧义，实测导致循环断裂）
- ❌ 错误：`~/my-project/`（`~` 在不同上下文展开不同）

Orchestrator 在 Step 0 中应验证路径可用性：`terminal: ls <project_path>`

If the user doesn't specify a rubric, use the 7-dimension rubric from `skill-project-review`:
SKILL.md quality (15), scripts (20), references (15), test data (15), test records (10), iterations (15), README (10).

## Core Workflow

### State Management

循环的状态由 `scripts/state_manager.py` 管理。它不做编排决策，只负责：
- 初始化状态目录
- 记录每轮分数
- 展示进度和平台期检测
- 追加 feedback 内容

**Agent 自己决定下一步做什么**，脚本只提供状态信息。

**关键命令：**
```bash
python scripts/state_manager.py init --project /path --target 90 --max-rounds 5
python scripts/state_manager.py status --project /path
python scripts/state_manager.py record --project /path --score 85 --critical 2 --minor 3
python scripts/state_manager.py feedback --project /path --append "评审报告内容"
python scripts/state_manager.py history --project /path   # 输出纯 JSON，方便解析
```

**Agent 的执行流程（每轮，连续执行，不中断）：**

```
┌──────────────────────────────────────────────────────┐
│ 每轮开始（报告分数后不等待，直接进入下一轮）            │
│                                                      │
│ 1. terminal: python state_manager.py status          │
│    → 看当前进度、分数趋势、是否平台期                     │
│                                                      │
│ 2. 检查停止条件（自动判断，不等用户）：                    │
│    - score >= target → Step 5 结束                    │
│    - round >= max_rounds → Step 5 结束                │
│    - PLATEAU → Step 4 聚焦策略（此时才暂停询问用户）      │
│    - 否则 → 继续第 3 步（不问用户，直接做）               │
│                                                      │
│ 3. delegate_task(Agent A) → 等待返回                  │
│                                                      │
│ 4. delegate_task(Agent B) → 等待返回                  │
│                                                      │
│ 5. 解析分数，record + feedback                        │
│                                                      │
│ 6. 向用户报告："第N轮 XX分"（一行，不停顿）               │
│                                                      │
│ 7. 立即回到第 1 步（不等用户回复）                       │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Completion criteria:** 每轮必须调用 `status` 和 `record`，不得跳过记录。

### Step 0: Setup

```bash
python scripts/state_manager.py init --project <project_path> --target <score> --max-rounds <N>
```

脚本自动创建 `.iteration-state/` 目录、`feedback.md`、`round-history.json`。

**Completion criteria:** 目录和文件已创建。调用 `status` 确认状态为"无轮次"。

### Step 1: Build Round (Agent A)

根据模式决定 prompt：

**MODE: BUILD_FROM_SCRATCH（首轮）：**
```
goal: "Build the project at <project_path> according to these requirements: <spec>"
context: <full requirements + rubric so A knows what B will evaluate>
workdir: <project_path>
```

**MODE: IMPROVE_BASED_ON_FEEDBACK（后续轮）：**
```
goal: "Improve the project at <project_path>. Read .iteration-state/feedback.md for the reviewer's deduction items. Fix ONLY the listed issues. Do NOT rewrite files from scratch. Verify your changes don't break existing tests."
context: <feedback.md contents + specific deduction items>
workdir: <project_path>
```

**Critical rules for Agent A:**
- 必须读 `.iteration-state/feedback.md`
- 只修扣分项，不做额外重构
- 改完后运行 `python tests/test_all.py` 验证（如果存在）
- `workdir` 必须设为 `project_path`

**Completion criteria:** Agent A 返回。项目文件已修改。

**⚠️ Orchestrator 必须验证文件（e2e tested, 2026-07-12）：** Agent A 可能声称成功但文件写到了错误路径。在信任 Agent A 的自报前，必须验证：
```bash
search_files(target='files', pattern='*', path='<project_path>')
```
如果文件数量为 0 或不符合预期，重新调度 Agent A 并在 context 中明确指定绝对路径。

### Step 2: Grade Round (Agent B)

```
goal: "Review the project at <project_path> using the skill-project-review methodology. Score against the rubric. Produce a scored table with specific evidence for each dimension. List every deduction item with file:line references. Run every script with real test data — do NOT score based on code reading alone."
context: <rubric + project_path + previous round score if applicable>
workdir: <project_path>
```

**Agent B 必须输出这个结构化格式：**

```markdown
## Score Report — Round N

| 评分维度 | 满分 | 得分 | 扣分原因 | 修复建议 |
|----------|------|------|----------|----------|
| ...      | ...  | ...  | ...      | ...      |
| **总计** | **100** | **XX** | | |

## Critical Deductions (must fix)
1. [dimension] — [specific issue] — [file:line] — [how to fix]

## Minor Deductions (nice to fix)
1. ...
```

**Completion criteria:** Agent B 返回结构化分数报告。

### Step 3: Record, Report, and Continue

从 Agent B 的输出中提取 `**总计**` 行的分数，然后执行以下步骤（必须按顺序全部执行，不可跳过）：

**3a. 记录分数：**
```bash
python scripts/state_manager.py record --project <path> --score <score> --critical <N> --minor <N>
```

**3b. 追加反馈到 feedback.md：**
```bash
python scripts/state_manager.py feedback --project <path> --append "<Agent B 的完整报告>"
```

**3c. 向用户报告本轮结果（简短一行）：**
```
📊 第 N 轮：XX/100 (+N)。已修复 X 项，剩余 Y 项扣分。
```

**3d. 判断下一步（自动执行，不等待用户确认）：**

```
if score >= target:
    → 立即执行 Step 5: Finalize
elif round >= max_rounds:
    → 立即执行 Step 5: Finalize
elif status 显示 PLATEAU:
    → 立即执行 Step 4: Plateau strategy
else:
    → 立即回到 Step 1（不等用户回复，不问"是否继续"）
```

### 🔴 关键规则：报告 ≠ 结束（e2e tested, 2026-07-12）

**向用户报告分数是循环中的一个步骤，不是循环的终点。**

```
❌ 错误流程：Step 1 → Step 2 → Step 3(记录+报告) → 等用户指令
✅ 正确流程：Step 1 → Step 2 → Step 3(记录+报告+继续) → Step 1 → ...
```

**只有以下情况才停止循环：**
1. `score >= target` → 达标，生成 final-report
2. `round >= max_rounds` → 超轮次，生成 final-report
3. 平台期触发 → 暂停，询问用户

**其他所有情况：报告完分数后，立即开始下一轮。不要等。不要问。直接做。**

### Step 4: Plateau Strategy

当 `status` 输出 `PLATEAU`：

1. 分析最近 2 轮的 stuck items（读 feedback.md 中反复出现的扣分项）
2. 在 feedback.md 中追加平台期分析：
   ```
   ⚠️ PLATEAU DETECTED
   
   Stuck items (appeared in last 2 rounds):
   1. [item] — Agent A hasn't fixed because [hypothesis]
      → Try: [specific approach]
   
   Strategy: Focus ONLY on top 3 highest-impact items.
   ```
3. 回到 Step 1

**Completion criteria:** feedback.md 已更新平台期策略，或循环已终止。

### Step 5: Finalize

```bash
python scripts/state_manager.py status --project <path>
python scripts/state_manager.py history --project <path>  # 获取完整 JSON 历史
```

生成 `final-report.md`：

```markdown
# Build-Grade Loop — Final Report

**Project:** <name>
**Target Score:** <target>
**Final Score:** <score>
**Rounds Completed:** <N>
**Status:** ✅ Target reached / ⚠️ Max rounds hit / 🛑 Plateau

## Score Progression
| Round | Score | Delta | Critical Fixes |
|-------|-------|-------|----------------|
| ...   | ...   | ...   | ...            |

## Remaining Deductions
<items still not fixed>

## Recommendation
<what user should focus on next>
```

**Completion criteria:** `final-report.md` 存在，用户已收到最终报告。

## Configuration Defaults

| Parameter | Default | Range | Notes |
|-----------|---------|-------|-------|
| `target_score` | 90 | 60–100 | Scores above 95 are aspirational — may not converge |
| `max_rounds` | 5 | 1–10 | Each round = 2 agent calls (build + grade) |
| `plateau_threshold` | 2 | 2–3 | Consecutive rounds with no score improvement before plateau strategy |
| `focus_mode` | false | true/false | When true, Agent A only fixes critical deductions, ignores minor ones |

## Feedback File Format

The `feedback.md` file is the memory that bridges rounds. It grows each round and is always passed to Agent A in full. See `references/feedback-format.md` for the full specification.

## Integration with skill-project-review

This skill delegates the Grader role to `skill-project-review`'s methodology. Specifically:

1. Agent B should load `skill-project-review` skill context
2. Agent B follows the 8-step core workflow (Inventory → Read → Run Scripts → Bug Hunt → Doc Sync → Iteration Quality → Parameter Justification → Score)
3. Agent B uses the 7-dimension rubric as default (unless user provides custom rubric)
4. Agent B applies all pitfalls from the skill

The orchestrator does NOT re-implement review logic — it delegates review entirely to Agent B running the review skill.

## Cost Awareness

Each round costs approximately:
- **Agent A (builder):** 3,000–8,000 output tokens (depends on project size)
- **Agent B (grader):** 5,000–15,000 output tokens (full project read + detailed report)
- **Total per round:** ~10,000–25,000 tokens

5 rounds ≈ 50,000–125,000 tokens. Inform the user of expected cost before starting.

## Common Pitfalls

### Pitfall 0: Orchestrator 报告完分数就停止了（e2e 实测 bug, 2026-07-12）

**问题：** Orchestrator 跑完 Round 1，记录了分数、写了 feedback，然后向用户报告"得分 59/100"——然后就停了。没有继续 Round 2。原因是 Orchestrator 把"报告结果"当成了任务终点。

**根因：** Step 3 没有显式区分"报告"和"结束"。Agent 自然倾向于在汇报后等待用户指令，而不是自动继续。

**代码示例：**
```
❌ 错误行为：
  Round 1: record(59) → feedback(报告) → 告诉用户"59分" → 停止等待
  
✅ 正确行为：
  Round 1: record(59) → feedback(报告) → 告诉用户"59分" → 立即开始 Round 2
  Round 2: record(88) → feedback(报告) → 告诉用户"88分" → 立即开始 Round 3
  Round 3: record(92) → 告诉用户"92分，达标" → 生成 final-report
```

**修复：** Step 3d 的判断是自动的——只有达标/超轮次/平台期才停止，其他情况报告完立即继续。不要等用户说"继续"。

**验证清单：**
- [ ] Round 1 报告后，是否立即启动了 Round 2 的 delegate_task？
- [ ] 有没有在中间停下来问用户"是否继续"？
- [ ] 循环是连续跑完的，还是每轮都要用户催？

### Pitfall 0b: Confusing "utility script test" with "skill end-to-end test"
**问题：** 只测试了 state_manager.py 的各个命令（init/record/status/history/feedback），就认为 skill 可用。实际上 skill 的核心是整个 build→grade→improve 循环流程，不是状态管理脚本。
**修复：** 必须做端到端测试——真正跑一轮 delegate_task(Agent A) → delegate_task(Agent B) → record → feedback 的完整流程。脚本测试只验证了"记账员"好用，没验证"两个 Agent 协作"好用。
**验证清单：**
- [ ] 脚本单元测试通过（test_all.py）
- [ ] Agent A 能按要求构建项目（不是空跑）
- [ ] Agent B 能读取项目并输出结构化评分报告（不是随便打分）
- [ ] 分数能正确提取并记录到 state_manager
- [ ] feedback.md 能正确传递给下一轮的 Agent A

### Pitfall 1: Agent A rewrites from scratch on improvement rounds
**问题：** Agent A ignores existing code and regenerates everything, losing good work and introducing new bugs.
**代码示例：**
```
# 错误：Agent A 的 prompt 只说 "improve the project"
goal: "Improve the project at /path/to/project"

# 正确：明确要求增量修改，列出具体扣分项
goal: "Fix ONLY these specific issues in the project at /path/to/project. Do NOT rewrite files from scratch. Read each file first, then make targeted edits:\n1. scripts/analyzer.py:45 — add error handling\n2. tests/iteration-log.md — add before/after table"
```
**修复：** Always pass specific deduction items with file:line references to Agent A.

### Pitfall 2: Reviewer scores are inconsistent across rounds
**问题：** Agent B gives 85 in round 1, then 82 in round 2 even though Agent A fixed issues. Different runs have different "moods."
**修复：**
1. Include previous scores in Agent B's context: "Previous round scored 85. Verify that previously-fixed items remain fixed."
2. Tell Agent B to use the exact same rubric weights every round
3. If score drops after improvement, Agent B must explain each new deduction

### Pitfall 3: Feedback.md grows unboundedly
**问题：** After 5 rounds, feedback.md is 10,000+ chars, eating into Agent A's context window.
**修复：** On round 4+, compress older rounds into summaries:
```
## Rounds 1-3 Summary
- Fixed: error handling, iteration log, test data boundaries
- Score: 72 → 81 → 85
- Stuck items: reference file depth (15→10, unchanged since round 2)
```

### Pitfall 4: No human escape hatch
**问题：** Loop runs autonomously for 5 rounds, user can't intervene.
**修复：** After each round, report the score to the user. If score drops or plateaus, pause and ask: "分数卡在 82，是否继续？还是手动调整方向？"

### Pitfall 5: Target score 100 is unreachable
**问题：** User sets target=100, loop runs max_rounds and never converges.
**修复：** On setup, warn user if target > 95: "目标分数 >95 可能无法收敛。建议设置为 90-95。" If target=100 is confirmed, set max_rounds to 3 to limit cost.

### Pitfall 6: Agent B doesn't verify, just reads
**问题：** Agent B reviews by reading code but doesn't run scripts or check actual output. Scores are based on "looks correct."
**修复：** Agent B's prompt must explicitly include: "Run every script with real test data. Do NOT score based on code reading alone. Execute and verify output."

### Pitfall 7: Circular dependency — A fixes what B didn't flag
**问题：** Agent A changes code that wasn't flagged by Agent B, introducing new issues that Agent B then deducts for.
**修复：** Agent A's prompt includes: "Fix ONLY the items listed in the feedback. Do not refactor or improve code that is not flagged as a deduction."

## Verification Checklist

- [ ] `.iteration-state/` 目录已创建（feedback.md + round-history.json）
- [ ] 每轮 Agent B 输出结构化评分报告
- [ ] 分数记录到 round-history.json
- [ ] 评审报告追加到 feedback.md（含 file:line 引用）
- [ ] 平台期检测在连续 2 轮不升时触发
- [ ] 每轮结束后向用户报告分数（一行简短消息）
- [ ] **报告分数后，如果未达标且未超轮次，立即开始下一轮（不等用户确认）**
- [ ] 只有达标/超轮次/平台期才停止循环
- [ ] 最终报告包含分数趋势表和剩余扣分项
- [ ] Agent A 收到具体扣分项（不是"改进项目"这种笼统指令）
- [ ] Agent B 运行脚本验证（不是只读代码）
- [ ] 开始前告知用户预估成本
- [ ] 路径使用确定的绝对路径（Windows 上不用 /tmp/）

## Quick Start Example

User: "帮我把这个 skill 项目做评改循环到 90 分"

Orchestrator response:
1. Load `build-grade-loop` + `skill-project-review` skills
2. Initialize `.iteration-state/`
3. Round 1: Agent A builds initial project → Agent B grades → score 68
4. Report: "📊 第1轮：68/100。Critical 2 项，Minor 3 项。继续改进..."
5. Round 2: Agent A fixes 2 critical items → Agent B re-grades → score 81
6. Report: "📊 第2轮：81/100 (+13)。已修复：错误处理、迭代记录。继续改进..."
7. Round 3: Agent A improves references → Agent B grades → score 89
8. Report: "📊 第3轮：89/100 (+8)。距目标差1分。继续改进..."
9. Round 4: Agent A adds boundary test data → Agent B grades → score 92
10. Report: "📊 第4轮：92/100 (+3)。🎉 达标！"
11. Finalize: "✅ 最终得分 92/100。详见 final-report.md"
