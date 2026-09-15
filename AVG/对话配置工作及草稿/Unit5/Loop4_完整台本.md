# Unit5 L4｜完整对白第一版

> 审阅稿。当前模型完整初稿 → Gemini 3.8 润色 → 主模型事实及结构核对。API 原文保留，必要修正另记。未同步 JSON、预览配置或 Unity。
> 阅读顺序：押送与 Emma 坦白 → 录音室及自由调查 → Mary 三轮指证（第二轮后含 Mickey 推理）→ 药物争议 → 后台三材料小推理。自由调查顺序不由排版锁定。
> `@` 为设计期控制标记；成功／失败、条件段互斥播放，回访不重复发放证据。玩法适配与画面需求尚待实现；Emma 开门获释在 L5 开场。

# L4 第一包｜走廊坦白与自由调查

## L4_opening_escort_corridor

@scene 5007

【演出】Moore 由警员押向看守房。Pierce 走在侧面，Zack 跟在后方。经过 Emma 房门时，Moore 停了一下。

**Harold Moore**

> 书房那扇暗门还是我开给你们看的。现在倒好，把我往没门可开的屋子里关。

**Pierce**

> 走你的。

**Emma O'Malley** [从房门内出声]

> 书房暗门？……Zack？

【演出】Zack 停在门边。Emma 走近门口，看向正被带走的 Moore。

**Emma O'Malley**

> 书房也能进夹层？他是打那儿进去的？

**Zack Brennan**

> 他是这么招的。刚才开了书房天花板上的暗门，确实通夹层。

**Harold Moore** [回过头]

> 里面还有四组脚印呢。记得把另外几位也请来作伴，别光可着我一个人关。

**Pierce** [将手指向看守房]

> 进去。

【演出】警员将 Moore 带入独立看守房并关门。Pierce 确认看守安排后离开。走廊安静下来，Moore 不再隔门参与谈话。

@set u5_moore_isolated=true

**Emma O'Malley** [仍看着关上的门，随后转向 Zack]

> ……我以前真不知道书房也有暗道。

**Zack Brennan**

> 我也是刚才查到的。

**Emma O'Malley**

> ……其实还有一件事。你也不知道。

【演出】Zack 等她继续。Emma 扶着门边，拇指从木边上收回来。

**Emma O'Malley**

> 晚宴前，我去找了 Watts。让他帮我在庄园外头安排单向电气刻录。
> 我约 Charles 九点半在礼堂碰头，不光是想当面套话。我想把那老头说的一字一句全刻下来。

**Zack Brennan**

> 你在后台引了线？

**Emma O'Malley**

> 就在后台深处那间录音室。舞台麦克风的声音顺着接线盒直接往庄园外送。
> 屋里没配刻盘机，也没有母盘或者放音设备。那地方根本没法当场回放。

**Zack Brennan**

> 那 Watts 那边录着了吗？

**Emma O'Malley** [摇头]

> 不清楚。要是成了，母盘应该在他办公室。可现在外头那场要命的雪，联系已经断了。
> 这条线撑了多久，到底录没录上……我一概不清楚。别把我原本的算盘，当成已经到手的铁证。

**Zack Brennan**

> 我只认你实际干了什么。

**Emma O'Malley**

> 还有我瞒了你什么。
> 彩排那张批准联……你带回圆桌公开了。你明明知道交出去会让我处境更糟，但你还是照我们的约定办了。

**Zack Brennan**

> 答应过的事，就得这么办。

**Emma O'Malley** [停顿，目光没有躲开]

> 我要求你把所有查到的事全摊开，可转头我自己也替你做了主，自作主张挑挑拣拣地瞒你。这事，是我对不起你。

**Zack Brennan**

> 我收下了。不过，你瞒我的这码事，跟我之前瞒你的，不能拿来两相抵消。

**Emma O'Malley**

> 我也没打算拿这当借口。

【演出】两人短暂沉默。Zack 没再追问她为什么独自行动，将笔记本翻到空白处。

**Zack Brennan**

> 线接上以后，你脑子里最后的记忆停在哪儿？

**Emma O'Malley**

> 喝酒。杯上标着 E-12。
> 接好线后我喝了那杯酒，后来意识就开始发混。最后是在杯子边上，想动，动弹不得。

**Zack Brennan**

> 就在录音室里？

**Emma O'Malley**

> 对，就那间屋。到这儿记忆就全掐断了。再往后的事……我编不出来，也没法凭空给你补。

**Zack Brennan** [合上笔记本]

> 够了，我去查那只杯子。

**Emma O'Malley**

> 查到什么，回头告诉我一声。

**Zack Brennan**

> 放心。

【演出】Zack 离开门边，Emma 留在独立客房。警员仍在看守位置。

@set u5_emma_remote_plan_disclosed=true

@event_complete L4_opening

@change_scene 5022

@goto L4_opening_recording_room_arrival

## L4_opening_recording_room_arrival

@scene 5022

【演出】Zack 进入舞台后台深处的录音室。Foster 在现场等候；地上的倒杯和线缆保持原位。

**Zack Brennan**

> Emma 说她接好线喝了杯 E-12，接着就倒在杯子旁边动不了了。

**Eleanor Foster**

> 那就以这地方为准。杯子先别挪动，保持原样。

**Zack Brennan** [俯身查看杯号]

> E-12……找到了。

@event_complete L4_recording_arrival

@release exploration

## L4_talk_foster_e12

@scene 5022

**Zack Brennan**

> 这杯底剩下的残液，查出什么成分没有？

**Eleanor Foster**

> 简易检验有结果了。这只 E-12 里留有安眠药痕迹，足以让人失去行动能力。

**Zack Brennan**

> 别的杯子呢？只有这一杯被动了手脚？

**Eleanor Foster**

> 只有 Emma 用的这只 E-12 检出安眠药痕迹。这已经足以让她失去行动能力，不必拿酒量来解释。

**Zack Brennan**

> 冲着她专程下的套。

**Eleanor Foster**

> 杯子里有药，这是事实。但药是谁放进去的，检验回答不了。

**Zack Brennan**

> 明白，事实和推论我分得清。

@get testimony:5054001

@end

### 回访｜Foster

@repeat L4_talk_foster_e12

**Eleanor Foster**

> E-12 留有足以使人失去行动能力的安眠药痕迹。至于下药的那双手是谁的，那属于你的工作。

@end

## 调查｜倒下的 E-12 酒杯

@investigate 5401 scene:5022

【演出】对倒杯位置、E-12 标记及残液拍照，原杯不拾取。

**Zack Brennan** [内心]

> E-12，倒在录音室地面。她记忆彻底中断前，人就在这只杯子旁边。

@get item:5401

@if has_testimony:5054001

**Zack Brennan** [内心]

> Foster 验出来的安眠药痕迹，单单落在了这一只杯子里。

@endif

@end

## 调查｜录音室至舞台的跨血拖痕

@investigate 5402 scene:5022

【演出】从 E-12 杯旁取景，沿连续擦抹纹理记录至舞台正面；交叉血区与残留礼服纤维另留近照。

【突发事件需求｜必须画面呈现】触发位置：拖痕调查；画面必须让玩家看见：杯旁起点、连续拖擦至舞台正面的路径，以及拖痕覆盖在既有致命喷溅血区上方的交叉点；宽度、纤维及擦抹纹理与 L1 礼服记录一致，不增加反向痕迹；承载的信息：可供玩家复核的方向与先后；接回对白的位置：Zack 观察记录。此处不出现拖行者人影或身份。

**Zack Brennan** [内心]

> 拖痕从杯子旁一路延伸到舞台前头。抹擦的痕迹宽度、刮蹭下来的织物纤维，全跟 Emma 晚礼服后背一致。
> 还有这个交叉点——拖擦的血痕，明明白白叠在了那片已经形成的致命喷溅血迹上方。
> 没有她从舞台正面返回录音室的反向移动痕迹。两层血叠压的细节，必须再拍一张。

@get item:5402

@end

## 环境观察｜单向拾音接线盒

@investigate 5451 scene:5022

【演出】Zack 沿舞台麦克风线缆查看接线盒与向外延伸的线路，没有尝试回放。

**Zack Brennan** [内心]

> 舞台上的麦克风走线接到这儿，再单向往庄园外侧排。
> 这间屋里没有刻盘机，也没有母盘或者能重放的设备。光看这堆线缆，根本没法断定那头到底有没有录成。

@observe environment:5451

@end

## 环境观察｜录音室隔音层

@investigate 5452 scene:5022

【演出】Zack 用 L3 局部墙面照片对照录音室墙面；两处材质的纹理与层叠结构相应。

**Zack Brennan** [内心]

> 文件柜后那一小段，用的是同类隔音材质。这儿靠它隔开内外声音。
> 舞台的声音全靠电缆直接通进来，压根用不着穿透这道墙。

@review item:5312

@observe environment:5452

@end

## L4_talk_butler_medication

@scene 5023

【演出】Zack 走到护士站。管家看见他关注药剂盒，停下等他问话。

**Zack Brennan**

> 老 Charles 平时按时吃的心脏病药，你熟吗？

**Butler**

> 每次整整两片，蓝色药丸。

**Zack Brennan**

> 这属于他长期的日常剂量？

**Butler**

> 是的，Brennan 先生。老 Charles 先生每次服两片蓝色心脏病药。

**Zack Brennan**

> 知道了。我得去查查当晚送过去的那一剂。

@get testimony:5134001

@end

### 回访｜管家

@repeat L4_talk_butler_medication

**Butler**

> 平时每次两片蓝色心脏病药，先生。

@end

## L4_talk_mary_delivery

@scene 5023

【演出】Mary 戴着面罩，站在护士站。Zack 走近时，她先转向他，声音平稳。

**Mary Jones**

> 您是在查给老 Charles 送药的事？二十点三十分那一趟，是我经手的。

**Zack Brennan**

> 具体说说过程。你当时都做了什么？

**Mary Jones**

> 我按时间进了老 Charles 先生的房间，亲手把心脏病药送给他。

**Zack Brennan**

> 中间转没转过别人的手？

**Mary Jones**

> 绝没有。从我手里直接送过去的，中途绝对没经过第二个人。

@get testimony:5094001

@end

### 回访｜Mary

@repeat L4_talk_mary_delivery

**Mary Jones**

> 二十点三十分，我亲手把心脏病药送到老先生房里。没有任何人代劳。

@end

## 调查｜心脏病药剂盒

@investigate 5403 scene:5023

【演出】查看药剂盒正面图像，再保留原盒。包装的药片图像为蓝色，文字不说明颜色。

【突发事件需求｜必须画面呈现】触发位置：药盒调查；画面必须让玩家看见：正常药片的蓝色图像，不能由印刷文字写“蓝色药片”代替；承载的信息：与后续实物比较的外观；接回对白的位置：Zack 看药盒图示。

**Zack Brennan** [内心]

> 心脏病处方药。包装盒上印着药片的样式和颜色……先收着，留着比对。

@get item:5403

@end

## 环境观察｜护士站排班表

@investigate 5453 scene:5023

**Zack Brennan** [内心]

> 晚上八点半，Mary，负责给老 Charles 送心脏病药。排班表上白纸黑字记着她的差事。

@observe environment:5453

@end

## 环境观察｜医用乙醚

@investigate 5454 scene:5023

【演出】护士站存放的医用乙醚保持密封，只查看外观。

**Zack Brennan** [内心]

> 医用乙醚。现在密封着。

@observe environment:5454

@end

## 环境观察｜书房废纸篓

@investigate 5455 scene:5021

【演出】Zack 翻查废纸篓，看到废纸深处压着的手帕。

**Zack Brennan** [内心]

> 纸篓底下塞了块手帕，里头好像裹着硬物。

@observe environment:5455

@container contents:5404

@end

## 调查｜手帕中的两片紫色药物

@investigate 5404 scene:5021 container:5455

【演出】打开手帕，里面是两片近乎完整的紫色药。连手帕保留原物。

**Zack Brennan** [内心]

> 两片，泛紫色，药体几乎没怎么损耗。先拿手帕包好带走。

@get item:5404

@end

## 环境观察｜书房空水杯

@investigate 5456 scene:5021

**Zack Brennan** [内心]

> 杯底残留一点清水和少量粉末。服药时用过。

@observe environment:5456

@end

## 环境观察｜1912 年档案缺页处

@investigate 5457 scene:5019

【演出】Zack 正式翻查先前观察的文件柜，打开 1912 年档案至缺口。

**Zack Brennan** [内心]

> 这里缺了一页。页码、撕边和装订孔，都保持原样。

@review environment:5353

@observe environment:5457

@end

## 环境观察｜文件柜附近气味

@investigate 5458 scene:5019

【演出】Zack 靠近被翻动的档案，停下来辨认气味。

**Zack Brennan** [内心]

> 消毒剂的气味。医务室常用的那种味道，档案柜边上还没散干净。
> 那几位进出过夹层的人里头，恐怕有人平时成天跟药水打交道。得先对对当晚谁当值。

@observe environment:5458

@end

## 调查｜TideWater 毒杀文件

@investigate 5405 scene:5019

【演出】Zack 取出文件，视线停在年份、南区安排和签名处；没有笔迹比对画面。

**Zack Brennan** [内心]

> 1928 年，TideWater……南区水源投毒的细则安排。
> 签名栏是 Charles Miller。这种要命的黑账，他竟然也真敢落笔签下去……

【演出】Zack 将原件平整收好，指尖在纸边停了一瞬。

@get item:5405

@end

## 调查｜世博会计划与庄园扩建单

@investigate 5406 scene:5019

**Zack Brennan** [内心]

> 世博会计划、南区清退，连着 Miller 庄园的扩建单。
> 只要把南区的老百姓赶走，这大片地皮就能严丝合缝地并进他们的新项目里。

@get item:5406

@end

## 调查｜临时护工房里的 1912 年纸页

@investigate 5407 scene:5024

【演出】Mary 临时房间内发现单张旧页，保留页码、撕边与装订孔。

**Zack Brennan** [内心]

> 1912 年的原档残页。撕边和装订孔还在，原页先带走。

@get item:5407

@end

## 调查｜Mickey 寄出的信

@investigate 5408 scene:5024

【演出】信已拆阅。Zack 查看信封的到达信息和正文；没有 Lula 全名。

**Zack Brennan** [内心]

> 邮戳显示一周前就寄到了芝加哥，信封已经拆开了。
> Mickey 写来的，用的是旧互助网里的称呼。信里叮嘱收信人无论如何得把 Frank 在 1912 年的那份底料刨出来。

@get item:5408

@end

## 调查｜Mary Jones 的护照

@investigate 5409 scene:5024

【演出】Zack 翻至入境记录，不以肖像比较或伪造标记作判断。

**Zack Brennan** [内心]

> 姓名 Mary Jones。入境章是三天前的，路线是从墨西哥入境美国。

@get item:5409

@end

## 回查｜Emma 礼服背部的擦抹血迹

@review item:5101

**Zack Brennan** [内心]

> 礼服背面是连续擦抹的血迹。这跟人站着时溅上去的血点不一样。

@end

---

# L4 第二包｜Mary 指证、药物争议与 Emma 洗清

## L4_expose_mary

@scene 5024

@requires doubts:5401,5402,5403 items:5401,5402,5403,5404,5405,5406,5407,5408,5409,5101,5312 environments:5451,5452,5453,5457,5458 testimonies:5054001,5134001,5094001 flags:u5_moore_isolated,u5_emma_remote_plan_disclosed

【演出】Mary 戴着面罩站在临时房间内。Zack 走到她面前，Pierce 留在出口旁，Foster 站在能看清证物的位置。

**Mary Jones** [看向 Zack 手中的证物]

> 屋也翻过了，现在还要盘问送药的事？

**Zack Brennan**

> 二十点三十分，你说亲手送进老 Charles 房间，中途没经别人的手。

**Mary Jones**

> 对。心脏病药，我亲手送的。自己做过什么我还不至于记错。

### R1｜有没有换药

**Mary Jones**

> 我送进去的就是两片蓝色药物，Charles 平时吃的药。我没换过。

@lie testimony:5094001 semantic_anchor:onsite_escalation

@present items:5403,5404

@failure r1

**Mary Jones**

> 拿这个出来，能说明我送的不是心脏病药？

**Zack Brennan**

> 看看送进去的那一剂。

@retry r1

@success r1

【演出】Zack 并列放好药盒与手帕中的两片紫色药。

【突发事件需求｜必须画面呈现】触发位置：R1 正确出示；画面必须让玩家看见：药盒图像的蓝色药片，与手帕里两片近乎完整的紫色实物；颜色来自图像和实物，药盒文字不标颜色；承载的信息：整剂数量一致、外观不一致；接回对白的位置：Zack 让 Mary 看实物。紫片没有药性标签。

**Zack Brennan**

> 管家说他每次吃两片蓝的。药盒上的图样也画得清清楚楚。

**Mary Jones**

> 我送进去的就是平时的药。

**Zack Brennan**

> 书房纸篓的手帕里包着两片紫的，近乎完整。

**Mary Jones** [低头看着手帕，没立刻接话]

> 他没咽……

**Zack Brennan**

> 他吐出来了。你刚才说亲手送进去的，没过第二个人。

**Mary Jones**

> 东西是我送的。

**Zack Brennan**

> 盯着这两片，再跟我说一遍你没换过。

**Mary Jones** [把手从证物边收回]

> 行，药是我换的。但那不是毒药，只是安眠药。我得让他睡过去一阵子。

**Zack Brennan**

> 弄睡他干什么？

**Mary Jones**

> 照护上的安排。你们查出一条暗道，就打算把我干的所有事都往谋杀上套？

### R2｜是否进入暗门取页

**Mary Jones**

> 那只是护理判断。我没进过书房暗门，也没从夹层拿走任何东西。

@lie expose:5094901

@present items:5407

@failure r2

**Mary Jones**

> 我说了没进过书房暗门、没拿过里面的东西。你拿这玩意儿对着我干什么？

**Zack Brennan**

> 咱们谈的是你拿没拿过夹层里的东西。再核对。

@retry r2

@success r2

【演出】Zack 展示在临时护工房取得的原页，并对照之前观察的文件柜档案缺口。

【突发事件需求｜必须画面呈现】触发位置：R2 正确出示；画面必须让玩家看见：原页页码、撕边、装订孔与已观察的档案缺口相对应；承载的信息：房内这页来自夹层档案；接回对白的位置：Zack 指出对应。对照不是新生成的拼合证据，不播放 Mary 进入或撕页的回忆画面。

**Zack Brennan**

> 纸是在你房间搜出来的。页码、撕下来的边，还有装订孔，全都严丝合缝。

**Mary Jones** [没有看他，目光停在纸上]

> 别折边角。

**Zack Brennan**

> 夹层柜子里缺的，刚好是这张。

**Mary Jones**

> 我长着耳朵呢。

**Zack Brennan**

> 刚才还说没拿过里面的东西。

**Mary Jones** [缓慢抬头]

> 进去了。东西是我拿的。
> 可我只是替人取回一份材料。Charles 死不死，跟这没关系。

### 中间推理｜谁委托了 Mary

@mechanic mickey_inference

@requires items:5408,5407 previous_round:2

【推理界面】谁会委托“Mary Jones”潜入 Miller 庄园，寻找 1912 年材料？玩家可回看旧案线索、Frank 的关系与来信。

@answer "Mickey" -> mickey_correct

@answer "Harold Moore" -> mickey_wrong

@answer "Lawson Vanderbilt" -> mickey_wrong

@path mickey_wrong

**Zack Brennan** [内心]

> 委托人找的是什么，信里提到了谁。再顺一遍。

@retry mickey_inference

@path mickey_correct

@set u5_mickey_inference_completed=true

**Zack Brennan**

> Mickey。信里让你找 Frank 留下的那份 1912 年记录。

**Mary Jones** [压住呼吸，看向信]

> 你看过了。

**Zack Brennan**

> 如果找你的是 Mickey……你真叫 Mary Jones？

### R3｜是不是 Mary Jones

**Mary Jones**

> 我当然是 Mary Jones。为什么问这个？

@lie expose:5094902

@requires flag:u5_mickey_inference_completed

@present items:5408,5409

@failure r3

**Mary Jones**

> 我叫什么跟案子有什么关系？

**Zack Brennan**

> 现在查的就是你的底细。重看一眼。

@retry r3

@success r3

【演出】Zack 将已拆阅的信与护照入境记录并列，视线在两处日期之间停留。

**Zack Brennan**

> 这封信一个礼拜前就寄到了芝加哥，有人收下，还拆了信封。
> 但护照上的 Mary Jones，三天前才从墨西哥入境美国。

**Mary Jones**

> ……

**Zack Brennan**

> 正牌的护工上周人还在境外，拆信的这位却早就在城里待着了。
> 你才是收信的人。你到底叫什么？

【演出】Mary 看着旧信，伸手摘下面罩。她将面罩放下，重新迎上 Zack 的目光。

【突发事件需求｜必须画面呈现】触发位置：R3 成功后摘面罩；画面必须让玩家看见：同一位临时护工摘下面罩，显露 Lula 的既定身份面貌；承载的信息：Mary 与 Lula 是同一人，换的是名字显示而非新增人物；接回对白的位置：她自报姓名。

**Lula Washington**

> Lula Washington。
> Frank 的妻子。现在你可以叫我本名了。

@display_name npc:509 name:Lula_Washington

@event_complete L4_expose

@goto L4_post_expose_drug_dispute

## L4_post_expose_drug_dispute

@scene 5024

【演出】Lula 将面罩留在一边，手仍靠近那张旧信。Pierce 从门边走近，Foster 没有伸手收走药物。

**Lula Washington**

> Mickey 留话，让我接着把 Frank 那份 1912 年的底子找出来。我就是为了这个进来的。
> 顶别人的名字、摸进暗门、拿走那张纸，我都认。药也是我掉包的。

**Zack Brennan**

> 把两片蓝色的心脏病药换成紫色的。

**Lula Washington**

> 就两片普通片剂安眠药。我得让 Charles 睡着，好有工夫继续找材料。我没想弄死他。

**Pierce**

> 假名字混进庄园，偷换雇主的药，连暗门在哪儿都门儿清。抓着了你当然咬定是安眠药。
> 谁能保证那不是毒药？

**Lula Washington** [将手从旧信边移开，转身面对他]

> 把药封存起来。等雪停了，正式送检。

**Pierce**

> 凭你一张嘴，我们就得信？

**Lula Washington**

> 我让你送去验，没求你信我。

**Eleanor Foster**

> 庄园现在的条件，做不了严密的成分比对。我没法在眼下给这两片药下定论。

**Pierce**

> 那它照样可能要人命。

**Eleanor Foster**

> 那是你的推测，那是她的口供。都不是化验单。

**Lula Washington**

> 所以先收好。别凭一句“可能”，就急着把杀人的帽子扣我头上。

**Zack Brennan**

> 药会封存。换药和拿纸算招了，但致命伤是那一刀。

**Pierce**

> 你还打算折腾什么？

**Zack Brennan**

> 搞清楚 Emma 到底是怎么挪到尸体边上的。去后台，把现场记录拼在一块儿看。

【演出】Zack 收好原始材料。Pierce 随 Lula 一同离开临时房间，Foster 跟上。Moore 不在场。

@event_complete L4_drug_dispute

@change_scene 5011

@goto L4_event_clear_emma

## L4_event_clear_emma

@scene 5011

@requires items:5401,5101,5402 testimony:5054001 event:L4_drug_dispute

【演出】众人来到舞台后台，Vivian 与小 Charles 加入。Zack 摊开倒杯照片、礼服记录与拖痕照片。Emma 仍在独立客房，没有随行。

**Charles Miller Jr.**

> Brennan 先生，特意把我们叫过来，是看到什么了？

**Zack Brennan**

> Emma 最后有意识是在录音室，倒在杯子旁边动不了。可我们破门进去的时候，她人却在尸体旁边。

**Pierce**

> 刀也在她手里。

**Zack Brennan**

> 所以才得看清楚，这两处地方中间到底发生了什么。

**Eleanor Foster**

> E-12 杯底的残液确实有安眠药成分，足够让人丧失行动力。至于她是怎么过去的，看地上的痕迹说话。

@mechanic clear_emma

@inputs items:5401,5101,5402

【推理界面】三件原材料并置，玩家查看杯旁起点、礼服背部连续擦抹、跨血拖痕的交叉点，联系失能位置与致命血区的先后。三件均须纳入本事件；未完成时保持材料界面，不提前播放结论，不生成新物品或疑点。

@success clear_emma all_three_materials_considered:true

【突发事件需求｜必须画面呈现】触发位置：三材料小推理完成；画面必须让玩家看见：杯旁起点与礼服、拖痕纹理对应，拖痕横跨已形成的致命喷溅血区并到达尸旁；承载的信息：致命刀刺在先，失能 Emma 被拖放在后；接回对白的位置：Zack 说出排除结论。不得描出投药者、拖行者或放刀者身份。

**Zack Brennan**

> 致命伤喷出来的血先落的地上，拖痕是后来从既有血区上擦过去的。
> 拖拽的起点就在 E-12 旁边，礼服背面的纤维、连续擦抹纹理跟拖痕吻合，一路接到尸体旁边。现场也没有任何她自己从舞台走回录音室的痕迹。

**Vivian** [看着礼服记录，声音低下来]

> ……她不是自己走过去摔在那里的。

**Zack Brennan**

> 人在录音室就已经动弹不得了。是 Charles 遭到致命刀刺以后，有人把她硬拖到尸体边上，再把刀塞进她手里。
> 捅人的不是她。

**Pierce** [视线从拖痕移到 Lula 身上]

> 酒里有安眠药。你刚才不是也认了，自己带的也是安眠药？

**Lula Washington**

> 我认的是换给 Charles 的两片药。

**Pierce**

> 能换掉老头的药，顺手给 Emma 的酒里也下一份有多难？把人麻倒，再塞把刀栽赃——你完全干得出来。

**Vivian**

> 这两处的药……会不会根本就是同一种？

**Eleanor Foster**

> 不能这么简单下结论。E-12 的安眠药痕迹确认了，但这俩紫片还没化验过。现阶段不能判定是同一种药，更不能认定出自同一个人之手。

**Lula Washington**

> 我刚才就说了，拿去化验。只要走正规程序检验，你们自然知道那紫片就是普通片剂安眠药。

**Pierce**

> 又是等雪停，你拿暴风雪当护身符呢。

**Lula Washington**

> Pierce，你再急着结案，也变不出化验单。

**Charles Miller Jr.** [抬手截住 Pierce 的下一句]

> 都先打住。药的事继续核实，在这里吵不出化验结果。
> 既然排除 Emma 握刀行凶的嫌疑，我支持释放她。Brennan 先生，劳烦你把下药和拖人进现场的真凶揪出来。

**Zack Brennan**

> 我会查到底。不过眼下，先把 Emma 的门开了。

【演出】Zack 收起照片。小 Charles 看向走廊方向，众人准备离开后台；开门释放留到下一段。

@set u5_emma_knife_suspicion_cleared=true

@event_complete L4_clear_emma

@loop_end 4 -> L5_opening_corridor_release
