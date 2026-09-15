# Unit5 L3｜完整对白第一版

> 审阅稿。当前模型写完整初稿，Gemini 3.8 润色，主模型逐处校正事实及结构；保留原始 API 输出与修正记录。未同步 JSON、预览配置或 Unity。
> 阅读顺序：测量探索 → 第一次图纸 → 圆桌及第二次图纸 → 舞台开门 → 夹层探索 → Moore 指证 → 书房端开门。调查条目的排版顺序不限制玩家搜证先后。
> `@` 行是设计期控制标记，不是已接入的运行指令；失败／成功与分支段按标记互斥播放。回访问原路径，获取只生效一次。画面需求仍待制作。

# L3 第一包｜测量、图纸与舞台侧入口

## L3_opening_measurement_proposal

@scene 5005

【演出】众人停在舞台前。Zack 仰头看着 A 位平台所对的布景板，随后把目光移到通高玻璃。Vivian 留在稍远处；Moore 看了看楼梯，又看向 Zack。

**Harold Moore**
> 还要在这块木头板子前面耗多久？

**Zack Brennan**
> 不站着看了。拿尺子来。

**Pierce**
> 你这是要查板子，还是要查整座房子？

**Zack Brennan**
> 房子。先看看明面上一楼加二楼，合起来到底够不够整栋楼的高。

**Charles Miller Jr.**
> 查吧。不过东西没定论之前，各位嘴上还是叫它布景板吧。家里现在已经够乱了。

**Zack Brennan**
> 漏风的地方未必就能过人。总得量出来。

**Lawson Vanderbilt** [抬头扫了一眼通高玻璃的上沿]
> 怎么，连这块大玻璃也要量？……倒也是，这儿能从底直接望到顶。

**Zack Brennan**
> 这儿要量，你和 Vivian 的房间也各量一处。先把你俩屋里的净空高度摸准。

**Vivian**
> 行啊。搭把手拉个尺子，我还不至于推三阻四。

@event_complete L3_opening
@release exploration

## 调查｜舞台通高玻璃

@investigate 5301 scene:5005

【演出】完成通高玻璃上下端点的实测。Zack 把端点与数值记在同一页。

**Zack Brennan** [内心]
> 顶到底，足足九米。整栋楼的内部总高先压在这儿。

@get item:5301
@end

## 调查｜A 位楼梯高度

@investigate 5302 scene:5005

【演出】Zack 以舞台地面为基准，记录平台垂直高度，并在侧视草图上画出平台面对的布景板。

**Zack Brennan** [内心]
> 平台离舞台地面正好三米。现在是 A 位……正对着这块板。

@get item:5302
@end

## L3_talk_vivian_measurement

@scene 5015

【演出】Zack 进门，Vivian 为量尺让出位置。她留意到他的笔记本，先开了口。

**Vivian**
> 这回又要往本子上写什么？天花板可没法按手印。

**Zack Brennan**
> 记你头顶上的动静。Lawson 先前说过，出事前地板下面有动静。

**Vivian** [抬起头，短促地笑了一声]
> 他说下面？真会挑地方甩。我耳朵还没聋呢，动静分明是在顶上。急急忙忙的脚步，还有一声发闷的撞击声。

**Zack Brennan**
> 就在这间屋顶上面？

**Vivian**
> 就在顶上。出事前我人就在这屋里待着。你记归记，别回头又把我说的“上面”抄成了“下面”。

@label vivian_hub
@branch
@opt "你为什么怀疑 Lawson 有访客？" -> vivian_visitors
@opt "你愿意把这些签成证言吗？" -> vivian_record
@opt "先量房间。" -> vivian_end

@path vivian_visitors

**Zack Brennan**
> 你当时觉得是 Lawson 屋里进了人？

**Vivian**
> 不然我能怎么想？他嫌我楼下吵，我还嫌他楼上没个消停呢。自己房里藏着动静，倒有脸先跑来挑我的刺。

**Zack Brennan**
> 那个客人，你亲眼打过照面了？

**Vivian** [把脸偏向一边]
> ……没见着。我没在他房里看见我说的那个人。你问出这句算舒坦了？

**Zack Brennan**
> 这句确实重要。

**Vivian**
> 那就原话全记上，省得回头又只剩半截来编排我。

@record oral:5043001 collectible:false
@goto vivian_hub

@path vivian_record

**Zack Brennan**
> 声音是从哪儿传来的，我可以落笔。不过，你怀疑 Lawson 那部分呢？

**Vivian**
> 没见着就是没见着。吵归吵，我也犯不上硬给他头上安个大活人。
> 纸你也收回去吧，我不签字。芝麻大点误会，平白写下来给你们当笑话看一圈么。

**Zack Brennan**
> 那就当口头记录留着。天花板上方有急促脚步和闷撞；你怀疑 Lawson 有客人，但没见着你说的那个人。

**Vivian**
> 随你。反正声音是实打实听见的，别的我没看见。

@record oral:5043001 collectible:false
@goto vivian_hub

@path vivian_end

**Vivian** [走到房间另一侧，伸手按死尺头]
> 这头我按着了。你盯你的刻度，别老盯着我。

**Zack Brennan**
> 抓紧，别松劲。

@end

### 回访｜Vivian

@repeat L3_talk_vivian_measurement

**Vivian**
> 还想问案发前那阵动静？

@goto vivian_hub

## 调查｜Vivian 房间净高

@investigate 5303 scene:5015

【演出】Vivian 在房间另一侧扶持量尺；测量完成后，Zack 在纸上明确写下“净高”。

**Zack Brennan**
> 行了，放手吧。地板到天花板，大概两米七。

**Vivian** [收回手，拍了拍掌心]
> 这么巴掌大个地方，量清楚就得了。

**Zack Brennan** [内心]
> 这只是屋里的空高。中间隔着的那层楼板有多厚，还没算进去。

@get item:5303
@end

## 环境观察｜晚宴手包

@investigate 5351 scene:5015

【演出】测量期间，Vivian 在房间另一侧扶持量尺。晚宴手包内衬下露出枪身与象牙贴片枪柄；Zack 的视线短暂停住，随后移回尺上。

【突发事件需求｜必须画面呈现】触发位置：测量期间观察手包；画面必须让玩家看见：内衬下的 Colt Vest Pocket Model 1908，.25 ACP、象牙贴片枪柄，与 Unit1 原枪身份连续；承载的信息：枪仍由 Vivian 持有；接回对白的位置：Zack 内心辨认。此处是静态特写需求。

**Zack Brennan** [内心]
> 还是那把 Colt。.25 口径，象牙贴片……案子结了之后确实退给她了。
> 我留下的是调查记录，枪可好好地留在她手袋里。

@observe environment:5351
@end

## L3_talk_lawson_measurement

@scene 5016

【演出】Lawson 从工作台旁让开，却仍护着台边，给 Zack 指出可以放尺的位置。

**Lawson Vanderbilt**
> 尺子下在这儿。小心点，别蹭着台上的料子，我给你腾点空。

**Zack Brennan**
> 耽误你两分钟。

**Lawson Vanderbilt**
> 已经给搅和了，问吧。再磨蹭两下，我都快忘了刚才手上的活做到哪一步了。

@label lawson_hub
@branch
@opt "再说说地板下的声音。" -> lawson_sound
@opt "地上的蓝色水痕怎么来的？" -> lawson_blue
@opt "我先看测量和档案。" -> lawson_end

@path lawson_sound

**Zack Brennan**
> 先前你说案发前听到急促的脚步和闷撞。到底哪个方向，再对一次。

**Lawson Vanderbilt** [手指直接往下一点]
> 下面。就在这块地板底下。既不是我房顶上，更不是谁在我身旁晃荡。

**Zack Brennan**
> 你先前为这事跟 Vivian 吵过。

**Lawson Vanderbilt**
> 对，我是跟她吵了，可吵得再凶，动静总不能自己长翅膀飞到天上去吧？

**Zack Brennan**
> 我只要你咬准方向。

**Lawson Vanderbilt**
> 就是脚底下。我没记错，也不会改口。

@review oral:5061001
@goto lawson_hub

@path lawson_blue

**Zack Brennan** [视线扫过工作台与水槽之间的地面]
> 地上这几道蓝洼洼的印子哪儿来的？

**Lawson Vanderbilt**
> 我踩出来的。处理宝石的金属镶座时，洒了硫酸铜晶体，碎渣卡进鞋底了。踩到水，一溶就成了这种蓝水印。

**Zack Brennan**
> 脚抬一下，我看眼鞋底。

【演出】Lawson 抬起鞋跟，侧过鞋底。槽纹中仍可见晶屑。

**Lawson Vanderbilt**
> 瞧，这不还卡着么。你别拿指甲去抠，回头我自己刷。

**Zack Brennan**
> 出事之后你换过鞋没有？

**Lawson Vanderbilt**
> 哪有工夫换？出事以后就脚上这双。

@get testimony:5063001
@goto lawson_hub

@path lawson_end

**Lawson Vanderbilt**
> 图纸尺寸那些你自己翻吧。我站一边去，别把你那些尺子摊到我工具堆里来就行。

@end

### 回访｜Lawson

@repeat L3_talk_lawson_measurement

**Lawson Vanderbilt** [手里动作一顿，抬眼看过来]
> 还有哪儿没量清楚？

@goto lawson_hub

## 调查｜Lawson 办公区净高

@investigate 5304 scene:5016

【演出】Zack 完成办公区地面至天花板的测量，记录上下测点。

**Zack Brennan** [内心]
> 屋里净高大概三米六。隔层的楼板厚度还得找图纸对一对。

@get item:5304
@end

## 调查｜建筑材料登记册附图

@investigate 5305 scene:5016

【演出】从登记册封底夹层取出双面折页，先展开正面，再翻到背面。两处房间与外壳未按当前实测比例归位。

**Zack Brennan** [内心]
> 当年入保和估价留的底子，比 Lawson 这次接管还早。
> 正面的高度比例全得推倒重核。反面倒是标了结构：一层楼板厚零点三米，二层厚零点四米。

@get item:5305
@read document:5305.floor1_thickness=0.3
@read document:5305.floor2_thickness=0.4
@end

## 调查｜蓝色水痕

@investigate 5306 scene:5016

【演出】取景包含矿物工作台到洗手区之间的蓝色湿鞋印；另记录鞋底槽纹中残留的晶屑。

**Zack Brennan** [内心]
> 台子到水池这一路的蓝色湿脚印，还有他鞋底里嵌着的晶体渣。这两处都得落进记录里。

@get item:5306
@end

## 调查｜Moore 公文夹

@investigate 5307 scene:5017

【演出】Zack 从搁架取下红封公文夹，转到缺损的一侧。

**Zack Brennan** [内心]
> 红封公文夹少了枚黄铜牵引铆圈。断茬很新，边缘不规则。
> 这个破口得记下。

@get item:5307
@end

## 调查｜Moore 私人授权牌

@investigate 5308 scene:5017

【演出】Zack 查看私人授权牌盒内的凭牌。牌面显示湖滨信托及 M-7。

**Zack Brennan** [内心]
> 湖滨信托给 Moore 配的夜间授权牌，编号 M-7。
> 持有人能从庄园通信设备发出专用止付指令。

@get item:5308
@end

## 小玩法接入｜第一次复原

@mechanic section_stage1
@requires items:5301,5303,5304,5305 fields:5305.floor1_thickness,5305.floor2_thickness
@location current_scene preserve_return_scene:true

**Zack Brennan** [内心]
> 实测的净高和楼板厚度全齐了。把这些数字往图纸上排一排。

【玩法画面】先开背面网格。五个尺寸槽由玩家拖入；楼梯记录本次锁定。首次放错只弹回并显示校准记号，不播放解释对白。

@feedback repeated_same_data

界面提示：净高需要与对应楼板厚度合计。

@feedback missing_material

界面提示：仍缺一项实测。

@success section_stage1

【玩法画面】五槽正确后呈现 9－（2.7＋0.3）－（3.6＋0.4）＝2 米；自动翻回正面，下部模块贴地，上部模块贴 9 米上沿，中间显出约 2 米未登记阴影带。

**Zack Brennan** [内心]
> 上下对不齐。正当中平白吃掉了两米。

@set u5_section_stage1=true
@restore current_scene

## L3_event_roundtable_locate

@scene 5006
@requires items:5301,5302,5303,5304,5305,5306,5307,5308 talks:L3_talk_vivian_measurement,L3_talk_lawson_measurement flag:u5_section_stage1

【演出】众人回到圆桌。Zack 展开已复原的折页。Moore 没有坐下，俯身看着中间的阴影带。

**Harold Moore**
> 空了两米。行，纸上我看见了。可这少了的两米，跟台上那块烂木头板子到底能有什么干系？

**Charles Miller Jr.**
> 这话倒实在。图纸上画不齐，不代表真有这么个能进能出的门，更别说刚好开在你想找的地方。

**Zack Brennan**
> 所以得看它跟哪儿平齐。

**Pierce**
> 绕这么大圈子，你无非就是咬定还有别人从礼堂里溜出去了。

**Zack Brennan**
> 至少正门值守那一块，你确实没法打包票说没溜进去第二个人。

**Pierce** [眼皮一抬，硬生生把火气压回喉咙里]
> ‘没法排除’。可不是我眼睁睁看着谁走进去的。

**Zack Brennan**
> 我也没说你看见他进去了。

**Charles Miller Jr.**
> 可各位撞门进去的时候，门闩分明是在里头插死的。大厅里连个多余的人影都没见着。

**Zack Brennan**
> 进去刺那一刀的人如果存在，他总不能插上门之后凭空蒸发。

**Vivian**
> 而且好巧不巧，那架要命的楼梯，偏偏在刀刺之后被人转回了 A 位。

**Harold Moore**
> 翻来覆去还是这几句。Brennan，你总不能图纸上漏了截空白，就拿它当现成的逃跑路线使吧？

**Zack Brennan** [把摊开的图纸正面朝自己拉了半寸]
> 能不能接得上，把刚量出来的标高搭上去看看。

@segment open_section_stage2
@mechanic section_stage2

【玩法画面】同一张已复原图纸正面。玩家选择结构记录，拖到舞台侧零米基准；第一阶段数值保持锁定。

@feedback wrong_record

界面提示：它能确认高度，不能形成抵达这段空间的路径。

@feedback wrong_baseline

【玩法画面】记录不吸附，标高线不闭合。

@success section_stage2

【玩法画面】A 位楼梯落在舞台零米基准，顶端三米标线与未登记空间下沿闭合；所对布景板出现待查问号。

**Lawson Vanderbilt** [顺着对齐的标高虚线一路看过去]
> 高度严丝合缝……可这块板子后面究竟藏了什么，图上照样一个字都没画。

**Zack Brennan**
> 图上没有，那就去敲实物。

**Charles Miller Jr.** [按在图纸边缘的手指慢慢收了回去]
> 请吧。既然量都量到这个份上了，索性把那块板子查个清楚。

@set u5_section_stage2=true
@event_complete L3_roundtable
@change_scene 5020
@goto L3_event_stage_door_open

## L3_event_stage_door_open

@scene 5020

【演出】众人直接前往礼堂，沿 A 位楼梯登到顶端。Zack 先检查布景板边缘，轻敲板面。狭窄平台上，其余人依次停住。

**Zack Brennan**
> 板边这儿的灰断了一小截。敲上去是空心的，缝里还往外吐凉风。

**Pierce**
> 手放哪儿？连个普通把手都没有。

**Zack Brennan**
> 没把手。先摸边缘。

【演出】Zack 抵住板边试推。布景板向内让开，露出连续夹层。门缘可见异物将锁芯卡在退栓状态。

【突发事件需求｜必须画面呈现】触发位置：试推布景板；画面必须让玩家看见：板打开后约两米高的连续夹层，以及门缘异物卡住退栓的状态；门内门外各有一处三瓣不等、左右断翼的浅槽，没有普通把手；承载的信息：实地确认舞台侧入口与双面槽形；接回对白的位置：Pierce 看向锁芯。槽形只短暂特写，不开放热点或拓片。

**Pierce** [探身看向门缘的锁芯]
> 里面的舌头没弹出来。

**Zack Brennan**
> 塞了东西，硬把锁芯卡在退栓的位置上了。别动它，留着。

**Vivian** [跟上前迈了半步，停在门边]
> 真能钻过人去……合着不是板子后面多垫了两寸，是真有条夹道。

**Lawson Vanderbilt**
> 刚才图上没登记的那两米，全落在这儿了。

**Zack Brennan** [回头看了看脚下的平台，又扫视了一眼黑洞洞的夹层]
> 整栋楼明面上的进出口里，唯独舞台这架楼梯能在三米的高度上直通进来。

**Harold Moore**
> 既然门也推开了，还要一帮人跟傻子似的在这过道上堵着？

**Zack Brennan**
> 往前走，先看前面的岔口。

@observe environment:5352
@set u5_stage_door_open=true
@set u5_stage2_exploration_unlocked=true
@event_complete L3_stage_door_open
@change_scene 5018
@release exploration


---

# L3 第二包｜第一岔口、Moore 指证与书房端入口

## 调查｜第一岔口黄铜牵引铆圈

@investigate 5309 scene:5018

【演出】Zack 在第一岔口拾起黄铜牵引铆圈，转向断面查看。

**Zack Brennan** [内心]
> 黄铜铆圈。断口很新，不规则的边还在。

@get item:5309
@end

## 调查｜催收急件

@investigate 5310 scene:5018

【演出】Zack 查看文件的签署栏、时限与经办标记。

**Zack Brennan** [内心]
> 催收急件。当夜截止，需要老 Charles 签字……经手人，Moore。

@get item:5310
@end

## 调查｜湿地毯上的鞋印

@investigate 5311 scene:5018

【演出】翻倒的清水壶旁，整段狭窄通道的地毯已经浸湿。Zack 在不覆盖原有足迹的位置取景，逐一记录大小、纹路与踩踏深浅。

【突发事件需求｜必须画面呈现】触发位置：足迹调查；画面必须让玩家看见：覆盖整段通道的湿地毯、翻倒清水壶，以及大量叠压乱向但可按大小、纹路、深浅稳定分成四组的足迹；承载的信息：至少四人经过，身份和先后无法确认；接回对白的位置：Zack 内心观察。不用箭头将各组对应到具体人物。

**Zack Brennan** [内心]
> 壶倒了，水渗得哪儿都是。地毯上的脚印压着脚印，来回的方向也乱。
> 别看花眼……底纹、鞋掌宽窄，吃力深的这几下……四种。至少四个人打这儿过去过。
> 全叠在一块儿，谁踩在谁上面根本分不出。

@get item:5311
@end

## 环境观察｜夹层文件柜

@investigate 5353 scene:5018

【演出】Zack 停在文件柜前，查看可见的档案标识与翻动、缺页痕迹，没有展开逐页调查。

**Zack Brennan** [内心]
> Miller 家早年的底子。1912 年的卷宗。
> 翻动过，里头还缺了页。回头得翻个底朝天。

@observe environment:5353
@end

## 调查｜文件柜后方局部墙面

@investigate 5312 scene:5018

【演出】Zack 从现有可见角度观察文件柜后方的一小段墙面，只对局部材质差异取景；柜与墙均留在原处。

**Zack Brennan** [内心]
> 柜子后面这一小截材质不一样，像是另外加的隔音层。
> 先记下位置。

@get item:5312
@end

## L3_talk_moore_before_expose

@scene 5018

【演出】Moore 站在岔口一侧。Zack 朝他走近时，他先直起身，截住了开口的时机。

**Harold Moore**
> 我昨晚压根没进过这鬼缝隙。Brennan 先生，你既然挖出条暗道，也犯不着非得把在场每个人都塞进来过一遍堂。

**Zack Brennan**
> “压根没进过。”行，我记着。

**Harold Moore**
> 记准点。别待会儿又让我把同样的话嚼第二遍。

@get testimony:5083001
@end

### 回访｜Moore

@repeat L3_talk_moore_before_expose

**Harold Moore**
> 刚才不是说过了？我没进去过。

@end

## 回查｜湖滨信托夜间止付密电

@review item:5106

【演出】Zack 重看先前取得的发送联，停留在时间与授权号栏。

**Zack Brennan** [内心]
> 二十一点三十八分。授权码 M-7。那头登记死亡的止付单子已经发出去了。

@end

## L3_expose_moore

@scene 5018
@requires doubts:5301,5302,5303 items:5106,5307,5308,5309,5310,5311,5312 environments:5352,5353 testimonies:5083001,5063001 flags:u5_section_stage1,u5_section_stage2,u5_stage2_exploration_unlocked

【演出】众人在第一岔口停住。Zack 走到 Moore 面前，给身后的人留出看清证物的位置。

**Harold Moore**
> 又怎么了？折腾到现在，在场谁嘴里没两句含糊话？你打算挨个盘到天亮吗。

**Zack Brennan**
> 不用天亮，就从你刚撂下的那句开始。

### R1｜是否进入夹层

**Harold Moore** [压下不耐]
> 我昨晚没有进入过那条夹层。

@lie testimony:5083001
@present items:5307,5309

@failure r1

**Harold Moore**
> 拿这玩意儿就想往我头上扣？你再好好看一眼。

**Zack Brennan**
> 拿错了，换一组。

@retry r1

@success r1

【演出】Zack 将第一岔口的铆圈放到公文夹缺口旁，两处新鲜断面并列展示。

【突发事件需求｜必须画面呈现】触发位置：R1 正确出示；画面必须让玩家看见：铆圈与公文夹新鲜不规则断面的对应关系，使用同一断面形状，保留物体各自完整形态；承载的信息：公文夹到过第一岔口；接回对白的位置：Zack 要求 Moore 看断口。此处不生成拼合报告。

**Zack Brennan**
> 你的公文夹。从你客房搜出来的时候，这儿少了枚铆圈。

**Harold Moore** [手刚伸出一半，猛地停在半空]
> ……你连这东西都翻出来了。

**Zack Brennan**
> 崩掉的铜圈就掉在岔路口地上。别光看成色，看这道豁口，能不能对上。

**Harold Moore**
> ……是它。轻点拿，别把断口弄坏了。

**Zack Brennan**
> 公文夹进来了。你呢？

**Harold Moore** [眼风往旁边扫了一圈，慢慢收回手]
> 我进来过。偶然看见入口，进去看了一眼，就在门边站了下。我又没追着 Charles 到处跑。

**Vivian**
> 刚才不是咬得挺死的么？连边都没沾过似的。

**Harold Moore**
> 我要是说了，你们现在还不得一口咬定我进去干了别的事？像现在这样。

### R2｜进入的目的

**Harold Moore**
> 我不是去找 Charles，只是看见有条通道，进去看了一眼。

@lie expose:5083901
@present items:5310

@failure r2

**Harold Moore**
> 我刚不是认了进过门吗？你拿这个还想问我什么？

**Zack Brennan**
> 问你进去到底图什么。接着说。

@retry r2

@success r2

【演出】Zack 展开催收急件，将签署栏和当夜时限转向 Moore。

**Zack Brennan**
> 也是在刚才那个岔口捡着的。有你的经办标记，需要老 Charles 签字，当夜截止。

**Harold Moore**
> 银行的正经业务函件。这能说明什么？

**Zack Brennan**
> 说明你揣着这种要命的东西，专程钻进耗子洞里看风景？

**Harold Moore** [嘴角紧绷，齿缝里挤出话]
> 我不找他签字找谁？他当时就在那儿拖着不办！要是拖过了时限，天大的窟窿全得湖滨信托扛着，难道我回客房喝着咖啡干等他发善心？

**Charles Miller Jr.**
> Moore 先生，公事找我父亲，摊在台面上讲就是了。刚才死活说没来过，改口又成了随便瞧瞧。

**Harold Moore**
> 现在不是跟你们说清楚了吗？我追到第一岔口，拿文件要求他签。他不签，接着往前走，我就掉头回去了。

**Zack Brennan**
> 他不签，你就这么老实走了？

**Harold Moore**
> 不然呢？我跟他在这儿打一架？我没再往前跟，后头发生什么我一概不知。

### R3｜何时知道死讯

**Harold Moore** [视线从急件移回 Zack]
> 我走的时候 Charles 还活着。直到所有人后来破门，我才知道他死了。

@lie expose:5083902
@present items:5106,5308

@failure r3

**Harold Moore**
> 你不是在查我什么时候知道他人死了么？这些能证明什么？

**Zack Brennan**
> 那就看时间和授权。

@retry r3

@success r3

【演出】Zack 将止付发送联与私人授权牌并列。先停留在两处 M-7，再让 Moore 看发送时间。

**Zack Brennan**
> 二十一点三十八分。授权码 M-7 发出的死亡止付，登记的是老 Charles 死亡。

**Harold Moore**
> 这是我为银行作的处置。

**Zack Brennan**
> 私人授权牌 M-7，谁的？

**Harold Moore**
> ……我的。指令也是我发的。

**Pierce**
> 我们破开礼堂门的时候是二十二点。你早了整整二十二分钟。

**Charles Miller Jr.** [脸上的笑意彻底挂不住了]
> Moore 先生，我们连父亲的面都还没见着，你倒是先向银行报了他的死亡？

**Harold Moore**
> 我不能让交易继续！

**Zack Brennan**
> 别扯你的账。我就问你，二十一点三十八分前，你眼睛看见什么了？

**Harold Moore** [喉结动了动，把声音压得很沉]
> 什么都没看着。我往回走的时候……前头很远的地方，咚的一声，闷响。

**Zack Brennan**
> 你没回去查看？

**Harold Moore**
> 没回去。

**Zack Brennan**
> 也没找人求救？

**Harold Moore**
> 没喊。我得先作判断！要是等你们一大群人去查看、确认，交易还会停在那儿等我吗？

**Lawson Vanderbilt** [从墙边直起身]
> 凭一声响你就敢直接填“死亡”？那是条人命啊！

**Harold Moore**
> 最坏的情况必须先处理！

**Zack Brennan**
> 算得挺明白。账顾上了，人呢？

**Harold Moore** [胸口起伏了一下，抬手把急件翘起的纸角狠狠抹平]
> 我没走到舞台那边，那把刀更不是我捅进去的！你少给我往谋杀上套！

**Zack Brennan**
> 听见了。你没回去查看，也没求救。二十一点三十八分，你用死亡登记抢先冻结了交易。

**Harold Moore**
> 是！那是银行家的职业判断。少拿你们那套道德来审我，我没杀人。

@event_complete L3_expose
@goto L3_post_expose_study_door

## L3_post_expose_study_door

@scene 5018

【演出】Moore 要收起文件，Zack 的手停在纸边，挡住他的动作。众人仍在第一岔口，没有离开夹层。

**Zack Brennan**
> 你说自己在岔口折返了，也可能接着往前，一路走向舞台。

**Harold Moore**
> “可能”？Brennan，你查不出证据，就打算全凭脑子猜了是吧。

**Pierce**
> 你从舞台那头进出，就得把那边的事说清。

**Harold Moore** [眼珠猛地转向 Pierce，又硬生生扭回盯着 Zack]
> 谁跟你们说我是从舞台钻进来的？
> 你们就咬死我进了通道，自作聪明觉着全天下就舞台那一个豁口！

**Zack Brennan**
> 怎么，还有别的门？

**Harold Moore**
> 跟我走。用不着你拿尺子满庄园乱量。

【演出】Moore 从第一岔口走向书房端。Pierce 紧跟，其余人沿狭窄夹层单列前行，不返回礼堂、不交还操作权。

@change_scene 5021 continuation:same_talk
@segment study_ceiling_door_open

【演出】Moore 在先前看似封死的一端停下。他俯身沿饰面边缘寻找，按动几乎不可辨认的暗扣，打开夹层地面上的门；下方露出老 Charles 书房。

【突发事件需求｜必须画面呈现】触发位置：Moore 操作暗扣；画面必须让玩家看见：门位于夹层地面，向下通往老 Charles 书房天花板；不是侧墙门，不回舞台重复进门；打开后同时带出附近一大片凌乱重叠足迹；承载的信息：第二入口的垂直位置、Moore 熟悉此入口、至少四组经过痕迹；接回对白的位置：Lawson 看向下方。不得凭此画面给鞋印标上具体姓名或顺序。

**Lawson Vanderbilt** [在门边蹲下，向下看]
> 这是……老 Charles 的书房？门居然开在天花板上……

**Charles Miller Jr.** [停在后面，让出门边的位置]
> Moore 先生，这你又怎么说？

**Harold Moore**
> 我昨晚亲眼看见 Charles 从书房进来。我拿着急件跟进去，一路追到第一岔口。

**Zack Brennan**
> 你看着他开的暗门？

**Harold Moore**
> 废话。他钻进去，我追上去。字没签成，我就原路从这儿退回书房。我从头到尾就没去过舞台！

**Pierce** [弯腰查看入口附近地面]
> 见鬼，这块地上的脚印……全踩烂了。

**Zack Brennan** [查看各处纹路与踩踏深浅]
> 底纹、鞋型、踩下去的轻重，能理出四组脚印。起码四个人打这顶上踩过去。

**Harold Moore**
> 我，Charles——还有至少两个人！剩下的脚印是谁的？你们怎么不去查他们？

**Zack Brennan**
> 踩得太烂，现在分不清谁压着谁，也认不出脚是谁的。

**Harold Moore**
> 那就去找啊！光围着我咬算什么本事？

**Zack Brennan** [起身，仍挡在 Moore 与众人之间]
> 人我肯定找。不过你找着了新门，只能说明还有入口，证明不了你没往舞台去。

**Harold Moore**
> 至少证明了你们刚才那套全扣错了！我用不着非得跑去舞台绕大半圈。

**Zack Brennan**
> 入口那点我改正。但二十一点三十八分那封电报，你洗不掉。

【演出】Moore 抿紧嘴，没有再答。Zack 看了一眼书房下方，再回看门边乱向的足迹。

**Zack Brennan**
> 底下书房也得彻底翻一遍。

@observe environment:5354
@set u5_study_door_open=true
@event_complete L3_post_expose
@loop_end 3 -> L4_opening_escort_corridor
