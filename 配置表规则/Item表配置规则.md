# Item表配置规则文档

## 1. 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 物品唯一ID，导表时通过id索引（类似primaryKey） |
| cnName | string | 是 | 中文名字 |
| enName | string | 是 | 英文名字 |
| itemType | string | 是 | 物品分类，详见类型说明 |
| canCollected | int | 是 | 能否被收集（1=是，0=否） |
| canAnalyzed | int | 是 | 能否被分析（1=是，0=否） |
| canCombined | int | 是 | 能否被合并（1=是，0=否） |
| combineParameter0 | string | 否 | 合并需要用到的物品ID |
| combineParameter1 | string | 否 | 合并后生成的物品ID |
| cnDescribe1 | string | 是 | 中文描述（初始状态） |
| cnDescribe2 | string | 否 | 中文描述（分析后状态，canAnalyzed=1时展示） |
| cnDescribe3 | string | 否 | 中文描述（备用） |
| enDescribe1 | string | 是 | 英文描述（初始状态） |
| enDescribe2 | string | 否 | 英文描述（分析后状态） |
| enDescribe3 | string | 否 | 英文描述（备用） |
| path1 | string | 否 | 物品美术资源存储路径（优先使用，前期可用编辑器现有资源） |
| path2 | string | 否 | 其他美术资源路径2 |
| path3 | string | 否 | 其他美术资源路径3 |
| parameter | string | 否 | JudgeCondition 判断的事件ID |

---

## 2. ID命名规则

**格式：`EV` + `章节(1位)` + `循环(1位)` + `场景(1位)` + `序号(1位)`**

| 位置 | 含义 | 说明 |
|------|------|------|
| EV | 固定前缀 | Evidence（证据） |
| 第1位 | 章节 | 1=第1章 |
| 第2位 | 循环 | 1-6=循环1-6 |
| 第3位 | 场景 | 场景编号 |
| 第4位 | 序号 | 该场景内的序号 |

**示例：**
- `EV1111` = 第1章 循环1 场景1 第1个证据
- `EV1114` = 第1章 循环1 场景1 第4个证据
- `EV1221` = 第1章 循环2 场景2 第1个证据
- `EV1511` = 第1章 循环5 场景1 第1个证据

---

## 3. itemType物品类型

| 类型 | 说明 | canCollected | 示例 |
|------|------|--------------|------|
| item | 可收集的物品 | 1 | 毛巾、工作记录卡、氯仿瓶 |
| clue | 线索 | 1 | 拖拽痕迹、VIP客户照片 |
| note | 证词/笔记 | 1 | Tommy时间证词、Rosa目击证词 |
| envir | 环境物品 | 0 | 通缉令、功勋奖章（只能查看不能收集） |

---

## 4. 物品交互机制

### 4.1 分析机制（canAnalyzed）

当 `canAnalyzed = 1` 时，玩家可以对物品进行分析操作。

分析后：
- 显示 `cnDescribe2`/`enDescribe2` 替代初始描述
- 物品名称可能变化（如"毛巾" → "沾着氯仿的毛巾"）

**示例：**
```yaml
- id: EV1114
  cnName: 毛巾
  enName: Chloroform-Stained Towel
  itemType: item
  canCollected: 1
  canAnalyzed: 1
  canCombined: 0
  cnDescribe1: 一条普通的白色毛巾
  cnDescribe2: 一条白色毛巾，散发着刺鼻的甜腻气味，是氯仿的味道
  enDescribe1: An ordinary white towel
  enDescribe2: A white towel with a pungent sweet smell, it's chloroform
```

### 4.2 合并机制（canCombined）

当 `canCombined = 1` 时，物品可以与其他物品合并。

| 参数 | 说明 |
|------|------|
| combineParameter0 | 合并所需的**所有物品ID（包括自己）** |
| combineParameter1 | 合并后生成的新物品ID |

**示例：分手信合并**
```yaml
# 分手信信件
- id: EV1511
  cnName: 分手信信件
  itemType: item
  canCombined: 1
  combineParameter0: EV1511/EV1512    # 包括自己和信封
  combineParameter1: EV1513

# 分手信信封
- id: EV1512
  cnName: 分手信信封
  itemType: item
  canCombined: 1
  combineParameter0: EV1511/EV1512    # 包括信件和自己
  combineParameter1: EV1513

# 合并后：给Webb的分手信
- id: EV1513
  cnName: 给Webb的分手信
  itemType: item
  canCombined: 0
  cnDescribe1: Vivian亲笔写的分手信，"我已经受够了，我们之间结束了"
```

**注意：** combineParameter0 中用 `/` 分隔多个物品ID，必须包含自己的ID。

### 4.3 事件触发（parameter）

`parameter` 字段用于关联 JudgeCondition 事件ID，当物品被获取或使用时触发相应事件。

```yaml
- id: EV1122
  cnName: 地板拖拽痕迹
  itemType: clue
  parameter: EVT_DRAG_FOUND
```

---

## 5. 常见配置模式

### 5.1 普通可收集物品

```yaml
- id: EV1115
  cnName: 工作记录卡
  enName: Work Record Card
  itemType: item
  canCollected: 1
  canAnalyzed: 0
  canCombined: 0
  cnDescribe1: Rosa Martinez - 11月15日夜班：后台走廊清洁 23:00-01:00
  enDescribe1: Rosa Martinez - Night shift Nov 15: Backstage corridor cleaning 23:00-01:00
  path1: Art/UI/Item/WorkCard
```

### 5.2 需要分析的物品

```yaml
- id: EV1122
  cnName: 地板拖拽痕迹
  enName: Floor Drag Marks
  itemType: clue
  canCollected: 1
  canAnalyzed: 1
  canCombined: 0
  cnDescribe1: 地板上的拖拽痕迹
  cnDescribe2: 压痕较深，被拖动的东西至少150磅，普通女性的力量基本无法完成
  enDescribe1: Drag marks on the floor
  enDescribe2: Deep indentations, dragged object weighs at least 150 pounds
```

### 5.3 环境物品（不可收集）

```yaml
- id: EV1111
  cnName: 芝加哥警局通缉令
  enName: Chicago Police Wanted Poster
  itemType: envir
  canCollected: 0
  canAnalyzed: 0
  canCombined: 0
  cnDescribe1: 通缉"疤面Tony"的悬赏金高达5000美元
  enDescribe1: Wanted poster for "Scarface Tony" with a bounty of $5,000
```

### 5.4 证词/笔记

```yaml
- id: EV1133
  cnName: Tommy时间证词
  enName: Tommy's Time Testimony
  itemType: note
  canCollected: 1
  canAnalyzed: 0
  canCombined: 0
  cnDescribe1: 确实有一声枪响...但这声枪响和平时黑帮火拼的声音不太一样，只听到了一声
  enDescribe1: Indeed there was a gunshot... but different from usual gang firefights
```

---

## 第二部分：与 evidences.yaml 的对应关系

### 2.1 文件说明

| 文件 | 位置 | 用途 |
|------|------|------|
| ItemStaticData.yaml | D:\NDC_project\story\ | 配置表（Excel转换） |
| evidences.yaml | D:\NDC_project\Preview\data\master\ | Preview网站使用的数据 |

---

### 2.2 字段对应关系

| ItemStaticData（配置表） | evidences.yaml（Preview） | 说明 |
|-------------------------|--------------------------|------|
| id | 键名（如 EV1111） | ID格式相同 |
| cnName | name | 中文名 |
| enName | name_en | 英文名 |
| itemType | type | 物品类型 |
| cnDescribe1 | description.initial | 初始描述 |
| cnDescribe2 | analysis.result_description | 分析后描述 |
| canAnalyzed | analysis.required | 是否需要分析 |
| - | analysis.action | Preview特有，分析动作描述 |
| - | analysis.result_name | Preview特有，分析后名称 |
| - | asset_id | Preview特有，资源ID |
| - | purpose | Preview特有，设计目的 |
| - | has_puzzle | Preview特有，是否有谜题 |
| - | puzzle_description | Preview特有，谜题描述 |

---

### 2.3 type字段对应

| ItemStaticData.itemType | evidences.yaml.type |
|------------------------|---------------------|
| item | item |
| clue | clue |
| note | note |
| envir | envir |

---

### 2.4 转换对照示例

**配置表（ItemStaticData.yaml）：**
```yaml
- id: EV1114
  cnName: 毛巾
  enName: Chloroform-Stained Towel
  itemType: item
  canCollected: 1
  canAnalyzed: 1
  canCombined: 0
  cnDescribe1: 一条普通的白色毛巾
  cnDescribe2: 接近闻嗅时有明显的甜腻化学味，是氯仿的味道
  enDescribe1: An ordinary white towel
  enDescribe2: A pungent sweet smell, it's chloroform
```

**对应到 evidences.yaml：**
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
    result_description: 接近闻嗅时有明显的甜腻化学味，是氯仿的味道，这不是清洁用品
  asset_id: SC101_clue_04
  purpose: 否定Rosa"专心清洁，什么都没看到"的目击谎言
```

---

### 2.5 evidences.yaml 特有字段说明

| 字段 | 说明 |
|------|------|
| asset_id | 美术资源ID，格式：场景ID_clue/note_序号 |
| purpose | 设计目的，说明该证据在剧情中的作用 |
| analysis.action | 分析操作描述（如"接近闻嗅"、"测量压痕深度"） |
| analysis.result_name | 分析后的物品名称 |
| has_puzzle | 是否关联谜题 |
| puzzle_description | 谜题描述 |

---

## 6. 注意事项

1. **ID必须唯一**：同一张表中不能有重复ID
2. **中英文都要填**：cnName/enName、cnDescribe1/enDescribe1 都必须填写
3. **bool值格式**：使用 1 表示是，0 表示否（不要用 true/false）
4. **合并参数成对**：如果 canCombined=1，combineParameter0 和 combineParameter1 都要填
5. **分析描述**：如果 canAnalyzed=1，cnDescribe2/enDescribe2 要填写分析后的描述
6. **路径格式**：美术资源路径使用 `/` 分隔，如 `Art/UI/Item/Name`

---

## 7. 更新日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2025-11-29 | 初始版本，基于 ItemStaticData 表和 evidences.yaml 整理 |
