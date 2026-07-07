# Unit2 AVG 特殊场景需求

说明：本文件只记录 Unit2 里“纯 AVG 对话/过场场景”和“指证场景背景”的美术语义。它不是自由探索场景清单，也不是 NPC 可点击立绘、证据道具、动态漫画分镜清单。

## 核心规则

- 纯 AVG 场景是一张完整的对话/过场图：人物和场景画在同一张图里，不是空底图加立绘挂载。
- 因此同一个地点，只要在场人物、人物状态、戏剧关系或构图不同，就应该是不同的 AVG 美术需求和不同资产命名。
- 纯 AVG 图可以参考探索底图的地点结构、光线和时代氛围，但不能把探索道具、可点击 NPC、证据挂载写进 AVG 图。
- 自由探索场景才是“底图 + Item / NPC 覆盖”；开篇自动对白、指证后对白一般都应该走纯 AVG 场景。
- ChapterConfig.openingScene 专门给开篇 AVG 使用；initScene 仍然是进入自由探索后的场景。
- 指证阶段目前只使用 topBg；bottomBg 已废弃。topBg 也应当指向对应的指证画面资产，而不是随便借探索场景。
- 突发事件动态漫画另见《Unit2_AVG突发事件动态漫画.md》，这里最多说明事件发生在哪个剧情节点，不展开格数。

## 纯 AVG 场景清单

| Loop | 类型 | SceneId | 资产命名 | 画面人物 | 画面重点 |
|---|---|---:|---|---|---|
| L1 | 开篇纯 AVG | `2191` | `SC2191_avg_Opening_MorrisonBlocksZack` | Morrison、Zack、Emma | Morrison 拦住 Zack，不让他靠近火场和尸体；Zack 急于确认死者身份；Emma 介入，为 Zack 争取进入现场的机会。 |
| L2 | 开篇纯 AVG | `2206` | `SC2206_bg_SacredHeartHospital_MargaretRoom` | Zack、Emma、Mickey、病床上的 Margaret | Margaret 昏迷在病房中，Mickey 带来新的调查方向，Zack/Emma 接上银行与威胁链条。 |
| L2 | 指证后纯 AVG | `2292` | `SC2292_avg_LeonardEnvelope` | Leonard、Zack、Emma；Moore 可按对白远处/侧面暗示 | Leonard 表面配合，递出信封或继续引导 Zack，态度礼貌但带操控感。 |
| L3 | 开篇纯 AVG | `2316` | `SC2316_bg_CityHall_Courthouse` | Mickey、Zack、Emma；市政厅警卫可作为场面人物 | Mickey 以律师身份介入，市政厅门口的程序阻力把调查推向正式文件、房产证明和银行搜查。 |
| L3 | 指证后纯 AVG | `2392` | `SC2392_avg_MooreOldKey` | Moore、Zack、Emma | Moore 被逼到交代房产证交易，旧铁钥匙作为剧情焦点进入玩家视线。 |
| L4 | 开篇纯 AVG | `2491` | `SC2491_avg_NightHospitalMeeting` | Zack、Emma、Mickey；Margaret 可作为病床背景人物 | 夜间医院的紧张感，几人根据对白汇总地下室、Lula、Danny 方向。 |
| L4 | 指证纯 AVG | `2492` | `SC2492_avg_DannyBathroomConfrontation` | Danny、Zack、Emma | 厕所隔门、狭窄、封闭、回避感；Danny 的压力来自躲在里面不肯面对。 |
| L4 | 指证后纯 AVG | `2493` | `SC2493_avg_DannyBathroomWindowWaiver` | Danny、Zack、Mickey、Lula（小窗外） | Lula 在厕所小窗外平静签下放弃继承声明，Danny 仰头看着小窗彻底崩溃；之后才转入主屋会合。 |
| L5 | 开篇纯 AVG | `2591` | `SC2591_avg_FrankHomeMislead` | Zack、Emma；线索物可作为画面焦点 | 小铁盒、举报材料、情书作为剧情焦点出现，但不是可点击拾取物。 |
| L5 | 指证后纯 AVG | `2592` | `SC2592_avg_VinnieConfession` | Vinnie、Zack、Emma；Tony 如对白需要可在场 | Vinnie 抢话认罪，试图把案件收束到自己身上，场面要有突然打断和强行揽罪的压迫感。 |
| L6 | 开篇纯 AVG | `2691` | `SC2691_avg_FinalHospitalBeforeSearch` | Zack、Emma、Margaret、Foster | 最终循环前的证词整合，Margaret 苏醒后的虚弱与 Foster 的严肃说明都要能看出来。 |
| L6 | 指证后纯 AVG | `2692` | `SC2692_avg_LeonardConfession` | Leonard、Zack、Emma；Vinnie 可作为替罪被揭穿后的关系暗示 | Leonard 招供，Vinnie 替罪被揭穿，空间要有终局摊牌后的冷硬感。 |

## 需要单独明确人物动作资产的纯 AVG 场景

这里记录的是“额外人物动作/进出场资产”，命名应当是人物资产命名，不是整张 AVG 场景图命名。

- L1 开篇 `2191`：
  - 整图里需要表现 Morrison 拦路、Zack 被拦、Emma 介入。
  - 但额外人物资产只需要 Emma 入场/介入这一条。
  - 中途入场角色：Emma（命名：`emma_intervene_morrison_001` · 对话节点 201001014）
  - 情境：Emma 一步挡在 Morrison 面前，拦住他要去抓 Zack 的手，为 Zack 争取进入现场的机会。

- L3 开篇 `2316`：
  - 整图里需要表现市政厅门口被程序挡住，以及 Mickey 以律师身份介入。
  - 额外人物动作资产：
    - Guard（命名：`guard_cityhall_block_file_001` · 对话节点 201003004 起）：警卫伸手挡门/退回文件。
    - Mickey（命名：`mickey_cityhall_intervene_001` · 对话节点 201003028 起）：Mickey 从东翼方向走上台阶，扬起文件出面介入。

其他纯 AVG 场景暂不单独增加人物进出/动作资产需求，只按各自整图场面需求处理。
## 指证背景 topBg

| Loop | 当前配置 | 语义 |
|---|---|---|
| L1 | `SC2104_bg_PoliceStation_MorrisonOffice_Night` | Morrison 指证用警局办公室画面。 |
| L2 | `SC2211_bg_LakeshoreTrust_Lobby` | Leonard 指证用银行大厅画面。 |
| L3 | `SC2312_bg_LakeshoreTrust_VIPParlor` | Moore 指证用银行贵宾室画面。 |
| L4 | `SC2492_avg_DannyBathroomConfrontation` | Danny 指证用厕所隔门对峙完整 AVG 图。 |
| L5 | `SC2515_bg_SilverMoon_Casino_Night` | Vinnie 指证用赌场夜景画面。 |
| L6 | `SC2617_bg_LeonardResidence` | Leonard 指证用住所画面。 |

## 和自由探索分开的点

- L1 开篇 `2191` 不能再显示成 `2101` 的探索证据场景；它是 Morrison 拦住 Zack 的完整 AVG 图。
- L2 开篇 `2206` 不能显示成 Mickey 可点击 NPC 病房；Mickey 是画面人物，和对白一起构图。
- L2 指证后 `2292` 不能写成 Leonard NPC 挂载；Leonard 递信封/假善意是完整过场图。
- L3 指证后 `2392` 不能写成 Moore NPC 或旧钥匙拾取点；旧钥匙是剧情焦点。
- L4 `2492` 是厕所隔门对峙图，Danny 的空间关系要画在同一张图里。
- L4 指证后 `2493` 是同一厕所地点的另一张完整 AVG 图：Lula 小窗签字、Danny 崩溃、Zack/Mickey 收束；它不是 `2420` 探索厕所底图，也不是 `2418` 主屋会合。
- L5 开篇 `2591` 可以出现小铁盒、举报材料、情书等视觉焦点，但这些不是可点击拾取物。
- L6 开篇 `2691` 中 Margaret / Foster 是对白场面人物，不是自由探索 NPC。

## 配置落点

- SceneConfig.json：纯 AVG scene 使用独立 sceneId，并把 location.backgroundImage 指向独立 AVG 资产命名。
- ArtAssetConfig.json：每张纯 AVG 图单独一条资产记录，sceneKind=dialogue，ArtRequirement 写清楚在场人物和叙事作用。
- ChapterConfig.json：openingScene 指向开篇纯 AVG scene；initScene 指向自由探索入口；topBg 指向指证画面。
- ChapterConfig.json：指证后如果先在指证地点收束、再转到其他地点，需要拆成多个 postExposeSegments，并显式填写 videoScene + entryTalkId。例如 L4 先挂 `Loop4_danny #240080` 的厕所小窗签字，再转 `danny_l4_postexpose #211006001` 的主屋会合。
- unit_flow.json：流程预览引用 openingScene / postExposeSegments.sceneId，不再把开篇和探索混在同一个卡片里。
