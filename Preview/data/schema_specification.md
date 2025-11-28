# NDC游戏数据规范完整手册

## 目录

1. [文件组织架构](#文件组织架构)
2. [主数据定义（Master Data）](#主数据定义master-data)
   - [场景规范](#场景规范scenes)
   - [NPC规范](#npc规范npcs)
   - [证据规范](#证据规范evidences)
3. [循环流程定义（Loop Configuration）](#循环流程定义loop-configuration)
4. [对话内容定义（Dialog Content）](#对话内容定义dialog-content)
   - [玩家选择系统](#玩家选择系统)
   - [条件Section系统](#条件section系统)
5. [ID命名规范总览](#id命名规范总览)
6. [数据关联图谱](#数据关联图谱)
7. [完整示例](#完整示例)

---

## 文件组织架构

```
data/
├── Unit1/                          # 第1章数据
│   ├── metadata.yaml               # 章节元信息
│   ├── master/                     # 主数据
│   │   ├── scenes.yaml             # 场景定义
│   │   ├── npcs.yaml               # NPC定义
│   │   └── evidences.yaml          # 证据定义
│   ├── loops/                      # 循环配置
│   │   ├── loop1.yaml              # 循环1配置
│   │   ├── loop2.yaml              # 循环2配置
│   │   └── ...
│   └── dialogs/                    # 对话内容
│       ├── loop1/                  # 循环1对话
│       │   ├── opening.yaml        # 开篇对话
│       │   ├── {npc_name}.yaml     # NPC对话文件
│       │   ├── accusation.yaml     # 指证对话
│       │   └── ending.yaml         # 结尾对话
│       └── loop2/
│           └── ...
└── Unit2/                          # 第2章数据
    └── ...
```

**数据职责分离原则**：
- **Master数据**：定义游戏元素的详细属性（场景、NPC、证据）
- **Loop配置**：定义循环流程编排和引用关系
- **Dialog内容**：定义具体的对话文本和交互逻辑

---

## 主数据定义（Master Data）

### 场景规范（Scenes）

#### 基本字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✓ | 场景中文名称 |
| `name_en` | string | ✓ | 场景英文名称（用于资源ID） |
| `asset_id` | string | ✓ | 美术资源ID，格式：`SC{编号}_bg_{英文名}` |
| `description` | string | ✓ | 场景描述（简短，一句话） |
| `state` | string |  | 场景状态描述（时间、氛围等），如"白天_晴朗" |

#### ID命名规范

```
SC + 章节(1位) + 循环(1位) + 场景编号(2位)
```

**示例**：
- `SC1001` = 第1章 标准场景 01号场景
- `SC1101` = 第1章 循环1特定 01号场景

**重要原则**：
- 优先使用标准场景（循环位=0）
- 只有当循环确实需要不同状态时，才创建循环特定场景

#### 完整示例

```yaml
SC1001:
  name: Rosa储藏室
  name_en: RosaStorageRoom
  asset_id: SC001_bg_RosaStorageRoom
  description: 酒吧后方的储藏室，堆满杂物，是Rosa的私人空间
```

---

### NPC规范（NPCs）

#### 基本字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✓ | NPC英文名（游戏内显示） |
| `name_cn` | string | ✓ | NPC中文名 |
| `role` | string | ✓ | 角色类型：`protagonist`主角 / `partner`伙伴 / `suspect`嫌疑人 / `witness`证人 / `victim`受害者 |
| `description` | string | ✓ | 角色简介（游戏内显示） |

#### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `info.loop{N}` | array | 玩家在该循环可了解的信息（最多4条） |

#### ID命名规范

```
NPC + 章节(1位) + 序号(2位)
```

**示例**：
- `NPC101` = 第1章 第01个NPC
- `NPC103` = 第1章 第03个NPC

#### 角色类型说明

| role值 | 说明 |
|--------|------|
| `protagonist` | 主角（玩家角色） |
| `partner` | 主角伙伴 |
| `suspect` | 嫌疑人（可指证对象） |
| `witness` | 证人（提供证词） |
| `victim` | 受害者 |

#### 完整示例

```yaml
NPC103:
  name: Rosa Martinez
  name_cn: 罗莎·马丁内斯
  role: suspect
  description: 蓝月亮歌舞厅的清洁女工，有个8岁生病的儿子Miguel，因经济困境被Morrison威胁配合栽赃
  info:
    loop1:
      - 蓝月亮歌舞厅清洁工，夜班23:00-01:00
      - 单身母亲，儿子Miguel患病需要昂贵药物
      - 声称在地下室酒窖工作（实际在后台走廊）
      - 表现紧张，似乎在隐瞒什么
    loop2:
      - 被Morrison威胁配合栽赃，内心充满恐惧和愧疚
      - 在Zack的劝说下说出真相
```

---

### 证据规范（Evidences）

#### 基本字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✓ | 证据中文名称 |
| `name_en` | string | ✓ | 证据英文名称（用于资源ID） |
| `type` | string | ✓ | 证据类型：`envir`环境叙事 / `clue`线索 / `item`实体证据 / `note`证词笔记 |
| `description.initial` | string | ✓ | 初始描述文本 |
| `asset_id` | string | ✓ | 美术资源ID |
| `purpose` | string | ✓ | 证据在剧情中的作用说明 |

#### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `analysis.required` | boolean | 是否需要分析 |
| `analysis.action` | string | 触发分析的动作描述 |
| `analysis.result_name` | string | 分析后的证据名称 |
| `analysis.result_description` | string | 分析后的描述文本 |
| `has_puzzle` | boolean | 是否包含解谜玩法 |
| `puzzle_description` | string | 解谜玩法描述 |

#### ID命名规范

```
EV + 章节(1位) + 循环(1位) + 场景(1位) + 序号(1位)
```

**示例**：
- `EV1111` = 第1章 第1循环 第1场景 第1个证据
- `EV1234` = 第1章 第2循环 第3场景 第4个证据

#### 证据类型说明

| type值 | 说明 | 用途 |
|--------|------|------|
| `envir` | 环境叙事 | 背景信息，非指证关键证据 |
| `clue` | 线索 | 需要观察或推理的证据 |
| `item` | 实体证据 | 可拿取的物品，通常是指证核心证据 |
| `note` | 证词笔记 | 对话中获得的证词记录 |

#### 完整示例

```yaml
EV1114:
  name: 沾有氯仿的毛巾
  name_en: Chloroform-Stained Towel
  type: item
  description:
    initial: 一条普通的白色毛巾
  analysis:
    required: true
    action: 接近闻嗅
    result_name: 沾着氯仿的毛巾
    result_description: 接近闻嗅时有明显的甜腻化学味，是氯仿的味道
  asset_id: SC101_clue_04
  purpose: 否定Rosa"专心清洁，什么都没看到"的目击谎言
```

---

## 循环流程定义（Loop Configuration）

### 基本字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `loop_id` | string | ✓ | Loop唯一ID，格式：`Unit{章节}_Loop{循环}` |
| `chapter` | number | ✓ | 章节编号（1-9） |
| `loop_number` | number | ✓ | 循环编号（1-6） |
| `title` | string | ✓ | 循环标题（中文） |
| `title_en` | string | ✓ | 循环标题（英文） |
| `investigation_target` | string | ✓ | 本循环的调查目标 |

### 场景总览（scenes_overview）

```yaml
scenes_overview:
  - scene: SC1001              # 场景ID
    name: Rosa储藏室            # 可选：场景名称
    status: accessible         # 场景状态
    type: search               # 场景类型
    note: 可搜索获取证据        # 可选：备注
```

**场景状态**：
- `accessible` - 可进入探索
- `locked` - 锁定，暂时不可进入
- `hidden` - 隐藏，玩家不知道

**场景类型**：
- `search` - 探索场景，可收集证据
- `npc` - NPC对话场景
- `blank` - 空白场景

### 开篇（opening）

```yaml
opening:
  description: Zack在案发现场附近醒来，被Emma救出
  scenes:
    - scene_id: SC1004
      name: Webb会客室              # 可选
      description: Zack猛然惊醒     # 场景描述
      dialog_file: loop1/opening.yaml
      dialog_section: webb_office   # 可选：指定section，不指定则播放所有
```

**dialog_section字段说明**：
- 如果指定，只播放该section的对话
- 如果不指定，播放对话文件中的所有sections
- 同一个 `scene_id` 可以出现多次，通过不同的 `dialog_section` 实现同一地点的多场戏

### 自由环节（free_phase）

```yaml
free_phase:
  description: 玩家可自由探索场景，收集证据和对话
  scenes:
    - scene: SC1001
      type: search
      npc: NPC103                          # 可选：该场景的NPC ID
      dialog_file: loop1/rosa.yaml         # 可选：对话文件路径
      dialog_section: initial_contact      # 可选：对话section名
      evidences:
        - id: EV1111
          note: 芝加哥警局通缉令           # 可选：证据备注
        - id: EV1114
          note: 沾有氯仿的毛巾，可分析
```

### 指证环节（expose）

```yaml
expose:
  scene: SC1010
  scene_name: 酒吧大堂                     # 可选
  target: NPC103
  target_name: Rosa Martinez               # 可选
  total_rounds: 3
  dialog_file: loop1/accusation.yaml

  rounds:
    - round: 1
      name: 否定地点谎言
      lie:
        content: 我一直在地下室酒窖工作，什么都没看到
      required_evidences: [EV1115]
      result: 地点谎言被戳穿，Rosa被迫修正说法
```

### 结尾（ending）

```yaml
ending:
  scene: SC1013
  scene_name: 酒吧外街道                   # 可选
  description: 循环1结束，过渡到循环2
  dialog_file: loop1/ending.yaml
  transition_to: Unit1_Loop2
  next_objective: Morrison为何要陷害我？
```

---

## 对话内容定义（Dialog Content）

### 基本字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `dialog_id` | string | ✓ | 对话唯一ID |
| `loop` | number | ✓ | 循环编号 |
| `type` | string | ✓ | 对话类型：`opening`开篇 / `npc_dialog`NPC对话 / `accusation`指证 / `ending`结尾 |
| `npc` | string |  | NPC ID（npc_dialog类型必填） |
| `target` | string |  | 指证目标NPC ID（accusation类型必填） |

### Section结构

对话文件直接使用section名称作为顶层字段：

```yaml
initial_contact:
  description: 初次接触
  duration: 约60秒            # 可选
  lines:
    - speaker: NPC101
      emotion: direct
      text: "对话内容"
```

**Section命名规范**：
- 使用具体的英文名称，描述该段对话的内容或目的
- 推荐命名：`initial_contact`、`probing`、`confrontation`
- 指证对话使用：`round1`、`round2`、`round3`

### Lines字段

每条对话行包含：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `speaker` | string | ✓ | 说话者：`NPC{ID}`、`narration`旁白、`player_choice`玩家选择 |
| `text` | string | ✓（选择除外） | 对话文本 |
| `emotion` | string |  | 情绪状态 |
| `action` | string |  | 动作描述 |

**情绪状态值（emotion）**：
- `neutral` 中立
- `direct` 直接
- `nervous` 紧张
- `defensive` 防御
- `cold` 冷漠
- `sharp` 尖锐
- `panicked` 恐慌
- `pleading` 恳求

---

### 玩家选择系统

当 `speaker: player_choice` 时，该行表示玩家选择点：

```yaml
lines:
  - speaker: NPC103
    emotion: nervous
    text: "我...我一直在地下室..."

  # 玩家选择点
  - speaker: player_choice
    options:
      - text: "继续追问"
        next_section: confrontation

      - text: "用证据戳穿她"
        next_section: evidence_route
        required_evidences: [EV1115]        # 需要特定证据才能选择

      - text: "关心她的处境"
        next_section: empathy_route
```

#### Options字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | ✓ | 选项文本 |
| `next_section` | string | ✓ | 跳转到的section名称 |
| `required_evidences` | array |  | 需要的证据ID列表，不满足则不显示该选项 |
| `condition` | string |  | 其他条件（如变量、状态等） |

---

### 条件Section系统

某些section可以作为"条件决策点"，根据玩家状态自动跳转到不同的section。

#### 触发机制

条件section通过`next_section`明确指定跳转：

```yaml
# 普通对话
initial_contact:
  lines:
    - speaker: NPC103
      text: "我一直在地下室..."
    - speaker: player_choice
      options:
        - text: "继续追问"
          next_section: evidence_check  # ✅ 明确跳转到条件section

# 条件决策点 - 玩家看不到，自动判断
evidence_check:
  description: 根据证据情况自动选择路线
  conditions:
    - has_evidence: EV1115
      next_section: evidence_confrontation  # 有证据→跳这里
    - default: true
      next_section: normal_dialog           # 没证据→跳这里
  lines: []  # 条件section不包含对话内容
```

#### Conditions字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `has_evidence` | string |  | 检查是否拥有某证据（如`EV1115`） |
| `has_variable` | string |  | 检查变量条件（如`morrison_trust >= 50`） |
| `default` | boolean |  | 默认路线，所有条件不满足时触发 |
| `next_section` | string | ✓ | 满足条件后跳转的section名称 |

#### 跳转规则总结

1. **不按位置顺序**：section不会自动按YAML定义顺序执行
2. **明确跳转**：通过`next_section`字段明确指定跳转目标
3. **玩家选择跳转**：通过`player_choice`的`options[].next_section`跳转
4. **条件自动判断**：跳转到条件section时，自动判断并再次跳转
5. **结束条件**：如果section没有`next_section`，对话结束

---

## ID命名规范总览

### 场景ID（Scene）

```
SC + 章节(1位) + 循环(1位) + 场景编号(2位)
```

示例：`SC1001`、`SC2102`

### NPC ID

```
NPC + 章节(1位) + 序号(2位)
```

示例：`NPC101`、`NPC215`

### 证据ID（Evidence）

```
EV + 章节(1位) + 循环(1位) + 场景(1位) + 序号(1位)
```

示例：`EV1111`、`EV1234`

### Loop ID

```
Unit{章节}_Loop{循环}
```

示例：`Unit1_Loop1`、`Unit2_Loop3`

### 对话ID（Dialog）

```
loop{循环}_{类型}_{npc名称或描述}
```

示例：`loop1_rosa_chat`、`loop1_accusation`

---

## 数据关联图谱

```
Master Data (主数据定义)
├── scenes.yaml        ←─────┐
├── npcs.yaml          ←───┐ │
└── evidences.yaml     ←─┐ │ │
                          │ │ │
Loop Configuration        │ │ │
└── loop1.yaml            │ │ │
    ├── scenes_overview   │ │ │
    │   └── scene: SC1001 ┼─┘ │
    ├── opening           │   │
    │   └── scene_id ─────┼───┘
    ├── free_phase        │
    │   ├── scene ────────┼───┘
    │   ├── npc: NPC103 ──┼───┘
    │   └── evidences     │
    │       └── id: EV1111┼───┘
    └── expose            │
        ├── scene ────────┼───┘
        ├── target ───────┼───┘
        └── required_evidences
            └── EV1115 ───┼───┘

Dialog Content
└── loop1/
    ├── opening.yaml
    │   └── sections
    │       └── lines
    │           └── speaker: NPC101 ──┐
    │                                 │
    ├── rosa.yaml                     │
    │   └── sections                  │
    │       └── lines                 │
    │           ├── speaker: NPC103 ──┼─→ 引用 npcs.yaml
    │           └── player_choice     │
    │               └── required_evidences
    │                   └── EV1115 ───┼─→ 引用 evidences.yaml
    │                                 │
    └── accusation.yaml               │
        └── sections                  │
            └── lines                 │
                └── speaker: NPC103 ──┘
```

**引用关系说明**：
- Loop配置引用Master数据的所有ID
- Dialog文件引用Master数据中的NPC和Evidence ID
- Loop配置通过`dialog_file`引用Dialog文件

---

## 完整示例

### 示例场景：Rosa储藏室探索

#### 1. Master数据定义

**scenes.yaml**:
```yaml
SC1001:
  name: Rosa储藏室
  name_en: RosaStorageRoom
  asset_id: SC001_bg_RosaStorageRoom
  description: 酒吧后方的储藏室，堆满杂物，是Rosa的私人空间
```

**npcs.yaml**:
```yaml
NPC103:
  name: Rosa Martinez
  name_cn: 罗莎·马丁内斯
  role: suspect
  description: 蓝月亮歌舞厅的清洁女工，有个8岁生病的儿子Miguel
  info:
    loop1:
      - 蓝月亮歌舞厅清洁工，夜班23:00-01:00
      - 单身母亲，儿子Miguel患病需要昂贵药物
```

**evidences.yaml**:
```yaml
EV1115:
  name: Rosa的工作记录卡
  name_en: Rosa's Work Log Card
  type: clue
  description:
    initial: 一张打卡记录，显示Rosa昨晚23:45在一楼后台走廊打卡
  asset_id: SC101_clue_05
  purpose: 否定Rosa"在地下室工作"的谎言

EV1114:
  name: 沾有氯仿的毛巾
  name_en: Chloroform-Stained Towel
  type: item
  description:
    initial: 一条普通的白色毛巾
  analysis:
    required: true
    action: 接近闻嗅
    result_name: 沾着氯仿的毛巾
    result_description: 接近闻嗅时有明显的甜腻化学味，是氯仿的味道
  asset_id: SC101_clue_04
  purpose: 证明有人使用氯仿迷晕他人
```

#### 2. Loop配置

**loop1.yaml**:
```yaml
loop_id: Unit1_Loop1
chapter: 1
loop_number: 1
title: Rosa现场目击指证
title_en: Rosa Eyewitness Accusation
investigation_target: 到底是谁把我迷晕了？

scenes_overview:
  - scene: SC1001
    name: Rosa储藏室
    status: accessible
    type: search
    note: 可搜索获取证据，可与Rosa对话

free_phase:
  description: 玩家可自由探索场景，收集证据和对话
  scenes:
    - scene: SC1001
      type: search
      npc: NPC103
      dialog_file: loop1/rosa.yaml
      dialog_section: initial_contact
      evidences:
        - id: EV1115
          note: Rosa的工作记录卡
        - id: EV1114
          note: 沾有氯仿的毛巾，可分析

expose:
  scene: SC1010
  target: NPC103
  total_rounds: 2
  dialog_file: loop1/accusation.yaml
  rounds:
    - round: 1
      name: 否定地点谎言
      lie:
        content: 我一直在地下室酒窖工作
      required_evidences: [EV1115]
      result: 地点谎言被戳穿
```

#### 3. Dialog内容

**dialogs/loop1/rosa.yaml**:
```yaml
dialog_id: loop1_rosa_chat
loop: 1
type: npc_dialog
npc: NPC103

# 初次接触
initial_contact:
  description: 初次接触Rosa
  lines:
    - speaker: NPC101
      emotion: direct
      text: "你是这儿的清洁工？"

    - speaker: NPC103
      emotion: nervous
      text: "是...是的，先生。"

    - speaker: NPC101
      emotion: professional
      text: "昨晚你在哪儿工作？"

    - speaker: NPC103
      emotion: evasive
      text: "我...我一直在地下室。什么都没看到..."

    # 玩家选择点
    - speaker: player_choice
      options:
        - text: "直接质问她在撒谎"
          next_section: confrontation

        - text: "用工作记录卡戳穿她"
          next_section: evidence_confrontation
          required_evidences: [EV1115]

        - text: "询问她孩子的情况"
          next_section: empathy_route

# 直接对峙路线
confrontation:
  description: 直接对峙
  lines:
    - speaker: NPC101
      emotion: sharp
      text: "你在撒谎。"

    - speaker: NPC103
      emotion: panicked
      text: "没有！我真的在地下室！"

# 证据对峙路线
evidence_confrontation:
  description: 用证据对峙
  lines:
    - speaker: NPC101
      emotion: cold
      text: "你的工作记录显示你不在地下室。"

    - speaker: NPC103
      emotion: desperate
      text: "那...那是记错了..."

# 同理心路线
empathy_route:
  description: 同理心路线
  lines:
    - speaker: NPC101
      emotion: softening
      text: "你孩子多大？"

    - speaker: NPC103
      emotion: vulnerable
      text: "八岁...他生病了..."
```

**dialogs/loop1/accusation.yaml**:
```yaml
dialog_id: loop1_accusation
loop: 1
type: accusation
target: NPC103

round1:
  description: 第一轮指证 - 否定地点谎言
  lines:
    - speaker: NPC101
      emotion: cold
      text: "你说你在地下室，但工作记录显示你在一楼走廊。"

    - speaker: NPC103
      emotion: panicked
      text: "那...那是我记错了..."

round2:
  description: 第二轮指证 - 揭露真相
  lines:
    - speaker: NPC101
      emotion: firm
      text: "说实话。"

    - speaker: NPC103
      emotion: confessing
      text: "好吧...是Morrison警官...他威胁我..."
```

---

## 注意事项

### 数据一致性

1. **ID引用**：所有ID引用必须与Master文件中的定义保持一致
2. **文件路径**：对话文件路径使用相对路径，从Unit目录开始
3. **字段完整性**：必填字段必须填写，可选字段按需使用

### 命名规范

1. **英文名称**：使用驼峰命名（PascalCase），首字母大写
2. **中文描述**：保持简洁，避免冗长
3. **Section命名**：使用描述性的英文名称，而非section1、section2

### 数据职责分离

1. **不要重复定义**：Master数据定义一次，Loop和Dialog只引用ID
2. **保持简洁**：Loop文件可选添加name/note用于快速显示，但不重复完整定义
3. **单一职责**：每个文件类型只负责自己的数据内容

---

**文档版本**：v2.0
**最后更新**：2025-11-28
**相关文档**：
- [场景详细规范](master/schema_scenes.md)
- [NPC详细规范](master/schema_npcs.md)
- [证据详细规范](master/schema_evidences.md)
- [循环详细规范](Unit1/loops/schema_loops.md)
- [对话详细规范](Unit1/dialogs/schema_dialogs.md)
