---
name: state-to-table
description: "把一个 Unit 的 state YAML（loop1-6）增量合并到 preview_new2/data/table/ 下的配置表 JSON。覆盖除 Talk / Expose 以外的全部活跃表。LLM 驱动，逐表 dry-run 后写入。"
argument-hint: "[Unit 编号或 state 目录路径；可选：--dry-run / --tables 表名清单]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion
---

把 Unit 的 state YAML 翻译成游戏配置表 JSON。**只覆盖非 Talk / Expose 的活跃表**——Talk 由 `sync_to_json.py` 处理，Expose 系列由用户排除。

## 适用场景

- 一个 Unit 的 6 个 state 文件已定稿，需要把内容落地到 `preview_new2/data/table/*.json`
- 单个 state 改了（增了证据、改了疑点、调了场景），需要按 ID 段更新
- **不适用**：state 还没定稿、要重新设计证据/疑点（先走 `/team-loop` 或 `/unit-state-generator`）

## 输入约定

| 必需 | 说明 |
|------|------|
| state 路径 | `剧情设计/Unit{N}/state/`（含 loop1-6_state.yaml）或单个 loop 文件 |
| Unit 编号 | 决定 ID 段（Unit3 = 3xxx 证据 / 31xx-36xx 场景 / 1031xxx 等） |

可选：
- `--dry-run`：只输出计划，不写文件
- `--tables ItemStaticData,DoubtConfig,...`：限定只跑指定表（默认全跑）

如 argument 没给 Unit 或路径，用 AskUserQuestion 问。**不假设默认 Unit。**

## 处理范围

### 完全写入（11 张表）

| 表 | state 数据源 |
|---|---|
| ItemStaticData | `scenes[].evidence[]`（含派生证据 `analysedEvidence`） |
| NPCStaticData | NPC 块（仅本 Unit 首次出现的 NPC，已存在则跳过） |
| LocationConfig | `scenes[].name` + 美术参考文档（背景图路径） |
| SceneConfig | `scenes[]`（不含 Talk 字段） |
| NPCLoopData | `scenes[].npcs.*` 实例（**TalkInfo / LoopTalkInfo 留空**——Talk 由 sync_to_json 维护） |
| DoubtConfig | `doubts[]`（含字符串/结构化两种格式） |
| TestimonyItem | NPC 块的 `testimony_ids` + 证词内容（取 7 位 ID） |
| Testimony | NPC 块的证词原文（**evidenceItem 引用 TestimonyItem ID**） |
| DayTimeConfig | state 文件头部注释的时间 |
| MapConfig | 跨 Unit 共享，按需新增地图点 |
| GameFlowConfig | Unit 大纲（章节名、loopCount、死者、开篇视频） |

### 部分写入（1 张表）

| 表 | 写入字段 | 跳过字段（保留原值或留空） |
|---|---|---|
| ChapterConfig | `id` / `initScene` / `doubts` / `topBg` / `bottomBg` | `initTalk` / `exposeNpcId` / `exposes` |

### 完全跳过

| 表 | 原因 |
|---|---|
| Talk | 由 `AVG/对话配置工作及草稿/sync_to_json.py` 处理 |
| ExposeData / ExposeConfig / ExposeTalk | 用户明确排除（指证系列） |
| ChapterStepConfig | 空表，预留未用 |

## 字段映射手册

> 全部字段规范以 [docs/配置表详解.md](../../../docs/配置表详解.md) 为准。本节列出 state → JSON 的映射要点，遇到歧义查上述文档。

> **JSON 编码约定**：所有数字字段在 JSON 里都是字符串（`"id": "3101"`、`"itemType": "3"`），不是 int。

### ItemStaticData

| JSON 字段 | 来源 | 说明 |
|---|---|---|
| id | `evidence[].id` | 4 位，Unit3 = 31xx-36xx，派生 = 37xx |
| Name | `evidence[].name` + 英文（state 通常无英文，留空字符串数组 `["xxx", ""]`，待人工补） |
| itemType | 推断：默认 `"3"` (item)；门 `"5"`；楼梯 `"8"/"9"`；装饰 `"0"`；线索（拍照取证）`"1"`；环境叙事 `"2"`。从 note 关键词 + 设计文档判断，不确定时问用户 |
| canAnalyzed | 若有派生证据指向它则 `"true"` |
| analysedEvidence | 派生证据 ID（如有） |
| beforeAnalysedEvidence | 反向：派生证据指回原物 |
| canCombined | 若 state 中标注合成关系则 `"true"` |
| combineParameter | 合成原料 ID 列表 |
| Describe / ShortDescribe | `note` 字段拆解：去掉 `关键——` / `陷阱——` / `伏笔——` 前缀作为描述；不确定时问用户 |
| location | `scenes[].name`（中英对） |
| Chapter | `EPI0{N}`（Unit3 → EPI03） |
| folderPath | `EPI0{N}\\{场景英文名}`（按现有约定） |
| desSpritePath / mapSpritePath | `SC{sceneId}_item_{后两位}_big` / `SC{sceneId}_item_{后两位}` |
| Position / ArtRequirement | state 不含——留空字符串 / 留空，标注"待美术补" |

### NPCStaticData

| JSON 字段 | 来源 |
|---|---|
| id | NPC 编码（Unit3 → 3xx；新增 NPC 时按 docs/枚举速查表 排号） |
| Name | `[中文名, 英文名]` |
| role | `1`=死者 / `2`=嫌疑人(is_liar 或 motive 含动机) / `3`=证人 / `4`=主角 |
| Chapter | `EPI0{N}` |
| IconSmall / IconLarge | `{name}_small` / `{name}_big` |
| color | 设计文档或问用户 |

**已存在则跳过**——NPC 表跨 Unit 共享，不要覆盖已有条目。

### LocationConfig

| JSON 字段 | 来源 |
|---|---|
| id | sceneId 的第 3-4 位（如 SC3001 → location id `301`） |
| Name | `scenes[].name`（中英对） |
| sceneType | `"1"` (dialogue) 默认；指证场景 `"2"`；过场 `"3"` —— 按 docs/枚举速查表 |
| backgroundImage | `Art\\Scene\\Backgrounds\\EPI0{N}\\SC{...}_bg_{name}` |
| ambientSound | 留空 |

### SceneConfig

| JSON 字段 | 来源 |
|---|---|
| sceneId | `scenes[].id`（4 位 `{unit}{loop}{location}`，state 中可能是物理 ID 3001，需按 loop 转成 3101/3201/...） |
| location | LocationConfig 内联对象（**冗余存储**） |
| backgroundMusic | 留空或 `"test"` |
| unlockCondition | 解锁条件文本（state 注释中的"🔒尚未发现 xxx"） |
| NPCInfos | `scenes[].npcs.*` → NPCLoopData 内联对象数组 |
| ItemIDs | `scenes[].evidence[].id` 字符串数组 |
| note | 留空 |

> **场景 ID 转换**：state 文件里通常用物理 ID（3001、3002…），写入 SceneConfig 时按本 Loop 转换：`scene_id = int(f"{unit}{loop}{physical_id % 100:02d}")`。同一物理场景在不同 Loop 是不同的 sceneId。

### NPCLoopData

| JSON 字段 | 来源 |
|---|---|
| id | `{npc_id}{loop}{seq:02d}`（如 NPC 301 在 Loop1 第 1 个实例 → 30101） |
| NPC | NPCStaticData 内联对象 |
| TalkInfo | **留空对象 `{}` 或保留原值** —— 由 sync_to_json 写入 |
| LoopTalkInfo | 同上 |
| ResPath / ClickResPath | `Art\\Scene\\NPC\\EPI0{N}\\SC{sceneId}_npc_{name}1` / `_npc_{name}2` |
| PosX / PosY / PosZ | state 不含——留空，标注"待美术补" |

### DoubtConfig

| JSON 字段 | 来源 |
|---|---|
| id | `doubts[].id`（4 位 `{unit}{loop}{seq}`） |
| condition | `unlock_condition` 解析（见下） |
| text | `doubts[].text` |

**`unlock_condition` 两种格式**：

1. **新格式（Unit8+ 推荐）**：直接是结构化数组，原样写入。
   ```yaml
   unlock_condition:
     - {type: 1, param: "3104"}
     - {type: 3, param: "3101001"}
   ```

2. **旧格式（Unit2 / Unit3）**：字符串，按 `+` 分隔，每段 `{key}:{value}`：
   - `item:xxx` → `{type: "1", param: "xxx"}`
   - `relation:xxx` → `{type: "2", param: "xxx"}`
   - `testimony:xxx` / `timeline:xxx` → `{type: "3", param: "xxx"}`

   ```yaml
   unlock_condition: "item:3104 + testimony:3101001"
   # → [{"type":"1","param":"3104"}, {"type":"3","param":"3101001"}]
   ```

`type` 取值参照 [docs/配置表详解.md §3.9](../../../docs/配置表详解.md)：1=Item / 2=RelationNetwork / 3=Timeline。

### TestimonyItem

| JSON 字段 | 来源 |
|---|---|
| id | `testimony_ids[]`（7 位 `{loop}{npc_code}{seq}`） |
| testimonyType | `"1"` 自述（NPC 谈自己） / `"2"` 见闻（NPC 谈他人）—— 从 state 注释或 NPC 块判断 |
| testimony | `[中文摘要, 英文摘要]`，从 state 的 `# ⚠谎言: "xxx"` 注释或对话草稿提取 |
| triggerType | `0`=无条件 / `1`=时间线 / `2`=关系网 |
| triggerParam | 见 [docs §3.8](../../../docs/配置表详解.md) |

> 若 state 只列了 ID 没给摘要内容，先到对应 Loop 的对话 MD 草稿（`AVG/对话配置工作及草稿/生成草稿/Loop{N}_*.md`）里找该 ID 的 `get` 行；找不到再问用户。

### Testimony

| JSON 字段 | 来源 |
|---|---|
| id | NPC 在该 Loop 的证词容器 ID（与对话 ID 同段） |
| npc | NPCStaticData 内联对象 |
| chapter | ChapterConfig.id（如 `"301"`） |
| words | NPC 完整证词段落（从对话草稿合并 `<special>` 标记） |
| evidenceItem | TestimonyItem 内联对象数组 |

### ChapterConfig（部分写入）

| JSON 字段 | 写入逻辑 |
|---|---|
| id | `{unit}{loop}` 或 `{unit}0{loop}`（看现有数据约定） |
| initScene | 该 Loop 的 opening 场景 ID |
| doubts | 该 Loop 的 DoubtConfig 内联对象数组 |
| topBg / bottomBg | `Art/Scene/Expose/epi0{N}/top_{npc}` / `Art/Scene/Expose/epi0{N}/{npc}` |
| **initTalk / exposeNpcId / exposes** | **如条目已存在 → 保留原值；如新增 → 留空字符串 / 空数组**，并在最终报告里列出"待 sync_to_json / 指证 skill 补全"清单 |

### DayTimeConfig / GameFlowConfig / MapConfig

- **DayTimeConfig**：state 头部注释的"时间: 1928年11月21日 约08:00"提取 day（用 sceneId）+ startTime/endTime（HHMM）。
- **GameFlowConfig**：Unit 大纲取 chapterName / loopCount / openingVideo / deceased。
- **MapConfig**：跨 Unit 共享，本 skill 默认不动；若 state 提到新地图点（Unit 大纲中的 location 列表），追加。

## 工作流

### Phase 1: 扫描 + 字段提取

1. 读 Unit 大纲（如 `剧情设计/Unit{N}/Unit{N}_大纲*.md`）取 chapter 元信息
2. 顺序读 6 个 `loop{1-6}_state.yaml`
3. 按表分类提取数据，构建内存中的"待写条目集合"：
   ```
   {
     "ItemStaticData": [{id, fields...}, ...],
     "DoubtConfig": [...],
     ...
   }
   ```
4. 自动检测 state 格式版本（旧字符串 / 新结构化），分别处理

**前置检查**（任一失败 → AskUserQuestion 停下）：
- state YAML 全部可解析
- 所有 evidence ID 落在 Unit 段内（Unit3 → 3xxx）
- 所有 NPC 在 NPCStaticData 中已存在或可新建
- 派生证据的 `analysedEvidence` 和 `beforeAnalysedEvidence` 必须双向一致
- DoubtConfig 引用的 testimony / item ID 都已在本次提取的集合内或表中已存在

### Phase 2: 计划呈现 + 用户确认

读取 `preview_new2/data/table/*.json` 现有内容，按 ID 段过滤本 Unit 条目，生成对比清单：

| 表 | 新增 | 更新 | 删除 | 不变 |
|---|---|---|---|---|
| ItemStaticData | 12 | 3 | 0 | 88 |
| DoubtConfig | 2 | 1 | 0 | 8 |
| ... | | | | |

**逐表展开"新增/更新"清单**（id + 关键字段差异）。

用 AskUserQuestion：
- "全部确认，写入"
- "只写部分表（用户指定）"
- "停下，我再调 state"

`--dry-run` 模式下停在此步，输出报告。

### Phase 3: 写入

**逐表处理**，每张表三步走：

1. **Read** 当前 `table/{TableName}.json` 全文
2. **构建新数组**：
   - 保留所有非本 Unit 条目（按 ID 段判断）
   - 加入本次提取的新条目
   - 替换有更新的同 ID 条目
   - 按 ID 升序排序
3. **Write** 整张表

> 用 Write 整表覆盖（不用 Edit 单条）的原因：JSON 数组中按位置插入容易破坏格式，整表重写 + ID 排序最稳。但写之前必须确认 Phase 1 的"非本 Unit 条目"完整保留。

**写入顺序**（避免外键悬空）：
1. NPCStaticData → LocationConfig → ItemStaticData（被引用方）
2. TestimonyItem → Testimony
3. NPCLoopData → SceneConfig（引用 NPC + Item）
4. DoubtConfig
5. ChapterConfig（引用 Doubt + Scene）
6. DayTimeConfig / GameFlowConfig / MapConfig（独立表）

**ID 段判断公式**（用于"非本 Unit 条目"过滤）：
- ItemStaticData: `int(id // 1000) == unit`（Unit3 → 3000-3999）
- SceneConfig: `int(str(id)[0]) == unit`
- DoubtConfig: 同上
- LocationConfig: 看现有约定（EPI01=1xx，EPI02=2xxx，需先扫现有数据确认 EPI03 段）
- NPCStaticData: `int(str(id)[0]) == unit`（Unit3 → 3xx）
- TestimonyItem: 7 位 `{loop}{npc}{seq}`，NPC 段在 Unit 内
- ChapterConfig: 前缀 `{unit}` 开头

**冲突处理**：
- 同 ID 但字段不同 → 按本次 state 为准（state 是真理）
- 跨 Unit ID 冲突（不该发生）→ 停下报错

### Phase 4: 报告

写完输出：
- 各表新增/更新条数
- 跳过的字段清单（"PosX/PosY 留空待美术补，共 5 处"）
- ChapterConfig 待补全清单（initTalk / exposeNpcId / exposes）
- 后续手动步骤提示：
  - 跑 `python AVG/对话配置工作及草稿/sync_to_json.py` 同步 Talk
  - `_all_tables.xlsx` 由用户手动同步（本 skill 不动）

## 旧 / 新 state 格式兼容

| 字段 | EPI01(Unit2) 旧格式 | EPI02+ / Unit8+ 新格式 |
|---|---|---|
| NPC 知识块 | `knows` / `does_not_know` / `lie` | `active_topics` / `withheld_topics` |
| `doubts.unlock_condition` | 字符串 `"item:xxx + testimony:yyy"` | 结构化数组 |
| `opening` 子字段 | `scene_id` / `characters` / `purpose` | `type` / `description` |
| `evidence` 子字段 | `id` / `name` / `note` | 增补 `type` / `pickup` / `analysis` / `description` |

**处理原则**：自动识别两种格式都吃下；写入 JSON 时统一成新格式（结构化 condition 等）。详见 [.claude/rules/state.md](../../rules/state.md)。

## 不要做的事

- **不要重写 Talk / Expose 系列表**：这些由其他流程维护，本 skill 严格跳过
- **不要碰其他 Unit 的条目**：按 ID 段过滤，跨 Unit 数据原样保留
- **不要凭空补 Position / 美术资源路径**：state 没的就留空 + 报告里标注，让美术后续填
- **不要在没 dry-run 确认的情况下直接写**：Phase 2 必须出对比清单 + 用户确认
- **不要用 Edit 做单条 JSON 增删**：用 Read 全表 → Write 全表的方式，配合 ID 排序，避免格式破坏
- **不要假设默认 Unit**：argument 没给就 AskUserQuestion 问
- **不要修改 `_all_tables.xlsx`**：用户手动同步

## 后续步骤（不在本 skill 范围）

1. Talk 配置：`python AVG/对话配置工作及草稿/sync_to_json.py`
2. 指证（Expose）配置：手动或专用 skill
3. 鉴赏力节点：暂未纳入配置表
4. `_all_tables.xlsx` 同步：手动
5. 同步到 Unity 工程：手动 copy（CLAUDE.md 描述）
