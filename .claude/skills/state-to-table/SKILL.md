---
name: state-to-table
description: "把一个 Unit 的 state YAML（loop1-6）落地到 preview_new2/data/table/ 下的预览版配置表 JSON。三段式：LLM 写临时 MD → py 脚本 dry-run → py 脚本写入。覆盖 6 张活跃表（DoubtConfig / ItemStaticData / NPCStaticData / SceneConfig / Testimony / TestimonyItem）+ ChapterConfig 部分写入。"
argument-hint: "[Unit 编号或 state 目录路径；可选：--tables 表名清单]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

把 Unit 的 state YAML 翻译成预览版配置表 JSON。**目标：`preview_new2/data/table/*.json`**（preview 端 11 张表的子集，结构跟 Unity 真表不完全一致，preview 是给前端展示用的视图）。

> **范围说明**：preview 端只有 11 张表，缺 LocationConfig / NPCLoopData / DayTimeConfig / GameFlowConfig / MapConfig 等 5 张 Unity 端独有表。本 skill 不补——这些表的对齐由独立的 preview→Unity 同步流程负责。SceneConfig 字段平铺、NPCInfos 内联 NPCLoopData 也是 preview 现状，本 skill 沿用。

## 设计原则：LLM 不直接写 JSON

为避免 LLM 全表重写出格式错误、丢条目、字段漂移，严格三段：

| 阶段 | 谁干 | 输入 | 输出 |
|---|---|---|---|
| Phase 1 | **LLM**（按本 SKILL 推断手册） | state YAML + Unit 大纲 | 临时 MD（每 Loop 一份） |
| Phase 2 | **py 脚本**（[preview_new2/table_md_to_json.py](../../../preview_new2/table_md_to_json.py)） | 临时 MD | 解析 → 与现表合并、按 ID 排序、写文件、json.load 自校验 |
| Phase 3 | **LLM** | 校验通过后 | 删临时 MD、给用户最终 diff 摘要 |

**LLM 完全不写 JSON**。py 脚本完全不做业务推断（推断规则只在本 SKILL 手册里）。

## 适用场景

- 一个 Unit 的 6 个 state 文件已定稿，需要落地到 preview 配置表
- 单个 state 改了，按 ID 段更新
- **不适用**：state 还没定稿（先走 `/team-loop` 或 `/unit-state-generator`）

## 输入约定

| 必需 | 说明 |
|------|------|
| Unit 编号 或 state 路径 | 如 `Unit3` 或 `剧情设计/Unit3/state/` |

可选：
- `--tables ItemStaticData,DoubtConfig,...`：限定只跑指定表

如 argument 没给 Unit，用 AskUserQuestion 问。**不假设默认 Unit。**

## 处理范围

### 完全写入（6 张表）

| 表 | state 数据源 |
|---|---|
| ItemStaticData | `scenes[].evidence[]`（含派生证据） |
| NPCStaticData | NPC 块的基础信息（仅本 Unit 首次出现的 NPC） |
| SceneConfig | `scenes[]` + `scenes[].npcs.*`（NPC 实例内联到 NPCInfos）|
| DoubtConfig | `doubts[]`（含字符串/结构化两种格式） |
| TestimonyItem | NPC 块的 `testimony_ids` + 证词内容 |
| Testimony | NPC 块的证词原文（evidenceItem 内联 TestimonyItem 对象） |

### 部分写入（1 张表）

| 表 | 写入字段 | 跳过字段（py 脚本保留原值或留空） |
|---|---|---|
| ChapterConfig | `id` / `initScene` / `doubts` / `topBg` / `bottomBg` | `initTalk` / `exposeNpcId` / `exposes` / `suspectVideoPos` / `suspectTalkPos` / `zackTalkPos` |

### 完全跳过

| 表 | 原因 |
|---|---|
| Talk | 由 `AVG/对话配置工作及草稿/sync_to_json.py` 处理 |
| ExposeData / ExposeConfig / ExposeTalk | 用户明确排除（指证系列） |

### NPCInfos / Talk 字段的处理

SceneConfig.NPCInfos 内联了完整 NPC + TalkInfo + LoopTalkInfo 对象：

- **NPC** 子对象：本 skill 填写（基于 NPCStaticData）
- **TalkInfo / LoopTalkInfo** 子对象：本 skill **写空对象 `{}` 或保留原值**——由 sync_to_json 后续填充
- **ResPath / ClickResPath**：本 skill 推断填写
- **PosX / Posy / PosZ**：本 skill 写空字符串（待美术补）

合并策略：如某 sceneId 在表中已有 NPCInfos 且 TalkInfo 非空，py 脚本**保留原 TalkInfo**，只覆盖本 skill 关心的字段（NPC / ResPath / Position）。

## Phase 1: LLM 写临时 MD

### 临时 MD 存放

`preview_new2/data/_table_drafts/Unit{N}/Loop{N}.md`

每 Loop 一份，与 state 文件一一对应。Phase 3 写入成功后自动清理；失败时保留以供手修。

### MD 格式规范（py 脚本依赖此格式解析）

```markdown
# Unit{N} Loop{N} - 配置表草稿

## ItemStaticData

### 3101 - 着地点照片 / Landing Spot Photo
- itemType: 1
- canAnalyzed: false
- canCombined: false
- Describe: |
    案发现场尸体距墙仅 0.8 米，主动跳跃应 ≥1.5 米——无水平初速度。
- ShortDescribe: 着地点照片
- location: Thomas公寓楼下现场 / ThomasBuildingDownstairs
- Chapter: EPI03
- folderPath: EPI03\ThomasBuildingDownstairs
- desSpritePath: SC3001_item_01_big
- mapSpritePath: SC3001_item_01
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

## SceneConfig

### 3101 - Thomas公寓楼下现场 / ThomasBuildingDownstairs
- sceneType: 1
- backgroundImage: Art\Scene\Backgrounds\EPI03\SC3001_bg_ThomasBuildingDownstairs
- backgroundMusic: 待补充
- ItemIDs: [3101, 3108]
- NPCInfos:
  - npc_ref: 301
    instance_id: 30101
    ResPath: Art\Scene\NPC\EPI03\SC3104_npc_Morrison1
    ClickResPath: Art\Scene\NPC\EPI03\SC3104_npc_Morrison2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）

## TestimonyItem

### 3101001 - Morrison 自述结案
- testimonyType: 1
- testimony: 自杀，很明显。这种烂酒鬼，喝多了自己跳下去了。
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
- Chapter: EPI03
- condition:
  - {type: 1, param: 3104}
  - {type: 3, param: 3101001}

### 9201 - Jimmy 很缺钱（碎片示例）
- text: Jimmy 很缺钱（碎片）
- Chapter: EPI09
- isFragment: true
- condition:
  - {type: 3, param: 9021001}

## ChapterConfig (部分写入)

### 301
- initScene: 3117
- doubts_ref: [3001, 3002]
- topBg: Art/Scene/Expose/epi03/top_morrison
- bottomBg: Art/Scene/Expose/epi03/morrison
- _skip_fields: [initTalk, exposeNpcId, exposes, suspectVideoPos, suspectTalkPos, zackTalkPos]
```

### MD 字段语法约定（py 脚本依赖）

- **表名**：`## {TableName}`，必须与 preview JSON 文件名一致
- **条目**：`### {id} - {可读描述}`
- **字段**：`- {key}: {value}`
- **多行字符串**：`- {key}: |` + 缩进续行
- **数组**：`- {key}: [a, b, c]`
- **结构化数组**（如 condition）：`- condition:` + 缩进 `- {type: X, param: Y}`
- **嵌套对象数组**（如 NPCInfos）：`- NPCInfos:` + 缩进 `- key: value`
- **跳过字段**：值写 `待补充` 或 `待补充（说明）` → py 脚本翻译为空字符串/不写
- **跨条目引用**：`{key}_ref: {id}` 或 `{key}_refs: [id, id]` → py 脚本展开成完整内联对象
- **部分写入标记**：`_skip_fields: [...]` → py 脚本保留 table 中原值（条目存在）或留空（新增）

## LLM 推断规则手册

> 全部字段规范见 [docs/配置表详解.md](../../../docs/配置表详解.md)（注意 docs 描述的是 Unity 真表，preview 字段子集见上）。
>
> 原则：**能推就推，推不出就写"待补充"**。py 脚本对"待补充"的处理是统一的。

### ID 段推断

| 表 | ID 公式 |
|---|---|
| ItemStaticData | 4 位，`{unit}{loop}{xx}`，派生证据 `{unit}7{xx}` |
| NPCStaticData | 3 位，`{unit}{xx}`（如 Unit3 → 301-310） |
| SceneConfig | 4 位，`{unit}{loop}{location}`，物理 ID 转：`int(f"{unit}{loop}{physical_id % 100:02d}")` |
| TestimonyItem | 7 位，`{loop}{npc_code}{seq}` |
| Testimony | 与 TestimonyItem 同段（容器 ID） |
| DoubtConfig | 4 位，`{unit}{loop}{seq}` |
| ChapterConfig | 3 位 `{unit}0{loop}`（看现有约定：EPI01 是 101/102/103…） |
| NPCInfos.instance_id（嵌入 SceneConfig） | 4 位 `{npc_seq}{loop}{seq:02d}`，先扫现表确认约定 |

### 字段推断（按表）

#### ItemStaticData

| 字段 | 推断 |
|---|---|
| Name | `[中文名, 英文名]`，英文名查 Unit 美术参考；查不到 `["xxx", "待补充"]` |
| itemType | name/note 关键词推：照片/痕迹/脚印 → 1 (clue)；瓶/钥匙/文件/票据/笔记/烟斗 → 3 (item)；门 → 5；上楼梯 → 8；下楼梯 → 9；纯装饰 → 0；环境叙事 → 2 |
| canAnalyzed | 若有派生证据指向（state/note 提到"分析后..."）→ true，否则 false |
| analysedEvidence | 派生证据 ID（如有），否则不写 key |
| beforeAnalysedEvidence | 派生证据反向指回（如有），否则不写 key |
| canCombined / combineParameter | state 标注合成则填，否则 false / 不写 combineParameter key |
| Describe | `note` 字段去掉 `关键——` / `陷阱——` / `伏笔——` / `场景道具` 前缀；可结合 evidence 上下文扩展 |
| ShortDescribe | 同 Describe 但截短 |
| location | `[scenes[].name, 英文场景名]` |
| Chapter | `EPI0{N}` |
| folderPath | `EPI0{N}\\{location_en}` |
| desSpritePath | `SC{sceneId}_item_{后两位}_big`（sceneId 用本 Loop 转换后的） |
| mapSpritePath | `SC{sceneId}_item_{后两位}` |
| iconPath | 不写（或 ""），除非 state 明示 |
| Position / ArtRequirement | `待补充（美术）` |

#### NPCStaticData

| 字段 | 推断 |
|---|---|
| Name | `[中文全名, 英文全名]` |
| role | `1`=死者 / `2`=is_liar 为 true 或 motive 含犯罪动机 / `3`=证人 / `4`=主角（Zack/Emma） |
| Chapter | `EPI0{N}` |
| IconSmall / IconLarge | `{name_lower}_small` / `{name_lower}_big`；主角/幕后角色不写这两字段 |

> **跨 Unit 已存在的 NPC**（如 Zack）：LLM 不要写进 MD。py 脚本看到 MD 里没有就不动。

#### SceneConfig（注意 preview 字段平铺，不是 Unity 的 location 子对象）

| 字段 | 推断 |
|---|---|
| sceneId | 物理 ID 按 Loop 转换 |
| sceneName | `scenes[].name` 中文部分 |
| sceneNameEn | 英文场景名 |
| sceneType | `"1"` (dialogue) 默认；指证场景 `"2"`；过场 `"3"` |
| backgroundImage | `Art\\Scene\\Backgrounds\\EPI0{N}\\SC{sceneId}_bg_{en_name}` |
| backgroundMusic | `待补充` |
| ItemIDs | `scenes[].evidence[].id` 字符串数组 |
| NPCInfos | 数组，每元素含 `npc_ref / instance_id / ResPath / ClickResPath / PosX / Posy / PosZ`；TalkInfo / LoopTalkInfo 由 py 脚本写空对象 `{}` 或保留原值 |
| note | 不写或 `""` |

#### DoubtConfig

| 字段 | 推断 |
|---|---|
| text | `doubts[].text` |
| Chapter | `EPI0{N}` |
| isFragment | 可选，布尔。state 中 `doubts[].is_fragment: true` → 写 `true`；缺省/false → 不写该字段（反序列化默认 false）。碎片的 condition 通常只有 1 条 |
| condition | 解析 `unlock_condition`：<br>**新格式**（结构化数组）→ 直接复制<br>**旧格式**（字符串 `item:xxx + testimony:yyy`）→ `+` 分隔，每段：`item:xxx` → `{type: 1}`；`relation:xxx` → `{type: 2}`；`testimony:xxx` 或 `timeline:xxx` → `{type: 3}` |

#### TestimonyItem

| 字段 | 推断 |
|---|---|
| testimonyType | `1` 自述（NPC 谈自己） / `2` 见闻（NPC 谈他人） |
| testimony | `[中文摘要, 英文摘要]`；从 state 的 `# ⚠谎言: "xxx"` 注释或对话草稿提取；找不到 `待补充` |
| triggerType | `0` 无条件 / `1` 时间线 / `2` 关系网 |
| triggerParam | `"NPCID,sceneId,startTime,endTime"`（时间线）/ `"NPCID1,NPCID2"`（关系网）/ `"NPCID"`（无条件） |

> preview 端 TestimonyItem 不含 `truth / shortTruth / shortDesc`（这些是 Unity 端独有），本 skill 不写。

#### Testimony（preview 端简化版）

| 字段 | 推断 |
|---|---|
| npc | NPCStaticData 内联对象（py 脚本展开） |
| chapter | ChapterConfig.id（如 `"301"`） |
| words | `[中文证词全文, 英文证词全文]`；从对话草稿合并 `<special>` 标记 |
| evidenceItem | TestimonyItem 内联对象数组（如有；preview 端 evidenceItem 字段非必填） |

#### ChapterConfig（部分写入）

| 字段 | 推断 |
|---|---|
| id | `{unit}0{loop}` 或 `{unit}{loop}`（按 EPI01 现有约定 → `101`-`106`，EPI03 应为 `301`-`306`） |
| initScene | 该 Loop 的 opening 场景 ID |
| doubts | DoubtConfig 内联对象数组（py 展开 doubts_ref） |
| topBg | `Art/Scene/Expose/epi0{N}/top_{npc_lower}` |
| bottomBg | `Art/Scene/Expose/epi0{N}/{npc_lower}` |
| _skip_fields | `[initTalk, exposeNpcId, exposes, suspectVideoPos, suspectTalkPos, zackTalkPos]` |

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
4. 扫一眼现有 `preview_new2/data/table/*.json`：了解本 Unit 段已有哪些条目（用于差异说明）
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
   - 留白字段清单（"PosX/Posy 留空 N 处, backgroundMusic 留空 N 处..."）
   - MD 文件路径列表（让用户能手改）
2. AskUserQuestion：
   - "MD 看起来 OK，跑 dry-run"
   - "我先手改一下 MD"
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
   - 跳过字段清单
   - 后续手动步骤提示：
     - Talk → `python AVG/对话配置工作及草稿/sync_to_json.py`
     - Unity 同步 → 独立流程（preview → Unity 转换）

## 不要做的事

- **不要直接写 / 编辑 `preview_new2/data/table/*.json`**：所有写入走 py 脚本
- **不要重写 Talk / Expose 系列表**
- **不要碰其他 Unit 的条目**：py 脚本按 ID 段过滤
- **不要凭空补 Position / 美术资源路径**：state 没的就写 `待补充`
- **不要在没 dry-run + 用户确认的情况下直接跑写入**
- **不要假设默认 Unit**
- **不要修改 `_all_tables.xlsx`**
- **不要在脚本失败时清理 MD**
- **不要尝试生成 LocationConfig / NPCLoopData / DayTimeConfig / GameFlowConfig / MapConfig**：preview 端没有这 5 张表，本 skill 不补
- **不要写 truth / shortDesc / shortTruth / color** 等 Unity 端独有字段

## 与现有脚本的关系

- `preview_new2/state_to_preview*.py`：生成 `preview_new2/data/Unit{N}/*.yaml`（前端流程图用）+ 也会追加 table。本 skill 与之**互不重叠**——本 skill 只管 `table/*.json` 的写入；如要更新 Unit{N}/yaml，仍走原 py。
- `AVG/对话配置工作及草稿/sync_to_json.py`：维护 Talk + ExposeTalk 的对话内容。本 skill 在 SceneConfig.NPCInfos 里写空 TalkInfo，等 sync_to_json 后续填。

## 后续步骤（不在本 skill 范围）

1. Talk 配置：`python AVG/对话配置工作及草稿/sync_to_json.py`
2. 指证（Expose）：手动或专用 skill
4. preview → Unity 同步：独立流程（含字段映射 + 拆表 + Unity-flavored JSON 输出）
5. `_all_tables.xlsx` 同步：手动
