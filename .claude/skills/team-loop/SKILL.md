---
name: team-loop
description: "编排整个 Loop 的端到端设计：证据 → 指证 → state → 对话 → 全面审查。用于规划整个 Loop。"
argument-hint: "[Loop 标识，如 'Unit3 L5']"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

编排整个 Loop 的端到端设计。这是最大规模的设计任务，涉及 7 个 Phase。

## Pipeline

### Phase 1: 证据体系设计

spawn `evidence-designer` agent：
- 提供：Loop 信息、章节设计文档、已有证据
- 输出：本 Loop 证据体系设计

使用 AskUserQuestion 让用户确认证据方案。

### Phase 2: 指证谜题设计

spawn `expose-designer` agent：
- 提供：证据方案、指证目标 NPC
- 输出：通过质检的指证方案列表

使用 AskUserQuestion 让用户选择方案。

### Phase 3: State 文件生成

spawn `state-architect` agent：
- 提供：确认的证据方案 + 指证方案 + 场景设计
- 输出：完整的 loop{N}_state.yaml

使用 AskUserQuestion 让用户确认 state 文件。

### Phase 4: 对话草稿生成

可按 NPC 并行 spawn 多个 `dialogue-writer` agent：
- 每个 agent 负责一个 NPC 的对话
- 提供：state 文件、该 NPC 的人物设计和知识池

呈现所有对话草稿给用户审阅。

### Phase 5: 全面审查

并行 spawn 4 个审查员：
- `dialogue-reviewer`：对话质量
- `player-simulator`：玩家体验
- `timeline-auditor`：时序一致性
- `consistency-checker`：数据一致性

### Phase 7: 内容总监汇总

spawn `content-director`：
- 输入：所有产出 + 所有审查报告
- 输出：终稿建议 + 全面评分表
