# Unit2 人物表情需求

> 版本：v1.0 / 2026-08-10  
> 依据：Unit2 当前大纲、角色档案、六个 Loop 的 AVG 情绪状态需求，以及 Unit1 已有表情资源。  
> 规则：只写英文资源名，不写路径；Zack、Emma 等 Unit1 已登场角色优先复用旧资源，只有旧资源无法表达的 U2 新状态才列为新增。  
> 统计：建议新增 74 个表情资源，其中 Zack 3 个、Emma 1 个、Morrison 0 个，Unit2 新角色 70 个。

---

## 一、我对本章表情设计的理解

Unit2 的核心不是单纯查明“谁放了火”，而是六个 Loop 逐层撕开人物的社会面具：Mickey 用可靠律师的从容掌握调查节奏，Leonard 用银行职员的职业话术掩盖恐惧，Vinnie 用冷硬和假认罪替别人接过结局，Lula 则用近乎安静的克制守住她和 Frank 的感情。玩家从 L1 以为 Margaret 死于火灾的失控出发，经过 Danny 的贪婪、Lula 的放弃继承、Vinnie 的主动认罪，最终看见 Leonard 的体面彻底崩塌，却仍没有得到一个真正圆满的胜利。

因此本章的表情差分重点是“身份面具如何裂开”，不是为每个角色平均配置喜怒哀乐。多数关键状态应表现为眼神、嘴角和动作节奏的细小变化：Leonard 反复压袖口，Mickey 平静递出文件，Tony 擦杯子的手停一拍，Vinnie 被问到 Leonard 时短暂停手，Lula 签完放弃继承声明后才抬头，Earl 则从 L2 双手不停记账变成 L5 本能地护住自己的手。除 Danny、Edith 等少数人物外，不建议使用大幅度咆哮或戏剧化哭喊。

主角与回归角色不重复生产 Unit1 已有表情。只有当 U2 的剧情信息依赖一种旧资源无法覆盖的复合状态时，才新增差分；普通愤怒、惊讶、思考、疲惫、冷淡等继续沿用 Unit1 资源。

---

## 二、Unit1 资源复用说明

| 角色 | U2 直接复用的 Unit1 资源 | 可覆盖的 U2 状态 | U2 新增数量 |
|---|---|---|---:|
| Zack Brennan | `zack_angry.png`、`zack_annoyed.png`、`zack_calm.png`、`zack_cold.png`、`zack_surprised.png`、`zack_suspicious.png`、`zack_thoughtful.png`、`zack_weary.png` | 火场愤怒、调查怀疑、思考、L6 冷硬逼供与结尾疲惫 | 3 |
| Emma O'Malley | `emma_angry.png`、`emma_angry_stare.png`、`emma_calm.png`、`emma_happy.png`、`emma_sad.png`、`emma_surprised.png`、`emma_thinking.png`、`emma_tired.png`、`emma_furious.png` | 记者拦场、医院看护、电话报喜与反转震惊、行动状态 | 1 |
| Morrison | `morrison_calm.png`、`morrison_sluggish.png`、`morrison_sharp.png`、`morrison_strained.png`、`morrison_resigned.png` | 火场冷漠阻拦、被记者身份卡住、看到报告后服软、签署搜查令 | 0 |

说明：Emma 的 `BarLobby_*_test` 测试资源和同义 V2 资源不作为 U2 新需求重复统计；实际接入时从 Unit1 已定稿版本中选用。

---

## 三、U2 新增表情资源清单

### Zack Brennan（新增 3 个）

| 资源名 | 表情描述 |
|---|---|
| `zack_desperate.png` | 恐惧失控 (Desperate)：眉头上挑并向内收紧，眼睛睁大，嘴唇紧张微张；身体明显前倾，像下一秒就要撞开阻拦冲进火场。核心不是愤怒，而是害怕母亲已经死去。 |
| `zack_teary_relief.png` | 含泪释然 (Teary Relief)：眼眶发红湿润，眉眼从紧绷突然松开，嘴角出现压不住的微笑，像看到“她还活着”的电报后终于重新呼吸。不能画成大哭。 |
| `zack_resolute.png` | 坚定追凶 (Resolute)：眼神稳定直视前方，眉心收紧但没有怒意，嘴唇平直；表现 L5 在法庭路线与继续追凶之间作出选择后的坚定。 |

### Emma O'Malley（新增 1 个）

| 资源名 | 表情描述 |
|---|---|
| `emma_red_eyed_defiant.png` | 红眼不甘 (Red-eyed Defiant)：眼眶发红但没有落泪，眉头压低，嘴唇用力收紧，悲伤和愤怒同时存在；用于结尾面对“不完整胜利”时的克制不甘。不能画成单纯哭泣。 |

### Morrison（新增 0 个）

U2 所需状态均可由 Unit1 已有资源覆盖，不新增表情。火场的不耐烦优先使用 `morrison_sluggish.png` 或 `morrison_calm.png`，签署搜查令时优先使用 `morrison_strained.png`，不要为了同义状态重复生产。

### Mickey Donnelly（新增 5 个）

| 资源名 | 表情描述 |
|---|---|
| `mickey_calm.png` | 训练有素的平静 (Composed)：目光稳定，嘴角自然，面部没有明显紧张；不是冷漠，而是已经把情绪计算进去之后留下的从容。 |
| `mickey_warm.png` | 熟人式温和 (Warm)：嘴角轻微上扬，眼神放松，带旧友和可靠长辈的亲近感；不能笑得过分热情。 |
| `mickey_serious.png` | 转入正事 (Serious)：笑意收住，视线聚焦，眉眼略沉；用于谈 Frank 委托、法律风险和关键证据。 |
| `mickey_authoritative.png` | 律师压场 (Authoritative)：下巴略抬，眼神平稳锁定对方，嘴角平直；可配合递出法院文件或扶住公文包，压力来自专业确定性而非发怒。 |
| `mickey_measured.png` | 克制衡量 (Measured)：视线短暂落在文件或对方手中的工具上，眉心极轻微收紧，像在迅速调整方案；只表现“知道得多、反应快”，不能表现成反派算计。 |

### Margaret Brennan（新增 5 个）

| 资源名 | 表情描述 |
|---|---|
| `margaret_calm.png` | 平静/中立 (Calm / Neutral)：眼神平视，面部肌肉放松，嘴唇自然闭合；作为 Margaret 清醒时普通对白及其他表情差分的基础版本。 |
| `margaret_unconscious.png` | 昏迷病床 (Unconscious)：双眼闭合，面部苍白疲惫，呼吸微弱但稳定；不能画成遗体状态，必须保留仍然活着的迹象。 |
| `margaret_sharp.png` | 苏醒后的尖锐 (Sharp)：眼神有力地打量对方，一侧眉毛微抬，嘴角带一点不留情面的讥讽；身体虚弱，但人格不能显得软弱。 |
| `margaret_recollecting.png` | 冷静回忆 (Recollecting)：视线略偏向远处，眉心轻皱，嘴唇自然收住；像在按时间顺序核对记忆，而不是沉浸在火灾恐惧中。 |
| `margaret_guarded_warmth.png` | 带刺的关心 (Guarded Warmth)：眼神短暂柔和，嘴角仍压着，像想关心 Zack 又不愿直说；可配合递出旧照片。不能画成慈祥母亲式微笑。 |

### Mrs. O'Hara（新增 5 个）

| 资源名 | 表情描述 |
|---|---|
| `ohara_calm.png` | 平静/中立 (Calm / Neutral)：眼神自然平视，眉眼和嘴角放松，保持年长街坊的日常状态；不叼烟，不带警惕或算计，作为其他差分的基础版本。 |
| `ohara_wary_cigarette.png` | 叼烟警惕 (Wary Cigarette)：眼神从门缝或烟雾后打量来人，眉头轻压，嘴角夹烟；表现街坊对陌生访客的本能戒备。 |
| `ohara_chatty.png` | 街坊式健谈 (Chatty)：眉眼打开，嘴角带熟络笑意，像一句话能顺手带出三件邻里旧事；不要画成夸张大笑。 |
| `ohara_shrewd.png` | 市井精明 (Shrewd)：一侧眉毛挑起，眼神快速衡量对方，嘴角有若有若无的算计感；用于谈钱、抵押和 Silver Moon。 |
| `ohara_witness.png` | 收起玩笑的证人 (Matter-of-fact Witness)：笑意完全消失，眼神平直稳定，嘴唇收紧；只说亲眼看见的事实，不表现恐惧或戏剧化震惊。 |

### Leonard（新增 8 个）

| 资源名 | 表情描述 |
|---|---|
| `leonard_calm.png` | 平静/中立 (Calm / Neutral)：眼神平视，眉眼放松，嘴唇自然闭合；保留歪领带等固定外形，但不整理文件、不压袖口，作为职业面具以外的原始基础版本。 |
| `leonard_private_urgent.png` | 私下急切 (Private Urgency)：眉心收紧，眼神快速扫向四周，声音像压在喉咙里；身体靠近 Danny，急于确认 Frank 是否留下其他东西。 |
| `leonard_professional.png` | 银行职业面具 (Professional)：眼神平稳，嘴角维持职员式礼貌，表情没有温度；一只手整理文件、压平袖口或扶正歪领带，表现他靠流程维持控制。 |
| `leonard_guarded.png` | 合规防守 (Guarded)：眉眼略收，嘴唇平直，视线仍正面迎向 Zack；不是心虚躲闪，而是正在选择哪套银行话术可以挡住问题。 |
| `leonard_cracked.png` | 防线裂开 (Cracked)：眼神短暂失焦，嘴角僵住，压袖口的动作停在半途；像职业程序突然卡住，但很快还想恢复。 |
| `leonard_mechanical.png` | 机械招供 (Mechanical)：眼神变空，嘴唇僵硬开合，面部情绪被抽掉；用于承认行动、甩锅 Vinnie 等冷硬陈述，不能画成普通反派的愤怒。 |
| `leonard_pleading.png` | 体面崩塌后的哀求 (Pleading)：眉头上挑内收，目光追着 Edith，嘴角失去控制；第一次不再维护银行职员姿态，只想阻止妻子离开。 |
| `leonard_hollow.png` | 被抽空 (Hollow)：视线低垂或失焦，肩颈松下，嘴角没有张力；不是痛哭，而是所有辩护和期待都结束后机械地接受自首。 |

### Danny（新增 7 个）

| 资源名 | 表情描述 |
|---|---|
| `danny_calm.png` | 平静/中立 (Calm / Neutral)：眼神自然平视，眉眼放松，嘴唇闭合，站姿没有捂腹、堵门或撤退倾向；作为 Danny 未受压力时的基础版本。 |
| `danny_nervous.png` | 缺钱心虚 (Nervous)：眼神频繁偏开，眉头轻皱，嘴唇不安地抿住；被 Zack 撞见时身体僵住，像急着从现场撤走。 |
| `danny_sick_defensive.png` | 病弱防御 (Sick and Defensive)：脸色发白、额头冒汗，一手捂住腹部，另一侧身体仍挡着门；身体难受，但嘴上不肯示弱。 |
| `danny_contemptuous.png` | 轻蔑甩锅 (Contemptuous)：一侧嘴角下压或歪起，眼神带刻意放大的鄙夷；用于谈 Lula 时主动把她塑造成感情骗子。 |
| `danny_denial.png` | 大声否认 (Denial)：眉头压低，眼睛睁大，嘴巴张开反驳；声势很大但眼神不稳，表现他靠音量抢回控制。 |
| `danny_panicked.png` | 谎言失序 (Panicked)：眼神慌乱游移，额头汗意加重，嘴唇急促开合；被婚戒、房产证等证据连续逼迫后，语速和表情一起失控。 |
| `danny_defeated.png` | 失去退路 (Defeated)：眼神低垂，肩膀塌下，嘴角僵硬下沉；不是悔悟，而是发现已经没有可继续利用的人。 |

### Harold Moore（新增 5 个）

| 资源名 | 表情描述 |
|---|---|
| `moore_calm.png` | 平静/中立 (Calm / Neutral)：目光自然平视，面部放松，嘴唇自然闭合；不带热络笑容、傲慢俯视或权力得意，作为其他差分的基础版本。 |
| `moore_patronizing.png` | 热络俯视 (Patronizing)：笑容饱满但眼神没有真正看进对方，眉毛略抬，像在接待一个可以轻易打发的小人物。 |
| `moore_smug.png` | 权力得意 (Smug)：嘴角单侧上扬，下巴微抬，眼神享受规则带来的优势；不要画成街头恶棍式凶狠。 |
| `moore_cold.png` | 关闭热络 (Cold)：笑容瞬间消失，嘴角平直，目光变得功利而直接；表现他判断对方已没有可利用价值。 |
| `moore_rattled.png` | 被规则压住 (Rattled)：脸色发青，眼神短暂失稳，原本顺畅的笑停在脸上；被 Mickey 的律师身份和法院文件夺走控制。 |

### Lula Washington（新增 8 个）

| 资源名 | 表情描述 |
|---|---|
| `lula_calm.png` | 平静/中立 (Calm / Neutral)：眼神自然平视，眉眼放松，嘴唇自然闭合；不预设悲伤、眼泪或防御，作为 Lula 普通交流及其他情绪差分的基础版本。 |
| `lula_restrained_grief.png` | 克制悲伤 (Restrained Grief)：眼眶湿润但没有落泪，眉头轻轻内收，嘴角压住；像一直在努力把事实说完整。 |
| `lula_urgent.png` | 压住的急切 (Contained Urgency)：眼神牢牢看向 Zack，眉眼紧张，嘴唇刚结束一句便准备追问下一句；情绪不稳体现在节奏，不体现在哭喊。 |
| `lula_certain.png` | 悲伤中的笃定 (Certain)：眼神由下沉转为稳定，嘴唇收紧，像说出“Frank 不会做饭”这类她绝对确认的生活事实。 |
| `lula_resolute.png` | 放弃继承 (Resolute)：表情平静干净，眼神直视 Danny，嘴角没有胜利感；可配合签完文件、放下笔后抬头的姿态。 |
| `lula_tender.png` | 私人回忆 (Tender)：眼神柔和地落在铁盒、戒指或信件上，嘴角极轻微松开，悲伤之下短暂出现与 Frank 相处时的温度。 |
| `lula_breaking_tears.png` | 未来坍塌 (Breaking Tears)：泪水终于落下，眉头内收，嘴唇轻颤；不是嚎哭，而是读到情书后再也压不住的安静崩塌。 |
| `lula_farewell.png` | 平静告别 (Peaceful Farewell)：眼眶仍红但目光安定，嘴角带极淡、极短的温柔；用于墓地把“我爱你”完整说出口，没有胜利或释然过度。 |

### Earl “Stub” Hirsch（新增 6 个）

#### 角色基础需求（供美术）

| 项目 | 美术需求 |
|---|---|
| 角色定位 | 约 39 岁的德裔犹太移民第二代，Silver Moon 后场的赛马赌注簿记员。不是赌场老板、酒保或黑帮打手，而是依附在地下现金流里的小人物。第一眼应该让人想到“账房和电话”，不是“暴力和权力”。 |
| 体型与轮廓 | 小个子，身形偏瘦或紧缩，长期坐在卡座里使肩颈略向前。轮廓重心应落在低头、含胸、双手忙碌上，与 Tony 的迎客姿态和 Vinnie 的压迫体型明显区分。 |
| 年龄感 | 接近四十岁，但长期熬夜、接电话和核账让他看起来比实际年龄更疲惫。眼下可有轻微青黑，面部不能画成滑稽老头。 |
| 服装 | 核心识别物是衬衫袖箍。建议使用适合簿记工作的旧衬衫、马甲或便于坐姿工作的日常衣着，颜色压低；袖口和衣料可以略有磨损，但不能像流浪汉。不要穿赌场老板式华丽西装，也不要穿酒保围裙。 |
| 固定道具 | 短到快握不住的铅笔是最高优先级识别物；同时配置厚账本、赛马报纸、scratch sheet、三部电话和找零盒。L5 可增加酒瓶压住 scratch sheet。道具应表现真实工作关系，不能只作为背景装饰。 |
| 手部设计 | 手是 Earl 最重要的叙事部位。L2 的手一直在接电话、压账页、写数字、数钞票；L5 的手会蜷紧、压住或藏向身体一侧。表情差分若包含上半身，必须保证短铅笔和护手动作清晰可读。 |
| L2 整体状态 | 三部电话轮流响，Earl 几乎没有完整抬头的时间。身体前倾，注意力在听筒、账本和来客之间高速切换；忙乱但不笨拙，每个动作都熟练准确。 |
| L5 整体状态 | 电话全部安静，账本摊开，酒瓶压着纸。姿态从“向工作台前倾”变成“向自己内部收缩”，醉意只是提前麻醉，真正的情绪是等待双手被废的具体恐惧。 |
| 色彩建议 | 主题色使用铅灰色 `#4f5961`，可搭配旧纸张的灰黄、电话机的暗黑和低饱和酒渍色。整体不抢 Tony、Vinnie 的视觉焦点，但在手、铅笔和账页区域保留足够明度对比。 |
| 禁止方向 | 不画成精明圆滑的赌场老板，不画成笑脸酒保，不画成凶狠催债人，也不画成负责搞笑的忙乱账房。他的压迫感来自数字、电话和规矩；他的脆弱来自这些数字最终会落到自己的手上。 |

#### 表情资源

| 资源名 | 表情描述 |
|---|---|
| `earl_calm.png` | 平静/中立 (Calm / Neutral)：眼神自然平视，眉眼和嘴角放松，双手处于未工作的自然状态；保留轻微疲态，作为其他差分的基础版本。 |
| `earl_busy.png` | 多线忙碌 (Busy)：眉眼集中，视线落在账页与电话之间，嘴唇像在低声重复赔率；一手接听筒，一手握短铅笔，忙但不能慌。 |
| `earl_irritated.png` | 被打断 (Irritated)：眉头压低，眼神短促地瞥向来人，嘴角不耐烦地收紧；短铅笔停在账页上，像在嫌对方挡住电话线。 |
| `earl_calculating.png` | 数字聚焦 (Calculating)：一听到下注、欠账、找零或钞票号码，眼神立即清醒集中，眉心轻皱；不是侦探式怀疑，而是在心里核对账目。 |
| `earl_drunk.png` | 恐惧前的麻醉 (Drunk)：眼皮沉重，脸上有酒意，嘴部略松，但眼神仍知道自己在等什么；不能画成醉得滑稽或完全失去意识。 |
| `earl_guarding_hand.png` | 护手恐惧 (Guarding His Hand)：视线落在握笔的手上，眉头内收，嘴唇紧抿，手指蜷紧或被另一只手护住；恐惧必须具体指向“这双手今晚可能保不住”，不做泛化惊恐。 |

### Tony（新增 5 个）

| 资源名 | 表情描述 |
|---|---|
| `tony_calm.png` | 平静/中立 (Calm / Neutral)：眼神自然平视，眉眼放松，嘴唇闭合；不带招呼客人的职业笑容，也不擦杯，作为 Tony 脱离生意动作后的基础版本。 |
| `tony_business_smile.png` | 生意笑脸 (Business Smile)：嘴角熟练上扬，眼神却在观察客人和周围动静；可配合持续擦杯的手部动作。 |
| `tony_observant.png` | 记录细节 (Observant)：笑容仍在，眼神轻微偏向目标，眉眼更集中；像把钞票、打火机和客人的话都记进心里。 |
| `tony_serious.png` | 笑意收敛 (Serious)：嘴角慢慢放平，视线稳定下来；用于谈 Vinnie 与 Leonard 的过去，说明这件事超出普通酒吧闲谈。 |
| `tony_conflicted.png` | 停顿后放手 (Conflicted)：擦杯的动作停住，眼神短暂落向 Vinnie，嘴唇仍闭着；不是震惊，而是明白对方正在做什么后选择照办。 |

### Vincent “Vinnie” Moretti（新增 6 个）

| 资源名 | 表情描述 |
|---|---|
| `vinnie_calm.png` | 平静/中立 (Calm / Neutral)：眼神自然平视，眉眼和嘴角放松，身体没有封闭或警戒倾向；保留手掌烫疤等固定特征，作为其他差分的基础版本。 |
| `vinnie_closed.png` | 封闭沉默 (Closed-off)：眼神低垂或落在琴键、酒杯上，嘴唇平直，肩膀略向内收；像主动把自己从酒吧人群里隔开。 |
| `vinnie_wary.png` | 警觉抬眼 (Wary)：头部动作很小，只有眼神突然抬起锁定 Zack，眉头轻压；表现他一直在听，但不愿参与。 |
| `vinnie_cold.png` | 冷硬否认 (Cold)：眼神正面迎向质问，嘴角没有张力，面部几乎不动；不能出现被冤枉者式激动。 |
| `vinnie_pressured.png` | 被逼到节点 (Pressured)：眼神短暂偏向 Tony 或出口，嘴唇微张后重新抿住，手部动作停下；不是普通破防，而是在判断是否该抢过结局。 |
| `vinnie_decisive.png` | 表演性决绝 (Performative Resolve)：眼神异常稳定，下巴略抬，嘴部张力增大，像主动把周围所有人变成观众；认罪时语速可以快，但不能含泪、崩溃或表现爱情。 |

### Dr. Foster（新增 4 个）

| 资源名 | 表情描述 |
|---|---|
| `foster_calm.png` | 平静/中立 (Calm / Neutral)：眼神自然平视，面部肌肉放松，嘴唇自然闭合；不带通宵疲态、职业锐利或冷淡不耐烦，作为其他差分的基础版本。 |
| `foster_tired.png` | 通宵疲惫 (Exhausted)：眼皮沉重，眼下疲劳明显，嘴角松下；可配合打哈欠或靠门框，但不能显得意识模糊。 |
| `foster_sharp.png` | 信息锋利 (Sharp)：眼神突然聚焦，眉眼收紧，嘴角平直；一谈到尸检报告和证据，疲态立即退到背景。 |
| `foster_dry.png` | 冷淡直白 (Dry)：眼神平视，表情几乎没有起伏，嘴角略带不耐烦；她只给结论，不负责安慰人。 |

### Edith（新增 6 个）

| 资源名 | 表情描述 |
|---|---|
| `edith_calm.png` | 平静/中立 (Calm / Neutral)：眼神自然平视，眉眼和嘴角放松，保持端正贵妇姿态；不带社交笑容、嫌恶或切割意味，作为其他差分的基础版本。 |
| `edith_social_smile.png` | 贵妇社交面具 (Social Smile)：嘴角得体上扬，眼神维持礼貌距离，姿态像准备接受记者采访；笑意精致但没有亲近感。 |
| `edith_appraising.png` | 衡量来客 (Appraising)：一侧眉毛轻抬，目光从 Zack、Emma 移到文件，嘴角仍保持礼貌；像在判断来人对她的体面有多大威胁。 |
| `edith_distancing.png` | 迅速撇清 (Distancing)：笑意收住，下巴略抬，眼神冷下来；得知搜查令后立即把 Leonard 从“丈夫”变成需要切割的麻烦。 |
| `edith_disgusted.png` | 嫌恶 (Disgusted)：眉头轻皱，鼻翼和上唇略收紧，眼神不愿再落在 Leonard 身上；不能画成害怕被牵连的慌乱。 |
| `edith_cutting.png` | 尖锐离场 (Cutting)：眼神冷硬直视，嘴角绷紧，带已经作出决定后的刻薄确定性；可配合握住行李箱、身体朝出口转开的姿态。 |

---

## 四、不纳入本表的资源

- Frank Kowalski 主要通过遗物、证词、照片和闪回建立人物，不新增常规 AVG 站立表情；如闪回需要独立画面，归入 Unit2 闪回或特殊场景需求。
- 法院守卫等只有单次场景姿态的功能性人物沿用场景 NPC 或特殊事件资源，不扩展成完整表情组。
- 电话中的 Foster、远端声音和无实体出场台词不单独制作表情。
- `emma_intervene_morrison_001.png`、`evt_l5_vinnie_confession.png` 等已经归入突发事件或场景 NPC 的画面，不在本表重复列为通用表情资源。

---

## 五、制作边界

- 每个角色必须有一张 `角色名_calm.png` 基础表情。Zack、Emma、Morrison 沿用 Unit1，Mickey 使用本表已有的 `mickey_calm.png`，其余 U2 新角色均在本表单独列出。
- 同一个表情资源应能跨相近对白节点复用，不为每句台词制作一张差分。
- 复合状态必须保留主要信息。例如 Zack 的“含泪释然”不能拆成普通开心或普通哭泣，Emma 的“红眼不甘”不能直接使用单纯悲伤。
- Leonard、Mickey、Vinnie、Lula 的核心情绪以克制为主。除明确写出外，不增加咆哮、嚎哭、夸张惊恐等状态。
- 姿态只在承担叙事信息时写入表情：Leonard 压袖口、Tony 停止擦杯、Danny 捂腹、Lula 签字后抬头等必须保留；普通挥手、摊手不单独拆资源。
- Mickey 的资源名和画面不能出现 Whale、阴谋者、反派等提前暴露身份的信息。
- Vinnie 的认罪状态不能出现眼泪、深情凝视或直接的爱情表达；他的情绪只能通过停顿、语速和决绝程度体现。
