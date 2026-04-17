---
name: team-dialogue
description: "从用户指定的 state 文件出发，并行生成整个 Loop 的对话草稿（Talk + Expose），并过一轮审查汇总。用于 state 已定稿，只需补全对话的场景。"
argument-hint: "[state 文件或目录路径；可选：知识池路径、人物设计目录]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

编排"State → 对话草稿"的端到端流程。前提：state 文件已定稿。本 skill 只负责对话（Talk + Expose）生成与审查，不动证据/指证/state 设计本身。

## 适用场景

- state 文件已经通过 `team-loop` 或 `unit-state-generator` 生成并确认
- 只想要整个 Loop 的对话草稿 MD，不想重新跑证据/指证设计
- 对话改动较大，需要整 Loop 重写（小修单 NPC 用 `/team-design`）

## 输入约定

本 skill **完全由用户提供的路径驱动**，不假设任何默认目录。用户通过 argument 或后续对话告知：

| 必需 | 说明 |
|------|------|
| state 路径 | 单个 `loop{N}_state.yaml` 文件，或包含多个 state 的目录（此时会按 loop 顺序逐个处理） |
| 知识池路径 | `npc_knowledge_pools.yaml`（通常一个 Unit 共用一份） |
| 人物设计目录 | 包含 `{npc_name}.md` 的目录 |

**解析顺序：**

1. 如果 argument 直接给了路径，按给的用
2. 如果 argument 只给了 state 路径，先尝试在 state 同目录 / 上级目录找 `npc_knowledge_pools.yaml` 和 `characters/`
3. 上述都没找到，用 AskUserQuestion 问用户："知识池和人物设计在哪？"——**不要自己猜路径，不要默认回退到 `AVG/对话配置工作及草稿/前置配置/`**

## 前置检查

读到 state 后必须确认：

1. state 文件可解析（YAML 合法）
2. state 里出现的 NPC 名单，每个都能在知识池里找到对应条目
3. state 里出现的 NPC 名单，每个都能在人物设计目录里找到对应 `{npc_name}.md`

**任何一项缺失都停下来**，用 AskUserQuestion 列出缺失的 NPC/文件，问用户：
- "这些 NPC 的人物设计/知识池在哪里？"
- 或"跳过这些 NPC，只处理已有资料的"（用户选择时才降级）

不要硬跑、不要用占位人设。

## Pipeline

### Phase 1: State 拆解与方案确认

先读 state 文件，提取：

- 本 Loop 涉及的 NPC 列表（Talk 场景）
- Expose 场景清单（哪些 NPC 触发指证、对应 ExposeID）
- Opening 需求（硬切场景数量、是否有鉴赏力 source/quiz）
- 平行场景隔离约束（哪些场景之间不能互相引用）

输出一份"对话生成方案"摘要（不写文件，直接呈现）：
- 计划并行的 dialogue-writer 数量与各自负责的 NPC
- 计划复用/新写的 Expose 节点
- 鉴赏力 source/quiz 的初步分布（仅标记位置，详细设计由 connoisseur-designer 或后续 `/team-loop` Phase 5 补）

使用 AskUserQuestion 让用户确认：
- "方案 OK，开始生成"
- "调整分工（用户指定）"
- "取消"

### Phase 2: 并行对话生成

**2a. Talk 部分** — 按 NPC 并行 spawn 多个 `dialogue-writer` agent：

每个 agent prompt 必须包含：
- 本 Loop state 文件路径（用户指定的那个，必读）
- 负责的 NPC 名称
- 该 NPC 的人物设计路径（用户指定目录下的 `{npc}.md`）+ 知识池路径（用户指定的那份）
- 平行场景隔离约束（哪些场景/信息不能在本 NPC 对话里出现）
- 产出路径：临时文件 `AVG/对话配置工作及草稿/生成草稿/.temp_Loop{N}_{npc}.md`（避免多 agent 同时写同一文件冲突；如用户指定了其他输出目录则用用户的）

**2b. Expose 部分** — 若本 Loop 有指证场景：
- state 里指证方案已定稿 → spawn `dialogue-writer` 写指证对话（多层谎言递进格式）
- state 里指证方案缺失或不完整 → 停下来提示用户"此 Loop 需先跑 `/team-expose`"，不要自己补指证设计

### Phase 3: 合并与格式化

所有并行 agent 返回后，lead（你自己）负责合并：

1. 按场景顺序把各 NPC 的临时草稿拼进主文件 `AVG/对话配置工作及草稿/生成草稿/Loop{N}_生成草稿.md`
2. 按 `AVG对话配置规则.md` 的 MD 格式规范统一字段、分隔符、ID 前缀
3. 清理临时文件
4. 对话 ID 冲突校验：9 位 ID 全局唯一
5. 把合并后的草稿路径呈现给用户

### Phase 4: 并行审查

并行 spawn 3 个审查员（对话类默认配置）：

- `dialogue-reviewer`：12 项对话质量清单评分
- `consistency-checker`：证据物理属性、NPC 陈述、ID 编码一致性
- `timeline-auditor`：跨 Loop 信息泄露、证据权限时序

每个审查员 prompt 中必须提供：
- 草稿路径：`AVG/对话配置工作及草稿/生成草稿/Loop{N}_生成草稿.md`
- state 文件路径
- 本 Loop 所在 Unit 的大纲/设计文档路径

**player-simulator 不纳入默认审查**（它是完整体验审计，更适合在 Loop 全部组件就绪后跑 `/playthrough-audit`）。如用户显式要求，再加入。

### Phase 5: 内容总监汇总

spawn `content-director` agent，输入：
- 草稿路径
- 3 份审查报告全文
- Phase 1 的方案摘要
- 用户原始要求

输出：
- FAIL 必修清单 + WARNING 建议改清单
- 综合评分表

使用 AskUserQuestion：
- "采纳全部修改"
- "采纳部分（用户指定）"
- "保持原稿"

### Phase 6: 执行修改（可选）

若用户选择修改：
- 按 NPC 维度再次 spawn `dialogue-writer`，只改涉及的 NPC
- 修改后可选再跑一轮 Phase 4 审查（用户决定）

## 产出清单

| 文件 | 路径 | 说明 |
|------|------|------|
| 对话草稿 | `AVG/对话配置工作及草稿/生成草稿/Loop{N}_生成草稿.md` | 主产物 |
| 审查报告（可选保留） | `AVG/对话配置工作及草稿/生成草稿/Loop{N}_审查报告.md` | content-director 汇总版，用户要求时才写 |

## 后续手动步骤（本 skill 不做）

1. 对话草稿 → AVG JSON：`python sync_to_json.py Loop{N}_生成草稿.md`（Phase 2，用户触发）
2. 鉴赏力 source/quiz 的 ID 配对：走 `/connoisseur` 或 `team-loop` Phase 5
3. State → 配置表 JSON：`python preview_new2/state_to_preview.py`

## 不要做的事

- **不要重新设计证据/指证/state**：本 skill 假设 state 已定稿，有争议就停下来让用户先走上游流程
- **不要并行写同一个主文件**：多个 dialogue-writer 用临时文件隔离，最后由 lead 合并
- **不要自动同步 JSON**：严格遵守 Phase 1/Phase 2 两阶段分离，JSON 必须用户明确触发
- **不要跳过前置检查**：state / 知识池 / 人物设计缺一不可
