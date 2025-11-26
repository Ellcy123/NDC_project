# NDC 可视化工具 - 数据结构说明

## 概述

本数据结构采用 **实体分离 + ID关联** 的设计理念：
- **循环文件（loops/）** = 骨架，定义流程编排
- **主数据文件（master/）** = 肉，存储实际内容
- 通过 ID 互相引用，实现数据复用和反向查询

---

## 文件结构

```
数据源/
├── _schema.md          # 本文档
├── _index.yaml         # 总索引（网站入口）
│
├── master/             # 主数据（跨循环共享）
│   ├── scenes.yaml     # 场景定义
│   ├── npcs.yaml       # NPC定义
│   ├── evidences.yaml  # 证据定义
│   └── assets.yaml     # 美术资源映射
│
└── Unit1/              # 第一章
    ├── metadata.yaml   # 章节元信息
    ├── loops/          # 循环流程
    │   ├── loop1.yaml
    │   └── loop2.yaml
    └── dialogs/        # 对话文件（按循环分文件夹）
        ├── loop1/      # 循环1的对话
        │   ├── opening.yaml
        │   ├── rosa.yaml
        │   ├── tommy.yaml
        │   └── ending.yaml
        └── loop2/      # 循环2的对话
            ├── opening.yaml
            ├── morrison.yaml
            └── ending.yaml
```

**对话文件夹说明**：
- 每个循环的对话放在独立的 `loop{N}/` 文件夹中
- 文件名无需包含循环号，由文件夹区分
- 例如：`dialogs/loop1/rosa.yaml` 表示循环1的Rosa对话

---

## 主数据文件格式

### scenes.yaml - 场景主表

```yaml
scenes:
  SC1001:                          # 场景ID：SC + 章节 + 序号(2位)
    name: Rosa储藏室               # 中文名称
    name_en: storageroom           # 英文名称（小写连写）
    asset_id: SC001_bg_storageroom # 美术资源ID（美术规范不变）
    description: 酒吧后方的储藏室   # 场景描述
    # 注意：不存储 appears_in，由网站动态计算
```

**字段说明：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 中文场景名称 |
| name_en | string | ✅ | 英文名称（小写连写，如storageroom） |
| asset_id | string | ✅ | 美术资源ID，符合命名规范 |
| description | string | ❌ | 场景描述文本 |

---

### npcs.yaml - NPC主表

```yaml
npcs:
  NPC103:                          # NPC ID：NPC + 章节 + 序号(2位)
    name: Rosa Martinez            # 英文名
    name_cn: 罗莎·马丁内斯          # 中文名
    role: suspect                  # 角色类型
    avatar: Rosa_front_neutral     # 默认立绘

    # 证词列表（按循环组织）
    testimonies:
      loop1:
        - 我一直在地下室酒窖工作，什么都没看到
        - 我当时在后台走廊清洁，但很专心工作
        - 是Morrison警官迷晕了Zack先生

    # 玩家可了解到的NPC信息（按循环组织，每循环最多4条）
    info:
      loop1:
        - 蓝月亮歌舞厅清洁工，夜班23:00-01:00
        - 单身母亲，儿子Miguel患病需要昂贵药物
        - 声称在地下室酒窖工作（实际在后台走廊）
        - 表现紧张，似乎在隐瞒什么

    # 角色描述（上帝视角，策划参考用）
    description:
      - 蓝月亮歌舞厅的清洁女工，有个8岁生病的儿子Miguel
      - 因为经济困境被Morrison威胁配合栽赃
    # 注意：不存储 appears_in，由网站动态计算
```

**info字段规范**：
- 每个循环最多4条信息
- 使用列表格式（`-`开头）
- 内容是玩家通过对话**可以了解到的**信息
- 简洁扼要，每条控制在30字以内

**role 可选值：**
- `protagonist` - 主角
- `partner` - 搭档
- `suspect` - 嫌疑人
- `witness` - 证人
- `victim` - 受害者

---

### evidences.yaml - 证据主表

```yaml
evidences:
  # ===== 第1章 循环1 证据 =====

  EV1111:                          # 证据ID：EV + 章节 + 循环 + 场景 + 序号
    name: 芝加哥警局通缉令          # 中文名称
    name_en: Chicago Police Wanted Poster
    type: envir                    # 证据类型
    description:
      initial: 通缉"疤面Tony"的悬赏金高达5000美元
    asset_id: SC101_clue_01        # 美术资源ID（美术规范不变）
    purpose: 环境叙事，强化1920年代芝加哥黑帮横行的社会背景

  # 可分析证据示例
  EV1114:
    name: 沾有氯仿的毛巾
    name_en: Chloroform-Stained Towel
    type: item
    description:
      initial: 一条普通的白色毛巾
      analyzed: 接近闻嗅时有明显的甜腻化学味，是氯仿的味道，这不是清洁用品
    requires_analysis: true        # 标记为可分析证据
    analysis_action: 接近闻嗅      # 分析操作描述
    result_name: 沾着氯仿的毛巾    # 分析后的显示名称（可选）
    asset_id: SC101_clue_04
    purpose: 否定Rosa"专心清洁，什么都没看到"的目击谎言

  # 密码解谜证据示例
  EV1112:
    name: Rosa的女儿照片
    name_en: Rosa's Daughter Photo
    type: clue
    description:
      initial: 照片背面写着"我的小天使Miguel，妈妈的一切希望"
      analyzed: 上面写女儿的生日0915（工具箱密码线索）
    puzzle:
      type: password_hint          # 密码提示类型
      answer: "0915"
      unlocks: [EV1114, EV1115]    # 解锁的证据
    asset_id: SC101_clue_02
    purpose: 强化Rosa母爱主题，提供密码线索
```

**type 可选值：**
- `item` - 可收集物品
- `clue` - 线索
- `envir` - 环境物品（不可收集）

**method 可选值：**
- `visible` - 直接可见
- `search` - 搜索获取
- `dialog` - 对话获取
- `puzzle` - 解谜获取

**可分析证据字段：**
- `requires_analysis` - 是否需要分析（true/false）
- `analysis_action` - 分析操作描述（如"接近闻嗅"）
- `result_name` - 分析后的显示名称（可选）
- `description.initial` - 分析前描述
- `description.analyzed` - 分析后描述

---

## 循环文件格式

**开篇/结尾可选规则**：
- `opening` 和 `ending` 在循环文件中是**可选的**
- 如果上一循环的ending已包含本循环开篇内容，本循环可以不创建opening对话文件
- 如果本循环的ending已包含下一循环开篇内容，下一循环可以不创建opening对话文件
- **当对话文件缺失时，必须在循环文件中标注缺失原因**，使用 `missing` 字段

### loops/loop1.yaml - 循环流程

```yaml
loop_id: Unit1_Loop1
loop_number: 1
name: Rosa现场目击指证
objective: 到底是谁把我迷晕了？

# ===== 开篇（支持分支对话）=====
opening:
  dialog_file: loop1/opening.yaml
  scenes:
    - id: vip_room
      name: 蓝月亮酒吧·VIP包厢
      dialog_section: vip_room     # 对话文件中的section
    - id: street
      name: 酒吧外的街道
      dialog_section: street

# ===== 本循环场景总览 =====
scenes_overview:
  - scene: SC1001
    name: Rosa储藏室
    status: accessible            # accessible/locked/hidden
    type: search
    note: 可搜索获取证据
  - scene: SC1005
    name: Webb办公室（案发现场）
    status: locked
    type: story
    note: 本循环不可进入

# ===== 自由环节 =====
free_phase:
  scenes:
    - scene: SC1001                # 引用master/scenes.yaml
      type: search
      evidences:                   # 只存储ID和获取方式，名称从evidences.yaml读取
        - id: EV1111
          method: visible          # 获取方式：visible/search/puzzle/dialog
        - id: EV1112
          method: search
          puzzle_hint: 生日0915是密码
        - id: EV1113
          method: search
        - id: EV1114
          method: puzzle
          requires: 密码0915解锁工具箱
        - id: EV1115
          method: puzzle
          requires: 获得毛巾后可见

    - scene: SC1003
      type: npc
      npc: NPC105                  # Tommy
      dialog_file: loop1/tommy.yaml
      evidences:
        - id: EV1133
          method: dialog

    - scene: SC1004
      type: npc
      npc: NPC103                  # Rosa
      dialog_file: loop1/rosa.yaml
      evidences: []

# ===== 指证 =====
expose:
  scene: SC1004
  target: NPC103                   # Rosa

  rounds:
    - round: 1
      lie: Rosa声称在地下室酒窖工作
      evidence: EV1115
      result: 击破地点谎言

    - round: 2
      lie: Rosa声称专心清洁，没看到异常
      evidences: [EV1114, EV1121]
      result: 击破目击谎言

# ===== 结尾（支持分支对话）=====
ending:
  dialog_file: loop1/ending.yaml
  transition_to: Unit1_Loop2
  next_objective: 找到迷晕我的人
```

### opening/ending 缺失的标注示例

**示例1：opening对话文件缺失**

当上一循环的ending已包含本循环开篇内容时，不创建opening对话文件：

```yaml
loop_id: Unit1_Loop3
loop_number: 3
name: Webb的勒索目标调查
objective: Webb在勒索谁？为什么Whale要杀他？

# ===== 开篇 =====
opening:
  missing: true
  reason: Loop2的ending对话已包含前往Webb办公室的场景，直接进入自由环节
  inherited_from: Unit1_Loop2.ending.police_station_exit

# ===== 自由环节 =====
free_phase:
  scenes:
    - scene: SC1008
      name: Webb办公室
      type: search
      # ...
```

**示例2：ending对话文件缺失**

当本循环ending已包含下一循环开篇内容时，下一循环不创建opening对话文件：

```yaml
# ===== 结尾 =====
ending:
  scene: SC1013
  scene_name: 酒吧外街道
  description: 讨论案情并决定下一步行动，已包含下一循环开篇内容
  dialog_file: loop2/ending.yaml
  dialog_section: police_station_exit
  transition_to: Unit1_Loop3
  next_objective: Webb在勒索谁？
  includes_next_loop_opening: true  # 标记：此ending包含下一循环的opening内容
```

**字段说明**：
- `missing: true` - 标记对话文件缺失
- `reason` - 说明缺失原因
- `inherited_from` - 标注内容来源（格式：循环ID.section类型.section名称）
- `includes_next_loop_opening` - 标记ending是否包含下一循环opening内容

---

## 对话文件格式

**核心原则**：
- **dialog文件只包含对话内容**，不包含场景、NPC等元信息
- 场景和NPC信息由 `loops/*.yaml` 定义
- dialog文件通过 `dialog_id`、`loop`、`type` 标识自身
- 使用 `sections` 组织多段对话，每段有独立的描述和对话行

### 普通对话（自由环节）

```yaml
# NDC Episode 1 - 循环1 Rosa对话

dialog_id: loop1_rosa_chat
loop: 1
type: npc_dialog
npc: NPC103                       # 仅用于标识，实际场景信息在loop文件中

sections:
  initial_contact:
    description: 初次接触
    lines:
      - speaker: NPC101
        emotion: direct
        text: "你是这儿的清洁工？"

      - speaker: NPC103
        emotion: nervous
        text: "是...是的，先生。"

  probing:
    description: 试探
    lines:
      - speaker: NPC101
        emotion: skeptical
        text: "整晚？"

      - speaker: NPC103
        emotion: defensive
        text: "对！一直在！我什么都...什么都没看到！"

note: 此对话用于初步了解Rosa，正式指证需要收集足够证据后触发
```

**字段说明**：
- `dialog_id` - 对话唯一标识（格式：loop{N}_{npc/opening/ending/accusation}）
- `loop` - 所属循环编号
- `type` - 对话类型（npc_dialog / opening / ending / accusation）
- `npc` - 相关NPC ID（仅用于标识）
- `sections` - 对话段落，每段包含：
  - `description` - 段落描述
  - `duration` - 预计时长（可选）
  - `lines` - 对话行数组
- `note` - 备注说明（可选）

**对话行字段**：
- `speaker` - 说话者（NPC ID 或 narration）
- `text` - 对话内容
- `emotion` - 情绪标签（可选）
- `action` - 动作描述（可选）

### 开篇/结尾对话（多section）

```yaml
# NDC Episode 1 - 循环1 开篇对话

dialog_id: loop1_opening
loop: 1
type: opening

sections:
  webb_office:
    description: Zack猛然惊醒，发现自己被栽赃
    duration: 约60秒

    lines:
      - speaker: narration
        text: "[Zack猛然惊醒，头痛欲裂，眼神涣散]"

      - speaker: narration
        text: "[看到手中的枪...]"

      - speaker: NPC101
        emotion: confused
        text: "什么...该死..."

      - speaker: narration
        text: "[看到Webb的尸体，Zack猛地甩开枪，惊恐后退]"

  street_meeting:
    description: Zack和Emma初次合作
    duration: 约90秒

    lines:
      - speaker: narration
        text: "[Zack靠着墙，还在喘息，Emma走过来]"

      - speaker: NPC102
        emotion: concerned
        text: "你还好吗？"

      - speaker: NPC101
        emotion: cold
        text: "谢了。"
```

### 指证对话

**重要说明**：
- **指证对话文件只包含对话内容**，使用 `sections` 结构组织
- 指证的元信息（lie、required_evidences、result等）定义在 `loops/*.yaml` 的 `expose` 部分
- 对话文件通过 section 名称与 loop 文件中的轮次对应

```yaml
# NDC Episode 1 - 循环2 指证对话
# 目标：四轮指证击破Morrison谎言，揭露真相

dialog_id: loop2_accusation
loop: 2
type: accusation
target: NPC104                    # 指证目标NPC

sections:
  opening:
    description: Zack进入Morrison办公室，开始对质
    lines:
      - speaker: NPC101
        action: 推门进入
        emotion: cold
        text: "Morrison。"

      - speaker: NPC104
        action: 正在看文件，抬起头
        emotion: dismissive
        text: "Brennan。我办公室不欢迎嫌疑人。"

      - speaker: NPC101
        emotion: determined
        text: "那我们就让证据说话。从你的时间线开始。"

  round1:
    description: 第一轮指证 - 时间线矛盾
    lines:
      - speaker: NPC104
        emotion: defiant
        text: "好。那我告诉你：00:30我接到匿名电话，立即出警..."

      - speaker: NPC101
        emotion: analytical
        text: "很清楚。00:30出发，01:00到达。30分钟。"

      - speaker: NPC101
        emotion: sharp
        text: "所以从你家到蓝月亮酒吧只需要15分钟。剩下的30分钟，你在哪里？"

  round2:
    description: 第二轮指证 - 预谋行为
    lines:
      - speaker: NPC101
        emotion: questioning
        text: "便携式现场勘验箱。你记得吗？"

      - speaker: NPC104
        emotion: dismissive
        text: "我领用装备，关你屁事。"

      - speaker: NPC101
        emotion: sharp
        text: "日期。11月2日，19:30。案发前一天晚上。"

  round3:
    description: 第三轮指证 - 现场操作证据
    lines:
      - speaker: NPC101
        emotion: analytical
        text: "这些压痕，完美契合便携式现场勘验箱的底部。你的箱子，Morrison。"

  round4:
    description: 第四轮指证 - 职业签名致命击破
    lines:
      - speaker: NPC101
        emotion: calm
        text: "Rosa。"

      - speaker: NPC104
        emotion: confused
        text: "什么？"

      - speaker: NPC101
        emotion: revealing
        text: "Rosa一直在现场。她看得很清楚。"

  truth_reveal:
    description: Morrison崩溃坦白，揭露Whale和真相
    lines:
      - speaker: NPC104
        emotion: bitter
        text: "钱？你以为我是为了钱？Brennan，你根本不懂..."

      - speaker: NPC104
        emotion: desperate
        text: "我欠疤面Tony五千美元。他要杀我全家。我老婆，Brennan。我他妈的老婆。"

      - speaker: NPC104
        emotion: defeated
        text: "我只知道他叫Whale。他从不露面。只有纸条，特殊纹样的纸条。"
```

**对应的 loop 文件配置**（`loops/loop2.yaml`）：

```yaml
expose:
  scene: SC1010
  target: NPC104
  total_rounds: 4
  dialog_file: loop2/accusation.yaml

  rounds:
    - round: 1
      name: 时间线矛盾
      lie:
        content: 00:30我接到匿名电话，立即出警
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

    # ... 其他轮次

  truth_revealed: |
    Morrison迷晕Zack并栽赃给他
    他欠疤面Tony 5000美元赌债，被"Whale"收买来栽赃Zack
```

**字段说明**：
- `target` - 指证目标NPC ID
- `sections` - 对话段落
  - `opening` - 开场对质（必需）
  - `round1`、`round2`... - 各轮指证对话（必需，数量与 loop 文件中定义的轮数一致）
  - `truth_reveal` - 真相揭露（可选）
- 每个 section 包含：
  - `description` - 段落描述
  - `lines` - 对话行数组

---

## 对话节点类型

| type | 说明 | 必填字段 |
|------|------|---------|
| (空) | 普通对话 | speaker, text, next |
| `narration` | 旁白/场景描述 | text, next |
| `branch` | 分支选项 | options[] |
| `evidence_gain` | 获得证据 | evidence_id, evidence_name, next |
| `scene_end` | 场景结束 | transition_to |
| `phase_end` | 阶段结束 | transition_to, message |
| `dialog_end` | 对话结束 | message |

**对话节点可选字段**：
- `emotion` - 表情（nervous, angry, sad 等）
- `action` - 动作描述（用方括号包裹）
- `important` - 分支选项的关键标记

---

## ID 命名规范

| 类型 | 格式 | 示例 | 说明 |
|------|------|------|------|
| 场景 | SC + 章节 + 序号(2位) | SC1001, SC1002 | 跨循环共享，不含循环号 |
| NPC | NPC + 章节 + 序号(2位) | NPC101, NPC102 | NPC101 = 第1章 + 第01个NPC |
| 证据 | EV + 章节 + 循环 + 场景 + 序号 | EV1111, EV1121 | 保持场景分组逻辑 |
| 循环 | Unit{N}_Loop{M} | Unit1_Loop1 | 章节N + 循环M |

### ID编号详解

**场景ID (SC)** - 跨循环共享
```
SC1001 = 第1章 + 第01个场景 (Rosa储藏室)
SC1002 = 第1章 + 第02个场景 (歌舞厅一楼走廊)
SC1003 = 第1章 + 第03个场景 (Tommy办公室)
SC2001 = 第2章 + 第01个场景
```
**注意**：同一物理场景在不同循环中共享同一ID

**NPC ID**
```
NPC101 = 第1章 + 第01个NPC (Zack)
NPC102 = 第1章 + 第02个NPC (Emma)
NPC103 = 第1章 + 第03个NPC (Rosa)
NPC201 = 第2章 + 第01个NPC
```

**证据ID (EV)** - 保持场景分组逻辑
```
EV1111 = 第1章 + 第1循环 + 第1场景 + 第1个证据
EV1112 = 第1章 + 第1循环 + 第1场景 + 第2个证据
EV1121 = 第1章 + 第1循环 + 第2场景 + 第1个证据
EV1211 = 第1章 + 第2循环 + 第1场景 + 第1个证据

原始数据映射：
111 → EV1111 (第1章第1循环第1场景第1证据)
121 → EV1121 (第1章第1循环第2场景第1证据)
211 → EV1211 (第1章第2循环第1场景第1证据)
```

---

## 美术资源命名规范

> 完整规范参见：`美术对接文档/美术资产命名规则说明_v2.0.md`

### 场景ID编号

**格式**：`SC` + `循环编号` + `场景固定编号`

```
SC101 = 循环1 + Rosa储藏室（场景固定编号：01）
SC201 = 循环2 + Rosa储藏室（同一场景，固定编号保持：01）
```

### 背景资产

**格式**：`SC00{场景固定编号}_bg_{场景英文名}`

```
SC001_bg_storageroom     → Rosa储藏室背景
SC002_bg_corridor        → 歌舞厅一楼走廊背景
SC003_bg_office          → Tommy办公室背景
SC004_bg_barhall         → 酒吧大堂背景
SC005_bg_crimescene      → Webb办公室（案发现场）背景
```

**命名原则**：
- 使用**英文小写**
- 多单词**连写**（storageroom，不使用storage_room）
- 背景编号最后一位 = 场景固定编号

### 证据资产

**格式**：`SC{循环}{场景}_clue_{编号:2位}`

```
SC101_clue_01      → 循环1-储藏室-证据01
SC101_clue_01_big  → 大图（详细查看）
SC101_clue_01_icon → UI图标
```

### NPC立绘

**格式**：`{角色名}_{角度}_{表情}`

```
Rosa_front_neutral   → Rosa正面中性表情
Rosa_front_nervous   → Rosa正面紧张表情
Jimmy_side_angry     → Jimmy侧面愤怒表情
```

**角度选项**：front（正面）、side（侧面）、back（背面）

---

## 动态计算 vs 静态存储

### 设计原则

**master 文件只存储静态定义**（名称、描述、美术资源ID等）

**统计和关联由网站动态计算**，通过扫描所有 `loops/*.yaml` 生成：
- 场景出现次数
- NPC出现次数
- 证据使用情况
- 指证关联

### 为什么这样设计？

1. **避免重复维护**：改了循环文件，不需要同步更新 master 文件
2. **数据一致性**：统计结果始终与实际内容一致
3. **灵活扩展**：新增循环时只需添加 loop 文件

---

## 查询能力

| 查什么 | 数据来源 | 计算方式 |
|-------|---------|---------|
| 场景出现几次 | 扫描所有 loops/*.yaml | 统计 scene 引用次数 |
| 证据在哪获取 | loops/*.yaml → free_phase.scenes[].evidences | 找到包含该证据的场景 |
| 某循环有哪些场景 | loops/loopN.yaml | 直接读取 free_phase.scenes |
| 某NPC出现在哪 | 扫描所有 loops/*.yaml | 统计 npc 引用次数 |
| 某证据用于哪个指证 | loops/*.yaml → expose.rounds | 找到使用该证据的指证轮次 |
| 美术资源制作状态 | assets.yaml → status | 直接读取（手动更新）|

---

## 版本信息

- **版本**: v1.2
- **更新日期**: 2025-11-25
- **适用范围**: NDC Episode 1-6

### v1.2 更新内容
- ✅ 场景ID改为 SC + 章节 + 序号(2位)，跨循环共享（如SC1001）
- ✅ 证据ID改为 EV + 章节 + 循环 + 场景 + 序号，保持场景分组逻辑（如EV1111）
- ✅ 添加可分析证据字段说明（requires_analysis, analysis_action, result_name）
- ✅ 更新所有示例中的ID引用

### v1.1 更新内容
- ✅ NPC info字段改为列表格式，每循环最多4条
- ✅ 对话文件支持按循环分文件夹（dialogs/loop1/）
- ✅ 开篇和结尾对话支持分支选项
- ✅ 整合美术资源命名规范
