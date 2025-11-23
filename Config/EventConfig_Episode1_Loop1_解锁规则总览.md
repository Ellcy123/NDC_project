# Episode 1 循环1 事件系统解锁规则总览

## 📋 文档说明

本文档详细列出了第一章第一循环（Rosa现场目击指证）中所有事件的**解锁条件**和**解锁内容**，方便策划和程序员快速查阅。

---

## 🎬 循环开始阶段

### 事件1：EVE_LOOP001_START - 循环1开始

**解锁条件**：
- 开场AVG完成（OPENING_AVG_COMPLETE）

**解锁内容**：
- ✅ 场景：SC102（歌舞厅外的街道）
- ✅ 任务：TAS_CH001_MAIN（主案件：蓝月亮歌舞厅谋杀案）
- ✅ 任务：TAS_LOOP001_PHASE（循环目标：调查Rosa的证词）
- ✅ 任务：TAS_LOOP001_GOAL_01（行动目标：前往歌舞厅外的街道）

**提示文本**：
- 中文："前往歌舞厅外的街道"
- 英文："Go to the street outside the ballroom"

---

### 事件2：EVE_ENTER_SC102 - 进入街道场景

**解锁条件**：
- 进入街道场景（SCENE_SC102_ENTER）

**解锁内容**：
- ✅ 对话：D_EMMA_TALK_START（Emma对话开始）
- ✅ 任务：TAS_LOOP001_GOAL_02（行动目标：与Emma对话）

**提示文本**：
- 中文："与Emma对话"
- 英文："Talk to Emma"

---

### 事件3：EVE_EMMA_TALK_COMPLETE - Emma对话完成

**解锁条件**：
- Emma对话完成（DIALOGUE_D045_COMPLETE）

**解锁内容**：
- ✅ 场景：SC103（Rosa储藏室）
- ✅ 场景：SC104（歌舞厅一楼走廊）
- ✅ 场景：SC105（Tommy办公室）
- ✅ 场景：SC106（酒吧大堂）
- ✅ 任务：TAS_LOOP001_GOAL_03（行动目标：调查Rosa的储藏室）
- ✅ 任务：TAS_LOOP001_DOUBT_01（疑点：Morrison为何如此确定我是凶手？）
- ✅ 任务：TAS_LOOP001_DOUBT_02（疑点：Rosa的证词有什么破绽？）

**提示文本**：
- 中文："多个场景已解锁，开始调查！"
- 英文："Multiple scenes unlocked, start investigating!"

---

## 🔍 证据收集阶段（储藏室）

### 事件4：EVE_COLLECT_EV111 - 收集证据111（通缉令）

**解锁条件**：
- 收集证据111（EV111_COLLECTED）

**解锁内容**：
- ✅ 提示：环境叙事证据 - 了解芝加哥黑帮背景

**提示文本**：
- 中文："获得证据：芝加哥警局通缉令"
- 英文："Evidence obtained: Chicago Police Wanted Poster"

---

### 事件5：EVE_COLLECT_EV112 - 收集证据112（女儿照片）

**解锁条件**：
- 收集证据112（EV112_COLLECTED）

**解锁内容**：
- ✅ 提示：密码提示 - 照片背面的生日日期可能有用
- ✅ 谜题：PUZZLE_TOOLBOX_PASSWORD（工具箱密码谜题激活）

**提示文本**：
- 中文："获得证据：Rosa的女儿照片（生日：0915）"
- 英文："Evidence obtained: Rosa's daughter photo (Birthday: 0915)"

**特殊说明**：
- 这个证据会解锁密码谜题
- 玩家需要用生日"0915"作为工具箱密码

---

### 事件6：EVE_COLLECT_EV113 - 收集证据113（医疗账单）

**解锁条件**：
- 收集证据113（EV113_COLLECTED）

**解锁内容**：
- ✅ 提示：环境叙事证据 - Rosa的家庭困境

**提示文本**：
- 中文："获得证据：Rosa的医院就诊清单"
- 英文："Evidence obtained: Rosa's hospital bill"

---

### 事件7：EVE_SOLVE_TOOLBOX_PUZZLE - 解开工具箱密码

**解锁条件**：
- 工具箱密码谜题解开（PUZZLE_TOOLBOX_SOLVED）
- 正确密码：0915

**解锁内容**：
- ✅ 证据：EV114（沾有氯仿的毛巾）
- ✅ 证据：EV115（工作记录卡）

**提示文本**：
- 中文："工具箱已打开！"
- 英文："Toolbox unlocked!"

**特殊说明**：
- 这两个证据是指证Rosa的核心证据
- 必须解开密码才能获得

---

### 事件8：EVE_COLLECT_EV114 - 收集证据114（氯仿毛巾）

**解锁条件**：
- 收集证据114（EV114_COLLECTED）
- 前置条件：工具箱密码已解开

**解锁内容**：
- ✅ 任务：TAS_LOOP001_DOUBT_03（疑点：谁把我迷晕了？）
- ✅ 提示：关键证据 - 这条毛巾可以指证Rosa

**提示文本**：
- 中文："获得关键证据：沾有氯仿的毛巾"
- 英文："Key evidence obtained: Chloroform-stained towel"

**特殊说明**：
- 需要分析证据：闻嗅后发现氯仿味道
- 第二轮指证的关键证据

---

### 事件9：EVE_COLLECT_EV115 - 收集证据115（工作记录卡）

**解锁条件**：
- 收集证据115（EV115_COLLECTED）
- 前置条件：工具箱密码已解开

**解锁内容**：
- ✅ 提示：关键证据 - 这可以揭穿Rosa的地点谎言

**提示文本**：
- 中文："获得关键证据：工作记录卡"
- 英文："Key evidence obtained: Work schedule card"

**特殊说明**：
- 记录卡显示Rosa应该在后台走廊工作，不是地下室
- 第一轮指证的关键证据

---

### 事件10：EVE_SC103_CLEARED - 储藏室搜证完成

**解锁条件**：
- 储藏室所有证据收集完成（SCENE_SC103_ALL_EVIDENCE_COLLECTED）
- 包括：EV111、EV112、EV113、EV114、EV115

**解锁内容**：
- ✅ 任务：TAS_LOOP001_GOAL_04（行动目标：调查歌舞厅一楼走廊）

**提示文本**：
- 中文："储藏室调查完毕，前往走廊继续调查"
- 英文："Storage room investigation complete, proceed to corridor"

---

## 🔍 证据收集阶段（走廊）

### 事件11：EVE_COLLECT_EV121 - 收集证据121（氯仿瓶）

**解锁条件**：
- 收集证据121（EV121_COLLECTED）

**解锁内容**：
- ✅ 提示：关键证据 - 与毛巾配合，可以证明迷晕手法

**提示文本**：
- 中文："获得关键证据：氯仿瓶"
- 英文："Key evidence obtained: Chloroform bottle"

**特殊说明**：
- 在走廊垃圾桶中发现
- 第二轮指证的关键证据（配合EV114使用）

---

### 事件12：EVE_COLLECT_EV122 - 收集证据122（拖拽痕迹）

**解锁条件**：
- 收集证据122（EV122_COLLECTED）

**解锁内容**：
- ✅ 提示：关键证据 - 这可以否定Rosa的自认

**提示文本**：
- 中文："获得关键证据：地板拖拽痕迹"
- 英文："Key evidence obtained: Floor drag marks"

**特殊说明**：
- 需要分析证据：压痕较深，需要150磅力量
- 第三轮指证的关键证据

---

### 事件13：EVE_SC104_CLEARED - 走廊搜证完成

**解锁条件**：
- 走廊所有证据收集完成（SCENE_SC104_ALL_EVIDENCE_COLLECTED）
- 包括：EV121、EV122

**解锁内容**：
- ✅ 任务：TAS_LOOP001_GOAL_05（行动目标：与Tommy对话）

**提示文本**：
- 中文："走廊调查完毕，前往Tommy办公室"
- 英文："Corridor investigation complete, proceed to Tommy's office"

---

## 💬 对话阶段

### 事件14：EVE_TOMMY_TALK_COMPLETE - Tommy对话完成

**解锁条件**：
- Tommy对话完成（DIALOGUE_TOMMY_001_COMPLETE）

**解锁内容**：
- ✅ 证据：EV133（Tommy时间证词：关于枪声的反应）
- ✅ 任务：TAS_LOOP001_DOUBT_04（疑点：Tommy为什么说看到警察进入后台？）

**提示文本**：
- 中文："获得证词：Tommy关于枪声的反应"
- 英文："Testimony obtained: Tommy's reaction to gunshot"

**特殊说明**：
- 这个证词将在循环6使用
- 用于证明枪声的时间点

---

## ✅ 准备指证阶段

### 事件15：EVE_ALL_EVIDENCES_COLLECTED - 所有证据收集完成

**解锁条件**（多条件，全部满足）：
- ✅ 工作记录卡已收集（EV115_COLLECTED）
- ✅ 氯仿毛巾已收集（EV114_COLLECTED）
- ✅ 氯仿瓶已收集（EV121_COLLECTED）
- ✅ 拖拽痕迹已收集（EV122_COLLECTED）
- ✅ Tommy证词已收集（EV133_COLLECTED）

**解锁内容**：
- ✅ 任务：TAS_LOOP001_GOAL_06（行动目标：指证Rosa）

**提示文本**：
- 中文："证据已齐全，可以指证Rosa了！"
- 英文："All evidence collected, ready to expose Rosa!"

**特殊效果**：
- 🔆 高亮任务：TAS_LOOP001_PHASE（循环目标任务）
- 📊 更新进度：5/5 (100%)
- ⚠️ 这是关键节点，提示玩家可以进行指证了

---

## ⚔️ 指证阶段

### 事件16：EVE_ROSA_EXPOSE_ROUND1_SUCCESS - 指证Rosa第一轮成功

**解锁条件**：
- 第一轮指证成功（EXPOSE_ROSA_ROUND1_SUCCESS）
- 玩家使用正确证据：EV115（工作记录卡）

**解锁内容**：
- ✅ 对话：D_ROSA_ROUND1_RESULT（Rosa承认在后台走廊工作）

**提示文本**：
- 中文："第一轮指证成功：Rosa承认在后台走廊工作"
- 英文："Round 1 success: Rosa admits working in backstage corridor"

**指证逻辑**：
- **Rosa的谎言**："我在地下室酒窖工作"
- **使用证据**：工作记录卡（显示她应该在后台走廊）
- **结果**：Rosa被迫修正说法，承认地点说谎

---

### 事件17：EVE_ROSA_EXPOSE_ROUND2_SUCCESS - 指证Rosa第二轮成功

**解锁条件**：
- 第二轮指证成功（EXPOSE_ROSA_ROUND2_SUCCESS）
- 玩家使用正确证据：EV114（氯仿毛巾）+ EV121（氯仿瓶）

**解锁内容**：
- ✅ 对话：D_ROSA_ROUND2_RESULT（Rosa承认使用氯仿迷晕Zack）

**提示文本**：
- 中文："第二轮指证成功：Rosa承认使用氯仿迷晕Zack"
- 英文："Round 2 success: Rosa admits using chloroform"

**指证逻辑**：
- **Rosa的新谎言**："我在后台专心清洁，什么都没看到"
- **使用证据**：氯仿毛巾 + 氯仿瓶（证明迷晕手法）
- **结果**：Rosa心理防线崩溃，承认使用氯仿迷晕Zack

---

### 事件18：EVE_ROSA_EXPOSE_ROUND3_SUCCESS - 指证Rosa第三轮成功

**解锁条件**：
- 第三轮指证成功（EXPOSE_ROSA_ROUND3_SUCCESS）
- 玩家使用正确证据：EV122（拖拽痕迹）

**解锁内容**：
- ✅ 对话：D_ROSA_ROUND3_RESULT（Rosa供出Morrison是幕后黑手）

**提示文本**：
- 中文："第三轮指证成功：Rosa供出Morrison是幕后黑手"
- 英文："Round 3 success: Rosa reveals Morrison as mastermind"

**指证逻辑**：
- **Rosa的自认**："是我把您拖到办公室的"
- **使用证据**：拖拽痕迹（需要150磅力量，Rosa只有120磅）
- **结果**：Rosa供认真相 - Morrison是幕后黑手

**特殊说明**：
- ⚠️ **打断式事件**（ifInterrupt=1）
- 立即播放Rosa供认对话，暂停其他流程

---

### 事件19：EVE_ROSA_EXPOSE_COMPLETE - Rosa指证完成

**解锁条件**：
- Rosa指证成功（EXPOSE_ROSA_SUCCESS）
- 三轮指证全部完成

**解锁内容**：
- ✅ 对话：D_LOOP001_ENDING（循环1结束对话）
- ✅ 循环：LOOP002（循环2解锁）

**提示文本**：
- 中文："循环1完成！Morrison成为新的嫌疑人"
- 英文："Loop 1 complete! Morrison becomes new suspect"

**特殊效果**：
- ✅ 完成任务：TAS_LOOP001_PHASE（循环目标任务标记完成）
- ❌ 移除疑点：TAS_LOOP001_DOUBT_02、TAS_LOOP001_DOUBT_03（已解答的疑点移除）
- 🎬 播放动画：LOOP_COMPLETE_EFFECT（循环完成特效）

**特殊说明**：
- ⚠️ **打断式事件**（ifInterrupt=1）

---

## 🔄 循环过渡阶段

### 事件20：EVE_LOOP001_TO_LOOP002 - 循环1至循环2过渡

**解锁条件**：
- 循环1完成（LOOP001_COMPLETE）

**解锁内容**：
- ✅ 场景：SC107（Vivian化妆室）
- ✅ 场景：SC110（Morrison家中客厅）
- ✅ 场景：SC111（Morrison家中书房）
- ✅ 场景：SC112（Morrison警局办公室）
- ✅ 任务：TAS_LOOP002_PHASE（循环目标：调查Morrison警官）
- ✅ 对话：D_LOOP002_OPENING（循环2开场对话）

**提示文本**：
- 中文："循环2已开启：调查Morrison警官"
- 英文："Loop 2 unlocked: Investigate Officer Morrison"

**特殊说明**：
- ⚠️ **打断式事件**（ifInterrupt=1）
- 🔄 所有场景刷新（清除clear标识）
- 🎬 播放循环过渡动画

---

## 📊 事件统计总览

### 按事件类型统计

| 事件类型 | 数量 | 优先级范围 |
|---------|------|-----------|
| 循环开始 | 1 | 100 |
| 场景进入 | 1 | 90 |
| 对话完成 | 2 | 70-85 |
| 证据收集 | 8 | 50-80 |
| 谜题解开 | 1 | 70 |
| 场景清理 | 2 | 75 |
| 证据齐全 | 1 | 90 |
| 指证成功 | 4 | 95-100 |
| 循环过渡 | 1 | 100 |
| **总计** | **20** | - |

---

### 解锁内容统计

| 解锁类型 | 总数量 | 说明 |
|---------|--------|------|
| **场景** | 9个 | SC102, SC103, SC104, SC105, SC106, SC107, SC110, SC111, SC112 |
| **对话** | 7个 | Emma对话、Rosa指证对话、循环结束对话等 |
| **任务** | 11个 | 1个主案件、2个循环目标、6个行动目标、4个疑点 |
| **证据** | 8个 | EV111-EV115（储藏室）、EV121-EV122（走廊）、EV133（证词） |
| **谜题** | 1个 | 工具箱密码谜题 |
| **循环** | 1个 | LOOP002（循环2） |

---

## 🎯 关键解锁链条

### 链条1：开始调查

```
开场AVG完成
    → 解锁：街道场景
    → 进入街道
    → 解锁：Emma对话
    → Emma对话完成
    → 解锁：4个调查场景（储藏室、走廊、Tommy办公室、酒吧大堂）
```

---

### 链条2：密码谜题

```
收集女儿照片（EV112）
    → 解锁：密码提示（生日0915）
    → 解开工具箱密码
    → 解锁：氯仿毛巾（EV114）+ 工作记录卡（EV115）
```

---

### 链条3：证据收集

```
储藏室搜证（5个证据）
    → 触发：储藏室清理完成
    → 解锁：走廊调查任务

走廊搜证（2个证据）
    → 触发：走廊清理完成
    → 解锁：Tommy对话任务

Tommy对话（1个证词）
    → 触发：证据齐全检测

所有5个关键证据收集完成
    → 触发：可以指证提示
    → 解锁：指证Rosa任务
```

---

### 链条4：三轮指证

```
第一轮指证：工作记录卡（EV115）
    → 结果：Rosa承认在后台走廊工作
    → 解锁：第二轮指证

第二轮指证：氯仿毛巾（EV114）+ 氯仿瓶（EV121）
    → 结果：Rosa承认使用氯仿迷晕Zack
    → 解锁：第三轮指证

第三轮指证：拖拽痕迹（EV122）
    → 结果：Rosa供出Morrison是幕后黑手
    → 解锁：循环1结束对话

循环1完成
    → 解锁：循环2场景 + 循环2任务
```

---

## ⚠️ 特殊规则说明

### 1. 多条件触发（AND关系）

**EVE_ALL_EVIDENCES_COLLECTED**需要同时满足5个条件：
- EV115_COLLECTED（工作记录卡）
- EV114_COLLECTED（氯仿毛巾）
- EV121_COLLECTED（氯仿瓶）
- EV122_COLLECTED（拖拽痕迹）
- EV133_COLLECTED（Tommy证词）

**注意**：缺少任何一个证据都不会触发"可以指证"提示。

---

### 2. 打断式事件（ifInterrupt=1）

以下事件会**立即打断当前流程**：
- EVE_ROSA_EXPOSE_ROUND3_SUCCESS（第三轮指证成功）
- EVE_ROSA_EXPOSE_COMPLETE（Rosa指证完成）
- EVE_LOOP001_TO_LOOP002（循环过渡）

**效果**：暂停当前操作，强制播放对话或动画。

---

### 3. 前置依赖关系

**证据依赖**：
- EV114、EV115 依赖于 PUZZLE_TOOLBOX_SOLVED（必须先解开密码）

**场景依赖**：
- SC103、SC104、SC105、SC106 依赖于 DIALOGUE_D045_COMPLETE（必须先完成Emma对话）

**指证依赖**：
- Round2 依赖于 Round1成功
- Round3 依赖于 Round2成功
- 循环2 依赖于 循环1完成

---

### 4. 场景刷新机制

**触发时机**：循环完成时
**刷新内容**：
- 清除所有场景的"clear"标识
- 重置场景探索状态
- 可能刷新新证据

**目的**：让玩家可以重新探索场景，发现新线索。

---

## 🔍 证据使用对照表

| 证据ID | 证据名称 | 收集位置 | 用途 | 使用时机 |
|--------|---------|---------|------|---------|
| EV111 | 通缉令 | 储藏室 | 环境叙事 | - |
| EV112 | 女儿照片 | 储藏室 | 密码提示 | 解锁工具箱 |
| EV113 | 医疗账单 | 储藏室 | 环境叙事 | - |
| **EV114** | **氯仿毛巾** | 储藏室 | **指证核心** | **第二轮指证** |
| **EV115** | **工作记录卡** | 储藏室 | **指证核心** | **第一轮指证** |
| **EV121** | **氯仿瓶** | 走廊 | **指证核心** | **第二轮指证** |
| **EV122** | **拖拽痕迹** | 走廊 | **指证核心** | **第三轮指证** |
| EV133 | Tommy证词 | Tommy办公室 | 循环6使用 | 循环6枪声证明 |

---

## 📝 配置文件引用

本文档内容对应以下配置文件：
- 📄 JSON配置：`d:\NDC_project\Config\EventConfig_Episode1_Loop1.json`
- 📊 Excel配置：`d:\NDC_project\Config\EventConfig_Episode1_Loop1.xlsx`
- 📖 详细说明：`d:\NDC_project\Config\EventConfig_Episode1_Loop1_说明.md`

---

**创建日期**: 2025-11-23
**版本**: 1.0
**适用章节**: Episode 1 循环1（Rosa现场目击指证）
