# Unit4 证据与道具交付清单

> 适用范围：Unit4 / EPI04 / 4xxx。  
> 章节结构：5 个 Loop + 非 Loop 终幕。  
> 重建基线：2026-08-27，Git `4a563f6`。
> 当前用途：生产路由索引，不是第四份证据设计文档，也不是资产完成报告。
> 本清单覆盖 59 条正式证据；4122、4123 等玩法附属素材另列，不计入正式证据总数。

---

## 一、来源分工与冲突处理

| 决定事项 | 采用的依据 |
|---|---|
| 证据是什么、必须表现什么、哪些内容不能提前出现 | [Unit4 证据美术资产总览](../证据设计/Unit4_证据美术资产_总览.md)及 Loop 1—5 证据美术文档 |
| 首次出现、实际获取事件、场景状态、时序与门控 | [Loop 1 State](../state/loop1_state.yaml)、[Loop 2 State](../state/loop2_state.yaml)、[Loop 3 State](../state/loop3_state.yaml)、[Loop 4 State](../state/loop4_state.yaml)、[Loop 5 State](../state/loop5_state.yaml) |
| Map、Position、Big、Icon、环境观察与容器链的技术合同 | [NDC Scene Evidence Placement Skill](../../../.codex/skills/ndc-scene-evidence-placement/SKILL.md) |
| Unit / Episode / ID 身份 | [canon_manifest.json](../../../canon_manifest.json) |
| 当前字段、既有资源 stem 与实施缺口 | [ItemStaticData.json](../../../avg_editor_v2/data/table/ItemStaticData.json)与 [SceneConfig.json](../../../avg_editor_v2/data/table/SceneConfig.json)；只作实施现状，不反推设计 |

冲突处理规则：

1. 证据名称、物理身份、可读信息和剧透边界以证据设计为准。
2. 实际获取方式以 State 中发生的玩家事件为准；这一步决定是否需要世界 Map 和 Position。
3. 交付规格以当前 Skill 为准。旧文档或旧试制包与 Skill 冲突时，不得继续沿用旧规格。
4. 当前配置中预填了路径，不代表对应资产、坐标或获取路由已经成立。
5. 无法由以上来源唯一裁决的条目必须标为“阻塞”，不能用占位 Map、假坐标或多余 Icon 补齐。

本清单不重复证据正文、英文上画文本、精确美术细节和跨证据视觉锚；制作时必须回到对应 Loop 的证据美术文档读取。

---

## 二、交付类别速查

| 交付类别 | 实际玩家事件 | 必交资产 |
|---|---|---|
| `scene-pickup` / item | 玩家在基础探索场景点击或搜索后取得物品 | Map + Position + ordinary Big + Icon |
| `scene-pickup` / clue | 玩家在基础探索场景拍摄或记录现场线索 | Map + Position + `620 x 620` clue Big + Icon |
| `container-state` / 逐件点击 | 玩家打开 Type 6 → Type 7 后继续点击子物 | Type 6 Map/Position + Type 7 Map/Position + 子物 Map/Position/Big/Icon |
| `container-state` / 原子发放 | 玩家打开容器后由事件一次自动取得全部内容 | Type 6/Type 7 可见状态 + 每件 Big/Icon；明确不制作子物 Map/Position |
| `detail-only` | 对话、AVG、事件、分析、记忆或推理界面自动交付 | Big + Icon；无 Map/Position；画面中实际展示时另做 handover/条件状态 |
| `environment` | 玩家点击环境观察，但物件不进入背包 | Map + Position + Big；完全省略 Icon |
| `minigame-only` | 玩法界面素材，不进入 ItemStaticData | 进入对应玩法资产流程，不计入下方 59 条 |

ordinary Big、Icon、clue Big、Type 7 白边、命名、坐标推导和验证细节全部以当前 Skill 及其 references 为准，本清单不复制尺寸流程。

### 路由数量

| 路由 | 数量 | 说明 |
|---|---:|---|
| 基础场景直接拾取／记录 | 20 | 包含点击家具后直接取得；不自动升级为 Type 6/7 |
| 真实二级容器中的逐件点击 | 1 | 4320，必须有完整子物 Map/Position |
| 对话、AVG、事件、分析、记忆、推理或容器原子发放 | 33 | 全部 detail-only，无世界 Map/Position |
| 环境观察 | 5 | 4216、4321、4322、4323、4324；均需 Map/Position/Big 且无 Icon |
| 合计 | 59 | 与当前 EPI04 ItemStaticData 正式行数一致 |

---

## 三、59 条正式证据交付路由

“路由已定”只表示可以按本行开资产任务，不表示资产已经完成或配置已经落表。

### Loop 1｜11 条

来源：[循环1证据美术资产](../证据设计/Unit4_循环1_证据美术资产.md) + [loop1_state.yaml](../state/loop1_state.yaml)

| ID | 名称 / 运行类型 | 场景与实际获取事件 | 交付类别 | 必交资产 | 路由状态 |
|---|---|---|---|---|---|
| 4111 | Harrison公开日程与夜间出入对照 / clue | SC4003；完成调阅检索后自动生成 | `detail-only` | 结果 Big + Icon；无 Map/Position | 已定；另做 4122、4123 玩法页 |
| 4112 | 1919-A入账存根 / item | SC4002；点击普通费用抽屉直接取得 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定；抽屉是直接热点，不建 Type 6/7 |
| 4113 | 未完成的辞职信草稿 / item | SC4002；点击打字机旁废纸篮直接取得 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定；废纸篮是直接热点，不建 Type 6/7 |
| 4114 | 圣心医院资助档案卷宗 / item | SC4003；档案管理员对话交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；如落桌，另做交付状态 |
| 4115 | Harrison两个月调阅索引 / item | SC4003；玩家从中央调阅桌取得 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定 |
| 4701 | 调阅索引中的本人赔偿裁定 / item | SC4003；整理 4115 与旧案目录后生成 | `detail-only` | 结果 Big + Icon；无 Map/Position | 已定；按运行 itemType 3，不套 clue 相框 |
| 4116 | Mary / Helen案改判往来信 / item | SC4003；玩家从 Harrison 调阅车取得 | `scene-pickup` | Map + Position + ordinary Big + Icon | 路由已定；第三次提交日期阻塞最终上画文本 |
| 4117 | Harrison留下的编号纸条 / item | SC4002 指证后 AVG；Watts 开柜后一次交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；另做保险柜开启状态 |
| 4118 | 医院冷藏库留样试剂 / item | SC4002 指证后 AVG；从保险柜内保冷箱材料中交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；基础探索不得提前摆保冷箱或药瓶 |
| 4119 | Harrison亲笔资金流向图 / item | SC4002 指证后 AVG；同批一次交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定 |
| 4120 | 南区综合商业开发计划摘要 / item | SC4002 指证后 AVG；同批一次交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定 |

### Loop 2｜11 条

来源：[循环2证据美术资产](../证据设计/Unit4_循环2_证据美术资产.md) + [loop2_state.yaml](../state/loop2_state.yaml)

| ID | 名称 / 运行类型 | 场景与实际获取事件 | 交付类别 | 必交资产 | 路由状态 |
|---|---|---|---|---|---|
| 4211 | 红线注射器与十三日封签药盒 / item | SC4011；Rosa 对话交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；可另做对话后桌面状态 |
| 4212 | Isabel使用后的封签药瓶 / item | SC4011；Rosa 对话交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；可另做物证垫状态 |
| 4217 | Isabel的病历本 / item | SC4011；Rosa 从随身旧包取出并交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；旧包只是演出载体 |
| 4702 | 经容量分析的回收药瓶 / item | SC4013；完成 4212 容量分析后生成 | `detail-only` | 结果 Big + Icon；无 Map/Position | 已定 |
| 4216 | Miller事故基金项目铭牌与康复名册 / envir | SC4012；点击 Miller 项目展示墙观察 | `environment` | Map + Position + Big；无 Icon | 已定；当前表需去 Icon |
| 4213 | 同配方药瓶封签组 / item | SC4013；Foster 对话交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；托盘只作交付状态 |
| 4218 | 验尸官办公室有限调档许可 / item | SC4013；Foster 对话交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定 |
| 4219 | 五年七例儿童死亡病例对照表 / clue | SC4012；提交编号并完成调档演出后自动生成 | `detail-only` | 结果 Big + Icon；无 Map/Position | 已定；另做条件档案车／病例演出态 |
| 4703 | 经化验的医院冷藏库留样试剂 / item | SC4013；受控化验后由 Foster 交付 | `detail-only` | 结果 Big + Icon；无 Map/Position | 已定 |
| 4214 | 圣心医院慈善项目采购与发放记录 / item | SC4015；Mickey 对话交付法院卷宗 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；不再按阅卷桌自由拾取 |
| 4215 | 缺失的第十九页副本 / item | SC4015；Mickey 在同册卷宗演出中交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；不另摆第二份桌面证据 |

### Loop 3｜14 条

来源：[循环3证据美术资产](../证据设计/Unit4_循环3_证据美术资产.md) + [loop3_state.yaml](../state/loop3_state.yaml)

| ID | 名称 / 运行类型 | 场景与实际获取事件 | 交付类别 | 必交资产 | 路由状态 |
|---|---|---|---|---|---|
| 4311 | 磨号手枪与枪内未击发余弹 / clue | SC4022；记录 Harold 尸体右手枪位 | `scene-pickup` | Map + Position + `620 x 620` clue Big + Icon | 已定 |
| 4312 | 伪造遗书 / item | SC4022；点击书桌中央遗书 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定 |
| 4313 | Pierce档案移交通知 / item | SC4022；点击书桌侧档案袋 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定；日期／时刻数字故意模糊不可辨，不填写具体钟点 |
| 4314 | 两只酒杯 / clue | SC4027；记录会客矮桌上的两只酒杯 | `scene-pickup` | Map + Position + `620 x 620` clue Big + Icon | 已定；不放电话桌 |
| 4315 | 古巴雪茄烟蒂 / clue | SC4027；记录第二只酒杯旁的湿杯垫与烟蒂 | `scene-pickup` | Map + Position + `620 x 620` clue Big + Icon | 已定 |
| 4316 | 伪造煤气铅封与异常时钟接线 / clue | SC4028；完成铅封与时钟接线两个热点后自动生成 | `detail-only` | 结果 Big + Icon；无 Map/Position | 已定；另做两个现场热点，禁止伪造单一 Map |
| 4317 | 214号黄铜寄存柜钥匙 / item | SC4025；点击调度台旁临时物品盘 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定 |
| 4318 | Harrison案证物转运调度单 / item | SC4025；点击调度台合订夹 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定 |
| 4319 | 晚间报纸号外 / item | SC4025；点击晚报架／长椅 | `scene-pickup` | Map + Position + ordinary Big + Icon | 路由已定；发行时刻阻塞最终上画文本；不按旧版“散落报纸”落位 |
| 4320 | Morrison写给Zack的未寄出口供 / item | SC4026；使用 4317 开柜后点击柜内封套 | `container-state` / 逐件点击 | Type 6/7 + 子 Map/Position/ordinary Big/Icon | 已有机器验证通过的合规试制包；正式 ID、人工视觉审批与同步仍待确认，见第五节 |
| 4321 | 煤气阀门异常开启痕迹 / envir | SC4028；点击主煤气阀观察 | `environment` | Map + Position + Big；无 Icon | 已定；当前表需去 Icon |
| 4322 | 窗缝逆风与煤气味 / envir | SC4028；点击背风窗缝观察 | `environment` | Map + Position + Big；无 Icon | 已定；当前表需去 Icon |
| 4323 | 宅邸常用物件的偏左摆放 / envir | SC4022；点击书桌左侧常用区观察 | `environment` | Map + Position + Big；无 Icon | 已定；SC4027只延续视觉，不建第二热点 |
| 4324 | 门廊卷收式厚质防风帘 / envir | SC4029视觉首现；SC4023爆炸后可选观察 | `environment` | Map + Position + Big；无 Icon | 已定；不作为 QTE 门槛，当前表需去 Icon |

### Loop 4｜11 条

来源：[循环4证据美术资产](../证据设计/Unit4_循环4_证据美术资产.md) + [loop4_state.yaml](../state/loop4_state.yaml)

| ID | 名称 / 运行类型 | 场景与实际获取事件 | 交付类别 | 必交资产 | 路由状态 |
|---|---|---|---|---|---|
| 4411 | Lakeshore清退协警通知 / item | SC4031；Doris 在开场对话交出 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；如镜头展示，另做 handover 状态 |
| 4412 | Lakeshore最终收购协议 / item | SC4033；点击餐桌文件组 | `scene-pickup` | Map + Position + ordinary Big + Icon | 阻塞精确上画文本；最终收购金额尚未锁定 |
| 4413 | Margaret写给O'Hara的短便条 / item | SC4033；点击协议旁独立便条 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定 |
| 4414 | 临时停止执行回执 / item | SC4033；电话事件后由 Watts 送达并自动取得 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；不做条件拾取 Map |
| 4415 | 1903南区码头旧照片 / item | SC4034；点击半开相册抽屉中的照片 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定；直接热点，不建 Type 6/7 |
| 4704 | 右下牙长期缺损 / item | SC4034；查看 4415 后自动生成记忆 | `detail-only` | 记忆结果 Big + Icon；无 Map/Position | 路由已定；结果卡框架与来源回溯表现待统一 |
| 4416 | Patrick葬礼册与1919旧信封 / item | SC4034；点击半拆纸箱内材料 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定；直接热点，不建 Type 6/7 |
| 4709 | 1919同时出现的两项可观察事实 / item | SC4034；查看 4416 后自动生成记忆 | `detail-only` | 记忆结果 Big + Icon；无 Map/Position | 路由已定；结果卡框架与来源回溯表现待统一 |
| 4417 | Patrick外套口袋里的粉笔转运牌 / clue | SC4034；点击外套口袋取得并记录 | `scene-pickup` | Map + Position + `620 x 620` clue Big + Icon | 已定；直接热点，不建 Type 6/7 |
| 4418 | Patrick遗物匣 / item | SC4034 指证后；Margaret 主动交付 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；另做旋转、刻句、打开与返程票玩法资产 |
| 4419 | Margaret写给Mickey但未寄出的短笺 / item | SC4034；点击写字台未寄信格 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定；直接热点，不建 Type 6/7 |

### Loop 5 与非 Loop 终幕｜12 条

来源：[循环5证据美术资产](../证据设计/Unit4_循环5_证据美术资产.md) + [loop5_state.yaml](../state/loop5_state.yaml)

| ID | 名称 / 运行类型 | 场景与实际获取事件 | 交付类别 | 必交资产 | 路由状态 |
|---|---|---|---|---|---|
| 4511 | Mickey定制钢笔 / item | SC4042；点击私人书桌钢笔 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定 |
| 4512 | Mickey的半支古巴雪茄 / item | SC4042；点击 M.F.D. 私人烟灰缸 | `scene-pickup` | Map + Position + ordinary Big + Icon | 已定 |
| 4513 | 1925年内部接口接管记录 / item | SC4042；字母锁密码正确后原子自动发放 | `detail-only` / 容器原子发放 | ordinary Big + Icon；无子 Map/Position | 父容器待落地；开柜态只显示可辨轮廓 |
| 4514 | 1919年银行授权附页 / item | SC4042；同一次开柜原子自动发放 | `detail-only` / 容器原子发放 | ordinary Big + Icon；无子 Map/Position | 父容器待落地 |
| 4515 | 手写功业簿 / item | SC4042；同一次开柜原子自动发放 | `detail-only` / 容器原子发放 | ordinary Big + Icon；无子 Map/Position | 父容器待落地；另做翻页／笔迹玩法裁切 |
| 4516 | Tidewater南区商业开发执行卷 / item | SC4042；同一次开柜原子自动发放并保持整袋封存 | `detail-only` / 容器原子发放 | ordinary Big + Icon；无子 Map/Position | 父容器待落地；另做 SC4044 三阶段拆阅状态 |
| 4705 | 1919-A与Donnelly属于同一法律资金网络 / item | SC4042 身份锁 4501 完成后生成 | `detail-only` | CASE BOARD 结果 Big + Icon；无 Map/Position | 路由已定；结果卡框架、来源回溯与资源命名待统一 |
| 4706 | Morrison页结论 / item | SC4042 身份锁 4502 完成后生成 | `detail-only` | CASE BOARD 结果 Big + Icon；无 Map/Position | 路由已定；结果卡框架、来源回溯与资源命名待统一 |
| 4707 | 书写者一致性 / item | SC4042 身份锁 4502 完成后生成 | `detail-only` | CASE BOARD 结果 Big + Icon；无 Map/Position | 路由已定；结果卡框架、来源回溯与资源命名待统一 |
| 4708 | Mickey就是Morrison死亡当晚的陌生访客 / item | SC4042 身份锁 4503 完成后生成 | `detail-only` | CASE BOARD 结果 Big + Icon；无 Map/Position | 路由已定；结果卡框架、来源回溯与资源命名待统一 |
| 4518 | Sean O'Malley特殊处置页 / item | SC4044 AVG；Zack 拆开 4516 隐藏附件后自动取得并扣下 | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；只在终幕三阶段拆阅中出现 |
| 4519 | 后插入的水源维护页 / item | SC4044 AVG；与 4518 同批取得，SC4045 再交给 Watts | `detail-only` | ordinary Big + Icon；无 Map/Position | 已定；不在 SC4045 生成第二件道具 |

---

## 四、真实容器与附属演出资产

### 运行容器

| 场景 | 容器与输入 | 输出事件 | 正确交付 | 当前状态 |
|---|---|---|---|---|
| SC4026 | 214号寄存柜；4317 解锁 | 开柜后玩家继续点击 4320 封套 | 完整 Type 6 → Type 7 → 4320 子 Map/Position/Big/Icon | [试制包](../../../image/edit_jobs/u4-station-locker-4320-v1/delivery/container_delivery_manifest.json)采用 `4805 → 4806 → 4320`，验证已通过；尚未批准或同步正式表 |
| SC4042 | 七位字母锁保险柜；输入 `FTMWPTF` | 密码正确后一次原子发放 4513—4516 | Type 6/Type 7 可见状态 + 四件独立 Big/Icon；四件无子 Map/Position | Type 6/7 ID 与正式配置待落地 |

只有 Type 6 可以进入 `SceneConfig.ItemIDs`。Type 7 由 Type 6 的 `ActionParam` 生成，逐件点击的子物由 Type 7 指向；原子发放必须在 manifest 中写明无子 Map/Position 的原因。

旧文档曾把 4112、4113、4415、4416、4417、4419列为 Type 6/7 容器。现行场景文档把它们定义为加载时直接开放的调查热点，State 也没有二级菜单事件，因此本清单统一按 `scene-pickup` 处理。将来若交互设计改为“打开后继续点击”，必须先改 State／场景合同，再把对应行升级为 `container-state`。

### 不计入 59 条的附属资产

| 场景／玩法 | 附属资产 | 路由 |
|---|---|---|
| SC4002 / SC4003 | 4122公开日程页、4123夜间访问页 | `minigame-only`；服务 4111，不进 ItemStaticData |
| SC4002 指证后 | Watts保险柜关闭／开启、保冷箱与4117—4120交付状态 | AVG 演出资产；不建 Type 6/7 |
| SC4012 | 七份病例档案车与调档完成状态 | 条件演出资产；输出 4219 |
| SC4028 | 煤气铅封热点、时钟接线热点与两点完成状态 | 场景热点／条件叠层；输出 4316，不生成假 Map |
| SC4034 | 4418旋转、七词刻句、打开内衬与未使用返程票 | 物品玩法资产；不作为世界 Map |
| SC4042 | 保险柜字母锁、打开态四组材料轮廓 | 容器／玩法资产；四件原子发放 |
| SC4044 | 4516公开外卷 → 硬质底衬暗夹 → 4518/4519取出 | AVG三阶段演出；不得在SC4042提前出现隐藏附件 |

---

## 五、开工前阻塞项

| 阻塞项 | 当前问题 | 放行条件 |
|---|---|---|
| 4412 精确金额 | 证据总览明确标为 open，最终收购金额尚未锁定 | 结合 O'Hara 房产正常价值拍板美元数，再制作最终可读 Big |
| 4116 / 4319 精确时间 | 第三次提交日期、晚报发行时刻尚未与 Unit4 最终时间线校准 | 锁定日期／钟点并同步两件文书的最终英文上画文本；4313 已按“数字不可辨”口径放行 |
| 4704—4709 结果卡表现 | Skill 已锁定 Big + Icon，但通用框架、结果卡尺寸选择和来源回溯交互尚未统一 | UI／系统确认统一模板和回溯表现后，再批量制作最终结果卡 |
| 正式英文上画文本 | 当前证据文档仍是内容设计稿，法律、银行、医院术语未完成统一英文编辑 | 正式进表前完成全量英文校对，并把最终文本同步到资源母版 |
| 4320 试制包同步 | 当前合规包使用试制 ID `4805 → 4806 → 4320`，manifest 与验证均通过，但正式文件未改 | 审批 4805／4806 的正式占用和整包视觉结果后，再同步 ItemStaticData 与 SceneConfig |
| 容器正式配置 | SceneConfig 仍直接列出 4320、4513—4516；正式 Type 6/7 链未建立 | 分配或批准容器 ID，只把 Type 6 绑定到 SceneConfig，并完成 ActionParam 链 |
| Envir 配置 | 4216、4321、4322、4323、4324 当前都有 Icon 路径且 Position 为空 | 五条 Envir 均制作真实 Map/Position/Big，并删除 Icon 路径和 Icon 文件 |
| 获取方式配置 | 4316、4411、4414、4418、4704、4709、4513—4516、4518、4519 等仍被当前表或 SceneConfig 当作直接场景物／manual | 按本清单和 State 统一 obtainMethod、SceneConfig 绑定与空 Map/Position |
| 资源命名缺口 | 4516、4704—4709 当前缺 folderPath、Big、Icon 等正式 stem | 在各自资产任务建立前分配并审查命名；不得用临时文件名直接进 Unity |
| 全局坐标 | 当前 59 条 EPI04 ItemStaticData 的 Position 全为空 | 仅为 20 条 scene-pickup、4320 子物和 5 条 Envir，从验收通过的原生分辨率图自动推导；detail-only 继续保持为空 |

这些阻塞项只记录现状。本次重建不修改 State、SceneConfig、ItemStaticData、Unity 表或任何美术资产。

---

## 六、生产与验收顺序

1. 从本清单选定一条未阻塞记录，回读对应证据美术卡与 State 获取事件。
2. 按最新 Skill 建立 acquisition coverage row；世界交互必须有真实可见锚点，detail-only 必须写明无 Map 原因。
3. 场景类资产只在批准的原生分辨率底图上非破坏制作；Position 从最终验收图自动推导，不手抄、不目测。
4. Big、Icon、clue Big、Envir Icon 省略和容器链按 Skill 完整验证；旧试制包不得跳过新闸门。
5. 先交付到 `image/edit_jobs/<job>/delivery/`。资产进 Unity、正式配置表变更和 SceneConfig 重绑需另行取得用户授权。
