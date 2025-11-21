# NDC配置详解

> 📌 **配合文档**: 请先阅读 `01_NDC内容生产工作流.md` 了解基本工作流
>
> 🎯 **本文档目的**: 详细说明6个Level的配置内容、字段关系、数据流向

---

## 📊 配置层级总览

```
Level 1: 章节元数据 (Unit Metadata)
   ↓ 定义6个循环
Level 2: 循环配置 (Loop Config) ×6
   ↓ 引用场景、证据、对话
Level 3: 对话树 (Dialog Tree)
Level 4: 证据配置 (Evidence Config)
Level 5: 场景配置 (Scene Config)
Level 6: 指证配置 (Expose Config)
```

**数据流向**：
- Level 1 → Level 2：通过 `loop_id` 关联
- Level 2 → Level 3/4/5/6：通过各种ID引用（`dialog_id`, `evidence_id`, `scene_id`, `expose_id`）
- Level 3/4/5 → Level 6：指证时需要用到对话、证据、场景中收集的信息

---

## 🎯 Level 1: 章节元数据

### 作用
- 定义整个章节的全局信息
- 章节选择界面显示的内容
- 循环结构的索引

### 核心字段

#### 1. 基础标识
| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `unit_id` | string | 章节唯一ID | `Unit1` |
| `unit_name.zh` | string | 中文章节名 | `血色酒吧·意外卷入` |
| `unit_name.en` | string | 英文章节名 | `Blood Red Bar - Caught in the Trap` |

#### 2. 故事背景
| 字段 | 类型 | 说明 |
|------|------|------|
| `story_background.era` | string | 时代背景 |
| `story_background.location` | string | 主要地点 |
| `story_background.time_span` | string | 时间跨度 |
| `story_background.duration_minutes` | int | 预估时长 |

#### 3. 循环结构
| 字段 | 类型 | 说明 |
|------|------|------|
| `loop_structure.total_loops` | int | 循环总数（通常为6） |
| `loop_structure.loops[]` | array | 循环列表 |
| `loop_structure.loops[].loop_id` | string | 循环ID（关联Level 2） |
| `loop_structure.loops[].objective` | string | 循环目标（显示在任务系统） |

#### 4. 主要角色
| 字段 | 类型 | 说明 |
|------|------|------|
| `main_characters[].npc_id` | string | NPC唯一ID |
| `main_characters[].name` | string | 角色名称 |
| `main_characters[].role` | enum | `protagonist`/`victim`/`suspect` |
| `main_characters[].description` | string | 角色简介 |

### 与其他Level的关系
- `loop_id` → 对应Level 2的配置文件名
- `npc_id` → 被Level 3/4/5/6引用

### 文件命名规则
```
Level1_Unit{N}_Metadata.yaml
示例: Level1_Unit1_Metadata.yaml
```

---

## 🔄 Level 2: 循环配置

### 作用
- 定义单个循环的玩法结构
- 配置可用场景、证据、对话
- 设置解锁条件和难度参数

### 核心字段

#### 1. 循环标识
| 字段 | 类型 | 说明 |
|------|------|------|
| `loop_id` | string | 与Level 1中的`loop_id`一致 |
| `loop_number` | int | 循环序号（1-6） |

#### 2. 任务系统
| 字段 | 类型 | 说明 |
|------|------|------|
| `objectives.main_case` | object | 章节主线案件 |
| `objectives.phase_goal` | object | 循环目标（带进度） |
| `objectives.sub_tasks[]` | array | 子任务列表 |

**示例**：
```yaml
objectives:
  main_case:
    type: MainCase
    text: 蓝月亮歌舞厅谋杀案

  phase_goal:
    type: PhaseGoal
    text: 找出迷晕我的人
    total_required: 4  # 需要4个证据才能触发指证
    current_progress: 0
```

#### 3. 游戏阶段
| 字段 | 类型 | 说明 |
|------|------|------|
| `phases[]` | array | 游戏阶段列表 |
| `phases[].phase_id` | string | 阶段ID |
| `phases[].phase_type` | enum | `Investigation`/`Expose`/`Cutscene` |
| `phases[].entry_condition` | object | 进入条件 |

**示例**：
```yaml
phases:
  - phase_id: P1_Investigation
    phase_type: Investigation
    entry_condition:
      type: GameStart
    available_scenes:
      - SC101
      - SC102
    available_dialogs:
      - D001
```

#### 4. 可用资源
| 字段 | 类型 | 说明 |
|------|------|------|
| `phases[].available_scenes[]` | array | 可访问的场景ID（引用Level 5） |
| `phases[].available_dialogs[]` | array | 可触发的对话ID（引用Level 3） |
| `phases[].collectible_evidence[]` | array | 可收集的证据ID（引用Level 4） |

#### 5. 指证配置
| 字段 | 类型 | 说明 |
|------|------|------|
| `expose_config.target_npc` | string | 指证目标NPC |
| `expose_config.trigger_condition` | object | 触发条件 |
| `expose_config.expose_file` | string | 指证配置文件路径（指向Level 6） |

### 与其他Level的关系
- `available_scenes[]` → 引用Level 5的`scene_id`
- `available_dialogs[]` → 引用Level 3的`dialog_id`
- `collectible_evidence[]` → 引用Level 4的`evidence_id`
- `expose_config.target_npc` → 引用Level 1的`npc_id`
- `expose_config.expose_file` → 指向Level 6的配置文件

### 文件命名规则
```
Level2_Unit{N}_Loop{M}_Config.yaml
示例: Level2_Unit1_Loop1_Config.yaml
```

---

## 💬 Level 3: 对话树

### 作用
- 定义AVG对话内容
- 设置对话分支逻辑
- 配置对话奖励（解锁场景、获得证据）

### 核心字段

#### 1. 对话节点
| 字段 | 类型 | 说明 |
|------|------|------|
| `dialog_id` | string | 对话唯一ID |
| `node_type` | enum | `Start`/`NPC`/`Player`/`Branch`/`End` |
| `speaker` | string | 说话人（NPC ID或"Zack"） |
| `text` | string | 对话文本 |
| `next_nodes[]` | array | 下一个节点ID列表 |

#### 2. 分支条件
| 字段 | 类型 | 说明 |
|------|------|------|
| `branches[].condition` | object | 分支触发条件 |
| `branches[].target_node` | string | 跳转到的节点ID |

**示例**：
```yaml
dialogs:
  - dialog_id: D001
    node_type: Start
    speaker: Zack
    text: Rosa，你昨晚在酒吧吗？
    next_nodes:
      - D002

  - dialog_id: D002
    node_type: NPC
    speaker: NPC002  # Rosa
    text: 我...我不记得了
    next_nodes:
      - D003_Choice

  - dialog_id: D003_Choice
    node_type: Branch
    branches:
      - option_text: [追问] 你在撒谎
        condition:
          type: None
        target_node: D004_Pressure

      - option_text: [安抚] 别紧张，我只是想了解真相
        condition:
          type: None
        target_node: D005_Comfort
```

#### 3. 对话奖励
| 字段 | 类型 | 说明 |
|------|------|------|
| `rewards.unlock_scenes[]` | array | 解锁的场景ID |
| `rewards.gain_evidence[]` | array | 获得的证据ID |
| `rewards.update_relationship` | object | 关系值变化 |

### 与其他Level的关系
- `speaker` → 引用Level 1的`npc_id`
- `rewards.unlock_scenes[]` → 引用Level 5的`scene_id`
- `rewards.gain_evidence[]` → 引用Level 4的`evidence_id`

### 文件命名规则
```
Level3_Unit{N}_Loop{M}_Dialog.yaml
示例: Level3_Unit1_Loop1_Dialog.yaml
```

---

## 🔍 Level 4: 证据配置

### 作用
- 定义所有证据的属性
- 配置证据之间的关系
- 设置证据的显示和使用条件

### 核心字段

#### 1. 证据基础信息
| 字段 | 类型 | 说明 |
|------|------|------|
| `evidence_id` | string | 证据唯一ID |
| `name` | string | 证据名称 |
| `category` | enum | `物证`/`证词`/`文件`/`照片` |
| `description` | string | 证据描述 |
| `icon` | string | 图标资源路径 |

#### 2. 收集方式
| 字段 | 类型 | 说明 |
|------|------|------|
| `collection_method` | enum | `搜证`/`对话`/`分析`/`剧情` |
| `source_scene` | string | 来源场景ID（如果是搜证） |
| `source_dialog` | string | 来源对话ID（如果是对话） |
| `requires_analysis` | bool | 是否需要分析才能看到完整描述 |

#### 3. 证据关系
| 字段 | 类型 | 说明 |
|------|------|------|
| `related_evidence[]` | array | 相关证据ID |
| `contradicts_evidence[]` | array | 矛盾证据ID |
| `supports_evidence[]` | array | 支持证据ID |

**示例**：
```yaml
evidences:
  - evidence_id: EV001
    name: 沾血毛巾
    category: 物证
    description: 一条白色毛巾，沾有血迹，散发刺鼻气味
    collection_method: 搜证
    source_scene: SC103
    requires_analysis: true
    analysis_result: 毛巾上有氯仿残留，这是用来迷晕人的
    related_evidence:
      - EV002  # 氯仿瓶
      - EV003  # Rosa的证词
```

#### 4. 证据使用
| 字段 | 类型 | 说明 |
|------|------|------|
| `usable_in_expose` | bool | 是否可在指证时使用 |
| `priority` | int | 证据优先级（影响玩家选择顺序） |

### 与其他Level的关系
- `source_scene` → 引用Level 5的`scene_id`
- `source_dialog` → 引用Level 3的`dialog_id`
- `related_evidence[]` → 引用Level 4中的其他`evidence_id`
- `usable_in_expose` → 决定是否在Level 6中可用

### 文件命名规则
```
Level4_Unit{N}_Loop{M}_Evidence.yaml
示例: Level4_Unit1_Loop1_Evidence.yaml
```

---

## 🗺️ Level 5: 场景配置

### 作用
- 定义可探索的场景
- 配置场景中的热区（hotspot）
- 设置场景解锁条件

### 核心字段

#### 1. 场景基础信息
| 字段 | 类型 | 说明 |
|------|------|------|
| `scene_id` | string | 场景唯一ID |
| `name` | string | 场景名称 |
| `description` | string | 场景描述 |
| `background_image` | string | 背景图资源路径 |
| `bgm` | string | 背景音乐资源路径 |

#### 2. 解锁条件
| 字段 | 类型 | 说明 |
|------|------|------|
| `unlock_condition.type` | enum | `GameStart`/`DialogComplete`/`EvidenceCollected` |
| `unlock_condition.required_ids[]` | array | 需要的对话/证据ID |

**示例**：
```yaml
scenes:
  - scene_id: SC103
    name: 储藏室
    description: 酒吧后方的储藏室，堆满杂物
    background_image: Scenes/Unit1/SC103_Storage.png
    unlock_condition:
      type: DialogComplete
      required_ids:
        - D045  # 完成与Rosa的对话后解锁
```

#### 3. 热区配置
| 字段 | 类型 | 说明 |
|------|------|------|
| `hotspots[].hotspot_id` | string | 热区ID |
| `hotspots[].type` | enum | `搜证`/`NPC`/`物品`/`场景切换` |
| `hotspots[].position` | object | 热区位置（x, y, width, height） |
| `hotspots[].interaction_type` | enum | `Collect`/`Examine`/`Talk`/`Move` |

**搜证热区示例**：
```yaml
hotspots:
  - hotspot_id: HS103_001
    type: 搜证
    position:
      x: 320
      y: 180
      width: 80
      height: 80
    interaction_type: Collect
    result:
      evidence_id: EV001  # 沾血毛巾
      hint_text: 这里有一条毛巾
```

**NPC热区示例**：
```yaml
hotspots:
  - hotspot_id: HS102_NPC
    type: NPC
    position:
      x: 400
      y: 150
      width: 100
      height: 200
    interaction_type: Talk
    result:
      npc_id: NPC002  # Rosa
      dialog_id: D001  # 触发的对话
```

#### 4. 场景中的NPC
| 字段 | 类型 | 说明 |
|------|------|------|
| `npcs_present[].npc_id` | string | NPC ID |
| `npcs_present[].position` | object | NPC位置 |
| `npcs_present[].available_dialogs[]` | array | 可触发的对话ID列表 |

### 与其他Level的关系
- `unlock_condition.required_ids[]` → 引用Level 3的`dialog_id`或Level 4的`evidence_id`
- `hotspots[].result.evidence_id` → 引用Level 4的`evidence_id`
- `hotspots[].result.dialog_id` → 引用Level 3的`dialog_id`
- `npcs_present[].npc_id` → 引用Level 1的`npc_id`

### 文件命名规则
```
Level5_Unit{N}_Loop{M}_Scene.yaml
示例: Level5_Unit1_Loop1_Scene.yaml
```

---

## ⚖️ Level 6: 指证配置

### 作用
- 定义指证玩法的问答逻辑
- 配置多轮指证的递进关系
- 设置难度参数和失败惩罚

### 核心字段

#### 1. 指证基础信息
| 字段 | 类型 | 说明 |
|------|------|------|
| `expose_id` | string | 指证配置ID |
| `target_npc` | string | 指证目标NPC |
| `total_rounds` | int | 总轮数（通常3轮） |

#### 2. 单轮指证配置
| 字段 | 类型 | 说明 |
|------|------|------|
| `rounds[].round` | int | 轮次序号 |
| `rounds[].question` | string | 指证问题 |
| `rounds[].question_type` | enum | `选择证据`/`选择矛盾点`/`选择证词` |
| `rounds[].correct_answer` | string | 正确答案的ID |
| `rounds[].options[]` | array | 选项列表 |

**示例**：
```yaml
expose:
  expose_id: EX_Rosa_Loop1
  target_npc: NPC002  # Rosa
  total_rounds: 3

  rounds:
    - round: 1
      question: Rosa，你说你昨晚不在酒吧。但是有证据表明你在撒谎！
      question_type: 选择证据
      npc_reaction_before: 我...我真的不记得了！

      options:
        - evidence_id: EV001  # 沾血毛巾（错误）
          feedback: 毛巾跟Rosa在不在没有关系

        - evidence_id: EV004  # Rosa的工作日志（正确）
          feedback: 工作日志显示Rosa昨晚值班！
          is_correct: true

        - evidence_id: EV002  # 氯仿瓶（错误）
          feedback: 这不能证明Rosa在场

      correct_answer: EV004
      npc_reaction_after: 好吧...我确实在。但我没有杀人！
```

#### 3. 难度设置
| 字段 | 类型 | 说明 |
|------|------|------|
| `difficulty_settings.normal.wrong_attempts_allowed` | int | Normal模式允许错误次数 |
| `difficulty_settings.expert.wrong_attempts_allowed` | int | Expert模式允许错误次数 |
| `difficulty_settings.normal.hint_enabled` | bool | 是否显示提示 |

#### 4. 奖励与后续
| 字段 | 类型 | 说明 |
|------|------|------|
| `success_rewards.unlock_dialog` | string | 成功后解锁的对话ID |
| `success_rewards.unlock_evidence` | string | 成功后获得的证据ID |
| `failure_consequence` | object | 失败后的后果 |

### 与其他Level的关系
- `target_npc` → 引用Level 1的`npc_id`
- `options[].evidence_id` → 引用Level 4的`evidence_id`
- `success_rewards.unlock_dialog` → 引用Level 3的`dialog_id`
- `success_rewards.unlock_evidence` → 引用Level 4的`evidence_id`

### 文件命名规则
```
Level6_Unit{N}_Loop{M}_Expose_{NPC名称}.yaml
示例: Level6_Unit1_Loop1_Expose_Rosa.yaml
```

---

## 🔗 跨Level引用关系总览

### 引用链条示例

```
Level 1: Unit1_Metadata
  ├─ loop_id: Unit1_Loop1 ───┐
  ├─ npc_id: NPC002 (Rosa) ──┼───┐
  └─ npc_id: NPC004 (Morrison)│   │
                              ↓   │
Level 2: Unit1_Loop1_Config   │   │
  ├─ available_scenes:        │   │
  │    - SC103 ───────────────┼───┼───┐
  ├─ available_dialogs:       │   │   │
  │    - D001 ───────────────┼───┼───┼───┐
  └─ collectible_evidence:    │   │   │   │
       - EV001 ───────────────┼───┼───┼───┼───┐
                              ↓   │   ↓   │   │
Level 3: Dialog               │   │   │   │   │
  - dialog_id: D001           │   │   │   │   │
    speaker: NPC002 ──────────┼───┘   │   │   │
    rewards:                  │       │   │   │
      unlock_scenes: [SC103]──┼───────┘   │   │
      gain_evidence: [EV001]──┼───────────┼───┘
                              ↓           ↓
Level 4: Evidence                         │
  - evidence_id: EV001                    │
    source_scene: SC103 ──────────────────┘
                              ↓
Level 5: Scene
  - scene_id: SC103
    hotspots:
      - result.evidence_id: EV001 ────┐
                              ↓       │
Level 6: Expose                       │
  - target_npc: NPC002                │
    options:                          │
      - evidence_id: EV001 ───────────┘
```

### 引用检查清单

添加新内容时，AI会自动检查：

#### ✅ 引用完整性
- [ ] Level 2引用的`scene_id`在Level 5中存在
- [ ] Level 2引用的`dialog_id`在Level 3中存在
- [ ] Level 2引用的`evidence_id`在Level 4中存在
- [ ] Level 3/4/5/6引用的`npc_id`在Level 1中存在
- [ ] Level 6引用的`evidence_id`在Level 4中存在

#### ✅ 逻辑闭环
- [ ] Level 6指证需要的证据，玩家在Level 4中能收集到
- [ ] Level 4证据的`source_scene`，在Level 2中已解锁
- [ ] Level 3对话的`unlock_scenes`，在Level 5中已定义
- [ ] 场景解锁链条没有死锁（至少有一个`GameStart`入口）

#### ✅ 数据一致性
- [ ] Level 1的`total_loops`数量与实际Level 2文件数量一致
- [ ] Level 2的难度设置与Level 6的难度设置一致
- [ ] NPC ID拼写在所有Level中一致

---

## 📝 字段命名规范

### ID命名规则

| 类型 | 格式 | 示例 |
|------|------|------|
| Unit ID | `Unit{N}` | `Unit1`, `Unit2` |
| Loop ID | `Unit{N}_Loop{M}` | `Unit1_Loop1` |
| NPC ID | `NPC{3位数字}` | `NPC001`, `NPC002` |
| Scene ID | `SC{3位数字}` | `SC101`, `SC102` |
| Dialog ID | `D{3位数字}` | `D001`, `D045` |
| Evidence ID | `EV{3位数字}` | `EV001`, `EV010` |
| Hotspot ID | `HS{场景编号}_{3位数字}` | `HS103_001` |
| Expose ID | `EX_{NPC名}_{循环}` | `EX_Rosa_Loop1` |

### 枚举值规范

#### node_type（对话节点类型）
- `Start` - 起始节点
- `NPC` - NPC发言
- `Player` - 玩家发言
- `Branch` - 分支选择
- `End` - 结束节点

#### evidence_category（证据类型）
- `物证` - 物理证据
- `证词` - 人物证词
- `文件` - 文档记录
- `照片` - 照片影像

#### phase_type（阶段类型）
- `Investigation` - 自由探索
- `Expose` - 指证玩法
- `Cutscene` - 过场动画

#### condition_type（条件类型）
- `GameStart` - 游戏开始
- `DialogComplete` - 对话完成
- `EvidenceCollected` - 证据收集
- `ExposeSuccess` - 指证成功

---

## 🛠️ Unity读取示例

### C# 数据结构定义

```csharp
// Level 1: Unit Metadata
[System.Serializable]
public class UnitMetadata
{
    public string unit_id;
    public LocalizedString unit_name;
    public StoryBackground story_background;
    public LoopStructure loop_structure;
    public List<CharacterInfo> main_characters;
}

// Level 2: Loop Config
[System.Serializable]
public class LoopConfig
{
    public string loop_id;
    public int loop_number;
    public Objectives objectives;
    public List<GamePhase> phases;
    public ExposeConfig expose_config;
}

// Level 3: Dialog
[System.Serializable]
public class DialogConfig
{
    public List<DialogNode> dialogs;
}

[System.Serializable]
public class DialogNode
{
    public string dialog_id;
    public NodeType node_type;
    public string speaker;
    public string text;
    public List<string> next_nodes;
    public List<DialogBranch> branches;
    public DialogRewards rewards;
}

// Level 4: Evidence
[System.Serializable]
public class EvidenceConfig
{
    public List<Evidence> evidences;
}

[System.Serializable]
public class Evidence
{
    public string evidence_id;
    public string name;
    public string category;
    public string description;
    public string collection_method;
    public bool requires_analysis;
    public List<string> related_evidence;
}

// Level 5: Scene
[System.Serializable]
public class SceneConfig
{
    public List<GameScene> scenes;
}

[System.Serializable]
public class GameScene
{
    public string scene_id;
    public string name;
    public string background_image;
    public UnlockCondition unlock_condition;
    public List<Hotspot> hotspots;
    public List<NPCPresence> npcs_present;
}

// Level 6: Expose
[System.Serializable]
public class ExposeConfig
{
    public string expose_id;
    public string target_npc;
    public int total_rounds;
    public List<ExposeRound> rounds;
    public DifficultySettings difficulty_settings;
}
```

### 读取代码示例

```csharp
using YamlDotNet.Serialization;
using System.IO;

public class ConfigLoader
{
    private IDeserializer deserializer;

    public ConfigLoader()
    {
        deserializer = new DeserializerBuilder().Build();
    }

    // 读取Level 1
    public UnitMetadata LoadUnitMetadata(string unitId)
    {
        string path = $"Configs/Level1_{unitId}_Metadata.yaml";
        string yaml = File.ReadAllText(path);
        return deserializer.Deserialize<UnitMetadata>(yaml);
    }

    // 读取Level 2
    public LoopConfig LoadLoopConfig(string loopId)
    {
        string path = $"Configs/Level2_{loopId}_Config.yaml";
        string yaml = File.ReadAllText(path);
        return deserializer.Deserialize<LoopConfig>(yaml);
    }

    // 读取Level 3
    public DialogConfig LoadDialogConfig(string loopId)
    {
        string path = $"Configs/Level3_{loopId}_Dialog.yaml";
        string yaml = File.ReadAllText(path);
        return deserializer.Deserialize<DialogConfig>(yaml);
    }

    // 类似的方法用于Level 4/5/6...
}
```

---

## 🎯 实际使用示例

### 示例1: 添加新场景

**您的需求**：
```
在Loop1添加一个"Morrison的警车"场景，可以搜到赌债欠条（EV010）
```

**AI会做的事**：

1. **修改Level 2** (`Level2_Unit1_Loop1_Config.yaml`)
```yaml
phases:
  - phase_id: P1_Investigation
    available_scenes:
      - SC101
      - SC102
      - SC107  # ← 新增
```

2. **修改Level 5** (`Level5_Unit1_Loop1_Scene.yaml`)
```yaml
scenes:
  - scene_id: SC107
    name: Morrison的警车
    description: 警车停在酒吧外，车门没锁
    background_image: Scenes/Unit1/SC107_PoliceCar.png
    unlock_condition:
      type: DialogComplete
      required_ids:
        - D045
    hotspots:
      - hotspot_id: HS107_001
        type: 搜证
        position: {x: 300, y: 200, width: 100, height: 80}
        interaction_type: Collect
        result:
          evidence_id: EV010  # ← 赌债欠条
```

3. **修改Level 4** (`Level4_Unit1_Loop1_Evidence.yaml`)
```yaml
evidences:
  - evidence_id: EV010
    name: 赌债欠条
    category: 文件
    description: 一张赌场的欠条，借款人是Morrison
    collection_method: 搜证
    source_scene: SC107
    usable_in_expose: true
```

4. **检查Level 6** - 如果指证Rosa时需要用这个证据，更新选项列表

5. **生成Excel预览** - 让您确认改动

---

### 示例2: 修改对话奖励

**您的需求**：
```
D045对话完成后，不解锁SC103，改成解锁SC107
```

**AI会做的事**：

修改Level 3 (`Level3_Unit1_Loop1_Dialog.yaml`)
```yaml
dialogs:
  - dialog_id: D045
    # ... 其他字段 ...
    rewards:
      unlock_scenes:
        - SC107  # ← 原来是SC103
```

然后检查：
- SC107的`unlock_condition`是否依赖D045 ✅
- 如果SC103没有其他解锁途径，警告您

---

### 示例3: 调整指证难度

**您的需求**：
```
Loop1对Rosa的指证，Normal模式改成允许3次重试
```

**AI会做的事**：

修改Level 6 (`Level6_Unit1_Loop1_Expose_Rosa.yaml`)
```yaml
difficulty_settings:
  normal:
    wrong_attempts_allowed: 3  # ← 原来是2
    hint_enabled: true
```

同时检查Level 2中的难度配置是否需要同步更新

---

## ❓ 常见问题

### Q1: 所有字段都必须填吗？
A: 不是。带 `⚠️` 标记的是可选字段，必填字段会标记 `✅`。我会在您创建配置时提醒哪些必填。

### Q2: 如果我引用了一个不存在的ID会怎样？
A: AI会立即检测到并警告您，提示需要先创建对应的配置。

### Q3: 我可以自定义字段吗？
A: 可以！任何 `_` 开头的字段都是自定义备注，程序不会读取。

### Q4: 如何知道我改了哪些Level？
A: 每次修改后，AI会明确列出修改了哪些文件的哪些字段，并解释原因。

### Q5: Excel预览多久更新一次？
A: 每次您让AI修改配置后，AI会自动重新生成Excel预览。

---

## 📌 下一步

### 建议的调整方向

这份文档是初步版本，我们可以一起优化：

1. **字段补充**
   - 是否有遗漏的重要字段？
   - 是否需要添加更多枚举值？
   - 字段类型是否准确？

2. **关系梳理**
   - 跨Level引用关系是否清晰？
   - 是否有特殊的引用场景未覆盖？

3. **示例完善**
   - 需要更多实际操作示例吗？
   - 哪些场景需要详细说明？

4. **Unity集成**
   - C#数据结构是否符合您的项目？
   - 是否需要更多代码示例？

---

**请告诉我**：
- 哪些部分需要调整？
- 哪些字段说明不清楚？
- 是否需要补充新的Level？
- 您在实际使用中会遇到什么场景？

我们一起把这个配置体系调整到最适合您项目的状态！

---

**文档版本**: v1.0
**最后更新**: 2025-11-06
**配套文档**: `01_NDC内容生产工作流.md`