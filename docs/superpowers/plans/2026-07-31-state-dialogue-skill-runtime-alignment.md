# State 与对白 Skill 运行时对齐实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修正 State 与对白生成 skill，使大纲事件、Opening 场景流、对白连续性和 Unity 实际入口机制保持一致。

**Architecture:** `unit-state-generator` 负责建立 active outline 覆盖矩阵、连续性合同和设计期到运行时的映射；`team-dialogue` 消费这些合同，按场景包写作并逐接缝审查。Unity 细节集中放入 skill reference，正式配置仍遵守 `D:\NDC` 的 Excel-first 工作流。

**Tech Stack:** Markdown skills、YAML State 合同、Unity C# 运行时语义、Luban XML Schema、Git、Codex subagent forward-test。

## Global Constraints

- 每个 Loop 只有一个根级 `opening` 流程；可含多个按场景或事件命名的 `sequence` Talk。
- active outline 是内容事实最高权威；讨论结论不能无批准地新增、删除、移动或改序事件。
- `ChapterConfig.initTalk` 是 Loop 开篇根入口；NPC `TalkInfo/LoopTalkInfo` 只用于玩家点击。
- 跨场强制 Opening 默认用 `DialogueAction.change_scene + Talk.next` 续接，并避免重复配置目标 `firstEnterTalk`。
- State 中的 continuity、coverage 和 runtime mapping 均为设计期合同，不直接写入 Unity 正式表。
- 正式 Unity 表以 `D:\NDC\res\xls/*.xlsx` 为源，经 `Translate.exe` 生成 JSON 与 bytes。
- 本计划不修改 Unit4 State、Unit4 validator、Unity C#、Unity Excel 或生成表。

---

### Task 1: 固化 Unity Opening 运行时合同

**Files:**
- Create: `.agents/skills/unit-state-generator/references/unity-opening-runtime-contract.md`
- Modify: `.agents/skills/unit-state-generator/SKILL.md`

**Interfaces:**
- Consumes: `canon_manifest.json`、active outline、Unity `ChapterConfig/SceneConfig/NPCLoopInfo/Talk` schema 与运行时代码。
- Produces: State 生成者可执行的 Opening Schema、权威顺序、覆盖矩阵和运行时映射规则。

- [x] **Step 1: 记录旧 skill 的失败基线**

使用现有 U4 L3/L5 产物与只读基线 agent 结果确认：旧 skill 允许按人物嵌套 Opening、允许讨论结论覆盖大纲、没有逐事件覆盖矩阵，并允许在 `firstEnterTalk` 与 `Talk.next` 之间自由选择而没有稳定默认。

- [x] **Step 2: 编写 Unity 运行时参考**

参考文件必须明确：

```text
ChapterConfig.initTalk = Loop 根入口
SceneConfig.firstEnterTalk = 场景首次进入一次性入口
NPCLoopData.TalkInfo/LoopTalkInfo = 玩家点击 NPC 入口
change_scene.Parameters[0] = 目标 sceneId
change_scene.next = 跨场续接 Talk
next > 0 时运行时 skipFirstEnter
```

并区分设计期字段、预览字段和 Unity 正式字段。

- [x] **Step 3: 修改 State 生成流程**

加入：

```yaml
opening:
  type: cutscene_sequence
  runtime_root:
    table: ChapterConfig
    init_scene: 4021
    init_talk: L3_opening_broken_call
  sequence:
    - event_id: broken_call
      talk: L3_opening_broken_call
      scene_id: 4021
      cast: [Zack, Emma, Harold]
      required_beats: []
      runtime_exit:
        action: change_scene
        target_scene_id: 4022
        continuation: next_talk
        next_talk: L3_opening_mansion_arrival
  player_control_restored_after: mansion_arrival
```

并加入 outline coverage matrix、`narrative_continuity.units`、deviation approval gate、Opening/自由探索职责分离和 Unity mapping review。

- [x] **Step 4: 静态验证**

运行：

```powershell
rg -n "active outline|outline coverage|opening.sequence|runtime_root|narrative_continuity|change_scene|TalkInfo|LoopTalkInfo" .agents/skills/unit-state-generator
```

预期：所有关键合同可检索，且不再声明“讨论结论是唯一权威”或“优先照 Unit3 State 结构”。

### Task 2: 将对白流水线改为场景包与全接缝审查

**Files:**
- Modify: `.agents/skills/team-dialogue/SKILL.md`

**Interfaces:**
- Consumes: `opening.sequence[]`、`narrative_continuity.units`、前序实际对白和人物档案。
- Produces: 按完整场景 treatment 生成、按明确切点拆文件、逐接缝审查的对白流程。

- [x] **Step 1: 修改 Canon 与命名输入**

删除 Unit9/Unit10 独立章节的过时描述；一律从 Manifest 解析 canonical Unit、active outline、AVG 目录和 ID 空间。

- [x] **Step 2: 扩展 Phase 0 深读包**

新增：

```text
整章认知/情绪主轴
场景包清单
场景接缝账本
伏笔/回收账本
动态人物状态表
前序实际对白摘要
```

- [x] **Step 3: 修改派发与写作粒度**

Opening 文件从 `opening.sequence[].talk` 读取；Phase 1 从“每 NPC Talk”改为“每场景包”。同一连续场景先写完整 treatment，再按 State 指定的 Talk 切点拆分。

- [x] **Step 4: 修改审查门禁**

把随机抽查两段改为全部相邻接缝逐一检查；重复询问、重复进场、遗忘前一段承诺或物件、没有消费既有压力和产生状态变化均判 FAIL。

- [x] **Step 5: 静态验证**

运行：

```powershell
rg -n "opening.sequence|场景包|场景接缝账本|伏笔/回收账本|动态人物状态|逐接缝|Unit9 / Unit10" .agents/skills/team-dialogue/SKILL.md
```

预期：新结构存在，过时章节判断不存在。

### Task 3: 同步命名与转场规则

**Files:**
- Modify: `AVG/对话配置工作及草稿/AVG对话配置规则.md`
- Modify: `.agents/skills/config-edit/pitfalls.md`

**Interfaces:**
- Consumes: State Opening 命名和 Unity `change_scene + next` 运行时事实。
- Produces: 与两个 skill 一致的文件命名和配置交接规则。

- [x] **Step 1: 修改 Opening 命名**

把：

```text
L{Loop}_{phase}_{npc}
L1_opening_mickey
```

改为 Opening 专用的：

```text
L{Loop}_opening_{scene_or_event}
L3_opening_broken_call
L3_opening_mansion_arrival
```

普通探索仍保留 `L{Loop}_scene{sceneId}_{npc}`。

- [x] **Step 2: 修正过时转场说明**

把“change_scene 不能硬 next”改成：

```text
强制跨场连续段使用 change_scene + next；
next > 0 时目标 firstEnterTalk 会被跳过；
不得同时用 next 和目标 firstEnterTalk 承载同一剧情拍。
```

- [x] **Step 3: 静态验证**

运行：

```powershell
rg -n "opening_\\{scene_or_event\\}|opening_mickey|change_scene.*next|firstEnterTalk" AVG/对话配置工作及草稿/AVG对话配置规则.md .agents/skills/config-edit/pitfalls.md
```

预期：Opening 示例按事件命名，旧的绝对禁令不存在。

### Task 4: Skill 结构与行为验证

**Files:**
- Verify: `.agents/skills/unit-state-generator/`
- Verify: `.agents/skills/team-dialogue/`

**Interfaces:**
- Consumes: Task 1–3 的最终文件。
- Produces: 静态校验结果与 fresh-context forward-test 报告。

- [x] **Step 1: 运行 skill frontmatter 校验**

运行 `skill-creator/scripts/quick_validate.py` 分别校验两个 skill 目录；如果现有项目扩展 frontmatter 与官方校验器不兼容，记录具体错误，并以 YAML 可解析、name/description 存在及项目运行时兼容作为补充验证。

- [x] **Step 2: 运行内容契约扫描**

确认：

```text
无“讨论结论是唯一权威”
无“Unit9 / Unit10 是独立新章节”
无人物命名 Opening 正面示例
存在一个根 Opening、多 sequence、场景包和逐接缝规则
存在 Unity Excel-first 边界
```

- [x] **Step 3: 运行 fresh-context forward-test**

给独立 state-architect 只提供修订后 skill、Manifest、U4 active outline 和 Unity runtime schema/code，要求输出 L3 Opening 最小 State。验收：

```text
一个 opening 根
至少两个 scene/event Talk
Talk 不按人物命名
Mickey 到场强制拍不进入 scenes[].npcs
ChapterConfig.initTalk 为根入口
跨场使用 change_scene + next
无大纲外新增 NPC/地点
存在逐事件 coverage 与 continuity handoff
```

- [x] **Step 4: 检查 Git diff**

运行：

```powershell
git diff --check
git diff --stat
git status --short
```

确认只出现计划内文件及原有无关未跟踪目录。
