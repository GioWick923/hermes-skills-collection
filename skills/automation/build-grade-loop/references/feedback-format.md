# Feedback File Format Specification

## 文件位置

```
<project_path>/.iteration-state/feedback.md
```

## 结构

```markdown
# Iteration Feedback

## Round {N} — Score: {score}/100 (+{delta})

### Fixed Items ✅
- [{dimension}] {what was fixed} — {evidence}

### Critical Deductions (must fix)
1. **{dimension} ({max}→{actual})** — {issue description}
   - File: {filename}:{line_number}
   - Fix: {specific fix instruction}

### Minor Deductions (nice to fix)
1. **{dimension} ({max}→{actual})** — {issue description}
   - File: {filename}:{line_number}
   - Fix: {specific fix instruction}

### New Issues (introduced by this round's fixes)
1. **{dimension}** — {what broke}

---
```

## 字段规范

### Score 行
- 格式：`## Round {N} — Score: {score}/100 (+{delta})`
- delta 相对于上一轮，首轮为 `—`
- 示例：`## Round 3 — Score: 85/100 (+4)`

### Fixed Items
- 只在第 2 轮及以后出现
- 列出上一轮 Critical Deductions 中已修复的项
- 必须附带验证证据（测试输出、截图描述等）

### Critical Deductions
- 格式：`**{dimension} ({max}→{actual})**`
- 必须包含：文件路径、行号、具体修复指令
- 修复指令必须可操作：
  - ❌ "加强错误处理"
  - ✅ "在 `scripts/analyzer.py:45` 的 `analyze()` 函数开头添加 `if not data: return {'error': 'empty input'}` 检查"

### Minor Deductions
- 同 Critical 格式，但优先级更低
- Agent A 在修复完所有 Critical 后再处理

### New Issues
- 本轮修复引入的新问题
- 下一轮的 Critical/Minor 列表中应包含这些项

## 压缩规则

当轮次 ≥ 4 时，执行压缩：

```markdown
## Rounds 1-{N-2} Summary
- Score progression: {score1} → {score2} → ... → {scoreN-2}
- Fixed items: {list of all fixed items across early rounds}
- Stuck items: {items that appeared in multiple rounds without being fixed}
- See round-history.json for full details

---

## Round {N-1} — Score: {score}/100
（完整内容）

## Round {N} — Score: {score}/100
（完整内容）
```

## 平台期标记

当检测到平台期时，在 feedback.md 末尾追加：

```markdown

---

## ⚠️ PLATEAU DETECTED — Round {N}

分数连续 {threshold} 轮未提升（{scores}）。

### 卡住的问题
以下扣分项在最近 {threshold} 轮中反复出现：
1. **{item}** — 出现在轮次 {round_numbers} — 原因分析：{hypothesis}
   → 建议尝试：{different approach}

### 新策略
- 只关注上述卡住问题
- 忽略 Minor Deductions
- 如果某个问题确实无法解决，诚实说明原因
```

## round-history.json 格式

```json
{
  "rounds": [
    {
      "round": 1,
      "score": 72,
      "timestamp": "2026-07-11T10:30:00",
      "critical_fixes": 3,
      "minor_fixes": 2
    }
  ],
  "target_score": 90,
  "max_rounds": 5,
  "plateau_threshold": 2,
  "created_at": "2026-07-11T10:00:00",
  "project_path": "/absolute/path/to/project"
}
```

## Agent A 读取 feedback.md 的规则

1. 首次改进轮：读取全部内容
2. 第 4 轮起：如果文件被压缩，只读取压缩摘要 + 最近 2 轮完整内容
3. 关注点优先级：
   - Critical Deductions > Minor Deductions > New Issues
   - 平台期标记 > 普通扣分项
