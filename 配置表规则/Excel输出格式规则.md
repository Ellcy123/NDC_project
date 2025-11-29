# Excel 配置表输出格式规则

## 概述

本项目使用 **Luban 配置表格式**，所有输出的 Excel 配置表必须包含标准的三行表头。

---

## 表头结构

| 行号 | 前缀 | 内容 | 说明 |
|------|------|------|------|
| 第1行 | `##var` | 字段名 | 变量名，代码中使用的字段名 |
| 第2行 | `##type` | 类型定义 | 字段的数据类型 |
| 第3行 | `##` | 字段描述 | 中文注释，说明字段含义 |
| 第4行起 | 无 | 实际数据 | 配置数据内容 |

---

## 支持的数据类型

| 类型 | 说明 | 示例值 |
|------|------|--------|
| `string` | 字符串 | `"NPC001"`, `"查克"` |
| `int` | 整数 | `1001001`, `0`, `-1` |
| `float` | 浮点数 | `1.5`, `0.0` |
| `bool` | 布尔值 | `true`, `false`, `1`, `0` |
| `enum(值1/值2/值3)` | 枚举类型 | `enum(crime/dialogue/locked)` |

---

## 示例

### 示例1：Talk表

```
| ##var  | id      | step | speakType | waitTime | IdSpeaker | cnSpeaker | enSpeaker    |
| ##type | int     | int  | int       | float    | string    | string    | string       |
| ##     | 对话ID  | 步骤 | 对话类型  | 等待时间 | 说话人ID  | 中文名    | 英文名       |
| 1001001| 1       | 2    | 2.0       | NPC001   | 查克      | Zack Brennan |
```

### 示例2：SceneConfig表

```
| ##var  | sceneId | sectionId | sceneName     | sceneType                   |
| ##type | string  | string    | string        | enum(crime/dialogue/locked) |
| ##     | 场景ID  | 小节ID    | 场景名称      | 场景类型                    |
| SC101  | SEC01   | Rosa储藏室 | crime         |
```

### 示例3：ItemStaticData表

```
| ##var  | id    | cnName   | enName              | itemType | canCollected | canAnalyzed |
| ##type | string| string   | string              | string   | bool         | bool        |
| ##     | ID    | 中文名称 | 英文名称            | 物品分类 | 能否收集     | 能否分析    |
| EV111  | 通缉令 | Chicago Police Wanted Poster | envir  | true     | false       |
```

---

## 输出要求

### 必须遵守

1. **第1行必须以 `##var` 开头**，后跟所有字段名
2. **第2行必须以 `##type` 开头**，后跟对应的类型定义
3. **第3行必须以 `##` 开头**，后跟字段的中文描述
4. **第4行起为实际数据**，无前缀

### 类型定义规则

- 根据字段内容选择合适的类型
- ID 字段通常为 `string`（如 `NPC001`、`SC101`）或 `int`（如 `1001001`）
- 名称、描述类字段为 `string`
- 数量、计数类字段为 `int`
- 时间、比例类字段为 `float`
- 开关、标记类字段为 `bool`
- 有限选项的字段使用 `enum(选项1/选项2/...)`

---

## 参考文件

现有配置表位置：`D:\NDC\Config\Datas\story\`

| 文件名 | 说明 |
|--------|------|
| NPCStaticData.xlsx | NPC静态数据 |
| Talk.xlsx | 对话配置 |
| Testimony.xlsx | 证词配置 |
| SceneConfig.xlsx | 场景配置 |
| ItemStaticData.xlsx | 物品配置 |
| Event.xlsx | 事件配置 |
| TaskConfig.xlsx | 任务配置 |
| TimeLineEvent.xlsx | 时间线事件 |

---

## 更新日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2025-11-29 | 初始版本，定义 Luban 配置表三行表头格式规则 |
