# Unit5｜人物声纹试稿：Lawson 与 Zack—Emma

> 人名格式已统一：说话人标签使用英文全名，台词及动作中的姓名使用英文；仅调整姓名显示，历史初稿与 Gemini 原始输出不变。文内旧版对照也仅统一姓名显示，其余台词保留。

> 2026-09-15。独立新旧对照，待用户选择，不替代 Loop2／Loop3 原台本。主模型按已确认人设重写完整初稿，经 `[次]gemini-3.8-flash` 润色；交付只作事实限定与演出细节收回，原始输出保留。

## 这次看什么

- Lawson：对公司缺少兴趣，不等于对人冷漠；配合调查时也会顺着石头与工作话题讲岔。保留被打断的不耐烦，不靠追加画作或新经历展示性格。
- Zack—Emma：熟悉之中仍有裂口。Zack先急于带她出去，Emma把话题拉回事实；愿意继续交代不等于已经和好。
- 结构不变：Lawson两条独立话题回同一枢纽，只有原有5063001证词；Emma开场线性、无@get，消防卡仍由她独自观察且留房。
- 以下先放完整新版，末尾收录写作前的完整旧版供对照。旧版仅作快照，不可作为额外配置入口重复导入。
- 输入：[Lawson档案](./../../../../剧情设计/Unit5/人物设定/lawson_vanderbilt.md)、[Zack档案](./../../../../剧情设计/Unit5/人物设定/zack.md)、[Emma档案](./../../../../剧情设计/Unit5/人物设定/emma.md)、[L3 State](./../../../../剧情设计/Unit5/state/loop3_state.yaml)、[L2 State](./../../../../剧情设计/Unit5/state/loop2_state.yaml)。原 L2、L3 完整对白稿已按用户要求删除；本文历史对照仅作实验记录，不作为新完整稿输入。

## Talk: L3_talk_lawson_measurement.json

<!-- SC5016外层办公区。两个独立话题，均回枢纽；不依赖先见Vivian或已取5306。调查实测与附图另点，不由Talk发物品。Lawson穿着按最新人设为老钱风睡衣，具体材质颜色不指定；仅试稿演出方向，不宣称资产已制作。 -->

**Lawson Vanderbilt** [往旁边让了让，给量尺留出位置]
> 量你的。要我顺手帮你扯着那头吗？

**Zack Brennan**
> 尺子先等等。问两句。

**Lawson Vanderbilt** [转过身，仍是一身睡衣]
> 别是外头那些公事就行。那堆破烂账我多看一眼都头疼，你要聊石头我还能奉陪。

**Zack Brennan**
> 今天先问你脚底下的。

**Lawson Vanderbilt**
> 地板？行啊。问吧。

@label lawson_hub
@branch lawson_hub
@opt "案发前地板下的声音，再说一遍。" -> lawson_sound #事件/线索
@opt "工作台和洗手区之间这些蓝痕？" -> lawson_crystals #工作/痕迹
@opt "先问到这里。" -> lawson_end #退出

@path lawson_sound

**Zack Brennan**
> 底下的急促脚步，还有那声闷撞。你案发前听得真切？

**Lawson Vanderbilt**
> 就在地板下头。脚步急得要命，紧接着咚的一声，撞得挺瓷实的。我先前就说过了，别又指望我猜底下是谁。

**Zack Brennan**
> 没让你猜。

**Lawson Vanderbilt**
> 之前我猜是 Vivian 那头来了人，可我没看见。既然你连尺子都拿来了……量呗。耳朵听见的我认，眼睛没见着的，谁也别想让我跟着画押。

**Zack Brennan**
> 笔录里就记地板下。

**Lawson Vanderbilt** [低头瞄了眼脚下]
> 随你。反正现在这楼里，人人都忙着替别人把账给认了。

<!-- 回查L1口头记录5061001，无再次获取、不作声音拖拽。不判断访客身份或夹层。 -->
@goto lawson_hub

@path lawson_crystals

**Zack Brennan** [指了指工作台到水槽的一路地面]
> 工作台到洗手区，这些蓝色湿鞋印是怎么回事？

**Lawson Vanderbilt**
> 硫酸铜。别瞎琢磨，石头好端端的没掉色。
> 处理宝石金属镶座的时候洒了些硫酸铜晶体。你看——

<!-- Lawson主动展示现有鞋底，不新增操作物、画作、样品或新痕迹。 -->
**Lawson Vanderbilt** [抬起一只脚，把鞋底侧过来给 Zack 看]
> 花纹里嵌着一点呢。踩到水就溶出来，留下蓝色痕迹。石头是石头，底座是底座，你们外行总以为发亮的东西会褪色。

**Zack Brennan**
> 我没看石头。我盯的是你的鞋印。

**Lawson Vanderbilt** [愣了下，自己笑了一声]
> 得，白科普了。还要再凑近瞧瞧么？

**Zack Brennan**
> 案发到现在，换过鞋没有？

**Lawson Vanderbilt**
> 没换过。一直是这双。

@get 证词 5063001 "自己处理宝石金属镶座时曾洒落硫酸铜晶体，晶屑卡进鞋底，踩到水会溶出蓝色痕迹；案发后没有换鞋。" #statement

**Zack Brennan**
> 痕迹得拍张照。

**Lawson Vanderbilt** [放下脚往旁边侧了侧身]
> 拍吧。别把我刚才说的当废话全删了就行，留点能听的。

<!-- 5306仍由独立调查取得；无化学试验、不排除夹层经过者。 -->
@goto lawson_hub

@label lawson_end
@end

## Talk: L2_opening_waking_promise.json

<!-- SC5008，L2唯一开场根。Emma已苏醒，仍被单独看守。Zack来见她。无普通选项、无证词获取，不新增伤势诊断或看守人数。 -->

**Emma O'Malley** [视线转向门口]
> 门带上。

**Zack Brennan** [合拢房门，在椅子前停住]
> 感觉怎么样。

**Emma O'Malley**
> 你杵在那儿不吭声，我还以为 Pierce 又换了副生面孔来守我。
> 坐吧。外头传成什么样了？

**Zack Brennan** [拉开椅子坐下]
> Pierce 还让人守着。……找到你的时候，你倒在老 Charles 旁边，手里攥着刀。
> 还没定死。

**Emma O'Malley** [低头看着自己的掌心，手指收紧又慢慢松开]
> 那把刀……
> 脑子里一片空白，怎么拼都拼不起来。

**Zack Brennan**
> 先别硬拽。说说你确定记得的。

**Emma O'Malley**
> 彩排是我自己申请的。也是我约他九点半到舞台碰头。
> 这两桩事摆在那儿，用不着任何人替我找补，我也没打算抵赖。

**Zack Brennan**
> 我记着了。

**Emma O'Malley**
> 但后面全断了。有些模模糊糊的动静……我越想理顺，越分不清那是真听到的，还是我慌了神自己编进去填空的。
> Zack，如果真是我动的手呢？

**Zack Brennan** [握笔的手停在便签上方，没立刻接话]
> 我会带你出去。

**Emma O'Malley**
> 我不是问你这个。

**Zack Brennan** [停了停]
> 我知道。

**Emma O'Malley**
> 那你看着我回。要是查到底，所有证据都坐实是我扎的，你怎么办？
> 别再像上次那样，把你不乐意看到的东西直接扣在你手里。

**Zack Brennan** [抬眼迎上她的目光]
> 全交出去。
> 让你看，也给外头的人看。

**Emma O'Malley**
> 哪怕那些东西能直接定我的罪？

**Zack Brennan**
> 哪怕对你最不利。
> 我不能一边查，一边替你把不利的擦掉。以前做错过，现在不干了。

**Emma O'Malley** [盯着他看了好一会儿，紧绷的肩膀才微微松了一点]
> 好。九点半，我约的他。
> 这条笔录别漏了。

**Zack Brennan**
> 漏不掉。

<!-- 两人没有拥抱或恢复旧关系；Emma愿意继续交代，不能演成已相信自己无罪。 -->

**Zack Brennan** [收起记录，起身前停住]
> 还有个细节。断片前后，屋里有人进出过吗？

**Emma O'Malley**
> 我很想说有人进来过……但我不敢拿臆想骗自己。
> 我只记得一声动静，模模糊糊的，像刀刃扎进肉里。我没看见是谁的手。
> 我甚至不知道……那是不是我自己的手。

**Zack Brennan**
> 只记声音，不填人名。

**Emma O'Malley**
> 那声响动，给我留在本子上。

**Zack Brennan**
> 留着。

<!-- Zack退出。Emma留在客房，翻开既有应急疏散册，夹页露出5251。强制卡面特写：Miller飞行机械馆旧消防维护卡；三处呈正三角分布，上方正向屋顶排烟图标，图标右侧有不对称卡扣；左下单人校准舱；右下带消防标志和EXIT的防火隔断。三处无连接线，无R-42/R-17/R-28编号，不显示操作答案。 -->

**Emma O'Malley** [将夹页摆正]
> 飞行机械馆的……怎么塞在这儿。

<!-- Emma目光逐处停留，看清图标朝向和右侧卡扣；卡片放回疏散册，留在房内。记录environment_observed:5251，observer=502，u5_fire_card_seen=true。不入包，不让Zack取得同等卡面记忆。自动切5009，续L2_opening_corridor_arrival。 -->

## 旧版完整对照

### 旧版： L3_talk_lawson_measurement.json

<!-- SC5016外层办公区。两个独立话题，均回枢纽；不依赖先见Vivian或已取5306。调查实测与附图另点，不由Talk发物品。 -->

**Lawson Vanderbilt**
> 尺子扯直了量，别踩我台子。

**Zack Brennan**
> 离着半步呢。

**Lawson Vanderbilt**
> 丑话说前头。

@label lawson_hub
@branch lawson_hub
@opt "案发前地板下的声音，再说一遍。" -> lawson_sound #事件/线索
@opt "工作台和洗手区之间这些蓝痕？" -> lawson_crystals #工作/痕迹
@opt "先问到这里。" -> lawson_end #退出

@path lawson_sound

**Zack Brennan**
> 地下那些动静，急跑，撞击声。没记错吧？

**Lawson Vanderbilt**
> 板子底下透上来的，真真切切。
> 我说的是自己听见的动静。

**Zack Brennan**
> 来的是谁，确定么？

**Lawson Vanderbilt**
> 那是顺着理猜的，早跟你说过了。
> 反正响动跑不了。你想核高度就核高度，用不着替谁遮掩门风。

**Zack Brennan**
> 明白了。只认你耳朵听到的。

<!-- 回查L1口头记录5061001，无再次获取、不作声音拖拽。 -->
@goto lawson_hub

@path lawson_crystals

**Zack Brennan** [看向工作台与洗手区之间]
> 地上发蓝。

**Lawson Vanderbilt**
> 硫酸铜。处理宝石金属镶座的时候洒了点，少量晶屑卡鞋底了。
> 见水就化，踩着地就是这印子。

**Zack Brennan**
> 卡在鞋底？

**Lawson Vanderbilt** [抬起鞋底让他看]
> 缝里还有，自个儿看。
> 又不是血，别见着颜色不对就疑神疑鬼。

**Zack Brennan**
> 出了事之后换过鞋么？

**Lawson Vanderbilt**
> 一直就这双。

@get 证词 5063001 "自己处理宝石金属镶座时曾洒落硫酸铜晶体，晶屑卡进鞋底，踩到水会溶出蓝色痕迹；案发后没有换鞋。" #statement

**Zack Brennan**
> 痕迹我拍照存底，不动你台面。

**Lawson Vanderbilt** [把脚放回地面]
> 省得惹嫌。

<!-- 不在此反驳Lawson经过夹层；5306独立调查取得。 -->
@goto lawson_hub

@label lawson_end
@end 

### 旧版： L2_opening_waking_promise.json

<!-- SC5008，L2唯一开场根。Emma已苏醒，仍被单独看守。Zack来见她，留出距离。无普通选项、无证词获取，不新增伤势诊断或看守人数。 -->

**Emma O'Malley** [抬头看向门口]
> 门关上。

**Zack Brennan** [带上门，停在椅子旁]
> 醒了多久？

**Emma O'Malley**
> 外面现在怎么说？

**Zack Brennan**
> 老 Charles 死了。发现你的时候倒在他边上，手里攥着刀。Pierce 让人守在门外，还没定论。

**Emma O'Malley** [看着自己的手]
> 死了我知道。那把刀我不知道。

**Zack Brennan**
> 能记起多少？

**Emma O'Malley**
> 彩排是我自己打的申请。九点半，我约了他去舞台碰面。

**Zack Brennan**
> 你主动约的？

**Emma O'Malley**
> 是我。别帮我挑好听的说。可后头的事情全断了……昏过去前后有些动静，混在一块。

**Zack Brennan** [把椅子往后挪了半步，坐下]
> 先别硬凑。

**Emma O'Malley**
> 外头的人会等我慢慢想吗？万一真是我呢。

**Zack Brennan**
> 我会带你出去。

**Emma O'Malley** [抬眼]
> 你根本没听我说。如果查出来，那一刀真是我刺的，你还会把那张纸扣在手里吗？

**Zack Brennan**
> 不会。

**Emma O'Malley**
> 医院那时候，你也说该让我知道。

**Zack Brennan** [视线避开了一瞬，随即迎上去]
> 这一趟翻出来的东西，我都拿出来。对你不好也交。你约他这事，同样写进去。

**Emma O'Malley**
> 那就写。确实是我约的。找你来查，不是让你来替我编说辞。

**Zack Brennan**
> 明白。

<!-- Emma松开攥住的床沿，没伸手碰Zack。他站起，不演和解拥抱。 -->

**Zack Brennan**
> 还有。失去意识前后，有没有人进来、出去？记不清就别猜。

**Emma O'Malley**
> 模模糊糊的。听见一声……像刀子扎进肉里的动静。看不见是谁的手。我甚至不敢说……那是不是我自己的手。

**Zack Brennan**
> 只记这个声音。不往上套人。

**Emma O'Malley**
> 知道了。

<!-- Zack退出。Emma留在客房，翻开既有应急疏散册，夹页露出5251。强制卡面特写：Miller飞行机械馆旧消防维护卡；三处呈正三角分布，上方正向屋顶排烟图标，图标右侧有不对称卡扣；左下单人校准舱；右下带消防标志和EXIT的防火隔断。三处无连接线，无R-42/R-17/R-28编号，不显示操作答案。 -->

**Emma O'Malley** [将夹页摆正]
> 飞行机械馆的……怎么塞在这儿。

<!-- Emma目光逐处停留，看清图标朝向和右侧卡扣；卡片放回疏散册，留在房内。记录environment_observed:5251，observer=502，u5_fire_card_seen=true。不入包，不让Zack取得同等卡面记忆。自动切5009，续L2_opening_corridor_arrival。 -->

## 运行与核对记录

- Run ID：`u5-character-samples-20260915-r1`；已成功回收完整正文。
- 本机初稿和提示词：`C:/Users/Ellcy/.codex/novai-gemini/experiments/u5-character-samples-20260915/`。
- 本机原始输出：`C:/Users/Ellcy/.codex/novai-gemini/runs/u5-character-samples-20260915-r1/answer.md`；未被交付稿覆盖。
- 最小纠偏：将Vivian访客恢复为猜测；撤去硫酸铜洒落的新增时间、数量与手滑原因，以及地毯、睡衣未换、固定看守批次等新断言；恢复蓝色湿鞋印与“见水溶出”表述；去除新增日期与视野模糊的目击暗示。保留润色的互动和语言，不另作审美试验。
- 睡衣只沿用户已确认方向标出演出，未指定颜色、材质或品牌；未制作或同步美术资产。
- 未改原台本、State、正式JSON、预览表和Unity；未新增Repeat或证词。
