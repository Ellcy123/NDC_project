# Episode 1 循环1 事件触发配置说明

## 📋 文件清单

| 文件名 | 说明 | 创建时间 |
|-------|------|---------|
| **EventConfig_Episode1_Loop1.json** | 事件配置JSON | 2025-11-23 |
| **EventConfig_Episode1_Loop1.xlsx** | 事件配置Excel（方便查看） | 2025-11-23 |
| **EventConfig_Episode1_Loop1_说明.md** | 本说明文档 | 2025-11-23 |

---

## 🎯 循环1概览

**循环名称**: Rosa现场目击指证
**核心目标**: 到底是谁把我迷晕了，还想把杀人的罪名扣在我头上？
**核心谎言**: Rosa声称"我一直在地下室酒窖工作，什么都没看到"
**指证策略**: 三轮递进式指证，逐层击破Rosa的谎言防线

---

## 📊 事件统计

- **事件总数**: 20个
- **场景解锁事件**: 4个
- **证据收集事件**: 8个
- **对话完成事件**: 3个
- **指证成功事件**: 4个
- **循环过渡事件**: 1个

---

## 🗺️ 事件流程图

```
开场AVG完成 (OPENING_AVG_COMPLETE)
    ↓
[EVE_LOOP001_START] 循环1开始
    ↓ 解锁：SC102（街道场景）
进入街道场景 (SCENE_SC102_ENTER)
    ↓
[EVE_ENTER_SC102] 触发Emma对话
    ↓
Emma对话完成 (DIALOGUE_D045_COMPLETE)
    ↓
[EVE_EMMA_TALK_COMPLETE] 解锁多个调查场景
    ↓ 解锁：SC103（储藏室）、SC104（走廊）、SC105（Tommy办公室）、SC106（酒吧大堂）
    ├─── 调查储藏室 ─────┐
    │   ├─ EV111_COLLECTED (通缉令) [EVE_COLLECT_EV111]
    │   ├─ EV112_COLLECTED (女儿照片) [EVE_COLLECT_EV112] → 解锁密码提示
    │   ├─ EV113_COLLECTED (医疗账单) [EVE_COLLECT_EV113]
    │   ├─ PUZZLE_TOOLBOX_SOLVED (解开密码) [EVE_SOLVE_TOOLBOX_PUZZLE]
    │   ├─ EV114_COLLECTED (氯仿毛巾) [EVE_COLLECT_EV114]
    │   └─ EV115_COLLECTED (工作记录卡) [EVE_COLLECT_EV115]
    │
    ├─── 调查走廊 ─────┐
    │   ├─ EV121_COLLECTED (氯仿瓶) [EVE_COLLECT_EV121]
    │   └─ EV122_COLLECTED (拖拽痕迹) [EVE_COLLECT_EV122]
    │
    ├─── 与Tommy对话 ─────┐
    │   └─ DIALOGUE_TOMMY_001_COMPLETE [EVE_TOMMY_TALK_COMPLETE]
    │       └─ EV133_COLLECTED (Tommy证词)
    │
    └─── 所有证据收集完成 ─────┐
         [EVE_ALL_EVIDENCES_COLLECTED]
         ↓ 高亮PhaseGoal任务，提示可以指证
前往酒吧大堂指证Rosa
    ├─ 第一轮指证：地点谎言 [EVE_ROSA_EXPOSE_ROUND1_SUCCESS]
    │   使用证据：EV115 (工作记录卡)
    │   结果：Rosa承认在后台走廊工作
    │
    ├─ 第二轮指证：目击谎言 [EVE_ROSA_EXPOSE_ROUND2_SUCCESS]
    │   使用证据：EV114 (氯仿毛巾) + EV121 (氯仿瓶)
    │   结果：Rosa承认使用氯仿迷晕Zack
    │
    └─ 第三轮指证：自认否定 [EVE_ROSA_EXPOSE_ROUND3_SUCCESS]
        使用证据：EV122 (拖拽痕迹)
        结果：Rosa供出Morrison是幕后黑手
        ↓
[EVE_ROSA_EXPOSE_COMPLETE] Rosa指证完成
    ↓
[EVE_LOOP001_TO_LOOP002] 循环1→循环2过渡
    ↓ 解锁：循环2场景 + 循环2任务
循环2开始
```

---

## 🔑 关键事件详解

### 1. 循环开始事件

**EVE_LOOP001_START**
- **触发条件**: 开场AVG完成
- **解锁内容**:
  - 场景：SC102（街道场景）
  - 任务：TAS_CH001_MAIN（主案件）、TAS_LOOP001_PHASE（循环目标）、TAS_LOOP001_GOAL_01（行动目标）
- **提示**: "前往歌舞厅外的街道"

---

### 2. 密码谜题解锁

**EVE_COLLECT_EV112** → **EVE_SOLVE_TOOLBOX_PUZZLE**

**流程**:
1. 收集证据112（女儿照片）
2. 查看照片背面，发现生日：0915
3. 使用生日作为密码解开工具箱
4. 获得核心证据：EV114（氯仿毛巾）+ EV115（工作记录卡）

**密码设计**:
- 密码类型：4位数字
- 正确密码：0915
- 提示来源：女儿照片背面的生日

---

### 3. 证据收集完成触发

**EVE_ALL_EVIDENCES_COLLECTED**

**触发条件**（多条件AND关系）:
```
EV115_COLLECTED AND
EV114_COLLECTED AND
EV121_COLLECTED AND
EV122_COLLECTED AND
EV133_COLLECTED
```

**特殊效果**:
- 高亮任务：TAS_LOOP001_PHASE
- 更新进度：5/5 (100%)
- 显示提示："证据已齐全，可以指证Rosa了！"

---

### 4. 三轮指证流程

#### **第一轮：否定地点谎言**

**EVE_ROSA_EXPOSE_ROUND1_SUCCESS**
- **使用证据**: EV115 (工作记录卡)
- **Rosa的谎言**: "我在地下室酒窖工作"
- **Zack反驳**: 工作记录卡显示你在后台走廊清洁
- **结果**: Rosa承认地点说谎

---

#### **第二轮：否定目击谎言**

**EVE_ROSA_EXPOSE_ROUND2_SUCCESS**
- **使用证据**: EV114 (氯仿毛巾) + EV121 (氯仿瓶)
- **Rosa的新谎言**: "我在后台专心清洁，什么都没看到"
- **Zack反驳**: 毛巾有氯仿残留，氯仿是医用麻醉剂不是清洁用品
- **结果**: Rosa承认使用氯仿迷晕Zack

---

#### **第三轮：否定自认，揭露真相**

**EVE_ROSA_EXPOSE_ROUND3_SUCCESS**
- **使用证据**: EV122 (拖拽痕迹)
- **Rosa的自认**: "是我把您拖到办公室的"
- **Zack反驳**: 拖拽痕迹需要150磅力量，你体重不到120磅
- **结果**: Rosa供出Morrison是幕后黑手
- **打断式事件**: ifInterrupt=1，立即播放真相揭露对话

---

### 5. 循环过渡事件

**EVE_LOOP001_TO_LOOP002**
- **触发条件**: LOOP001_COMPLETE
- **解锁内容**:
  - 场景：SC107、SC110、SC111、SC112（循环2场景）
  - 任务：TAS_LOOP002_PHASE（循环2目标）
  - 对话：D_LOOP002_OPENING（循环2开场）
- **特殊效果**:
  - 播放循环完成动画
  - 刷新所有场景（清除clear标识）
  - 更新任务面板

---

## 📦 证据清单

### 储藏室证据（SC103）

| 证据ID | 证据名称 | 类型 | 作用 |
|--------|---------|------|------|
| EV111 | 芝加哥警局通缉令 | 环境叙事 | 强化黑帮背景 |
| EV112 | Rosa的女儿照片 | 环境叙事 | 密码提示（0915） |
| EV113 | Rosa的医院就诊清单 | 环境叙事 | 展现经济困境 |
| **EV114** | **沾有氯仿的毛巾** | **指证核心** | 第二轮指证关键证据 |
| **EV115** | **工作记录卡** | **指证核心** | 第一轮指证关键证据 |

---

### 走廊证据（SC104）

| 证据ID | 证据名称 | 类型 | 作用 |
|--------|---------|------|------|
| **EV121** | **氯仿瓶** | **指证核心** | 第二轮指证关键证据 |
| **EV122** | **地板拖拽痕迹** | **指证核心** | 第三轮指证关键证据 |

---

### Tommy办公室证据（SC105）

| 证据ID | 证据名称 | 类型 | 作用 |
|--------|---------|------|------|
| EV133 | Tommy时间证词 | 对话摘录 | 循环6枪声证明 |

---

## 🎮 Unity实现要点

### 1. 多条件触发检测

```csharp
// EVE_ALL_EVIDENCES_COLLECTED 的实现
public void CheckAllEvidencesCollected()
{
    bool ev115 = GameState.Instance.IsEvidenceCollected("EV115");
    bool ev114 = GameState.Instance.IsEvidenceCollected("EV114");
    bool ev121 = GameState.Instance.IsEvidenceCollected("EV121");
    bool ev122 = GameState.Instance.IsEvidenceCollected("EV122");
    bool ev133 = GameState.Instance.IsEvidenceCollected("EV133");

    if (ev115 && ev114 && ev121 && ev122 && ev133)
    {
        // 触发事件
        EventManager.Instance.TriggerEvent("EVE_ALL_EVIDENCES_COLLECTED");

        // 高亮任务
        TaskManager.Instance.HighlightTask("TAS_LOOP001_PHASE");

        // 更新进度
        TaskManager.Instance.UpdateTaskProgress("TAS_LOOP001_PHASE", 5, 5);
    }
}
```

---

### 2. 密码谜题实现

```csharp
public class ToolboxPuzzle : MonoBehaviour
{
    private string correctPassword = "0915";

    public void OnPasswordSubmit(string inputPassword)
    {
        if (inputPassword == correctPassword)
        {
            // 解锁成功
            GameState.Instance.MarkPuzzleSolved("PUZZLE_TOOLBOX_SOLVED");

            // 触发事件
            EventManager.Instance.TriggerEvent("EVE_SOLVE_TOOLBOX_PUZZLE");

            // 解锁证据
            UnlockEvidence("EV114");
            UnlockEvidence("EV115");

            // 显示提示
            UIManager.ShowNotification("工具箱已打开！");
        }
        else
        {
            // 密码错误
            UIManager.ShowNotification("密码错误，请重试");
        }
    }
}
```

---

### 3. 三轮指证系统

```csharp
public class ExposeRosaSystem : MonoBehaviour
{
    private int currentRound = 1;

    public void OnExposeRound1(string evidenceId)
    {
        if (evidenceId == "EV115")
        {
            // 第一轮成功
            GameState.Instance.MarkExposeSuccess("EXPOSE_ROSA_ROUND1_SUCCESS");
            EventManager.Instance.TriggerEvent("EVE_ROSA_EXPOSE_ROUND1_SUCCESS");

            // 播放Rosa承认对话
            DialogManager.Instance.PlayDialog("D_ROSA_ROUND1_RESULT");

            // 进入第二轮
            currentRound = 2;
        }
        else
        {
            // 证据错误
            ShowExposeFailed("这个证据不能揭穿Rosa的谎言");
        }
    }

    public void OnExposeRound2(string[] evidenceIds)
    {
        bool hasEV114 = System.Array.Exists(evidenceIds, id => id == "EV114");
        bool hasEV121 = System.Array.Exists(evidenceIds, id => id == "EV121");

        if (hasEV114 && hasEV121)
        {
            // 第二轮成功
            GameState.Instance.MarkExposeSuccess("EXPOSE_ROSA_ROUND2_SUCCESS");
            EventManager.Instance.TriggerEvent("EVE_ROSA_EXPOSE_ROUND2_SUCCESS");

            // 播放Rosa承认对话
            DialogManager.Instance.PlayDialog("D_ROSA_ROUND2_RESULT");

            // 进入第三轮
            currentRound = 3;
        }
        else
        {
            ShowExposeFailed("证据不足以揭穿Rosa的新谎言");
        }
    }

    public void OnExposeRound3(string evidenceId)
    {
        if (evidenceId == "EV122")
        {
            // 第三轮成功
            GameState.Instance.MarkExposeSuccess("EXPOSE_ROSA_ROUND3_SUCCESS");
            EventManager.Instance.TriggerEvent("EVE_ROSA_EXPOSE_ROUND3_SUCCESS");

            // 播放Rosa供认真相对话（打断式）
            DialogManager.Instance.PlayDialogImmediately("D_ROSA_ROUND3_RESULT");

            // 完成循环1
            CompleteLoop1();
        }
        else
        {
            ShowExposeFailed("这个证据不能否定Rosa的自认");
        }
    }

    private void CompleteLoop1()
    {
        // 标记循环1完成
        GameState.Instance.MarkLoopComplete("LOOP001");

        // 触发循环完成事件
        EventManager.Instance.TriggerEvent("EVE_ROSA_EXPOSE_COMPLETE");

        // 播放循环完成动画
        PlayLoopCompleteAnimation();

        // 过渡到循环2
        StartLoop2Transition();
    }
}
```

---

### 4. 场景刷新机制

```csharp
public class SceneRefreshSystem : MonoBehaviour
{
    public void OnLoopComplete(string loopId)
    {
        // 清除所有场景的clear标识
        foreach (var scene in allScenes)
        {
            scene.ClearAllEvidenceClearMarks();
        }

        // 重置场景探索状态
        GameState.Instance.ResetSceneExplorationStatus();

        // 可能刷新新证据
        RefreshNewEvidences(loopId);
    }
}
```

---

## ⚠️ 注意事项

### 1. 事件触发顺序

- **同步触发**: 大部分事件是同步触发（ifInterrupt=0）
- **打断式触发**: 指证成功和循环过渡事件是打断式（ifInterrupt=1）

### 2. 多条件触发

使用逗号分隔多个条件，表示**AND关系**：
```
"triggerCondition": "EV115_COLLECTED,EV114_COLLECTED,EV121_COLLECTED"
```

### 3. 优先级系统

| 优先级范围 | 含义 | 背景色 |
|----------|------|--------|
| 90-100 | 关键事件（循环过渡、指证成功） | 黄色 |
| 70-89 | 重要事件（证据收集、对话完成） | 绿色 |
| 0-69 | 普通事件（环境叙事） | 白色 |

---

## 📈 后续扩展

### 循环2需要的事件

1. Morrison家中搜证事件
2. Morrison警局对话事件
3. Morrison三轮指证事件
4. 循环2→循环3过渡事件

### 循环3-6需要的事件

按照相同模式配置，每个循环包含：
- 场景解锁事件
- 证据收集事件
- NPC对话事件
- 三轮指证事件
- 循环过渡事件

---

**创建日期**: 2025-11-23
**版本**: 1.0
**作者**: Claude Code
**适用章节**: Episode 1 循环1
