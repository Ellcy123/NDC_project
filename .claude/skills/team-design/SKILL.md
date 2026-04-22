---
name: team-design
description: "编排标准内容设计团队：设计师产出 → 多审查员并行审查 → 内容总监汇总。用于单场景/单 NPC 设计等中等复杂度任务。"
argument-hint: "[设计任务描述，如 'Unit3 L3 Tommy 对话']"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

编排标准内容设计流程。收到任务后按以下 Pipeline 执行。

## 任务分级

先判断任务复杂度，决定审查员配置：

| 复杂度 | 判断标准 | 审查员配置 |
|--------|---------|-----------|
| 简单 | 改文案、单文件小修 | 不开 team，直接做 |
| 中等 | 单场景/单 NPC | dialogue-reviewer |
| 复杂 | 完整指证、多角色 | dialogue-reviewer + player-simulator |
| 重大 | 多 Loop 联动 | dialogue-reviewer + player-simulator + timeline-auditor + consistency-checker |

## Pipeline

### Phase 1: 设计师产出

根据任务类型 spawn 对应设计师 agent：
- 对话任务 → `dialogue-writer`
- state 任务 → `state-architect`
- 证据任务 → `evidence-designer`
- 指证任务 → `expose-designer`

在 agent prompt 中提供完整上下文：任务描述、相关文件路径、用户的具体要求。

等待设计师返回初稿，呈现给用户审阅。

使用 AskUserQuestion 询问用户：
- "初稿满意，进入审查"
- "需要修改，列出修改点"
- "跳过审查，直接采用"

### Phase 2: 并行审查

根据任务分级，并行 spawn 审查员 agent：
- `dialogue-reviewer`（对话类必选）
- `player-simulator`（推理体验类必选）
- `timeline-auditor`（跨 Loop 任务必选）
- `consistency-checker`（配置表任务必选）

每个审查员在 prompt 中提供：初稿内容路径、相关 state 文件路径。

等待所有审查员返回报告。

### Phase 3: 内容总监汇总

spawn `content-director` agent，提供：
- 初稿摘要
- 所有审查报告全文
- 用户的原始要求

content-director 输出：
- 终稿修改建议（FAIL 必修 / WARNING 建议改）
- 评分汇总表

呈现给用户，使用 AskUserQuestion：
- "采纳全部修改建议"
- "采纳部分修改（指定哪些）"
- "不修改，保持原稿"

### Phase 4: 执行修改（可选）

如用户确认修改，再次 spawn 对应设计师执行修改。
修改完成后可选再跑一轮审查。
