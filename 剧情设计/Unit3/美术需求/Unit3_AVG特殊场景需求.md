# Unit3 AVG 特殊场景需求

说明：本文件只记录 Unit3 里"纯 AVG 对话/过场场景"和"指证场景背景"的美术语义。它不是自由探索场景清单，也不是 NPC 可点击立绘、证据道具、动态漫画分镜清单。

> **说明**：Unit3 处于 state 设计阶段，对白与配置尚未落地。下表 SceneId / 资产命名为按 Unit2 命名规律拟定的建议值（`SC3{loop}{9x}_avg_*`），待配置落地时以实际 SceneConfig 为准。

## 核心规则

- 纯 AVG 场景是一张完整的对话/过场图：人物和场景画在同一张图里，不是空底图加立绘挂载。
- 同一个地点，只要在场人物、人物状态、戏剧关系或构图不同，就应该是不同的 AVG 美术需求和不同资产命名。
- 纯 AVG 图可以参考探索底图的地点结构、光线和时代氛围，但不能把探索道具、可点击 NPC、证据挂载写进 AVG 图。
- 自由探索场景才是"底图 + Item / NPC 覆盖"；开篇自动对白、指证后对白一般都应走纯 AVG 场景。
- ChapterConfig.openingScene 专门给开篇 AVG 使用；initScene 是进入自由探索后的场景。
- 指证阶段使用 topBg；topBg 应指向对应的指证画面资产，而不是随便借探索场景。
- 突发事件动态漫画另见《Unit3_AVG突发事件动态漫画.md》，这里最多说明事件发生在哪个剧情节点，不展开格数。

## 纯 AVG 场景清单

| Loop | 类型 | SceneId | 资产命名 | 画面人物 | 画面重点 |
|---|---|---:|---|---|---|
| L1 | 开篇纯 AVG | `3191` | `SC3191_avg_Opening_MickeyCommission` | Mickey、Zack、Emma | Mickey 登门事务所委托调查 Thomas 坠楼案；点出"欠贷款 + 巨额保险 + 湖滨信托银行"与 Frank 案同模式，自己不参与、请两人查后到他办公室汇报。 |
| L1 | 指证后纯 AVG | `3192` | `SC3192_avg_MorrisonPointsToMary` | Morrison、Zack、Emma | Morrison 摆烂放任调查，抛出"楼顶脚印可能属于死者妻子 Mary"；态度是"内部牵扯太多、不想管"。 |
| L2 | 开篇纯 AVG | `3291` | `SC3291_avg_Opening_BackToApartment` | Zack、Emma | 带着"脚印属于 Mary"的线索回到 Thomas 公寓楼下（楼体为 6 层住宅 + 楼顶天台，画面可从街面仰看至楼顶护栏）；Emma 仰看天台护栏，感慨普通人被谋杀却被警方掩盖。 |
| L2 | 指证后纯 AVG | `3292` | `SC3292_avg_MaryRooftopVersion` | Mary、Zack、Emma | Mary 三轮被逼后退守：承认 22:00 上过天台，称与 Thomas 约好为 Emily 祈福、Thomas 突然想推她、她推回去时 Thomas 失力撞栏坠落；反复说自己会不会被当凶手。 |
| L3 | 开篇纯 AVG | `3391` | `SC3391_avg_Opening_ExpandSearch` | Zack、Emma | 走回公寓楼内，Emma 盯着住户名牌思考"Thomas 为何要推妻子、他的出轨对象会不会知情"，决定扩大搜查。 |
| L3 | 指证后纯 AVG | `3392` | `SC3392_avg_ThomasKillerRevealed` | Helen、Zack、Emma | 第一重反转：Thomas 是杀妻骗保恶魔（非单纯酗酒丈夫）。Helen 承认布置陷阱（毁栏 + 涂油）、否认杀人，坚称"被 Thomas 命令独自去做、Thomas 肯定是意外坠楼"。 |
| L4 | 开篇纯 AVG | `3491` | `SC3491_avg_Opening_FosterCall` | Zack、Emma（Foster 电话，不出实体立绘） | Helen 家门外，琢磨突破口时 Foster 来电：组里申请的油痕检测仪到了；两人决定去法医办公室取仪器并扩大调查。 |
| L4 | 指证后衔接 1 | `3492` | `SC3492_avg_CityHallVerdict` | Harrison（法官）、Mickey、Zack、Emma | 市政厅，Mickey 以辩护律师身份交代案情，为 Mary 争取合法杀人判决、为 Helen 争取无罪。 |
| L4 | 指证后衔接 2 | `3493` | `SC3493_avg_NewspaperInterview` | Emma、Mary、Helen | 报社，Emma 采访 Mary 与 Helen；Mary 陈述多年家暴遭遇，Helen 补充"银行存在诱导"（为 L5 起势）。 |
| L5 | 开篇纯 AVG | `3591` | `SC3591_avg_Opening_MickeyOffice` | Mickey、Zack、Emma | Mickey 律所，告知"Mary 已无罪、Helen 还在争取"；为起诉湖滨信托银行取证，派两人继续查 Bernard，写介绍函。 |
| L5 | 指证后纯 AVG | `3592` | `SC3592_avg_BernardConfession` | Bernard、Zack | Bernard 软化，承认主动诱导 Thomas、承认有戴花瓣缺口手链的女人来咨询；请 Zack 别再打探，"我也是打工人"。 |
| L6 | 开篇纯 AVG | `3691` | `SC3691_avg_Opening_NeedEvidence` | Mickey、Zack、Emma | Mickey 律所，Zack 怀疑去咨询的女人是 Mary；Mickey 提醒法庭只认事实证据；Zack 决定再查（若合谋且预谋，两人将面临死刑）。 |
| L6 | 关键剧情 AVG（法医室） | `3695` | `SC3695_avg_FosterFinalReport` | Foster、Zack、Emma | 法医办公室，Foster 推出盖红章的精密检测报告：血液酒精浓度 0.25%、Thomas 无有效攻击能力 → 颠覆"正当防卫"。L6 死因反转的关键剧情对话节点（不做突发事件动态漫画，按纯 AVG 关键场处理）。 |
| L6 | 结局衔接 1 | `3692` | `SC3692_avg_OfficeEmmaReturn` | Zack、Emma | 事务所，Emma 从报社回来；Zack 说银行教唆 Thomas 杀妻骗保，但隐瞒 Mary 蓄意谋杀。Emma 察觉 Zack 脸色不对。 |
| L6 | 结局衔接 2 | `3693` | `SC3693_avg_MaryHelenThanks` | Mary、Helen、Zack、Emma | 事务所，Mary 携 Helen 上门道谢；提房子卖给 TideWater 换 $8000、与 Helen 同住打工还债。Emma 疑惑银行为何轻易让 Mary 卖给 TideWater。 |
| L6 | 结局衔接 3 | `3694` | `SC3694_avg_LeonardDelivers` | Leonard、Emma、Zack | 事务所，Leonard 送来湖滨信托银行内部消息：南区清退房产最终流入 TideWater；不知 TideWater 为何想要这些房子（为 Unit4+ 起势）。 |

> **结局二选项**（Zack 销毁证据 / 拿起证据）发生在 L6 指证后、上述事务所衔接之前，属于剧情分叉点；两个 outcome 都进入共用的事务所衔接序列，画面上无需为两个分支单独出整图，差异由 Zack 是否持证及表情体现。

## 需要单独明确人物动作资产的纯 AVG 场景

这里记录"额外人物动作/进出场资产"，命名应当是人物资产命名，不是整张 AVG 场景图命名。

- L4 衔接 2 报社 `3493`：
  - 整图表现 Emma 采访 Mary 与 Helen。
  - Mary：从压抑到陈述家暴遭遇的舒缓（命名建议 `mary_interview_speak_001`）。
- L6 结局衔接 2 `3693`：
  - Mary + Helen 上门道谢的入场（命名建议 `mary_helen_visit_enter_001`）：两人一同登门，Mary 在前、Helen 在侧，状态克制平静。
- L6 结局衔接 3 `3694`：
  - Leonard 登门送文件的入场（命名建议 `leonard_deliver_enter_001`）：审慎、点到为止。

其他纯 AVG 场景暂不单独增加人物进出/动作资产需求，只按各自整图场面需求处理。

## 指证背景 topBg

| Loop | 指证对象 | 指证场景 | topBg 语义 |
|---|---|---|---|
| L1 | Morrison | SC3004 警局 | Morrison 指证用警局办公室画面。 |
| L2 | Mary | SC3013 公寓楼门口 | Mary 指证用公寓楼门口画面。 |
| L3 | Helen | SC3008 Helen 家 | Helen 指证用 Helen 家画面。 |
| L4 | Helen（补充） | SC3008 Helen 家 | Helen 补充指证用 Helen 家画面（可与 L3 区分光线/时段）。 |
| L5 | Bernard | SC3014 Bernard 办公室 | Bernard 指证用银行办公室画面。 |
| L6 | Mickey（控辩对决） | SC3011 Mickey 办公室 | Mickey 5 轮控辩对决用律所办公室画面；是友方辩护人之间的推理对决，不是敌对审讯，氛围区别于前几轮指证。 |

## 和自由探索分开的点

- L1 开篇 `3191` 是 Mickey 登门委托的完整 AVG 图，不是 SC3001 探索证据场景。
- L2 指证后 `3292` 是 Mary 退守自述的过场图，不是 Mary NPC 挂载。
- L3 指证后 `3392` 是 Thomas 真面目反转 + Helen 承认布陷阱的过场图。
- L4 开篇 `3491` 中 Foster 仅电话出现，不画实体立绘；油痕检测仪是 L4 自由探索/小玩法的功能道具，不在本过场图。
- L4 Mary 登场求情是突发事件动态漫画（见《突发事件》文档），不在本表纯 AVG 场景内。
- L6 法医室 `3695` 中 Foster 推红章报告是关键剧情对话；报告本身是证据道具（法医鉴定 3601），AVG 图只表现 Foster 出报告的场面，不画成可点击拾取。
- L6 结局衔接的三张事务所图（`3692`/`3693`/`3694`）人物各不同，应分别成图。

## 配置落点

- SceneConfig.json：纯 AVG scene 使用独立 sceneId，并把 location.backgroundImage 指向独立 AVG 资产命名。
- ArtAssetConfig.json：每张纯 AVG 图单独一条资产记录，sceneKind=dialogue，ArtRequirement 写清在场人物和叙事作用。
- ChapterConfig.json：openingScene 指向开篇纯 AVG scene；initScene 指向自由探索入口；topBg 指向指证画面。
- unit_flow.json：流程预览引用 openingScene / postExposeSegments.sceneId，不把开篇和探索混在同一卡片里。

## 变更记录

- 2026-06-27 v1.0：基于 Unit3 state（loop1-6）首次建立。列出各 Loop 开篇 / 指证后 / 衔接纯 AVG 场景与指证 topBg；L6 Foster 法医反转作为关键剧情 AVG（`3695`）处理，不做突发事件。SceneId / 资产命名为待落地的建议值。
