# Task表配置规则文档

## 第一部分：配置表字段说明

### 1.1 字段列表

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| taskId | string | 是 | 任务唯一ID，格式：TAS + 序号(3位) |
| taskType | string | 是 | 任务类型（MainCase/PhaseGoal/CurrentGoal/Doubt/SideCase） |
| sectionId | string | 是 | 子章节ID，如 SEC01 = 循环1 |
| priority | number | 是 | 显示优先级（数值越大越优先） |
| cnTitle | string | 是 | 中文标题 |
| enTitle | string | 是 | 英文标题 |
| showProgressBar | boolean | 是 | 是否显示进度条 |
| progressType | string | 否 | 进度类型（如 evidence_collection） |
| progressTotal | number | 否 | 进度总数 |
| requiredEvidences | string | 否 | 需要的证据列表（多个用逗号分隔） |

---

### 1.2 ID命名规则

**格式：`TAS` + `序号(3位)`**

| 位置 | 含义 | 说明 |
|------|------|------|
| TAS | 固定前缀 | Task |
| 序号 | 3位数字 | 001-999 |

**示例：**
- `TAS001` = 第1个任务
- `TAS010` = 第10个任务

---

### 1.3 taskType 任务类型

| 类型 | 说明 | 默认优先级 | 最大显示数 |
|------|------|-----------|-----------|
| MainCase | 章节主线案件 | 100 | 1 |
| PhaseGoal | 循环目标 | 90 | 1 |
| CurrentGoal | 当前行动目标 | 80-85 | 1 |
| Doubt | 疑点 | 70 | 6 |
| SideCase | 支线案件 | 60 | 2 |

---

### 1.4 priority 优先级说明

| 范围 | 对应类型 |
|------|---------|
| 100 | MainCase |
| 90 | PhaseGoal |
| 80-89 | CurrentGoal |
| 70 | Doubt |
| 60 | SideCase |

**显示逻辑：**
- 缩略模式：优先显示 CurrentGoal → PhaseGoal → MainCase
- 展开模式：按 PhaseGoal → CurrentGoal → Doubt → SideCase 顺序

---

### 1.5 进度条相关字段

| 字段 | 说明 |
|------|------|
| showProgressBar | true=显示进度条，false=不显示 |
| progressType | 进度类型，如 evidence_collection（证据收集） |
| progressTotal | 进度总数（如需要收集5个证据则填5） |
| requiredEvidences | 需要的证据ID列表，逗号分隔 |

---

### 1.6 完整配置示例

**MainCase（章节主线）：**
```yaml
- taskId: TAS001
  taskType: MainCase
  sectionId: SEC01
  priority: 100
  cnTitle: 蓝月亮歌舞厅谋杀案
  enTitle: Blue Moon Ballroom Murder Case
  showProgressBar: false
```

**PhaseGoal（循环目标，带进度条）：**
```yaml
- taskId: TAS002
  taskType: PhaseGoal
  sectionId: SEC01
  priority: 90
  cnTitle: 调查Rosa的证词
  enTitle: Investigate Rosa's Testimony
  showProgressBar: true
  progressType: evidence_collection
  progressTotal: 5
  requiredEvidences: EV001, EV002, EV003, EV004, EV007
```

**CurrentGoal（当前行动目标）：**
```yaml
- taskId: TAS003
  taskType: CurrentGoal
  sectionId: SEC01
  priority: 85
  cnTitle: 前往歌舞厅外的街道
  enTitle: Go to the Street Outside the Ballroom
  showProgressBar: false
```

**Doubt（疑点）：**
```yaml
- taskId: TAS009
  taskType: Doubt
  sectionId: SEC01
  priority: 70
  cnTitle: Morrison为何如此确定我是凶手？
  enTitle: Why is Morrison so sure I'm the killer?
  showProgressBar: false
```

**SideCase（支线案件）：**
```yaml
- taskId: TAS013
  taskType: SideCase
  sectionId: SEC01
  priority: 60
  cnTitle: Emma的真实目的
  enTitle: Emma's True Purpose
  showProgressBar: false
```

---

## 第二部分：注意事项

1. **ID唯一性**：taskId必须唯一
2. **优先级规则**：同类型任务优先级越高越先显示
3. **进度条**：只有PhaseGoal类型通常需要显示进度条
4. **证据关联**：requiredEvidences中的证据ID需要与Item表中的证据ID对应

---

## 第三部分：更新日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2025-11-29 | 初始版本 |
