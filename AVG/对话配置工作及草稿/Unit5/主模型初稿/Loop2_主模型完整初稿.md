# U5 L2｜开场与自由探索｜主模型完整初稿

## Talk: L2_opening_waking_promise.json

【场景】Emma 的独立客房。门外仍有看守。Zack 进门后停在门边；Emma 已经坐起，看了他一会儿。

**Emma O'Malley**
> 外面的人让你进来了？

**Zack Brennan**
> 嗯。

**Emma O'Malley** [看向他身后的门]
> 那把门关上吧。

【演出】Zack 合上门，走近几步，没有立刻坐到她身边。

**Zack Brennan**
> 现在感觉怎么样？

**Emma O'Malley**
> 醒着。至少这一会儿，我知道自己在干什么。
> 他们说我手里有刀。

**Zack Brennan**
> 我赶到时，你握着一把餐刀，倒在老 Charles 旁边。

**Emma O'Malley** [低头看自己的手]
> 我一点也想不起来，怎么拿到它的。

**Zack Brennan**
> 先说想得起来的。不用拼。

**Emma O'Malley**
> 彩排是我自己申请的。
> 我还约了老 Charles，九点半，到舞台见我。

**Zack Brennan** [停顿，缓缓拉开一把椅子]
> 你主动约的？

**Emma O'Malley**
> 是。我有话要当面问他。
> 这部分你可以记。我记得很清楚。

**Zack Brennan** [坐下]
> 后来呢？

**Emma O'Malley**
> 断了。前后只剩一点声音，我连它们怎么接起来都不知道。

**Zack Brennan**
> 刀呢？

**Emma O'Malley** [手指轻轻蜷起]
> 你是问，是不是我刺的？

【演出】Zack 没催她。Emma 抬眼看他，又看回自己的手。

**Emma O'Malley**
> 我不知道。
> 我想说不是。可要是我现在说得特别肯定，你会记下来吗？

**Zack Brennan**
> 我记你不记得。不把空白写成承认，也不写成证明。

**Emma O'Malley**
> 好。

**Zack Brennan**
> 我会带你出去。

**Emma O'Malley** [立刻看向他]
> Zack，别。

**Zack Brennan**
> 别什么？

**Emma O'Malley**
> 别先把结局答应下来，再去找能配上的东西。
> 要是真是我杀了他呢？

**Zack Brennan**
> 还没有证据能——

**Emma O'Malley**
> 我说要是。你查到的东西真的指向我，你怎么办？

【演出】Zack 看着她，原本想说的话停住。

**Zack Brennan**
> 拿出来。跟对我有利的东西一起。

**Emma O'Malley**
> 是对我有利。

**Zack Brennan** [低头片刻]
> 对。对你有利的也一样。

**Emma O'Malley**
> 我要知道发生了什么。不是听你告诉我，可以放心了。

**Zack Brennan**
> 我答应你。查到什么就说什么，不扣下。

【演出】Emma 的手松开一些，没有伸向他。Zack 起身，走到门边，又停住。

**Zack Brennan**
> 再想一件事。你失去意识前后，待着的地方，有没有人进出？

**Emma O'Malley** [闭了闭眼]
> 我听见……有个声音。
> 像刀刺进肉里。很模糊。

**Zack Brennan**
> 看见人了吗？

**Emma O'Malley**
> 没有。别让我给那声音安一张脸，我安不出来。

**Zack Brennan**
> 不用。先到这里。

【演出】Emma 侧过身，拿起客房里的应急疏散册。翻页时，一张旧卡片露了出来，她将它抽出，放正。

**Emma O'Malley**
> 疏散册里怎么夹着别处的东西……Miller 飞行机械馆。

**Zack Brennan** [留在门边]
> 旧消防维护卡？

**Emma O'Malley** [沿卡面看过去]
> 嗯。上面是屋顶排烟，下面这两个……单人校准舱，防火隔断。

【突发事件需求｜必须画面呈现】触发位置：Emma 将旧消防维护卡放正查看；画面必须让玩家看见：卡上三个独立位置呈正三角分布，上方为正向屋顶排烟图标且右侧有不对称卡扣，左下为单人校准舱，右下为带消防标志与“EXIT”的防火隔断；三处之间不画连接线，不添加任何拉杆编号或正确答案标记；承载的信息：Emma 看清位置、朝向与卡扣差异；接回对白的位置：Emma 查看图标右侧卡扣。卡片保留独立可读特写，原物不入背包。

**Emma O'Malley** [目光停在上方图标右侧]
> 这个卡扣只在右边。

【演出】Emma 看完，将卡片夹回疏散册，留在客房。

@observe environment:5251 observer:502
@set u5_fire_card_seen=true

**Zack Brennan**
> 我去查。你先歇一会儿。

**Emma O'Malley**
> 记着刚才答应的。

**Zack Brennan**
> 记着。

【演出】Zack 开门离去。Emma 留在房内，门外看守维持原状。

@next L2_opening_corridor_arrival

## Talk: L2_opening_corridor_arrival.json

【场景】礼堂入口走廊。Zack 停在礼堂门外，看一眼门内受损的闩，再望向舞台。

**Zack Brennan** [内心]
> 绕过镜子观察，从这扇门进来，办得到。
> 可门后来是从里面上闩的。

【演出】Zack 收回视线，走向调查区域。

@exploration

## Talk: L2_talk_corridor_stair_position.json

【场景】礼堂入口走廊。Pierce 看见 Zack 来，停下手里的事。

**Pierce**
> 镜子的记录已经改了。

**Zack Brennan**
> 这回问楼梯。你在圆桌上提过两个位置，我要把时间对清楚。

**Pierce**
> 九点十五，还是 B 位。等门撞开，已经在 A 位了。

**Zack Brennan**
> 九点十五那一次，是你最后看舞台？

**Pierce**
> 是。我最后看见它的时候，它就在 B。

**Zack Brennan**
> 破门以后在 A。

**Pierce** [看着他]
> 对。这次也记“他说的”，省得又说我把话当证据压你。

**Zack Brennan**
> 你的话会记。影像也会查。

@get testimony:5032001

**Pierce**
> 那就查。

@end

### 回访短开场（同一入口文字草案）

**Zack Brennan**
> 楼梯的时间，再核一次。

**Pierce**
> 还是那两次观察。

【回访续接】接本段正文关于“九点十五”的回答；同一证词不重复发放。

## Talk: L2_talk_corridor_stage_departure.json

【场景】礼堂入口走廊。Vivian 看向舞台，听见 Zack 走近才转头。

**Vivian**
> 现在要问舞台了？

**Zack Brennan**
> 你带的人，什么时候离开的？

**Vivian**
> 六点零五。该做的做完，我们就走了。

**Zack Brennan**
> 楼梯停在哪边？

**Vivian**
> A。离开的时候就在 A，此后也没人再动过。

**Zack Brennan**
> 这是你的说法？

**Vivian** [笑意很浅，没维持住]
> 不然呢，你替我说？
> 六点零五，我们离开时楼梯已经在 A，之后没有人再动过。你就照这个记。

@get testimony:5042001

**Zack Brennan**
> 好。

@if has_item:5203 -> vivian_hub
@else -> vivian_end

@label vivian_hub
@branch vivian_hub
@opt "离场时的楼梯，再核一遍。" -> vivian_stairs
@opt "批准联上的临时彩排，是你批的？" -> vivian_rehearsal
@opt "先到这里。" -> vivian_end

@path vivian_stairs

**Zack Brennan**
> 还是六点零五、A 位，此后没人动？

**Vivian**
> 对。问多少遍也是这句。

@goto vivian_hub

@path vivian_rehearsal

**Zack Brennan** [示意已取得的批准联]
> 这上面是你的签字？

**Vivian**
> 是。Emma 临时申请了彩排，我批的。

**Zack Brennan**
> 八点半到十点半，这段时间是你手写的。

**Vivian**
> 是。日期、她的名字，都在这儿。
> 她申请用舞台，我给她留出时间。批准的就是这件事。

**Zack Brennan**
> 我会照着核对。

**Vivian** [将目光从纸上移开]
> 那就照着来，别给我的签字多添几件事。

@goto vivian_hub

@path vivian_end

**Zack Brennan**
> 先问到这儿。

**Vivian**
> 好。

@end

### 回访短开场（同一入口文字草案）

**Vivian**
> 又有哪处要核？

**Zack Brennan**
> 还是舞台的事。

【回访续接】未持5203时，回离场原话并结束；持5203时直接回 vivian_hub。临时彩排话题始终要求先取得批准联，不重复发放5042001。

## Talk: L2_talk_stage_death_sequence.json

【场景】舞台正面。已取得回转轮下叠压血滴记录后开放本段。Foster 将导轨记录与伤情记录摆在一起。

**Eleanor Foster**
> 导轨那处血滴，我看过了。

**Zack Brennan**
> 现在能把空着的部分写上？

**Eleanor Foster**
> 可以。老 Charles 不只有刀伤，还有高处坠落造成的伤。

**Zack Brennan**
> 坠落要了他的命？

**Eleanor Foster**
> 没有。摔得很重，但没有立即死。
> 后来那一刀，才是直接致命伤。

**Zack Brennan** [看向两份记录]
> 先摔伤，后被刺。

**Eleanor Foster**
> 是。导轨上、回转轮下面这滴血，与尸旁刀创形成时的活体喷溅是连续的。
> 不是拿一滴来路不明的血替他排先后。

**Zack Brennan**
> 血源这一点，你能确认。

**Eleanor Foster**
> 能。坠落重伤，没有立即致死；随后刀刺致命。这就是我写完的顺序。

@get testimony:5052001

**Zack Brennan**
> 好。我拿这份去核楼梯。

**Eleanor Foster**
> 记清楚是哪滴血。别把不同位置的痕迹混着用。

@end

### 回访短开场（同一入口文字草案）

**Zack Brennan**
> 导轨血滴和伤序，我再核一下。

**Eleanor Foster**
> 记录在这里。

【回访续接】接正文“现在能把空着的部分写上？”；重复回查同一证词，不重复发放，不受L1手帕选择影响。

## 调查反馈：item:5201｜回转轮下的叠压血滴

【场景】舞台正面，旋转楼梯内导轨及回转轮下方。

【突发事件需求｜必须画面呈现】触发位置：检查内导轨；画面必须让玩家看见：一滴血的集中落点，被回转轮经过后叠压拖开的短痕，以及轮缘与导轨的接触关系；承载的信息：玩家能自己读取血滴与轮子的叠压顺序；接回对白的位置：Zack 留下记录。不要直接画先后箭头或重演操作者。

**Zack Brennan** [俯身查看，内心]
> 一滴落在这里，被轮子拖开了。
> 留下记录，给 Foster 看。

@get item:5201
@end

## 调查反馈：environment:5252｜A 位顶端布景板

【场景】楼梯保持 A 位封存。Zack 沿楼梯登到顶端，查看与装饰融为一体的木合地布景板，不推动板面。

**Zack Brennan** [视线沿板边移动，内心]
> 把手没有，普通锁孔也没有。
> 边上的灰断了这么一点……还有冷风。

【演出】Zack 停在板前看了一会儿，没有强行开启。

**Zack Brennan** [内心]
> 先记下来。

@observe environment:5252
@end

## 调查反馈：item:5202｜21:15 舞台预备全景底片

【场景】舞台背面，查看预备全景底片。

【突发事件需求｜必须画面呈现】触发位置：查看底片；画面必须让玩家看见：同一全景中的 B 位楼梯、21:15 舞台钟、控制箱旁可辨认的彩排批准联；承载的信息：停位与钟面时间，以及留待核对的纸件；接回对白的位置：Zack 记录钟面。底片不追加日期字幕、日历、报纸或现代时间戳。

**Zack Brennan** [内心]
> 钟面九点十五，楼梯在 B。
> 控制箱旁边还夹着一张纸。

@get item:5202
@end

## 调查反馈：item:5203｜Emma 的彩排申请批准联

【场景】舞台背面，控制箱旁取得批准联。取得后唯一续接公开事件链。

**Zack Brennan** [看着纸件，内心]
> Emma 的名字，Vivian 的签字。
> 手写时段，八点半到十点半。日期是今天。

@get item:5203
@next L2_event_approval_promise

## 调查反馈：item:5204｜22:10—22:15 破门照片组

【场景】舞台背面，取得开场拍摄的两张连续底片。此轮查看22:10全景，照片组作为同一原物整体保留。

**Zack Brennan** [内心]
> 十点十分、十点十五。那两张。

【演出】展开22:10全景：Emma 与 Zack、其他可见人物、C-3 正面的 Lawson 及 A 位楼梯。保持全景阅读。

**Zack Brennan** [内心]
> 我在 Emma 旁边。Lawson 在 C-3 正面。
> 楼梯已经在 A。

@get item:5204
@end

## 复查反馈：item:5102｜礼堂唯一正常入口勘验页

**Zack Brennan** [查看已有勘验页，内心]
> 正常进出只经过这条廊道和这扇门。发现时，门从里面上了闩。

@review item:5102
@end

## 复查反馈：environment:5154｜可旋转的镜子

**Zack Brennan** [查看原镜，内心]
> 镜子能让人盯错方向。可它说不了进门以后的事。

@review environment:5154
@end

## 复查反馈：environment:5155｜礼堂正门

**Zack Brennan** [内心]
> 门闩在里面。这一处还得解释。

@review environment:5155
@end

## 复查反馈：environment:5156｜衣帽间门

**Zack Brennan** [内心]
> 门脚那块浅色补漆。Pierce 在镜子里盯过的，是这里。

@review environment:5156
@end


---

# U5 L2｜公开批准联与 Vivian 指证｜主模型完整初稿

## Talk: L2_event_approval_promise.json

【场景】舞台背面。紧接取得批准联。Zack 仍站在控制箱旁，纸在手中。

**Zack Brennan** [内心]
> 她主动申请，也主动约了人。
> 这张纸拿出去，Pierce 会怎么说？

【念头演出｜固定播放，无可选按钮】短暂并置“先不公开批准联”与“带回圆桌”。Zack 的手把纸页往自己这边收了些，又停住。

**Emma O'Malley** [回忆声，仅重现本轮客房已说的话]
> 你查到的东西真的指向我，你怎么办？

【演出】Zack 展开纸页，把折起的边角抚平。

**Zack Brennan** [低声]
> 才答应过。

【演出】他拿着批准联离开。念头收起，不产生隐藏、丢弃或推迟公开的玩家选择。

@next L2_event_public_approval

## Talk: L2_event_public_approval.json

【场景】圆桌会议室。Zack 将批准联摊在桌面。Pierce、Vivian、Foster、Lawson、小 Charles 在场。Emma 仍在客房看守中。

**Lawson Vanderbilt**
> 这回带了什么来？

**Zack Brennan**
> Emma 的彩排申请批准联。今天的日期，Vivian 签字，准用时段是八点半到十点半。

**Vivian** [看一眼纸，点头]
> 是我批的。临时彩排。

**Pierce**
> 她自己申请的？

**Zack Brennan**
> 她自己申请的。
> 还有一件事。她醒来后告诉我，主动约过老 Charles，九点半，到舞台见面。

【演出】Pierce 的目光从批准联移到 Zack 脸上。

**Pierce**
> 先在晚宴上当众跟他冲突，再把他约到舞台。最后，人死了，她手里有刀。

**Zack Brennan**
> 申请和约见，是她承认的。最后那一刀，她不记得。

**Pierce**
> 你觉得“不记得”就能过去？

**Zack Brennan**
> 不能。所以东西在这里，没有拿走。

**Lawson Vanderbilt** [低头看着批准联]
> 你知道这对她有多糟吧？

**Zack Brennan**
> 知道。

**Lawson Vanderbilt**
> 还肯拿过来。

**Zack Brennan**
> 她让我查清，不是让我挑着查。

**Eleanor Foster**
> 申请时段和她说的约见时间，分别记。批准联只记载彩排申请。

**Zack Brennan**
> 会分开。

**Charles Miller Jr.** [看过纸面后，将它留在桌上]
> 既然拿到这里，就让大家核对。这件事也要和别的发现一起查。

**Vivian** [看向 Zack，语气缓下来一点]
> 那就接着查吧。

【演出】Zack 收妥已经公开供众人核对的批准联，继续调查。

@exploration

## Expose: L2_expose_vivian.json

【场景】舞台正面，既定疑点、调查与批准联公开完成后。楼梯保持 A 位，Vivian 与 Zack 相对，Foster 在场。材料只随对应正确提交展开。

**Vivian** [看一眼楼梯]
> 还要我说那句话？

**Zack Brennan**
> 你的离场说法，和后来见到的位置对不上。

**Vivian**
> Pierce 的话？他的镜子才出过事。你不能让他的眼睛错一回，又让我的人替他担一回。

**Zack Brennan**
> 那就核对你的。

### R1｜楼梯是否一直在 A

**Vivian**
> 我们六点零五离开的时候，楼梯已经在 A。此后没有人再动过。
> Pierce 说九点十五还在 B，那就是他看错了。

@lie testimony:5042001
@present item:5202
@on_wrong r1_wrong
@on_correct r1_success

@path r1_wrong

**Vivian**
> 这说明不了楼梯当时在哪边。

**Zack Brennan**
> 再核一件。

@retry R1

@path r1_success

【演出】展开21:15舞台预备全景底片，先看楼梯与钟面，不放大批准联日期。

**Zack Brennan**
> 这回不问 Pierce。看底片。

**Vivian** [视线停在画面里的楼梯上]
> 我看见了。

**Zack Brennan**
> 九点十五。楼梯在哪边？

**Vivian**
> ……B。

**Zack Brennan**
> 你说离开时在 A，此后没动过。

【演出】Vivian 将目光移到画面中的钟上，没有立刻接话。

**Vivian**
> 那得先弄清这是哪天的底片。
> 前一天同一时候也可以拍。你拿张旧片来，我怎么认今天的事？

### R2｜这是不是旧底片

**Vivian** [指着钟面]
> 钟面只能说明时间，不能说明日期。
> 这也可能是前一天的彩排旧片。

@lie testimony:5042901
@present item:5203
@on_wrong r2_wrong
@on_correct r2_success

@path r2_wrong

**Vivian**
> 你还是没说清楚，它是哪一天拍的。

**Zack Brennan**
> 日期要能核上。

@retry R2

@path r2_success

【演出】Zack 出示已公开的彩排批准联。将原纸件与刚才底片中控制箱旁的同一纸件并列；沿用同一版式、折痕和夹放方向，日期只由原纸特写清楚读出。

**Zack Brennan**
> 控制箱旁的这张纸。你的签字，Emma 的申请。

**Vivian**
> 我认这个签字。

**Zack Brennan**
> 今天批的。

**Vivian** [看着纸上的日期]
> 是今天。

**Zack Brennan**
> 它怎么进前一天的底片？

【演出】Vivian 的手从钟面的位置落下。

**Vivian**
> 好。九点十五，楼梯还在 B。后来有人转回 A，也不能就把人命算上。
> 舞台调整漏个记录，就一定是杀完人干的？也可能在挨刀之前就动完了。

### R3｜移动发生在刀创前还是后

**Vivian**
> 那次移动发生在刀创之前。是没登记的舞台调整，跟伤后处理现场无关。

@lie testimony:5042902
@present item:5201
@on_wrong r3_wrong
@on_correct r3_success

@path r3_wrong

**Vivian**
> 楼梯动过，和它什么时候动，是两件事。

**Zack Brennan**
> 我核对的是先后。

@retry R3

@path r3_success

【演出】展开回转轮下叠压血滴记录。轮缘接触路径与被拖开的血滴同框可读。

**Zack Brennan**
> 内导轨这一滴。

**Vivian** [俯身看]
> 你怎么知道它是哪来的？

**Eleanor Foster**
> 与尸旁刀创形成时的活体喷溅连续。我已经写进检验记录。

**Zack Brennan**
> 血落在导轨上，轮子从这里经过。
> 先有哪一个？

【演出】Vivian 的视线沿着被轮子拖开的短痕移动。她直起身，没再去碰材料。

**Vivian**
> 血先。

**Zack Brennan**
> 不是刀创以前。

**Vivian** [过了一会儿才开口]
> ……是挨刀以后，楼梯才动的。

@next L2_post_expose_concealment

## Talk: L2_post_expose_concealment.json

【场景】舞台正面，紧接指证。Vivian 看着眼前 A 位的楼梯，先前应答时的熟练停了下来。

**Vivian**
> 六点零五，我们走的时候，它在 B。
> 一直是 B，我们在那里做完正常锁闭就走了。我没把它从 A 转去 B，也没转回来。

**Zack Brennan**
> 破门后，你看见了 A。

**Vivian**
> 是。我知道不一样。

**Zack Brennan**
> 却说没人动过。

**Vivian** [看向 Zack]
> 你觉得只会问到我这里吗？舞台是我接的，出了事，蓝月亮跟着一起赔进去。
> 我的人靠它吃饭。我也一样。

**Zack Brennan**
> Emma 就可以替这个异常留在房里？

**Vivian** [嘴唇动了一下，停住]
> 我没说她该……

【演出】她没有把这句辩解说完。

**Vivian**
> 可我确实没说楼梯变过。你要记，就记这句。
> 后来是谁转的，我没看见。是在那一刀以后转的，我刚才才知道。

**Zack Brennan**
> 我得把你隐瞒的部分写清楚。

**Vivian**
> 那就写清楚。

### 关系选择｜如何划定隐瞒的边界

@choice vivian_boundary
@opt "她隐瞒了异常，不能据此认定她操作或共谋。" -> vivian_restraint
@opt "她替移动遮掩，就是参与了这场谋杀。" -> vivian_overreach

@path vivian_restraint

**Zack Brennan**
> 你知道楼梯变了，却把它说成没变。这个不能省。
> 但谁转的、谁杀的，我不会拿你的隐瞒填上去。

**Vivian** [看他片刻，呼吸缓下来一点]
> 我以为你会把后面两件也一起扣给我。

**Zack Brennan**
> 证据没到那里。

**Vivian**
> 好。查到哪儿，就说到哪儿。

@set u5_vivian_hint=true
@goto l2_end_common

@path vivian_overreach

**Zack Brennan**
> 你替那次移动遮掩，就是在替杀人遮掩。别把自己摘出去，你也是这场谋杀的一份。

**Vivian** [表情慢慢收住]
> 我承认没说真话，你就替我认了杀人？

**Zack Brennan**
> 你的话帮了那个人。

**Vivian**
> 帮了谁，你也还没查出来。现在倒先查出我跟他是一伙的了。
> 你爱怎么写，是你的事。别说这是我承认的。

@set u5_vivian_hint=false
@goto l2_end_common

@label l2_end_common

【演出】Zack 收起血滴记录，抬头望向 A 位楼梯顶端。Vivian 顺着他的视线看过去。

**Zack Brennan**
> 转回 A，楼梯顶端正对那块板。

**Vivian**
> 布景检修板。跟旁边的装饰做在一起的。

**Zack Brennan**
> 边上有断尘，也漏冷风。

**Vivian**
> 这就算门？

**Zack Brennan**
> 还不算。

【演出】Zack 的视线越过板面，看向舞台通高部分，没有开始测量。

**Zack Brennan**
> 先查公开的一楼、二楼。加在一起，能不能占满这栋建筑。

**Vivian**
> 你要量？

**Zack Brennan**
> 量完再说。

@loop_end 2 -> L3_opening_measurement_proposal
