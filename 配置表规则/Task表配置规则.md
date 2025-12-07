# Task表配置规则文档

## 概述

Task表分为 **两个子页签**：
- **子页签1 - Task(章节)(循环)**：定义章节和循环级别的宏观任务框架
- **子页签2 - Task(详细)**：定义具体的任务条目

---

## 第一部分：子页签1 - Task(章节)(循环)

### 1.1 字段列表

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| ID | string | 是 | 章节循环ID，格式：`Task` + 章节 + 循环 |
| ChapterTextCn | string | 是 | 主章节任务文本（中文） |
| ChapterTextEn | string | 是 | 主章节任务文本（英文） |
| PhaseGoalCn | string | 是 | 当前循环主任务（中文） |
| PhaseGoalEn | string | 是 | 当前循环主任务（英文） |
| Condition | string | 否 | 完成条件，多个用 `/` 分隔 |
| TaskID | string | 否 | 关联的具体任务ID，多个用 `/` 分隔 |

---

### 1.2 ID命名规则

**格式：`Task` + `章节(1位)` + `循环(1位)`**

| 位置 | 含义 | 说明 |
|------|------|------|
| Task | 固定前缀 | Task |
| 第1位 | 章节 | 1-9 = 第1-9章 |
| 第2位 | 循环 | 1-6 = 循环1-6 |

**示例：**
- `Task11` = 第1章 循环1
- `Task12` = 第1章 循环2
- `Task21` = 第2章 循环1

---

### 1.3 字段说明

| 字段 | 说明 |
|------|------|
| ChapterTextCn/En | 章节主线案件名称（如"谁杀了Webb？"） |
| PhaseGoalCn/En | 当前循环的调查目标（如"谁迷晕了我？"） |
| Condition | 完成该循环的条件，通常为证据ID（如 `EV001/EV002`） |
| TaskID | 该循环包含的具体任务ID列表（如 `Task001/Task002`） |

---

### 1.4 配置示例

```
| ##var  | ID     | ChapterTextCn | ChapterTextEn       | PhaseGoalCn | PhaseGoalEn          | Condition     | TaskID           |
| ##type | string | string        | string              | string      | string               | string        | string           |
| ##     | id     | 主章节任务CnText | 主章节任务EnText       | 当前循环主任务  | 当前循环主任务En        | 条件           | 任务ID            |
| Task11 | 谁杀了Webb？   | Who killed Webb? | 谁迷晕了我？    | Who knocked me out?  | EV001/EV002   | Task001/Task002  |
| Task12 | 谁杀了Webb？   | Who killed Webb? | 揭露Morrison  | Expose Morrison      | EV003/EV004   | Task003/Task004  |
```

---

## 第二部分：子页签2 - Task(详细)

### 2.1 字段列表

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| ID | string | 是 | 任务唯一ID，格式：`Task` + 序号(3位) |
| TaskType | string | 是 | 任务类型（CurrentGoal / Doubt / SideCase） |
| Condition | string | 否 | 触发条件（Event ID） |
| TaskContentCn | string | 是 | 任务内容（中文） |
| TaskContentEn | string | 是 | 任务内容（英文） |

---

### 2.2 ID命名规则

**格式：`Task` + `序号(3位)`**

| 位置 | 含义 | 说明 |
|------|------|------|
| Task | 固定前缀 | Task |
| 序号 | 3位数字 | 001-999 |

**示例：**
- `Task001` = 第1个任务
- `Task010` = 第10个任务

---

### 2.3 TaskType 任务类型

| 类型 | 说明 |
|------|------|
| CurrentGoal | 当前行动目标，下一步需要完成的具体行动 |
| Doubt | 疑点，调查中发现的待解决疑问 |
| SideCase | 支线案件，可选的额外调查内容 |

---

### 2.4 配置示例

```
| ##var  | ID      | TaskType    | Condition | TaskContentCn          | TaskContentEn                    |
| ##type | string  | string      | string    | string                 | string                           |
| ##     | id      | 任务类型     | 条件       |                        |                                  |
| Task001| CurrentGoal | Event001  | 前往Rosa储藏室搜证        | Go to Rosa's storage room        |
| Task002| Doubt       |           | Morrison为何如此确定我是凶手？ | Why is Morrison so sure I'm guilty? |
| Task003| SideCase    | Event002  | Emma的真实目的           | Emma's true purpose              |
```

---

## 第三部分：两个子页签的关系

### 3.1 关联结构

```
┌─────────────────────────────────────────────────────────┐
│  子页签1：Task(章节)(循环) - 宏观框架                      │
├─────────────────────────────────────────────────────────┤
│  Task11 (第1章循环1)                                     │
│    ├─ ChapterText: 谁杀了Webb？    ← 章节主线            │
│    ├─ PhaseGoal: 谁迷晕了我？      ← 循环目标            │
│    ├─ Condition: EV001/EV002      ← 完成条件            │
│    └─ TaskID: Task001/Task002 ────┐ 关联具体任务         │
└───────────────────────────────────│─────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────┐
│  子页签2：Task(详细) - 具体任务                           │
├─────────────────────────────────────────────────────────┤
│  Task001 (CurrentGoal)                                  │
│    ├─ Condition: Event001                               │
│    └─ Content: 前往Rosa储藏室搜证                         │
│                                                         │
│  Task002 (Doubt)                                        │
│    └─ Content: Morrison为何如此确定我是凶手？              │
└─────────────────────────────────────────────────────────┘
```

### 3.2 显示逻辑

| 层级 | 来源 | 显示位置 |
|------|------|----------|
| 章节主线 | 子页签1.ChapterText | 任务面板顶部 |
| 循环目标 | 子页签1.PhaseGoal | 任务面板主目标 |
| 当前行动 | 子页签2.CurrentGoal | 缩略模式优先显示 |
| 疑点 | 子页签2.Doubt | 展开模式显示 |
| 支线 | 子页签2.SideCase | 展开模式显示 |

---

## 4. 注意事项

1. **ID格式区分**：
   - 子页签1：`Task` + 章节 + 循环（2位，如 `Task11`）
   - 子页签2：`Task` + 序号（3位，如 `Task001`）
2. **TaskID关联**：子页签1的 `TaskID` 字段关联子页签2的具体任务
3. **Condition格式**：多个条件用 `/` 分隔
4. **TaskType限定**：只能是 `CurrentGoal` / `Doubt` / `SideCase` 三种
5. **中英文必填**：ChapterText、PhaseGoal、TaskContent 都需要中英文版本

---

## 5. 更新日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v2.0 | 2025-12-07 | 重构为两个子页签结构；ChapterText/PhaseGoal 替代原 MainCase/PhaseGoal；移除进度条相关字段；TaskType 简化为3种类型 |
| v1.0 | 2025-11-29 | 初始版本 |
