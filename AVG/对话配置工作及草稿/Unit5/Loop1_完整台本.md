# Unit5 · Loop1 完整对白｜第一版

> 2026-09-15。供用户审阅的完整工作稿。主模型依现行大纲、State与最新人物档案写初稿；三个场景包分别经 NovAI `[次]gemini-3.8-flash` 润色一轮，再由主模型逐句修正事实、限定词与衔接偏差。保留原始初稿与 Gemini 原始输出，本文不是未经修正的 Gemini 原稿。
>
> 包含七段开场、四名自由问话NPC、两个首次入场事件、手帕关系选择、十二个调查反馈、四名NPC回访短开场、三轮指证及收束。角色名使用英文，保留动作、表情与必要画面需求。
>
> 这是对白草案，尚未同步 AVG JSON、预览表或 Unity。`@` 是台本控制意图；入口沿用现行 State 逻辑名，不代表已分配正式 Talk ID。回访与调查调用备注交由后续配置落实；普通动作和必须画面的制作、时长仍待演出验收。

## 阅读顺序

1. 开场：医院决裂 → Watts 留信 → 赶路广播 → 序幕短回扣 → 二楼误认 → 破门后双曝光 → 圆桌规则。
2. 自由探索：四名NPC问话、两处相遇、手帕选择及调查反馈；按地点分组展示，允许玩家换序。
3. 指证：鬼影身份 → 镜面方向 → 镜后路程；之后留下楼梯变化的下一轮问题。

---

# 一、开场连续段

## Talk: L1_opening_hospital_break.json

【场景】圣心医院急诊室外。急诊门刚合上。Emma 留在门前，Zack 走近时，她抬手挡住他的去路。她的目光停在他手里的材料上。

**Zack Brennan** [看了一眼急诊门]
> Rosa 那边怎么样？

**Emma O'Malley**
> 通知过了。Sarah 留在 Rosa 那里，不回去，也不碰那边的水。

**Zack Brennan**
> 好。那我去——

**Emma O'Malley** [没有让开]
> 车里那几页。拿来。

**Zack Brennan** [手指收紧，随即松开]
> Emma。

**Emma O'Malley**
> 别这么叫我。刚才在路上，你怎么跟我说的？有人要把 O'Hara 强撵走，对吧？
> 你可没提过水里被人下了东西。

**Zack Brennan**
> 水源那页，我看到了。

**Emma O'Malley**
> 在车上就看到了？

**Zack Brennan**
> 是。

**Emma O'Malley** [把目光从纸上移到他脸上]
> 那你还看着我一路盘算怎么劝他搬家。
> 我们本来可以一起看，可以早点找人去查水源。你一个字都没吭。

**Zack Brennan**
> 我当时以为还来得及。

**Emma O'Malley**
> 你以为。你顺便把我也给“以为”进去了。

【演出】走廊安静下来。Emma 伸出的手仍停在两人之间。Zack 把水源材料递过去，她接住，却看见余下页面中的名字。

**Emma O'Malley** [声音压低]
> ……Sean？
> 怎么会有我爸的事？

**Zack Brennan**
> 当年的旧报告有问题。它跟 Miller、TideWater 的材料连得上，有些联系被遮住了。
> Sean 的死，不能再按一场普通事故归档。

**Emma O'Malley**
> 你手里攥着这个，跟我说了多少次“还得再查查”？

**Zack Brennan**
> 证据链条还没闭合。就凭这薄薄几张纸，定不死老 Charles 到底干了什么。

**Emma O'Malley**
> 我没问你案子。我问你凭什么瞒着我。

**Zack Brennan** [避开她的目光，又看回来]
> 我怕你一看到，就会继续追下去。
> Harrison、Morrison、还有 Mickey……一个接一个全折进去了。我不能眼睁睁看着名单上再添一个你。

**Emma O'Malley**
> 所以你就擅自替我做主，把我的名字从里面划掉？

**Zack Brennan**
> 材料是我压下的。对。

**Emma O'Malley**
> 查 Mary 那案子的时候，你怎么答应我的？你说过绝不再把真相挑挑拣拣留给我。

**Zack Brennan**
> 我没忘。

**Emma O'Malley**
> 那你就是故意的。

【演出】Zack 将剩余页面全部递出。Emma 接过，低头检查。Zack 想扶住滑落的纸角，手伸到一半又停下。

**Zack Brennan**
> 我手头所有关于这两边的东西，全在这儿了。
> ……对不起。

**Emma O'Malley** [把纸页拢齐]
> 现在舍得给我了？
> 非得等 O'Hara 被抬进抢救室，非得等我当场撞破，你才肯拿出来。

**Zack Brennan**
> 确实不该拖到现在。

**Emma O'Malley**
> 你明明知道 Mickey 错在哪儿，可一落到我头上，你就觉得自己有资格替我决定，是吧？

【演出】Zack 没有回答。Emma 将材料抱在身前，转身向走廊出口走去。Zack 跟出半步。

**Zack Brennan**
> Emma，等等——

**Emma O'Malley** [回头，第一次提高声音]
> 别跟过来。

【演出】Zack 停住。Emma 离开，急诊门仍关着。他低头看着空下来的手。

@next L1_opening_office_departure

## Talk: L1_opening_office_departure.json

【场景】Watts 办公室。Zack 推门进来，在空椅子前停了一下。Watts 从桌后抬头。

**Zack Brennan**
> Emma 来过？

**Watts**
> 把材料理了一遍，就走了。这是留给你的。

【演出】Watts 将纸条推过来。Zack 没坐，站着读完。

【纸条｜Emma 留给 Zack；不入背包】
> 我们没有办法再一起共事了。现在，我没有办法相信从你嘴里说出的真相。
> 接下来的路，我只能一个人走。

**Watts** [等他放下纸条才开口]
> 先坐会儿吧。

**Zack Brennan**
> 她走的时候说什么没有？去哪儿？

**Watts**
> 没留地址。

**Zack Brennan** [慢慢折起纸条]
> 行。那就对一下东西。她带走了哪几份，今晚这时间能去堵谁。

**Watts**
> 挑出来的还是那叠旧卷宗，加上 Miller 相关的记录。你看看这张公开日程。
> 慈善纪念晚宴，在 Miller 庄园。

**Zack Brennan**
> 老 Charles 今晚在那儿。

**Watts**
> 按行程表看，人在。她要是打算当面去要说法，很可能往那儿去。

**Zack Brennan**
> 我去庄园。

**Watts**
> 丑话说在前面，这只是按逻辑推出来的去处，回头到了地方别跟人说是我打包票的。

**Zack Brennan**
> 心里有数。你呢？

**Watts**
> 我留在这里。她走前交待了我一件事，手续还没办完。

**Zack Brennan** [看他一眼，收好纸条]
> 行，你忙你的。

**Watts**
> 外头雪大，开车慢点。

【演出】Zack 拉开门离去。Watts 把公开活动安排收回桌边，继续手头的工作。

@next L1_opening_drive_broadcast

## Talk: L1_opening_drive_broadcast.json

【场景】赶路车内。风雪掠过挡风玻璃，Zack 独自开车。无线电的声音夹着杂音。

**Radio Announcer**
> 本台插播《艾斯弗德晚报》现场快讯。
> 今晚，Miller 庄园举行的慈善纪念晚宴突发混乱。一名年轻女性记者在未经主办方邀请的情况下强行闯入会场，当众对 Charles Miller 先生发难，声称其与十六年前的一桩旧案死亡有关。

【演出】Zack 的视线仍盯着前方，握方向盘的手收紧。

**Radio Announcer**
> 截至发稿，Miller 家族尚未作出正式声明。本报特此提醒公众，针对一位多年来持续资助本市医疗与教育事业的知名慈善家提出如此严重的指控，应当拿出确凿证据，而不是任由情绪宣泄。

**Zack Brennan** [低声]
> 她当面问了什么，你怎么一个字都不敢念？

**Radio Announcer**
> 目前现场秩序正在恢复。关于该名女记者过激举动的后续进展，本台将持续跟踪报道。

【演出】车驶抵庄园。Zack 停车，推开车门，迎着门口方向开口；无线电仍在响。

**Zack Brennan**
> 别拦着。Zack Brennan，私家侦探，我要进去。

**Radio Announcer**
> 另据前线最新消息——目前又有一名私家侦探强行要求进入庄园。

【演出】Zack 回头看了一眼车里的无线电，随即关上车门。画面转场，不增设门口问答。

@next L1_opening_prologue_callback

## Talk: L1_opening_prologue_callback.json

【场景】既有序幕短回扣，约 8—12 秒；声音与画面重叠，随后回到二楼走廊现在。

【突发事件需求｜必须画面呈现】触发位置：抵达庄园后的短回扣；画面必须让玩家看见：明晨新闻通稿的“CONFIRMED SPEAKER / MISS EMMA O'MALLEY”，老 Charles 借资助施压的既有对峙，最后是记者闪光灯；承载的信息：Emma 的演讲被预先安排，Zack 未能阻止；接回对白的位置：L1_opening_upstairs_interruption。

**Charles Miller Sr.** [既有序幕声画摘句]
> Miller 基金付过你的学费。

**Emma O'Malley** [既有序幕声画摘句]
> 学费不是买断。

**Charles Miller Sr.** [闪光灯亮起前，面向全场]
> 我给你们全城最大的讲台。

【演出】闪光消退，接二楼窗玻璃上的冷光。Zack 独自站在窗前，手里一支烟。

@next L1_opening_upstairs_interruption

## Talk: L1_opening_upstairs_interruption.json

【场景】庄园二楼走廊，22:00 前。窗外风雪渐密。小 Charles 走近，先看见 Zack 的背影。

**Charles Miller Jr.**
> Lawson？

【演出】Zack 转身。小 Charles 停了一瞬，歉意地抬了抬手。

**Charles Miller Jr.**
> 抱歉，Brennan 先生。这边光线暗，背影和衣服轮廓看着又像，我给认岔了。

**Zack Brennan**
> 我不是他。

**Charles Miller Jr.** [看见烟，给他留出一点距离]
> 楼底下闹得头疼吧？

**Zack Brennan**
> 托你们的福，这会儿挺清静。

**Charles Miller Jr.**
> 我是指明早那个发言。走到这一步，大家脸上都不好看。

**Zack Brennan**
> 你父亲看起来倒是游刃有余。

【演出】小 Charles 没接这句，转向窗外。Zack 顺着他的视线，看见西丘上模糊的建筑轮廓。

**Zack Brennan**
> 山坡上那栋是什么？

**Charles Miller Jr.**
> Miller 飞行机械馆。小时候我父亲特意盖的。
> 早就封馆了。

**Zack Brennan**
> 这雪要是再大点，轮廓都看不着了。

**Charles Miller Jr.**
> 可不是么。

【演出】小 Charles 收回视线，重新面对 Zack。

**Charles Miller Jr.**
> 对了，您刚才进门急，底下人可能没说清楚。庄园原则上不准宾客携枪。武器留在门口，归 Pierce 管理。

**Zack Brennan**
> 身上没带。

**Charles Miller Jr.**
> 这样最好。照章办事，先跟您打个招呼。

【演出】警员快步走进走廊，停在两人面前。

**Patrol Officer** [喘息未平]
> 小 Miller 先生！大礼堂出大事了……舞台那边，您父亲他——

**Charles Miller Jr.** [脸上的客气退去]
> 怎么了？说清楚。

**Patrol Officer**
> 发现尸体了！刚才闹事的那个女记者也在场，就是 Emma O'Malley，手里还攥着凶器！

**Zack Brennan**
> 她人呢？还喘气吗？

**Patrol Officer**
> 晕死过去了。Pierce 长官说她搞不好——

**Zack Brennan** [掐灭烟，已朝来路走去]
> 别废话，带路。

@next L1_opening_stage_exposures

## Talk: L1_opening_stage_exposures.json

【场景】礼堂入口接舞台。门闩破坏痕迹留在门内。警员把守入口，Zack 与小 Charles 赶到。

**Pierce**
> 门口守住。通知庄园里其他人，别让他们自己闯进来。

**Zack Brennan**
> 门是怎么破开的？

**Patrol Officer**
> 刚才整十点撞开的，里面下了内闩。我在门槛外就瞧见地上的情况了，第一时间封死出入口，这才放法医和急救的人进来。

**Charles Miller Jr.**
> 我来协调外围。办正事的人先进。

【演出】Zack 走到 Emma 身旁，蹲下。她握着餐刀，昏迷不醒。Foster 正在查看现场。

**Zack Brennan** [低头靠近她]
> Emma。能听见我说话吗？

**Eleanor Foster**
> 呼吸还在。别晃她，手里的刀先不要碰。

**Zack Brennan** [停住手]
> ……我在这儿。

【演出】Emma 没有回应。Zack 留在她身侧。Vivian 与 Lawson 赶到，Moore 落在后面，停在众人外侧。

**Vivian** [先看 Zack，随后看见 Emma，声音一下低了]
> Zack？……怎么 Emma 也倒在这儿？

**Zack Brennan**
> 人还没醒。

**Vivian** [把原本要上前的脚收住]
> 好……你别乱动她。

**Lawson Vanderbilt** [朝入口的警员，话说得急]
> 联系 TideWater 的公司律师！告诉他们，文件暂时别放行，先等等。

**Pierce**
> 知道了！所有人退开点，别围着碍事。

【演出】时间过渡至 22:10。摄影师在舞台正面固定相机。Foster 示意小 Charles 看向景墙编号。

**Eleanor Foster**
> Charles，看到 C-3 那块背景板了吗？绕到后面去帮我打光。

**Charles Miller Jr.** [循她指的方向走去]
> 打这边穿过去？

**Eleanor Foster**
> 对，顺着边沿拐。光对着我检查的位置。

**Lawson Vanderbilt** [在 C-3 正面靠近，低下身]
> 他真的……这就彻底断气了？

**Eleanor Foster**
> 已经没有生命体征了。就留在那儿，不要再往前凑。

【演出】Lawson 停在景墙正面暗角附近。小 Charles 已被景墙挡住。Zack 仍照看 Emma，其他可见人物维持各自位置。

**Photographer**
> 十点十分，第一张底片。所有人站住别动。

【突发事件需求｜必须画面呈现】触发位置：第一张曝光及其后的换片；画面必须让玩家看见：固定的正面相机、Emma 与 Zack、C-3 正面的 Lawson、其他可见人物与当前楼梯，小 Charles 绕至景墙背面后被遮挡；换片时相机与舞台装置不动，众人可见站位保持；承载的信息：两次曝光是同一现场的连续记录；接回对白的位置：摄影师宣布换片。画面保留正常全景，不追加暗角动作或局部解读。

**Photographer** [完成曝光，着手换玻璃底片]
> 准备换片。千万别碰脚架，台上的摆设谁也别挪。

**Zack Brennan** [仍蹲在 Emma 身边，抬头看 Foster]
> 她这样还能在这里留多久？

**Eleanor Foster**
> 我一直在看着。先让她保持平躺。

【演出】换片与等待以连续站位的短过渡呈现。Foster 继续勘验，不移动舞台装置。时间过渡至 22:15。

**Photographer**
> 十点十五分，第二张。

【演出】第二次曝光完成。摄影师收妥底片。

**Pierce**
> 拍完了就挪步，去圆桌会议室。都过去，别在这儿杵着。

**Zack Brennan** [没有立刻起身]
> Emma 怎么处理？

**Eleanor Foster**
> 我守着她。你去你的。

【演出】Zack 又看了 Emma 一眼，起身。众人离开舞台，转入圆桌会议室。

@next L1_opening_roundtable_rules

## Talk: L1_opening_roundtable_rules.json

【场景】圆桌会议室。Pierce 站在秩序端，Zack 尚未坐下。Vivian、Lawson 分处两侧，小 Charles 居中。

**Pierce**
> Emma O'Malley 必须逮捕。前脚刚在大庭广众之下跟死者起冲突，后脚就倒在尸体旁边，手上的餐刀和伤口吻合。

**Zack Brennan**
> 案发那会儿，你查过还有谁进过那道门吗？

**Pierce**
> 大礼堂的主出入口从头到尾是我亲自盯的，我一分钟都没离开过。

**Zack Brennan**
> 那就先查你眼皮底下有没有漏掉什么。怎么，连这个环节都想跳过去？

**Pierce**
> 你这是打定主意要替嫌犯开脱了？

**Zack Brennan**
> 我是要弄清楚到底还有没有第三个人在场。至于她手里抓着凶器，我一个字也没替她否认。

**Vivian**
> 人在地上还没醒呢，你们倒好，先把罪名给她扣严实了。现场到底什么样，总得让人查明白吧？

**Lawson Vanderbilt** [抬起头]
> 查明白？然后呢？庄园由着他满世界翻，连带着把公司的公司文件也顺手牵走？

**Vivian**
> 谁说要拿公司文件了？

**Lawson Vanderbilt**
> 查着查着不就奔那儿去了么！
> 我先把话挑明了，Brennan，晚宴开场前我是跟老 Charles 大吵了一架。老头子把那一烂摊子破事全甩给我，我咽不下这口气，当面说了。怎么着，这也打算算到我头上？

**Zack Brennan**
> 你们吵了什么我自然会问。但这不代表你坦白两句，我就得凭空给你栽个杀人罪名。

**Lawson Vanderbilt**
> 嘴上说得轻巧。Miller 家出了这么大的漏子，我可信不过你到处乱翻。
> 反正 TideWater 的公司文件先封存，等公司律师来了再说。名义上那破总裁是我顶着的，东西让你抄走了，回头吃官司的可是我。

**Charles Miller Jr.** [等 Lawson 说完才开口]
> 封存文件的事照 Lawson 说的办。但我父亲不能死得不明不白，总得有个交代。
> Brennan 先生，查案的事拜托您。

**Lawson Vanderbilt** [看向小 Charles，又转回 Zack]
> 行啊，查可以，话得摊在桌面上。
> 每次查完，要拿材料作判断，都得回到大家面前讲清楚。别跟 Pierce 俩人关在屋里把口径串好了，再出来给我们下判决书。

**Charles Miller Jr.**
> 这个要求很公道。您随时可以找在场的任何人对质，也包括 Pierce。既然是奔着真相去的，就不能光挑一部分人的证词来审。

**Zack Brennan**
> 找到东西我会摆在桌上，大家当面对账。

**Vivian**
> 那还不赶紧让他回现场看？

**Pierce**
> 案子可以接着查，但 Emma 现在就得逮捕——

【突发事件需求｜必须画面呈现】触发位置：Pierce 坚持逮捕后；画面必须让玩家看见：小 Charles 看向 Pierce，Pierce 察觉这一眼，停顿后改变安排；承载的信息：Pierce 的处置受到小 Charles 非公开示意影响；接回对白的位置：Pierce 改口安排客房看守。

**Pierce** [停顿，看向门口，再开口时语气已变]
> ……先把她抬去东侧的独立客房。门外留人看守，等人醒了再说。

**Zack Brennan**
> 还没醒？

**Pierce**
> 没醒。现在谁也别去碰她。

**Charles Miller Jr.**
> 那就先这么定。各位有什么想法，咱们就留在台面上把话讲透。

【演出】Zack 拉开椅子，却没有坐，转身去往调查区域。

@exploration


---

# 二、自由探索与调查反馈

## Talk: L1_talk_stage_medical.json

【场景】舞台正面。Foster 在伤情记录上落笔。Zack 走近时，她用手挡住了纸边被带起的风。

**Eleanor Foster**
> 往边上站站。纸要吹翻了。

**Zack Brennan** [往侧面让开]
> 那把餐刀，对过了？

**Eleanor Foster**
> 对过，餐刀与伤口吻合。

**Zack Brennan**
> 纸上这几行，你能敲死的有哪几句？

**Eleanor Foster** [停笔，抬眼看着他]
> 初步能确认，直接致命的是刀刺。先听完整，Brennan。
> 至于掉下来和挨刀哪个在前……我这儿还没落笔。

**Zack Brennan**
> 所以那格空着。

**Eleanor Foster**
> 没定论的东西不空着留给谁？你拿去问别人可以，嘴里别把“初步”两个字吃了。

@get testimony:5051001

**Zack Brennan** [收回看记录的视线]
> 知道了。你写你的。

**Eleanor Foster**
> 现场随便你复核。但别拿我查到一半的草稿，到处当结论使。

@end

### 回访短开场（同一问话入口的文字草案）

**Zack Brennan**
> 你能确认的部分，我再对一遍。

**Eleanor Foster**
> 看吧。别自作主张往空白处填字就行。

【回访续接】接正文“纸上这几行，你能敲死的有哪几句？”；复述同一证词，已取得时不重复发放。

## Talk: L1_event_handkerchief_boundary.json

【场景】玩家查看伤情记录旁的白色医用手帕后触发。Foster 在旁。

【突发事件需求｜必须画面呈现】触发位置：关系选项出现前；画面必须让玩家看见：白色医用手帕上的“E.F.”绣字及它与 Foster 记录的相邻位置；承载的信息：手帕归属 Foster；接回对白的位置：Zack 内心辨认。两条选择共用同一特写。

**Zack Brennan** [内心]
> E.F.……Foster 的东西。

**Eleanor Foster** [抬眼]
> 怎么，看什么呢？

@choice foster_attitude
@opt "把手帕递还，只记录她能确认的部分。" -> foster_restraint
@opt "要求她现在就把死亡顺序写出来。" -> foster_pressure

@path foster_restraint

**Zack Brennan** [将手帕递过去]
> 你的手帕，压在记录边上了。

**Eleanor Foster** [接回手帕]
> ……多谢。手头这页还没弄完。

**Zack Brennan**
> 能定下的就先记刀伤。先后顺序证据不够，空着就空着吧。

**Eleanor Foster** [肩膀略微松下来，重新拿起笔]
> 这样我省心不少。

**Zack Brennan**
> 不逼你签字画押。

**Eleanor Foster**
> 你查你的去吧。我尽快把手头这截收尾。

@set u5_foster_hint=true
@goto foster_event_end

@path foster_pressure

**Zack Brennan** [目光停在未填的记录上]
> 人已经被圈在屋里了。你先把先后顺出来，我好拿回圆桌对账。

**Eleanor Foster**
> 拿什么顺？我手里的东西还没过完。

**Zack Brennan**
> 多少给个倾向。总这么悬着那一栏，谁也走不下去。

**Eleanor Foster** [把记录收回自己面前，声音未提高]
> 能确认刀刺直接致命。坠落和刀创哪个在前，没验完就是没验完。
> 你急着用个由头去交差，我就该拿自己的名字陪你押宝？

**Zack Brennan** [停了片刻]
> ……行，我看别处。

**Eleanor Foster**
> 请便。

@set u5_foster_hint=false
@goto foster_event_end

@label foster_event_end
@end

## Talk: L1_talk_corridor_watch.json

【场景】礼堂入口走廊。Pierce 站在值守位置。Zack 走来，他侧过身，没有离开。

**Pierce**
> 怎么，是来翻我的哨？要问什么直接问。

**Zack Brennan**
> 案发那阵子，你在这条道上看到谁了？

**Pierce** [看向走廊深处]
> 有个警员抽着烟打这儿走过去，随后就没影了。

**Zack Brennan**
> 熟面孔？

**Pierce**
> 抬手那下子……看着像 Morrison。

**Zack Brennan** [等了一拍]
> Morrison 已经死了。

**Pierce**
> 废话，我能不知道？

**Zack Brennan**
> 你看清脸了？

**Pierce**
> 我看的是手！左手拿着烟。Morrison 以前也是左撇子。
> 随后就在走廊尽头没影了。我都怀疑自己见了 Morrison 的鬼魂，要不怎么解释？

**Zack Brennan**
> 这茬是在你打点前，还是打点后？

**Pierce**
> 前后脚。低头前有个警员过去，等我签完一抬头，就是那个左手抽烟的人影，接着就不见了。

**Zack Brennan**
> 你低头多久？

**Pierce**
> 签字打点能多久？就那一下，十四秒，纸带上有记录。

**Zack Brennan**
> 我按你看见的写。至于是不是 Morrison，另算。

@get testimony:5031001

**Pierce** [将目光收回来]
> 随你的便。反正我没擅自离开过岗位。

**Zack Brennan**
> 那我就先在你站的这块地方找找看。

@end

### 回访短开场（同一问话入口的文字草案）

**Pierce**
> 又怎么了？刚才哪句没听懂？

**Zack Brennan**
> 抽烟那个人。你再从头捋一遍。

【回访续接】接正文“有个警员抽着烟打这儿走过去，随后就没影了。”；同一证词已取得时不重复发放。

## Talk: L1_event_c3_encounter.json

【场景】首次走进 C-3 景墙背面。Zack 从开放末端绕入，看见支架旁的小 Charles。

**Charles Miller Jr.** [侧身让路]
> 留神脚底下，别绊着。

**Zack Brennan** [停在支架外侧]
> 没事。C-3……后头全是撑架。

**Charles Miller Jr.**
> 贴着外边走还宽敞点。刚才那一窝蜂的人，挤得转不开身。

【演出】Zack 看向来路，又看小 Charles。他没有追问对方为什么在这里。

**Charles Miller Jr.**
> Emma 小姐……人还没醒吧？

**Zack Brennan**
> 没。

**Charles Miller Jr.** [低头片刻]
> 唉，我都不知道该先顾哪头。父亲就那么躺在那儿，你们喊她，她又没个动静……

**Zack Brennan**
> 乱成那样，总得先顾活着的。

**Charles Miller Jr.**
> 也是。能理解。

**Zack Brennan**
> 既然你放话让我查，我就接着往下摸了。

**Charles Miller Jr.**
> 只要有用，随时问我。父亲到底是怎么走的，我也想讨个明白。

【演出】小 Charles 让开开放末端，Zack 留在景墙背面继续查看。构图让 C-3 编号、背面支架与末端关系可读。

@end

## Talk: L1_event_backstage_warning.json

【场景】舞台后台转角。Zack 尚未转出时，先听见 Vivian 和小 Charles 的说话声。

**Charles Miller Jr.** [声音温和]
> Vivian，方才在前面你替他们出头，我全听在耳朵里。既然案子已经准了去查，你也该分分心，想想手底下这帮人。

**Vivian**
> 正是因为我还得对他们负责，今晚这事才不能糊弄过去。

**Charles Miller Jr.**
> 你的心是好的。只是 Brennan 和 Emma 的事，犯不上总由你往火坑前头凑。晚宴砸了，后面这一大家子，全指着你拿主意安顿呢。

【演出】Zack 转过拐角。Vivian 先看见他，话停住。小 Charles 顺着她的视线转头。

**Charles Miller Jr.** [自然接回另一个话题]
> 剩下的尾巴，回头就全托给你了。

**Vivian** [把目光移回他身上]
> 放心吧，大家还等着呢，我会处理。

**Charles Miller Jr.**
> Brennan 先生。正聊着晚宴收场的事呢。

**Zack Brennan**
> 听着了。

【演出】短暂安静。Vivian 整理了一下自己的袖口，面对 Zack。

**Vivian**
> 查你的案子去吧。这边的碎摊子用不着你插手。

**Zack Brennan**
> 行。

@end

## Talk: L1_talk_security_patrol.json

【场景】安保室。巡逻警员站在桌边，Zack 走近。此开场不依赖已问过 Pierce。

**Zack Brennan**
> 礼堂外边那条走廊，今晚是你当值巡的？

**Patrol Officer**
> 是我啊，一直打入口那头晃过来。

**Zack Brennan**
> 走一趟大概多久？

**Patrol Officer**
> 晃到礼堂门口？二十秒上下吧，就平时巡街的步子。

**Zack Brennan**
> 走到当中那面镜子呢？

**Patrol Officer**
> 入口过去约十秒。
> 反正第十三圈的时候我走到镜子边上，正好看见 Pierce 低着头签字打点。

**Zack Brennan**
> 这圈你怎么记得这么死？

**Patrol Officer** [右手自然伸入制服右袋，取出烟草]
> 嗨，走到那儿烟瘾上来了，顺手掏包烟。喏，就这口袋。

**Zack Brennan** [视线落在他的手上]
> 当时也是拿这只手掏的？

**Patrol Officer**
> 右手啊。我干啥不都用右手么。

**Zack Brennan**
> 烟搁右边兜，拿右手掏。

**Patrol Officer**
> 昂。谁没事还反着手绕一大圈去掏兜啊，那不多别扭。

**Zack Brennan** [收起视线，记下回答]
> 行。就按你走的路线和动作记。

@get testimony:5111001

**Patrol Officer**
> 差不多就这些。别的我也没长三只眼。

@end

### 回访短开场（同一问话入口的文字草案）

**Zack Brennan**
> 走廊巡逻的那几步，再跟我顺一遍。

**Patrol Officer**
> 成啊，还从入口那边算起？

【回访续接】接正文“走一趟大概多久？”；同一证词已取得时不重复发放。若烟草尚未取得，沿用右袋右手动作；若已交给 Zack，则不再演取烟，改为警员口述“当时从右袋拿的，一直用右手”，回查同一事实。

## Talk: L1_talk_roundtable_noise.json

【场景】圆桌会议室。Lawson 独坐在桌边。Zack 靠近时，他把视线从别处转回来。

**Lawson Vanderbilt**
> 怎么，排到审我了？

**Zack Brennan**
> 刚才在圆桌上，你说开席前吵过一架。

**Lawson Vanderbilt**
> 公事公办的争执。多少人听见了，有什么好捂着的？
> 再说了，我今晚被硬塞过来的麻烦事，可不止这一件。

@label lawson_hub
@branch lawson_hub
@opt "除了争吵，案发前还有什么动静？" -> lawson_noise
@opt "老 Charles 交给了你什么工作？" -> lawson_archive
@opt "先到这里。" -> lawson_end

@path lawson_noise

**Zack Brennan**
> 案发前，还有别的动静没？

**Lawson Vanderbilt** [迟疑，带着不愿沾手的表情]
> 不是……别人屋里的私事，你也要我当口供交代？

**Zack Brennan**
> 先把你耳朵听到的说出来。

**Lawson Vanderbilt**
> 地板底下，先是一阵很急的碎步，接着“咚”地闷响了一下，像撞着哪儿了。
> 楼下就是 Vivian 的房间。依我看八成是哪个客人私下过去，她又不想摆上台面。

**Zack Brennan**
> 你撞见那个客人了？

**Lawson Vanderbilt**
> 没啊！我这不是正跟你说听见的动静吗？
> 脚步和闷撞声，是真真切切从底下传上来的。客人那茬，是我自己顺嘴猜的。

**Zack Brennan**
> 听到的和猜的，我分两笔写。

**Lawson Vanderbilt**
> 哎，你可别正儿八经写成证词让我按手印啊。回头传出去，Vivian 该以为我吃饱了撑的编排她了。

**Zack Brennan**
> 普通备忘。你嘴里怎么说的，我就怎么落纸，猜的也标成猜的。

@record oral:5061001

**Lawson Vanderbilt** [向后靠了靠]
> 行吧，随你折腾。反正亲眼看见的才算数，我可没见着人。

@goto lawson_hub

@path lawson_archive

**Zack Brennan**
> 刚才说的那些差事，到底是些什么？

**Lawson Vanderbilt**
> TideWater 的档案呗。莫名其妙全扣我脑门上了。
> 我还当能给我列个单子，好歹知道去哪儿翻。好嘛，交接文件，再扔给我一个监印，拍拍屁股让我管。

**Zack Brennan**
> 拿出来看看？

**Lawson Vanderbilt** [取出原物，在掌心展示]
> 就这玩意儿。瞧瞧。

**Zack Brennan** [俯身看表面纹样，手不碰原物]
> 没有附带的目录索引？

**Lawson Vanderbilt**
> 没有索引。鬼知道它对应哪儿。
> 看管档案的人连档案被老头子塞哪儿了都摸不着，可真够讽刺的。

**Zack Brennan**
> 让我拍张照。

**Lawson Vanderbilt**
> 拍随你拍，东西我可得捏紧了。你破你的案，我可担不起再丢东西的罪过。

【调查衔接】本次问话先完成展示与收回。整个 L1_talk_roundtable_noise 结束后，已获拍摄许可的玩家可独立点击 item:5105 调查；届时 Lawson 再展示片刻，拍完立即收回。跳过调查可回访补拍，实体始终由 Lawson 保管。

**Lawson Vanderbilt** [收回原物]
> 看够了吧？摸不透名堂也别自作聪明给它安个名头。

**Zack Brennan**
> 只记是谁交出来的，还有长什么模样。

@goto lawson_hub

@path lawson_end

**Zack Brennan**
> 先问到这儿。

**Lawson Vanderbilt**
> 行啊。今晚总算有句中听的人话了。

@end

### 回访短开场（同一问话入口的文字草案）

**Lawson Vanderbilt**
> 又转回来了？说吧，这回要查活人还是死文件？

**Zack Brennan**
> 有几句再核一下。

【回访续接】直接回 lawson_hub；两个话题可独立重访，口头记录不重复生成，监印可重新展示供独立拍摄。

## 调查反馈：item:5101｜Emma 礼服背部的擦抹血迹

【场景】舞台正面，查看开篇衣物记录。Emma 当前已在客房，本段只复核记录。

**Zack Brennan** [内心，沿记录中的血迹看过去]
> 礼服后背这一大块，是蹭上去的。
> 跟站着喷出来的血点子完全两码事。先记着。

@get item:5101
@end

## 调查反馈：environment:5151｜舞台上的尸体与 Emma

【场景】复核破门后现场记录，保持回看记录的呈现。

**Zack Brennan** [内心]
> 人倒在他边上，手攥着餐刀，餐刀跟伤口也吻合。
> 撞开门看见的是这副光景。门撞开以前呢？

@observe environment:5151
@end

## 调查反馈：environment:5152｜舞台麦克风

**Zack Brennan** [沿舞台边缘看线缆，内心]
> 麦克风的线贴着台沿拉过去，通到后台录音室。

@observe environment:5152
@end

## 调查反馈：environment:5153｜绣有 E.F. 的手帕

【衔接】玩家查看白色手帕的绣字，登记环境观察后，唯一续接 L1_event_handkerchief_boundary；不另重复一次归属特写或辨认台词。

@observe environment:5153
@next L1_event_handkerchief_boundary

## 调查反馈：item:5102｜礼堂唯一正常入口勘验页

**Zack Brennan** [查看入口并记录，内心]
> 正经进出就这一条走廊、一扇大门。
> 破门前在里头落了横栓。

@get item:5102
@end

## 调查反馈：environment:5154｜可旋转的镜子

【演出】Zack 查看走廊中央转轴镜，轻转镜面，再转回调查开始的角度。

**Zack Brennan** [内心]
> 带转轴的。能扭动。

【突发事件需求｜必须画面呈现】触发位置：旋转镜面时；画面必须让玩家看见：固定观察点不动，镜中视野由礼堂门转向衣帽间门与继续离开走廊的方向，再复位；两门外观保留可辨差异；承载的信息：旋转改变观察方向，供玩家自己比对；接回对白的位置：Zack 将镜面复位。此处不重演案发人物、不指认转镜者。

**Zack Brennan** [将镜面轻轻转回，内心]
> 先给它摆回刚才的角。

@observe environment:5154
@end

## 调查反馈：environment:5155｜礼堂正门

**Zack Brennan** [内心]
> 深色木门，黄铜拉手。底下横着根铜压条。
> 里面的门闩已经给撞烂了。

@observe environment:5155
@end

## 调查反馈：environment:5156｜衣帽间门

**Zack Brennan** [目光移到门脚，内心]
> 衣帽间。这扇门脚上补过一层漆，那一块颜色浅。

@observe environment:5156
@end

## 调查反馈：item:5103｜巡逻警员右侧口袋里的手卷烟草

【场景】已完成巡逻警员问话后，玩家独立调查右侧口袋。巡警沿用右手从制服右袋取烟的动作。

**Zack Brennan**
> 兜里那包烟草，拿来瞧一眼。

**Patrol Officer** [右手从右袋取出，递给他]
> 拿去呗。手卷的烟草。

**Zack Brennan**
> 扣下当个参照。

**Patrol Officer**
> 烟草也得查？行吧行吧。

@get item:5103
@end

## 调查反馈：item:5104｜Pierce 巡更打点纸带

**Zack Brennan** [核对纸带，内心]
> 签字打点，从低头到抬头十四秒。就这一下。

@get item:5104
@end

## 调查反馈：item:5105｜Lawson 所持监印照片

【场景】已完成 L1_talk_roundtable_noise，且已走过档案话题取得拍摄许可后，玩家独立点击拍摄。Lawson 再次展示原物，拍完立即收回。原物不转交。

**Zack Brennan**
> 成了。印面上的花纹照得挺清楚。

【演出】保存监印照片。Lawson 将原物立即收回；结束独立调查，回到自由探索，不重新播放已完成的问话。

@get item:5105
@return investigation_caller

## 调查反馈：item:5106｜湖滨信托夜间止付密电

【场景】安保与通讯室。Zack 在通信台查看碳写发送联。

**Zack Brennan** [内心]
> 湖滨信托……冻结老 Charles 当夜的交易……这会儿就已经把人当死人报了。
> 拍发时间，九点三十八分。门明明是十点才硬撞开的。

【演出】目光移至授权号码及发送记录。

**Zack Brennan** [内心]
> 授权代号 M-7。没有名字，只留个号。
> 线路断以前已经发出去了。

@get item:5106
@end


---

# 三、Pierce 指证及收束

## Expose: L1_expose_pierce.json

【场景】圆桌会议室。Zack 带回本轮调查材料。Pierce 在桌对面，小 Charles、Vivian、Lawson 在场。谈话围绕值守观察展开。

**Lawson Vanderbilt** [看着 Zack 放下材料]
> 人都在这儿干坐着了。你到底翻出什么没有？

**Zack Brennan**
> 走廊值守那阵 Pierce 看到的情况。让他当着所有人再过一遍。

**Pierce**
> 我一步都没离开过岗位。在走廊里我就回过你一次了。

**Zack Brennan**
> 还有那个抽烟的人。

**Pierce** [目光扫过众人]
> 左手拿烟，晃了一下人就没影了。

**Vivian**
> 你当时看出来那是谁了？

**Pierce**
> Morrison。他生前惯用左手。

**Lawson Vanderbilt** [皱眉]
> 怎么还扯上死人了？ Pierce，你今天真是……

**Pierce**
> 我两只眼睛看到的就是这个，用不着你信不信。

### R1｜所谓鬼影是谁

**Pierce** [面对 Zack，压住不耐烦]
> 我看得很清楚，那就是用左手夹着烟的 Morrison；眨眼功夫那人就凭空没了。

@lie testimony:5031001
@present item:5103
@on_wrong r1_wrong
@on_correct r1_success

@path r1_wrong

**Pierce**
> 随便丢个东西出来，就能证明我看到的是谁了？

**Zack Brennan**
> 证据对不上。换一件。

@retry R1

@path r1_success

【演出】Zack 把巡逻警员右袋里的手卷烟草放到桌上。

**Zack Brennan**
> 当晚巡警身上带的手卷烟草。制服右边口袋里的，掏烟拿烟全用右手。

**Pierce**
> 那就更不可能是他了。我看到的明明白白是左手。

**Zack Brennan**
> 你看到的是镜子照出来的手。

【演出】Pierce 原本要指向烟草的手停在半空。

**Zack Brennan**
> 人习惯用右手。但只要站在镜子跟前，照出来的可不就是左手？

**Pierce** [手慢慢收回]
> ……镜子里，确实是反的。

**Lawson Vanderbilt**
> 闹了半天是个大活人在那儿抽烟。

**Pierce** [立刻抬眼]
> 不可能。那警员当时已经出走廊了，他人怎么可能折回来又晃到我眼皮底下？

### R2｜离开的巡警为何又被看见

**Pierce**
> 他分明已经走过去了。我再一抬头，人难道还能倒着走回我面前？
> 那名警员早就离开走廊了，绝对不可能又出现在我视线里。

@lie testimony:5031901
@present environment:5154
@on_wrong r2_wrong
@on_correct r2_success

@path r2_wrong

**Pierce**
> 我问的是他怎么可能再冒出来。你根本没答到点子上。

**Zack Brennan**
> 先核对你当时看见的方向。

@retry R2

@path r2_success

【演出】调用玩家已调查的中央转轴镜观察画面，保持 Pierce 观察点不动。场景人物不离开圆桌。

**Zack Brennan**
> 过道中间这面镜子带转轴，是能转动的。现场能转给人看。

**Pierce**
> 能转动又能证明什么？

【突发事件需求｜必须画面呈现】触发位置：R2 正确提交后；画面必须让玩家看见：镜面转向后，衣帽间门及离开方向进入固定观察点的视野；门脚浅色补漆与礼堂门槛铜条可对照；承载的信息：同一观察点可以看见不同的门与继续离去者，巡警无需折返；接回对白的位置：Zack 询问门脚补漆。仅演已验证的反射关系，不重演具体凶手。

**Zack Brennan**
> 门底下这道浅色补漆，到底在哪扇门上？

**Pierce** [看着观察画面]
> ……衣帽间。

**Zack Brennan**
> 根本不是礼堂大门。只要镜子角度一偏，你留在原来的观察位置，眼睛盯牢的其实是另一扇关着的门。

**Vivian** [视线从画面转到 Pierce]
> 这么说，巡警根本就没回头。

**Zack Brennan**
> 他只是顺着路往前走，是镜子换了反射方向。

**Pierce** [沉默片刻，将目光移回桌面]
> 就算有人暗中动了镜子，也不代表真有人能溜进礼堂。
> 从走廊口走到礼堂门要约二十秒。我全程只低头打了十四秒的点。

### R3｜镜子之后还剩多少路

**Zack Brennan**
> 你就凭这十四秒，咬定没人进得去。

**Pierce**
> 就算那个人当时正好摸到了镜子边上，十四秒的时间，也绝对不够他进入礼堂。

@lie testimony:5031902
@present testimony:5111001 + item:5104
@on_wrong r3_wrong
@on_correct r3_success

@path r3_wrong

**Pierce**
> 步速和时间根本严丝合缝对不上。拿出硬证据再说话。

**Zack Brennan**
> 东西还没齐。

@retry R3

@path r3_success

【演出】巡逻证词与打点纸带并列展开。画面只呈现材料已有的三项数值，不先播放整条进入路线。

**Zack Brennan**
> 巡警从入口起步，到中间的转轴镜约十秒，走到礼堂大门约二十秒。
> 你嘴里那个二十秒，是从走廊入口算到礼堂门的整段路。

**Pierce**
> 顺手转镜子也要花时间。

**Zack Brennan** [手指落在纸带的记录上]
> 你低头了整整十四秒。

【演出】Pierce 看向证词中的中央镜位置，又看向纸带。桌边没人接话。

**Pierce**
> 从镜子……走到礼堂门……十秒左右。

**Zack Brennan**
> 还要继续坚持没人进得去吗？

**Pierce** [下颌绷紧]
> 转一下镜子，再走过去……时间确实够。

**Charles Miller Jr.** [在安静中开口]
> Pierce，观察记录里的这一条，得改过来了。

**Pierce**
> ……知道了。我改观察记录。

@next L1_post_expose_observation

## Talk: L1_post_expose_observation.json

【场景】圆桌会议室，紧接指证。Pierce 把面前的材料整理齐，动作比先前慢。

**Pierce**
> 我没有故意擅离职守，镜子是谁动过的我也不知情。
> 不过……打点后再抬头，我盯着的可能确实不是礼堂大门。

**Zack Brennan**
> 也就是说，你那段值守，根本排除不了有其他人混进去。

**Pierce**
> 排除不了。但你现在也没能证明真有人打那儿走过。

**Zack Brennan**
> 是没证明。有没有人走过这条路线、是谁、做了什么，都还得继续查。

**Lawson Vanderbilt**
> 把这句也原样添进记录里吧，省得回头律师拿这个翻来覆去盘问。

**Zack Brennan**
> 会写进去的。

【演出】Pierce 的手停在材料边缘。他抬起头。

**Pierce**
> 还有楼梯的事。

**Zack Brennan**
> 怎么？

**Pierce**
> 九点十五分，我最后往舞台方向看了一眼，那座活动楼梯当时停在 B 位。等破门冲进去的时候，它已经移到了 A 位。

**Lawson Vanderbilt**
> 这回你看准了没有？

**Pierce** [冷冷看他一眼]
> 我只说我亲眼看到的东西。

**Zack Brennan**
> 这件事我会去调底片和现场画面对。先不拿它排死先后顺序。

**Charles Miller Jr.**
> 这样妥当。等有了确凿能核实的东西，我们再摆到桌面上谈。

【演出】Zack 收好材料，走到门边停住，回头看 Pierce。

**Zack Brennan**
> Emma 那边有情况吗？

**Pierce**
> 还在东侧独立客房里躺着，人没醒。门口有人守着，出不了岔子。

【演出】Zack 点了一下头，拉开门。镜头留在他离开的方向，不切入客房，不出现 Emma 苏醒。

@loop_end 1 -> L2_opening_waking_promise
