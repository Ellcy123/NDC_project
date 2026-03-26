# Testimony表配置规则文档

## 第一部分：配置表字段说明

### 1.1 字段列表

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | number | 是 | 对应Talk表的对话ID |
| speakerName | string | 是 | 说话者中文名 |
| speakerNameEn | string | 是 | 说话者英文名 |
| cnWords | string | 是 | 中文证词内容（可含富文本） |
| enWords | string | 是 | 英文证词内容（可含富文本） |
| ifIgnore | number | 是 | 是否显示（0=显示，1=不显示） |
| ifEvidence | number | 是 | 证词序号（0=普通对话，1+=该人物第N条证词） |
| cnExracted | string | 否 | 提取的中文证据文本 |
| enExracted | string | 否 | 提取的英文证据文本 |

---

### 1.2 ID命名规则

**id = Talk表对话ID**

| 说明 |
|------|
| 证词表的id对应Talk表中的对话ID |
| 当该对话播放完毕后，对应的证词内容会显示在证词界面 |
| 不是所有Talk对话都有对应证词，无需证词的对话不在此表配置 |

**示例：**
- Talk表中 `3001010` 对话播放后 → 显示证词表中 `3001010` 的证词内容

---

### 1.3 ifIgnore 字段说明

| 值 | 说明 |
|----|------|
| 0 | 显示该条证词 |
| 1 | 不显示该条证词 |

---

### 1.4 ifEvidence 字段说明

| 值 | 说明 |
|----|------|
| 0 | 普通对话，不是可提取的证词 |
| 1 | 该人物的第1条证词 |
| 2 | 该人物的第2条证词 |
| N | 该人物的第N条证词 |



---

### 1.5 证据字段（重复配置）

| 字段 | 说明 |
|------|------|
| cnWords | 中文证词，用 `<link="key_evidence">文本</link>` 标记证据 |
| cnExracted | 与 cnWords 内容相同（重复填写） |
| enWords | 英文证词，用 `<link="key_evidence">文本</link>` 标记证据 |
| enExracted | 与 enWords 内容相同（重复填写） |

---

### 1.6 完整配置示例

**普通证词（无证据）：**
```yaml
- id: 3001001
  speakerName: 查克
  speakerNameEn: Zack Brennan
  cnWords: 你是这儿的清洁工?
  enWords: You're the janitor here?
  ifIgnore: 0
  ifEvidence: 0
```

**包含证据的证词：**
```yaml
- id: 3001010
  speakerName: 罗莎
  speakerNameEn: Rosa Martinez
  cnWords: 我...<link="key_evidence">我一直在地下室</link>。酒窖那边,整理酒瓶和架子...很忙的...一直在那儿...
  enWords: I... I was <link="key_evidence">in the basement all the time.</link> Wine cellar area, organizing bottles and shelves... very busy... stayed there...
  ifIgnore: 0
  ifEvidence: 2
  cnExracted: 我...<link="key_evidence">我一直在地下室</link>。酒窖那边,整理酒瓶和架子...很忙的...一直在那儿...
  enExracted: I... I was <link="key_evidence">in the basement all the time.</link> Wine cellar area, organizing bottles and shelves... very busy... stayed there...
```

**不显示的证词（ifIgnore=1）：**
```yaml
- id: 3001015
  speakerName: 查克
  speakerNameEn: Zack Brennan
  cnWords: 地下室能听到一楼的枪声吗?
  enWords: Can you hear gunshots from the first floor in the basement?
  ifIgnore: 1
  ifEvidence: 0
```

---

## 第二部分：选项证词配置

### 2.1 选项结构说明

证词表支持选项分支结构，玩家可选择不同选项获得不同回复：

| 类型 | 说明 |
|------|------|
| 问题 | 侦探提出的问题 |
| 选项A/B/C | 玩家可选择的选项 |
| 回复A/B/C | NPC对应各选项的回复 |

**示例：**
```yaml
# 问题
- id: 3001001
  speakerName: 查克
  cnWords: 你是这儿的清洁工?
  ifIgnore: 0
  ifEvidence: 0

# 选项A
- id: 3001002
  speakerName: 查克
  cnWords: 我是选项A
  ifIgnore: 0
  ifEvidence: 0

# 选项B
- id: 3001003
  speakerName: 查克
  cnWords: 我是选项B
  ifIgnore: 0
  ifEvidence: 0

# 选项C
- id: 3001004
  speakerName: 查克
  cnWords: 我是选项C
  ifIgnore: 0
  ifEvidence: 0

# 回复A（包含证据）
- id: 3001005
  speakerName: 罗莎
  cnWords: 选项A对应这<link="key_evidence">个</link>
  ifIgnore: 0
  ifEvidence: 1
  cnExracted: 选项A对应这个
```

---

## 第三部分：注意事项

1. **ID唯一性**：每条证词的ID必须唯一
2. **说话者一致性**：speakerName和speakerNameEn必须与NPC表中的名称一致
3. **证据标记**：`ifEvidence > 0` 时，cnWords/enWords中必须包含 `<link="key_evidence">` 标记
4. **提取文本**：包含证据时，必须填写cnExracted和enExracted
5. **富文本转义**：YAML中的引号需要转义，使用 `\"` 表示引号

---

## 第四部分：更新日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2025-11-29 | 初始版本 |
