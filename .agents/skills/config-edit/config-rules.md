# config-edit 规则手册（skill 自带，仅适用本工程编辑器表）

> 本手册是 `config-edit` skill 的判断依据。语义层浓缩自 `D:\NDC\.claude\rules\config-table-language-rules.md`，结构层浓缩自 `D:\NDC\.claude\rules\config-tables.md`，并补充本工程新建的设计期表/字段。**改表前先读相关段。**

## 0. 数据源（唯一目标，别改别处）

- **只改** `D:\NDC_project\avg_editor_v2\data\table\*.json`（编辑器表，16 张）。
- **绝不改** `D:\NDC\Assets\table`（Unity 运行时）、`res/xls`、`preview_new2/data/table`（旧预览）。
- 编辑器表 = Unity 真表的镜像 + 设计期外挂字段；改完即在编辑器生效，不需要打表。
- 改前必做：对目标文件 `copy` 一份 `.bak.{时间戳}`。

## 1. 表清单与主键

| 表 | 主键 | 性质 |
|---|---|---|
| ChapterConfig | id | 游戏数据 |
| SceneConfig | sceneId | 游戏数据 + 设计期(loop/isOpen) |
| ItemStaticData | id | 游戏数据 + 设计期(obtainMethod) |
| NPCStaticData | id | 游戏数据 + 设计期(ArtRequirement) |
| NPCLoopData | id | 游戏数据 |
| Talk | id | 游戏数据（**改对白走 AVG 管线，不在本 skill**）|
| Testimony | id | 游戏数据 |
| TestimonyItem | id | 游戏数据 |
| DoubtConfig | id | 游戏数据 |
| ExposeData | id | 游戏数据 |
| LocationConfig | id | 游戏数据 |
| ChapterStepConfig / DayTimeConfig / GameFlowConfig / MapConfig | id/day/chapterId/id | 外围 |
| **ArtAssetConfig** | id(底图路径) | **设计期新表**（美术资源总览）|

废弃别碰：Event / ExposeTalk / Task / TaskConfig / TimeLineEvent / UITextConfig。

## 2. 跨表外键关系图（改一处必连带检查）

```
ItemStaticData.id  ←  SceneConfig.ItemIDs[]
                   ←  ExposeData.item[]
                   ←  DoubtConfig.condition[type=Item].param
                   ←  ItemStaticData.{analysedEvidence, beforeAnalysedEvidence, combineParameter[]}（自引用）
TestimonyItem.id   ←  Testimony.evidenceItem[]
                   ←  ExposeData.testimony
                   ←  DoubtConfig.condition[type=Testimony/Timeline/Relation].param
NPCStaticData.id   ←  NPCLoopData.NPC / SceneConfig.NPCInfos[].NPC / Talk.Speaker
                   ←  ChapterConfig.exposeNpcId / GameFlowConfig.deceased
SceneConfig.sceneId←  ChapterConfig.initScene / ChapterConfig.map2Scenes[] / DayTimeConfig.day
LocationConfig.id  ←  SceneConfig.location
backgroundImage    ←  ArtAssetConfig.id（新）；SceneConfig.location.backgroundImage
Talk.id            ←  ChapterConfig.initTalk / ExposeData.talkId / NPCLoopData.TalkInfo·LoopTalkInfo / Talk.next
```

**连带规则**：
- 删/改某条的主键 → 上面所有"被引用"处必须同步改或确认仍有效。
- 改 ItemStaticData 的语义类型(itemType) → 检查它在疑点/指证里的用法是否还成立。
- 改 SceneConfig 的 backgroundImage → 对应底图换了，ArtAssetConfig 那条(sceneKind/events/美术需求)是否还对应。

## 3. ID 编码

- Scene `{unit}{loop}{loc}` 4 位：1101=U1L1，2206=U2L2。
- Item 4 位：11XX=U1L1，17XX=分析后证据，18XX=门/道具；6 位(110XXX)=装饰。
- NPC 3 位：101 Zack…；Unit2=2XX。
- Doubt `{unit}{loop}{seq}`：1101。
- TestimonyItem 7 位 `{NPC3}{loop1}{seq3}`：1031002。
- Talk 9 位 `{NPC3}{组3}{句3}` 或指证 6 位 `{loop2}{seq4}`。

## 4. 各表可改字段（白名单，超出的要先确认）

- SceneConfig：note、loop、isOpen、（location 内联只读，改背景图须同步 ArtAssetConfig）
- ItemStaticData：Name、itemType、Describe、ShortDescribe、location、ArtRequirement、obtainMethod、canAnalyzed、canCombined、iconPath、folderPath
- NPCStaticData：Name、role、Chapter、ArtRequirement
- ChapterConfig：chapterTitle、chapterBrief、chapterGoal、summary*、newDoubt*、ArtRequirement
- DoubtConfig：text、condition（改 condition 牵连外键，慎重）
- TestimonyItem：testimony、truth、shortDesc、shortTruth、testimonyType、triggerType、triggerParam
- Testimony：words、chapter
- ExposeData：testimony、item、talkId（牵连外键，慎重）
- **ArtAssetConfig**：Name、displayName、sceneKind、ArtRequirement、events、category

## 5. 设计期新表/字段（本工程独有，Unity 没有）

### ArtAssetConfig（底图/美术资源总览，按底图去重）
| 字段 | 含义 |
|---|---|
| id | 底图资源全路径（主键），如 `Art\Scene\Backgrounds\EPI02\SC2105_bg_...` |
| Name | 中文名 |
| displayName | 纯文件名（美术提交用，可复制）|
| category | `scene_bg`（背景底图）|
| sceneKind | `explore`(探索/AVG) / `dialogue`(对话)。**一张底图只一种**；探索优先（被任一场景当探索用即归 explore）|
| ArtRequirement | 底图美术需求文本 |
| events[] | 内嵌的突发事件 / 特殊 AVG / 需要美术表演的人物进出场：`{name 事件名, resName 首格预名称, loop, req 分格需求}` |
| exposeReuseLoops[] | 该底图复用为哪些 Loop 的指证场景（空=非指证复用）|

- **指证场景不单建底图**：指证复用某个探索/AVG 场景的底图，不改它的 sceneKind，只在 `exposeReuseLoops` 里列出复用的 Loop（如赌场夜 `[5]` = L5 Vinnie 指证场）。Unit2 六轮指证复用底图：L1 警局 / L2 银行大厅 / L3 贵宾室 / L4 Frank厕所 / L5 赌场夜 / L6 Leonard住所。

- NPC 立绘"预名称"**不存这里**，由 `SceneConfig.NPCInfos[].ResPath/ClickResPath` 实时反查显示。
- 突发事件**不单开条目**，作为它发生那张底图的 `events` 子项。
#### ArtAssetConfig.events[] 写法
`events[]` 是美术/演出需求索引，不是运行时事件表。每条 event 必须能回答：发生在哪张底图、哪个 Loop、怎么触发、挂到哪段 Talk、产出什么。

必填/推荐字段：
- `name`：事件名，建议含 Loop + 核心动作，如 `L5 炉锅沸溢 → James 口音暴露`。
- `resName`：美术首格/首张资源预名称，只写文件基名，不写扩展名；多格用 `_01 ... _NN` 约定。
- `loop`：实际发生 Loop，按剧情发生点填，不按资源命名猜。
- `req`：完整需求文本，至少包含：Loop / 场景、类型、触发条件、叙事作用、在场角色、音效、台词/挂点、产出物。

`req` 推荐结构：
```
**美术资产**：`xxx_01.png` ... `_NN.png`

Loop / 场景：L? / 场景名或 sceneId
类型：突发事件 / 强制剧情 / 点击触发 / 对话中触发 / 指证后坦白 / 人物入场 / 人物退场
触发条件：玩家点击什么，或 Talk 哪句出现时触发，或哪个剧情段结束后触发
Talk 挂点：文件名 + Talk id / 首句文本（若未确定，写“待挂点”）
叙事作用：这段事件解决或抛出什么信息
产出：获得/展示/预曝光的 Item/Testimony/Doubt；没有则写“无”
在场角色：Zack、NPC...
音效：...
台词参考：...
```

#### 突发事件归属规则
- 事件挂在**实际发生画面的底图**下面，不按对白文件名、不按谁触发来挂。
- 点击场景物件触发（柜子、电话、抽屉、炉锅等）→ 挂在该物件所在探索场景底图。
- 对话中突然触发（锅溢出、车灯亮、电话铃等）→ 挂在当时 Talk 画面所在底图。
- 指证后坦白 / post-expose AVG → 若是完整 AVG 场景图，挂在该指证后场景底图；若复用指证底图，在 `exposeReuseLoops` 和 `events[]` 里同时说明。
- 仅作为普通证据图标、背包道具、可交互道具子物品的美术需求，不放 `events[]`；放 `ItemStaticData.ArtRequirement`。
- 全屏背景图和 comic 叠图要分清：首张若是铺底全屏图，应作为底图/特殊场景；后续分镜才写在 event 的资源链里。

#### 人物进出场与 Talk 脚本
人物进出场的运行时逻辑在 Talk 新增脚本中，`ArtAssetConfig.events[]` 只记录“需要美术/演出资源的入退场”。普通入退场没有额外表演资源时，不需要新增 event。

Talk 脚本参数规则：
- `new_npc_in`
  - `Parameters[0].ParameterInt` = `NPCLoopData.id`
  - `Parameters[0].ParameterStr` = 入场提示文本，空则不显示
  - `Parameters[1].ParameterStr` = 提示文本位置，格式 `x,y`，anchoredPosition；空则不处理
- `npc_out`
  - `Parameters[0].ParameterInt` = `NPCStaticData.id`

配置/审核入退场时必须检查：
- 入场 NPC 是否存在对应 `NPCLoopData`，且 `NPC` 指向正确 `NPCStaticData.id`。
- `NPCLoopData.ResPath/ClickResPath` 是否对应这个 Loop 的立绘，不要把 L3 立绘挂到 L4。
- Talk 挂点是否在正确场景、正确 Loop、正确剧情时刻；入场/退场脚本是“该 Talk 节点出现时触发”。
- 如果入场同时改变场景可点击 NPC，检查 `SceneConfig.NPCInfos[]` 是否需要补对应实例。
- 入场提示文本是拟声/短促喊话/情绪提示（如 `Wait!`、`Riiing...`），不是系统说明；位置只写坐标，不写描述。
- 退场只传 NPC id；如果同一场景存在同 NPC 多个实例，需先确认运行时是否支持区分，否则不要盲配。

### SceneConfig 设计期字段
- `loop`：场景归属哪个 Loop（一个场景=一个 Loop；多数可由 sceneId 第 2 位推得，但 10xx 开篇/AVG 场景例外，以本字段为准）。
- `isOpen`：该场景在其 Loop 内是否开放给玩家（布尔）。

## 6. 语义判断要点（来自语言规则，最常踩）

- 信息是"看到的物" → Item；"听到的话" → Testimony+TestimonyItem。
- 改 `ItemStaticData` 的 `itemType`、英文内部名、资源名或 `ArtRequirement` 时，必须同时读 `evidence-rules.md`：`clue` / `item` / `envir` 分类、`envir` 不进背包且不配 icon、英文名带类型前缀均以该文件为准。
- 疑点归属 = 道具/证词**被发现**的 Loop，不是被指证使用的 Loop。
- NPC 对话 `get` 给的普通物品**默认不进疑点 condition**；但指证要用的证词谎言 / 关键证词材料必须进入对应 Loop 的疑点或碎片条件。自由探索点到的证据通常进疑点；指证后才获得、或纯展示的内容不进前置疑点。
- 时间线证词：`shortDesc`/`shortTruth` **不写时间前缀**（如 `[22:00]`），时间由 `TestimonyItem.triggerParam = NPCID,日期代码,开始时间,结束时间` 渲染；`TimeLineEvent` 若存在只做兼容校验，不作为必配表。
- chapterGoal 写悬疑问句，不写穿谜底。
- 点击只触发对白的物件用 `itemType=talk`，不要伪装成 NPC。
- 同一语义不要既配高亮证词又配普通证词（案情分析会重复）。

## 7. 校验闸门

改前后必跑 `validate.py`（基线对比，只拦新增破坏）：
```
改前: python validate.py --save .ce_baseline.json
改后: python validate.py --compare .ce_baseline.json   # 新增 ERROR → 退出码 1 → 回滚
```
历史欠债（既有断链）不阻断，但若改动**修复**或**新增**断链都会报告。


