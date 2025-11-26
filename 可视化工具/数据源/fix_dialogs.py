# -*- coding: utf-8 -*-
import codecs
import os

base_path = r'd:\NDC_project\可视化工具\数据源\Unit1\dialogs'

# ============== Loop 1 Accusation ==============
loop1_accusation = '''# NDC Episode 1 - 循环1 指证对话
# 场景：酒吧大堂 - Rosa指证
# 目标：三轮击破Rosa谎言，揭露Morrison

dialog_id: loop1_accusation
loop: 1
type: accusation

expose_info:
  scene: SC1004
  scene_name: 酒吧大堂
  target: NPC103
  target_name: Rosa
  total_rounds: 3
  duration: 约54秒
  design_concept: 专业侦探 vs 恐惧母亲的心理博弈

opening:
  lines:
    - speaker: NPC101
      emotion: calm
      text: "Rosa，我需要问你一些问题。"

    - speaker: NPC103
      emotion: nervous
      text: "Brennan先生...我...我很忙..."

    - speaker: NPC101
      emotion: firm
      text: "不会耽误你太久。关于昨晚的事。"

rounds:
  - round: 1
    name: 地点谎言
    lie:
      content: "我一直在地下室酒窖清理，整理酒瓶和架子"
      source: Rosa虚假陈述

    required_evidences: [EV1115]
    evidence_names: [工作记录卡]

    dialog:
      - speaker: NPC103
        emotion: nervous
        text: "昨晚...我一直在地下室酒窖清理，整理酒瓶和架子..."

      - speaker: NPC101
        action: 取出工作记录卡，平静但严厉
        emotion: serious
        text: "Rosa，这是你的工作安排表。上面明确写着你昨晚23:00到01:00在后台走廊清洁，不是地下室酒窖。你为什么要撒谎？"

      - speaker: NPC103
        action: 声音颤抖，开始搓手
        emotion: panicked
        text: "哦...哦天哪，我...我可能记错了...最近太累了，总是搞混工作安排...对，我是在后台清洁..."

    result: 地点谎言被戳穿，Rosa被迫修正说法

  - round: 2
    name: 目击谎言
    lie:
      content: "我在后台走廊工作，但我很专心清洁地板和墙壁，那里很安静，什么异常都没发生..."
      source: Rosa否认目击

    required_evidences: [EV1114, EV1121]
    evidence_names: [沾有氯仿的毛巾, 氯仿瓶]

    dialog:
      - speaker: NPC103
        emotion: defensive
        text: "我在后台走廊工作，但我很专心清洁地板和墙壁，那里很安静，什么异常都没发生..."

      - speaker: NPC101
        action: 严肃地展示毛巾和氯仿瓶
        emotion: accusatory
        text: "专心清洁？Rosa，这条毛巾在你的工作区域被发现，上面有氯仿残留。而这个氯仿瓶是在后台走廊的垃圾桶内发现的，你说当时你在后台清洁，你工作区域的毛巾沾染了案发现场附近的氯仿，氯仿是医用麻醉剂，不是清洁用品。如果你什么都没看到，怎么解释这个？"

      - speaker: NPC103
        action: 长时间沉默，看着毛巾，眼中涌出泪水
        emotion: breaking
        text: "我...我..."

      - speaker: NPC103
        action: 抱头哭泣
        emotion: confessing
        text: "好吧！是我！是我用这条毛巾迷昏了您！我儿子Miguel生病了，需要手术费，我实在没办法了...求求您别让我坐牢，Miguel还需要我照顾..."

    result: 目击谎言被彻底击破，Rosa承认使用氯仿

  - round: 3
    name: 自认谎言
    lie:
      content: "我等您路过走廊时，从背后用毛巾捂住您的嘴和鼻子...您昏倒后我把您拖到Webb先生的办公室..."
      source: Rosa虚假自认

    required_evidences: [EV1122]
    evidence_names: [地板拖拽痕迹]

    dialog:
      - speaker: NPC103
        emotion: desperate
        text: "我等您路过走廊时，从背后用毛巾捂住您的嘴和鼻子...您昏倒后我把您拖到Webb先生的办公室..."

      - speaker: NPC101
        action: 温和但坚定，展示照片
        emotion: analytical
        text: "Rosa，我相信你爱你的儿子，但你不是凶手。看这些拖拽痕迹——需要150磅的力量才能造成2.5厘米的压痕。你体重不到120磅，根本做不到。谁威胁你这样说的？"

      - speaker: NPC103
        action: 声音几乎是耳语，充满恐惧
        emotion: terrified
        text: "是...是Morrison警官..."

      - speaker: NPC103
        action: 抱头痛哭
        emotion: broken
        text: "他...他说如果我不配合，就让我失去工作...他知道我儿子生病的事，知道我需要这份工作...我不知道他要做什么！我只是按他说的，如果有人问起，就说什么都没看到...如果实在瞒不住，就说是我做的..."

      - speaker: NPC103
        action: 看向Zack，眼中充满恐惧
        emotion: pleading
        text: "求求您别让Morrison知道我说了...我真的不知道他具体做了什么...我发誓！"

    result: 自认谎言被彻底否定，揭露Morrison是幕后黑手

truth_reveal:
  lines:
    - speaker: NPC101
      emotion: cold
      text: "Rosa，你不用害怕。Morrison会为他做的事付出代价。"

    - speaker: NPC103
      emotion: hopeful
      text: "真的吗...Brennan先生..."

    - speaker: NPC101
      emotion: reassuring
      text: "我会保护你。但你要配合我的调查。"

    - speaker: NPC103
      emotion: grateful
      text: "我...我会的...谢谢您..."

truth_summary:
  rosa_role: 被Morrison威胁的帮凶，负责用氯仿迷晕Zack
  morrison_involvement: Morrison是幕后指使者，威胁Rosa配合栽赃
  key_revelation: Morrison才是真正需要调查的对象
  next_target: 调查Morrison，揭露更深层的阴谋
'''

with codecs.open(os.path.join(base_path, 'loop1', 'accusation.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop1_accusation)

print('Loop 1 accusation.yaml written successfully')

# ============== Loop 1 Tommy对话 ==============
loop1_tommy = '''# NDC Episode 1 - 循环1 Tommy对话
# 场景：Tommy办公室

dialog_id: loop1_tommy
loop: 1
type: npc_dialog

dialog_info:
  scene: SC1003
  scene_name: Tommy办公室
  target: NPC105
  target_name: Tommy

dialog:
  - speaker: NPC101
    emotion: questioning
    text: "关于昨晚的情况，你有什么要说的吗？"

  - speaker: NPC105
    action: 紧张地整理文件
    emotion: nervous
    text: "昨晚...我大部分时间都在办公室里..."

  - speaker: NPC101
    emotion: questioning
    text: "11:30左右有听到什么异常声响吗？"

  - speaker: NPC105
    action: 停顿
    emotion: hesitant
    text: "确实有一声枪响...但这声枪响和平时黑帮火拼的声音不太一样，只听到了一声..."

evidence_obtained:
  - id: EV1133
    name: Tommy时间证词
    description: Tommy确认11:30左右听到一声枪响，与平时黑帮火拼不同
'''

with codecs.open(os.path.join(base_path, 'loop1', 'tommy.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop1_tommy)

print('Loop 1 tommy.yaml written successfully')

# ============== Loop 1 Rosa对话（非指证） ==============
loop1_rosa = '''# NDC Episode 1 - 循环1 Rosa初次对话
# 场景：酒吧大堂

dialog_id: loop1_rosa_chat
loop: 1
type: npc_dialog

dialog_info:
  scene: SC1004
  scene_name: 酒吧大堂
  target: NPC103
  target_name: Rosa

dialog:
  - speaker: NPC101
    emotion: calm
    text: "你好，我是Brennan。想问你几个问题。"

  - speaker: NPC103
    action: 低头继续打扫
    emotion: nervous
    text: "我...我很忙...要打扫..."

  - speaker: NPC101
    emotion: gentle
    text: "不会耽误太久。昨晚你在哪里工作？"

  - speaker: NPC103
    emotion: evasive
    text: "我...我在地下室酒窖...整理酒瓶..."

  - speaker: NPC101
    emotion: observing
    text: "你看起来很紧张。"

  - speaker: NPC103
    action: 手开始颤抖
    emotion: fearful
    text: "没...没有...我只是...最近太累了..."

note: 此对话用于初步了解Rosa，正式指证需要收集足够证据后触发
'''

with codecs.open(os.path.join(base_path, 'loop1', 'rosa.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop1_rosa)

print('Loop 1 rosa.yaml written successfully')

# ============== Loop 1 Ending ==============
loop1_ending = '''# NDC Episode 1 - 循环1 结尾对话
# 场景：酒吧外街道

dialog_id: loop1_ending
loop: 1
type: ending

sections:
  loop1_conclusion:
    scene: SC1006
    scene_name: 酒吧外街道
    description: 循环1结束，确定下一步调查方向

    lines:
      - speaker: NPC102
        emotion: thoughtful
        text: "Rosa说是Morrison威胁她的..."

      - speaker: NPC101
        action: 点燃一根烟
        emotion: analytical
        text: "Morrison来得太快，太急于定罪。他一定知道些什么。"

      - speaker: NPC102
        emotion: curious
        text: "你打算怎么调查他？他是警探，不会轻易露出破绽。"

      - speaker: NPC101
        emotion: determined
        text: "每个人都有弱点。Morrison也不例外。"

      - speaker: NPC102
        emotion: questioning
        text: "从哪里开始？"

      - speaker: NPC101
        action: 看向远方
        emotion: cold
        text: "他的家。他的妻子。她可能知道些什么。"

      - speaker: NPC102
        emotion: agreeing
        text: "我来安排。记者证有时候比侦探执照更好用。"

      - speaker: NPC101
        emotion: appreciative
        text: "你学得很快。"

      - speaker: NPC102
        action: 微笑
        emotion: confident
        text: "我有个好老师。"

next_loop_hint:
  target: Morrison
  location: Morrison家中
  approach: 以记者身份接近Morrison夫人
'''

with codecs.open(os.path.join(base_path, 'loop1', 'ending.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop1_ending)

print('Loop 1 ending.yaml written successfully')

# ============== Loop 3 Whale Call ==============
loop3_whale_call = '''# NDC Episode 1 - 循环3 Whale电话事件
# 场景：Webb办公室 - 电话铃响

dialog_id: loop3_whale_call
loop: 3
type: special_event
trigger: 搜索Webb办公室

event_info:
  scene: SC1005
  scene_name: Webb办公室
  duration: 约30秒
  description: Whale给Zack打神秘电话

dialog:
  - speaker: narration
    text: "[电话铃突然响起]"

  - speaker: NPC101
    action: 看向电话
    emotion: suspicious
    text: "Webb办公室的电话...谁会打来..."

  - speaker: narration
    text: "[电话继续响]"

  - speaker: NPC101
    action: 拿起听筒
    emotion: cautious
    text: "喂？"

  - speaker: unknown_voice
    action: 电话那头传来低沉的声音
    emotion: cold
    text: "Brennan先生...我听说你在调查Webb的死..."

  - speaker: NPC101
    emotion: alert
    text: "你是谁？"

  - speaker: unknown_voice
    emotion: amused
    text: "我？我只是一个...关心这件事的人。你可以叫我...Whale。"

  - speaker: NPC101
    emotion: sharp
    text: "Whale？你和Webb的死有关？"

  - speaker: unknown_voice
    action: 轻笑
    emotion: threatening
    text: "Webb先生做了一些不该做的事...他试图勒索我...这是不明智的选择。"

  - speaker: NPC101
    emotion: cold
    text: "所以你杀了他。"

  - speaker: unknown_voice
    emotion: calm
    text: "我？不，Brennan先生。我只是...提供了一些建议。真正动手的人...你很快就会知道了。"

  - speaker: NPC101
    emotion: threatening
    text: "我会找到你的。"

  - speaker: unknown_voice
    emotion: amused
    text: "也许吧。但在此之前...小心你身边的人，Brennan先生。不是每个人都像看起来那么无辜。"

  - speaker: narration
    text: "[电话被挂断]"

  - speaker: NPC101
    action: 放下听筒，表情凝重
    emotion: troubled
    text: "Whale...这个名字...到底是谁..."

evidence_obtained:
  - id: EV1351
    name: Whale的神秘电话
    description: 一个自称Whale的人打来电话，暗示Webb因勒索他而被杀
'''

with codecs.open(os.path.join(base_path, 'loop3', 'whale_call.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop3_whale_call)

print('Loop 3 whale_call.yaml written successfully')

# ============== Loop 6 Ending ==============
loop6_ending = '''# NDC Episode 1 - 循环6 结局对话
# 场景：Jimmy家中 + Webb办公室

dialog_id: loop6_ending
loop: 6
type: ending

sections:
  jimmy_tragedy:
    scene: SC1014
    scene_name: Jimmy家中
    description: Jimmy认罪后的悲剧

    lines:
      - speaker: NPC107
        emotion: desperate
        text: "是...是我杀了他...'Whale'...他联系了我..."

      - speaker: NPC101
        emotion: calm
        text: "Jimmy，从头说。"

      - speaker: NPC107
        emotion: hopeless
        text: "他给我钱...答应给我合法身份...我只需要...杀死Webb..."

      - speaker: narration
        text: "[Zack沉默片刻]"

      - speaker: NPC101
        emotion: cold
        text: "你有家人。"

      - speaker: NPC107
        action: 眼中涌出泪水
        emotion: broken
        text: "Anna怀孕了...Brennan先生...我们住在贫民窟...我们是非法移民...我没有选择..."

      - speaker: NPC101
        emotion: understanding
        text: "我知道被逼到绝境是什么感觉。"

      - speaker: NPC107
        emotion: desperate
        text: "但您没有杀人...您还有机会...我没有了..."

  jimmy_final_choice:
    scene: SC1014
    scene_name: Jimmy家中
    description: Jimmy的最终选择

    lines:
      - speaker: narration
        text: "[Jimmy拿起厨房的刀，Zack立刻警觉]"

      - speaker: NPC101
        emotion: urgent
        text: "放下刀。"

      - speaker: NPC107
        emotion: broken
        text: "我做了最愚蠢的选择...我不配拥有这个家庭..."

      - speaker: NPC101
        emotion: persuasive
        text: "Jimmy，你的孩子需要父亲。"

      - speaker: NPC107
        emotion: hopeless
        text: "我的孩子需要的是好父亲...不是杀人犯..."

      - speaker: narration
        text: "[Jimmy把刀刺向自己，Zack冲上前]"

      - speaker: NPC101
        emotion: shocked
        text: "该死！"

      - speaker: narration
        text: "[Zack接住倒下的Jimmy]"

      - speaker: NPC107
        action: 声音微弱
        emotion: dying
        text: "Brennan先生...告诉Anna...我爱她..."

      - speaker: NPC101
        emotion: solemn
        text: "我会的。我会告诉她。"

      - speaker: NPC107
        emotion: peaceful
        text: "谢谢...谢谢您...您是...好人..."

      - speaker: narration
        text: "[Jimmy闭上眼睛]"

      - speaker: narration
        text: "[Zack坐在地上，抱着Jimmy的身体，长时间沉默]"

      - speaker: NPC101
        action: 闭上眼睛，深深地叹气
        emotion: bitter
        text: "该死...该死的芝加哥..."

  safe_discovery:
    scene: SC1005
    scene_name: Webb办公室
    description: 保险柜的秘密

    lines:
      - speaker: narration
        text: "[深夜，Zack站在保险柜前]"

      - speaker: NPC101
        emotion: frustrated
        text: "Webb的生日。酒吧开业日。都不对。"

      - speaker: NPC102
        emotion: thoughtful
        text: "也许是某个特殊的日期..."

      - speaker: narration
        text: "[门被轻轻推开，Anna站在门口，眼睛红肿]"

      - speaker: NPC108
        emotion: grieving
        text: "Brennan先生..."

      - speaker: NPC101
        emotion: gentle
        text: "Anna太太。"

      - speaker: NPC108
        action: 声音哽咽
        emotion: determined
        text: "我想帮忙...Jimmy他...留了遗书...说密码是我们的结婚纪念日..."

      - speaker: NPC101
        emotion: questioning
        text: "什么时候？"

      - speaker: NPC108
        action: 眼泪滑落
        emotion: tearful
        text: "1919年3月25日...圣帕特里克教堂..."

      - speaker: narration
        text: "[Zack输入：19190325]"

      - speaker: narration
        text: "[保险柜打开]"

  final_revelation:
    scene: SC1005
    scene_name: Webb办公室
    description: 最终揭露

    lines:
      - speaker: narration
        text: "[Zack从保险柜里拿出一把手枪、一封信和一盘录音带]"

      - speaker: NPC102
        emotion: curious
        text: "信是Webb写给Vivian的..."

      - speaker: NPC102
        action: 快速阅读
        emotion: surprised
        text: "他要把酒吧留给Vivian...还说他知道Rita可能是Whale派来的线人..."

      - speaker: NPC101
        emotion: analytical
        text: "Webb在反侦察。但没来得及。"

      - speaker: narration
        text: "[Zack放入录音带，按下播放]"

      - speaker: narration
        text: "[传来一个女人惊恐的声音]"

      - speaker: unknown_voice
        action: 充满恐惧和痛苦
        emotion: terrified
        text: "不...求求你们...放开我...不要...啊——！"

      - speaker: narration
        text: "[声音突然中断]"

      - speaker: narration
        text: "[Zack的脸色瞬间煞白，身体僵住]"

      - speaker: NPC101
        emotion: shocked
        text: "Margret..."

      - speaker: NPC102
        emotion: horrified
        text: "你的母亲？！"

      - speaker: NPC101
        action: 双手撑在桌上，整个人在颤抖
        emotion: shaken
        text: "我得回家...马上..."

      - speaker: NPC102
        emotion: determined
        text: "我跟你一起去！"

      - speaker: narration
        text: "[Zack和Emma快速离开]"

episode_end:
  message: "Episode 1 结束，待续..."
  next_episode_hint: "Whale的阴影笼罩着芝加哥，Zack的母亲陷入危险..."
'''

with codecs.open(os.path.join(base_path, 'loop6', 'ending.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop6_ending)

print('Loop 6 ending.yaml written successfully')

print('\n=== All corrupted dialog files fixed! ===')
