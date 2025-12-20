# Event表配置规则文档

## 第一部分：配置表字段说明

### 1.1 字段列表

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| EventID | string | 是 | 事件唯一ID，格式：Event + 序号(3位) |
| conditionType | string | 是 | 触发条件类型 |
| condition | string | 是 | 触发条件值 |
| unlockType | string | 是 | 解锁目标类型 |
| unlockID | string | 是 | 解锁目标ID |

---

### 1.2 ID命名规则

**格式：`Event` + `序号(3位)`**

| 位置 | 含义 | 说明 |
|------|------|------|
| Event | 固定前缀 | Event |
| 序号 | 3位数字 | 001-999 |

**示例：**
- `Event001` = 第1个事件

---

### 1.3 conditionType 条件类型

| 类型 | 说明 | condition格式 |
|------|------|---------------|
| ItemC | 物品收集 | 物品ID |
| ItemA | 物品分析 | 物品ID |
| Talk | 完成对话 | npcID,对话ID |
| SceneV | 场景光顾（访问） | 场景ID |
| SceneUL | 场景锁 | 场景ID |
| Puzzle | 完成谜题 | 谜题ID |
| Task | 完成任务 | TaskID |

---

### 1.4 unlockType 解锁类型

| 类型 | 说明 | unlockID格式 |
|------|------|--------------|
| Item | 解锁物品 | 物品ID |
| TalkH | 解锁隐藏对话（少用） | npcID,对话ID |
| TalkS | 解锁人物对话状态（常用） | npcID,状态(1-5) |
| Scene | 解锁场景 | 场景ID |
| Puzzle | 解锁谜题 | 谜题ID |

**TalkS状态说明：**

| 状态值 | 说明 |
|--------|------|
| 1 | 该人物的第1段对话（对应Talk表ID中间三位001） |
| 2 | 该人物的第2段对话（对应Talk表ID中间三位002） |
| 3 | 该人物的第3段对话（对应Talk表ID中间三位003） |
| 4 | 该人物的第4段对话（对应Talk表ID中间三位004） |
| 5 | 该人物的第5段对话（对应Talk表ID中间三位005） |

---

### 1.5 完整配置示例

**对话触发解锁：**
```yaml
- EventID: Event001
  conditionType: Talk
  condition: NPC001,1001001
  unlockType: Item
  unlockID: EV001
```

**物品触发解锁场景：**
```yaml
- EventID: Event002
  conditionType: ItemA
  condition: EV003
  unlockType: Scene
  unlockID: SC1102
```

**场景访问触发解锁对话：**
```yaml
- EventID: Event003
  conditionType: SceneV
  condition: SC1101
  unlockType: TalkH
  unlockID: NPC103,3001010
```

---

## 第二部分：注意事项

1. **ID唯一性**：EventID必须唯一
2. **条件格式**：Talk类型的condition需要用逗号分隔npcID和对话ID
3. **关联一致性**：condition和unlockID中的ID需要与对应表中的ID一致

---

## 第三部分：更新日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2025-11-29 | 初始版本 |
