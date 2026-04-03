# Audit Brief — Unit1 Loop 4

## 元信息
- Unit: Unit1
- Episode: EPI01
- Loop: 4
- 副标题: 厨师的秘密 / The Cook's Secret
- 说谎者: Jimmy (107)
- State 文件: 剧情设计/Unit1/state/loop4_state.yaml
- 对话文件数: 8 个（7 Talk + 1 Expose）

---

## 1. 玩家进入状态

### 已知事实 (known_facts)
来自 L1+L2+L3 的 post_expose_knowledge 累积：
- Rosa承认被Morrison胁迫，Morrison才是迷晕Zack的幕后指使者
- Rosa实际在后台走廊工作，目睹了部分案发过程
- Morrison因赌债被Whale收买$5000
- Whale要处理掉Webb和Zack
- Webb把Zack当"保险"
- Webb不只做私酒生意，还经营以古董交易为幌子的勒索网络
- Tommy是勒索网络的核心操作者，负责记账和伪装
- 同一件古董被反复"出售"给不同客户——本质是按月收取保护费
- Whale通过电话威胁Zack不要再查下去

### 已持有证据
L1-L3全部证据均在背包中。与L4直接相关的L3证据：
| ID | 名称 | 来源 Loop | 关联 |
|----|------|----------|------|
| 1320 | 古董鉴定报告 | L3 | L4合并用(1429的combineParameter之一) |

### 已解锁疑点
L1-L3疑点已解锁并清除

---

## 2. 本 Loop 信息分配

### 场景列表
| 场景 | ID | 可用 NPC | 搜证物品 | 场景功能 |
|------|-----|---------|---------|---------|
| 公园 | 1420 | Emma(102) | 无 | 开篇，讨论调查Jimmy |
| Jimmy厨房 | 1411 | 无 | 1411,1412,1413,1414 | 新解锁，关键搜证(水壶) |
| Jimmy家客厅 | 1413 | Anna(108) | 1421,1422,1423,1424,1425,1427,1428 | 新解锁，Anna首次出场，大量搜证 |
| Jimmy家卧室 | 1412 | 无 | 1429 | 新解锁，关键证据(鉴定报告) |
| Webb办公室 | 1408 | 无 | 无新证据 | 已解锁，可再次调查 |
| Tommy办公室 | 1405 | Tommy(105) | 无 | 已解锁，Tommy提供证词1054001 |
| Vivian化妆室 | 1407 | Vivian(106) | 无 | 已解锁，Vivian提供证词1063001 |
| Rosa储藏室 | 1401 | Rosa(103) | 无 | 已解锁，Rosa提供Jimmy钥匙信息 |
| 酒吧歌舞厅 | 1409 | Jimmy(107) | 无 | Jimmy对话+指证 |
| 酒吧大堂 | 1410 | Emma(102) | 无 | 与Emma对话 |

### 信息点分配
| NPC/搜证 | 信息点 | 类型 | 重要度 |
|---------|--------|------|--------|
| Jimmy厨房搜证 | 伪装成陶泥的古董水壶(1411→分析→1705) | 物证 | 核心 |
| Jimmy厨房搜证 | 厨房工作表(1414)——23:00-23:10只有Jimmy外出 | 物证 | 核心 |
| Jimmy家客厅搜证 | 额外收入记录(1424)——Whale+$5000 | 物证 | 核心 |
| Jimmy家客厅搜证 | Bennington陶器照片(1425) | 物证 | 核心 |
| Jimmy家卧室搜证 | 古董鉴定报告(1429)——Bennington价值$2,000 | 物证 | 核心 |
| Tommy对话 | 看到Jimmy从Webb办公室抱出古董水壶(证词1054001) | 证词 | 核心 |
| Vivian对话 | 目睹Jimmy和另一人争吵(证词1063001) | 证词 | 核心 |
| Anna对话 | Jimmy深夜不归、写遗书、有额外收入 | 对话信息 | 辅助 |
| Rosa对话 | Jimmy用钥匙进Webb会客室 | 对话信息 | 辅助 |

核心信息点总计: 7 个（合理范围内）

---

## 3. 新增证据

### 本 Loop 可获取的证据
| ID | 名称 | itemType | 获取方式 | 描述 | 关键属性 |
|----|------|----------|---------|------|---------|
| 1411 | 沾泥的水壶 | 3(物品) | Jimmy厨房搜证 | 表面被人为涂抹泥浆 | canAnalyzed=true→1705 |
| 1412 | Jimmy的奖状 | 环境叙事 | Jimmy厨房搜证 | 厨师身份展示 | — |
| 1413 | Jimmy的厨房手套 | 环境叙事 | Jimmy厨房搜证 | 日常工作道具 | — |
| 1414 | 厨房工作表 | 1(线索) | Jimmy厨房搜证 | 23:00-23:10仅Jimmy外出送餐 | Doubt1405 |
| 1421 | Jimmy家庭合照 | 环境叙事 | Jimmy家客厅搜证 | 家庭生活展示 | — |
| 1422 | Whale的联系暗号 | 环境叙事 | Jimmy家客厅搜证 | 暗示Jimmy与Whale联系 | — |
| 1423 | Jimmy给Anna的遗书 | 环境叙事 | Jimmy家客厅搜证 | 暗示Jimmy意识到危险 | — |
| 1424 | 额外收入记录 | 3(物品) | Jimmy家客厅搜证 | 标注Whale+$5000金额 | Doubt1404 |
| 1425 | Bennington陶器照片 | 3(物品) | Jimmy家客厅搜证 | 证明Jimmy认识Bennington陶器 | 1429合并材料 |
| 1427 | 英语学习书籍 | 环境叙事 | Jimmy家客厅搜证 | 移民背景暗示 | — |
| 1428 | 移民申请表 | 环境叙事 | Jimmy家客厅搜证 | 移民计划暗示 | — |
| 1429 | 古董鉴定报告 | 3(物品) | Jimmy家卧室搜证 | **注意**: canCombined=true, combineParameter=[1320,1425]→1426 | Expose R2用(直接使用1429) |
| 1705 | 沾泥的水壶(分析后) | 3(物品) | 派生自1411分析 | 清理后露出古董底色 | Expose R1用 |

**已知数据问题**:
- 1429(古董鉴定报告) 的 Describe 字段为"还没写描述"
- 1429 标记为 canCombined=true，combineParameter=[1320,1425]，存在合并输出 1426(鉴定报告)
- 但 state 文件标注 1429 为 Jimmy家卧室直接拾取，且 ExposeData id=14 直接使用 1429
- 存在矛盾：1429 究竟是直接拾取还是合并产物？当前配置表同时支持两种获取方式

### 本 Loop 可获取的证词
| ID | 说话人 | 证词原文 | 获取方式 |
|----|--------|---------|---------|
| 1054001 | Tommy(105) | "Tommy看到Jimmy从Webb办公室抱出一个疑似古董的陶土水壶" | Tommy对话触发(triggerType=1, triggerParam=107,1103,2100,2100) |
| 1063001 | Vivian(106) | "Vivian目睹Jimmy和另一人争吵后离开，两人脸色都很难看" | Vivian对话触发(triggerType=2, triggerParam=106,107) |
| 1071001 | Jimmy(107) | "Jimmy是蓝月亮的主厨" | Jimmy对话触发 |
| 1071006 | Jimmy(107) | "Jimmy声称自己从没干过坏事" | Jimmy对话触发——Expose谎言证词 |

---

## 4. 疑点与解锁

### 本 Loop 可解锁的疑点
| 疑点 ID | 描述 | 解锁条件 | 所需证据/证词 |
|---------|------|---------|-------------|
| 1401 | 这个水壶似乎和照片上的一样？ | item:1705 + item:1429 | 1705(分析后水壶)+1429(鉴定报告) |
| 1402 | Jimmy为什么拿这个水壶？ | testimony:1054001 | Tommy证词 |
| 1403 | Jimmy和Webb因为什么产生了矛盾？ | testimony:1063001 | Vivian证词 |
| 1404 | Jimmy只是厨师吗？ | testimony:1071001 + item:1424 | Jimmy证词+额外收入记录 |
| 1405 | Jimmy有不在场证明？ | item:1414 | 厨房工作表 |

clearDoubts: [1205, 1401, 1402, 1403, 1404]
注意: 1405(不在场证明)未被clear，保留到后续Loop

---

## 5. 指证设计

### 目标
- 指证对象: Jimmy (107)
- 指证证词: 1071006 "Jimmy声称自己从没干过坏事"
- ExposeData IDs: 13, 14, 15

### 谎言层级
| 轮次 | ExposeData.id | 谎言内容 | 正确证据(item[]) | 反驳逻辑 |
|------|---------------|---------|-----------------|---------|
| R1 | 13 | "我从没干过坏事——我就是个厨师" | 1054001(Tommy证词) + 1705(分析后水壶) | Tommy亲眼看到Jimmy偷拿水壶+水壶被人为伪装，"老实厨师"不会做这种事 |
| R2 | 14 | "那只是个普通陶壶，不值几个钱" | 1429(古董鉴定报告) | 报告明确标注Bennington陶器价值$2,000，Jimmy家有陶器照片(1425)，他完全知道价值 |
| R3 | 15 | "我和Webb之间没有任何问题！相处得很好！" | 1063001(Vivian证词) | Vivian亲眼目睹Jimmy和人激烈争吵——直接矛盾 |

### 指证验证逻辑（配置表）
- R1: testimony=1071006, item=[1054001, 1705]。注意 item[] 中包含证词ID(1054001)和物品ID(1705)——ExposeData的item[]字段可同时包含物品ID和证词ID
- R2: testimony=1071006, item=[1429]
- R3: testimony=1071006, item=[1063001]。item[]中使用的是证词ID
- 玩家从**完整背包**中选择，不存在"可选证据池"限制

### 指证后获得的新知识
- Jimmy不只是厨师，是Webb最信任的助手
- Jimmy知道古董水壶的真实价值并故意伪装
- Jimmy和Webb因Whale的勒索问题产生严重矛盾
- Jimmy警告Webb不要惹Whale但Webb不听
- Whale是一个极其危险的勒索目标
- Jimmy暗示Vivian也很可疑（L5铺垫）

---

## 6. 对话摘要

### Emma — emma_006 (pre-expose / 开篇)
- **文件路径**: `AVG/EPI01/Talk/loop4/emma_006.json`
- **对话结构**: 含分支(next指向102006400)
- **叙事时间点**: L3 expose后的过渡讨论
- **实际内容验证**: 第1句Emma说"这就是你的...律所？我以为我们在去垃圾填埋场的路上迷路了"——场景在Zack's Office，Emma嫌弃Zack办公室环境
- **关键对话节点**:
  1. [开场] Emma来到Zack办公室，嫌弃环境
  2. [方向引导] 讨论调查Jimmy的策略
- **NPC 情绪弧线**: 调侃 → 认真分析

### Jimmy — jimmy_001 (pre-expose / 自由探索)
- **文件路径**: `AVG/EPI01/Talk/loop4/jimmy_001.json`
- **对话结构**: 线性
- **叙事时间点**: 指证前
- **实际内容验证**: 第1句Zack说"你好，我是Zack Brennan，在调查Webb先生的案子。你是这里的厨师？"——场景在Jimmy厨房，首次见面
- **关键对话节点**:
  1. [开场] Zack以调查名义接近Jimmy
  2. [信息试探] 了解Jimmy与Webb的关系
- **NPC 情绪弧线**: 防备 → 否认

### Anna — anna_001 (pre-expose / 自由探索)
- **文件路径**: `AVG/EPI01/Talk/loop4/anna_001.json`
- **对话结构**: 线性
- **叙事时间点**: 指证前
- **实际内容验证**: 第1句Anna说"谁？"——门内传来谨慎女声，场景在Jimmy家客厅
- **关键对话节点**:
  1. [开场] Anna谨慎地应门
  2. [信息提供] Jimmy深夜不归、写遗书、额外收入、神秘电话
- **NPC 情绪弧线**: 戒备 → 焦虑倾诉

### Tommy — tommy_007 (pre-expose / 自由探索)
- **文件路径**: `AVG/EPI01/Talk/loop4/tommy_007.json`
- **对话结构**: 线性
- **叙事时间点**: 指证前（L3被击穿后的配合状态）
- **实际内容验证**: 第1句Tommy说"...这笔账不对...那个也不对..."——场景在Tommy办公室，Tommy正在埋头对账
- **关键对话节点**:
  1. [开场] Tommy在对账，被Zack打断
  2. [证词提供] 提供证词1054001：看到Jimmy从Webb办公室抱出古董水壶
  3. [信息补充] Webb对Jimmy的信任程度远超其他人

### Rosa — rosa_007 (pre-expose / 自由探索)
- **文件路径**: `AVG/EPI01/Talk/loop4/rosa_007.json`
- **对话结构**: 分支（3选1: Webb勒索/询问Jimmy/询问Vivian）
- **叙事时间点**: 指证前
- **实际内容验证**: 第1句Rosa说"Brennan先生……我能帮什么忙吗？"，script="branches"，3个选项
- **关键对话节点**:
  1. [开场] Rosa紧张地拖地
  2. [分支选择] 询问Jimmy情况——Rosa提供Jimmy用钥匙进Webb会客室的信息
- **NPC 情绪弧线**: 紧张 → 配合

### Vivian — vivian_005 (pre-expose / 自由探索)
- **文件路径**: `AVG/EPI01/Talk/loop4/vivian_005.json`
- **对话结构**: 线性
- **叙事时间点**: 指证前
- **实际内容验证**: 第1句Vivian说"又是你。我是不是得把化妆室租给你？按小时收费，还是包月？"——场景在Vivian化妆室
- **关键对话节点**:
  1. [开场] Vivian调侃Zack频繁来访
  2. [证词提供] 提供证词1063001：目睹Jimmy和另一人争吵
- **NPC 情绪弧线**: 调侃 → 回忆（认真）

### Expose — loop4_jimmy (指证)
- **文件路径**: `AVG/EPI01/Expose/loop4_jimmy.json`
- **叙事时间点**: 指证阶段
- **实际内容验证**: 第1句Zack说"Jimmy，我们聊聊"
- **谎言呈现顺序**: R1(从没干过坏事) → R2(水壶不值钱) → R3(和Webb没矛盾)
- **每轮结构**: 指控 → Jimmy辩解 → 出示证据 → 击破
- **击破后**: Jimmy崩溃承认，暗示Vivian可疑，为L5做铺垫

---

## 7. NPC 知识边界

### Jimmy (107) — 说谎者
- **active_topics**: 厨师工作（表面）、酒吧日常
- **blind_spots**: Webb被杀完整经过、Whale真实身份、Morrison被收买细节
- **withheld_topics**: 自己是Webb最信任的助手、古董水壶真实价值和伪装、与Webb因Whale问题的矛盾、Vivian与Webb的复杂关系
- **说谎内容**: "我从没干过坏事——我就是个厨师，老实做饭而已"
- **说谎动机**: 恐惧驱动——知道太多秘密，一旦说出会危及家人(Anna)安全

### Tommy (105) — 诚实（L3被击穿后配合）
- **active_topics**: Jimmy频繁出入Webb办公室、Jimmy拿走水壶、Webb对Jimmy的信任
- **blind_spots**: Jimmy为何拿走水壶、Jimmy和Webb矛盾原因、Whale真实身份
- **withheld_topics**: 无（已释然配合）
- **说谎内容**: 无

### Vivian (106) — 诚实
- **active_topics**: 目睹Jimmy和人争吵、Jimmy近期脾气变化
- **blind_spots**: 争吵对象身份、争吵原因、Jimmy和Webb矛盾、古董水壶
- **withheld_topics**: 无
- **说谎内容**: 无

### Rosa (103) — 诚实
- **active_topics**: Jimmy用钥匙进Webb会客室、Jimmy在酒吧工作多年
- **blind_spots**: Jimmy为何有钥匙、Jimmy在会客室做什么、勒索网络细节
- **withheld_topics**: 无

### Anna (108) — 诚实（新角色）
- **active_topics**: Jimmy深夜不归、遗书、额外收入、神秘电话、学英语
- **blind_spots**: Jimmy在勒索网络中的角色、Whale身份、Webb死亡细节、水壶价值
- **withheld_topics**: 无
- **说谎内容**: 无

### Emma (102) — 诚实/引导角色
- **active_topics**: 调查策略、Webb勒索网络分析、Jimmy可能知道Whale线索
- **blind_spots**: Jimmy是Webb助手、水壶价值、Jimmy与Webb矛盾、Jimmy家情况

---

## 8. 前后衔接

### 从前序 Loop 继承的悬念
- Whale到底是谁？（L2/L3留悬念，L4部分推进）
- Webb身边更亲近的人还隐瞒了什么？（L3 expose后引出，L4主要解答）
- Tommy暗示"真正可怕的不是Webb，而是Whale"（L3留悬念）

### 本 Loop 应解答的问题
- Jimmy只是厨师吗？→ 通过指证揭示为Webb最信任的助手
- 古董水壶的伪装意味着什么？→ 揭示Jimmy知道真实价值并故意伪装
- Jimmy和Webb之间发生了什么？→ 因Whale勒索问题产生严重矛盾

### 本 Loop 埋下的新悬念
- Vivian到底知道什么？（Jimmy暗示，L5回收）
- Whale为什么如此危险？（持续悬念，L5-L6回收）
- Jimmy的不在场证明问题——23:00-23:10外出送餐（Doubt1405未clear，后续回收）

### 情绪弧线设计
- 设计情绪: 同情→纠结（发现Jimmy不是坏人，而是被迫的参与者）
- 全局功能: 转折（从"追查黑帮"转向"被迫的恶"）

### 特殊机制
- **古董水壶分析**: 1411(沾泥水壶) → 分析 → 1705(分析后)
- **古董鉴定报告合并**: 1429标记canCombined=true, combineParameter=[1320,1425]→1426，但同时可直接拾取于Jimmy家卧室
