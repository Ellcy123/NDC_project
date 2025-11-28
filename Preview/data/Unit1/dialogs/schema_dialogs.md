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
| `speaker` | string | ✓ | 说话者：`NPC{ID}`、`narration`旁白、`player_choice`玩家选择 |
| `text` | string | ✓（选择除外） | 对话文本 |
| `emotion` | string |  | 情绪状态 |
| `action` | string |  | 动作描述 |

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
        emotion: aggressive
        next_section: confrontation

      - text: "用证据戳穿她"
        emotion: cold
        next_section: evidence_route
        required_evidences: [EV1115]  # 需要特定证据才能选择

      - text: "关心她的处境"
        emotion: gentle
        next_section: empathy_route
```

### Options字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | ✓ | 选项文本 |
| `emotion` | string |  | 选择该选项时的情绪 |
| `next_section` | string | ✓ | 跳转到的section名称 |
| `required_evidences` | array |  | 需要的证据ID列表，不满足则不显示该选项 |
| `condition` | string |  | 其他条件（如变量、状态等） |

## 条件Section

某些section可以根据条件自动触发：

```yaml
sections:
  decision_point:
    description: 根据证据情况自动选择路线
    conditions:
      - has_evidence: EV1115
        next_section: evidence_confrontation
      - default: true
        next_section: normal_dialog
    lines: []  # 条件section可以没有对话
```

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
          emotion: aggressive
          next_section: confrontation

        - text: "用工作记录卡戳穿她"
          emotion: cold
          next_section: evidence_confrontation
          required_evidences: [EV1115]

        - text: "询问她女儿的情况"
          emotion: gentle
          next_section: daughter_topic

confrontation:
  description: 直接对峙
  lines:
    - speaker: NPC101
      emotion: sharp
      text: "你在撒谎。"

    - speaker: NPC103
      emotion: panicked
      text: "没有！我真的在地下室！"

evidence_confrontation:
  description: 用证据对峙
  lines:
    - speaker: NPC101
      emotion: cold
      text: "你的工作记录显示你不在地下室。"

    - speaker: NPC103
      emotion: desperate
      text: "那...那是记错了..."

daughter_topic:
  description: 同理心路线
  lines:
    - speaker: NPC101
      emotion: softening
      text: "你孩子多大？"

    - speaker: NPC103
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
      - speaker: NPC101
        emotion: cold
        text: "你说你在地下室，但工作记录显示你在一楼走廊。"

      - speaker: NPC103
        emotion: panicked
        text: "那...那是我记错了..."

  round2:
    description: 第二轮指证 - 否定目击谎言
    lines:
      - speaker: NPC101
        emotion: pressing
        text: "你看到了什么？"

      - speaker: NPC103
        emotion: breaking
        text: "我...我真的什么都没看到..."

  round3:
    description: 第三轮指证 - 揭露真相
    lines:
      - speaker: NPC101
        emotion: firm
        text: "说实话。"

      - speaker: NPC103
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
