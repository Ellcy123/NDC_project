# Unit1 Loop1 完整配置示例

## 📋 概述

本文件夹包含NDC游戏 **Unit1 Loop1（栽赃陷害的真相）** 的完整6级配置示例，展示了如何使用结构化JSON配置来组织侦探游戏的内容生产。

## 🗂️ 文件结构

```
Unit1_Loop1_完整配置示例/
├── Level1_Unit1_Metadata.json           # 章节元数据
├── Level2_Unit1_Loop1_Config.json       # 循环配置
├── Level3_Unit1_Loop1_Dialog_Config.json # 对话树配置
├── Level4_Unit1_Loop1_Evidence_Config.json # 证据配置
├── Level5_Unit1_Loop1_Scene_Config.json  # 场景配置
├── Level6_Unit1_Loop1_Expose_Rosa.json   # 指证诡计配置
└── README.md                            # 本说明文档
```

## 📊 各层级详细说明

### Level 1: 章节元数据
**文件**: `Level1_Unit1_Metadata.json`

**作用**: 定义整个Unit1章节的全局信息

**包含内容**:
- 章节基础信息（ID、名称、时代背景）
- 难度模式配置（Normal/Expert）
- 6个循环的概览
- 主要角色列表
- 开场/结尾动画
- 叙事目标与Hook设计

**关键字段**:
```json
{
  "unit_id": "Unit1",
  "loop_structure": { "total_loops": 6 },
  "main_characters": [...],
  "ending_hook": { "revelation": "...", "threat": "..." }
}
```

---

### Level 2: 循环配置
**文件**: `Level2_Unit1_Loop1_Config.json`

**作用**: 定义Loop1的调查目标、可用场景、证据需求和完成条件

**包含内容**:
- 任务系统目标（Main Case、Phase Goal、Current Goal、Doubts）
- 可用场景列表及解锁条件
- 必需证据清单
- 指证触发条件
- 循环完成标准
- 难度差异化配置

**关键字段**:
```json
{
  "objectives": {
    "phase_goal": "到底是谁把我迷晕了...",
    "total_required": 4
  },
  "available_scenes": [...],
  "expose_configuration": {
    "target_npc": "NPC002",
    "trigger_condition": { "min_evidence_count": 4 }
  }
}
```

---

### Level 3: 对话树配置
**文件**: `Level3_Unit1_Loop1_Dialog_Config.json`

**作用**: 定义Loop1中所有对话节点、分支选项和对话流程

**包含内容**:
- 23个对话节点（D001-D023）
- 1个分支选择点（D002）
- 角色立绘表情
- 语音文件引用
- 场景转换逻辑
- 证据自动收集

**对话结构**:
```
Act 1: Morrison逮捕Zack (D001-D009)
  └─ 分支选择 (D002: 3种回应)
Act 2: Emma救场 (D010-D021)
  └─ 设立72小时期限
Act 3: 建立合作 (D022-D045)
  └─ 继续分支对话
```

**关键字段**:
```json
{
  "node_id": "D002",
  "dialog_type": "AVG_Choice",
  "options": [
    { "text": "...", "personality_trait": "cooperative" }
  ]
}
```

---

### Level 4: 证据配置
**文件**: `Level4_Unit1_Loop1_Evidence_Config.json`

**作用**: 定义Loop1中所有可收集的证据、关系网络和组合规则

**包含内容**:
- 7条证据（4条关键证据 + 2条辅助证据 + 1条环境叙事）
- 证据关系网络（支持/矛盾/时间匹配/印证）
- 证据组合规则（如 EV002 + EV003 = 迷晕工具组合）
- 指证可用性配置
- 收集顺序推荐

**证据网络图**:
```
EV001 (工作记录卡) ─supports→ EV003 (毛巾)
                  ─contradicts→ EV004 (拖拽痕迹)
EV002 (氯仿瓶) ─supports→ EV003
               ─timeline_match→ EV004
EV004 ─corroborates→ EV006 (Tommy证词)
EV005 (Tommy证词) ─supports→ EV006
```

**关键字段**:
```json
{
  "evidence_id": "EV003",
  "relationships": [
    {
      "target_evidence_id": "EV002",
      "relationship_type": "supports",
      "strength": 0.95
    }
  ],
  "combinations": [
    {
      "with_evidence_id": "EV002",
      "result_evidence_id": "EV_Combo_001"
    }
  ]
}
```

---

### Level 5: 场景配置
**文件**: `Level5_Unit1_Loop1_Scene_Config.json`

**作用**: 定义Loop1中所有场景的背景、热区、NPC位置和交互逻辑

**包含内容**:
- 9个场景（6个可访问 + 3个锁定）
- 场景类型：对话场景(dialogue) / 搜证场景(crime) / 未开放(noentry)
- 热区坐标定义（搜证点）
- NPC位置和状态
- 场景转换逻辑
- 地图系统配置

**搜证场景示例** (SC103 - Rosa的储藏室):
```json
{
  "hotspots": [
    {
      "hotspot_id": "HS_SC103_Shelf",
      "coordinates": { "x": 1200, "y": 800, "width": 200, "height": 150 },
      "evidence_id": "EV001",
      "cursor_hint": {
        "normal_mode": "magnifying_glass_pulse",
        "expert_mode": "magnifying_glass_static"
      }
    }
  ]
}
```

**关键字段**:
```json
{
  "scene_id": "SC103",
  "scene_type": "crime",
  "background": {
    "parallax_enabled": true,
    "parallax_range": { "min_x": 0, "max_x": 640 }
  },
  "hotspots": [...],
  "scene_progress": {
    "normal_mode": { "show_progress": true, "total_collectibles": 5 }
  }
}
```

---

### Level 6: 指证诡计配置
**文件**: `Level6_Unit1_Loop1_Expose_Rosa.json`

**作用**: 定义对Rosa的三轮渐进式指证策略

**包含内容**:
- 3轮指证逻辑（What → Why → How）
- 每轮的正确/错误证据反馈
- 玩家对话选项（攻击性/分析性/同理心）
- NPC情感状态变化
- 成功/失败条件
- 难度差异化配置

**三轮指证策略**:
```
Round 1: What - 事实矛盾
  └─ 使用 EV001 指出Rosa位置矛盾

Round 2: Why - 动机压力
  └─ 使用 EV003 + EV007 揭示Rosa被收买

Round 3: How - 完整真相
  └─ 使用 EV004 + 同理心说服 → Rosa完整供述
```

**情感曲线**:
```
恐惧 ━━━━━━━━━━━━━┓
                    ┃
                    ┗━━━━━━━ 罪恶感
                             ┃
                             ┗━━━ 信任 ━━━ 解脱
```

**关键字段**:
```json
{
  "round_number": 3,
  "reassurance_options": [
    {
      "option_id": "R3_Empathy",
      "effectiveness": "very_high",
      "trust_increase": 25
    }
  ],
  "npc_final_confession": "...[完整供述]..."
}
```

---

## 🔗 层级依赖关系

```
Level 1 (Unit Metadata)
  ↓
Level 2 (Loop Config) ← 引用 Level 1 的 unit_id
  ↓
┌─────────┬─────────┬─────────┐
│ Level 3 │ Level 4 │ Level 5 │ ← 都引用 Loop Config
│ Dialog  │Evidence │ Scene   │
└────┬────┴────┬────┴────┬────┘
     └──────┬──────┬─────┘
            ↓      ↓
         Level 6 (Expose) ← 引用 Evidence + Scene + Dialog
```

---

## 🎮 游戏流程示例

基于这些配置，Loop1的完整游戏流程如下：

### 1. 开场序列（线性）
- **SC101**: Morrison逮捕Zack
  - 对话 D001-D009（含1次分支选择）
- **SC119**: Emma出场救援
  - 对话 D010-D021（设立72小时期限）
- **SC102**: 街道对话
  - 对话 D022-D045（建立合作关系）

### 2. 自由探索阶段
玩家可以自由访问以下场景：
- **SC103** (Rosa储藏室): 收集 EV001, EV003, EV007, EV008, EV009
- **SC104** (走廊): 收集 EV002, EV004
- **SC105** (Tommy办公室): 获取证词 EV005, EV006

### 3. 指证阶段
当玩家收集足够证据后：
- **SC106** (酒吧大堂): 对Rosa进行三轮指证
  - Round 1: 使用 EV001 揭露位置矛盾
  - Round 2: 使用 EV003 + EV007 揭示被收买
  - Round 3: 使用 EV004 获得完整供述

### 4. 循环完成
- 解锁 Unit1_Loop2
- Morrison成为下一循环的调查目标
- 解锁新场景：SC113, SC114, SC115

---

## 🤖 AI协作应用场景

### 场景1: 逻辑验证
**任务**: 验证证据链完整性

**AI Prompt**:
```
请分析 Level4_Unit1_Loop1_Evidence_Config.json 中的证据关系网络，
检查是否存在以下问题：
1. 孤立证据（没有任何关系的证据）
2. 循环依赖（A支持B，B支持A）
3. 指证所需证据是否在场景中可收集
4. 证据组合规则是否合理
```

---

### 场景2: 对话生成
**任务**: 根据角色设定生成分支对话

**AI Prompt**:
```
基于以下角色设定：
- Zack: 理想主义侦探，直觉敏锐但有时冲动
- 当前场景: SC106 酒吧大堂
- 目标: 说服Rosa说出真相

请生成3个对话选项，分别体现：
1. 攻击性风格（质疑Rosa的谎言）
2. 分析性风格（用逻辑推理施压）
3. 同理心风格（理解Rosa的困境）

参考格式见 Level3_Unit1_Loop1_Dialog_Config.json
```

---

### 场景3: 难度平衡
**任务**: 检查Normal/Expert难度差异

**AI Prompt**:
```
请比较以下配置文件中Normal和Expert模式的差异：
- Level2_Unit1_Loop1_Config.json (难度配置)
- Level4_Unit1_Loop1_Evidence_Config.json (证据提示)
- Level6_Unit1_Loop1_Expose_Rosa.json (指证重试次数)

评估难度曲线是否合理，Expert模式是否过于惩罚性。
```

---

### 场景4: 内容完整性检查
**任务**: 确保所有引用ID正确

**AI Prompt**:
```
请检查以下跨文件引用的一致性：
1. Level2 中的 required_evidence 是否都在 Level4 中定义？
2. Level3 中的 scene_id 是否都在 Level5 中存在？
3. Level6 中的 correct_evidence 是否可在场景中收集？
4. Level5 中的 dialog_entry 是否在 Level3 中有对应节点？

输出不一致项列表。
```

---

## 📈 使用统计

### 内容规模
- **对话节点**: 23个（含1个分支点）
- **证据**: 7条（4条关键 + 2条辅助 + 1条环境）
- **场景**: 9个（6个可访问 + 3个锁定）
- **指证轮次**: 3轮渐进式
- **估计游戏时长**: 10-15分钟

### 配置复杂度
- **JSON文件**: 6个
- **总配置行数**: ~1500行
- **证据关系**: 8对
- **场景热区**: 7个
- **NPC状态**: 12种

---

## 🛠️ Unity集成建议

### 1. ScriptableObject映射
```csharp
// Level 1
[CreateAssetMenu(fileName = "UnitMetadata", menuName = "NDC/Unit Metadata")]
public class UnitMetadata : ScriptableObject {
    public string unitId;
    public string unitName;
    public LoopInfo[] loops;
    public CharacterInfo[] characters;
}

// Level 2
[CreateAssetMenu(fileName = "LoopConfig", menuName = "NDC/Loop Config")]
public class LoopConfig : ScriptableObject {
    public string loopId;
    public ObjectiveConfig objectives;
    public SceneReference[] availableScenes;
    public EvidenceReference[] requiredEvidence;
    public ExposeConfig exposeConfiguration;
}

// Level 6
[CreateAssetMenu(fileName = "ExposeConfig", menuName = "NDC/Expose Config")]
public class ExposeConfig : ScriptableObject {
    public string exposeId;
    public NPCReference targetNPC;
    public ExposeRound[] rounds;
}
```

### 2. 运行时加载
```csharp
public class GameManager : MonoBehaviour {
    public void LoadLoop(string loopId) {
        // 加载Loop配置
        LoopConfig loop = Resources.Load<LoopConfig>($"Loops/{loopId}");

        // 加载关联的证据配置
        EvidenceConfig evidence = Resources.Load<EvidenceConfig>($"Evidence/{loopId}");

        // 加载场景配置
        SceneConfig scenes = Resources.Load<SceneConfig>($"Scenes/{loopId}");

        // 初始化游戏状态
        GameState.Initialize(loop, evidence, scenes);
    }
}
```

### 3. 事件驱动架构
```csharp
// 证据收集事件
public class EvidenceCollectedEvent : UnityEvent<string> { }

// 对话完成事件
public class DialogCompletedEvent : UnityEvent<string> { }

// 指证成功事件
public class ExposeSuccessEvent : UnityEvent<string> { }

// 事件监听
GameEvents.OnEvidenceCollected.AddListener(evidenceId => {
    // 检查是否满足指证触发条件
    if (CheckExposeTrigger()) {
        EnableExposeUI();
    }
});
```

---

## ⚠️ 注意事项

### 1. ID命名规范
- **Unit ID**: `Unit{N}` (如 Unit1, Unit2)
- **Loop ID**: `Unit{N}_Loop{M}` (如 Unit1_Loop1)
- **Scene ID**: `SC{3位数字}` (如 SC101)
- **Evidence ID**: `EV{3位数字}` (如 EV001)
- **Dialog ID**: `D{3位数字}` (如 D001)
- **NPC ID**: `NPC{3位数字}` (如 NPC002)

### 2. 文件编码
- 所有JSON文件使用 **UTF-8编码**
- 确保中文字符正确显示

### 3. 版本控制
- 每次修改配置文件后更新 `meta_info.last_modified`
- 使用Git追踪所有配置文件变更
- 重要修改需要在commit message中说明

### 4. 本地化考虑
- 所有文本内容同时提供中文(`zh`)和英文(`en`)
- 为未来其他语言预留扩展空间
- 语音文件使用独立的文件名引用

---

## 📚 扩展阅读

- [NDC内容生产框架.html](../NDC内容生产框架.html) - 完整框架文档
- [NDC_DATA.md](../../系统策划/NDC_DATA.md) - 现有数据表
- [Unit1_血色酒吧_意外卷入.md](../../六章内容合集/Unit1_血色酒吧_意外卷入.md) - 故事大纲

---

## 📝 更新日志

### 2025-11-06
- ✅ 创建Level 1-6完整配置示例
- ✅ 添加详细注释和说明文档
- ✅ 建立AI协作应用场景

---

**制作团队**: NDC Content Team
**最后更新**: 2025-11-06
**配置版本**: v1.0
