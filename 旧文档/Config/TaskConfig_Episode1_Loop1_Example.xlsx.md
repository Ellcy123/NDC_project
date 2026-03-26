# 任务配置表 Excel 预览

由于系统环境限制，这里提供任务配置的Markdown表格预览。

---

## 工作表1: 任务主表

### 图例说明
- 🟨 黄色背景 = MainCase（章节案件）
- 🟩 绿色背景 = PhaseGoal（循环目标）
- 🟦 蓝色背景 = CurrentGoal（行动目标）
- 🟧 橙色背景 = Doubt（疑点）
- ⬜ 灰色背景 = SideCase（支线案件）

---

| 任务ID | 任务类型 | 子章节ID | 循环ID | 优先级 | 中文标题 | 英文标题 | 中文描述 | 显示进度条 | 进度总数 | 需要的证据列表 | 显示完成动效 | 100%时高亮 | 高亮提示_中文 | 最大显示数量 | 触发条件 | 完成条件 |
|--------|---------|---------|--------|--------|---------|---------|---------|-----------|---------|--------------|-------------|-----------|-------------|-------------|---------|---------|
| 🟨 TAS_CH001_MAIN | MainCase | SEC01 | | 100 | 蓝月亮歌舞厅谋杀案 | Blue Moon Ballroom Murder Case | 查清Webb的死因，找出真凶，洗清我的冤屈 | FALSE | | | TRUE | | | 1 | LOOP001_START | LOOP006_COMPLETE |
| 🟩 TAS_LOOP001_PHASE | PhaseGoal | SEC01 | LOOP001 | 90 | 调查Rosa的证词 | Investigate Rosa's Testimony | 收集证据，揭穿Rosa的谎言 | TRUE | 5 | EV001, EV002, EV003, EV004, EV007 | TRUE | TRUE | 证据已齐全，可以进行指证！ | 1 | LOOP001_START | EXPOSE_ROSA_SUCCESS |
| 🟦 TAS_LOOP001_GOAL_01 | CurrentGoal | SEC01 | LOOP001 | 85 | 前往歌舞厅外的街道 | Go to the Street Outside the Ballroom | 与Emma汇合，商讨调查计划 | FALSE | | | TRUE | | | 1 | DIALOGUE_D021_COMPLETE | SCENE_SC102_ENTER |
| 🟦 TAS_LOOP001_GOAL_02 | CurrentGoal | SEC01 | LOOP001 | 84 | 与Emma对话 | Talk to Emma | 了解Emma的调查动机 | FALSE | | | TRUE | | | 1 | SCENE_SC102_ENTER | DIALOGUE_D045_COMPLETE |
| 🟦 TAS_LOOP001_GOAL_03 | CurrentGoal | SEC01 | LOOP001 | 83 | 调查Rosa的储藏室 | Investigate Rosa's Storage Room | 寻找能够证明Rosa说谎的证据 | FALSE | | | TRUE | | | 1 | DIALOGUE_D045_COMPLETE | SCENE_SC103_CLEARED |
| 🟦 TAS_LOOP001_GOAL_04 | CurrentGoal | SEC01 | LOOP001 | 82 | 调查歌舞厅一楼走廊 | Investigate the First Floor Corridor | 这里是我被迷晕的现场，一定有重要线索 | FALSE | | | TRUE | | | 1 | SCENE_SC103_CLEARED | SCENE_SC104_CLEARED |
| 🟦 TAS_LOOP001_GOAL_05 | CurrentGoal | SEC01 | LOOP001 | 81 | 与Tommy对话 | Talk to Tommy | 前往Tommy的办公室，询问案发当晚的情况 | FALSE | | | TRUE | | | 1 | SCENE_SC104_CLEARED | DIALOGUE_TOMMY_001_COMPLETE |
| 🟦 TAS_LOOP001_GOAL_06 | CurrentGoal | SEC01 | LOOP001 | 80 | 指证Rosa | Expose Rosa | 前往酒吧大堂，用证据指证Rosa的谎言 | FALSE | | | TRUE | | | 1 | ALL_EVIDENCES_COLLECTED_LOOP001 | EXPOSE_ROSA_SUCCESS |
| 🟧 TAS_LOOP001_DOUBT_01 | Doubt | SEC01 | LOOP001 | 70 | Morrison为何如此确定我是凶手？ | Why is Morrison so sure I'm the killer? | | FALSE | | | FALSE | | | 6 | DIALOGUE_D009_COMPLETE | EXPOSE_MORRISON_SUCCESS |
| 🟧 TAS_LOOP001_DOUBT_02 | Doubt | SEC01 | LOOP001 | 70 | Rosa的证词有什么破绽？ | What's wrong with Rosa's testimony? | | FALSE | | | FALSE | | | 6 | DIALOGUE_ROSA_001_COMPLETE | EXPOSE_ROSA_SUCCESS |
| 🟧 TAS_LOOP001_DOUBT_03 | Doubt | SEC01 | LOOP001 | 70 | 谁把我迷晕了？ | Who knocked me out? | | FALSE | | | FALSE | | | 6 | EV002_COLLECTED | EXPOSE_ROSA_SUCCESS |
| 🟧 TAS_LOOP001_DOUBT_04 | Doubt | SEC01 | LOOP001 | 70 | Tommy为什么说看到警察进入后台？ | Why did Tommy say he saw a cop entering backstage? | | FALSE | | | FALSE | | | 6 | DIALOGUE_TOMMY_001_COMPLETE | EXPOSE_MORRISON_SUCCESS |
| ⬜ TAS_LOOP001_SIDE_01 | SideCase | SEC01 | LOOP001 | 60 | Emma的真实目的 | Emma's True Purpose | Emma为什么要帮我？她在调查什么？ | FALSE | | | TRUE | | | 2 | DIALOGUE_D025_COMPLETE | OPTIONAL_DIALOGUE_EMMA_SIDE_COMPLETE |

---

## 工作表2: 子任务表

| 父任务ID | 子任务ID | 中文描述 | 英文描述 | 完成条件 |
|---------|---------|---------|---------|---------|
| TAS_LOOP001_PHASE | SUB_LOOP001_01 | 收集Rosa储藏室的证据 | Collect evidence from Rosa's storage | EV001_COLLECTED,EV003_COLLECTED,EV007_COLLECTED |
| TAS_LOOP001_PHASE | SUB_LOOP001_02 | 收集走廊的证据 | Collect evidence from the corridor | EV002_COLLECTED,EV004_COLLECTED |

---

## 工作表3: 任务类型配置

| 任务类型 | 最大显示数量 | 显示进度条 | 显示完成动效 | 默认优先级 |
|---------|------------|-----------|------------|-----------|
| MainCase | 1 | FALSE | TRUE | 100 |
| PhaseGoal | 1 | TRUE | TRUE | 90 |
| CurrentGoal | 1 | FALSE | TRUE | 80 |
| Doubt | 6 | FALSE | FALSE | 70 |
| SideCase | 2 | FALSE | TRUE | 60 |

---

## 工作表4: 显示优先级

### 缩略展示优先级（只显示1个任务）

| 顺序 | 任务类型 |
|-----|---------|
| 1 | CurrentGoal |
| 2 | PhaseGoal |
| 3 | MainCase |

### 展开展示顺序（显示所有任务）

| 顺序 | 任务类型 |
|-----|---------|
| 1 | PhaseGoal |
| 2 | CurrentGoal |
| 3 | Doubt |
| 4 | SideCase |

---

## 📊 数据统计

- **总任务数**: 13个
  - MainCase: 1个
  - PhaseGoal: 1个
  - CurrentGoal: 6个
  - Doubt: 4个
  - SideCase: 1个

- **子任务数**: 2个

---

## 🎯 关键设计特点

### 1. PhaseGoal（循环目标）特殊机制
- ✅ 显示进度条：5/5
- ✅ 需要收集5个证据：EV001, EV002, EV003, EV004, EV007
- ✅ 进度达到100%时高亮显示
- ✅ 高亮提示："证据已齐全，可以进行指证！"
- ⚠️ 但此时任务未完成，需要等指证成功后才完成

### 2. CurrentGoal（行动目标）流程
```
开场对话结束
    ↓
前往街道 → 与Emma对话
    ↓
调查储藏室 → 调查走廊
    ↓
与Tommy对话
    ↓
指证Rosa
```

### 3. Doubt（疑点）特点
- ❌ 无进度条
- ❌ 无完成动效（完成时静默移除）
- ✅ 最多显示6条
- ✅ 随着调查推进逐步解答

### 4. 显示逻辑
**缩略模式**（默认）：
- 优先显示 CurrentGoal（当前该做什么）
- 没有CurrentGoal就显示 PhaseGoal（循环目标）
- 都没有就显示 MainCase（章节总目标）

**展开模式**（鼠标悬停）：
- 按顺序显示所有任务
- PhaseGoal → CurrentGoal → Doubt → SideCase

---

## 💡 使用说明

### 如何生成真正的Excel文件

如果你的电脑上安装了Python，可以运行以下命令生成Excel文件：

```bash
cd d:\NDC_project\好用的工具
python task_config_to_excel.py
```

这将生成：`d:\NDC_project\Config\TaskConfig_Episode1_Loop1_Example.xlsx`

Excel文件将包含：
- ✅ 彩色编码（不同任务类型不同颜色）
- ✅ 冻结首行（方便查看表头）
- ✅ 自动调整列宽
- ✅ 边框和对齐
- ✅ 4个工作表（任务主表、子任务表、类型配置、显示优先级）

---

**生成时间**: 2025-11-23
**配置版本**: 1.0
