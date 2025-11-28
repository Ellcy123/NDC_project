# Loop配置文件规范（Loops Schema）

## 基本字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `loop_id` | string | ✓ | Loop唯一ID，格式：`Unit{章节}_Loop{循环}` |
| `chapter` | number | ✓ | 章节编号（1-9） |
| `loop_number` | number | ✓ | 循环编号（1-6） |
| `title` | string | ✓ | 循环标题（中文） |
| `title_en` | string | ✓ | 循环标题（英文） |
| `investigation_target` | string | ✓ | 本循环的调查目标 |
| `core_lie` | string |  | 核心谎言描述 |

## 场景总览（scenes_overview）

用于展示本循环可访问的场景列表，包含场景状态和类型信息。

```yaml
scenes_overview:
  - scene: SC1001            # 场景ID（引用master/scenes.yaml）
    name: Rosa储藏室          # 可选：场景名称（用于快速显示）
    status: accessible       # 场景状态：accessible/locked/hidden/story_only
    type: search             # 场景类型：search/npc/story
    note: 可搜索获取证据      # 可选：场景备注
```

**场景状态说明**：
| status值 | 说明 |
|---------|------|
| `accessible` | 可进入探索 |
| `locked` | 锁定，暂时不可进入 |
| `hidden` | 隐藏，玩家不知道 |

**场景类型说明**：
| type值 | 说明 |
|--------|------|
| `search` | 探索场景，可收集证据 |
| `npc` | NPC对话场景 |
| `blank` | 空白场景（可进入但无特殊交互） |

## 开篇（opening）

循环开场剧情配置。可以包含多个场景，按顺序播放。

```yaml
opening:
  description: Zack在案发现场附近醒来，被Emma救出，开始调查
  scenes:
    - scene_id: SC1004           # 场景ID（引用master/scenes.yaml）
      name: Webb会客室            # 可选：场景名称
      description: Zack猛然惊醒，发现自己在案发现场旁  # 场景描述
      dialog_file: loop1/opening.yaml      # 对话文件路径
      dialog_section: webb_office          # 可选：对话section名，不指定则播放所有sections

    # 可以添加多个场景，支持同一地点的多场戏
    - scene_id: SC1013           # 不同地点
      name: 酒吧外街道
      description: Zack和Emma在街道上初次合作
      dialog_file: loop1/opening.yaml
      dialog_section: street_meeting
```

**字段说明**：
- `dialog_section`：可选字段，指定播放对话文件中的哪个section
  - 如果指定，只播放该section的对话
  - 如果不指定，播放对话文件中的所有sections
- 同一个 `scene_id` 可以出现多次，通过不同的 `dialog_section` 实现同一地点的多场戏

## 自由环节（free_phase）

玩家自由探索阶段的场景和证据配置。

```yaml
free_phase:
  description: 玩家可自由探索场景，收集证据和对话
  scenes:
    - scene: SC1001             # 场景ID
      type: search              # 场景类型
      npc: NPC103               # 可选：该场景的NPC ID
      dialog_file: loop1/rosa.yaml  # 可选：对话文件路径
      dialog_section: initial_contact  # 可选：对话section名
      evidences:
        - id: EV1111            # 证据ID
          note: 芝加哥警局通缉令  # 可选：证据备注（用于可视化）
        - id: EV1114
          note: 沾有氯仿的毛巾，需要密码0915解锁工具箱，可分析
```

**字段说明**：
- `dialog_file` + `dialog_section`：指定NPC对话
  - 如果只指定 `dialog_file`，播放所有sections
  - 如果同时指定 `dialog_section`，只播放该section

## 指证环节（expose）

NPC指证环节配置。

```yaml
expose:
  scene: SC1010                    # 指证场景ID
  scene_name: 酒吧大堂              # 可选：场景名称（用于快速显示）
  target: NPC103                   # 指证目标NPC ID
  target_name: Rosa Martinez       # 可选：NPC名称（用于快速显示）
  total_rounds: 3                  # 总轮次数
  total_duration: 54秒             # 可选：总时长
  design_concept: 三次证据否定，层层击破谎言  # 可选：设计理念
  dialog_file: loop1/accusation.yaml  # 指证对话文件路径

  rounds:
    - round: 1
      name: 否定地点谎言
      duration: 22秒              # 可选：本轮时长
      lie:
        content: 我一直在地下室酒窖工作，什么都没看到
      required_evidences: [EV1115]  # 所需证据ID列表
      result: 地点谎言被戳穿，Rosa被迫修正说法
```

## 结尾（ending）

循环结尾剧情配置。

```yaml
ending:
  scene: SC1013                    # 结尾场景ID
  scene_name: 酒吧外街道            # 可选：场景名称
  description: 循环1结束，过渡到循环2
  dialog_file: loop1/ending.yaml   # 结尾对话文件路径
  transition_to: Unit1_Loop2       # 下一循环ID
  next_objective: Morrison为何要陷害我？  # 下一目标
  transition_text: Morrison迷晕了我...他为什么要这么做？这背后一定有更大的阴谋。
```

## 完整示例

```yaml
loop_id: Unit1_Loop1
chapter: 1
loop_number: 1
title: Rosa现场目击指证
title_en: Rosa Eyewitness Accusation

investigation_target: 到底是谁把我迷晕了，还想把杀人的罪名扣在我头上？
core_lie: Rosa声称一直在地下室酒窖工作，什么都没看到

scenes_overview:
  - scene: SC1001
    name: Rosa储藏室
    status: accessible
    type: search
    note: 可搜索获取证据，可与Rosa对话

opening:
  description: Zack在案发现场附近醒来，被Emma救出，开始调查
  scenes:
    - scene_id: SC1004
      name: Webb会客室
      description: Zack猛然惊醒，发现自己在案发现场旁
      dialog_file: loop1/opening.yaml
      dialog_section: webb_office

free_phase:
  description: 玩家可自由探索场景，收集证据和对话
  scenes:
    - scene: SC1001
      type: search
      npc: NPC103
      evidences:
        - id: EV1111
          note: 芝加哥警局通缉令
        - id: EV1114
          note: 沾有氯仿的毛巾，需要密码解锁，可分析

expose:
  scene: SC1010
  scene_name: 酒吧大堂
  target: NPC103
  target_name: Rosa Martinez
  total_rounds: 3
  dialog_file: loop1/accusation.yaml

  rounds:
    - round: 1
      name: 否定地点谎言
      lie:
        content: 我一直在地下室酒窖工作，什么都没看到
      required_evidences: [EV1115]
      result: 地点谎言被戳穿，Rosa被迫修正说法

ending:
  scene: SC1013
  scene_name: 酒吧外街道
  description: 循环1结束，过渡到循环2
  dialog_file: loop1/ending.yaml
  transition_to: Unit1_Loop2
  next_objective: Morrison为何要陷害我？
```

## 注意事项

### 1. 数据职责分离

| 数据类型 | 定义位置 | Loop文件中 |
|---------|---------|-----------|
| 场景详情 | master/scenes.yaml | 只引用ID，可选保留name用于快速显示 |
| NPC详情 | master/npcs.yaml | 只引用ID，可选保留name用于快速显示 |
| 证据详情 | master/evidences.yaml | 只引用ID，可选添加note用于可视化 |
| 证据分析 | master/evidences.yaml | ❌ 不在Loop中定义 |
| 证据解谜 | master/evidences.yaml | ❌ 不在Loop中定义 |
| 流程编排 | Loop文件 | ✅ 核心职责 |

### 2. 文件路径规范

对话文件路径使用相对路径，从Unit目录开始：
- ✅ `loop1/opening.yaml`
- ✅ `loop2/accusation.yaml`
- ❌ `dialogs/loop1/opening.yaml`

### 3. ID引用规范

所有ID引用必须与master文件中的定义保持一致：
- 场景ID格式：`SC{章节}{循环}{场景编号}` （如SC1001）
- NPC ID格式：`NPC{章节}{序号}` （如NPC103）
- 证据ID格式：`EV{章节}{循环}{场景}{序号}` （如EV1114）

## 与其他数据的关联

| 关联数据 | 关联方式 |
|---------|---------|
| 场景定义 | 通过scene ID引用master/scenes.yaml |
| NPC定义 | 通过npc ID引用master/npcs.yaml |
| 证据定义 | 通过evidence ID引用master/evidences.yaml |
| 对话文件 | 通过dialog_file路径引用Unit{N}/dialogs/下的对话文件 |
