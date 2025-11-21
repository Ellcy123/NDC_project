# NDC项目配置表扩展建议

## 📋 文档说明

**基于**: 新表结构设计文档 v2.0
**项目**: NDC Episode 1（6循环推理游戏）
**目标**: 在现有三表基础上，补充NDC项目所需的完整配置系统
**版本**: v1.0
**日期**: 2025-11-12

---

## 🎯 现有表结构总结

### ✅ 已有核心三表

1. **Talk表（对话表）** - 存储所有对话内容
2. **NPCStaticData表（角色静态数据表）** - 存储角色基础信息
3. **ItemStaticData表（物品/证据静态数据表）** - 存储证据/物品信息

---

## 🆕 建议新增配置表

### 1. SceneConfig表（场景配置表）

#### 用途
管理游戏中的所有场景信息，包括场景解锁、场景内可获取证据、可对话NPC等。

#### 表结构

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| **id** | string | 场景唯一ID | scene_loop1_rosa_storage |
| **cnName** | string | 场景中文名称 | Rosa储藏室 |
| **enName** | string | 场景英文名称 | Rosa's Storage Room |
| **sceneType** | string | 场景类型<br>`explore` - 可探索<br>`dialogue` - 对话场景<br>`event` - 事件场景 | explore |
| **loopNumber** | int | 所属循环 | 1 |
| **cnDescription** | string | 场景中文描述 | Rosa的清洁工储藏室，堆满了清洁工具和杂物 |
| **enDescription** | string | 场景英文描述 | Rosa's cleaning storage room, filled with cleaning tools and sundries |
| **bgImagePath** | string | 场景背景图路径 | Art/BG/Loop1/RosaStorage |
| **bgMusicPath** | string | 背景音乐路径 | Audio/BGM/Mystery_Theme_01 |
| **availableItems** | string | 可获取证据ID列表（逗号分隔）<br>**注**: 实际获取逻辑由代码管理 | EV001,EV002,EV003,EV004,EV005 |
| **availableNPCs** | string | 可对话NPC ID列表（逗号分隔） | NPC003 |
| **nextScene** | string | 默认下一场景ID | scene_loop1_corridor |

#### 设计说明

**存储内容**：
- 场景的基础展示信息（名称、描述、美术资源）
- 场景内容提示（可获取证据、可对话NPC的ID列表）
- 场景连接关系

**不存储的内容**（由代码管理）：
- ❌ 场景解锁条件（代码根据剧情进度判断）
- ❌ 证据具体获取方式（点击交互逻辑由代码实现）
- ❌ 场景状态标记（已完成、未完成等）

#### 数据示例

```json
{
  "id": "scene_loop1_rosa_storage",
  "cnName": "Rosa储藏室",
  "enName": "Rosa's Storage Room",
  "sceneType": "explore",
  "loopNumber": 1,
  "cnDescription": "Rosa的清洁工储藏室，堆满了清洁工具和杂物",
  "enDescription": "Rosa's cleaning storage room, filled with cleaning tools and sundries",
  "bgImagePath": "Art/BG/Loop1/RosaStorage",
  "bgMusicPath": "Audio/BGM/Mystery_Theme_01",
  "availableItems": "EV001,EV002,EV003,EV004,EV005",
  "availableNPCs": "",
  "nextScene": "scene_loop1_corridor"
}
```

---

### 2. LoopConfig表（循环配置表）

#### 用途
管理游戏的6个调查循环，包括循环目标、开放场景、关键证据等信息。

#### 表结构

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| **id** | int | 循环编号 | 1 |
| **cnName** | string | 循环中文名称 | Rosa现场目击指证 |
| **enName** | string | 循环英文名称 | Rosa's Witness Testimony |
| **cnObjective** | string | 循环调查目标（中文） | 到底是谁把我迷晕了,还想把杀人的罪名扣在我头上? |
| **enObjective** | string | 循环调查目标（英文） | Who drugged me and tried to frame me for murder? |
| **cnSummary** | string | 循环简介（中文） | Zack开始调查自己是怎么被陷害的... |
| **enSummary** | string | 循环简介（英文） | Zack begins investigating how he was framed... |
| **keyNPC** | string | 关键NPC ID | NPC003 |
| **keyEvidence** | string | 关键证据ID列表（逗号分隔） | EV004,EV005,EV006,EV007 |
| **openScenes** | string | 开放场景ID列表（逗号分隔） | scene_loop1_rosa_storage,scene_loop1_corridor,scene_loop1_tommy_office,scene_loop1_bar_hall |
| **exposureRounds** | int | 指证轮数 | 3 |
| **nextLoop** | int | 下一循环编号（0表示结束） | 2 |

#### 设计说明

**存储内容**：
- 循环的基础信息（名称、目标、简介）
- 循环相关的关键元素（关键NPC、关键证据、开放场景）
- 循环流程提示（指证轮数、下一循环）

**不存储的内容**（由代码管理）：
- ❌ 循环解锁条件
- ❌ 循环完成判定逻辑
- ❌ 证据收集进度追踪

#### 数据示例

```json
{
  "id": 1,
  "cnName": "Rosa现场目击指证",
  "enName": "Rosa's Witness Testimony",
  "cnObjective": "到底是谁把我迷晕了,还想把杀人的罪名扣在我头上?",
  "enObjective": "Who drugged me and tried to frame me for murder?",
  "cnSummary": "Zack开始调查自己是怎么被陷害的。通过指证清洁女工Rosa，最终揭露Morrison警官才是陷害的幕后黑手。",
  "enSummary": "Zack begins investigating how he was framed. By confronting Rosa the janitor, he ultimately reveals Officer Morrison as the mastermind behind the setup.",
  "keyNPC": "NPC003",
  "keyEvidence": "EV004,EV005,EV006,EV007",
  "openScenes": "scene_loop1_rosa_storage,scene_loop1_corridor,scene_loop1_tommy_office,scene_loop1_bar_hall",
  "exposureRounds": 3,
  "nextLoop": 2
}
```

---

### 3. ExposureConfig表（指证配置表）

#### 用途
配置每个循环的指证系统，包括指证轮次、使用证据、预期对话等。

#### 表结构

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| **id** | string | 指证配置ID | exposure_loop1_round1 |
| **loopNumber** | int | 所属循环 | 1 |
| **roundNumber** | int | 指证轮次 | 1 |
| **targetNPC** | string | 指证目标NPC ID | NPC003 |
| **cnRoundTitle** | string | 轮次标题（中文） | 第一轮指证：否定地点谎言 |
| **enRoundTitle** | string | 轮次标题（英文） | Round 1: Refute Location Lie |
| **requiredEvidence** | string | 需要使用的证据ID列表（逗号分隔） | EV005 |
| **cnHint** | string | 提示文本（中文） | Rosa声称自己在地下室酒窖工作... |
| **enHint** | string | 提示文本（英文） | Rosa claims she was working in the basement wine cellar... |
| **correctResult** | string | 指证成功后的结果描述 | 击破地点谎言，Rosa承认在后台走廊工作 |
| **nextRound** | string | 下一轮指证ID（0表示结束） | exposure_loop1_round2 |
| **dialoguePath** | string | 关联对话ID范围（用于快速定位） | 001003010-001003015 |

#### 设计说明

**存储内容**：
- 指证的基础信息（轮次、目标NPC）
- 指证提示和结果描述
- 证据关联（需要使用哪些证据）

**不存储的内容**（由代码管理）：
- ❌ 证据选择判定逻辑
- ❌ 指证成功/失败处理
- ❌ 对话触发控制

---

### 4. TutorialConfig表（教程配置表）

#### 用途
管理游戏教程和提示系统。

#### 表结构

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| **id** | string | 教程ID | tutorial_exposure_system |
| **cnTitle** | string | 教程标题（中文） | 如何进行指证 |
| **enTitle** | string | 教程标题（英文） | How to Make Accusations |
| **cnContent** | string | 教程内容（中文） | 选择合适的证据进行指证... |
| **enContent** | string | 教程内容（英文） | Select appropriate evidence to make accusations... |
| **imagePath** | string | 教程配图路径 | Art/UI/Tutorial/Exposure_Guide |
| **triggerType** | string | 触发类型<br>`auto` - 自动触发<br>`manual` - 手动触发 | auto |
| **priority** | int | 优先级（数字越大越优先） | 1 |

---

### 5. UITextConfig表（UI文本配置表）

#### 用途
统一管理游戏中所有UI相关的文本，便于本地化和修改。

#### 表结构

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| **id** | string | 文本ID | ui_button_confirm |
| **cnText** | string | 中文文本 | 确认 |
| **enText** | string | 英文文本 | Confirm |
| **category** | string | 分类<br>`button` - 按钮文本<br>`menu` - 菜单文本<br>`system` - 系统提示<br>`ui` - 界面文本 | button |
| **description** | string | 说明 | 确认按钮通用文本 |

#### 常用分类示例

**按钮类**：
- 确认、取消、返回、继续、跳过、保存、加载

**菜单类**：
- 开始游戏、继续游戏、设置、退出

**系统提示类**：
- 保存成功、加载失败、确认退出

**UI界面类**：
- 证据、线索、人物、场景、目标

---

### 6. AudioConfig表（音频配置表）

#### 用途
管理游戏中的音效和BGM资源路径。

#### 表结构

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| **id** | string | 音频ID | bgm_mystery_theme_01 |
| **cnName** | string | 音频中文名称 | 悬疑主题曲1 |
| **enName** | string | 音频英文名称 | Mystery Theme 01 |
| **audioType** | string | 音频类型<br>`bgm` - 背景音乐<br>`sfx` - 音效<br>`voice` - 语音<br>`ambient` - 环境音 | bgm |
| **path** | string | 音频文件路径 | Audio/BGM/Mystery_Theme_01 |
| **volume** | float | 默认音量（0-1） | 0.7 |
| **loop** | bool | 是否循环 | true |
| **fadeIn** | float | 淡入时长（秒） | 1.0 |
| **fadeOut** | float | 淡出时长（秒） | 1.0 |

---

### 7. AchievementConfig表（成就配置表）

#### 用途
配置游戏成就系统。

#### 表结构

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| **id** | string | 成就ID | achievement_complete_loop1 |
| **cnName** | string | 成就中文名称 | 揭穿陷阱 |
| **enName** | string | 成就英文名称 | Expose the Setup |
| **cnDescription** | string | 成就中文描述 | 完成循环1，揭露Morrison的栽赃行为 |
| **enDescription** | string | 成就英文描述 | Complete Loop 1 and expose Morrison's frame-up |
| **iconPath** | string | 成就图标路径 | Art/UI/Achievement/Loop1_Complete |
| **points** | int | 成就点数 | 10 |
| **hidden** | bool | 是否隐藏成就 | false |

---

## 📊 完整配置表体系架构

```
NDC配置表体系
├── 核心三表（已完成）
│   ├── Talk表 - 对话内容
│   ├── NPCStaticData表 - 角色数据
│   └── ItemStaticData表 - 证据/物品数据
│
├── 游戏结构配置
│   ├── LoopConfig表 - 循环配置
│   ├── SceneConfig表 - 场景配置
│   └── ExposureConfig表 - 指证配置
│
├── 系统功能配置
│   ├── UITextConfig表 - UI文本
│   ├── AudioConfig表 - 音频配置
│   ├── TutorialConfig表 - 教程配置
│   └── AchievementConfig表 - 成就配置
│
└── 代码管理的逻辑（不在配置表）
    ├── 解锁条件判定
    ├── 游戏进度追踪
    ├── 证据分析系统
    ├── 指证判定逻辑
    └── 剧情分支控制
```

---

## 🎯 配置表使用优先级

### 必须立即实现（P0）
1. **Talk表** - 游戏核心对话系统
2. **NPCStaticData表** - 角色信息展示
3. **ItemStaticData表** - 证据系统基础
4. **LoopConfig表** - 循环流程管理
5. **SceneConfig表** - 场景管理

### 建议尽快实现（P1）
6. **ExposureConfig表** - 指证系统配置
7. **UITextConfig表** - 文本统一管理
8. **AudioConfig表** - 音频资源管理

### 可延后实现（P2）
9. **TutorialConfig表** - 新手教程
10. **AchievementConfig表** - 成就系统

---

## 💡 实施建议

### 阶段一：核心配置（已完成）
- ✅ Talk表
- ✅ NPCStaticData表
- ✅ ItemStaticData表

### 阶段二：游戏结构配置（建议优先）
1. 创建 **LoopConfig表**，配置6个循环的基础信息
2. 创建 **SceneConfig表**，配置所有场景信息
3. 创建 **ExposureConfig表**，配置指证系统

### 阶段三：系统功能配置
1. 创建 **UITextConfig表**，统一管理UI文本
2. 创建 **AudioConfig表**，管理音频资源
3. 根据需要添加教程和成就配置

---

## 🔧 技术实施要点

### 1. 数据关联方式
配置表之间通过ID字符串关联，不使用外键：
```
LoopConfig.keyNPC = "NPC003" → NPCStaticData.id
LoopConfig.openScenes = "scene_loop1_rosa_storage" → SceneConfig.id
ExposureConfig.requiredEvidence = "EV005" → ItemStaticData.id
```

### 2. 列表字段处理
使用逗号分隔的字符串存储ID列表，代码端解析：
```json
{
  "availableItems": "EV001,EV002,EV003",  // 配置表存储
  // 代码端：string[] items = availableItems.Split(',');
}
```

### 3. 本地化支持
所有需要展示给玩家的文本都提供中英文双版本：
- cnName / enName
- cnDescription / enDescription
- cnObjective / enObjective

### 4. 资源路径规范
统一使用相对路径，从Assets的子目录开始：
```
Art/UI/Character/Zack
Audio/BGM/Mystery_Theme_01
Art/BG/Loop1/RosaStorage
```

---

## 📝 配置表文件命名规范

建议的文件命名：
```
配置表/
├── Episode1_LoopConfig表.md
├── Episode1_SceneConfig表.md
├── Episode1_ExposureConfig表.md
├── Episode1_UITextConfig表.md
├── Episode1_AudioConfig表.md
├── Episode1_TutorialConfig表.md
└── Episode1_AchievementConfig表.md
```

---

## ⚠️ 注意事项

### 数据与逻辑分离原则
**配置表只存储静态展示数据，游戏逻辑由代码管理**

**举例说明**：

❌ **错误做法** - 在配置表中存储逻辑
```json
{
  "unlockCondition": "loop1_complete AND evidence_count >= 8",
  "analysisLogic": "if(hasChloroform) then showAnalyzedDescription"
}
```

✅ **正确做法** - 配置表只存储数据
```json
{
  "loopNumber": 1,
  "requiredEvidence": "EV004,EV005",
  "cnDescribe1": "初始描述",
  "cnDescribe2": "分析后描述"
}
```

### 扩展性考虑
所有表结构都支持灵活扩展：
- 添加新字段直接在表末尾添加新列
- 旧数据自动填充默认值（空字符串或0）
- 不影响现有数据和代码

---

## 📈 配置表工作量预估

| 配置表 | 预估记录数 | 工作量 | 优先级 |
|--------|-----------|--------|--------|
| Talk表 | 800-1000条 | 大 | P0 ✅ |
| NPCStaticData表 | 10-15条 | 小 | P0 ✅ |
| ItemStaticData表 | 50-70条 | 中 | P0 ✅ |
| LoopConfig表 | 6条 | 小 | P0 |
| SceneConfig表 | 25-30条 | 中 | P0 |
| ExposureConfig表 | 15-20条 | 中 | P1 |
| UITextConfig表 | 100-150条 | 中 | P1 |
| AudioConfig表 | 40-60条 | 小 | P1 |
| TutorialConfig表 | 10-15条 | 小 | P2 |
| AchievementConfig表 | 15-20条 | 小 | P2 |

---

## 🎉 总结

基于现有的新表结构设计，NDC项目建议扩展**7个额外配置表**：

1. **LoopConfig表** - 管理6循环结构
2. **SceneConfig表** - 管理场景信息
3. **ExposureConfig表** - 管理指证系统
4. **UITextConfig表** - 管理UI文本
5. **AudioConfig表** - 管理音频资源
6. **TutorialConfig表** - 管理教程系统
7. **AchievementConfig表** - 管理成就系统

这套配置表体系：
- ✅ 遵循数据与逻辑分离原则
- ✅ 完整支持双语本地化
- ✅ 结构清晰易于维护
- ✅ 支持灵活扩展
- ✅ 与现有三表无缝集成

---

**文档状态**: ✅ 建议方案完成
**下一步**: 根据优先级逐步创建新配置表
