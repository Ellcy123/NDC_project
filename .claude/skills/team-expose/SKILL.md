---
name: team-expose
description: "端到端指证设计流程：谜题方案 → state 写入 → 对话生成 → 全面审查。用于完整的指证（Expose）设计。"
argument-hint: "[Loop 和目标，如 'Unit3 L4 指证 Morrison']"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

端到端指证设计流程。这是最复杂的设计任务之一，涉及 5 个 Phase。

## Pipeline

### Phase 1: 谜题方案生成

spawn `expose-designer` agent：
- 提供：Loop 信息、指证目标 NPC、当前章节已有指证设计（避免重复）
- expose-designer 生成多个方案，过 5 层质检
- 只输出通过质检的方案

使用 AskUserQuestion 让用户选择方案。

### Phase 2: State 写入

spawn `state-architect` agent：
- 提供：用户选定的指证方案、现有 state 文件路径
- state-architect 将方案写入 state 文件的 expose 部分
- 更新 evidence、testimony 相关字段

呈现 state 变更给用户确认。

### Phase 3: Expose 对话生成

spawn `dialogue-writer` agent：
- 提供：更新后的 state 文件、人物设计
- dialogue-writer 根据 state 中的 expose 结构生成 Expose 对话草稿

呈现对话草稿给用户审阅。

### Phase 4: 并行审查

同时 spawn 3 个审查员：
- `dialogue-reviewer`：审查指证对话质量
- `player-simulator`：模拟玩家推理体验
- `timeline-auditor`：检查跨 Loop 信息一致性

### Phase 5: 内容总监汇总

spawn `content-director`：
- 汇总所有审查报告
- 输出终稿建议 + 评分表
