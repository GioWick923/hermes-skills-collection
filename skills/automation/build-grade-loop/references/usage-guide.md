# Implement-Review Loop — 使用指南

## 这是什么？

一个让两个 Agent 自动"实现→评审→改进"循环的 skill。Agent A 负责写项目，Agent B 负责打分，分数不达标就继续循环，直到达到目标分或用完轮次。

```
你（用户）
  │
  └──→ 告诉 Hermes："帮我把这个项目迭代到 90 分"
         │
         ▼
       Orchestrator（主 Agent）
         │
         ├── 第1轮：Agent A 构建 → Agent B 评审 → 68分
         ├── 第2轮：Agent A 改进 → Agent B 评审 → 81分
         ├── 第3轮：Agent A 改进 → Agent B 评审 → 89分
         └── 第4轮：Agent A 改进 → Agent B 评审 → 92分 ✅
```

---

## 快速开始

### 用法 1：从零构建项目

```
帮我用 implement-review-loop 自动构建一个 [项目描述]，
目标分数 90 分，最多跑 5 轮。
项目路径：D:\my_project\
```

Hermes 会：
1. 初始化状态目录
2. 让 Agent A 根据需求构建完整项目
3. 让 Agent B 按 7 维度 rubric 评审打分
4. 把扣分项反馈给 Agent A 改进
5. 循环直到达标或用完轮次

### 用法 2：改进已有项目

```
我有一个 skill 项目在 D:\my_project\，
目前大概 70 分水平。用 implement-review-loop 迭代到 90 分。
```

### 用法 3：自定义评分标准

```
用 implement-review-loop 迭代这个项目，目标 85 分。
我的评分标准是：代码质量 40分、文档 30分、测试 30分。
```

---

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `target_score` | 90 | 目标分数，达到就停 |
| `max_rounds` | 5 | 最多跑几轮（每轮 = 1次实现 + 1次评审） |
| `rubric` | 7维度100分制 | 评分标准，可自定义 |

### 推荐配置

| 场景 | target | max_rounds | 说明 |
|------|--------|------------|------|
| 快速迭代 | 85 | 3 | 3轮能到85就很好了 |
| 标准迭代 | 90 | 5 | 默认配置，性价比最高 |
| 深度迭代 | 95 | 8 | 高分段每轮提升很慢 |
| 极限迭代 | 100 | 3 | 100分几乎不可能，限制轮次控制成本 |

> ⚠️ **target > 95 可能无法收敛。** 评审有主观性，同一项目两次评审可能差 2-3 分。

---

## 运行过程中会发生什么

### 每轮循环

```
轮次 N
  │
  ├── 1. 调用 state_manager.py status 查看进度
  │
  ├── 2. Agent A（实现者）
  │      首轮：从零构建项目
  │      后续轮：读 feedback.md，只修扣分项
  │
  ├── 3. Agent B（评审者）
  │      读取所有文件 → 运行所有脚本 → 按 rubric 打分
  │      输出：分数表 + Critical Deductions + Minor Deductions
  │
  ├── 4. 记录分数到 state_manager.py
  │
  ├── 5. 把 Agent B 的报告追加到 feedback.md
  │
  └── 6. 向你报告本轮得分
```

### 你会看到的输出

每轮结束后 Hermes 会告诉你：

```
📊 第 2 轮评审完成
   得分：81/100 (+13)
   已修复：scripts 错误处理 ✅、迭代记录前后对比 ✅
   剩余 Critical：references 内容太浅
   剩余 Minor：README 缺 CLI 示例
   状态：🔄 继续下一轮
```

### 结束时的报告

```
✅ Implement-Review Loop 完成！

| 轮次 | 分数 | 变化 | 修复项数 |
|------|------|------|----------|
| 1    | 68   | —    | 3        |
| 2    | 81   | +13  | 2        |
| 3    | 89   | +8   | 1        |
| 4    | 92   | +3   | 1        |

最终得分：92/100 ✅
剩余扣分：测试数据缺少极端边界值 (-3)、README 设计决策章节较薄 (-2)

详见：D:\my_project\.iteration-state\final-report.md
```

---

## 平台期处理

如果分数连续 2 轮不提升：

```
⚠️ 分数卡在 81/90，连续 2 轮未提升

卡住的问题：
1. references/ 深度不够 — 已尝试添加示例，但 Agent B 仍认为不够
2. 迭代记录 Step ⑤ 缺数据 — Agent A 添加了数字但格式不对

请选择：
A) 继续自动迭代（聚焦 top 1 问题，再跑 2 轮）
B) 手动介入（你来决定怎么改）
C) 降低目标到 83
D) 终止，接受 81 分
```

---

## 文件结构

运行后项目会多出一个目录：

```
your_project/
├── .iteration-state/
│   ├── feedback.md          # 每轮评审报告（Agent A 的改进依据）
│   └── round-history.json   # 分数历史（机器可读）
├── final-report.md          # 最终报告（循环结束后生成）
└── <项目文件>
```

### feedback.md 示例

```markdown
# Iteration Feedback

## Round 1 — Score: 68/100

### Critical Deductions
1. **scripts/ (20→12)** — `analyze()` 无错误处理
   - File: scripts/analyzer.py:45
   - Fix: 添加 `if not data: return None` 检查

### Minor Deductions
1. **README (10→7)** — 缺 CLI 用法示例

---

## Round 2 — Score: 81/100 (+13)

### Fixed Items ✅
- [scripts] 错误处理已添加 — 空输入测试通过

### Critical Deductions
1. **references/ (15→10)** — 内容只是 README 的复制
```

### round-history.json 示例

```json
{
  "rounds": [
    {"round": 1, "score": 68, "critical_fixes": 3, "minor_fixes": 2},
    {"round": 2, "score": 81, "critical_fixes": 2, "minor_fixes": 1}
  ],
  "target_score": 90,
  "max_rounds": 5
}
```

---

## 评分标准（默认 7 维度）

| # | 维度 | 满分 | 评什么 |
|---|------|------|--------|
| 1 | SKILL.md 质量 | 15 | frontmatter、When to Use、工作流、pitfalls |
| 2 | scripts/ 脚本质量 | 20 | 模块设计、错误处理、CLI、可运行性 |
| 3 | references/ 参考文件 | 15 | 文件数量、深度、可操作性 |
| 4 | 测试数据 | 15 | 覆盖范围、真实性、边界情况 |
| 5 | 测试记录 | 10 | 断言数、可复现性、环境说明 |
| 6 | 迭代记录 | 15 | 5步完整性、前后对比、代码级根因 |
| 7 | README.md | 10 | 选题、features、用法、目录结构 |

> 自定义 rubric 时，总分必须是 100。Agent B 会严格按你给的标准打分。

---

## Agent A 和 Agent B 的区别

| | Agent A（实现者） | Agent B（评审者） |
|---|---|---|
| **职责** | 写代码、建项目、修 bug | 读代码、跑测试、打分 |
| **首轮** | 从零构建 | 全面评审 |
| **后续轮** | 只修扣分项，不重写 | 验证修复 + 重新打分 |
| **记忆** | 读 feedback.md 恢复上下文 | 读上一轮报告对比变化 |
| **约束** | 不能改未标记的代码 | 不能改代码，只能评 |

---

## 成本估算

| 轮次 | Agent A tokens | Agent B tokens | 合计 |
|------|---------------|---------------|------|
| 1 轮 | ~5,000 | ~10,000 | ~15,000 |
| 3 轮 | ~15,000 | ~30,000 | ~45,000 |
| 5 轮 | ~25,000 | ~50,000 | ~75,000 |

> 实际消耗取决于项目大小。以上是中等规模 skill 项目的估算。

---

## 常见问题

**Q: Agent A 每轮都是新的，怎么记得之前改了什么？**
A: 不记得。靠读 `feedback.md` 恢复上下文。文件就是记忆。

**Q: Agent B 会不会评分不一致？**
A: 有可能。prompt 里要求传入上一轮分数作为参考，但 LLM 非确定性，差 2-3 分是正常的。

**Q: 能不能中途暂停？**
A: 可以。状态都在 `.iteration-state/` 目录里，下次继续时 `status` 命令会恢复上下文。

**Q: target 设 100 行不行？**
A: 行，但建议 `max_rounds` 设 3。100 分几乎不可能达到，限制轮次控制成本。

**Q: 能不用默认 rubric 吗？**
A: 可以。告诉 Hermes 你的评分维度和分值，Agent B 会按你给的标准打分。

**Q: 项目太大，Agent B 读不完怎么办？**
A: 缩小项目范围，或者让 Agent B 只评审特定维度（比如只看 scripts 和 tests）。
