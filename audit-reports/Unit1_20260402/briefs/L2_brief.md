# Audit Brief — Unit1 Loop 2

## 元信息
- Unit: Unit1
- Episode: EPI01
- Loop: 2
- 副标题: 腐败的警徽 / The Corrupt Badge
- 说谎者: Morrison (104)
- State 文件: 剧情设计/Unit1/state/loop2_state.yaml
- 对话文件数: 10 个 (7 Talk + 1 Expose + 2 repeat)

---

## 1. 玩家进入状态

### 已知事实 (known_facts)
来自 L1 post_expose_knowledge：
- Morrison本人在走廊迷晕Zack并拖入会客室，Morrison不知道Rosa在场
- Rosa实际在后台走廊工作，目睹了Morrison迷晕Zack的全过程
- Rosa事后自行捡走掉落的毛巾藏匿在储物间，Morrison不知情
- Rosa出于恐惧+经济压力选择沉默
- 真正需要调查的对象转向Morrison

### 已持有证据
| ID | 名称 | 来源 Loop | 简述 |
|----|------|----------|------|
| 1111 | 悬赏通缉令 | L1 | 环境叙事 |
| 1112 | Miguel的照片 | L1 | Rosa家庭背景 |
| 1113 | 巨额医药单 | L1 | Rosa经济压力 |
| 1114→1701 | 毛巾→有甜腻气味的毛巾 | L1 | 氯仿证据 |
| 1115 | 工作记录卡 | L1 | Rosa工作地点 |
| 1121 | 氯仿瓶 | L1 | 迷晕手段 |
| 1122→1702 | 拖痕→沉重的拖痕 | L1 | 搬运证据 |

### 已解锁疑点
| 疑点 ID | 描述 | 状态 |
|---------|------|------|
| 1101 | Rosa当晚究竟在哪工作？ | ✓ L1已解决 |
| 1102 | 毛巾为什么有奇怪的味道？ | ✓ L1已解决 |
| 1103 | 是谁拖得我？ | ✓ L1已解决 |
| 1104 | 11:30的枪声是案发时间吗？ | 开放(遗留至L6) |

---

## 2. 本 Loop 信息分配

### 场景列表
| 场景 | ID | 可用 NPC | 搜证物品 | 场景功能 |
|------|----|---------|---------|---------|
| 酒吧外街道 | 1217 | Emma | 无 | 🎬开篇：Emma汇报，Morrison成为目标 |
| Morrison家客厅 | 1205 | Mrs. Morrison | 无 | 🔓新解锁：获取Morrison当晚行踪 |
| Morrison家书房 | 1206 | 无 | 1221勘验箱领用单, 1222勘验箱实体, 1224赌债, 1225Whale字条, 1226筹码, 1227头条新闻, 1228奖章 | 🔓新解锁：核心搜证(6件) |
| Webb会客室 | 1204 | 无 | 1209现场压痕, 1231合影 | 🔓新解锁：搜证 |
| Vivian化妆室 | 1207 | Vivian | 无 | 对话：Morrison到达时间 |
| Tommy办公室 | 1103 | Tommy | 无 | 已解锁：车程信息 |
| Rosa储藏室 | 1101 | Rosa | 无 | 已解锁：Morrison现场行为 |
| Morrison办公室 | 1118 | Morrison | 无 | ⚔️指证场所 |
| 酒吧大堂 | 1210 | 无 | 无 | 已解锁(无新内容) |

### 信息点分配
| NPC/搜证 | 信息点 | 类型 | 重要度 |
|---------|--------|------|--------|
| Mrs. Morrison对话 | Morrison 00:30离家 | 对话信息 | 辅助(时间线) |
| Tommy对话 | Morrison家到酒吧开车最多15分钟 | 证词(1052002) | 核心(Expose R1) |
| Vivian对话 | Morrison午夜12点到达现场 | 证词(1061001) | 核心(Expose R1) |
| Rosa对话 | Morrison检查现场未使用任何工具 | 证词(1032003) | 核心(Expose R4) |
| Morrison书房搜证 | 勘验箱领用单(案发前一天领取) | 物证(1221) | 核心(Expose R2) |
| Morrison书房搜证 | 勘验箱实体 | 物证(1222) | 核心(与1209对比→1703) |
| Morrison书房搜证 | 赌债5000+Whale字条+筹码 | 环境叙事 | 辅助(动机) |
| Webb会客室搜证 | 现场压痕(→分析后1703) | 物证(1209) | 核心(Expose R3) |

核心信息点总计: 8 个 ✓ (≤8-10)

---

## 3. 新增证据

### 本 Loop 可获取的证据
| ID | 名称 | 类型 | 获取方式 | 描述 | 分析后 |
|----|------|------|---------|------|--------|
| 1209 | 箱子的压痕 | 线索(itemType=1) | Webb会客室搜证 | 四方形压痕 | →1703 尺寸和勘验箱完全吻合 |
| 1221 | 勘验箱领用单 | 物证(itemType=3) | Morrison书房搜证 | 案发前一天19:30领取 | - |
| 1223 | 便携式勘验箱 | 线索(itemType=1) | Morrison书房搜证 | 测量设备随时可用 | - |
| 1224 | 催命的赌债 | 环境(itemType=2) | Morrison书房搜证 | 欠疤面Tony 5000美元 | - |
| 1225 | Whale的字条 | 环境(itemType=2) | Morrison书房搜证 | $5000已到账的指示 | - |
| 1226 | 磨损的筹码 | 环境(itemType=2) | Morrison书房搜证 | 赌场筹码，"最后一次" | - |
| 1227 | 过期的头条新闻 | 环境(itemType=2) | Morrison书房搜证 | Miller集团遭勒索的新闻 | - |
| 1228 | 闪亮的奖章 | 环境(itemType=2) | Morrison书房搜证 | 英勇服务奖章，形成反差 | - |
| 1231 | 不相称的合影 | 环境(itemType=2) | Webb会客室搜证 | Vivian与Webb的甜蜜合影 | - |

### 本 Loop 可获取的证词
| ID | 说话人 | 原文摘要 | 类型 |
|----|--------|---------|------|
| 1032001 | Rosa | Rosa大约12点半躲进了储藏室 | 时间线补充 |
| 1032003 | Rosa | Morrison空着手进出现场，没使用任何工具 | 核心(Expose R4) |
| 1041002 | Morrison | Morrison自称蓝月亮属于他的管辖范围 | 基础信息 |
| 1041003 | Morrison | Morrison称11:30接到匿名线报后立刻赶往现场 ⚠谎言 | 核心(指证对象) |
| 1041004 | Morrison | Morrison声称与Webb仅限公事公办 | 基础信息 |
| 1052001 | Tommy | Tommy曾去Morrison家送东西 | 辅助 |
| 1052002 | Tommy | 从Morrison家到酒吧开车最多15分钟 | 核心(Expose R1) |
| 1061001 | Vivian | Morrison在午夜12点到达现场 | 核心(Expose R1) |

---

## 4. 疑点与解锁

### 本 Loop 可解锁的疑点
| 疑点 ID | 描述 | 解锁条件 | 本Loop解决? |
|---------|------|---------|-----------|
| 1201 | Morrison到酒吧需要多久？ | testimony:1052002 + testimony:1041003 + testimony:1061001 | ✓ 指证解决 |
| 1202 | 为什么案发前一天就领了勘验设备？ | item:1221 | ✓ 指证解决 |
| 1203 | 压痕是什么时候造成的？ | item:1703 + testimony:1032003 | ✓ 指证解决 |
| 1204 | Morrison欠了谁的钱？ | item:1224 | 环境叙事疑点 |
| 1205 | Whale是谁？ | item:1225 | 伏笔(后续Loop) |

---

## 5. 指证设计

### 目标
- 指证对象: Morrison (104)
- 指证场景: Morrison办公室 (1118)
- 总轮数: 4

### 谎言层级
| 轮次 | 谎言内容 | 正确证据 | 反驳逻辑 |
|------|---------|---------|---------|
| R1 | "11:30接到线报后立刻赶往" | 1052002(Tommy证词:车程15分钟) + 1061001(Vivian证词:12:00到达) | 11:30+15分钟=最迟11:45到，实际12:00到→15分钟空白无法解释 |
| R2 | 继续硬撑时间说辞 | 1221 勘验箱领用单 | 案发前一天就领了设备→预谋非临时 |
| R3 | "带勘验箱到现场有什么问题？" | 1703 箱子压痕(分析后) | 勘验箱底部与现场压痕完全吻合→带箱去过现场 |
| R4 | 最后挣扎 | 1032003(Rosa证词:未使用测量工具) | 提前领+带到现场+不使用→勘验箱不是用来办案的 |

### 指证后获得的新知识 (post_expose_knowledge)
- Morrison承认迷晕Zack并栽赃
- Morrison因赌债被Whale收买，收了$5000
- Whale要处理掉Webb和他的"保险侦探"Zack
- Webb约Zack去酒吧不是给案子，而是把Zack当"保险"
- Morrison是Whale的工具人——走投无路被利用

---

## 6. 对话摘要

### Mrs. Morrison — mrsmorrison_001.json
- **文件路径**: `AVG/EPI01/Talk/loop2/mrsmorrison_001.json`
- **对话结构**: 线性
- **关键对话节点**:
  1. [关键信息] Morrison案发当晚00:30离家，说要处理工作
  2. [关键信息] Morrison最近脾气越来越差，经常半夜出门
- **NPC 情绪**: 困惑但不设防

### Tommy — tommy_003.json
- **文件路径**: `AVG/EPI01/Talk/loop2/tommy_003.json`
- **关键对话节点**:
  1. [证词获取] 曾去Morrison家送东西(→1052001)
  2. [证词获取] 从Morrison家到酒吧开车最多15分钟(→1052002)——关键时间线证据

### Vivian — vivian_001.json
- **文件路径**: `AVG/EPI01/Talk/loop2/vivian_001.json`
- **关键对话节点**:
  1. [证词获取] Morrison在午夜12点到达现场(→1061001)——关键时间线证据
- **NPC 情绪**: 悲伤中配合

### Rosa — rosa_003.json
- **文件路径**: `AVG/EPI01/Talk/loop2/rosa_003.json`
- **关键对话节点**:
  1. [证词获取] Rosa大约12:30躲进储藏室(→1032001)
  2. [证词获取] Morrison空着手进出现场(→1032003)——关键指证证据
- **NPC 态度转变**: L1被指证→L2戴罪立功，愿意配合

### Morrison — morrison_002.json
- **文件路径**: `AVG/EPI01/Talk/loop2/morrison_002.json`
- **功能**: 指证前Morrison的常规对话，获取谎言证词1041003

### Emma — emma_004.json
- **文件路径**: `AVG/EPI01/Talk/loop2/emma_004.json`
- **功能**: 开篇引导，汇报Rosa供词，确认Morrison为目标

### Expose — loop2_morrison.json
- **文件路径**: `AVG/EPI01/Expose/loop2_morrison.json`
- **谎言呈现顺序**: R1(时间线) → R2(领用单) → R3(压痕) → R4(Rosa证词)
- **击破后反应**: Morrison彻底崩溃，承认被Whale收买，揭露Webb约Zack的真实目的

---

## 7. NPC 知识边界

### Morrison (104) — 指证对象
- **active_topics**: 自己的职权范围、案发当晚说辞
- **blind_spots**: Zack已掌握多少证据、Rosa供出了哪些细节
- **withheld_topics**: 被Whale收买、迷晕Zack并栽赃、赌债$5000、Webb约Zack的真实目的
- **说谎内容**: "11:30接到匿名线报后立刻赶往现场"
- **说谎动机**: 掩盖预谋行为，用职务权威挡驾

### Mrs. Morrison (110)
- **active_topics**: Morrison当晚出门时间、最近行为异常
- **blind_spots**: Morrison被收买、迷晕Zack、赌债
- **withheld_topics**: 无

### Tommy (105)
- **active_topics**: Morrison家到酒吧的车程、曾去Morrison家
- **blind_spots**: Morrison被收买、Webb内幕
- **withheld_topics**: 无

### Vivian (106)
- **active_topics**: Morrison到达现场时间、Webb被杀当晚情况
- **blind_spots**: Morrison迷晕Zack、Morrison与Whale交易
- **withheld_topics**: 无

### Rosa (103) — L1后态度转变
- **active_topics**: Morrison检查现场的行为细节
- **blind_spots**: Morrison赌债、Whale交易、Webb约Zack目的
- **withheld_topics**: 无（L1已坦白，L2配合调查）

---

## 8. 前后衔接

### 从 L1 继承的悬念
- Morrison为什么要迷晕Zack？→ 本Loop解答
- 11:30的枪声意味着什么？→ 遗留至L6
- Rosa暗示的"他们"是谁？→ 后续Loop

### 本 Loop 应解答的问题
- Morrison的动机？→ 赌债被Whale收买
- Morrison有预谋吗？→ 勘验箱领用单证明预谋
- Zack为什么在酒吧？→ Webb把Zack当"保险"

### 本 Loop 埋下的新悬念
- Whale是谁？为什么要处理Webb和Zack？→ 后续Loop
- Webb的"保险"是什么意思？→ 后续Loop
- Morrison只是工具人，真正的幕后是谁？→ 后续Loop

### 情绪弧线设计
- 设计情绪: 愤怒→无力
- 全局功能: 升级——从个人恩怨升级到权力介入，发现更大的阴谋
