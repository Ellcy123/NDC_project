# 对话文件规范（Dialogs Schema）

## 基本字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `dialog_id` | string | ✓ | 对话唯一ID |
| `loop` | number | ✓ | 循环编号 |
| `type` | string | ✓ | 对话类型：`opening`开篇 / `npc_dialog`NPC对话 / `accusation`指证 / `ending`结尾 |
| `npc` | string |  | NPC ID（npc_dialog类型必填） |
| `target` | string |  | 指证目标NPC ID（accusation类型必填） |

## Section结构

对话文件直接使用section名称作为顶层字段，每个section包含：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `description` | string | ✓ | section描述 |
| `lines` | array | ✓ | 对话行数组 |
| `duration` | string |  | 预计时长（如"约60秒"） |

```yaml
# 直接使用section名称作为顶层字段
initial_contact:
  description: 初次接触
  duration: 约60秒  # 可选
  lines:
    - speaker: NPC101
      emotion: direct
      text: "对话内容"

confrontation:
  description: 对峙
  lines:
    - speaker: NPC101
      emotion: sharp
      text: "另一段对话"
```

### Section命名规范

- 使用具体的英文名称，描述该段对话的内容或目的
- 推荐命名：`initial_contact`（初次接触）、`probing`（试探）、`confrontation`（对峙）
- 指证对话使用：`round1`、`round2`、`round3` 等

**注意**：为了兼容性，也支持使用 `sections:` 包裹所有section，但不推荐使用

## Lines字段

每条对话行包含以下字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `talk_id` | int |  | 对话ID，7位数字，用于关联Talk配置表（详见下方ID规则） |
| `speaker` | string | ✓ | 说话者：`NPC{ID}`、`narration`旁白、`player_choice`玩家选择 |
| `text` | string | ✓（选择除外） | 对话文本 |
| `emotion` | string |  | 情绪状态 |
| `action` | string |  | 动作描述 |

### 对话ID规则（talk_id）

**格式：`NNXXYYY`（7位数字）**

| 位置 | 含义 | 说明 |
|------|------|------|
| NN (前1-2位) | 角色编号 | 每个角色有专属编号 |
| XX (中3位) | 对话段落 | 该角色的第几段对话，001=第1段 |
| YYY (后3位) | 句子序号 | 该段对话的第几句，001=第1句 |

**示例：**
- `1001001` = 角色1 的 第1段对话 的 第1句
- `1001015` = 角色1 的 第1段对话 的 第15句
- `3001001` = 角色3 的 第1段对话 的 第1句

**角色编号对照表：**

| 编号 | 角色 | NPC ID |
|------|------|--------|
| 1 | 查克 (Zack Brennan) | NPC101 |
| 2 | 艾玛 (Emma O'Malley) | NPC102 |
| 3 | 罗莎 (Rosa Martinez) | NPC103 |
| 4 | 莫里森夫人 (Mrs. Morrison) | NPC104 |
| 5 | 汤米 (Tommy) | NPC105 |
| 6 | 薇薇安 (Vivian) | NPC106 |
| 7 | 韦伯 (Webb) | NPC107 |
| 8 | 安娜 (Anna) | NPC108 |
| 9 | 吉米 (Jimmy) | NPC109 |

**使用示例：**
```yaml
lines:
  - talk_id: 3001001
    speaker: NPC101
    emotion: direct
    text: "你是这儿的清洁工？"

  - talk_id: 3001002
    speaker: NPC103
    emotion: nervous
    text: "是...是的，先生。"
```

**注意**：`talk_id` 用于导出到 Talk 配置表时的唯一标识，Preview 预览时可选填。

### 情绪状态值（emotion）

常用情绪值：
- `neutral` 中立
- `direct` 直接
- `nervous` 紧张
- `defensive` 防御
- `cold` 冷漠
- `sharp` 尖锐
- `panicked` 恐慌
- `pleading` 恳求

## 玩家选择系统

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
        required_evidences: [EV1115]  # 需要特定证据才能选择

      - text: "关心她的处境"
        next_section: empathy_route
```

### Options字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | ✓ | 选项文本 |
| `next_section` | string | ✓ | 跳转到的section名称 |
| `required_evidences` | array |  | 需要的证据ID列表，不满足则不显示该选项 |
| `condition` | string |  | 其他条件（如变量、状态等） |

## 条件Section（未实现功能）

**状态**：⚠️ 此功能为设计方案，HTML暂未实现

### 设计说明

某些section可以作为"条件决策点"，根据玩家状态（证据、变量等）自动跳转到不同的section。

### 触发机制

条件section通过`next_section`明确指定跳转，不是按YAML定义顺序执行：

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

### Conditions字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `has_evidence` | string |  | 检查是否拥有某证据（如`EV1115`） |
| `has_variable` | string |  | 检查变量条件（如`morrison_trust >= 50`） |
| `default` | boolean |  | 默认路线，所有条件不满足时触发 |
| `next_section` | string | ✓ | 满足条件后跳转的section名称 |

### 命名规范

每个条件section应有独特的描述性名称，推荐格式：**动作_名词**

- ✅ `evidence_check` - 证据检查
- ✅ `relationship_branch` - 关系分支
- ✅ `trust_decision` - 信任决策
- ✅ `finale_route` - 结局路由
- ❌ `decision_point1`, `decision_point2` - 不够描述性

### 完整示例：多条件分支

```yaml
# 初次接触
initial_contact:
  lines:
    - speaker: NPC102
      text: "你想知道什么？"
  next_section: evidence_check  # section结束后跳转

# 条件1：检查证据
evidence_check:
  description: 根据证据数量决定NPC态度
  conditions:
    - has_evidence: EV1115
      next_section: defensive_route
    - default: true
      next_section: relaxed_route
  lines: []

# 防御路线
defensive_route:
  lines:
    - speaker: NPC102
      emotion: tense
      text: "你从哪儿弄到这个的？"
  next_section: relationship_check  # 再次跳转到条件2

# 放松路线
relaxed_route:
  lines:
    - speaker: NPC102
      emotion: casual
      text: "那晚我在巡逻。"
  # 没有next_section，对话结束

# 条件2：检查关系值
relationship_check:
  description: 根据关系值决定结局
  conditions:
    - has_variable: trust >= 50
      next_section: cooperative_ending
    - default: true
      next_section: hostile_ending
  lines: []
```

### 跳转规则总结

1. **不按位置顺序**：section不会自动按YAML定义顺序执行
2. **明确跳转**：通过`next_section`字段明确指定跳转目标
3. **玩家选择跳转**：通过`player_choice`的`options[].next_section`跳转
4. **条件自动判断**：跳转到条件section时，自动判断并再次跳转
5. **结束条件**：如果section没有`next_section`，对话结束

## 完整示例

### 示例1：NPC证词对话（带选择）

```yaml
dialog_id: loop1_rosa_chat
loop: 1
type: npc_dialog
npc: NPC103

# 直接使用section名称作为顶层字段
initial_contact:
  description: 初次接触Rosa
  lines:
    - talk_id: 3001001
      speaker: NPC101
      emotion: direct
      text: "你是这儿的清洁工？"

    - talk_id: 3001002
      speaker: NPC103
      emotion: nervous
      text: "是...是的，先生。"

    - talk_id: 3001003
      speaker: NPC101
      emotion: professional
      text: "昨晚你在哪儿工作？"

    - talk_id: 3001004
      speaker: NPC103
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

        - text: "询问她女儿的情况"
          next_section: daughter_topic

confrontation:
  description: 直接对峙
  lines:
    - talk_id: 3001005
      speaker: NPC101
      emotion: sharp
      text: "你在撒谎。"

    - talk_id: 3001006
      speaker: NPC103
      emotion: panicked
      text: "没有！我真的在地下室！"

evidence_confrontation:
  description: 用证据对峙
  lines:
    - talk_id: 3001007
      speaker: NPC101
      emotion: cold
      text: "你的工作记录显示你不在地下室。"

    - talk_id: 3001008
      speaker: NPC103
      emotion: desperate
      text: "那...那是记错了..."

daughter_topic:
  description: 同理心路线
  lines:
    - talk_id: 3001009
      speaker: NPC101
      emotion: softening
      text: "你孩子多大？"

    - talk_id: 3001010
      speaker: NPC103
      emotion: vulnerable
      text: "八岁...她生病了..."
```

### 示例2：指证对话

```yaml
dialog_id: loop1_accusation
loop: 1
type: accusation
target: NPC103

sections:
  round1:
    description: 第一轮指证 - 否定地点谎言
    lines:
      - talk_id: 3002001
        speaker: NPC101
        emotion: cold
        text: "你说你在地下室，但工作记录显示你在一楼走廊。"

      - talk_id: 3002002
        speaker: NPC103
        emotion: panicked
        text: "那...那是我记错了..."

  round2:
    description: 第二轮指证 - 否定目击谎言
    lines:
      - talk_id: 3002003
        speaker: NPC101
        emotion: pressing
        text: "你看到了什么？"

      - talk_id: 3002004
        speaker: NPC103
        emotion: breaking
        text: "我...我真的什么都没看到..."

  round3:
    description: 第三轮指证 - 揭露真相
    lines:
      - talk_id: 3002005
        speaker: NPC101
        emotion: firm
        text: "说实话。"

      - talk_id: 3002006
        speaker: NPC103
        emotion: confessing
        text: "好吧...是Morrison警官...他威胁我..."
```

## 注意事项

1. **Section命名**：使用描述性的英文名称，而非 section1、section2
2. **Speaker值**：
   - NPC使用ID：`NPC101`、`NPC103`
   - 旁白使用：`narration`
   - 玩家选择使用：`player_choice`
3. **条件判断**：
   - `required_evidences`：需要特定证据才显示选项
   - `condition`：自定义条件（预留，可扩展）
4. **对话跳转**：
   - 通过 `next_section` 实现section之间的跳转
   - 如果section结束后没有跳转，对话结束
5. **Loop文件引用**：
   - 通过 `dialog_file` + `dialog_section` 指定播放哪个section
   - 如果不指定section，播放所有sections（按定义顺序）

## 与其他数据的关联

| 关联数据 | 关联方式 |
|---------|---------|
| Loop配置 | 通过dialog_file和dialog_section引用 |
| NPC定义 | 通过npc/target ID引用master/npcs.yaml |
| 证据定义 | 通过required_evidences引用master/evidences.yaml |
