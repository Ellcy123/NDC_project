# -*- coding: utf-8 -*-
import codecs
import os

base_path = r'd:\NDC_project\可视化工具\数据源\Unit1\loops'

# ============== Loop 2 ==============
loop2 = '''# NDC Episode 1 - 循环2
# Morrison腐败调查
# 调查目标：Morrison为什么要陷害我？背后是谁指使？

loop_id: Unit1_Loop2
chapter: 1
loop_number: 2
title: Morrison腐败调查
title_en: Morrison Corruption Investigation

investigation_target: Morrison为什么要陷害我？背后是谁指使？
core_lie: Morrison声称凌晨0点半接警后立即赶到现场

# ===== 本循环场景总览 =====
scenes_overview:
  - scene: SC1001
    name: Rosa储藏室
    status: accessible
    type: npc
    note: 获取Morrison相关目击证词

  - scene: SC1003
    name: Tommy办公室
    status: accessible
    type: npc
    note: 获取Morrison线索

  - scene: SC1004
    name: 酒吧大堂
    status: accessible
    type: npc
    note: 指证地点

  - scene: SC1008
    name: Morrison家中客厅
    status: accessible
    type: npc
    note: Mrs. Morrison对话

  - scene: SC1009
    name: Morrison家中书房
    status: accessible
    type: search
    note: 搜索关键证据

  - scene: SC1010
    name: Webb会客室
    status: accessible
    type: search
    note: 寻找现场线索

  - scene: SC1011
    name: Vivian化妆室
    status: accessible
    type: npc
    note: 获取时间证词

  - scene: SC1012
    name: 芝加哥警局Morrison办公室
    status: accessible
    type: npc
    note: 指证地点

# ===== 本循环可获取证据 =====
available_evidences:
  # Morrison家中书房证据
  - EV1211  # Morrison夫人时间证词
  - EV1221  # 警用便携式现场勘验箱领用单据
  - EV1222  # 警用便携式现场勘验箱
  - EV1223  # Morrison的收据
  - EV1224  # "Whale"特殊纹样纸条
  - EV1225  # 记账本
  - EV1226  # 1920年世博会门票
  - EV1227  # Morrison的家庭照
  # Webb会客室证据
  - EV1209  # 警用便携式现场勘验箱压痕
  - EV1231  # Vivian和Webb合影
  # 证词
  - EV1241  # Vivian时间证词
  - EV1261  # Tommy路线证词
  - EV1271  # Rosa行为证词

# ===== 本循环可对话NPC =====
available_npcs:
  - NPC103  # Rosa
  - NPC104  # Morrison
  - NPC105  # Tommy
  - NPC106  # Vivian
  - NPC109  # Mrs. Morrison

# ===== 开篇 =====
opening:
  description: 前往Morrison家调查
  scenes:
    - id: morrison_home
      scene_id: SC1008
      name: Morrison家中客厅
      description: 与Morrison夫人对话，获取时间证词
      dialog_file: loop2/opening.yaml
      dialog_section: morrison_living_room

# ===== 自由环节 =====
free_phase:
  description: 调查Morrison和Webb周围人物
  scenes:
    - scene: SC1008
      type: npc
      npc: NPC109
      evidences:
        - id: EV1211

    - scene: SC1009
      type: search
      evidences:
        - id: EV1221
          location: 抽屉内
        - id: EV1222
          location: 书房柜子
        - id: EV1223
          location: 文件夹
        - id: EV1224
          location: 抽屉夹层
        - id: EV1225
          location: 抽屉内
        - id: EV1226
          location: 抽屉
        - id: EV1227
          location: 墙上相框

    - scene: SC1010
      type: search
      evidences:
        - id: EV1209
          location: 地板
          analyzable: true
          analysis_requires: EV1222
        - id: EV1231
          location: 桌面

    - scene: SC1011
      type: npc
      npc: NPC106
      evidences:
        - id: EV1241

    - scene: SC1003
      type: npc
      npc: NPC105
      evidences:
        - id: EV1261

    - scene: SC1001
      type: npc
      npc: NPC103
      evidences:
        - id: EV1271

# ===== 指证 =====
expose:
  scene: SC1012
  scene_name: 芝加哥警局Morrison办公室
  target: NPC104
  target_name: Morrison
  total_rounds: 4
  total_duration: 120秒
  design_concept: 通过时间线证据击破Morrison
  dialog_file: loop2/accusation.yaml

  rounds:
    - round: 1
      name: 时间线矛盾
      lie:
        content: 00:30我接到匿名电话，立即出警。因为案情紧急，最快速度赶到现场。
        source: Morrison声称临时接警
      required_evidences: [EV1211, EV1261, EV1241]
      evidence_names: [Morrison夫人时间证词, Tommy路线证词, Vivian时间证词]
      result: 30分钟路程只需15分钟，时间不对

    - round: 2
      name: 预谋行为
      lie:
        content: 警察提前领用装备很正常
        source: Morrison辩称巧合
      required_evidences: [EV1221]
      evidence_names: [警用便携式现场勘验箱领用单据]
      result: 证明Morrison提前一天领用现场勘验箱

    - round: 3
      name: 现场操作证据
      lie:
        content: 那可能是我检查现场时留下的
        source: Morrison试图解释
      required_evidences: [EV1209, EV1223]
      evidence_names: [警用便携式现场勘验箱压痕, 便携式现场勘验箱]
      result: 现场压痕与Morrison的勘验箱完全吻合

    - round: 4
      name: 职业签名致命击破
      lie:
        content: 可能是我之后检查时用的
        source: Morrison最后挣扎
      required_evidences: [EV1271]
      evidence_names: [Rosa行为证词]
      result: Rosa证明Morrison检查现场时没有使用任何工具

  truth_revealed: |
    Morrison迷晕Zack并栽赃给他Webb
    他欠疤面Tony 5000美元赌债，被"Whale"收买来栽赃Zack

# ===== 结尾 =====
ending:
  description: Morrison坦白"Whale"的存在
  dialog_file: loop2/ending.yaml
  transition_to: Unit1_Loop3
  next_objective: Webb做了什么生意惹上了"Whale"？收买Morrison的人是谁？
  transition_text: Morrison只是帮凶，真正杀死Webb的人是"Whale"。Webb做了什么？

# 循环总结
summary:
  duration: 约10分钟
  core_discoveries:
    - Morrison迷晕Zack并栽赃给他Webb
    - Morrison被赌债逼迫，被"Whale"收买
    - "Whale"是幕后黑手
    - Webb可能惹上了大人物
  next_target: Webb的生意和"Whale"的身份
'''

with codecs.open(os.path.join(base_path, 'loop2.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop2)
print('Loop 2 written successfully')

# ============== Loop 3 ==============
loop3 = '''# NDC Episode 1 - 循环3
# Tommy勒索网络
# 调查目标：Webb的真正生意是什么？

loop_id: Unit1_Loop3
chapter: 1
loop_number: 3
title: Tommy勒索网络
title_en: Tommy Blackmail Network

investigation_target: Webb的真正生意是什么？
core_lie: Tommy声称Webb只做私酒生意，没有其他业务

# ===== 本循环场景总览 =====
scenes_overview:
  - scene: SC1002
    name: 酒吧大堂
    status: accessible
    type: npc
    note: Tommy对话和指证地点

  - scene: SC1003
    name: Tommy办公室
    status: accessible
    type: search
    note: 搜索财务证据

  - scene: SC1005
    name: Webb办公室
    status: accessible
    type: search
    note: 搜索古董和勒索证据

  - scene: SC1007
    name: 蓝月亮酒吧歌舞厅
    status: accessible
    type: search
    note: 现场照片证据

# ===== 本循环可获取证据 =====
available_evidences:
  - EV1311  # Webb月收入财务报告
  - EV1313  # Tommy的详细工作记录
  - EV1320  # Webb古董收藏记录
  - EV1322  # Webb酒吧营业收入记录
  - EV1331  # 酒吧歌舞厅现场照片-欧洲油画
  - EV1332  # 酒吧歌舞厅现场照片-中国花瓶
  - EV1351  # Whale的神秘电话
  - EV1361  # Tommy的证词

# ===== 本循环可对话NPC =====
available_npcs:
  - NPC105  # Tommy

# ===== 开篇 =====
opening:
  description: 与Tommy初步对话，引出古董生意
  scenes:
    - id: tommy_chat
      scene_id: SC1002
      name: 酒吧大堂
      description: 与Tommy初步对话
      dialog_file: loop3/opening.yaml
      dialog_section: tommy_lobby_chat

# ===== 自由环节 =====
free_phase:
  description: 调查Webb的真正生意
  scenes:
    - scene: SC1003
      type: search
      evidences:
        - id: EV1311
          location: 文件柜
        - id: EV1313
          location: 抽屉
        - id: EV1322
          location: 账本

    - scene: SC1005
      type: search
      evidences:
        - id: EV1320
          location: 保险柜
      special_event:
        trigger: 搜索Webb办公室
        dialog_file: loop3/whale_call.yaml

    - scene: SC1007
      type: search
      evidences:
        - id: EV1331
          location: 墙上
        - id: EV1332
          location: 展示架

# ===== 指证 =====
expose:
  scene: SC1002
  scene_name: 酒吧大堂
  target: NPC105
  target_name: Tommy
  total_rounds: 3
  total_duration: 90秒
  design_concept: 三轮精准指证，揭露勒索网络
  dialog_file: loop3/accusation.yaml

  rounds:
    - round: 1
      name: 收入来源谎言
      lie:
        content: 收入全部来自酒类销售
        source: Tommy声称只做私酒
      required_evidences: [EV1311, EV1322]
      evidence_names: [Webb月收入财务报告, Webb酒吧营业收入记录]
      result: Tommy被迫承认还有古董买卖

    - round: 2
      name: 古董销售谎言
      lie:
        content: 古董是正常买卖，已经卖出去了
        source: Tommy转移话题
      required_evidences: [EV1331, EV1332]
      evidence_names: [酒吧歌舞厅现场照片-欧洲油画, 酒吧歌舞厅现场照片-中国花瓶]
      result: Tommy无法解释古董为何还在现场

    - round: 3
      name: 不知情谎言
      lie:
        content: 我只是做账的，不知道具体业务
        source: Tommy推卸责任
      required_evidences: [EV1313]
      evidence_names: [Tommy的详细工作记录]
      result: 彻底击破Tommy的谎言

  truth_revealed: |
    Webb经营勒索网络，用古董作为档案代号
    Tommy深度参与，管理整个勒索网络的账目
    Jimmy也参与勒索生意，可能知道更多

# ===== 结尾 =====
ending:
  description: Tommy供出Jimmy，引出下一循环
  dialog_file: loop3/ending.yaml
  transition_to: Unit1_Loop4
  next_objective: Jimmy和Webb的关系是什么？Webb勒索的"Whale"是谁？
  transition_text: Tommy说Jimmy也参与了Webb的生意...他可能知道更多。

# 循环总结
summary:
  duration: 约8分钟
  core_discoveries:
    - Webb经营勒索网络
    - 用古董作为档案代号
    - Tommy是核心账目管理者
    - Jimmy深度参与
  next_target: Jimmy和Whale的真实身份
'''

with codecs.open(os.path.join(base_path, 'loop3.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop3)
print('Loop 3 written successfully')

# ============== Loop 4 ==============
loop4 = '''# NDC Episode 1 - 循环4
# Jimmy秘密调查
# 调查目标：Jimmy和Webb的真实关系是什么？

loop_id: Unit1_Loop4
chapter: 1
loop_number: 4
title: Jimmy秘密调查
title_en: Jimmy Secret Investigation

investigation_target: Jimmy和Webb的真实关系是什么？
core_lie: Jimmy声称自己只是普通厨师，和Webb只是普通雇佣关系

# ===== 本循环场景总览 =====
scenes_overview:
  - scene: SC1002
    name: 酒吧大堂
    status: accessible
    type: npc
    note: Jimmy对话和指证地点

  - scene: SC1012
    name: Jimmy家中客厅
    status: accessible
    type: search
    note: 搜索Jimmy的秘密

  - scene: SC1013
    name: Jimmy厨房
    status: accessible
    type: search
    note: 搜索工作证据

# ===== 本循环可获取证据 =====
available_evidences:
  - EV1320  # Webb古董收藏记录
  - EV1341  # Vivian争吵目击证词
  - EV1411  # 伪装成陶泥的古董水壶
  - EV1421  # Jimmy家庭合照
  - EV1441  # Tommy目击证词

# ===== 本循环可对话NPC =====
available_npcs:
  - NPC107  # Jimmy
  - NPC108  # Anna

# ===== 开篇 =====
opening:
  description: 与Anna对话，获准进入搜查
  scenes:
    - id: jimmy_home
      scene_id: SC1012
      name: Jimmy家中客厅
      description: 与Anna对话，获准进入搜查
      dialog_file: loop4/opening.yaml
      dialog_section: jimmy_home_entrance

# ===== 自由环节 =====
free_phase:
  description: 调查Jimmy的秘密
  scenes:
    - scene: SC1012
      type: search
      npc: NPC108
      evidences:
        - id: EV1411
          location: 厨房架子
          puzzle_hint: 需要用水清洗才能看出真面目
        - id: EV1421
          location: 卧室墙上

    - scene: SC1013
      type: search
      evidences: []

    - scene: SC1002
      type: npc
      npc: NPC107
      evidences:
        - id: EV1441

# ===== 指证 =====
expose:
  scene: SC1002
  scene_name: 酒吧大堂
  target: NPC107
  target_name: Jimmy
  total_rounds: 3
  total_duration: 90秒
  design_concept: 逐步拆解Jimmy的三层防御谎言
  dialog_file: loop4/accusation.yaml

  rounds:
    - round: 1
      name: 身份关系欺骗
      lie:
        content: 我只是这里的厨师，Webb雇我就是做些杂事
        source: Jimmy伪装普通员工
      required_evidences: [EV1320, EV1411]
      evidence_names: [Webb古董收藏记录, 伪装成陶泥的古董水壶]
      result: Jimmy被迫改口承认拿过水壶

    - round: 2
      name: 盗窃行为欺骗
      lie:
        content: 我看它像是要扔掉的破陶器，所以随手拿了
        source: Jimmy编造理由
      required_evidences: [EV1441]
      evidence_names: [Tommy目击证词]
      result: Jimmy被迫承认与Webb关系密切

    - round: 3
      name: 关系和谐欺骗
      lie:
        content: 我们合作很紧密，一直很愉快，从来没有矛盾
        source: Jimmy伪装和谐
      required_evidences: [EV1341]
      evidence_names: [Vivian争吵目击证词]
      result: Jimmy被迫透露Whale的存在

  truth_revealed: |
    Jimmy与Webb关系密切，深度参与勒索生意
    存在一个叫"Whale"的超级危险目标
    Jimmy曾警告Webb不要勒索Whale

# ===== 结尾 =====
ending:
  description: Jimmy透露Whale的存在，引出Vivian线索
  dialog_file: loop4/ending.yaml
  transition_to: Unit1_Loop5
  next_objective: Vivian和Webb的关系是什么？她知道Whale是谁吗？
  transition_text: Jimmy说Vivian可能知道更多关于Whale的事...

# 循环总结
summary:
  duration: 约8分钟
  core_discoveries:
    - Jimmy与Webb关系密切
    - Jimmy参与勒索生意
    - Whale是超级危险人物
    - Jimmy曾警告Webb
  next_target: Vivian和Whale的真实身份
'''

with codecs.open(os.path.join(base_path, 'loop4.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop4)
print('Loop 4 written successfully')

# ============== Loop 5 ==============
loop5 = '''# NDC Episode 1 - 循环5
# Vivian悲惨过去
# 调查目标：Vivian和Webb的关系是什么？

loop_id: Unit1_Loop5
chapter: 1
loop_number: 5
title: Vivian悲惨过去
title_en: Vivian Tragic Past

investigation_target: Vivian和Webb的关系是什么？她为什么要杀Webb？
core_lie: Vivian声称自己和Webb只是普通的雇佣关系

# ===== 本循环场景总览 =====
scenes_overview:
  - scene: SC1011
    name: Vivian化妆室
    status: accessible
    type: search
    note: 搜索Vivian的秘密

  - scene: SC1007
    name: 蓝月亮酒吧歌舞厅
    status: accessible
    type: search
    note: 搜索舞台证据

# ===== 本循环可获取证据 =====
available_evidences:
  - EV1511  # Webb给Vivian的信
  - EV1512  # Vivian的日记
  - EV1521  # 舞台节目单
  - EV1531  # Vivian的计划书

# ===== 本循环可对话NPC =====
available_npcs:
  - NPC106  # Vivian

# ===== 开篇 =====
opening:
  description: 发现Vivian的秘密
  scenes:
    - id: vivian_room
      scene_id: SC1011
      name: Vivian化妆室
      description: 发现Vivian的秘密，引出她的悲惨过去
      dialog_file: loop5/opening.yaml
      dialog_section: vivian_dressing_room

# ===== 自由环节 =====
free_phase:
  description: 调查Vivian和Webb的关系
  scenes:
    - scene: SC1011
      type: search
      npc: NPC106
      evidences:
        - id: EV1511
          location: 化妆台抽屉
        - id: EV1512
          location: 衣柜暗格
        - id: EV1531
          location: 化妆包内

    - scene: SC1007
      type: search
      evidences:
        - id: EV1521
          location: 后台公告栏

# ===== 指证 =====
expose:
  scene: SC1011
  scene_name: Vivian化妆室
  target: NPC106
  target_name: Vivian
  total_rounds: 4
  total_duration: 120秒
  design_concept: 揭露Vivian的悲惨过去和杀人动机
  dialog_file: loop5/accusation.yaml

  rounds:
    - round: 1
      name: 关系谎言
      lie:
        content: 我和Webb只是普通的雇佣关系
        source: Vivian掩饰
      required_evidences: [EV1511]
      evidence_names: [Webb给Vivian的信]
      result: Vivian承认Webb曾承诺帮她赎身

    - round: 2
      name: 动机谎言
      lie:
        content: Webb虽然没有兑现承诺，但我不怨恨他
        source: Vivian伪装
      required_evidences: [EV1512]
      evidence_names: [Vivian的日记]
      result: Vivian承认对Webb有怨恨

    - round: 3
      name: 计划谎言
      lie:
        content: 我从来没有想过要伤害Webb
        source: Vivian否认
      required_evidences: [EV1531]
      evidence_names: [Vivian的计划书]
      result: Vivian承认有杀人计划

    - round: 4
      name: 行动谎言
      lie:
        content: 那天晚上我没有去Webb的办公室
        source: Vivian最后挣扎
      required_evidences: [EV1521]
      evidence_names: [舞台节目单]
      result: Vivian承认去了Webb办公室但门锁着

  truth_revealed: |
    Vivian被Webb欺骗多年，承诺赎身却从未兑现
    她确实有杀人计划，但那晚Webb的门是锁着的
    Jimmy可能才是真凶

# ===== 结尾 =====
ending:
  description: Vivian的证词指向Jimmy
  dialog_file: loop5/ending.yaml
  transition_to: Unit1_Loop6
  next_objective: Jimmy是真凶吗？他如何伪造时间线？
  transition_text: Vivian说那晚Webb的门是锁着的，但有人回应了她...那个人是Jimmy！

# 循环总结
summary:
  duration: 约10分钟
  core_discoveries:
    - Vivian被Webb欺骗多年
    - Vivian有杀人动机和计划
    - 但案发时Webb的门是锁着的
    - 有人模仿Webb的声音
  next_target: Jimmy是真凶，揭露他的诡计
'''

with codecs.open(os.path.join(base_path, 'loop5.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop5)
print('Loop 5 written successfully')

# ============== Loop 6 ==============
loop6 = '''# NDC Episode 1 - 循环6
# 真凶Jimmy
# 调查目标：Jimmy如何杀害Webb并伪造时间线？

loop_id: Unit1_Loop6
chapter: 1
loop_number: 6
title: 真凶Jimmy
title_en: The Real Killer Jimmy

investigation_target: Jimmy如何杀害Webb并伪造时间线？
core_lie: Jimmy声称案发时一直在厨房，有不在场证明

# ===== 本循环场景总览 =====
scenes_overview:
  - scene: SC1005
    name: Webb会客室
    status: accessible
    type: search
    note: 重新调查案发现场

  - scene: SC1007
    name: 蓝月亮酒吧歌舞厅
    status: accessible
    type: search
    note: 节目表演记录

  - scene: SC1013
    name: Jimmy厨房
    status: accessible
    type: search
    note: 送餐订单检查

  - scene: SC1014
    name: Jimmy家中
    status: accessible
    type: npc
    note: 最终指证地点

# ===== 本循环可获取证据 =====
available_evidences:
  - EV1621  # 窗外弹孔
  - EV1631  # 节目表演记录
  - EV1632  # 舞台道具箱中的手枪
  - EV1641  # Rosa关于Vivian携带可疑物品的证词
  - EV1651  # Vivian证词：当晚去敲Webb的门已锁
  - EV1661  # 厨房的送餐订单

# ===== 本循环可对话NPC =====
available_npcs:
  - NPC103  # Rosa
  - NPC106  # Vivian
  - NPC107  # Jimmy
  - NPC108  # Anna

# ===== 开篇 =====
opening:
  description: Webb会客室重新开放调查
  scenes:
    - id: webb_office
      scene_id: SC1005
      name: Webb会客室
      description: 警方封锁解除，重新调查现场
      dialog_file: loop6/opening.yaml
      dialog_section: webb_office_investigation

# ===== 自由环节 =====
free_phase:
  description: 收集Jimmy作案的关键证据
  scenes:
    - scene: SC1005
      type: search
      evidences:
        - id: EV1621
          location: 窗台
          analyzable: true

    - scene: SC1007
      type: search
      evidences:
        - id: EV1631
          location: 后台公告栏
        - id: EV1632
          location: 道具箱

    - scene: SC1013
      type: search
      evidences:
        - id: EV1661
          location: 工作台

    - scene: SC1001
      type: npc
      npc: NPC103
      evidences:
        - id: EV1641

    - scene: SC1011
      type: npc
      npc: NPC106
      evidences:
        - id: EV1651

# ===== 指证 =====
expose:
  scene: SC1014
  scene_name: Jimmy家中
  target: NPC107
  target_name: Jimmy
  total_rounds: 5
  total_duration: 150秒
  design_concept: 最终指证，揭露悲剧性的真凶
  dialog_file: loop6/accusation.yaml

  rounds:
    - round: 1
      name: 不在场证明谎言
      lie:
        content: 那天晚上11点到12点我一直在厨房工作，从来没有离开过
        source: Jimmy伪造不在场证明
      required_evidences: [EV1621]
      evidence_names: [窗外弹孔]
      result: 证明11:30的枪声是从室内射向外面的假枪声

    - round: 2
      name: 唯一枪声谎言
      lie:
        content: 当晚只有11:30那一声枪响
        source: Jimmy坚持
      required_evidences: [EV1631]
      evidence_names: [节目表演记录]
      result: 11:00-11:10的激烈鼓点可以掩盖任何枪声

    - round: 3
      name: 送餐谎言
      lie:
        content: 我在歌曲开始前下楼送餐
        source: Jimmy改口
      required_evidences: [EV1661]
      evidence_names: [厨房的送餐订单]
      result: 11点到11点30分没有任何送餐记录

    - round: 4
      name: 房间操作谎言
      lie:
        content: Vivian能证明11点时Webb还活着
        source: Jimmy依赖证人
      required_evidences: [EV1651]
      evidence_names: [Vivian证词]
      result: Jimmy模仿Webb声音骗走了Vivian

    - round: 5
      name: 动机谎言
      lie:
        content: 我根本没有动机杀Webb
        source: Jimmy最后挣扎
      required_evidences: [EV1641]
      evidence_names: [虎头额外收入]
      result: Jimmy被Whale收买，背叛了Webb

  truth_revealed: |
    Jimmy在11:00杀害Webb，利用音乐掩盖枪声
    11:05模仿Webb声音骗走Vivian
    11:30向窗外开枪制造假死亡时间
    12:00 Morrison按计划栽赃Zack
    Jimmy因为贫穷和身份问题被Whale收买

# ===== 结尾 =====
ending:
  description: Jimmy认罪后的悲剧结局
  dialog_file: loop6/ending.yaml
  transition_to: Episode2
  next_objective: Whale是谁？他为什么要杀Webb？
  transition_text: Jimmy死了，但Whale还在暗处...他到底是谁？

# 循环总结
summary:
  duration: 约15分钟
  core_discoveries:
    - Jimmy是真凶
    - 利用音乐掩盖枪声
    - 伪造死亡时间
    - 被Whale收买背叛Webb
  next_target: Episode 2 - Whale的真实身份
'''

with codecs.open(os.path.join(base_path, 'loop6.yaml'), 'w', encoding='utf-8') as f:
    f.write(loop6)
print('Loop 6 written successfully')

print('\n=== All loop files fixed! ===')
