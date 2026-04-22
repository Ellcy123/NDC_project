---
name: state-to-table
description: "把一个 Unit 的 state YAML（loop1-6）落地到 preview_new2/data/table/ 下的配置表 JSON。三段式：LLM 写临时 MD → py 脚本 dry-run → py 脚本写入。覆盖除 Talk / Expose 以外的 16 张活跃表。"
argument-hint: "[Unit 编号或 state 目录路径；可选：--tables 表名清单]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

把 Unit 的 state YAML 翻译成游戏配置表 JSON。**只覆盖非 Talk / Expose 的活跃表**——Talk 由 `sync_to_json.py` 处理，Expose 系列由用户排除。

## 设计原则：LLM 不直接写 JSON

为了避免 LLM 全表重写出格式错误、丢条目、字段漂移，本 skill 严格三段：

| 阶段 | 谁干 | 输入 | 输出 |
|---|---|---|---|
| Phase 1 | **LLM**（按本 SKILL 的推断手册） | state YAML + Unit 大纲 | 临时 MD（每 Loop 一份） |
| Phase 2 | **py 脚本**（[preview_new2/table_md_to_json.py](../../../preview_new2/table_md_to_json.py)） | 临时 MD | JSON 条目数组 → 与现表合并、按 ID 排序、写文件、json.load 自校验 |
| Phase 3 | **LLM** | 校验通过的报告 | 删临时 MD、给用户最终 diff 摘要 |

**LLM 完全不写 JSON**。py 脚本完全不做业务推断（推断规则只在本 SKILL 手册里）。

## 适用场景

- 一个 Unit 的 6 个 state 文件已定稿，需要落地到 `preview_new2/data/table/*.json`
- 单个 state 改了，需要按 ID 段更新
- **不适用**：state 还没定稿（先走 `/team-loop` 或 `/unit-state-generator`）

## 输入约定

| 必需 | 说明 |
|------|------|
| Unit 编号 或 state 路径 | 如 `Unit3` 或 `剧情设计/Unit3/state/` |

可选：
- `--tables ItemStaticData,DoubtConfig,...`：限定只跑指定表

如 argument 没给 Unit，用 AskUserQuestion 问。**不假设默认 Unit。**

## 处理范围

### 完全写入（11 张表）

| 表 | state 数据源 |
|---|---|
| ItemStaticData | `scenes[].evidence[]`（含派生证据） |
| NPCStaticData | NPC 块的基础信息（仅本 Unit 首次出现的 NPC） |
| LocationConfig | `scenes[].name` + 美术参考 |
| SceneConfig | `scenes[]`（不含 Talk 字段） |
| NPCLoopData | `scenes[].npcs.*` 实例（TalkInfo / LoopTalkInfo 留空） |
| DoubtConfig | `doubts[]`（含字符串/结构化两种格式） |
| TestimonyItem | NPC 块的 `testimony_ids` + 证词内容 |
| Testimony | NPC 块的证词原文（evidenceItem 引用 TestimonyItem ID） |
| DayTimeConfig | state 文件头部注释的时间 |
| MapConfig | 跨 Unit 共享，按需新增 |
| GameFlowConfig | Unit 大纲（章节名、loopCount、死者、开篇视频） |

### 部分写入（1 张表）

| 表 | 写入字段 | 跳过字段（py 脚本保留原值或留空） |
|---|---|---|
| ChapterConfig | `id` / `initScene` / `doubts` / `topBg` / `bottomBg` | `initTalk` / `exposeNpcId` / `exposes` |

### 完全跳过

| 表 | 原因 |
|---|---|
| Talk | 由 `AVG/对话配置工作及草稿/sync_to_json.py` 处理 |
| ExposeData / ExposeConfig / ExposeTalk | 用户明确排除 |
| ChapterStepConfig | 空表，预留未用 |

## Phase 1: LLM 写临时 MD

### 临时 MD 存放

`preview_new2/data/_table_drafts/Unit{N}/Loop{N}.md`

每个 Loop 一份，与 state 文件一一对应。完成后 Phase 3 自动清理。

### MD 格式规范（py 脚本依赖此格式解析）

```markdown
# Unit{N} Loop{N} - 配置表草稿

## ItemStaticData

### 3101 - 着地点照片 / Landing Spot Photo
- itemType: 1
- canAnalyzed: false
- analysedEvidence: ""
- beforeAnalysedEvidence: ""
- canCombined: false
- combineParameter: []
- Describe: |
    案发现场尸体距墙仅 0.8 米，主动跳跃应 ≥1.5 米——无水平初速度。
- ShortDescribe: 着地点照片
- location: Thomas公寓楼下现场 / ThomasBuildingDownstairs
- Chapter: EPI03
- folderPath: EPI03\ThomasBuildingDownstairs
- desSpritePath: SC3001_item_01_big
- mapSpritePath: SC3001_item_01
- iconPath: ""
- Position: 待补充（美术）
- ArtRequirement: 待补充（美术）

### 3104 - 女性脚印照片 / Women Footprint Photo
- itemType: 1
- ...

## NPCStaticData

### 301 - Morrison / Morrison
- role: 2
- Chapter: EPI03
- IconSmall: morrison_small
- IconLarge: morrison_big
- color: 待补充

## LocationConfig

### 301 - Thomas公寓楼下现场 / ThomasBuildingDownstairs
- sceneType: 1
- backgroundImage: Art\Scene\Backgrounds\EPI03\SC3001_bg_ThomasBuildingDownstairs
- ambientSound: 待补充

## SceneConfig

### 3101 - Thomas公寓楼下现场
- location_ref: 301
- backgroundMusic: 待补充
- unlockCondition: ""
- NPCInfos_ref: []
- ItemIDs: [3101, 3108]
- note: ""

## NPCLoopData

### 30101 - Morrison @ SC3104
- npc_ref: 301
- TalkInfo: 待补充（Talk 由 sync_to_json 维护）
- LoopTalkInfo: 待补充（Talk 由 sync_to_json 维护）
- ResPath: Art\Scene\NPC\EPI03\SC3104_npc_Morrison1
- ClickResPath: Art\Scene\NPC\EPI03\SC3104_npc_Morrison2
- PosX: 待补充（美术）
- PosY: 待补充（美术）
- PosZ: 待补充（美术）

## TestimonyItem

### 3101001 - Morrison 自述结案
- testimonyType: 1
- testimony: |
    自杀，很明显。这种烂酒鬼，喝多了自己跳下去了。
- testimony_en: 待补充
- triggerType: 0
- triggerParam: "301"

## Testimony

### 3101001 - Morrison 完整证词
- npc_ref: 301
- chapter: 301
- words: |
    <special=1>自杀</special>，很明显。这种<special=2>烂酒鬼</special>，喝多了自己跳下去了。
- words_en: 待补充
- evidenceItem_refs: [3101001]

## DoubtConfig

### 3001 - 楼顶不只Thomas一个人
- text: 楼顶不只Thomas一个人——女性脚印与Thomas面对面站在护栏边
- condition:
  - {type: 1, param: 3104}
  - {type: 3, param: 3101001}

## ChapterConfig (部分写入)

### 301
- initScene: 3117
- doubts_ref: [3001, 3002]
- topBg: Art/Scene/Expose/epi03/top_morrison
- bottomBg: Art/Scene/Expose/epi03/morrison
- _skip_fields: [initTalk, exposeNpcId, exposes]

## DayTimeConfig

### 3101
- startTime: 0800
- endTime: 0900

## MapConfig

### 待补充

## GameFlowConfig

### 3
- loopCount: 6
- chapterName: 待补充
- openingVideo: 待补充
- deceased_ref: 309
```

### MD 字段语法约定（py 脚本依赖）

- **表名**：`## {TableName}`，必须与 docs/配置表详解.md 表名一致
- **条目**：`### {id} - {可读描述}`，id 必须能解析为字符串
- **字段**：`- {key}: {value}`
- **多行字符串**：`- {key}: |` + 缩进续行
- **数组**：`- {key}: [a, b, c]` 或多行 `-` 缩进
- **结构化数组**：`- condition:` + 缩进 `- {type: X, param: Y}`
- **跳过字段**：值写 `待补充` 或 `待补充（说明）` → py 脚本翻译为空字符串/空数组
- **跨条目引用**：`{key}_ref: {id}` 或 `{key}_refs: [id, id]` → py 脚本展开成完整内联对象（依据 docs 中"内联存储"约定）
- **部分写入标记**：`_skip_fields: [...]` → py 脚本保留 table 中原值（条目存在）或留空（新增）

## LLM 推断规则手册

> 全部字段规范见 [docs/配置表详解.md](../../../docs/配置表详解.md)。本节列出 LLM 写 MD 时如何**推断**字段值。
>
> 原则：**能推就推，推不出就写"待补充"**。py 脚本对"待补充"的处理是统一的（→ 空字符串/空数组），不要写 null 或假值。

### ID 段推断（按 Unit 编号）

| 表 | ID 公式 |
|---|---|
| ItemStaticData | 4 位，`{unit}{loop}{xx}`，派生证据 `{unit}7{xx}` |
| NPCStaticData | 3 位，`{unit}{xx}`（如 Unit3 → 301-310） |
| LocationConfig | 看现有约定（EPI01=1xx，EPI02=2xxx；EPI03 段需先扫现有数据确认） |
| SceneConfig | 4 位，`{unit}{loop}{location}`，物理 ID 转：`int(f"{unit}{loop}{physical_id % 100:02d}")` |
| NPCLoopData | 5 位，`{npc_id}{loop}{seq:02d}` |
| TestimonyItem | 7 位，`{loop}{npc_code}{seq}` |
| Testimony | 与 TestimonyItem 同段（容器 ID） |
| DoubtConfig | 4 位，`{unit}{loop}{seq}` |
| ChapterConfig | `{unit}0{loop}` 或 `{unit}{loop}`（先扫现表确认约定） |
| DayTimeConfig | 用 sceneId 作 day |
| GameFlowConfig | chapterId = unit |

### 字段推断

#### ItemStaticData

| 字段 | 推断方式 |
|---|---|
| Name | `[中文名, 英文名]`，英文名查 Unit 美术参考文档；查不到 `["xxx", "待补充"]` |
| itemType | name/note 关键词推：照片/痕迹/脚印 → 1 (clue)；瓶/钥匙/文件/票据/笔记/烟斗 → 3 (item)；门 → 5；上楼梯 → 8；下楼梯 → 9；纯装饰 → 0；环境叙事 → 2 |
| canAnalyzed | 若有派生证据指向（state 或 note 提到"分析后..."）→ true，否则 false |
| analysedEvidence | 派生证据 ID（如有），否则空字符串 |
| beforeAnalysedEvidence | 派生证据反向指回（如有） |
| canCombined / combineParameter | state 标注合成则填，否则 false / 空数组 |
| Describe | `note` 字段去掉 `关键——` / `陷阱——` / `伏笔——` / `场景道具` 前缀；如 note 太短可结合 evidence 上下文扩展 |
| ShortDescribe | 同 Describe 但截短 |
| location | `[scenes[].name, 英文场景名]`，英文名查 Unit 美术参考；查不到写 `["xxx", "待补充"]` |
| Chapter | `EPI0{N}` |
| folderPath | `EPI0{N}\\{location_en}` |
| desSpritePath | `SC{sceneId}_item_{后两位}_big`（sceneId 用本 Loop 转换后的） |
| mapSpritePath | `SC{sceneId}_item_{后两位}` |
| iconPath | 空字符串（除非 state 明示） |
| Position / ArtRequirement | `待补充（美术）` |

#### NPCStaticData

| 字段 | 推断 |
|---|---|
| Name | `[中文全名, 英文全名]` |
| role | `1`=死者（Unit 大纲指明）/ `2`=is_liar 为 true 或 motive 含犯罪动机 / `3`=证人 / `4`=主角（Zack/Emma） |
| Chapter | `EPI0{N}` |
| IconSmall / IconLarge | `{name_lower}_small` / `{name_lower}_big` |
| color | `待补充` |

**已存在则在 MD 里仍要写完整条目**——py 脚本会按 ID 比对，相同 ID 字段不同时按 MD 为准；完全相同则跳过。如要避免动跨 Unit NPC，LLM 不要把它们写进 MD。

#### LocationConfig

| 字段 | 推断 |
|---|---|
| Name | `[scenes[].name, 英文场景名]` |
| sceneType | `1` (dialogue) 默认；指证场景查 ChapterConfig 引用判断；过场 `3` |
| backgroundImage | `Art\\Scene\\Backgrounds\\EPI0{N}\\SC{sceneId}_bg_{en_name}` |
| ambientSound | `待补充` |

#### SceneConfig

| 字段 | 推断 |
|---|---|
| sceneId | 物理 ID 按 Loop 转换 |
| location_ref | LocationConfig.id（py 脚本展开成内联对象） |
| backgroundMusic | `待补充` |
| unlockCondition | state 注释中的"🔒尚未发现 xxx" |
| NPCInfos_ref | NPCLoopData.id 数组（py 脚本展开） |
| ItemIDs | `scenes[].evidence[].id` 字符串数组 |
| note | 空字符串 |

#### NPCLoopData

| 字段 | 推断 |
|---|---|
| npc_ref | NPCStaticData.id（py 脚本展开） |
| TalkInfo / LoopTalkInfo | `待补充（Talk 由 sync_to_json 维护）` → py 脚本写 `{}` 或保留原值 |
| ResPath | `Art\\Scene\\NPC\\EPI0{N}\\SC{sceneId}_npc_{name}1` |
| ClickResPath | 同上但末尾 `2` |
| PosX / PosY / PosZ | `待补充（美术）` |

#### DoubtConfig

| 字段 | 推断 |
|---|---|
| text | `doubts[].text` |
| condition | 解析 `unlock_condition`：<br>**新格式**（结构化数组）→ 直接复制<br>**旧格式**（字符串 `item:xxx + testimony:yyy`）→ `+` 分隔，每段：`item:xxx` → `{type: 1, param: "xxx"}`；`relation:xxx` → `{type: 2}`；`testimony:xxx` 或 `timeline:xxx` → `{type: 3}` |

#### TestimonyItem / Testimony

| 字段 | 推断 |
|---|---|
| testimonyType | `1` 自述（NPC 谈自己） / `2` 见闻（NPC 谈他人）—— 看 `testimony_ids` 注释 |
| testimony / words | 从 state 的 `# ⚠谎言: "xxx"` 注释或对话草稿提取；找不到 `待补充` |
| testimony_en / words_en | `待补充` |
| triggerType | `0` 无条件 / `1` 时间线 / `2` 关系网 |
| triggerParam | 见 [docs §3.8](../../../docs/配置表详解.md) 格式 |

#### ChapterConfig（部分写入）

| 字段 | 推断 |
|---|---|
| initScene | 该 Loop 的 opening 场景 ID |
| doubts_ref | DoubtConfig.id 列表 |
| topBg / bottomBg | `Art/Scene/Expose/epi0{N}/top_{npc_lower}` / `Art/Scene/Expose/epi0{N}/{npc_lower}` |
| _skip_fields | `[initTalk, exposeNpcId, exposes]` |

#### DayTimeConfig / GameFlowConfig / MapConfig

| 表 | 推断 |
|---|---|
| DayTimeConfig | state 头部"时间: 1928年11月21日 约08:00" → day=sceneId, startTime/endTime=HHMM |
| GameFlowConfig | Unit 大纲取 chapterName / loopCount / openingVideo / deceased_ref |
| MapConfig | 仅当 state 提到新地图点（Unit 大纲中的 location 列表）时新增；否则 `### 待补充`（py 脚本跳过本表） |

## 旧 / 新 state 格式兼容

| 字段 | EPI01(Unit2) 旧格式 | EPI02+ / Unit8+ 新格式 |
|---|---|---|
| NPC 知识块 | `knows` / `does_not_know` / `lie` | `active_topics` / `withheld_topics` |
| `doubts.unlock_condition` | 字符串 | 结构化数组 |
| `evidence` 子字段 | `id` / `name` / `note` | 增补 `type` / `pickup` / `analysis` / `description` |

LLM 在 Phase 1 自动识别两种格式都吃下；写 MD 时统一成新格式。详见 [.claude/rules/state.md](../../rules/state.md)。

## 工作流

### Phase 1: 扫描 + 写临时 MD

1. 解析 argument 取 Unit 编号；没给就 AskUserQuestion 问
2. 读 Unit 大纲（如 `剧情设计/Unit{N}/Unit{N}_大纲*.md`）
3. 顺序读 6 个 `loop{1-6}_state.yaml`
4. 扫一眼现有 `preview_new2/data/table/*.json`：了解本 Unit 段已有哪些条目（用于差异说明，不影响 MD 内容）
5. 自动检测 state 格式版本（旧字符串 / 新结构化）
6. **逐 Loop 生成 MD**：写到 `preview_new2/data/_table_drafts/Unit{N}/Loop{N}.md`
   - 按本 SKILL 的"推断规则手册"填字段
   - 不确定的字段一律写 `待补充` 或 `待补充（说明）`，绝不假数据
7. **前置自检**（任一失败 → AskUserQuestion 停下）：
   - state YAML 全部可解析
   - 所有 evidence ID 落在 Unit 段内
   - 派生证据 `analysedEvidence` / `beforeAnalysedEvidence` 双向一致
   - DoubtConfig 引用的 testimony / item ID 都已在本次写入或表中已存在

### Phase 2: 第一道用户确认 → dry-run

1. 输出"Phase 1 摘要"：
   - 各表条目数（6 个 Loop 合计）
   - 留白字段清单（"PosX/PosY 留空 N 处，色值留空 N 处..."）
   - MD 文件路径列表（让用户能手改）
2. AskUserQuestion：
   - "MD 看起来 OK，跑 dry-run"
   - "我先手改一下 MD（用户改完再回来跑）"
   - "取消"
3. 跑 `python preview_new2/table_md_to_json.py Unit{N} --dry-run`
4. 把脚本的 dry-run 报告（每张表新增/更新条数 + ID 列表）原样呈现

### Phase 3: 第二道用户确认 → 实际写入

AskUserQuestion：
- "确认写入"
- "再调 MD"
- "取消"

写入：
1. `python preview_new2/table_md_to_json.py Unit{N}`
2. 检查脚本退出码与 stderr：
   - 成功：继续
   - 失败：把错误原样呈现给用户，停下，**不要清理 MD**（让用户能修）
3. 成功后清理：删 `preview_new2/data/_table_drafts/Unit{N}/`
4. 输出最终报告：
   - 各表写入条数
   - 跳过字段清单（"ChapterConfig.initTalk 留空待 sync_to_json 补，共 6 处"）
   - 后续手动步骤提示：
     - Talk → `python AVG/对话配置工作及草稿/sync_to_json.py`
     - 鉴赏力 / Expose → 对应 skill 或手动
     - `_all_tables.xlsx` 由用户手动同步

## 不要做的事

- **不要直接写 / 编辑 `preview_new2/data/table/*.json`**：所有写入走 py 脚本
- **不要重写 Talk / Expose 系列表**
- **不要碰其他 Unit 的条目**：py 脚本按 ID 段过滤，跨 Unit 数据原样保留
- **不要凭空补 Position / 美术资源路径**：state 没的就写 `待补充`
- **不要在没 dry-run + 用户确认的情况下直接跑写入命令**
- **不要假设默认 Unit**：argument 没给就 AskUserQuestion 问
- **不要修改 `_all_tables.xlsx`**：用户手动同步
- **不要在脚本失败时清理 MD**：保留临时文件，让用户能手修

## 与现有脚本的关系

- `preview_new2/state_to_preview*.py`：生成 `preview_new2/data/Unit{N}/*.yaml`（前端流程图用），也会追加 table——本 skill 与之**互不重叠且不替代**。如要更新 Unit{N}/yaml，仍走原 py。本 skill 只管 `table/*.json`。
- 如未来要统一，可让 py 脚本同时吐 Unit{N}/yaml + table/json，但本 skill 当前不承担。

## 后续步骤（不在本 skill 范围）

1. Talk 配置：`python AVG/对话配置工作及草稿/sync_to_json.py`
2. 指证（Expose）：手动或专用 skill
3. 鉴赏力节点：暂未纳入配置表
4. `_all_tables.xlsx` 同步：手动
5. 同步到 Unity 工程：`copy /Y "preview_new2\data\table\*.json" "D:\NDC\Assets\table\"`
