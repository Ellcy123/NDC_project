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
| events[] | 内嵌的突发事件动态漫画：`{name 事件名, resName 首格预名称, loop, req 分格需求}` |
| exposeReuseLoops[] | 该底图复用为哪些 Loop 的指证场景（空=非指证复用）|

- **指证场景不单建底图**：指证复用某个探索/AVG 场景的底图，不改它的 sceneKind，只在 `exposeReuseLoops` 里列出复用的 Loop（如赌场夜 `[5]` = L5 Vinnie 指证场）。Unit2 六轮指证复用底图：L1 警局 / L2 银行大厅 / L3 贵宾室 / L4 Frank厕所 / L5 赌场夜 / L6 Leonard住所。

- NPC 立绘"预名称"**不存这里**，由 `SceneConfig.NPCInfos[].ResPath/ClickResPath` 实时反查显示。
- 突发事件**不单开条目**，作为它发生那张底图的 `events` 子项。

### SceneConfig 设计期字段
- `loop`：场景归属哪个 Loop（一个场景=一个 Loop；多数可由 sceneId 第 2 位推得，但 10xx 开篇/AVG 场景例外，以本字段为准）。
- `isOpen`：该场景在其 Loop 内是否开放给玩家（布尔）。

## 6. 语义判断要点（来自语言规则，最常踩）

- 信息是"看到的物" → Item；"听到的话" → Testimony+TestimonyItem。
- 疑点归属 = 道具/证词**被发现**的 Loop，不是被指证使用的 Loop。
- NPC 对话 `get` 给的物品**默认不进疑点 condition**；自由探索点到的才进。
- 时间线证词：`shortDesc`/`shortTruth` **不写时间前缀**（如 `[22:00]`），时间由 triggerParam + TimeLineEvent 渲染。
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
