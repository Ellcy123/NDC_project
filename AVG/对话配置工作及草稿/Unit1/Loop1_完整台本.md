# Unit1 Loop1 完整台本｜枪响之夜

> 正式命名空间：EPI01 / 1xxx。
> 台词、ID、跳转、脚本和参数以 Unity `Assets/table/Talk.json` 为准；动作与设计标注仅从迁移归档中的 EPI09 同 ID 内容补充。
> 本文件共 219 个运行时节点，11 个场景。
> Loop 目标：23:30 那声枪响，真来自Vivian手中的枪吗？

## Talk: emma_entrance_001

> 场景：蓝月亮酒吧大门口
> 节点数：17｜未配置独立入口；本文件链首：`101001001`

### 101001001 `branches`
**扎克·布伦南** / Zack Brennan [停在橡木重门前，扬手拍了拍，目光落在门正中那块黄铜观察孔盖上]
> - ❶ 晚上好。 / EN: Good evening. / → `101001054`
> - ❷ Webb 约了我。 / EN: Webb asked me to come. / → `101001055`
<!-- runtime: step=1; script=1:branches; isRight=true; waitTime=0; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_entrance_001.json -->

### 101001054
**扎克·布伦南** / Zack Brennan
> 晚上好。
> EN: Good evening...
→ 下一节点 `101001002`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 101001055
**扎克·布伦南** / Zack Brennan
> Webb 约了我。
> EN: Webb... set this up for me...
→ 下一节点 `101001002`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 101001002
**酒保** / Bartender [只有眼睛——从孔盖后面透出来，中性，没有表情，等着]
> 今晚有包厢吗，先生？
> EN: Got... a private room tonight, sir?...
→ 下一节点 `101001003`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/doorman; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_entrance_001.json -->

### 101001003
**扎克·布伦南** / Zack Brennan
> 我来找酒吧老板。他约了我今晚来谈点事。
> EN: I'm here to see the owner... He set this up for tonight...
→ 下一节点 `101001048`
<!-- runtime: step=3; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 101001048
**酒保** / Bartender
> 今晚有包厢吗，先生？
> EN: Got... a private room tonight, sir?...
→ 下一节点 `101001004`
<!-- runtime: step=35; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/doorman -->

### 101001004
**扎克·布伦南** / Zack Brennan
> 喂——我说，是你们老板Webb 约的我——
> EN: Hey—... come on, Webb invited me—
→ 下一节点 `101001005`
<!-- runtime: step=4; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_annoyed -->

### 101001005
**酒保** / Bartender [观察孔重新开了，语气一模一样]
> 今晚有包厢吗，先生。
> EN: Got... a private room tonight, sir...
→ 下一节点 `101001046`
<!-- runtime: step=5; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/doorman; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_entrance_001.json -->

### 101001046
**扎克·布伦南** / Zack Brennan [转身准备走]
> ……唉。
> EN: ...Ah, hell...
→ 下一节点 `101001047`
<!-- runtime: step=6; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_weary; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_entrance_001.json -->

### 101001047
**扎克·布伦南** / Zack Brennan
> 下次喊我来之前先和你的门卫说一声啊，Webb 先生。
> EN: Next time... tell your doorman before you summon me, Mr. Webb...
→ 下一节点 `101001006`
<!-- runtime: step=7; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_weary -->

### 101001006 `new_npc_in`
**艾玛·奥马利** / Emma O'Malley [从街角走来，步子不急，拦在他前面，手包已经开了一道口子，指尖摸着里头的东西]
> 等等！
> EN: Oh— wait! Wait a moment...
> 系统参数：WAIT! / → `1021`
→ 下一节点 `101001007`
<!-- runtime: step=8; script=13:new_npc_in; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_happy; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_entrance_001.json -->

### 101001007
**艾玛·奥马利** / Emma O'Malley
> 先别急着走！
> EN: Don't leave just yet... hold on...
→ 下一节点 `101001049`
<!-- runtime: step=9; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_happy; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_entrance_001.json -->

### 101001049
**酒保** / Bartender
> 请问今晚有包厢吗，小姐？
> EN: Got... a private room tonight, miss?...
→ 下一节点 `101001008`
<!-- runtime: step=95; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/doorman -->

### 101001008
**艾玛·奥马利** / Emma O'Malley
> 艾斯弗德的 King Oliver 派我们来的（King Oliver from Ashford sent us）。
> EN: King Oliver from Ashford... sent us...
→ 下一节点 `101001043`
<!-- runtime: step=10; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_smile -->

### 101001043
**酒保** / Bartender [语气突变，恭敬地为两人拉开门]
> 晚上好！两位请进！刚才多有怠慢，还请包涵。
> EN: Ah, good evening! Please... come in, both of you! Forgive my earlier rudeness...
→ 下一节点 `101001009`
<!-- runtime: step=11; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/doorman; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_entrance_001.json -->

### 101001009
**扎克·布伦南** / Zack Brennan [看着门开了，没动，把棒棒糖从左边移到右边]
> 你是谁？
> EN: Who... are you?...
→ 下一节点 `101001010`
<!-- runtime: step=12; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_suspicious; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_entrance_001.json -->

### 101001010 `change_scene`
**艾玛·奥马利** / Emma O'Malley [走进去，脚步没停，头也没回]
> 先进来再说。
> EN: We'll talk inside...
> 系统参数：→ `1029`
<!-- runtime: step=13; script=8:change_scene; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_entrance_001.json -->

## Talk: emma_lobby_001

> 场景：蓝月亮酒吧 1F 大堂
> 节点数：36｜未配置独立入口；本文件链首：`101001011`

### 101001011 `branches`
**扎克·布伦南** / Zack Brennan [跟进来，低音贝斯的震动从地板穿上来；他在大堂边缘停下，看了看她]
> - ❶ 刚才在门口，你为什么帮我？ / EN: Why did you help me at the door? / → `101001103`
> - ❷ 那个口令——哪儿来的？ / EN: That password--where did you get it? / → `101001204`
<!-- runtime: step=1; script=1:branches; isRight=true; waitTime=0; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001103
**艾玛·奥马利** / Emma O'Malley [站在大堂边缘，把手包挂正，没有立刻回答，像是在斟酌用哪个版本的答案]
> 你刚刚站在那扇门前，提到了一个我追了三个月的名字——Webb。
> EN: You just stood out there... and mentioned a name I've been chasing for three months — Webb...
→ 下一节点 `101001012`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001204
**艾玛·奥马利** / Emma O'Malley [把手包收紧了一点，略顿了一下]
> 我的线人三个月前给我的——和 Webb 这个名字一起。
> EN: My informant gave it to me three months ago... along with Webb's name...
→ 下一节点 `101001012`
<!-- runtime: step=3; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001012
**艾玛·奥马利** / Emma O'Malley [站在大堂边缘，扫了一圈宾客，目光最终落回他身上，理了理衣领准备正式开口]
> 重新认识一下，我是Emma O'Malley,职业是——
> EN: Let me start over... I'm Emma O'Malley, and my profession is—
→ 下一节点 `101001013`
<!-- runtime: step=4; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001013
**扎克·布伦南** / Zack Brennan [目光扫过她微敞的手包，还有袖口沾的一点墨迹，直接打断]
> 记者。带着速记本，一身还没散尽的油墨味。不太擅长喝酒……却待在酒吧里。
> EN: A reporter. Stenographer's pad... a smudge of ink still on your cuff. Not much of a drinker... and yet here you are at a bar...
→ 下一节点 `101001042`
<!-- runtime: step=5; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001042
**扎克·布伦南** / Zack Brennan [目光扫过她微敞的手包，还有袖口沾的一点墨迹，直接打断]
> 你是为了酒吧老板——Webb而来的。
> EN: You're here for the owner of this place... Webb...
→ 下一节点 `101001014`
<!-- runtime: step=6; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001014
**艾玛·奥马利** / Emma O'Malley
> 真讨厌你们这些私家侦探对细节极度敏锐的毛病，
> EN: God... I hate that habit you private eyes have -- picking up on every little detail...
→ 下一节点 `101001902`
<!-- runtime: step=7; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking -->

### 101001902
**艾玛·奥马利** / Emma O'Malley
> 在你们面前一点成就感都没有。
> EN: There's just no winning with you people...
→ 下一节点 `101001015`
<!-- runtime: step=7; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking -->

### 101001015 `branches`
**扎克·布伦南** / Zack Brennan [把棒棒糖从左边移到右边]
> - ❶ 彼此彼此。 / EN: Likewise. / → `101001101`
> - ❷ 你能追上三个月，和私家侦探比也不逞多让了。 / EN: You kept at it for three months. Not bad for someone who's not a private eye. / → `101001201`
<!-- runtime: step=8; script=1:branches; isRight=true; waitTime=0; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001101
**艾玛·奥马利** / Emma O'Malley [睨了他一眼，哼了一声]
> 说得倒轻巧。
> EN: Easy for you to say...
→ 下一节点 `101001016`
<!-- runtime: step=9; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001201
**艾玛·奥马利** / Emma O'Malley [微微一顿，嘴角动了一下，算是接受了这句话]
> 我只是喜欢自己探寻事实而已。
> EN: I just like uncovering the truth myself...
→ 下一节点 `101001016`
<!-- runtime: step=10; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001016
**艾玛·奥马利** / Emma O'Malley [不甘示弱地抱起手臂，语气里带着点得意，证明自己没落入下风]
> 作为记者，我可是做足了功课的——我知道你是谁，Brennan 先生。
> EN: As a reporter, I've done my homework... I know who you are, Mr. Brennan...
→ 下一节点 `101001017`
<!-- runtime: step=11; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001017
**艾玛·奥马利** / Emma O'Malley
> 你在邮局能见到的人，我可全都盘了一遍。
> EN: Everyone you've met at the post office... I've already gone through them all...
→ 下一节点 `101001903`
<!-- runtime: step=12; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking -->

### 101001903
**艾玛·奥马利** / Emma O'Malley
> 据我所知，你最近收到了一封来自他的委托信？
> EN: From what I hear... you recently received a commission letter from him?...
→ 下一节点 `101001018`
<!-- runtime: step=12; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking -->

### 101001018
**扎克·布伦南** / Zack Brennan [看了一眼那本子，了然——但没打算配合这个采访，目光移开]
> 只是一封挂号信。我还没见过他本人。你要是想捞点独家新闻，恐怕找错了人。
> EN: Just a registered letter... I haven't even met the man. If you're after an exclusive... you've come to the wrong guy...
→ 下一节点 `101001019`
<!-- runtime: step=13; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001019
**艾玛·奥马利** / Emma O'Malley [合上笔记本，不急着追，换了个角度]
> 这个酒吧——你知道里面是什么结构吗？
> EN: This bar... do you actually know the layout in there?...
→ 下一节点 `101001020`
<!-- runtime: step=14; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001020
**艾玛·奥马利** / Emma O'Malley
> 光靠你一个人，有的人问不到，有的门敲不开。
> EN: Alone... there are people you can't reach, doors that won't open for you...
→ 下一节点 `101001021`
<!-- runtime: step=15; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001021
**艾玛·奥马利** / Emma O'Malley [重新翻开本子，这次是认真地打开，笔也握好了]
> 让我报道一些真相，和好故事。
> EN: Let me report some truths... and some good stories...
→ 下一节点 `101001022`
<!-- runtime: step=16; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001022
**艾玛·奥马利** / Emma O'Malley
> 只要你能给我这个——这个酒吧里有更多需要我来帮忙协调的事，我很乐意。
> EN: As long as you can give me that... whatever in this bar needs coordinating, I'm glad to help...
→ 下一节点 `101001045`
<!-- runtime: step=17; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001045 `branches`
**扎克·布伦南** / Zack Brennan [停了一拍，目光从她笔记本上移开]
> - ❶ 说吧，你要什么条件？ / EN: Name your terms. / → `101001102`
> - ❷ 你为什么盯着 Webb 这条线？ / EN: Why are you following the Webb lead? / → `101001202`
<!-- runtime: step=18; script=1:branches; isRight=true; waitTime=0; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001102
**艾玛·奥马利** / Emma O'Malley [把笔在本子上点了一下，直接回应]
> 独家报道权。你发现了什么，第一个告诉我。
> EN: Exclusive rights... Whatever you find, I'm the first to know...
→ 下一节点 `101001023`
<!-- runtime: step=19; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001202
**艾玛·奥马利** / Emma O'Malley
> 三个月前，一个查账的稽查员跟我提到了 Webb——他说这男人手腕极硬，
> EN: Three months ago... a tax inspector mentioned Webb to me — said this man had an iron grip...
→ 下一节点 `101001904`
<!-- runtime: step=20; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking -->

### 101001904
**艾玛·奥马利** / Emma O'Malley
> 南区大半的地下生意都按他的规矩转。
> EN: Half the underground business in the South Side runs by his rules...
→ 下一节点 `101001203`
<!-- runtime: step=20; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking -->

### 101001203
**艾玛·奥马利** / Emma O'Malley
> 结果第二天，那个稽查员就连夜搬出了艾斯弗德。
> EN: The very next day... that inspector packed up and left Ashford overnight...
→ 下一节点 `101001205`
<!-- runtime: step=21; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking -->

### 101001205
**艾玛·奥马利** / Emma O'Malley
> 能用这种雷霆手段让人闭嘴，他绝不是个和善的酒吧老板。
> EN: Someone who can silence people with that kind of speed... he's no friendly barkeep...
→ 下一节点 `101001905`
<!-- runtime: step=22; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking -->

### 101001905
**艾玛·奥马利** / Emma O'Malley
> 我想，这地方一定有点什么好料。
> EN: I figured this place must be hiding something good...
→ 下一节点 `101001023`
<!-- runtime: step=22; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking -->

### 101001023
**扎克·布伦南** / Zack Brennan
> 好吧。委托信里写的是遗嘱嘱托——
> EN: Alright... The commission letter said it's an estate matter --
→ 下一节点 `101001906`
<!-- runtime: step=22; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 101001906
**扎克·布伦南** / Zack Brennan
> 他要我确保一个叫 Vivian 的姑娘，顺利继承他的遗产。
> EN: He wants me to make sure a girl named Vivian inherits his estate smoothly...
→ 下一节点 `101001024`
<!-- runtime: step=22; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 101001024
**扎克·布伦南** / Zack Brennan
> 我今晚来，是准备找到 Webb，把遗嘱委托的合同正式拿到手。
> EN: I came tonight to find Webb... and get the contract for that estate trust officially in hand...
→ 下一节点 `101001025`
<!-- runtime: step=23; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001025
**艾玛·奥马利** / Emma O'Malley
> ……遗嘱？这不可能。Webb 约莫五十岁，正是手腕最硬、野心最大的年纪。
> EN: ...An estate? That can't be right. Webb is around fifty... right at the peak of his power and ambition...
→ 下一节点 `101001056`
<!-- runtime: step=24; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_surprised -->

### 101001056
**艾玛·奥马利** / Emma O'Malley
> 一个大权在握的操盘手，怎么会突然安排后事？
> EN: A man with that kind of grip... suddenly arranging his affairs?...
→ 下一节点 `101001057`
<!-- runtime: step=24; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_surprised -->

### 101001057
**艾玛·奥马利** / Emma O'Malley
> 除非他——
> EN: Unless he--
→ 下一节点 `101001058`
<!-- runtime: step=24; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_surprised -->

### 101001058
**艾玛·奥马利** / Emma O'Malley
> ……除非他预感自己会被人谋杀。
> EN: ...Unless he... sensed that someone was going to murder him...
→ 下一节点 `101001059`
<!-- runtime: step=24; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_surprised -->

### 101001059 `comic`
**艾玛·奥马利** / Emma O'Malley
> 啊
> EN: ...Ah!...
> 系统参数：Art/Scene/Emergency/EPI01/opening/bang| |1026,215|2|-0.5 / → `2`
→ 下一节点 `101001026`
<!-- runtime: step=25; script=6:comic; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_surprised; bgm=Chapter1_03_BGM_GunShoot -->

### 101001026
**扎克·布伦南** / Zack Brennan [把棒棒糖从嘴里拿下来，放进外套口袋，脚步已经转向枪声传来的方向]
> 枪声是在哪边？
> EN: Where did the gunshot come from?...
→ 下一节点 `101001027`
<!-- runtime: step=25; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_surprised; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

### 101001027 `change_scene`
**艾玛·奥马利** / Emma O'Malley [跟上，声音微微颤了一下]
> 听上去像是……在 Webb 的会客室。
> EN: Sounds like... it came from Webb's parlor...
> 系统参数：→ `1007`
<!-- runtime: step=26; script=8:change_scene; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_surprised; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_lobby_001.json -->

## Talk: emma_parlor_001

> 场景：Webb 会客室
> 节点数：19｜未配置独立入口；本文件链首：`101001028`

### 101001028
**薇薇安·格雷** / Vivian Gray
> 呃……
> EN: ...hh...
→ 下一节点 `101001029`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead -->

### 101001029
**罗莎·马丁内斯** / Rosa Martinez
> 先生——是她！Vivian Gray！
> EN: Sir—... it's her! Vivian Gray!...
→ 下一节点 `101001050`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous -->

### 101001050
**艾玛·奥马利** / Emma O'Malley
> Vivian Gray?
> EN: Vivian Gray?...
→ 下一节点 `101001051`
<!-- runtime: step=25; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_surprised -->

### 101001051
**扎克·布伦南** / Zack Brennan
> 哦……恐怕，她就是Webb遗嘱里的那个继承人了。
> EN: Oh... I'm afraid... she's the heir from Webb's estate...
→ 下一节点 `101001052`
<!-- runtime: step=26; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_thoughtful -->

### 101001052
**罗莎·马丁内斯** / Rosa Martinez
> 她手里拿着枪——她一定是刚刚杀了 Webb 先生！
> EN: She had a gun in her hand— she must have just killed Mr. Webb!...
→ 下一节点 `101001030`
<!-- runtime: step=27; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous -->

### 101001030
**艾玛·奥马利** / Emma O'Malley
> 她手里有枪——但看枪口的样子，Brennan。
> EN: She has a gun in her hand—but look at the muzzle, Brennan...
→ 下一节点 `101001031`
<!-- runtime: step=3; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_thinking -->

### 101001031
**扎克·布伦南** / Zack Brennan
> 枪口看着很干净。
> EN: The barrel looks clean...
→ 下一节点 `101001032`
<!-- runtime: step=4; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_thoughtful -->

### 101001032 `new_npc_in`
**莫里森** / Harold Morrison [推门进来，目光先撞上 Zack 和 Emma，皱了下眉]
> 让一让。
> EN: Step aside...
> 系统参数：STEP ASIDE. / → `1041`
→ 下一节点 `101001044`
<!-- runtime: step=5; script=13:new_npc_in; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_parlor_001.json -->

### 101001044
**莫里森** / Harold Morrison
> 见鬼……Webb。哪个混蛋把你打成了这样？
> EN: Christ... Webb. What bastard did this to you?
→ 下一节点 `101001033`
<!-- runtime: step=6; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes -->

### 101001033
**莫里森** / Harold Morrison [停在门口，铅笔在记事本上停了一下，目光扫到 Zack 和 Emma——两个他不认识的人]
> 你们两个——是什么人？案发现场，闲杂人等得先出去。
> EN: You two— who are you? This is a crime scene... civilians need to clear out...
→ 下一节点 `101001034`
<!-- runtime: step=7; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_parlor_001.json -->

### 101001034
**扎克·布伦南** / Zack Brennan
> Zack Brennan。O'Malley小姐的记者助理。
> EN: Zack Brennan. Miss O'Malley's... reporting assistant...
→ 下一节点 `101001035`
<!-- runtime: step=8; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_smirk; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_parlor_001.json -->

### 101001035
**艾玛·奥马利** / Emma O'Malley
> 哈？
> EN: Huh?...
→ 下一节点 `101001036`
<!-- runtime: step=9; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_surprised; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_parlor_001.json -->

### 101001036
**莫里森** / Harold Morrison
> 助理？嗯？那么，那位记者小姐呢？是你吗？
> EN: Assistant? Huh?... So which one of you is the reporter? You?...
→ 下一节点 `101001037`
<!-- runtime: step=10; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_parlor_001.json -->

### 101001037
**艾玛·奥马利** / Emma O'Malley [往前走了半步，声音不高，但清楚]
> 呃……Emma O'Malley。记者。《艾斯弗德先驱报》，的记者。
> EN: Uh... Emma O'Malley. Reporter. The Ashford Herald...
→ 下一节点 `101001038`
<!-- runtime: step=11; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_parlor_001.json -->

### 101001038
**莫里森** / Harold Morrison [看了看那封信，又扫了 Emma 一眼，嘟了一下嘴，把铅笔重新夹在耳朵上]
> 《艾斯弗德先驱报》……行，采访权给你们。
> EN: The Ashford Herald... fine. You can have your interview...
→ 下一节点 `101001039`
<!-- runtime: step=12; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_parlor_001.json -->

### 101001039
**莫里森** / Harold Morrison
> 现场你们可以看，人你们可以问——但拿到你们要的东西就走。
> EN: You can look at the scene, you can ask your questions... But take what you came for and leave...
→ 下一节点 `101001040`
<!-- runtime: step=13; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_parlor_001.json -->

### 101001040 `unlock_map`
**莫里森** / Harold Morrison
> 这不是报社的茶水间。
> EN: This isn't your newspaper's lunch room...
> 系统参数：101 / → `101`
→ 下一节点 `101001041`
<!-- runtime: step=14; script=9:unlock_map; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\emma_parlor_001.json -->

### 101001041
**莫里森** / Harold Morrison
> Webb 先生，一枪毙命。
> EN: Mr. Webb-- one shot, dead on the spot...
→ 下一节点 `101001907`
<!-- runtime: step=15; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes -->

### 101001907 `change_scene`
**莫里森** / Harold Morrison
> 这姑娘——手里拿着枪，在场……哎，这案子不就结了吗？
> EN: This girl-- had the gun in her hand, right here at the scene... hah, case closed, isn't it?...
> 系统参数：→ `1003`
<!-- runtime: step=15; script=8:change_scene; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes -->

## Talk: morrison_001

> 场景：Webb 会客室
> 节点数：31｜正式入口：TalkInfo=`104001001`

### 104001001
**莫里森** / Harold Morrison [没有抬头，铅笔在记事本上停了一下，听见了脚步声]
> Brennan，助理先生。你看上去倒比我还专业哈。
> EN: Brennan, Mr. Assistant... you look more like a real detective than I do, hah...
→ 下一节点 `104001002`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sluggish; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001002
**扎克·布伦南** / Zack Brennan [把铅笔夹到耳朵上，终于抬了一下头]
> 见谅，为了保证报道的完整性……这边——我总得都问问。
> EN: My apologies, sir... for the sake of complete reporting... I do need to ask around...
→ 下一节点 `104001003`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001003 `branches`
**扎克·布伦南** / Zack Brennan [打开随身的笔记本]
> - ❶ 辖区是哪个？警徽号——我要在笔记里记一下。 / EN: Which precinct? Badge number--I need it for my notes. / → `104001101`
> - ❷ 能请您详细分析一下Webb先生的情况吗？ / EN: Could you give me a detailed assessment of Mr. Webb's condition? / → `104001201`
> - ❸ 没有其他问题了。 / EN: No more questions. / → `104001900`
<!-- runtime: step=3; script=1:branches; isRight=true; waitTime=0; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001101
**扎克·布伦南** / Zack Brennan [语气直白]
> 请问您的辖区是哪个？警徽号——我要在笔记里记一下。
> EN: Which precinct are you with? And your badge number... I need it for the notes...
→ 下一节点 `104001102`
<!-- runtime: step=4; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001102
**莫里森** / Harold Morrison
> 你问这个做什么？
> EN: What do you want that for?...
→ 下一节点 `104001103`
<!-- runtime: step=5; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_strained; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001103
**艾玛·奥马利** / Emma O'Malley
> 要是破了案子，《艾斯弗德先驱报》的读者们，
> EN: Well, if the case gets solved and Ashford Herald readers...
→ 下一节点 `104001901`
<!-- runtime: step=6; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_happy -->

### 104001901
**艾玛·奥马利** / Emma O'Malley
> 却都不知道您的名字，那可就糟糕了！
> EN: ...don't even know your name -- that would be a real shame!...
→ 下一节点 `104001104`
<!-- runtime: step=6; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_happy -->

### 104001104
**莫里森** / Harold Morrison
> 二十二分局，警察。Morrison——就这一个姓。
> EN: Precinct Twenty-Two, detective. Morrison... just the one name...
→ 下一节点 `104001902`
<!-- runtime: step=7; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sluggish -->

### 104001902
**莫里森** / Harold Morrison
> 这个案子在的这片区都归我管。
> EN: Everything in this district falls under me...
→ 下一节点 `104001105`
<!-- runtime: step=7; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sluggish -->

### 104001105
**扎克·布伦南** / Zack Brennan [走近半步]
> 你跟 Webb 认识？
> EN: So you knew Webb?...
→ 下一节点 `104001106`
<!-- runtime: step=8; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_thoughtful; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001106
**莫里森** / Harold Morrison [把本子合上，换了只手撑膝盖，语气不咸不淡]
> 认识，酒吧里的员工我也都认识。
> EN: I knew him. I know all the staff in the bar too...
→ 下一节点 `104001107`
<!-- runtime: step=9; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_resigned; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001107
**莫里森** / Harold Morrison
> ……可有什么区别吗？他现在死了，这只能就是个案子。
> EN: ...what difference does it make? He's dead now. It's just a case...
→ 下一节点 `104001108`
<!-- runtime: step=10; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_resigned; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001108
**莫里森** / Harold Morrison [站起来，膝盖响了一声，皱了下眉，像是在说一件很烦的小事]
> 我还欠他半个月的酒钱。……这帐大概是想结也结不了咯。
> EN: He still owed me half a month's bar tab... guess that debt's never getting settled now, huh...
→ 下一节点 `104001003`
<!-- runtime: step=11; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_resigned; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001201
**扎克·布伦南** / Zack Brennan
> 能请您详细分析一下Webb先生的情况吗？
> EN: Could you give me a detailed assessment of Mr. Webb's condition?
→ 下一节点 `104001202`
<!-- runtime: step=12; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_thoughtful -->

### 104001202
**莫里森** / Harold Morrison
> Webb死了，毋庸置疑，Brennan。
> EN: Webb is dead. No question about it, Brennan.
→ 下一节点 `104001906`
<!-- runtime: step=13; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes -->

### 104001203
**莫里森** / Harold Morrison
> 我本来该去打牌。现在得陪这具尸体耗到天亮——真他妈走运。
> EN: I was supposed to be at a card game. Now I am stuck with a corpse till dawn. Just my goddamn luck.
→ 下一节点 `104001204`
<!-- runtime: step=14; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_strained -->

### 104001204
**莫里森** / Harold Morrison
> 总之。我现在接案，Webb 死亡，
> EN: Anyway. I'm on the case now. Webb dead...
→ 下一节点 `104001903`
<!-- runtime: step=15; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_strained -->

### 104001903
**莫里森** / Harold Morrison
> 枪响时间 23:30，地点在会客室——就这些。
> EN: Gunshot at 23:30, location the parlor room... that's the lot...
→ 下一节点 `104001205`
<!-- runtime: step=15; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_strained -->

### 104001205
**扎克·布伦南** / Zack Brennan [往 Vivian 方向看了一眼]
> 你打算怎么处理这个案子？
> EN: How are you planning to handle this case?...
→ 下一节点 `104001206`
<!-- runtime: step=16; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_suspicious; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001206
**莫里森** / Harold Morrison
> Rosa 说的那番话……有人持枪，有人指认，够了。
> EN: What Rosa said... someone with a gun, an eyewitness. That's enough...
→ 下一节点 `104001904`
<!-- runtime: step=17; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sluggish -->

### 104001904
**莫里森** / Harold Morrison
> 准备先把 Gray小姐带走，就这样收了。
> EN: Taking Miss Gray in and wrapping this up...
→ 下一节点 `104001207`
<!-- runtime: step=17; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sluggish -->

### 104001207
**扎克·布伦南** / Zack Brennan [停了一秒]
> 就这两条？
> EN: Just those two things?...
→ 下一节点 `104001208`
<!-- runtime: step=18; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001208
**莫里森** / Harold Morrison
> 有人指认，有人手持凶器。
> EN: Eyewitness identification, suspect holding the weapon...
→ 下一节点 `104001905`
<!-- runtime: step=19; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp -->

### 104001905
**莫里森** / Harold Morrison
> Brennan，我现在要抓第一嫌疑人，不是陪你写他妈的论文。
> EN: Brennan, I am here to arrest the prime suspect, not help you write a goddamn thesis.
→ 下一节点 `104001401`
<!-- runtime: step=19; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp -->

### 104001401
**莫里森** / Harold Morrison [把本子重新掏出来，语气回到散漫的平静]
> 你们要看就看。拿到需要的东西了就离开这儿。
> EN: You can look around. Get what you need and then get out...
→ 下一节点 `104001402`
<!-- runtime: step=20; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001402
**扎克·布伦南** / Zack Brennan [把协议书收回内袋]
> 多少时间？
> EN: How much time?...
→ 下一节点 `104001403`
<!-- runtime: step=21; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001403
**莫里森** / Harold Morrison [头没抬，继续翻本子]
> 够你查的时间。
> EN: Enough for you to do your digging...
→ 下一节点 `104001404`
<!-- runtime: step=22; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001404
**莫里森** / Harold Morrison [翻到下一页，铅笔停在某一行上]
> 别踩那边，我还没做完记录。
> EN: Don't step over there. I'm not done with my notes...
→ 下一节点 `104001003`
<!-- runtime: step=23; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_001.json -->

### 104001900 `end`
**扎克·布伦南** / Zack Brennan
> 没有其他问题了。
> EN: No more questions...
<!-- runtime: step=900; script=2:end; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 104001906 `comic`
**莫里森** / Harold Morrison
> 看样子，他当时坐在右侧沙发上，来的还是个熟人——至少熟到让他连防备的动作都没有。
> EN: Looks like he was sitting on the sofa to the right. Whoever came in was someone he knew—well enough that he never even tried to defend himself.
> 系统参数：Art/Scene/Emergency/EPI01/SHOW/c01/001||188,159|0 / → `0`
→ 下一节点 `104001907`
<!-- runtime: step=3; script=6:comic; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes -->

### 104001907 `comic`
**莫里森** / Harold Morrison
> 一枪打进胸口，干净利落。人倒到地上，血从背后渗进了地毯。
> EN: One round to the chest. Clean and precise. He went down, and the blood soaked through his back into the carpet.
> 系统参数：Art/Scene/Emergency/EPI01/SHOW/c01/002|BANG!|280,576|2 / → `2`
→ 下一节点 `104001203`
<!-- runtime: step=4; script=6:comic; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes -->

## Talk: morrison_002

> 场景：Webb 会客室
> 节点数：24｜未配置独立入口；本文件链首：`104002001`

### 104002001
**扎克·布伦南** / Zack Brennan [从外套内袋取出 Webb 委托协议书（1103），把它放在 Morrison 面前的桌面上——不是递给他，是放在那里]
> 受某人所雇佣——我是他的遗产委托侦探。
> EN: Hired by a certain someone — I'm his estate trustee detective...
→ 下一节点 `104002002`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_002.json -->

### 104002002
**罗莎·马丁内斯** / Rosa Martinez [听到"侦探"两个字，手在围裙上攥了一下——动作不大，但比之前任何一次都快]
> 侦……侦探？
> EN: D-detective...?
→ 下一节点 `104002003`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_002.json -->

### 104002003
**莫里森** / Harold Morrison
> O'Malley小姐，这是什么意思？
> EN: Miss O'Malley, what is this supposed to mean...?
→ 下一节点 `104002004`
<!-- runtime: step=3; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_002.json -->

### 104002004
**艾玛·奥马利** / Emma O'Malley
> 先别急，您可以看看委托书的内容。
> EN: Take it easy, officer... why don't you have a look at what's in the document...
→ 下一节点 `104002005`
<!-- runtime: step=4; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_002.json -->

### 104002005
**莫里森** / Harold Morrison
> Webb 和 Brennan 的委托协议...
> EN: Webb and Brennan's commission agreement...
→ 下一节点 `104002901`
<!-- runtime: step=5; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_calm -->

### 104002901
**莫里森** / Harold Morrison
> Gray小姐...Webb的遗产继承权...
> EN: Miss Gray... Webb's estate... inheritance rights...
→ 下一节点 `104002006`
<!-- runtime: step=5; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_calm -->

### 104002006
**艾玛·奥马利** / Emma O'Malley
> Webb 委托Brennan先生执行他的遗嘱——继承人是 Gray小姐。
> EN: Webb commissioned Mr. Brennan to execute his will — the heir is Miss Gray...
→ 下一节点 `104002018`
<!-- runtime: step=6; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_calm -->

### 104002018
**艾玛·奥马利** / Emma O'Malley
> 而这是他生前和这位Zack Brennan签下的委托协议书。
> EN: And this is the commission agreement he signed with Mr. Brennan... while he was still alive...
→ 下一节点 `104002007`
<!-- runtime: step=65; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_calm -->

### 104002007
**扎克·布伦南** / Zack Brennan
> Morrison，你觉得Webb这个人，
> EN: Morrison... do you really think Webb...
→ 下一节点 `104002902`
<!-- runtime: step=7; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 104002902
**扎克·布伦南** / Zack Brennan
> 没有任何理由，会突然给自己安排后事吗？
> EN: ...with no reason at all, would suddenly arrange his own affairs?...
→ 下一节点 `104002008`
<!-- runtime: step=7; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 104002008
**莫里森** / Harold Morrison [慢慢抬起头，看了一眼协议书，又看了一眼 Zack，表情有些难看]
> ……你想说什么，Brennan？
> EN: ...What are you getting at, Brennan...?
→ 下一节点 `104002009`
<!-- runtime: step=8; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_strained; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_002.json -->

### 104002009
**扎克·布伦南** / Zack Brennan
> Gray 若被定罪谋杀 Webb，遗嘱即废——杀人者不得继承被害人的遗产。
> EN: If Gray is convicted of murdering Webb, the will is void — a killer cannot inherit from their victim...
→ 下一节点 `104002017`
<!-- runtime: step=9; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_002.json -->

### 104002017
**扎克·布伦南** / Zack Brennan
> 这一切发生得太顺理成章了，
> EN: This all happened far too neatly...
→ 下一节点 `104002903`
<!-- runtime: step=95; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 104002903
**扎克·布伦南** / Zack Brennan
> 简直像是有人刻意把这把枪和谋杀的罪名塞到了她手里。
> EN: ...almost as if someone deliberately placed that gun and the charge of murder into her hands...
→ 下一节点 `104002010`
<!-- runtime: step=95; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 104002010
**扎克·布伦南** / Zack Brennan
> 我是生前合法的遗嘱委托侦探，拥有将这件事彻查到底的法律权利。
> EN: I'm the legally appointed estate trustee detective... and I have the legal right to see this investigation through to the end...
→ 下一节点 `104002011`
<!-- runtime: step=10; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_002.json -->

### 104002011
**艾玛·奥马利** / Emma O'Malley
> Morrison先生，
> EN: Mr. Morrison...
→ 下一节点 `104002904`
<!-- runtime: step=11; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_calm -->

### 104002904
**艾玛·奥马利** / Emma O'Malley
> 您总不能在委托还没执行完之前，就把遗嘱继承人关进去。
> EN: Surely you can't, before the deceased's final commission has even been carried out... just lock up the heir...
→ 下一节点 `104002012`
<!-- runtime: step=11; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_calm -->

### 104002012
**莫里森** / Harold Morrison [把协议书放回桌面。叹了口气，语气里带着嫌麻烦的厌倦，既没有同情也没有威胁]
> ……七十二小时。如果你们找不出别的结论，我就按我看到的办。
> EN: ...Seventy-two hours. If you can't come up with anything else... I close it the way I see it...
→ 下一节点 `104002013`
<!-- runtime: step=12; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_002.json -->

### 104002013
**莫里森** / Harold Morrison
> 我现在要单独、仔细地问问在场的两个人。
> EN: I'm going to question the two people who were present -- separately, and thoroughly...
→ 下一节点 `104002905`
<!-- runtime: step=13; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp -->

### 104002905
**莫里森** / Harold Morrison
> 那个 Gray小姐，还有那个清洁工。
> EN: That Miss Gray... and the cleaner...
→ 下一节点 `104002014`
<!-- runtime: step=13; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp -->

### 104002014
**莫里森** / Harold Morrison
> 你先去问你该问的——酒吧里还有其他员工。
> EN: You go ask around -- there are other staff in the bar...
→ 下一节点 `104002906`
<!-- runtime: step=14; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp -->

### 104002906
**莫里森** / Harold Morrison
> 等我这边谈完了，再和你聊现场的事。
> EN: Once I'm done talking here... we can discuss the scene...
→ 下一节点 `104002015`
<!-- runtime: step=14; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp -->

### 104002015
**艾玛·奥马利** / Emma O'Malley [侧身对 Zack，声音低，轻]
> 走吧。我们还有时间。
> EN: Let's go... we still have time...
→ 下一节点 `104002016`
<!-- runtime: step=15; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/emma_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_002.json -->

### 104002016 `loop_end`
**扎克·布伦南** / Zack Brennan [对 Morrison 点了一下头，不带任何表情，然后转身走向门口]
> 好。
> EN: Right.
<!-- runtime: step=16; script=15:loop_end; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\morrison_002.json -->

## Talk: rosa_001

> 场景：Webb 会客室
> 节点数：30｜正式入口：TalkInfo=`103001001`

### 103001001
**罗莎·马丁内斯** / Rosa Martinez
> 哦——对不起先生！我...我是 Rosa，Rosa Martinez。
> EN: Oh... I'm sorry, sir! I... I'm Rosa, Rosa Martinez...
→ 下一节点 `103001901`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous -->

### 103001901
**罗莎·马丁内斯** / Rosa Martinez
> 就是...就是做清洁的。
> EN: I'm just... just the cleaning lady...
→ 下一节点 `103001002`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous -->

### 103001002
**扎克·布伦南** / Zack Brennan [没动，打量着她]
> 你在这里做什么。
> EN: What are you doing here...
→ 下一节点 `103001003`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001003
**罗莎·马丁内斯** / Rosa Martinez
> 我...月底了，Webb 先生要求彻底清洁。
> EN: I... end of the month, Mr. Webb wanted a thorough cleaning...
→ 下一节点 `103001902`
<!-- runtime: step=3; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous -->

### 103001902
**罗莎·马丁内斯** / Rosa Martinez
> 我一直在走廊那边打扫...然后...然后听到了枪声。
> EN: I was in the hallway the whole time... scrubbing... then... then I heard the gunshot...
→ 下一节点 `103001004`
<!-- runtime: step=3; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous -->

### 103001004
**罗莎·马丁内斯** / Rosa Martinez [语气有些急切，像是必须先把这件事说清楚才能往下走]
> 走廊尽头，就在这边，靠近会客室这一侧。
> EN: At the end of the hallway, right here... on this side, near the parlor...
→ 下一节点 `103001005`
<!-- runtime: step=4; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001005
**罗莎·马丁内斯** / Rosa Martinez
> 所以我在场，先生。
> EN: So I was there, sir!...
→ 下一节点 `103001903`
<!-- runtime: step=5; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous -->

### 103001903
**罗莎·马丁内斯** / Rosa Martinez
> 我有资格说——我是……我是……女巫（Witches）!
> EN: I have the right to say -- I am a... a witch... Witch!...
→ 下一节点 `103001006`
<!-- runtime: step=5; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous -->

### 103001006
**扎克·布伦南** / Zack Brennan
> 那是目击者（Witness）。
> EN: That's witness...
→ 下一节点 `103001007`
<!-- runtime: step=6; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 103001007
**罗莎·马丁内斯** / Rosa Martinez
> ...哦，哦，目击者（Witness）。
> EN: ...oh, oh, witness. Witness...
→ 下一节点 `103001008`
<!-- runtime: step=7; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_evasive -->

### 103001008 `branches`
**扎克·布伦南** / Zack Brennan [看着她，没有放下这件事的意思]
> 你说她杀了人。
> EN: You said she killed him...
> - ❶ 你亲眼看见她开枪了？ / EN: Did you actually see her fire the gun? / → `103001101`
> - ❷ 23:30 那一声——你在哪儿听到的？ / EN: That shot at 23:30--where did you hear it? / → `103001201`
> - ❸ 没有其他问题了。 / EN: No more questions. / → `103001900`
<!-- runtime: step=8; script=1:branches; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_suspicious; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001101
**扎克·布伦南** / Zack Brennan [语气平，但字字清楚]
> 你说 Gray 杀了 Webb。你亲眼看见她开枪了？
> EN: You said Gray killed Webb. Did you actually see her fire the gun?...
→ 下一节点 `103001102`
<!-- runtime: step=9; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_suspicious; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001102
**罗莎·马丁内斯** / Rosa Martinez
> 我...我是说...她手里有枪。那把枪。
> EN: I... I'm saying... she had the gun. That gun...
→ 下一节点 `103001904`
<!-- runtime: step=10; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_evasive -->

### 103001904
**罗莎·马丁内斯** / Rosa Martinez
> Webb 先生就死在那里。然后...
> EN: Mr. Webb... he died right there. And then...
→ 下一节点 `103001103`
<!-- runtime: step=10; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous -->

### 103001103
**罗莎·马丁内斯** / Rosa Martinez [抬起头，视线落在 Vivian 手里那把枪上，没有落在 Zack 脸上——眼珠快速动了一下]
> 谁手里拿着枪，就是谁做的，先生。这...这是明摆着的事。
> EN: Whoever is holding the gun... that's who did it, sir. It's... it's obvious...
→ 下一节点 `103001104`
<!-- runtime: step=11; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_evasive; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001104
**罗莎·马丁内斯** / Rosa Martinez [声音里有一点颤，说出这句话时语速比前一句快了半拍]
> 她此刻手里正拿着那把枪。她一定是刚刚杀了 Webb 先生。
> EN: She is holding that gun right now. She must have just killed Mr. Webb...
→ 下一节点 `103001105`
<!-- runtime: step=12; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_evasive; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001105
**扎克·布伦南** / Zack Brennan [听完，目光在 Rosa 脸上停了一秒]
> 你没有回答我的问题。
> EN: You didn't answer my question...
→ 下一节点 `103001106`
<!-- runtime: step=13; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001106
**罗莎·马丁内斯** / Rosa Martinez [把头低下去，盯着拖把的底端，声音缩小了]
> 先生...我只知道我看到的。
> EN: Sir... I only know what I saw...
→ 下一节点 `103001008`
<!-- runtime: step=14; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_evasive; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001201
**扎克·布伦南** / Zack Brennan [声调没变，换了个角度]
> 那声枪响。23:30——你在哪里？
> EN: That gunshot. 23:30... where were you?...
→ 下一节点 `103001202`
<!-- runtime: step=15; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_thoughtful; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001202
**罗莎·马丁内斯** / Rosa Martinez [一顿，不确定地看了 Zack 一眼，又低下头]
> 走廊那头...我一直在走廊那头，先生。打扫。就是...就是那一声。
> EN: Down the hallway... I was at the far end of the hallway, sir. Cleaning. It was just... just that one shot...
→ 下一节点 `103001203`
<!-- runtime: step=16; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001203
**扎克·布伦南** / Zack Brennan [不紧不慢]
> 那一声之前呢？还有别的动静吗？
> EN: Before that shot... any other sounds? Anything at all?...
→ 下一节点 `103001204`
<!-- runtime: step=17; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_suspicious; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001204
**罗莎·马丁内斯** / Rosa Martinez
> 有……枪响以后，我还听见玻璃碎掉的声音。除此以外，没有别的动静。
> EN: Yes... After the gunshot, I heard glass shatter. Other than that, there was nothing else.
→ 下一节点 `103001905`
<!-- runtime: step=18; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103001905
**罗莎·马丁内斯** / Rosa Martinez
> 那之前会客室那边都是安静的...就...就只有那一声，先生。
> EN: Before that it was all quiet near the parlor... just... just that one shot, sir...
→ 下一节点 `103001205`
<!-- runtime: step=18; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103001205
**罗莎·马丁内斯** / Rosa Martinez [没抬头，把手背在身后，手指在指甲缝里掐着什么]
> 而且...那个时候。里面只有她，就只有 Gray小姐在里面。
> EN: And... at that moment... only she was in there. Only Miss Gray was inside...
→ 下一节点 `103001206`
<!-- runtime: step=19; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001206
**罗莎·马丁内斯** / Rosa Martinez [语速稳下来，像是在背一段话——句子有点太整齐]
> 所以...所以只能是她。
> EN: So... so it can only be her...
→ 下一节点 `103001207`
<!-- runtime: step=20; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001207
**扎克·布伦南** / Zack Brennan [看着她]
> 你说话听起来，像是事先想好了要说这几句。
> EN: The way you're talking... it sounds like you had all that prepared beforehand...
→ 下一节点 `103001208`
<!-- runtime: step=21; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_suspicious; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001208
**罗莎·马丁内斯** / Rosa Martinez [快速抬起头，眼睛里有一瞬间的什么——然后又低回去]
> 我...我就是说了我知道的事，先生。
> EN: I... I just told you what I know, sir...
→ 下一节点 `103001401`
<!-- runtime: step=22; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_evasive; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001401
**扎克·布伦南** / Zack Brennan [没有开口，只是看她一秒]
> 就这些了？
> EN: That's everything?...
→ 下一节点 `103001402`
<!-- runtime: step=23; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001402
**罗莎·马丁内斯** / Rosa Martinez [重复否定，声音比之前更低，但没有动摇]
> 就这些。我看见的，就这些，先生。
> EN: That's everything. What I saw... that's everything, sir...
→ 下一节点 `103001008`
<!-- runtime: step=24; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\rosa_001.json -->

### 103001900 `end`
**扎克·布伦南** / Zack Brennan
> 没有其他问题了。
> EN: No more questions...
<!-- runtime: step=900; script=2:end; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

## Talk: vivian_001

> 场景：Webb 会客室
> 节点数：20｜正式入口：TalkInfo=`106001001`

### 106001001
**扎克·布伦南** / Zack Brennan [走到 Vivian 身旁，声音不高]
> 刚才听到了你的名字——你是 Vivian Gray吗？
> EN: I just heard your name... you're Vivian Gray?...
→ 下一节点 `106001002`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001002
**薇薇安·格雷** / Vivian Gray [嘴唇动了，但什么也没出来]
> 唔……
> EN: Mm...
→ 下一节点 `106001003`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001003
**扎克·布伦南** / Zack Brennan [轻声]
> 你好，我是 Zack Brennan。Webb 雇的侦探。
> EN: Hello. I'm Zack Brennan. A detective hired by Webb...
→ 下一节点 `106001004`
<!-- runtime: step=3; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001004
**薇薇安·格雷** / Vivian Gray ["Webb"这个词像是钩到了什么——她的眼神动了一下]
> ……Webb？
> EN: ...Webb?...
→ 下一节点 `106001005`
<!-- runtime: step=4; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001005
**扎克·布伦南** / Zack Brennan [语气平]
> 他委托我来处理一件遗产的事。
> EN: He hired me to handle an estate matter...
→ 下一节点 `106001006`
<!-- runtime: step=5; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001006
**薇薇安·格雷** / Vivian Gray [嘴唇收了一下，像是有什么话要出来，又被什么堵住]
> 可……他……
> EN: But... he...
→ 下一节点 `106001007`
<!-- runtime: step=6; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001007
**薇薇安·格雷** / Vivian Gray [视线飘向地板，声音轻而茫然]
> 他倒在地板上……
> EN: He's lying on the floor...
→ 下一节点 `106001008`
<!-- runtime: step=7; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001008 `branches`
**扎克·布伦南** / Zack Brennan [声音压低，只够两个人听见]
> - ❶ 你有没有开过这把枪？ / EN: Did you fire this gun? / → `106001101`
> - ❷ 这把枪——是你的吗？ / EN: This gun--is it yours? / → `106001301`
> - ❸ 没有其他问题了。 / EN: No more questions. / → `106001900`
<!-- runtime: step=8; script=1:branches; isRight=true; waitTime=0; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001101
**扎克·布伦南** / Zack Brennan [平静，不是审问，是在确认]
> 你有没有开过这把枪？
> EN: Did you fire this gun?...
→ 下一节点 `106001102`
<!-- runtime: step=9; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_thoughtful; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001102
**薇薇安·格雷** / Vivian Gray [抬头，眼神对着他的方向——但像是在看他后面的某样东西]
> 我……我不……
> EN: I... I don't...
→ 下一节点 `106001103`
<!-- runtime: step=10; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001103
**薇薇安·格雷** / Vivian Gray [摇了一下头，像是在摇走脑子里的什么]
> ……不知道。
> EN: ...I don't know...
→ 下一节点 `106001104`
<!-- runtime: step=11; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001104
**扎克·布伦南** / Zack Brennan [停了一拍——她说"不知道"，不是"没有"，也不是"有"。]
> 好。
> EN: Alright...
→ 下一节点 `106001008`
<!-- runtime: step=12; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001301
**扎克·布伦南** / Zack Brennan [目光落在枪上，声音平]
> 这把枪——是你的吗？
> EN: This gun... is it yours?...
→ 下一节点 `106001302`
<!-- runtime: step=17; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001302
**薇薇安·格雷** / Vivian Gray [低头看了枪一眼，停了一拍]
> 是……
> EN: Yes...
→ 下一节点 `106001303`
<!-- runtime: step=18; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001303
**扎克·布伦南** / Zack Brennan [跟上一句]
> 你在这里是做什么的？
> EN: What do you do here?...
→ 下一节点 `106001304`
<!-- runtime: step=19; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001304
**薇薇安·格雷** / Vivian Gray [声音出来，轻而慢，像在确认自己还站在这里]
> 蓝月亮的……歌女。
> EN: Blue Moon's... singer...
→ 下一节点 `106001400`
<!-- runtime: step=20; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001400
**扎克·布伦南** / Zack Brennan [声音平，是确认不是追问]
> 你是这里的歌女？
> EN: You're the singer here?...
→ 下一节点 `106001401`
<!-- runtime: step=22; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001401
**薇薇安·格雷** / Vivian Gray [停顿了一拍，缓慢点了一下头]
> ……嗯。
> EN: ...Mm...
→ 下一节点 `106001403`
<!-- runtime: step=23; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001403
**扎克·布伦南** / Zack Brennan [往 Morrison 那边看了一下，声音不高]
> 她没法回答。先这样。
> EN: She can't answer. Let's leave it here for now...
→ 下一节点 `106001008`
<!-- runtime: step=25; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_weary; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Talk\loop1\vivian_001.json -->

### 106001900 `end`
**扎克·布伦南** / Zack Brennan
> 没有其他问题了。
> EN: No more questions...
<!-- runtime: step=900; script=2:end; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_weary -->

## Expose: Loop1_rosa

> 节点数：28｜正式入口：ExposeData=`103901001`；ExposeData=`103901005`

### 103901001
**扎克·布伦南** / Zack Brennan [从嘴里取出棒棒糖，慢慢走向 Rosa，声音不高，每个字都很清晰]
> Rosa。你刚才说——Gray 手里拿着手枪，她一定是刚刚杀了 Webb。
> EN: Rosa. You just said — Gray was holding a pistol, that she must have just killed Webb...
> 指证可用材料：`1031001`「看见Vivian持枪」、`1711`「无硝烟的手枪」
→ 下一节点 `103901002`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_suspicious; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Expose\Loop1_rosa.json -->

### 103901002
**罗莎·马丁内斯** / Rosa Martinez
> 是...是的，先生。她就拿着那把枪，
> EN: Y-yes, sir! She was holding that gun...
→ 下一节点 `103901901`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103901901
**罗莎·马丁内斯** / Rosa Martinez
> Webb先生又刚刚死了——这还不够明显吗？
> EN: ...and Mr. Webb just died -- isn't that obvious enough?!...
→ 下一节点 `103901003`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103901003
**扎克·布伦南** / Zack Brennan
> 先别急着下定论。如果你真的看清了，就再把刚才的话重复一遍。
> EN: Don't be in such a hurry to draw conclusions. If you really did see it clearly, say it again...
→ 下一节点 `103901004`
<!-- runtime: step=3; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_thoughtful -->

### 103901004
**罗莎·马丁内斯** / Rosa Martinez
> 我说多少遍都是一样的！
> EN: No matter how many times you ask, it's the same!...
→ 下一节点 `103901902`
<!-- runtime: step=4; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103901902 `expose`
**罗莎·马丁内斯** / Rosa Martinez
> 她此刻手里正拿着一把手枪，她一定是刚刚开枪杀了 Webb 先生。
> EN: She's holding a pistol right now -- she must have just shot and killed Mr. Webb!...
→ 下一节点 `103901005`
<!-- runtime: step=4; script=7:expose; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103901005
**扎克·布伦南** / Zack Brennan
> 可她的枪管里没有硝烟残留，没有黑化痕迹……至少刚刚没有被击发过。
> EN: But there's no gunpowder residue in the barrel, no fouling marks... this gun hasn't been fired recently...
> 指证可用材料：`1031002`「Gray独自在会客室」
→ 下一节点 `103901006`
<!-- runtime: step=5; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_cold -->

### 103901006
**莫里森** / Harold Morrison
> 嘿！你从哪里拿到这把枪的！
> EN: Hey! Where did you get that gun?!...
→ 下一节点 `103901007`
<!-- runtime: step=6; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Expose\Loop1_rosa.json -->

### 103901007
**扎克·布伦南** / Zack Brennan
> Morrison, Rosa 说“刚刚杀了”。可这把枪，和那句话，对不上。
> EN: Morrison. Rosa said 'just killed.' But this gun... and those words... don't add up...
→ 下一节点 `103901008`
<!-- runtime: step=7; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_cold -->

### 103901008
**莫里森** / Harold Morrison
> 这是非法搜证……没有经过局子里正式的弹道检验！我不认同！
> EN: This is illegal evidence collection... no proper ballistic test from the precinct! I won't accept this...!
→ 下一节点 `103901009`
<!-- runtime: step=8; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Expose\Loop1_rosa.json -->

### 103901009
**扎克·布伦南** / Zack Brennan
> 你难道看不出来吗？
> EN: You really can't see it...?
→ 下一节点 `103901010`
<!-- runtime: step=9; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_suspicious; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Expose\Loop1_rosa.json -->

### 103901010
**莫里森** / Harold Morrison [走近两步，低头看了一眼那把枪，摘了摘帽子，重新压回去，语气里带着一点犹豫]
> ……确实没有硝烟反应，Rosa? 你确定你真的看到了吗？
> EN: ...There really is no powder residue. Rosa? You sure... you actually saw it...?
→ 下一节点 `103901011`
<!-- runtime: step=10; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_strained; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Expose\Loop1_rosa.json -->

### 103901011
**罗莎·马丁内斯** / Rosa Martinez [身体先僵了一秒——手在空中悬着，没有继续搓。然后手动起来了，比刚才更快，口音略重了一点]
> 那...那硝烟是可以消散的！或者她用的是...是别的...
> EN: B-but... the gunpowder can dissipate! Or maybe she used... used something... else...
→ 下一节点 `103901012`
<!-- runtime: step=11; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Expose\Loop1_rosa.json -->

### 103901012
**扎克·布伦南** / Zack Brennan
> 这里可没有别的手枪。
> EN: There's no other pistol here...
→ 下一节点 `103901013`
<!-- runtime: step=12; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_cold; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Expose\Loop1_rosa.json -->

### 103901013
**莫里森** / Harold Morrison
> 那得我搜完才能下定论。
> EN: I'll only know for sure once I've finished searching...
→ 下一节点 `103901014`
<!-- runtime: step=13; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Expose\Loop1_rosa.json -->

### 103901014
**罗莎·马丁内斯** / Rosa Martinez
> Morrison先生！相信我！
> EN: Mr. Morrison! Believe me!
→ 下一节点 `103901030`
<!-- runtime: step=14; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_losingit -->

### 103901030
**扎克·布伦南** / Zack Brennan
> 相信你？可Gray刚刚并没有开枪，你怎么能证明一定是她杀的？
> EN: Believe you? But Gray didn't fire that gun just now — so how can you prove it was her...?
→ 下一节点 `103901015`
<!-- runtime: step=14; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_cold -->

### 103901015
**罗莎·马丁内斯** / Rosa Martinez
> 枪声刚响起来的时候，我就来门口了。
> EN: When the shot rang out, I came straight to the door...
→ 下一节点 `103901031`
<!-- runtime: step=15; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103901031
**罗莎·马丁内斯** / Rosa Martinez
> 那时候Webb 先生身边只有 Gray小姐，没有别人……
> EN: At that moment, only Miss Gray was beside Mr. Webb... nobody else...
→ 下一节点 `103901017`
<!-- runtime: step=15; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103901016
**罗莎·马丁内斯** / Rosa Martinez
> 就算她不是用这把枪，也一定...一定是她杀的！
> EN: Even if she didn't use that gun — it still... it must have been her...!
→ 下一节点 `103901018`
<!-- runtime: step=16; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Expose\Loop1_rosa.json -->

### 103901017
**罗莎·马丁内斯** / Rosa Martinez
> 而且，23:30，大家都听到了，只有那一声枪声。
> EN: And — 23:30, everyone heard it. There was only that one gunshot...
→ 下一节点 `103901016`
<!-- runtime: step=17; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103901018
**罗莎·马丁内斯** / Rosa Martinez
> 大家都可以作证的……是吧？Morrison先生？
> EN: Everyone can attest to it... right...? Mr. Morrison...?
→ 下一节点 `103901019`
<!-- runtime: step=18; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103901019
**莫里森** / Harold Morrison [点头，语气恢复笃定]
> 今晚我一直在吧台那边。23:30，枪声只响了那一次。
> EN: I was over at the bar all night. 23:30, the shot rang out just that once...
→ 下一节点 `103901020`
<!-- runtime: step=19; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp; actionSource=旧文档\Unit1_EPI命名迁移前_20260810\AVG\EPI09_9xxx作者版\Expose\Loop1_rosa.json -->

### 103901020
**莫里森** / Harold Morrison
> 你和O'Malley小姐上来的时候，
> EN: When you and Miss O'Malley came upstairs...
→ 下一节点 `103901903`
<!-- runtime: step=20; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp -->

### 103901903
**莫里森** / Harold Morrison
> 这房间里也只有Gray小姐拿着枪吧？
> EN: ...only Miss Gray was in this room holding the gun... correct?...
→ 下一节点 `103901021`
<!-- runtime: step=20; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_sharp -->

### 103901021
**罗莎·马丁内斯** / Rosa Martinez
> 23:30 一定是Webb死亡的枪响。
> EN: The shot at 23:30 must have been the one that killed Mr. Webb...
→ 下一节点 `103901904`
<!-- runtime: step=21; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103901904 `finalexpose`
**罗莎·马丁内斯** / Rosa Martinez
> 我亲耳听到，那会儿只有Gray小姐在里面。
> EN: I heard it with my own ears -- only Miss Gray was inside at that moment...
→ 下一节点 `103901022`
<!-- runtime: step=21; script=11:finalexpose; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_resolute -->

### 103901022 `exhibit`
**扎克·布伦南** / Zack Brennan
> Morrison，Rosa，我想先请两位看看这个。
> EN: Morrison. Rosa. I'd like you both to take a look at this...
> 系统参数：0 / → `1103`
> 系统参数：80 / → `1`
> 系统参数：READ
THIS.
→ 下一节点 `104002001`
<!-- runtime: step=22; script=5:exhibit; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm; bgm=Gen_BGM_Testify_Step4_confuse -->

## Repeat Talk: rosa_001_repeat

> 场景：Webb 会客室
> 节点数：5｜正式入口：LoopTalkInfo=`103801001`

### 103801001
**罗莎·马丁内斯** / Rosa Martinez
> 您...您又回来了？先生，我刚才真的把知道的都说了。
> EN: You... you're back again? Sir, I really told you everything I know before...
→ 下一节点 `103801002`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_nervous -->

### 103801002
**扎克·布伦南** / Zack Brennan
> 我只再确认几处。你慢慢说。
> EN: I just need to double-check a few things... take your time.
→ 下一节点 `103801003`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 103801003 `branches`
**罗莎·马丁内斯** / Rosa Martinez
> 好...好吧。请您小声一点。
> EN: O... okay... please keep your voice down, sir...
> - ❶ 你亲眼看见她开枪了？ / EN: Did you actually see her fire the gun? / → `103001101`
> - ❷ 23:30 那一声——你在哪儿听到的？ / EN: That shot at 23:30--where did you hear it? / → `103001201`
> - ❸ 没有其他问题了 / EN: No more questions. / → `103801010`
<!-- runtime: step=3; script=1:branches; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_evasive -->

### 103801010
**扎克·布伦南** / Zack Brennan
> 暂时没有了。留在这里，别离开现场。
> EN: That's all for now... Stay here. Don't leave the scene.
→ 下一节点 `103801011`
<!-- runtime: step=10; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 103801011 `end`
**罗莎·马丁内斯** / Rosa Martinez
> 我不会走的...我只是个做清洁的，先生。
> EN: I won't go anywhere... I'm just the cleaner, sir...
<!-- runtime: step=11; script=2:end; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/rosa_evasive -->

## Repeat Talk: morrison_001_repeat

> 场景：Webb 会客室
> 节点数：5｜正式入口：LoopTalkInfo=`104801001`

### 104801001
**莫里森** / Harold Morrison
> 又是你，Brennan。你写报道还是查案？别把我的现场问出脚印来。
> EN: You again, Brennan... Are you writing a report or running an investigation? Don't leave footprints all over my crime scene.
→ 下一节点 `104801002`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_calm -->

### 104801002
**扎克·布伦南** / Zack Brennan
> 我只补几项记录。
> EN: Just filling in a few gaps in my notes...
→ 下一节点 `104801003`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 104801003 `branches`
**莫里森** / Harold Morrison
> 快点，趁我还愿意装得有耐心。
> EN: Make it quick... while I can still pretend to be patient.
> - ❶ 辖区是哪个？警徽号——我要在笔记里记一下。 / EN: Which precinct? Badge number--I need it for my notes. / → `104001101`
> - ❷ 能请您详细分析一下Webb先生的情况吗？ / EN: Could you give me a detailed assessment of Mr. Webb's condition? / → `104001201`
> - ❸ 没有其他问题了 / EN: No more questions. / → `104801010`
<!-- runtime: step=3; script=1:branches; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_strained -->

### 104801010
**扎克·布伦南** / Zack Brennan
> 暂时没有。
> EN: Nothing else for now.
→ 下一节点 `104801011`
<!-- runtime: step=10; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->

### 104801011 `end`
**莫里森** / Harold Morrison
> 好。那就别挡我记死亡时间。
> EN: Good... Now stop blocking me while I log the time of death.
<!-- runtime: step=11; script=2:end; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/morrison_resigned -->

## Repeat Talk: vivian_001_repeat

> 场景：Webb 会客室
> 节点数：4｜正式入口：LoopTalkInfo=`106801001`

### 106801001
**薇薇安·格雷** / Vivian Gray
> ……你还在这里。Webb……他还躺在那儿吗？
> EN: ...You're still here... Is Webb... still lying over there?
→ 下一节点 `106801002`
<!-- runtime: step=1; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead -->

### 106801002
**扎克·布伦南** / Zack Brennan
> 我只想确认几句话。你不用急着回答。
> EN: I just want to confirm a few things... No rush, take your time.
→ 下一节点 `106801003`
<!-- runtime: step=2; script=0:none; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_thoughtful -->

### 106801003 `branches`
**薇薇安·格雷** / Vivian Gray
> 问吧……如果我还听得见。
> EN: Ask away... if I can still hear you...
> - ❶ 你有没有开过这把枪？ / EN: Did you fire this gun? / → `106001101`
> - ❷ 这把枪——是你的吗？ / EN: This gun--is it yours? / → `106001301`
> - ❸ 没有其他问题了。 / EN: No more questions. / → `106801900`
<!-- runtime: step=3; script=1:branches; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/vivian_drunk_down_forehead -->

### 106801900 `end`
**扎克·布伦南** / Zack Brennan
> 没有其他问题了。
> EN: No more questions.
<!-- runtime: step=900; script=2:end; isRight=true; waitTime=0; staticImagePath=Art/avg_clip/EPI01/static/zack_calm -->
