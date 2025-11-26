# -*- coding: utf-8 -*-
"""
批量创建对话YAML文件的脚本
使用UTF-8编码确保中文正确保存
"""

import codecs
import os

base_path = r'd:\NDC_project\可视化工具\数据源\Unit1\dialogs'

# ============== Loop 2 Accusation ==============
loop2_accusation = '''# NDC Episode 1 - 循环2 指证对话
# 场景：芝加哥警局Morrison办公室
# 目标：通过时间线暴露Morrison的谎言

dialog_id: loop2_accusation
loop: 2
type: accusation

expose_info:
  scene: SC1009
  scene_name: 芝加哥警局Morrison办公室
  target: NPC104
  target_name: Morrison警探
  total_rounds: 4
  duration: 约120秒
  design_concept: 通过时间线矛盾→预谋行为→现场操作→职业签名，层层击破Morrison谎言

opening:
  lines:
    - speaker: NPC101
      action: 推门进入
      emotion: cold
      text: "Morrison。"

    - speaker: NPC104
      action: 正在看文件，抬起头
      emotion: dismissive
      text: "Brennan。我办公室不欢迎嫌疑人。"

    - speaker: NPC101
      action: 走到桌边，揉了揉眼睛，从口袋掏出糖罐，倒出几颗糖
      emotion: calm
      text: "那我不会待太久。我们谈谈那天晚上。"

    - speaker: NPC104
      emotion: mocking
      text: "我的报告写得很清楚。你不识字？"

    - speaker: NPC101
      action: 把一颗糖放进嘴里
      emotion: sarcastic
      text: "我读过。写得不错。很专业，很详细，唯一的问题是——全是谎言。"

    - speaker: NPC104
      action: 放下文件，靠回椅背
      emotion: threatening
      text: "小心你的措辞，Brennan。诽谤警官可是重罪。"

    - speaker: NPC101
      emotion: determined
      text: "那我们就让证据说话。从你的时间线开始。"

    - speaker: NPC104
      emotion: angry
      text: "时间线？你他妈在我办公室里审问我？"

    - speaker: NPC101
      action: 又吃了一颗糖
      emotion: calm
      text: "不是审问。只是...职业交流。警探对侦探。"

rounds:
  - round: 1
    name: 时间线矛盾
    lie:
      content: "00:30我接到匿名电话，立即出警。因为案情紧急，最快速度赶到现场。"
      source: Morrison声称临时接警
    required_evidences: [EV1211, EV1261, EV1241]
    evidence_names: [Morrison夫人时间证词, Tommy路线证词, Vivian时间证词]

    dialog:
      - speaker: NPC104
        emotion: confident
        text: "职业交流。好。那我'交流'给你听：00:30我接到匿名电话，立即出警。因为案情紧急，最快速度赶到现场。够清楚了？"

      - speaker: NPC101
        emotion: analytical
        text: "很清楚。00:30出发，01:00到达。30分钟。"

      - speaker: NPC104
        emotion: questioning
        text: "所以？"

      - speaker: NPC101
        emotion: sharp
        text: "所以从你家到蓝月亮酒吧只需要15分钟。我很好奇，剩下的15分钟——不，30分钟，你在哪里？"

      - speaker: NPC104
        emotion: angry
        text: "你他妈怎么知道15分钟？"

      - speaker: NPC101
        emotion: calm
        text: "我是侦探。问问题是我的工作。就像撒谎是腐败警察的工作一样。"

      - speaker: NPC104
        emotion: furious
        text: "你最好小心点，Brennan。"

      - speaker: NPC101
        emotion: confident
        text: "我很小心。所以我问了Tommy。他给你送过东西，记得吗？他说15分钟。最多。"

      - speaker: NPC104
        action: 停顿，眼神闪烁
        emotion: nervous
        text: "我...路上走错了。深夜接警，地址不清楚..."

      - speaker: NPC101
        action: 笑了
        emotion: mocking
        text: "走错路。Morrison，你在这个城市当了二十年警察。蓝月亮酒吧的招牌在三个街区外都看得见。你会'走错路'？"

      - speaker: NPC104
        emotion: defensive
        text: "也许我在路上处理了其他事情！这不关你的事！"

      - speaker: NPC101
        emotion: accusatory
        text: "关我的事。因为那30分钟里，你在用氯仿迷晕我。"

    result: Morrison无法解释30分钟的时间差，谎言初步被戳穿

  - round: 2
    name: 预谋行为
    lie:
      content: "警察提前领用装备很正常——"
      source: Morrison辩称巧合
    required_evidences: [EV1221]
    evidence_names: [警用便携式现场勘验箱领用单据]

    dialog:
      - speaker: NPC101
        emotion: questioning
        text: "便携式现场勘验箱。你记得吗？"

      - speaker: NPC104
        emotion: dismissive
        text: "我领用装备，关你屁事。"

      - speaker: NPC101
        emotion: sharp
        text: "日期。11月2日，19:30。案发前一天晚上。"

      - speaker: NPC104
        emotion: defensive
        text: "所以？警察提前领用装备很正常——"

      - speaker: NPC101
        emotion: accusatory
        text: "正常？Morrison，你在案发前一天晚上就领用了现场勘验箱。这叫什么？先见之明？还是预谋？"

      - speaker: NPC104
        emotion: panicked
        text: "那是巧合！我恰好领了，但没用到！"

      - speaker: NPC101
        emotion: calm
        text: "没用到。"

      - speaker: NPC104
        emotion: insistent
        text: "对！我只是恰好领了！"

      - speaker: NPC101
        emotion: mocking
        text: "Morrison，你知道你现在像什么吗？像那些我在法庭上见过的蠢货。每次被抓到把柄，都说'巧合'。"

    result: 证明Morrison提前准备，否定"临时接警"说法

  - round: 3
    name: 现场操作证据
    lie:
      content: "那可能是我检查现场时留下的。我把箱子放在地上了。"
      source: Morrison自相矛盾
    required_evidences: [EV1209, EV1223]
    evidence_names: [警用便携式现场勘验箱压痕, 便携式现场勘验箱]

    dialog:
      - speaker: NPC104
        emotion: dismissive
        text: "地板上的痕迹？这他妈能说明什么？"

      - speaker: NPC101
        emotion: analytical
        text: "这些压痕，完美契合便携式现场勘验箱的底部。间距、深度、尺寸——完全一致。你的箱子，Morrison。"

      - speaker: NPC104
        emotion: defensive
        text: "可能是清洁工具——"

      - speaker: NPC101
        emotion: firm
        text: "不是。"

      - speaker: NPC104
        emotion: desperate
        text: "可能是家具——"

      - speaker: NPC101
        emotion: firm
        text: "也不是。"

      - speaker: NPC104
        emotion: nervous
        text: "那...那可能是我检查现场时留下的。我把箱子放在地上了。"

      - speaker: NPC101
        emotion: sharp
        text: "哦？所以你'用到了'？刚才你不是说'没用到'吗？"

      - speaker: NPC104
        emotion: flustered
        text: "我...我是说...检查现场时用到了..."

      - speaker: NPC101
        emotion: mocking
        text: "Morrison，你在给自己挖坑。而且越挖越深。"

    result: 证明Morrison使用便携式现场勘验箱来到现场布置

  - round: 4
    name: 职业签名致命击破
    lie:
      content: "可能是我之后检查时用的！"
      source: Morrison最后挣扎
    required_evidences: [EV1271]
    evidence_names: [Rosa行为证词]

    dialog:
      - speaker: NPC104
        emotion: desperate
        text: "不！你没有证据证明我当时用了箱子！可能是我之后检查时用的！"

      - speaker: NPC101
        emotion: calm
        text: "Rosa。"

      - speaker: NPC104
        emotion: confused
        text: "什么？"

      - speaker: NPC101
        emotion: confident
        text: "Rosa一直在现场。她看得很清楚。"

      - speaker: NPC104
        emotion: dismissive
        text: "那个...那个清洁工...她什么都不知道..."

      - speaker: NPC101
        emotion: firm
        text: "她知道你'检查'现场的时候，什么工具都没用。你只是进去看了看，走了一圈，然后就出来了。"

      - speaker: NPC104
        emotion: desperate
        text: "她...她记错了...当时很乱..."

      - speaker: NPC101
        emotion: sharp
        text: "Morrison，你当了二十年警察。你比我更清楚什么时候证人在撒谎，什么时候在说真话。Rosa没有撒谎。"

      - speaker: NPC104
        emotion: defeated
        text: "够了...别说了..."

      - speaker: NPC101
        emotion: cold
        text: "为什么？Webb给了你多少钱？"

    result: 完全击破Morrison的谎言，逼迫其坦白

truth_reveal:
  lines:
    - speaker: NPC104
      emotion: bitter
      text: "钱？你以为我是为了钱？"

    - speaker: NPC101
      emotion: questioning
      text: "不然呢？"

    - speaker: NPC104
      emotion: desperate
      text: "我欠疤面Tony五千美元。他要杀我全家。我老婆，Brennan。我他妈的老婆。"

    - speaker: NPC101
      emotion: cold
      text: "所以你选择栽赃我。"

    - speaker: NPC104
      emotion: anguished
      text: "我已经走投无路了。有人找到我说可以帮我还债，保护我家人，我只需要把你变成嫌疑人。"

    - speaker: NPC101
      emotion: sarcastic
      text: "多么慷慨的提议。"

    - speaker: NPC104
      emotion: furious
      text: "你不懂！你他妈根本不懂！"

    - speaker: NPC101
      emotion: cold
      text: "我懂。我只是不同意。"

    - speaker: NPC104
      emotion: challenging
      text: "不同意？那你告诉我，Brennan，如果是你的家人，你会怎么做？"

    - speaker: NPC101
      emotion: firm
      text: "我不知道。但我不会栽赃一个无辜的人。我不会威胁一个为了孩子什么都愿意做的清洁工。Morrison，你有选择。你只是选择了最容易的那条路。"

    - speaker: NPC104
      emotion: guilty
      text: "最容易？每天晚上，我闭上眼就看到那个女人...Rosa...她为了孩子求我...我把她变成了帮凶..."

    - speaker: NPC101
      emotion: observing
      text: "至少你还有良心。虽然来得晚了点。"

    - speaker: NPC104
      emotion: bitter
      text: "良心。这个城市不相信良心，不相信正义。它只相信钱和权力。"

    - speaker: NPC101
      emotion: determined
      text: "也许。但我还是要试试。告诉我那个人是谁？"

    - speaker: NPC104
      emotion: fearful
      text: "我只知道他叫Whale。他从不露面。只有纸条，特殊纹样的纸条。"

    - speaker: NPC101
      emotion: questioning
      text: "除了你，他还收买了谁？"

    - speaker: NPC104
      emotion: uncertain
      text: "我不知道...他说会有人配合...Webb是别人杀的，我只负责栽赃你..."

    - speaker: NPC101
      emotion: analytical
      text: "双重保险。"

    - speaker: NPC104
      action: 点头
      emotion: defeated
      text: "对。他从一开始就没信任过我。Brennan...他还说了一件事。"

    - speaker: NPC101
      emotion: curious
      text: "什么？"

    - speaker: NPC104
      emotion: serious
      text: "Webb约你去酒吧，不是要给你案子。他把你当成'保险侦探'。如果他出事，你一定会查到底。他利用了你的职业操守。"

    - speaker: NPC101
      emotion: bitter
      text: "所以我也是工具。Webb的工具，Whale的目标。"

    - speaker: NPC104
      emotion: resigned
      text: "我们都是工具。Webb，我，你，Rosa...所有人。"

    - speaker: NPC101
      emotion: cold
      text: "不一样，Morrison。我被利用，但我没有出卖别人。你会为此付出代价。"

truth_summary:
  morrison_motive: 欠疤面Tony $5000赌债，被威胁家人安全
  whale_involvement: Whale收买Morrison，帮他还债，换取栽赃Zack
  morrison_role: 只负责栽赃，不是真凶
  key_revelation: Webb是别人杀的，Morrison只是帮凶
  next_clue: Whale的特殊纹样纸条，真凶另有其人
'''

with codecs.open(os.path.join(base_path, 'loop2', 'accusation.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop2_accusation)

print('Loop 2 accusation.yaml written successfully')

# ============== Loop 3 Opening ==============
loop3_opening = '''# NDC Episode 1 - 循环3 开篇对话
# 场景：酒吧大堂

dialog_id: loop3_opening
loop: 3
type: opening

sections:
  tommy_lobby_chat:
    scene: SC1002
    scene_name: 酒吧大堂
    duration: 约40秒
    description: 与Tommy初步对话，引出古董生意

    lines:
      - speaker: NPC101
        emotion: calm
        text: "Tommy，我需要问你一些关于Webb的事。"

      - speaker: NPC105
        emotion: nervous
        text: "Brennan先生...又是您。Webb先生的案子...警察不是在查吗？"

      - speaker: NPC101
        action: 从口袋掏出糖罐，吃了一颗糖
        emotion: casual
        text: "我也在查。Webb的生意，你了解多少？"

      - speaker: NPC105
        emotion: evasive
        text: "生意？我...我只是个账房先生，负责记账...具体的业务，Webb先生不太...不太让我过问..."

      - speaker: NPC101
        emotion: questioning
        text: "账房先生会记账。那账本上记的是什么？"

      - speaker: NPC105
        emotion: nervous
        text: "私酒...都是私酒生意。您知道的，禁酒令，但很多人还是想喝酒...Webb先生就做这个..."

      - speaker: NPC101
        emotion: suspicious
        text: "只有私酒？"

      - speaker: NPC105
        emotion: insistent
        text: "对，只有私酒。Webb先生的生意很简单，从加拿大进货，卖给芝加哥的客户...就这样..."

      - speaker: NPC101
        action: 又吃了一颗糖
        emotion: observing
        text: "很简单。那为什么你看起来这么紧张？"

      - speaker: NPC105
        emotion: defensive
        text: "我...我没有紧张...只是...Webb先生死了，大家都很...都很不安..."

      - speaker: NPC101
        emotion: analytical
        text: "Tommy，做私酒生意不需要这么紧张。除非...他还做了别的。"

      - speaker: NPC105
        emotion: panicked
        text: "没有！真的没有！Webb先生只做私酒生意，绝对没有其他业务！"

      - speaker: NPC101
        emotion: cold
        text: "绝对？你很确定。"

      - speaker: NPC105
        emotion: desperate
        text: "确定...我记了三年账，都是私酒...威士忌、朗姆酒、葡萄酒...就这些..."

evidence_obtained:
  - id: EV1361
    name: Tommy的证词
    description: Tommy坚称Webb只做私酒生意，没有其他业务
'''

with codecs.open(os.path.join(base_path, 'loop3', 'opening.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop3_opening)

print('Loop 3 opening.yaml written successfully')

# ============== Loop 3 Accusation ==============
loop3_accusation = '''# NDC Episode 1 - 循环3 指证对话
# 场景：酒吧大堂
# 目标：揭露Webb的勒索网络

dialog_id: loop3_accusation
loop: 3
type: accusation

expose_info:
  scene: SC1002
  scene_name: 酒吧大堂
  target: NPC105
  target_name: Tommy
  total_rounds: 3
  duration: 约90秒
  design_concept: 三轮精准指证，每个证据必须直接反驳Tommy上一句话

opening:
  lines:
    - speaker: NPC101
      emotion: cold
      text: "Tommy，我们需要再谈谈Webb的生意。"

    - speaker: NPC105
      emotion: nervous
      text: "Brennan先生...我该说的都说了...都是私酒生意..."

    - speaker: NPC101
      action: 从口袋掏出财务报告，放在桌上
      emotion: calm
      text: "是吗？那解释一下这个。"

    - speaker: NPC105
      action: 看了看
      emotion: confused
      text: "这是...Webb先生的财务报告..."

rounds:
  - round: 1
    name: 收入来源谎言
    lie:
      content: "收入全部来自酒类销售"
      source: Tommy声称只做私酒
    required_evidences: [EV1311, EV1322]
    evidence_names: [Webb月收入财务报告, Webb酒吧营业收入记录]

    dialog:
      - speaker: NPC101
        emotion: sharp
        text: "你说收入全部来自酒类销售。但这份报告显示，Webb每月收入15,000美元。"

      - speaker: NPC105
        emotion: questioning
        text: "对...所以？"

      - speaker: NPC101
        action: 拿出另一份文件
        emotion: analytical
        text: "所以你们的酒类销售额最多只有4,000美元。Tommy，多出来的11,000美元是从哪里来的？"

      - speaker: NPC105
        action: 停顿，紧张地
        emotion: nervous
        text: "我...那个...可能是..."

      - speaker: NPC101
        emotion: questioning
        text: "可能是什么？"

      - speaker: NPC105
        emotion: defeated
        text: "可能是...还有其他生意...我...我记错了..."

      - speaker: NPC101
        emotion: accusatory
        text: "你记账三年，会'记错'收入来源？Tommy，你在撒谎。"

      - speaker: NPC105
        action: 擦了擦额头
        emotion: confessing
        text: "好吧...好吧...Webb先生还做古董买卖...中国花瓶，欧洲油画，那些东西..."

      - speaker: NPC101
        emotion: cold
        text: "古董买卖。"

      - speaker: NPC105
        emotion: defensive
        text: "对！Webb先生从各地收购古董，然后卖给那些有钱人...Thompson议员，Coleman法官...这些都是正常的古董交易！"

    result: Tommy被迫承认还有古董买卖

  - round: 2
    name: 古董销售谎言
    lie:
      content: "古董是正常买卖，已经卖出去了"
      source: Tommy转移话题
    required_evidences: [EV1331, EV1332]
    evidence_names: [酒吧歌舞厅现场照片-欧洲油画, 酒吧歌舞厅现场照片-中国花瓶]

    dialog:
      - speaker: NPC101
        action: 拿出现场照片
        emotion: sharp
        text: "Tommy，你说中国花瓶卖给了Thompson议员，欧洲油画卖给了Coleman法官。对吗？"

      - speaker: NPC105
        emotion: confident
        text: "对...都是按账本记录的..."

      - speaker: NPC101
        emotion: cold
        text: "那看看这些照片。"

      - speaker: NPC105
        action: 看了看，脸色煞白
        emotion: shocked
        text: "这是..."

      - speaker: NPC101
        emotion: accusatory
        text: "Webb办公室的照片。这个中国花瓶，还在那里。那幅欧洲油画，也还挂在墙上。Tommy，如果真的'卖'了，为什么还在那里？"

      - speaker: NPC105
        emotion: panicked
        text: "我...我不知道...也许...也许Webb先生又买回来了..."

      - speaker: NPC101
        action: 冷笑
        emotion: mocking
        text: "买回来？那账本上怎么没有记录？"

      - speaker: NPC105
        emotion: desperate
        text: "我...我只是按Webb先生的指示记账！他说这些是'特殊的商业安排'，让我记录成古董销售..."

    result: Tommy无法解释古董为何还在现场

  - round: 3
    name: 不知情谎言
    lie:
      content: "我只是做账的，不知道具体业务"
      source: Tommy推卸责任
    required_evidences: [EV1313]
    evidence_names: [Tommy的详细工作记录]

    dialog:
      - speaker: NPC101
        action: 拿出工作日志，扔在桌上
        emotion: cold
        text: "这是什么？"

      - speaker: NPC105
        action: 看了看，声音发抖
        emotion: terrified
        text: "这是...我的工作日志..."

      - speaker: NPC101
        emotion: sharp
        text: "你的。笔迹和你办公室的经营记录一样。我对比过了。"

      - speaker: NPC105
        emotion: defensive
        text: "那...那又怎么样..."

      - speaker: NPC101
        emotion: analytical
        text: "你说你不知道具体业务，只是做账。但看看你记录了什么：Thompson访问30分钟，重点观看中国花瓶。Coleman访问25分钟，重点观看欧洲油画。Tommy，这些不是'做账的人'会记录的内容。"

      - speaker: NPC105
        emotion: panicked
        text: "我...我只是...Webb先生让我记录的..."

      - speaker: NPC101
        emotion: cold
        text: "还有更有意思的。"

      - speaker: NPC105
        action: 害怕地
        emotion: terrified
        text: "什么..."

      - speaker: NPC101
        emotion: accusatory
        text: "同一件古董，被不同客户'购买'多次。中国花瓶，在三个月内'卖给'Thompson五次，每次8,000美元。欧洲油画，'卖给'Coleman四次，每次6,000美元。"

      - speaker: NPC105
        emotion: panicked
        text: "那是...那是..."

      - speaker: NPC101
        emotion: final
        text: "那是按月收取的保护费。Tommy，这不是古董买卖，这是勒索。你不只是知情，你就是这个勒索网络的核心操作者。"

    result: 彻底击破Tommy的谎言

truth_reveal:
  lines:
    - speaker: NPC105
      action: 双手抱头
      emotion: broken
      text: "不...不是的...我只是...我只是帮Webb先生记录..."

    - speaker: NPC101
      emotion: cold
      text: "记录访问时间，记录停留时长，记录'购买'次数和金额。Tommy，你管理着整个勒索网络的账目。你知道每个客户，每笔交易，每个秘密。"

    - speaker: NPC105
      action: 崩溃
      emotion: desperate
      text: "我没有选择！Webb先生说如果我不配合，就让我失业！我有家要养，我不能失去这份工作！"

    - speaker: NPC101
      emotion: questioning
      text: "所以你帮他勒索那些人。"

    - speaker: NPC105
      action: 痛苦地
      emotion: anguished
      text: "我...我知道这不对...但是...但是我能怎么办？Brennan先生，我只是个打工的...我没办法..."

    - speaker: NPC101
      action: 沉默片刻，又吃了一颗糖
      emotion: cold
      text: "Tommy，你会为此付出代价。但如果你配合调查，会比Webb要轻。"

    - speaker: NPC105
      emotion: hopeful
      text: "我...我会配合...我会配合的..."

    - speaker: NPC101
      emotion: questioning
      text: "Webb最近勒索的目标是谁？"

    - speaker: NPC105
      emotion: fearful
      text: "我不知道具体是谁...但Webb先生遇到了大麻烦...他勒索的那个目标...很棘手..."

    - speaker: NPC101
      emotion: curious
      text: "除了你，还有谁了解Webb的生意？"

    - speaker: NPC105
      emotion: hesitant
      text: "Jimmy...厨师Jimmy...他也参与了勒索生意..."

    - speaker: NPC101
      emotion: questioning
      text: "Jimmy？"

    - speaker: NPC105
      emotion: explaining
      text: "对...他和Webb先生的关系...不太一样...Brennan先生，您应该去问问Jimmy，他可能知道更多..."

truth_summary:
  webb_business: Webb经营勒索网络，用古董作为档案代号
  tommy_role: Tommy深度参与，管理整个勒索网络的账目
  key_revelation: Jimmy也参与勒索生意，可能知道更多
  next_target: 调查Jimmy，揭露Webb遇到的大麻烦
'''

with codecs.open(os.path.join(base_path, 'loop3', 'accusation.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop3_accusation)

print('Loop 3 accusation.yaml written successfully')

# ============== Loop 4 Opening ==============
loop4_opening = '''# NDC Episode 1 - 循环4 开篇对话
# 场景：Jimmy家门口 + 客厅

dialog_id: loop4_opening
loop: 4
type: opening

sections:
  jimmy_home_entrance:
    scene: SC1012
    scene_name: Jimmy家中客厅
    duration: 约70秒
    description: 与Anna对话，获准进入搜查

    lines:
      - speaker: NPC108
        emotion: nervous
        text: "谁？"

      - speaker: NPC101
        emotion: professional
        text: "Zack Brennan，私家侦探。我在调查蓝月亮歌舞厅Webb先生的案子。"

      - speaker: NPC108
        emotion: fearful
        text: "我们不知道什么！请离开！"

      - speaker: NPC101
        emotion: calm
        text: "等等。我不是警察，也不是来找麻烦的。Webb先生死了，我被栽赃成凶手，只有三天时间找出真相。"

      - speaker: NPC108
        emotion: confused
        text: "那...那跟我丈夫有什么关系？Jimmy只是厨师..."

      - speaker: NPC101
        emotion: reassuring
        text: "我知道。但他在那里工作，可能见过或听过什么。我只想问几个问题，不会给他惹麻烦。"

      - speaker: NPC108
        emotion: worried
        text: "可是...我们的身份...如果警察来..."

      - speaker: NPC101
        emotion: logical
        text: "我不关心身份问题。而且正因为我来了，警察才不会来。帮我，就是在帮Jimmy。"

      - speaker: NPC108
        emotion: hesitant
        text: "...好吧。但我真的什么都不知道...Jimmy从不跟我说工作的事。"

      - speaker: NPC101
        emotion: questioning
        text: "Jimmy最近怎么样？工作还顺利吗？"

      - speaker: NPC108
        emotion: recalling
        text: "应该...挺顺利的。Webb先生对他很好，上个月还送了他生日礼物..."

      - speaker: NPC101
        emotion: curious
        text: "什么礼物？"

      - speaker: NPC108
        emotion: explaining
        text: "一本书...他说是很珍贵的书，让Jimmy好好保管。"

      - speaker: NPC101
        emotion: questioning
        text: "Jimmy经常看那本书？"

      - speaker: NPC108
        emotion: worried
        text: "最近每晚都在看...他会半夜惊醒，坐在床边翻那本书，看着看着就叹气...我问他怎么了，他说没事，让我别担心..."

      - speaker: NPC101
        emotion: persuasive
        text: "Anna，那本书可能很重要。我能看看吗？"

      - speaker: NPC108
        emotion: hesitant
        text: "可是...那是Jimmy的私人物品...我不能..."

      - speaker: NPC101
        emotion: serious
        text: "听着，Anna。如果Webb先生的死和某些生意有关，那本书可能是线索。我现在来看，至少还能保护Jimmy。如果警察来了，他们会翻遍整个房子，不会像我这么客气。"

      - speaker: NPC108
        emotion: alarmed
        text: "警察会来？"

      - speaker: NPC101
        emotion: calm
        text: "如果我查不出真相，他们一定会来。你是想让我看一本书，还是想让警察来搜家？"

      - speaker: NPC108
        emotion: surrendering
        text: "...您保证只看那本书？"

      - speaker: NPC101
        emotion: sincere
        text: "我保证。不会弄乱他的东西。"

      - speaker: NPC108
        emotion: resigned
        text: "...书在卧室。他放在枕头下面...但我不想动他的东西...您能...自己去看吗？"

      - speaker: NPC101
        emotion: questioning
        text: "你信得过我？"

      - speaker: NPC108
        emotion: trusting
        text: "您看起来...不像坏人。而且您说您也被栽赃了...我想您能理解我们的处境。"

      - speaker: NPC101
        emotion: grateful
        text: "我会小心的。"

      - speaker: NPC108
        emotion: pleading
        text: "请您...只看那本书就好...其他的东西，请别动..."

      - speaker: NPC101
        emotion: reassuring
        text: "我会的。"

evidence_obtained:
  - id: EV1421
    name: Jimmy家庭合照
    description: Jimmy与妻子Anna的温馨合影，写着"我的世界"
'''

with codecs.open(os.path.join(base_path, 'loop4', 'opening.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop4_opening)

print('Loop 4 opening.yaml written successfully')

# ============== Loop 4 Accusation ==============
loop4_accusation = '''# NDC Episode 1 - 循环4 指证对话
# 场景：酒吧大堂
# 目标：拆解Jimmy的三层防御谎言

dialog_id: loop4_accusation
loop: 4
type: accusation

expose_info:
  scene: SC1002
  scene_name: 酒吧大堂
  target: NPC107
  target_name: Jimmy
  total_rounds: 3
  duration: 约90秒
  design_concept: 逐步拆解Jimmy的三层防御谎言

opening:
  lines:
    - speaker: NPC101
      emotion: cold
      text: "Jimmy，我需要问你几个问题。"

    - speaker: NPC107
      emotion: nervous
      text: "Brennan先生...我...我只是厨师...Webb先生的事，我真的不太清楚..."

    - speaker: NPC101
      emotion: questioning
      text: "你的工作是什么？"

    - speaker: NPC107
      emotion: evasive
      text: "做饭...洗盘子...准备食材...就是些杂活...我和Webb先生就是普通的老板和员工..."

rounds:
  - round: 1
    name: 身份关系欺骗
    lie:
      content: "我只是这里的厨师，Webb雇我就是做些杂事"
      source: Jimmy伪装普通员工
    required_evidences: [EV1320, EV1411]
    evidence_names: [Webb古董收藏记录, 伪装成陶泥的古董水壶]

    dialog:
      - speaker: NPC101
        emotion: cold
        text: "普通？"

      - speaker: NPC107
        emotion: defensive
        text: "是的...很普通...他雇我做厨师，我就做我的工作...他的生意，我不了解..."

      - speaker: NPC101
        emotion: sharp
        text: "那你能解释这个吗？"

      - speaker: NPC107
        emotion: confused
        text: "这...这是什么？"

      - speaker: NPC101
        emotion: cold
        text: "Webb的古董收藏记录。Bennington陶器，价值两千美金。"

      - speaker: NPC107
        emotion: panicked
        text: "古董？我...我从来没见过这些东西..."

      - speaker: NPC101
        emotion: questioning
        text: "是吗？"

      - speaker: NPC107
        emotion: insistent
        text: "是的...我只是厨师...怎么会接触这些..."

      - speaker: NPC101
        emotion: accusatory
        text: "那这个呢？"

      - speaker: NPC107
        emotion: shocked
        text: "这...这是..."

      - speaker: NPC101
        emotion: sharp
        text: "你从Webb办公室拿出来的水壶。Bennington陶器。"

      - speaker: NPC107
        emotion: panicked
        text: "什么？！这...这个破水壶是古董？我...我真的不知道！"

      - speaker: NPC101
        emotion: cold
        text: "你刚才说'从来没见过'。"

      - speaker: NPC107
        emotion: backtracking
        text: "我...我是说...我见过这个水壶，但我不知道它是古董！我以为...以为是要扔掉的破陶器...就...就顺手拿了..."

    result: Jimmy被迫改口承认拿过水壶

  - round: 2
    name: 盗窃行为欺骗
    lie:
      content: "我看它像是要扔掉的破陶器，所以随手拿了"
      source: Jimmy编造理由
    required_evidences: [EV1441]
    evidence_names: [Tommy目击证词]

    dialog:
      - speaker: NPC101
        emotion: questioning
        text: "所以你以为它是垃圾？"

      - speaker: NPC107
        emotion: defensive
        text: "是...是的...看起来很旧...很破...我以为没人要了..."

      - speaker: NPC101
        emotion: sharp
        text: "Tommy说他看到你抱着这个水壶，两只手捧着，走得很慢，眼睛一直盯着它。"

      - speaker: NPC107
        emotion: nervous
        text: "Tommy...Tommy看错了..."

      - speaker: NPC101
        emotion: accusatory
        text: "他还说你看到他的时候，立刻把水壶藏到身后。"

      - speaker: NPC107
        emotion: desperate
        text: "我...我只是怕摔坏它..."

      - speaker: NPC101
        emotion: mocking
        text: "怕摔坏？"

      - speaker: NPC107
        emotion: weak
        text: "是...是的..."

      - speaker: NPC101
        emotion: sharp
        text: "一个你以为是垃圾的破陶器，你怕摔坏？"

      - speaker: NPC107
        emotion: cornered
        text: "我...我..."

      - speaker: NPC101
        emotion: accusatory
        text: "而且你还用泥浆涂在表面伪装它。一个普通厨师，怎么知道要伪装古董？"

      - speaker: NPC107
        emotion: confessing
        text: "好吧！好吧...我承认...Webb先生确实信任我...他不只是让我做饭...有时候会让我帮忙处理一些...一些重要的事情..."

    result: Jimmy被迫承认与Webb关系密切

  - round: 3
    name: 关系和谐欺骗
    lie:
      content: "我们合作很紧密，一直很愉快，从来没有矛盾"
      source: Jimmy伪装和谐
    required_evidences: [EV1341]
    evidence_names: [Vivian争吵目击证词]

    dialog:
      - speaker: NPC101
        emotion: cold
        text: "从来没有矛盾？"

      - speaker: NPC107
        emotion: defensive
        text: "是的...Webb先生对我很好...我很感激他..."

      - speaker: NPC101
        emotion: sharp
        text: "Vivian听到你们在办公室大吵。"

      - speaker: NPC107
        emotion: shocked
        text: "什么？不...那只是..."

      - speaker: NPC101
        emotion: accusatory
        text: "她说你警告Webb：'不要接这个生意，会出大事的'。"

      - speaker: NPC107
        emotion: defensive
        text: "那...那只是工作上的小分歧...很正常..."

      - speaker: NPC101
        emotion: sharp
        text: "小分歧？她说你摔门离开，脸色铁青。"

      - speaker: NPC107
        emotion: nervous
        text: "我...我当时只是...只是有点激动..."

      - speaker: NPC101
        emotion: questioning
        text: "什么生意？Webb想勒索谁？"

      - speaker: NPC107
        emotion: fearful
        text: "我...我不能说..."

      - speaker: NPC101
        emotion: pressing
        text: "不能说？"

      - speaker: NPC107
        emotion: terrified
        text: "这...这太危险了...Brennan先生，我真的不能说..."

      - speaker: NPC101
        emotion: cold
        text: "所以确实有个危险的目标。"

      - speaker: NPC107
        emotion: cornered
        text: "我..."

      - speaker: NPC101
        emotion: final
        text: "这就是Webb遇到的'大麻烦'。"

    result: Jimmy被迫透露Whale的存在

truth_reveal:
  lines:
    - speaker: NPC107
      emotion: defeated
      text: "...是的...有个人...叫'Whale'...这个人很危险...非常危险...Webb先生想勒索他...但我一直劝他不要...我说这会出大事...但Webb先生不听..."

    - speaker: NPC101
      emotion: questioning
      text: "'Whale'是谁？"

    - speaker: NPC107
      emotion: fearful
      text: "我不知道...真的不知道...我只知道这个代号...Webb先生也只知道代号..."

    - speaker: NPC101
      emotion: questioning
      text: "你怎么知道他危险？"

    - speaker: NPC107
      emotion: trembling
      text: "我...我听说过一些事...这种人...不是普通人能惹的...Brennan先生，其他的我真的不知道了...我只是想劝Webb先生别做蠢事...但他太贪心了..."

    - speaker: NPC101
      emotion: suspicious
      text: "如果你知道这么危险，为什么不离开？"

    - speaker: NPC107
      emotion: desperate
      text: "我...我需要这份工作...我还有家要养..."

    - speaker: NPC101
      emotion: cold
      text: "芝加哥不缺厨师的工作。"

    - speaker: NPC107
      emotion: cornered
      text: "可是...可是Webb先生给的工资很高...而且...而且我..."

    - speaker: NPC101
      emotion: pressing
      text: "而且什么？"

    - speaker: NPC107
      emotion: shutting_down
      text: "...没什么了..."

    - speaker: NPC101
      emotion: accusatory
      text: "Jimmy，你在隐瞒什么？"

    - speaker: NPC107
      emotion: desperate
      text: "我没有...我什么都说了...其他的我真的不知道..."

truth_summary:
  jimmy_role: Jimmy与Webb关系密切，深度参与勒索生意
  whale_reveal: 存在一个叫"Whale"的超级危险目标
  jimmy_warning: Jimmy曾警告Webb不要勒索Whale
  next_clue: Jimmy提示调查Vivian，她可能知道更多
'''

with codecs.open(os.path.join(base_path, 'loop4', 'accusation.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop4_accusation)

print('Loop 4 accusation.yaml written successfully')
