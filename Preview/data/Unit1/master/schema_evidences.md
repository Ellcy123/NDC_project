# 证据数据规范（Evidences Schema）

## 文件位置

```
Preview/data/UnitX/master/evidences.yaml
```

---

## 一、基础字段

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `name` | string | ✓ | 证据中文名称 | `沾有氯仿的毛巾` |
| `name_en` | string | ✓ | 证据英文名称 | `Chloroform-Stained Towel` |
| `type` | string | ✓ | 证据类型 | `item` |
| `asset_id` | string | ✓ | 美术资源ID | `SC101_clue_114` |

### 证据类型 (type)

| type值 | 说明 | canCollected |
|--------|------|--------------|
| `item` | 实体证据（可拿取物品） | 1 |
| `clue` | 线索（需要观察推理） | 1 |
| `note` | 证词笔记（对话获得） | 0 |
| `envir` | 环境叙事（背景信息） | 0 |

---

## 二、description 字段（中文描述）

```yaml
description:
  initial: 初始描述文本
  brief: 简短描述（可选）
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `initial` | string | ✓ | 初始描述（cnDescribe1） |
| `brief` | string | - | 简短描述（cnDescribe2） |

---

## 三、description_en 字段（英文描述）

```yaml
description_en:
  initial: Initial description text
  brief: Brief description (optional)
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `initial` | string | ✓ | 英文初始描述（enDescribe1） |
| `brief` | string | - | 英文简短描述（enDescribe2） |

---

## 四、analysis 字段（分析证据）

需要玩家分析才能获取完整信息的证据。

```yaml
analysis:
  required: true
  action: 接近闻嗅
  result_name: 沾着氯仿的毛巾
  result_description: 接近闻嗅时有明显的甜腻化学味，是氯仿的味道
  result_description_en: A distinct sweet chemical smell when sniffed closely, it's chloroform
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `required` | boolean | ✓ | 是否需要分析（true → canAnalyzed=1） |
| `action` | string | ✓ | 触发分析的动作描述 |
| `result_name` | string | ✓ | 分析后的证据名称 |
| `result_description` | string | ✓ | 分析后中文描述（cnDescribe3） |
| `result_description_en` | string | ✓ | 分析后英文描述（enDescribe3） |

---

## 五、Preview 专用字段

以下字段**仅用于 Preview 显示**，不导出到配置表：

| 字段 | 类型 | 说明 |
|------|------|------|
| `has_puzzle` | boolean | 是否包含解谜玩法 |
| `puzzle_description` | string | 解谜玩法描述 |
| `purpose` | string | 设计目的/用途说明 |

### 示例

```yaml
EV1112:
  name: Rosa的女儿照片
  name_en: Rosa's Daughter Photo
  type: clue
  description:
    initial: 照片背面写着"我的小天使Miguel，生日0915，妈妈的一切希望"
  asset_id: SC101_clue_112
  # Preview 专用
  has_puzzle: true
  puzzle_description: 需要四位密码解锁工具箱，密码提示在女儿照片生日上
  purpose: 强化Rosa母爱主题，提供密码线索
```

---

## 六、转表生成字段

以下字段**不在 YAML 中配置**，由转表工具自动生成：

| 配置表字段 | 生成规则 |
|-----------|----------|
| `canCollected` | `type` 为 `item`/`clue` → 1，否则 → 0 |
| `canAnalyzed` | `analysis.required` = true → 1，否则 → 0 |
| `canCombined` | 默认 0 |
| `combineParameter0` | 空 |
| `combineParameter1` | 空 |
| `path1` | `{asset_id}_big` |
| `path2` | `{asset_id}` |
| `path3` | 空 |
| `cnDescribe1` | `description.initial` |
| `cnDescribe2` | `description.brief` |
| `cnDescribe3` | `analysis.result_description` |
| `enDescribe1` | `description_en.initial` |
| `enDescribe2` | `description_en.brief` |
| `enDescribe3` | `analysis.result_description_en` |
| `parameter` | 空 |

---

## 七、ID命名规范

```
EV + 章节(1位) + 循环(1位) + 场景(1位) + 序号(1位)
```

**示例**：
- `EV1111` = 第1章 第1循环 第1场景 第1个证据
- `EV1234` = 第1章 第2循环 第3场景 第4个证据

### asset_id 格式

```
SC{场景号}_{clue/note}_{证据ID后三位}
```

**示例**：
- `SC101_clue_114` = 场景101 线索类 证据114
- `SC103_note_133` = 场景103 证词类 证据133

---

## 八、完整示例

### 示例1：需要分析的证据

```yaml
EV1114:
  name: 沾有氯仿的毛巾
  name_en: Chloroform-Stained Towel
  type: item
  description:
    initial: 一条普通的白色毛巾
  description_en:
    initial: An ordinary white towel
  analysis:
    required: true
    action: 接近闻嗅
    result_name: 沾着氯仿的毛巾
    result_description: 接近闻嗅时有明显的甜腻化学味，是氯仿的味道
    result_description_en: A distinct sweet chemical smell when sniffed closely, it's chloroform
  asset_id: SC101_clue_114
  purpose: 否定Rosa"专心清洁，什么都没看到"的目击谎言
```

### 示例2：证词笔记

```yaml
EV1211:
  name: Morrison夫人时间证词
  name_en: Mrs. Morrison Time Testimony
  type: note
  description:
    initial: Morrison于00:30从家出发，声称处理紧急案件
  description_en:
    initial: Morrison left home at 00:30, claiming to handle an urgent case
  asset_id: SC208_note_211
  purpose: 建立Morrison离家时间，为时间矛盾做铺垫
```

---

## 九、注意事项

1. **ID必须唯一**：同一张表中不能有重复ID
2. **中英文都要填**：name/name_en、description/description_en 必须填写
3. **分析证据**：有 `analysis` 的证据，所有子字段必须完整
4. **Preview字段**：`has_puzzle`、`puzzle_description`、`purpose` 仅用于策划查看
5. **出现次数统计**：由网站动态计算，不需要在数据中记录

---

## 十、转表命令

```bash
python scripts/evidence_converter.py
```

输出文件：`story/ItemStaticData.xlsx`
