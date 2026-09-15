# Unit5 L3｜主模型完整初稿

# L3 第一包｜测量、图纸与舞台侧入口

## L3_opening_measurement_proposal

@scene 5005

【演出】众人停在舞台前。Zack 仰头看着 A 位平台所对的布景板，随后把目光移到通高玻璃。Vivian 留在稍远处；Moore 看了看楼梯，又看向 Zack。

**Harold Moore**
> 还要对着这块板站多久？

**Zack Brennan**
> 不站了。拿尺子。

**Pierce**
> 你到底要查板，还是查房子？

**Zack Brennan**
> 先查房子。明面上的一楼、二楼，加起来是不是整栋楼的高度。

**Charles Miller Jr.**
> 可以。不过在结果出来前，我希望各位还把它叫作布景板。家里已经够乱了。

**Zack Brennan**
> 漏风的地方不一定能过人。我会量。

**Lawson Vanderbilt** [看向玻璃上沿]
> 量这里？倒是能从底一直看到顶。

**Zack Brennan**
> 这里，再加你和 Vivian 的房间。净高先各自记清。

**Vivian**
> 行。量尺我还扶得住。

@event_complete L3_opening
@release exploration

## 调查｜舞台通高玻璃

@investigate 5301 scene:5005

【演出】完成通高玻璃上下端点的实测。Zack 把端点与数值记在同一页。

**Zack Brennan** [内心]
> 从底到顶，九米。建筑内部的完整高度，记在这里。

@get item:5301
@end

## 调查｜A 位楼梯高度

@investigate 5302 scene:5005

【演出】Zack 以舞台地面为基准，记录平台垂直高度，并在侧视草图上画出平台面对的布景板。

**Zack Brennan** [内心]
> 顶端平台离舞台地面三米。A 位，正对这块板。

@get item:5302
@end

## L3_talk_vivian_measurement

@scene 5015

【演出】Zack 进门，Vivian 为量尺让出位置。她留意到他的笔记本，先开了口。

**Vivian**
> 又要记什么？天花板可不会给你签字。

**Zack Brennan**
> 它上面的声音。Lawson 说，出事前听到地板下面有动静。

**Vivian** [抬起头，短促地笑了一下]
> 下面？他倒会往下推。我听见的明明在上头。急急忙忙的脚步，还撞了那么一下，闷的。

**Zack Brennan**
> 在你这间房的天花板上方？

**Vivian**
> 对。案发前，我人在房间里。别把“上面”又给我写成“下面”。

@label vivian_hub
@branch
@opt "你为什么怀疑 Lawson 有访客？" -> vivian_visitors
@opt "你愿意把这些签成证言吗？" -> vivian_record
@opt "先量房间。" -> vivian_end

@path vivian_visitors

**Zack Brennan**
> 你觉得是 Lawson 在接待什么人？

**Vivian**
> 不然呢？他嫌我这边吵，我还嫌他上头不清静呢。自己有客人，倒先来问我的事。

**Zack Brennan**
> 你看见那位客人了？

**Vivian** [偏开视线]
> 没有。我没在他房里看见我说的那个人。你满意了？

**Zack Brennan**
> 我需要这句。

**Vivian**
> 那就连这句一起记，别只留下前半截。

@record oral:5043001 collectible:false
@goto vivian_hub

@path vivian_record

**Zack Brennan**
> 声音的方向可以记下来。你对 Lawson 的猜测呢？

**Vivian**
> 猜测就是猜测。我没看见他房里有谁，不能因为我们吵了一架，就给他安一个。
> 也别拿张纸来叫我签。这点男女间的误会，还不够你们把人笑话一圈的。

**Zack Brennan**
> 只留口头记录。上方有急促脚步和闷撞；你怀疑过他，但没见着被你指的那个人。

**Vivian**
> 对。声音是我听见的，别的没有。

@record oral:5043001 collectible:false
@goto vivian_hub

@path vivian_end

**Vivian** [走到房间另一侧，扶住量尺]
> 这边我按着。你看刻度，别又看我。

**Zack Brennan**
> 按稳了。

@end

### 回访｜Vivian

@repeat L3_talk_vivian_measurement

**Vivian**
> 还要问那阵声音？

@goto vivian_hub

## 调查｜Vivian 房间净高

@investigate 5303 scene:5015

【演出】Vivian 在房间另一侧扶持量尺；测量完成后，Zack 在纸上明确写下“净高”。

**Zack Brennan**
> 可以松开了。地面到天花板，约二点七米。

**Vivian** [松开手]
> 这么点地方，量清楚了就好。

**Zack Brennan** [内心]
> 这是房间里头的高度。楼板本身还没算。

@get item:5303
@end

## 环境观察｜晚宴手包

@investigate 5351 scene:5015

【演出】测量期间，Vivian 在房间另一侧扶持量尺。晚宴手包内衬下露出枪身与象牙贴片枪柄；Zack 的视线短暂停住，随后移回尺上。

【突发事件需求｜必须画面呈现】触发位置：测量期间观察手包；画面必须让玩家看见：内衬下的 Colt Vest Pocket Model 1908，.25 ACP、象牙贴片枪柄，与 Unit1 原枪身份连续；承载的信息：枪仍由 Vivian 持有；接回对白的位置：Zack 内心辨认。此处是静态特写需求。

**Zack Brennan** [内心]
> 那把 Colt。象牙贴片枪柄……结案后已经还她了。
> 我留下的是调查记录。枪在她这儿。

@observe environment:5351
@end

## L3_talk_lawson_measurement

@scene 5016

【演出】Lawson 从工作台旁让开，却仍护着台边，给 Zack 指出可以放尺的位置。

**Lawson Vanderbilt**
> 尺子放这儿。别压到工作台，我给你腾地方。

**Zack Brennan**
> 还得占你一点时间。

**Lawson Vanderbilt**
> 已经占了。问吧，趁我还记得刚才做到哪儿。

@label lawson_hub
@branch
@opt "再说说地板下的声音。" -> lawson_sound
@opt "地上的蓝色水痕怎么来的？" -> lawson_blue
@opt "我先看测量和档案。" -> lawson_end

@path lawson_sound

**Zack Brennan**
> 你先前说，案发前听到急促的脚步和闷撞。方向再确认一次。

**Lawson Vanderbilt** [指向脚下]
> 下面。地板下头。不是头顶，也不是有人站在我旁边走。

**Zack Brennan**
> 你跟 Vivian 为这事争过。

**Lawson Vanderbilt**
> 是。我们吵过，不会把声音吵到天上去。

**Zack Brennan**
> 我问的是方向。

**Lawson Vanderbilt**
> 那就下面。我没改口。

@review oral:5061001
@goto lawson_hub

@path lawson_blue

**Zack Brennan** [看向工作台与洗手区之间]
> 这些蓝色的湿鞋印？

**Lawson Vanderbilt**
> 我的。弄宝石的金属镶座时洒了硫酸铜，晶体碎屑卡进鞋底了。踩到水，就溶出这种蓝色。

**Zack Brennan**
> 鞋底给我看看。

【演出】Lawson 抬起鞋跟，侧过鞋底。槽纹中仍可见晶屑。

**Lawson Vanderbilt**
> 还在。别拿手抠，我自己清。

**Zack Brennan**
> 出事以后换过鞋没有？

**Lawson Vanderbilt**
> 没换。就脚上这双。

@get testimony:5063001
@goto lawson_hub

@path lawson_end

**Lawson Vanderbilt**
> 建筑的东西你自己看。我让开，别把它跟我手边的活混在一起。

@end

### 回访｜Lawson

@repeat L3_talk_lawson_measurement

**Lawson Vanderbilt** [停下手里的动作]
> 哪一件还没问完？

@goto lawson_hub

## 调查｜Lawson 办公区净高

@investigate 5304 scene:5016

【演出】Zack 完成办公区地面至天花板的测量，记录上下测点。

**Zack Brennan** [内心]
> 净高约三点六米。这里的楼板也要另查厚度。

@get item:5304
@end

## 调查｜建筑材料登记册附图

@investigate 5305 scene:5016

【演出】从登记册封底夹层取出双面折页，先展开正面，再翻到背面。两处房间与外壳未按当前实测比例归位。

**Zack Brennan** [内心]
> 公开的保险、估值档案。比 Lawson 这次接管还早。
> 正面的高度比例得重新核。背面有楼板记录：一层零点三米，二层零点四米。

@get item:5305
@read document:5305.floor1_thickness=0.3
@read document:5305.floor2_thickness=0.4
@end

## 调查｜蓝色水痕

@investigate 5306 scene:5016

【演出】取景包含矿物工作台到洗手区之间的蓝色湿鞋印；另记录鞋底槽纹中残留的晶屑。

**Zack Brennan** [内心]
> 蓝色的湿鞋印，鞋底还留着晶屑。把两处都拍清楚。

@get item:5306
@end

## 调查｜Moore 公文夹

@investigate 5307 scene:5017

【演出】Zack 从搁架取下红封公文夹，转到缺损的一侧。

**Zack Brennan** [内心]
> 少了一枚黄铜牵引铆圈。断口很新，边缘不齐。
> 这一面留好。

@get item:5307
@end

## 调查｜Moore 私人授权牌

@investigate 5308 scene:5017

【演出】Zack 查看私人授权牌盒内的凭牌。牌面显示湖滨信托及 M-7。

**Zack Brennan** [内心]
> Moore 的夜间授权牌。M-7。
> 持有人可以从庄园通信设备发出专用止付指令。

@get item:5308
@end

## 小玩法接入｜第一次复原

@mechanic section_stage1
@requires items:5301,5303,5304,5305 fields:5305.floor1_thickness,5305.floor2_thickness
@location current_scene preserve_return_scene:true

**Zack Brennan** [内心]
> 实测和楼板记录齐了。把它们放回图上。

【玩法画面】先开背面网格。五个尺寸槽由玩家拖入；楼梯记录本次锁定。首次放错只弹回并显示校准记号，不播放解释对白。

@feedback repeated_same_data

界面提示：净高需要与对应楼板厚度合计。

@feedback missing_material

界面提示：仍缺一项实测。

@success section_stage1

【玩法画面】五槽正确后呈现 9－（2.7＋0.3）－（3.6＋0.4）＝2 米；自动翻回正面，下部模块贴地，上部模块贴 9 米上沿，中间显出约 2 米未登记阴影带。

**Zack Brennan** [内心]
> 中间少了这一截。

@set u5_section_stage1=true
@restore current_scene

## L3_event_roundtable_locate

@scene 5006
@requires items:5301,5302,5303,5304,5305,5306,5307,5308 talks:L3_talk_vivian_measurement,L3_talk_lawson_measurement flag:u5_section_stage1

【演出】众人回到圆桌。Zack 展开已复原的折页。Moore 没有坐下，俯身看着中间的阴影带。

**Harold Moore**
> 两米。好，我看见了。可少了两米，跟舞台上那块板有什么关系？

**Charles Miller Jr.**
> 这个问题得说清。图纸上有空处，不等于入口就在你想查的地方。

**Zack Brennan**
> 所以还要定位。

**Pierce**
> 你还是在找另一个人离开礼堂的路。

**Zack Brennan**
> 你的观察没能排除另一人从正门进去。

**Pierce** [抬眼，压住话头]
> 没能排除。不是我看见他进去了。

**Zack Brennan**
> 我没说你看见。

**Charles Miller Jr.**
> 可破门时门闩在里面，我们也没在现场找到另一个人。

**Zack Brennan**
> 如果有人进来刺了那一刀，同一扇门解释不了他怎么走的。

**Vivian**
> 而楼梯偏偏在那一刀之后转回了 A。

**Harold Moore**
> 这些我都听过。你总不能把它们往两米空白里一扔，就算找到了路。

**Zack Brennan** [把折页正面转向自己]
> 那就看哪份实测接得上。

@segment open_section_stage2
@mechanic section_stage2

【玩法画面】同一张已复原图纸正面。玩家选择结构记录，拖到舞台侧零米基准；第一阶段数值保持锁定。

@feedback wrong_record

界面提示：它能确认高度，不能形成抵达这段空间的路径。

@feedback wrong_baseline

【玩法画面】记录不吸附，标高线不闭合。

@success section_stage2

【玩法画面】A 位楼梯落在舞台零米基准，顶端三米标线与未登记空间下沿闭合；所对布景板出现待查问号。

**Lawson Vanderbilt** [目光沿闭合的尺寸线移过去]
> 到得了同一高度。板后究竟是什么，图上还是没有。

**Zack Brennan**
> 去看实物。

**Charles Miller Jr.** [收回按住折页的手]
> 请。既然量到了这里，就把这块板查清楚。

@set u5_section_stage2=true
@event_complete L3_roundtable
@change_scene 5020
@goto L3_event_stage_door_open

## L3_event_stage_door_open

@scene 5020

【演出】众人直接前往礼堂，沿 A 位楼梯登到顶端。Zack 先检查布景板边缘，轻敲板面。狭窄平台上，其余人依次停住。

**Zack Brennan**
> 灰在这里断了。敲着是空的，还有冷风。

**Pierce**
> 手放哪儿？

**Zack Brennan**
> 没把手。先试板边。

【演出】Zack 抵住板边试推。布景板向内让开，露出连续夹层。门缘可见异物将锁芯卡在退栓状态。

【突发事件需求｜必须画面呈现】触发位置：试推布景板；画面必须让玩家看见：板打开后约两米高的连续夹层，以及门缘异物卡住退栓的状态；门内门外各有一处三瓣不等、左右断翼的浅槽，没有普通把手；承载的信息：实地确认舞台侧入口与双面槽形；接回对白的位置：Pierce 看向锁芯。槽形只短暂特写，不开放热点或拓片。

**Pierce** [看向门缘]
> 锁栓没顶出来。

**Zack Brennan**
> 有东西把锁芯卡在退栓位置了。先留着。

**Vivian** [跨过门边，停住]
> 真能走人……不是板后多留了一点地方。

**Lawson Vanderbilt**
> 差的那两米在这儿。

**Zack Brennan** [回望平台与夹层地面]
> 公开楼层里，能在这个高度直接走进来的，是舞台这一处。

**Harold Moore**
> 门开了。现在还要所有人堵在这儿？

**Zack Brennan**
> 往前，先看岔口。

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
> 黄铜铆圈。断面很新，不规则的边还在。

@get item:5309
@end

## 调查｜催收急件

@investigate 5310 scene:5018

【演出】Zack 查看文件的签署栏、时限与经办标记。

**Zack Brennan** [内心]
> 需要老 Charles 签字的催收急件。当夜截止，Moore 经办。

@get item:5310
@end

## 调查｜湿地毯上的鞋印

@investigate 5311 scene:5018

【演出】翻倒的清水壶旁，整段狭窄通道的地毯已经浸湿。Zack 在不覆盖原有足迹的位置取景，逐一记录大小、纹路与踩踏深浅。

【突发事件需求｜必须画面呈现】触发位置：足迹调查；画面必须让玩家看见：覆盖整段通道的湿地毯、翻倒清水壶，以及大量叠压乱向但可按大小、纹路、深浅稳定分成四组的足迹；承载的信息：至少四人经过，身份和先后无法确认；接回对白的位置：Zack 内心观察。不用箭头将各组对应到具体人物。

**Zack Brennan** [内心]
> 这一片都湿了。脚印压着脚印，来回的方向也乱。
> 大小、纹路，再看踩下去的深浅……能分出四组。至少四个人走过。
> 谁先谁后，看不清。

@get item:5311
@end

## 环境观察｜夹层文件柜

@investigate 5353 scene:5018

【演出】Zack 停在文件柜前，查看可见的档案标识与翻动、缺页痕迹，没有展开逐页调查。

**Zack Brennan** [内心]
> Miller 家的材料。1912。
> 翻动过，还缺了页。这里得仔细查。

@observe environment:5353
@end

## 调查｜文件柜后方局部墙面

@investigate 5312 scene:5018

【演出】Zack 从现有可见角度观察文件柜后方的一小段墙面，只对局部材质差异取景；柜与墙均留在原处。

**Zack Brennan** [内心]
> 这小段用的材质不一样，像是为隔音另加的。
> 先拍下这个位置。

@get item:5312
@end

## L3_talk_moore_before_expose

@scene 5018

【演出】Moore 站在岔口一侧。Zack 朝他走近时，他先直起身，截住了开口的时机。

**Harold Moore**
> 我昨晚没有进入过那条夹层。你找到一条通道，也不用挨个把人塞进去。

**Zack Brennan**
> “没有进入过。”我记下了。

**Harold Moore**
> 记清楚。别再让我为同一句话耽误时间。

@get testimony:5083001
@end

### 回访｜Moore

@repeat L3_talk_moore_before_expose

**Harold Moore**
> 我已经回答过了。没有进去过。

@end

## 回查｜湖滨信托夜间止付密电

@review item:5106

【演出】Zack 重看先前取得的发送联，停留在时间与授权号栏。

**Zack Brennan** [内心]
> 二十一点三十八分，M-7。死亡登记已经发出。

@end

## L3_expose_moore

@scene 5018
@requires doubts:5301,5302,5303 items:5106,5307,5308,5309,5310,5311,5312 environments:5352,5353 testimonies:5083001,5063001 flags:u5_section_stage1,u5_section_stage2,u5_stage2_exploration_unlocked

【演出】众人在第一岔口停住。Zack 走到 Moore 面前，给身后的人留出看清证物的位置。

**Harold Moore**
> 还有什么？查到了现在，谁都有几句可疑的话，你打算问到什么时候？

**Zack Brennan**
> 从你刚才那句开始。

### R1｜是否进入夹层

**Harold Moore** [压下不耐]
> 我昨晚没有进入过那条夹层。

@lie testimony:5083001
@present items:5307,5309

@failure r1

**Harold Moore**
> 这就能把我放进这条通道？你再看看。

**Zack Brennan**
> 我换一组。

@retry r1

@success r1

【演出】Zack 将第一岔口的铆圈放到公文夹缺口旁，两处新鲜断面并列展示。

【突发事件需求｜必须画面呈现】触发位置：R1 正确出示；画面必须让玩家看见：铆圈与公文夹新鲜不规则断面的对应关系，使用同一断面形状，保留物体各自完整形态；承载的信息：公文夹到过第一岔口；接回对白的位置：Zack 要求 Moore 看断口。此处不生成拼合报告。

**Zack Brennan**
> 你的公文夹。在房间里找到时，少了这个。

**Harold Moore** [伸手，停在公文夹前]
> 你把它也拿来了。

**Zack Brennan**
> 铆圈在这处岔口。看断面，不是只看颜色。

**Harold Moore**
> ……是它。把断口放开，别弄坏了。

**Zack Brennan**
> 公文夹来过。你呢？

**Harold Moore** [看了一眼旁边的人，收回手]
> 我进去过。偶然看见入口，在门边站了站。没有追着 Charles 找人。

**Vivian**
> 那刚才何必说得那么干净？

**Harold Moore**
> 因为你们会把看一眼说成另一回事。就像现在。

### R2｜进入的目的

**Harold Moore**
> 我不是去找 Charles，只是看见有条通道，进去看了一眼。

@lie expose:5083901
@present items:5310

@failure r2

**Harold Moore**
> 我已经承认进去了。你还拿这个问我为什么？

**Zack Brennan**
> 问的是目的。继续。

@retry r2

@success r2

【演出】Zack 展开催收急件，将签署栏和当夜时限转向 Moore。

**Zack Brennan**
> 也是在第一岔口。你的经办标记，需要 Charles 签字，当夜截止。

**Harold Moore**
> 银行的急件。你想看什么？

**Zack Brennan**
> 你带着这份，进去看风景？

**Harold Moore** [嘴角绷紧]
> 我在找他签字。他拖着不办，过了时限，风险留给湖滨信托。难道我就坐在房间里等？

**Charles Miller Jr.**
> 有事找父亲，可以直说。你先说从没来过，又说只是看一眼。

**Harold Moore**
> 现在直说了。我追到第一岔口，要求他签。他拒绝，接着往前走。我就折回去了。

**Zack Brennan**
> 拒绝后你就走了？

**Harold Moore**
> 对。我没有继续追，也不知道后面出了什么事。

### R3｜何时知道死讯

**Harold Moore** [视线从急件移回 Zack]
> 我离开时 Charles 还活着。直到所有人破门，我才知道他已经死亡。

@lie expose:5083902
@present items:5106,5308

@failure r3

**Harold Moore**
> 你在问我什么时候知道死讯。这些回答不了。

**Zack Brennan**
> 那就看时间和授权。

@retry r3

@success r3

【演出】Zack 将止付发送联与私人授权牌并列。先停留在两处 M-7，再让 Moore 看发送时间。

**Zack Brennan**
> 二十一点三十八分。M-7 发出的死亡止付。

**Harold Moore**
> 那是银行的处置。

**Zack Brennan**
> M-7 是你的授权牌。

**Harold Moore**
> 是我的。指令也是我发的。

**Pierce**
> 我们二十二点破门。早了二十二分钟。

**Charles Miller Jr.** [脸上的客气收住]
> Moore 先生。我们还没看见父亲，你已经向银行报了他的死亡？

**Harold Moore**
> 我不能让交易继续。

**Zack Brennan**
> 我问你看见了什么。

**Harold Moore** [片刻不答，随后把声音压低]
> 没看见。折返的时候，前面有一声很重的闷响。

**Zack Brennan**
> 你回去看了？

**Harold Moore**
> 没有。

**Zack Brennan**
> 叫人了吗？

**Harold Moore**
> 没有。我作了判断，先冻结交易。等人人都来确认，钱还会留在那儿等我吗？

**Lawson Vanderbilt** [从墙边直起身]
> 你连人怎么样都没看，就能填“死亡”？

**Harold Moore**
> 最坏的情况必须先处理。

**Zack Brennan**
> 你处理了钱。人呢？

**Harold Moore** [停了一下，伸手压平急件边缘]
> 我没到舞台，更没拿刀刺他。这个你听清了。

**Zack Brennan**
> 听清了。你没回去看，也没求救。二十一点三十八分，你用死亡登记冻结了交易。

**Harold Moore**
> 是。商业判断。不要把它改写成我杀了人。

@event_complete L3_expose
@goto L3_post_expose_study_door

## L3_post_expose_study_door

@scene 5018

【演出】Moore 要收起文件，Zack 的手停在纸边，挡住他的动作。众人仍在第一岔口，没有离开夹层。

**Zack Brennan**
> 你说自己在这里折返。也可能继续走向了舞台。

**Harold Moore**
> 可能。你已经开始靠“可能”说话了。

**Pierce**
> 你从舞台那头进出，就得把那边的事说清。

**Harold Moore** [猛地看向 Pierce，又转回 Zack]
> 谁说我是从舞台进去的？
> 你只证明我进过这里，却擅自认定我是从舞台这一端进去的。

**Zack Brennan**
> 你从哪儿进的？

**Harold Moore**
> 跟我来。用不了你量一遍房子的工夫。

【演出】Moore 从第一岔口走向书房端。Pierce 紧跟，其余人沿狭窄夹层单列前行，不返回礼堂、不交还操作权。

@change_scene 5021 continuation:same_talk
@segment study_ceiling_door_open

【演出】Moore 在先前看似封死的一端停下。他俯身沿饰面边缘寻找，按动几乎不可辨认的暗扣，打开夹层地面上的门；下方露出老 Charles 书房。

【突发事件需求｜必须画面呈现】触发位置：Moore 操作暗扣；画面必须让玩家看见：门位于夹层地面，向下通往老 Charles 书房天花板；不是侧墙门，不回舞台重复进门；打开后同时带出附近一大片凌乱重叠足迹；承载的信息：第二入口的垂直位置、Moore 熟悉此入口、至少四组经过痕迹；接回对白的位置：Lawson 看向下方。不得凭此画面给鞋印标上具体姓名或顺序。

**Lawson Vanderbilt** [在门边蹲下，向下看]
> 书房……门在天花板上。

**Charles Miller Jr.** [停在后面，让出门边的位置]
> Moore 先生，解释一下。

**Harold Moore**
> 我亲眼看见 Charles 从书房进来。我带着急件跟进去，追到第一岔口，就刚才那个地方。

**Zack Brennan**
> 你看着他打开这里？

**Harold Moore**
> 是。他进去，我跟上。签字没谈成，我从这里回去。我一直说，我没到舞台。

**Pierce** [弯腰查看入口附近地面]
> 这边也有脚印。都叠在一起了。

**Zack Brennan** [查看各处纹路与踩踏深浅]
> 大小、纹路、深浅，能分成四组。至少四个人经过这里。

**Harold Moore**
> 我，Charles——还有人。除了我们，另外两个人是谁？

**Zack Brennan**
> 还认不出来。也分不清谁先谁后。

**Harold Moore**
> 那就去找。别堵着我一个。

**Zack Brennan** [起身，仍挡在 Moore 与众人之间]
> 我会找。你打开的是另一处入口，不是你折返的证明。

**Harold Moore**
> 至少你现在知道，我用不着从舞台上来。

**Zack Brennan**
> 这点改正。止付的事不改。

【演出】Moore 抿紧嘴，没有再答。Zack 看了一眼书房下方，再回看门边乱向的足迹。

**Zack Brennan**
> 书房也得查。

@observe environment:5354
@set u5_study_door_open=true
@event_complete L3_post_expose
@loop_end 3 -> L4_opening_escort_corridor
