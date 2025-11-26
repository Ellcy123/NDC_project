# -*- coding: utf-8 -*-
"""
批量创建对话YAML文件的脚本 - 第二部分
使用UTF-8编码确保中文正确保存
"""

import codecs
import os

base_path = r'd:\NDC_project\可视化工具\数据源\Unit1\dialogs'

# ============== Loop 5 Opening ==============
loop5_opening = '''# NDC Episode 1 - 循环5 开篇对话
# 场景：Vivian化妆室

dialog_id: loop5_opening
loop: 5
type: opening

sections:
  vivian_dressing_room:
    scene: SC1011
    scene_name: Vivian化妆室
    duration: 约40秒
    description: 发现Vivian的秘密，引出她的悲惨过去

    lines:
      - speaker: narration
        text: "[Zack进入Vivian的化妆室，发现她不在]"

      - speaker: NPC101
        emotion: observing
        text: "化妆室...她应该快回来了。"

      - speaker: narration
        text: "[Zack开始搜索化妆室]"

      - speaker: NPC101
        action: 发现一封信
        emotion: curious
        text: "这是...Webb给她的信？"

      - speaker: narration
        text: "[Zack打开信件阅读]"

      - speaker: NPC101
        emotion: analytical
        text: "虚假的承诺...Webb承诺帮她赎身，却从未兑现。"

      - speaker: narration
        text: "[门打开，Vivian走进来]"

      - speaker: NPC106
        emotion: shocked
        text: "你在做什么？！"

      - speaker: NPC101
        emotion: calm
        text: "Vivian小姐。我们需要谈谈。"

      - speaker: NPC106
        emotion: angry
        text: "你在翻我的东西！出去！"

      - speaker: NPC101
        action: 举起信件
        emotion: cold
        text: "Webb承诺帮你离开这里。他兑现了吗？"

      - speaker: NPC106
        action: 停住
        emotion: shocked
        text: "你...你怎么..."

      - speaker: NPC101
        emotion: analytical
        text: "他没有。所以你恨他。"

      - speaker: NPC106
        emotion: defensive
        text: "我没有恨他！我只是..."

      - speaker: NPC101
        emotion: questioning
        text: "只是什么？"

      - speaker: NPC106
        action: 沉默片刻
        emotion: bitter
        text: "你不会懂的。"

evidence_obtained:
  - id: EV1513
    name: Webb给Vivian的虚假承诺信件
    description: Webb承诺帮Vivian赎身离开，但从未兑现
'''

with codecs.open(os.path.join(base_path, 'loop5', 'opening.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop5_opening)

print('Loop 5 opening.yaml written successfully')

# ============== Loop 5 Accusation ==============
loop5_accusation = '''# NDC Episode 1 - 循环5 指证对话
# 场景：酒吧后台走廊
# 目标：揭露Vivian的动机和她在案发当晚的行踪

dialog_id: loop5_accusation
loop: 5
type: accusation

expose_info:
  scene: SC1013
  scene_name: 酒吧后台走廊
  target: NPC106
  target_name: Vivian Rose
  total_rounds: 4
  duration: 约100秒
  design_concept: 拆解Vivian的四层防御，揭露她的悲惨遭遇和真实行踪

opening:
  lines:
    - speaker: NPC101
      emotion: cold
      text: "Vivian，我们需要谈谈Webb。"

    - speaker: NPC106
      emotion: hostile
      text: "我已经说过了，我不知道什么。"

    - speaker: NPC101
      emotion: calm
      text: "你知道的比任何人都多。"

    - speaker: NPC106
      emotion: defensive
      text: "Brennan先生，Webb的死跟我没关系。"

rounds:
  - round: 1
    name: 仇恨动机谎言
    lie:
      content: "Webb对我很好...我对他没有任何恨意..."
      source: Vivian掩饰仇恨
    required_evidences: [EV1513]
    evidence_names: [Webb给Vivian的虚假承诺信件]

    dialog:
      - speaker: NPC101
        emotion: questioning
        text: "Webb对你怎么样？"

      - speaker: NPC106
        emotion: cold
        text: "Webb对我很好...我对他没有任何恨意..."

      - speaker: NPC101
        action: 拿出信件
        emotion: sharp
        text: "这封信说了什么？"

      - speaker: NPC106
        action: 脸色变了
        emotion: shocked
        text: "你...你从哪里...？"

      - speaker: NPC101
        emotion: cold
        text: "Webb承诺帮你赎身。承诺给你自由。他做到了吗？"

      - speaker: NPC106
        emotion: bitter
        text: "他...他说需要时间..."

      - speaker: NPC101
        emotion: sharp
        text: "三年了，Vivian。三年的承诺，三年的等待。他从来没打算让你走。"

      - speaker: NPC106
        action: 眼眶泛红
        emotion: angry
        text: "你不懂！你什么都不懂！"

      - speaker: NPC101
        emotion: cold
        text: "我懂。Webb利用你的希望控制你。每次你想离开，他就拿出这封信，告诉你'再等等'。"

      - speaker: NPC106
        emotion: breaking
        text: "是...是的...他从来没打算让我走...他只是...只是在利用我..."

    result: Vivian被迫承认对Webb的仇恨

  - round: 2
    name: 案发时间谎言
    lie:
      content: "那天晚上我一直在化妆室...没有离开过..."
      source: Vivian伪造不在场证明
    required_evidences: [EV1514]
    evidence_names: [化妆室香水时间证据]

    dialog:
      - speaker: NPC101
        emotion: questioning
        text: "案发当晚，你在哪里？"

      - speaker: NPC106
        emotion: defensive
        text: "我一直在化妆室...没有离开过..."

      - speaker: NPC101
        emotion: sharp
        text: "你的香水。很独特的味道。"

      - speaker: NPC106
        emotion: confused
        text: "香水？这...这有什么关系？"

      - speaker: NPC101
        emotion: cold
        text: "Webb的门把手上有你的香水味。11点05分，有人用钥匙开过Webb的门。"

      - speaker: NPC106
        emotion: panicked
        text: "那...那不是我！"

      - speaker: NPC101
        emotion: accusatory
        text: "Vivian，你有Webb办公室的钥匙。你去过那里。"

      - speaker: NPC106
        action: 沉默
        emotion: cornered
        text: "..."

      - speaker: NPC101
        emotion: pressing
        text: "你去做什么？"

      - speaker: NPC106
        emotion: defensive
        text: "我...我只是去看看他..."

    result: Vivian被迫承认去过Webb办公室

  - round: 3
    name: 杀人动机谎言
    lie:
      content: "我只是去找他谈...我没有伤害他..."
      source: Vivian否认杀人
    required_evidences: [EV1515, EV1551]
    evidence_names: [Vivian的情绪记录, Tommy证词Webb和Rita的争吵]

    dialog:
      - speaker: NPC101
        emotion: questioning
        text: "去看看他？带着你对他三年的恨？"

      - speaker: NPC106
        emotion: defensive
        text: "我只是去找他谈...我没有伤害他..."

      - speaker: NPC101
        emotion: sharp
        text: "Tommy说Webb那天晚上和Rita吵过架。你知道吗？"

      - speaker: NPC106
        action: 眼神闪烁
        emotion: surprised
        text: "Rita？那个...那个新来的？"

      - speaker: NPC101
        emotion: cold
        text: "Webb答应过帮她赎身。就像答应你一样。"

      - speaker: NPC106
        emotion: shocked
        text: "什么？！"

      - speaker: NPC101
        emotion: accusatory
        text: "你发现了，是不是？Webb用同样的手段骗了很多女孩。你不是唯一一个。"

      - speaker: NPC106
        action: 崩溃
        emotion: furious
        text: "他...他怎么能...三年...我等了三年..."

      - speaker: NPC101
        emotion: cold
        text: "所以你去找他对质。"

      - speaker: NPC106
        emotion: breaking
        text: "是...我去了...我...我想问他...为什么..."

    result: Vivian情绪崩溃，但否认杀人

  - round: 4
    name: 真相还原
    lie:
      content: "我去的时候...他已经..."
      source: Vivian揭露真相
    required_evidences: []
    evidence_names: []

    dialog:
      - speaker: NPC101
        emotion: questioning
        text: "然后呢？"

      - speaker: NPC106
        action: 眼泪流下
        emotion: anguished
        text: "我去的时候...他已经..."

      - speaker: NPC101
        emotion: alert
        text: "已经什么？"

      - speaker: NPC106
        emotion: traumatized
        text: "他...他已经死了...血...到处都是血..."

      - speaker: NPC101
        emotion: sharp
        text: "你看到凶手了吗？"

      - speaker: NPC106
        action: 摇头
        emotion: terrified
        text: "没有...我敲门...有人说'进来'...是Webb的声音...但是当我进去..."

      - speaker: NPC101
        emotion: cold
        text: "有人模仿Webb的声音。"

      - speaker: NPC106
        emotion: scared
        text: "我...我不知道...我太害怕了...我马上就跑了..."

      - speaker: NPC101
        emotion: questioning
        text: "你为什么不报警？"

      - speaker: NPC106
        emotion: bitter
        text: "报警？然后告诉他们我深夜用钥匙进入死者房间？Brennan先生，我是什么身份你很清楚。没有人会相信我。"

    result: Vivian揭露真相——她到达时Webb已死

truth_reveal:
  lines:
    - speaker: NPC101
      emotion: analytical
      text: "所以你11点05分进入办公室，Webb已经死了。有人模仿他的声音骗你进去。"

    - speaker: NPC106
      emotion: nodding
      text: "是的...我发誓我没有杀他...我恨他...但我没有杀他..."

    - speaker: NPC101
      emotion: questioning
      text: "那个声音。你确定是男的？"

    - speaker: NPC106
      action: 回忆
      emotion: uncertain
      text: "是...听起来像Webb...但现在想想...有点不一样...更...更年轻一点..."

    - speaker: NPC101
      emotion: sharp
      text: "年轻。"

    - speaker: NPC106
      emotion: realizing
      text: "等等...Jimmy...Jimmy有时候会模仿Webb说话...开玩笑的时候..."

    - speaker: NPC101
      emotion: cold
      text: "Jimmy会模仿Webb的声音。"

    - speaker: NPC106
      emotion: shocked
      text: "你...你是说...Jimmy？不...他不可能...他那么老实..."

    - speaker: NPC101
      emotion: grim
      text: "老实的人不会模仿老板的声音骗人进入犯罪现场。"

truth_summary:
  vivian_motive: 被Webb欺骗三年，有强烈的仇恨动机
  vivian_alibi: 11点05分到达时Webb已死，发现尸体后逃离
  key_revelation: 有人模仿Webb声音，可能是Jimmy
  next_target: 最终指证Jimmy，揭露真凶
'''

with codecs.open(os.path.join(base_path, 'loop5', 'accusation.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop5_accusation)

print('Loop 5 accusation.yaml written successfully')

# ============== Loop 6 Opening ==============
loop6_opening = '''# NDC Episode 1 - 循环6 开篇对话
# 场景：Webb书房 + Jimmy家

dialog_id: loop6_opening
loop: 6
type: opening

sections:
  final_investigation:
    scene: SC1010
    scene_name: Webb书房
    duration: 约50秒
    description: 发现最后的关键证据

    lines:
      - speaker: narration
        text: "[Zack和Emma进入Webb的书房，这是最后一次搜查机会]"

      - speaker: NPC102
        emotion: urgent
        text: "时间不多了。我们还剩不到12小时。"

      - speaker: NPC101
        emotion: determined
        text: "Webb的书房。他把最重要的东西都藏在这里。"

      - speaker: NPC102
        emotion: searching
        text: "我来翻这边的文件柜。"

      - speaker: NPC101
        action: 检查书架
        emotion: focused
        text: "他的私人日记提到了时间记录...如果他真的那么谨慎..."

      - speaker: narration
        text: "[Zack发现一个隐藏的夹层]"

      - speaker: NPC101
        emotion: discovering
        text: "找到了。"

      - speaker: NPC102
        action: 走过来
        emotion: curious
        text: "是什么？"

      - speaker: NPC101
        action: 拿出一份文件
        emotion: grim
        text: "Webb的手写记录。11点到11点30分之间的访客记录..."

      - speaker: NPC102
        emotion: shocked
        text: "11点？那正是..."

      - speaker: NPC101
        emotion: cold
        text: "凶手动手的时间。Webb记录了一切。"

      - speaker: NPC102
        emotion: reading
        text: "'11:00 - J来访'...J？Jimmy？"

      - speaker: NPC101
        emotion: analytical
        text: "继续看。"

      - speaker: NPC102
        emotion: shocked
        text: "'11:05 - V敲门，J代为回应'...'11:10 - J离开，带走了...'后面被撕掉了。"

      - speaker: NPC101
        emotion: grim
        text: "Jimmy。11点来访，11点05分模仿Webb的声音骗走Vivian，11点10分离开。"

      - speaker: NPC102
        emotion: horrified
        text: "所以凶手真的是...Jimmy？那个看起来最老实的人？"

      - speaker: NPC101
        emotion: cold
        text: "老实人才最危险。走，我们去找他。"

evidence_obtained:
  - id: EV1621
    name: Webb的手写时间记录
    description: 记录了11点到11点30分的访客，证明Jimmy在场
'''

with codecs.open(os.path.join(base_path, 'loop6', 'opening.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop6_opening)

print('Loop 6 opening.yaml written successfully')

# ============== Loop 6 Accusation ==============
loop6_accusation = '''# NDC Episode 1 - 循环6 指证对话
# 场景：Jimmy的家
# 目标：揭露Jimmy是真凶

dialog_id: loop6_accusation
loop: 6
type: accusation

expose_info:
  scene: SC1014
  scene_name: Jimmy的家
  target: NPC107
  target_name: Jimmy
  total_rounds: 5
  duration: 约150秒
  design_concept: 最终指证，揭露悲剧性的真凶

opening:
  lines:
    - speaker: narration
      text: "[Zack和Emma来到Jimmy家门前]"

    - speaker: NPC101
      action: 敲门
      emotion: determined
      text: "Jimmy，开门。"

    - speaker: NPC107
      action: 开门，脸色苍白
      emotion: fearful
      text: "Brennan先生...您...您怎么来了..."

    - speaker: NPC101
      emotion: cold
      text: "我们需要谈谈。关于Webb。关于11月3日晚上11点。"

    - speaker: NPC107
      action: 退后一步
      emotion: panicked
      text: "我...我不知道您在说什么..."

    - speaker: NPC101
      action: 走进屋内
      emotion: grim
      text: "你知道。所有人都知道了，Jimmy。"

rounds:
  - round: 1
    name: 不在场证明谎言
    lie:
      content: "那天晚上11点到12点我一直在厨房工作，从来没有离开过。"
      source: Jimmy伪造不在场证明
    required_evidences: [EV1621]
    evidence_names: [Webb的手写时间记录]

    dialog:
      - speaker: NPC101
        emotion: questioning
        text: "11月3日晚上11点，你在哪里？"

      - speaker: NPC107
        emotion: defensive
        text: "我...我在厨房工作...一直在厨房...从来没有离开过..."

      - speaker: NPC101
        action: 拿出文件
        emotion: cold
        text: "Webb的手写记录。'11:00 - J来访'。J是谁，Jimmy？"

      - speaker: NPC107
        emotion: shocked
        text: "这...这不是我..."

      - speaker: NPC101
        emotion: sharp
        text: "这个酒吧里，名字以J开头的只有你。"

      - speaker: NPC107
        emotion: panicked
        text: "也许...也许是别人...也许Webb写错了..."

      - speaker: NPC101
        emotion: cold
        text: "Webb从来不会写错。你比我更清楚这一点。"

      - speaker: NPC107
        action: 沉默
        emotion: cornered
        text: "..."

    result: Jimmy无法解释Webb的记录

  - round: 2
    name: 模仿声音谎言
    lie:
      content: "我不会模仿任何人的声音...我只是个厨师..."
      source: Jimmy否认模仿
    required_evidences: [EV1631, EV1351]
    evidence_names: [Vivian的证词, Rosa证词]

    dialog:
      - speaker: NPC101
        emotion: questioning
        text: "11点05分，Vivian敲门。有人用Webb的声音让她进去。"

      - speaker: NPC107
        emotion: defensive
        text: "我不会模仿任何人的声音...我只是个厨师..."

      - speaker: NPC101
        emotion: sharp
        text: "Vivian说那个声音听起来像Webb，但更年轻一点。她还说你有时候会模仿Webb开玩笑。"

      - speaker: NPC107
        emotion: desperate
        text: "那只是...只是开玩笑..."

      - speaker: NPC101
        emotion: accusatory
        text: "Rosa也说过，11点左右她听到有人在走廊用Webb的声音说话。但Webb那时候已经死了。"

      - speaker: NPC107
        action: 脸色更白
        emotion: breaking
        text: "我...我..."

      - speaker: NPC101
        emotion: cold
        text: "你模仿Webb的声音，骗Vivian进去，然后离开。你想让她成为替罪羊。"

      - speaker: NPC107
        emotion: anguished
        text: "不！我没有想让她背锅！我只是...我只是不想被发现..."

    result: Jimmy承认模仿了Webb的声音

  - round: 3
    name: 动机谎言
    lie:
      content: "我没有理由杀Webb...他对我很好..."
      source: Jimmy掩盖真实动机
    required_evidences: [EV1414]
    evidence_names: [厨房的送餐订单]

    dialog:
      - speaker: NPC101
        emotion: questioning
        text: "你为什么杀Webb？"

      - speaker: NPC107
        emotion: defensive
        text: "我没有理由杀Webb...他对我很好..."

      - speaker: NPC101
        action: 拿出送餐订单
        emotion: sharp
        text: "厨房的送餐订单。11点到11点30分——空白。你说你一直在厨房，但你根本没有工作。"

      - speaker: NPC107
        emotion: panicked
        text: "那是...那是因为没有订单..."

      - speaker: NPC101
        emotion: cold
        text: "11点之前和之后都有你的送餐记录。只有这30分钟是空白的。刚好是Webb被杀的时间。"

      - speaker: NPC107
        action: 颤抖
        emotion: breaking
        text: "我...我..."

      - speaker: NPC101
        emotion: sharp
        text: "Jimmy，别再撒谎了。"

    result: Jimmy的不在场证明彻底崩溃

  - round: 4
    name: Whale关联谎言
    lie:
      content: "我不认识什么Whale..."
      source: Jimmy否认与Whale的关系
    required_evidences: [EV1442, EV1651]
    evidence_names: [Rosa证词Jimmy用钥匙进入会客室, Vivian证词模仿声音]

    dialog:
      - speaker: NPC101
        emotion: cold
        text: "'Whale'。你认识他。"

      - speaker: NPC107
        emotion: defensive
        text: "我不认识什么Whale..."

      - speaker: NPC101
        emotion: sharp
        text: "Rosa说她看到你用钥匙进入Webb的会客室。那是Webb藏勒索证据的地方。"

      - speaker: NPC107
        emotion: shocked
        text: "Rosa...她..."

      - speaker: NPC101
        emotion: accusatory
        text: "你帮Webb管理勒索生意，你知道所有的秘密。包括'Whale'是谁。"

      - speaker: NPC107
        action: 沉默良久
        emotion: defeated
        text: "...是的...我知道..."

      - speaker: NPC101
        emotion: pressing
        text: "'Whale'给了你多少钱？"

      - speaker: NPC107
        emotion: ashamed
        text: "五千美元...他说...他说只要我帮他除掉Webb...他就给我身份...合法的身份..."

    result: Jimmy承认与Whale的交易

  - round: 5
    name: 最终真相
    lie:
      content: "我真的没有别的选择..."
      source: Jimmy的最终辩解
    required_evidences: [EV1424, EV1312]
    evidence_names: [虎头额外收入记录, Webb焦虑状态记录]

    dialog:
      - speaker: NPC101
        emotion: questioning
        text: "告诉我那天晚上发生了什么。"

      - speaker: NPC107
        action: 眼眶湿润
        emotion: broken
        text: "11点...我去找Webb...他...他答应帮我办身份...但他一直拖延...三年了...他就是在利用我..."

      - speaker: NPC101
        emotion: listening
        text: "然后？"

      - speaker: NPC107
        emotion: anguished
        text: "'Whale'找到我...他说他可以给我想要的一切...身份...钱...只要我...只要我..."

      - speaker: NPC101
        emotion: cold
        text: "只要你杀了Webb。"

      - speaker: NPC107
        action: 点头，泪流满面
        emotion: devastated
        text: "是...我...我用Webb给我的钥匙进去...我...我求他再给我一次机会...但他笑了...他说我永远只是个非法移民...永远只能给他打工..."

      - speaker: NPC101
        emotion: quiet
        text: "所以你动手了。"

      - speaker: NPC107
        emotion: sobbing
        text: "我...我不知道自己在做什么...等我反应过来...他已经...已经..."

    result: Jimmy完全崩溃，承认杀人

truth_reveal:
  lines:
    - speaker: NPC107
      action: 跪在地上
      emotion: broken
      text: "我只是想要一个身份...我只是想让Anna和孩子过上正常的生活...我不是坏人...我只是..."

    - speaker: NPC101
      emotion: cold
      text: "你杀了一个人，Jimmy。不管理由是什么。"

    - speaker: NPC107
      emotion: anguished
      text: "我知道...我知道...但是...Brennan先生...如果是你...如果是你的家人...你会怎么做？"

    - speaker: NPC101
      action: 沉默
      emotion: conflicted
      text: "..."

    - speaker: NPC107
      emotion: pleading
      text: "我只是想保护我的家人...Anna什么都不知道...求你...不要让她知道..."

    - speaker: NPC108
      action: 从里屋走出
      emotion: shocked
      text: "Jimmy...这是真的吗？"

    - speaker: NPC107
      action: 看到Anna，崩溃
      emotion: devastated
      text: "Anna...我...我..."

    - speaker: NPC108
      action: 眼泪流下
      emotion: heartbroken
      text: "你...你杀了人？"

    - speaker: NPC107
      emotion: desperate
      text: "我是为了我们...为了孩子...我只是想..."

    - speaker: NPC108
      action: 后退
      emotion: horrified
      text: "不...不...这不是我认识的Jimmy..."

truth_summary:
  killer: NPC107  # Jimmy
  motive: "'Whale'收买，用钱和合法身份交换Webb的命"
  method: 利用Vivian的钥匙进入 + 模仿声音骗走Vivian + 杀害Webb + 布置现场
  timeline:
    - time: "11:00"
      event: Jimmy进入Webb办公室杀害Webb
    - time: "11:05"
      event: Vivian敲门，Jimmy模仿Webb声音骗她离开
    - time: "11:10-11:20"
      event: Jimmy离开现场，布置假证据
    - time: "11:30"
      event: Jimmy回到厨房，伪装一直在工作
    - time: "01:00"
      event: Morrison到达，开始栽赃Zack
'''

with codecs.open(os.path.join(base_path, 'loop6', 'accusation.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop6_accusation)

print('Loop 6 accusation.yaml written successfully')

print('\n=== All dialog files created successfully! ===')
