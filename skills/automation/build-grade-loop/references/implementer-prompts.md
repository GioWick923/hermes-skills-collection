# Implementer (Agent A) Prompt Templates

## Round 1: Build From Scratch

```
你是一个项目实现者。请根据以下需求在指定路径构建完整项目。

## 项目路径
{project_path}

## 需求规格
{requirements}

## 评审标准（Agent B 会按这个标准打分）
{rubric}

## 要求
1. 在 {project_path} 下创建完整的项目结构
2. 确保所有脚本可以运行（无语法错误）
3. 包含 README.md 说明项目用途和使用方法
4. 包含测试文件和测试数据
5. 参考文件不少于 5 个，内容要深入、有具体示例
6. 代码控制在 150 行以内（单个脚本）
7. 考虑边界情况和错误处理

完成后，列出你创建的所有文件及其用途。
```

## Round 2+: Improve Based on Feedback

```
你是一个项目改进者。请根据评审反馈修复项目中的问题。

## 项目路径
{project_path}

## 上一轮评审得分
{prev_score}/{target_score}

## 评审反馈（必须修复的问题）
{feedback_content}

## 改进规则
1. 先读取每个需要修改的文件，理解现有代码
2. 只修复评审中标记的问题（Critical Deductions 优先）
3. 不要重写整个文件——做最小化、针对性的修改
4. 修改后运行 `python tests/test_all.py` 验证不破坏现有功能（如果测试存在）
5. 不要修改评审没有标记的代码
6. 如果某个扣分项无法修复（例如要求的内容超出了技术可行性），说明原因

## Critical Deductions（必须修复）
{critical_items}

## Minor Deductions（尽量修复）
{minor_items}

完成后，列出你修改了哪些文件、修复了哪些扣分项。
```

## Plateau Round: Focused Improvement

```
你是一个项目改进者。分数已经连续多轮没有提升，需要换策略。

## 项目路径
{project_path}

## 当前分数
{current_score}/{target_score}

## 平台期分析
分数在以下轮次停滞：
{plateau_analysis}

## 卡住的问题（这些扣分项反复出现）
{stuck_items}

## 新策略
1. 只关注上面列出的卡住问题，忽略其他扣分项
2. 如果之前的方法不奏效，换一种完全不同的思路
3. 如果某个问题确实无法在当前框架下解决，诚实说明原因
4. 优先修复影响分数最大的问题（看扣分分值）

完成后，说明你用了什么新方法来解决卡住的问题。
```

## Self-Verification Checklist (Agent A 内部用)

Agent A 改完后，应自行检查：

```markdown
## 自检清单
- [ ] 所有 Critical Deductions 已处理（修复或说明无法修复的原因）
- [ ] 修改的文件没有引入新错误
- [ ] 测试文件仍然通过（`python tests/test_all.py`）
- [ ] README.md 已同步更新（如果改了功能）
- [ ] 没有修改评审未标记的代码
- [ ] 新增的代码有注释/文档
```
