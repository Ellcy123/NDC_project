# Unit5 运行时预检

日期：2026-09-14。职责：系统策划只读核对；本文件之外未修改任何文件，未修改 Unity、预览表或剧情。依据：Manifest、主大纲、README、state_source_contract.md、unit-state-generator 及 Unity runtime reference；已读系统策划必读和共读参考。

## 结论与边界

可以继续生成五份设计期 State。运行时尚未实现 U5 四个特殊玩法及互动终幕适配；这些是落表/工程交付依赖，不得反向删掉已批准的操作。用户已批准终幕可控，不生成 L6。末尾沿用 `loop_end` 并标 `chapter_boundary: true`，不创造 `chapter_end`。

Unity 正式源为 `D:/NDC/res/xls/*.xlsx`；本次仅检查 `res/xml` 与生成表/代码。普通 JSON 不是正式修改源。部分正式 JSON 含历史非严格转义，结构解析失败的表使用 ID token 保守扫描，包含嵌套引用；扫描数量不等同顶层行数。

## 可复用入口

| 能力 | 当前支持与证据 |
|---|---|
| 根 Opening | `res/xml/ChapterConfig.xml` 的 `initScene/initTalk`；一个根入口 |
| 跨场续接 | `TalkPanelCtrlMoveNextFunc.cs:346`，`change_scene + next`；next 非零跳过首次入场演出 |
| 自由 NPC / Repeat | `res/xml/NPCLoopInfo.xml` 的 `TalkInfo/LoopTalkInfo` |
| 分支及剧情动作 | `Assets/Scripts/table/Keywords.cs:93`：动作现为 0–20，loop_end=15，present_item=19，unit2_minigame=20；不可用旧 0–8 限制 |
| 环境调查 | `ItemDetailPanel.cs:948`，环境不入包、关闭发出 EnvironmentNarrativeClosed；`ItemMgr.cs:44` 记录点击 |
| 道具条件入场事件 | `SceneEnterTalkTriggerMgr.cs:205`，scene + requiredItemIds 全 AND；无通用 flag/Talk 完成条件 |
| 环境条件入场事件 | 同文件 `:239`，envir 条件读 `WasEnvirClickedInChapterConfig`，仅当前 Loop 观察 |
| post-expose 恢复 | `ChapterMgr.cs:370`，pending scene talk / active entry / post-expose talk / 总结页；不等于特殊玩法中途状态 |

上述代码均位于 `D:/NDC/Assets/_Project/Scripts/`（Keywords 例外）。正式 SceneConfig 的主键字段是 sceneId；ChapterConfig ID 实算为 `ChapterID * 100 + LoopID`。

## 环境物证进入疑点与 Expose：当前不直接支持

1. `Doubt/DoubtMgr.cs:172` 监听 ItemAdded；`:321` 的重判仅遍历 Bag.Items。它没有监听环境观察，也不读取环境点击集合。因此不入包环境物证原样挂 type=Item condition 不会正常点亮。
2. `UI/Expose/ExposeEvidencePanel.cs:280` 只刷新 itemType.item 和 itemType.clue；`:311` 从 Bag.GetItemsByType 取候选。envir 不在池内，即使强行入包仍不是正式候选类型。
3. `UI/Expose/ExposeBoardPanel.cs:267` 能按 ItemStaticData ID 表示槽位，是显示/校验的局部兼容，不等于玩家能取得并拖入环境材料。GM 自动补物品也不能作为正式能力依据。
4. `SceneEnterTalkTriggerMgr` 支持环境点击条件，只代表入场事件支持；不能把这项能力外推为疑点或 Expose 支持。

State 按已批准的 `environment_observed` special_adapter 保留原环境 ID、collectible:false、首次观察时段、合法信息层与疑点唯一归属。后续适配需同时覆盖：观察状态持久化/跨 Loop 读取、Doubt 实时触发与重判、Expose 候选池和拖放提交，以及未观察时不可用。不创建可拾取替代物、不伪造派生证据，不改变大纲材料含义。

## 特殊机制缺口

| 机制 | 需记录的适配职责 |
|---|---|
| L3 双面剖面 | 两阶段槽位与楼梯拖入、已完成阶段、当前场景弹出和圆桌再开、成功不生成物品 |
| L5 照片墙 | 翻面/年份排列/验证/提示/成功一次发放还原记录 |
| 终局 A | 五步进度、五格错误预算、提示资格、A 成败锁定、唯一续接 |
| 终局 B | 三格风险、R1/R2 自动纠正、拉杆提交、B 成功锁定、A 不影响答案权限 |
| 终幕协调 | 控制角色、阶段、A/B 独立结果、存档检查点、重复加载不重扣预算、不重发证物、结算路由 |
| 条件事件 | 明确 required_talks / previous_event_completed / flags；现有 SceneEnter 条件不足时标适配，不省略顺序 |
| 跨章 1602 | 从 U1 已获取状态合法导入 U5；缺导入为工程缺陷，不扣玩家错误格 |

`Unit2MiniGameMgr.cs:34` 仅保存 CompletedConfigIds；`Unit2MiniGamePanel.cs:111` 打开时重置中间步骤。其支持类型只有 dice/loan/spot/rose/tweezers/qte，没有 U5 对应玩法，不能声称直接落表即可运行。可参考入口/完成续接框架，但不能套用其取消=失败或仅存完成的语义。

`ItemStaticData.json:970` 已有 1602“录音盘碎片”，canCombined=false。`Manager/SaveData/ChapterMgr.Save.cs:145` 切章保存旧章快照后重置 ItemMgr，故不自动保留到 U5。A 的自动贴合应作为特殊流程事件，不能改成自行背包合成。

## ID 分配与扫描

正式表与预览表扫描结果：5xxx 的 Item/Scene/Location/Doubt/Expose 候选未见占用；5xx NPC 未见占用。ChapterConfig 501–505 空闲。GameFlowConfig chapterId=5 尚未落表，未来 loopCount=5。正式 Talk ID 延后分配，当前仅逻辑名。

唯一容易误判的占用：Unit2MiniGameConfig 的 5001–5006 属于 U2，不能用作该表 U5 新行；同数字出现在 Scene/Item 是不同表空间，不冲突。

### 主代理锁定的 U5 NPC 表

| U5 ID | 人物 | 旧章对照（不直接混用） |
|---|---|---|
| 501 | Zack | 正式 101/201，预览 310/401 |
| 502 | Emma | 正式 102/202，预览 311/402 |
| 503 | Pierce | 预览 412 |
| 504 | Vivian | 正式 106 |
| 505 | Foster | 正式 215，预览 304/408 |
| 506 | Lawson | 未见对应行 |
| 507 | 小 Charles | 预览 312 |
| 508 | Moore | 正式 208 |
| 509 | Mary，即 Lula | Mary 预览 302，Lula 正式 212；本章同一人物，不另拆 ID |
| 510 | 老 Charles | 未见对应行 |
| 511 | 巡逻警员 | U5 新登记 |
| 512 | 摄影师 | U5 新登记 |
| 513 | 管家 | U5 新登记 |
| 514 | Watts | 预览 404 |

七位证言使用 `{NPC三位}{Loop一位}{序号三位}`，501–514 × Loop1–5 候选区间已扫描正式/预览 Testimony 与 TestimonyItem，冲突 0。复用同一人物旧章 NPC ID 会使相同 Loop/seq 撞号；本章统一 5xx 避免此问题。普通可提取证言与指证现场动态谎言必须统一分配不同 seq，不可各从001自增。相同原文跨 Loop 回查保留既有 ID，不另造一条事实。

`ExposeBoardPanel.cs:276/:479` 存在 `testimonyId / 10000` 推导 NPC 的路径；因此七位前缀与 U5 NPC 必须一致，不能用旧证言 ID 指向新 U5 NPC。若引用旧章证言，保留其原 ID/原拥有者并另标跨章依赖，不能无迁移悄悄重写归属。

### 场景分配

场景 ID、地点及阶段变体统一引用主代理锁定的 [ID 登记表](../id_registry.yaml)，本报告不维护另一套候选。破门发生在礼堂；飞行机械馆位于另一端，不得合并为同一地点。

## 放行限制

本报告支持继续生成设计期 State，不代表现有 Unity 可直接运行 U5。所有特殊适配应在 State/风险中明确。后续落表必须复核最终 ID、入口唯一性、环境候选、跨章物件、终局保存恢复和 GameFlowConfig 五轮边界。
