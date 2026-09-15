# Unit5 L4｜主模型完整初稿

> 未经Gemini润色的完整初稿，保留当时措辞和控制标记。

# L4 第一包｜走廊坦白与自由调查

## L4_opening_escort_corridor

@scene 5007

【演出】Moore 由警员押向看守房。Pierce 走在侧面，Zack 跟在后方。经过 Emma 房门时，Moore 停了一下。

**Harold Moore**

> 书房暗门是我打开给你们看的。现在倒把我往一间没门可开的屋子里送。

**Pierce**

> 往前走。

**Emma O'Malley** [从房门内出声]

> 书房暗门？Zack？

【演出】Zack 停在门边。Emma 走近门口，看向正被带走的 Moore。

**Emma O'Malley**

> 书房也通夹层？他从那儿进去的？

**Zack Brennan**

> 他这么说。刚才确实打开了另一处入口，开在书房天花板上。

**Harold Moore** [回过头]

> 还有四组脚印。记得把那几个人也找来，别只给我准备房间。

**Pierce** [将手指向看守房]

> 进去。

【演出】警员将 Moore 带入独立看守房并关门。Pierce 确认看守安排后离开。走廊安静下来，Moore 不再隔门参与谈话。

@set u5_moore_isolated=true

**Emma O'Malley** [仍看着关上的门，随后转向 Zack]

> 我不知道还有书房那一处。

**Zack Brennan**

> 现在知道了。

**Emma O'Malley**

> ……还有一件事，你也不知道。

【演出】Zack 等她继续。Emma 扶着门边，拇指从木边上收回来。

**Emma O'Malley**

> 晚宴前，我找过 Watts。请他在庄园外安排单向电气刻录。
> 我约 Charles 九点半到礼堂，不只打算跟他谈。我想把他说的话留下来。

**Zack Brennan**

> 你在后台接线？

**Emma O'Malley**

> 后台深处那间录音室。舞台麦克风的声音送进接线盒，再往庄园外走。
> 我那间屋里没有刻盘机，也没有母盘和回放装置。不能在那儿重听。

**Zack Brennan**

> Watts 那边呢？

**Emma O'Malley** [摇头]

> 不知道。真录成了，母盘应该在他办公室。可暴风雪把联系断了。
> 线撑了多久，有没有录上……我都不知道。别把我这个打算，当成已经拿到的东西。

**Zack Brennan**

> 我记的是你做过什么。

**Emma O'Malley**

> 还有我没告诉你什么。
> 彩排那张批准联，你带回去说了。明知道会让我更难解释，还是照约定做了。

**Zack Brennan**

> 那是我答应你的。

**Emma O'Malley** [停顿，目光没有躲开]

> 我要求你把真相全都告诉我，可我也替你决定了什么不必知道。这件事，对不起。

**Zack Brennan**

> 我接受。你隐瞒的这一件，和我先前做的，不会互相抵掉。

**Emma O'Malley**

> 我也没想这么算。

【演出】两人短暂沉默。Zack 没再追问她为什么独自行动，将笔记本翻到空白处。

**Zack Brennan**

> 接线以后，你最后记得什么？

**Emma O'Malley**

> 喝酒。杯上有标记，E-12。
> 我把线接上，喝了那杯酒，然后脑子就开始发混。最后是在杯子旁边，想动，动不了。

**Zack Brennan**

> 在录音室里？

**Emma O'Malley**

> 对。到那儿就断了。后面的，我不能给你补。

**Zack Brennan** [合上笔记本]

> 够我去查这一杯了。

**Emma O'Malley**

> 查到什么，回来告诉我。

**Zack Brennan**

> 会的。

【演出】Zack 离开门边，Emma 留在独立客房。警员仍在看守位置。

@set u5_emma_remote_plan_disclosed=true

@event_complete L4_opening

@change_scene 5022

@goto L4_opening_recording_room_arrival

## L4_opening_recording_room_arrival

@scene 5022

【演出】Zack 进入舞台后台深处的录音室。Foster 在现场等候；地上的倒杯和线缆保持原位。

**Zack Brennan**

> Emma 说她接完线，喝过 E-12，然后在杯子旁边动不了了。

**Eleanor Foster**

> 那就从这个位置查。杯子先留在原处。

**Zack Brennan** [俯身查看杯号]

> E-12。找到了。

@event_complete L4_recording_arrival

@release exploration

## L4_talk_foster_e12

@scene 5022

**Zack Brennan**

> 那杯残液，能查出什么？

**Eleanor Foster**

> 简易检验有结果了。E-12 留有安眠药痕迹，足以让人失去行动能力。

**Zack Brennan**

> 只有这一杯？

**Eleanor Foster**

> 只有 Emma 用的 E-12 检出了这种痕迹。不是说她酒量差。

**Zack Brennan**

> 有人冲着她来的。

**Eleanor Foster**

> 这一杯被下了药，可以确认。谁下的，检验回答不了。

**Zack Brennan**

> 我会分开记。

@get testimony:5054001

@end

### 回访｜Foster

@repeat L4_talk_foster_e12

**Eleanor Foster**

> E-12 的安眠药痕迹，足以让人失去行动能力。投药的人，仍要你去查。

@end

## 调查｜倒下的 E-12 酒杯

@investigate 5401 scene:5022

【演出】对倒杯位置、E-12 标记及残液拍照，原杯不拾取。

**Zack Brennan** [内心]

> E-12，倒在录音室地上。她最后记得的，就是这杯旁边。

@get item:5401

@if has_testimony:5054001

**Zack Brennan** [内心]

> Foster 检出的安眠药痕迹，只在她用的这一杯里。

@endif

@end

## 调查｜录音室至舞台的跨血拖痕

@investigate 5402 scene:5022

【演出】从 E-12 杯旁取景，沿连续擦抹纹理记录至舞台正面；交叉血区与残留礼服纤维另留近照。

【突发事件需求｜必须画面呈现】触发位置：拖痕调查；画面必须让玩家看见：杯旁起点、连续拖擦至舞台正面的路径，以及拖痕覆盖在既有致命喷溅血区上方的交叉点；宽度、纤维及擦抹纹理与 L1 礼服记录一致，不增加反向痕迹；承载的信息：可供玩家复核的方向与先后；接回对白的位置：Zack 观察记录。此处不出现拖行者人影或身份。

**Zack Brennan** [内心]

> 从杯旁开始，一直擦到舞台正面。宽度、纤维、连续的擦纹，都跟 Emma 礼服背面合得上。
> 到这儿，拖擦盖过了已经落下的致命喷溅血迹。
> 没有她从舞台正面回到录音室的反向移动痕迹。交叉处再留一张。

@get item:5402

@end

## 环境观察｜单向拾音接线盒

@investigate 5451 scene:5022

【演出】Zack 沿舞台麦克风线缆查看接线盒与向外延伸的线路，没有尝试回放。

**Zack Brennan** [内心]

> 舞台的线进这里，再单向送出庄园。
> 这间屋里没有刻盘机、母盘或回放装置。看线路，查不出当时到底录成没有。

@observe environment:5451

@end

## 环境观察｜录音室隔音层

@investigate 5452 scene:5022

【演出】Zack 用 L3 局部墙面照片对照录音室墙面；两处材质的纹理与层叠结构相应。

**Zack Brennan** [内心]

> 和文件柜后那一小段是同类材料。这儿用来隔开内外的声音。
> 舞台的声音走独立线缆，不用穿这堵墙。

@review item:5312

@observe environment:5452

@end

## L4_talk_butler_medication

@scene 5023

【演出】Zack 走到护士站。管家看见他关注药剂盒，停下等他问话。

**Zack Brennan**

> Charles 平时的心脏病药，你清楚吗？

**Butler**

> 每次两片，蓝色的。

**Zack Brennan**

> 说的是他的日常服法？

**Butler**

> 是，先生。老 Charles 每次服用两片蓝色心脏病药。

**Zack Brennan**

> 好。我去核对送药的那一剂。

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

> 您在查送药？二十点三十分那一趟是我。

**Zack Brennan**

> 说说你做了什么。

**Mary Jones**

> 我进了老 Charles 的房间，亲手把心脏病药送给他。

**Zack Brennan**

> 药有交给别人代送吗？

**Mary Jones**

> 没有。从我手里送过去，中途没有交给第二个人。

@get testimony:5094001

@end

### 回访｜Mary

@repeat L4_talk_mary_delivery

**Mary Jones**

> 二十点三十分，我亲手送的心脏病药。没有让别人代送。

@end

## 调查｜心脏病药剂盒

@investigate 5403 scene:5023

【演出】查看药剂盒正面图像，再保留原盒。包装的药片图像为蓝色，文字不说明颜色。

【突发事件需求｜必须画面呈现】触发位置：药盒调查；画面必须让玩家看见：正常药片的蓝色图像，不能由印刷文字写“蓝色药片”代替；承载的信息：与后续实物比较的外观；接回对白的位置：Zack 看药盒图示。

**Zack Brennan** [内心]

> 心脏病药。药片的样子画在这一面，留着对照。

@get item:5403

@end

## 环境观察｜护士站排班表

@investigate 5453 scene:5023

**Zack Brennan** [内心]

> 二十点三十分，Mary，给老 Charles 送心脏病药。这里记的是派给她的差事。

@observe environment:5453

@end

## 环境观察｜医用乙醚

@investigate 5454 scene:5023

【演出】护士站存放的医用乙醚保持密封，只查看外观。

**Zack Brennan** [内心]

> 医用乙醚。密封着。

@observe environment:5454

@end

## 环境观察｜书房废纸篓

@investigate 5455 scene:5021

【演出】Zack 翻查废纸篓，看到废纸深处压着的手帕。

**Zack Brennan** [内心]

> 下面还压着一块手帕，包了东西。

@observe environment:5455

@container contents:5404

@end

## 调查｜手帕中的两片紫色药物

@investigate 5404 scene:5021 container:5455

【演出】打开手帕，里面是两片近乎完整的紫色药。连手帕保留原物。

**Zack Brennan** [内心]

> 两片，紫色，几乎还是完整的。先保留。

@get item:5404

@end

## 环境观察｜书房空水杯

@investigate 5456 scene:5021

**Zack Brennan** [内心]

> 杯底一点清水，还有少量粉末。服药时用过。

@observe environment:5456

@end

## 环境观察｜1912 年档案缺页处

@investigate 5457 scene:5019

【演出】Zack 正式翻查先前观察的文件柜，打开 1912 年档案至缺口。

**Zack Brennan** [内心]

> 少的就是这里这一页。页码、撕边、装订孔，都留着原样。

@review environment:5353

@observe environment:5457

@end

## 环境观察｜文件柜附近气味

@investigate 5458 scene:5019

【演出】Zack 靠近被翻动的档案，停下来辨认气味。

**Zack Brennan** [内心]

> 消毒剂。医务室常用的那种气味，柜子这边还留着。
> 那几名经过者里，或许有人做医务工作。先去核对当晚的职责。

@observe environment:5458

@end

## 调查｜TideWater 毒杀文件

@investigate 5405 scene:5019

【演出】Zack 取出文件，视线停在年份、南区安排和签名处；没有笔迹比对画面。

**Zack Brennan** [内心]

> 1928，TideWater……南区投毒安排。
> Charles Miller 的签名。他把这份东西也签下来了……

【演出】Zack 将原件平整收好，指尖在纸边停了一瞬。

@get item:5405

@end

## 调查｜世博会计划与庄园扩建单

@investigate 5406 scene:5019

**Zack Brennan** [内心]

> 世博会计划，南区清退，Miller 庄园扩建。
> 人从那边被清走，地就能接进他们的计划里。

@get item:5406

@end

## 调查｜临时护工房里的 1912 年纸页

@investigate 5407 scene:5024

【演出】Mary 临时房间内发现单张旧页，保留页码、撕边与装订孔。

**Zack Brennan** [内心]

> 1912 年的纸页。撕下来的边和装订孔还在，原页带走。

@get item:5407

@end

## 调查｜Mickey 寄出的信

@investigate 5408 scene:5024

【演出】信已拆阅。Zack 查看信封的到达信息和正文；没有 Lula 全名。

**Zack Brennan** [内心]

> 一周前就到芝加哥了，已经拆开读过。
> Mickey 的信，用的是旧互助网里的称呼。要收信人继续找 Frank 的 1912 年材料。

@get item:5408

@end

## 调查｜Mary Jones 的护照

@investigate 5409 scene:5024

【演出】Zack 翻至入境记录，不以肖像比较或伪造标记作判断。

**Zack Brennan** [内心]

> Mary Jones。三天前，从墨西哥入境美国。

@get item:5409

@end

## 回查｜Emma 礼服背部的擦抹血迹

@review item:5101

**Zack Brennan** [内心]

> 背面连续的擦抹血迹。跟站着时溅上去的不一样。

@end

---

# L4 第二包｜Mary 指证、药物争议与 Emma 洗清

## L4_expose_mary

@scene 5024

@requires doubts:5401,5402,5403 items:5401,5402,5403,5404,5405,5406,5407,5408,5409,5101,5312 environments:5451,5452,5453,5457,5458 testimonies:5054001,5134001,5094001 flags:u5_moore_isolated,u5_emma_remote_plan_disclosed

【演出】Mary 戴着面罩站在临时房间内。Zack 走到她面前，Pierce 留在出口旁，Foster 站在能看清证物的位置。

**Mary Jones** [看向 Zack 手中的证物]

> 我的房间查完了，还要问送药？

**Zack Brennan**

> 你说二十点三十分亲手送进去，中途没有交给第二个人。

**Mary Jones**

> 是。心脏病药，我亲手送的。做过什么我记得。

### R1｜有没有换药

**Mary Jones**

> 我送进去的就是 Charles 平时服用的两片蓝色药物。我没有换过药。

@lie testimony:5094001 semantic_anchor:onsite_escalation

@present items:5403,5404

@failure r1

**Mary Jones**

> 这能说明我送的不是心脏病药？

**Zack Brennan**

> 再核对送进去的那一剂。

@retry r1

@success r1

【演出】Zack 并列放好药盒与手帕中的两片紫色药。

【突发事件需求｜必须画面呈现】触发位置：R1 正确出示；画面必须让玩家看见：药盒图像的蓝色药片，与手帕里两片近乎完整的紫色实物；颜色来自图像和实物，药盒文字不标颜色；承载的信息：整剂数量一致、外观不一致；接回对白的位置：Zack 让 Mary 看实物。紫片没有药性标签。

**Zack Brennan**

> 管家说，他平时每次两片蓝色心脏病药。药盒上的图也对得上。

**Mary Jones**

> 我就是照常送的。

**Zack Brennan**

> 书房废纸篓，手帕里。两片紫色的，近乎完整。

**Mary Jones** [低头看着手帕，没立刻接话]

> 他没吃下去……

**Zack Brennan**

> 他吐掉的这一剂还在。你说自己亲手送进去，中途没转过手。

**Mary Jones**

> 是我送的。

**Zack Brennan**

> 那就看着这两片，再说一次没换过。

**Mary Jones** [把手从证物边收回]

> 好，是我换的。但那不是毒药，只是安眠药。我需要让他睡上一会儿。

**Zack Brennan**

> 你为什么需要他睡着？

**Mary Jones**

> 那是照护的事。你们查一条暗道，就要把我每件事都往那儿放？

### R2｜是否进入暗门取页

**Mary Jones**

> 那只是护理判断。我没有进入过书房暗门，也没有从夹层拿走任何东西。

@lie expose:5094901

@present items:5407

@failure r2

**Mary Jones**

> 我说的是没进暗门、没拿里面的东西。你拿这个问我什么？

**Zack Brennan**

> 那就回到拿没拿过东西。

@retry r2

@success r2

【演出】Zack 展示在临时护工房取得的原页，并对照之前观察的文件柜档案缺口。

【突发事件需求｜必须画面呈现】触发位置：R2 正确出示；画面必须让玩家看见：原页页码、撕边、装订孔与已观察的档案缺口相对应；承载的信息：房内这页来自夹层档案；接回对白的位置：Zack 指出对应。对照不是新生成的拼合证据，不播放 Mary 进入或撕页的回忆画面。

**Zack Brennan**

> 这一页在你房里。页码接上了，撕边和装订孔也接得上。

**Mary Jones** [没有看他，目光停在纸上]

> 别折它。

**Zack Brennan**

> 夹层文件柜少的，就是这一页。

**Mary Jones**

> 我听见了。

**Zack Brennan**

> 你说没拿过里面任何东西。

**Mary Jones** [缓慢抬头]

> 我进去过。那一页是我拿走的。
> 但我只是替人取回一份材料。这与 Charles 的死无关。

### 中间推理｜谁委托了 Mary

@mechanic mickey_inference

@requires items:5408,5407 previous_round:2

【推理界面】谁会委托“Mary Jones”潜入 Miller 庄园，寻找 1912 年材料？玩家可回看旧案线索、Frank 的关系与来信。

@answer "Mickey" -> mickey_correct

@answer "Harold Moore" -> mickey_wrong

@answer "Lawson Vanderbilt" -> mickey_wrong

@path mickey_wrong

**Zack Brennan** [内心]

> 委托找什么，信里提了谁。再对一遍。

@retry mickey_inference

@path mickey_correct

@set u5_mickey_inference_completed=true

**Zack Brennan**

> Mickey。要找的是 Frank 那份 1912 年材料。

**Mary Jones** [压住呼吸，看向信]

> 你已经翻过了。

**Zack Brennan**

> 如果委托你的人是 Mickey——你真的是 Mary Jones 吗？

### R3｜是不是 Mary Jones

**Mary Jones**

> 我当然是 Mary Jones。为什么要问这个？

@lie expose:5094902

@requires flag:u5_mickey_inference_completed

@present items:5408,5409

@failure r3

**Mary Jones**

> 这跟我叫什么有什么关系？

**Zack Brennan**

> 查的是身份。重新核对。

@retry r3

@success r3

【演出】Zack 将已拆阅的信与护照入境记录并列，视线在两处日期之间停留。

**Zack Brennan**

> 信一周前就寄到芝加哥，有人收下并拆开了。
> 护照上的 Mary Jones，三天前才从墨西哥入境美国。

**Mary Jones**

> ……

**Zack Brennan**

> 真正的 Mary 一周前还在墨西哥。可一周前，收下这封信的人已经在芝加哥。
> 你是那个收信人。你是谁？

【演出】Mary 看着旧信，伸手摘下面罩。她将面罩放下，重新迎上 Zack 的目光。

【突发事件需求｜必须画面呈现】触发位置：R3 成功后摘面罩；画面必须让玩家看见：同一位临时护工摘下面罩，显露 Lula 的既定身份面貌；承载的信息：Mary 与 Lula 是同一人，换的是名字显示而非新增人物；接回对白的位置：她自报姓名。

**Lula Washington**

> Lula Washington。
> Frank 的妻子。你现在可以叫我的名字了。

@display_name npc:509 name:Lula_Washington

@event_complete L4_expose

@goto L4_post_expose_drug_dispute

## L4_post_expose_drug_dispute

@scene 5024

【演出】Lula 将面罩留在一边，手仍靠近那张旧信。Pierce 从门边走近，Foster 没有伸手收走药物。

**Lula Washington**

> Mickey 留话，让我继续找 Frank 的 1912 年材料。我是为这个进来的。
> 冒名、进暗门、拿那一页，我认。药也是我换的。

**Zack Brennan**

> 把两片蓝色心脏病药换成了紫片。

**Lula Washington**

> 两片普通的片剂安眠药。我想让 Charles 睡着，好继续找材料。不是杀他。

**Pierce**

> 冒名进庄园，换掉他的药，还知道书房暗门。你当然会说是安眠药。
> 谁能证明那不是毒药？

**Lula Washington** [将手从旧信边移开，转身面对他]

> 把药封起来。等暴风雪停了，送出去正式检验。

**Pierce**

> 要我们现在就信你？

**Lula Washington**

> 我要你送检。不是叫你信我。

**Eleanor Foster**

> 庄园里的条件，做不了可靠的成分比对。我现在不能给这两片药定性。

**Pierce**

> 那就仍可能是毒药。

**Eleanor Foster**

> 你在怀疑。她在自述。都不是检验结果。

**Lula Washington**

> 那就留着，别拿一句“可能”替我签完罪名。

**Zack Brennan**

> 药会保留。换药和取页已经说清，刀刺还没有。

**Pierce**

> 你还想查什么？

**Zack Brennan**

> Emma 是怎么到尸体旁边的。去后台，把几份记录放在一起。

【演出】Zack 收好原始材料。Pierce 随 Lula 一同离开临时房间，Foster 跟上。Moore 不在场。

@event_complete L4_drug_dispute

@change_scene 5011

@goto L4_event_clear_emma

## L4_event_clear_emma

@scene 5011

@requires items:5401,5101,5402 testimony:5054001 event:L4_drug_dispute

【演出】众人来到舞台后台，Vivian 与小 Charles 加入。Zack 摊开倒杯照片、礼服记录与拖痕照片。Emma 仍在独立客房，没有随行。

**Charles Miller Jr.**

> Brennan 先生，你要让我们看什么？

**Zack Brennan**

> 她最后记得在录音室的杯子旁边动不了。我们破门，却在尸体旁边发现了她。

**Pierce**

> 刀也在她手里。

**Zack Brennan**

> 所以才要把中间这段看清。

**Eleanor Foster**

> E-12 的残液已检出安眠药痕迹，足以让她失去行动能力。至于后面的移动，看痕迹。

@mechanic clear_emma

@inputs items:5401,5101,5402

【推理界面】三件原材料并置，玩家查看杯旁起点、礼服背部连续擦抹、跨血拖痕的交叉点，联系失能位置与致命血区的先后。三件均须纳入本事件；未完成时保持材料界面，不提前播放结论，不生成新物品或疑点。

@success clear_emma all_three_materials_considered:true

【突发事件需求｜必须画面呈现】触发位置：三材料小推理完成；画面必须让玩家看见：杯旁起点与礼服、拖痕纹理对应，拖痕横跨已形成的致命喷溅血区并到达尸旁；承载的信息：致命刀刺在先，失能 Emma 被拖放在后；接回对白的位置：Zack 说出排除结论。不得描出投药者、拖行者或放刀者身份。

**Zack Brennan**

> 致命的喷溅血迹先落在地上，拖痕后来才从上面擦过去。
> 起点在 E-12 旁边，礼服背面的纤维和擦纹一路接到尸体旁。也没有她从舞台返回录音室的反向移动痕迹。

**Vivian** [看着礼服记录，声音低下来]

> 她不是自己走过去倒下的。

**Zack Brennan**

> 她在录音室失去行动能力。Charles 遭到致命刀刺以后，才有人把她拖到尸旁，把刀放进她手里。
> 她没刺那一刀。

**Pierce** [视线从拖痕移到 Lula 身上]

> 那杯酒有安眠药。你刚才也说，自己用的是安眠药。

**Lula Washington**

> 我说的是换给 Charles 的两片药。

**Pierce**

> 换他的药，再给 Emma 下药。把她弄倒，把刀放她手里——你也做得了。

**Vivian**

> 两边会不会用的就是一样的药？

**Eleanor Foster**

> 不能这样认。E-12 的痕迹确认了，紫片还没鉴定。现在不能说是同一种，更不能说来自同一个人。

**Lula Washington**

> 我要求送检，从刚才就说了。正式验过，你们会知道紫片只是普通安眠药。

**Pierce**

> 又要等雪停。

**Lula Washington**

> 你急着关案子，也不能替药长出一个结果。

**Charles Miller Jr.** [抬手截住 Pierce 的下一句]

> 先停。药物继续核查，别在这里互相喊出一个结论。
> Emma 持刀的嫌疑已经洗清，我支持释放她。Brennan 先生，请继续查投药和拖行的人。

**Zack Brennan**

> 我会继续。先把 Emma 房门打开。

【演出】Zack 收起照片。小 Charles 看向走廊方向，众人准备离开后台；开门释放留到下一段。

@set u5_emma_knife_suspicion_cleared=true

@event_complete L4_clear_emma

@loop_end 4 -> L5_opening_corridor_release
