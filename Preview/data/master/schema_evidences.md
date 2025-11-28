# 证据数据规范（Evidences Schema）

## 基本字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✓ | 证据中文名称 |
| `name_en` | string | ✓ | 证据英文名称（用于资源ID） |
| `type` | string | ✓ | 证据类型：`envir`环境叙事 / `clue`线索 / `item`实体证据 / `note`证词笔记 |
| `description.initial` | string | ✓ | 初始描述文本 |
| `asset_id` | string | ✓ | 美术资源ID，格式根据type：<br>`note`类型用`SC{场景}_note_{序号}`<br>其他类型用`SC{场景}_clue_{序号}` |
| `purpose` | string | ✓ | 证据在剧情中的作用说明 |

## 可选字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `analysis.required` | boolean | 是否需要分析 | `true` |
| `analysis.action` | string | 触发分析的动作描述 | "接近闻嗅" |
| `analysis.result_name` | string | 分析后的证据名称 | "沾着氯仿的毛巾" |
| `analysis.result_description` | string | 分析后的描述文本 | "接近闻嗅时有明显的甜腻化学味..." |
| `has_puzzle` | boolean | 是否包含解谜玩法 | `true` |
| `puzzle_description` | string | 解谜玩法描述（如有解谜） | "需要四位密码解锁工具箱，密码提示在女儿照片上" |

## ID命名规范

```
EV + 章节(1位) + 循环(1位) + 场景(1位) + 序号(1位)
```

**示例**：
- `EV1111` = 第1章 第1循环 第1场景 第1个证据
- `EV1234` = 第1章 第2循环 第3场景 第4个证据

## 证据类型说明

| type值 | 说明 | 用途 |
|--------|------|------|
| `envir` | 环境叙事 | 背景信息，非指证关键证据 |
| `clue` | 线索 | 需要观察或推理的证据 |
| `item` | 实体证据 | 可拿取的物品，通常是指证核心证据 |
| `note` | 证词笔记 | 对话中获得的证词记录 |

## 完整示例

### 示例1：需要分析的证据
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
    result_description: 接近闻嗅时有明显的甜腻化学味，是氯仿的味道
  asset_id: SC101_clue_04
  purpose: 否定Rosa"专心清洁，什么都没看到"的目击谎言
```

### 示例2：包含解谜的证据
```yaml
EV1112:
  name: Rosa的女儿照片
  name_en: Rosa's Daughter Photo
  type: clue
  description:
    initial: 照片背面写着"我的小天使Miguel，生日0915，妈妈的一切希望"
  has_puzzle: true
  puzzle_description: 需要四位密码解锁工具箱，密码提示在女儿照片生日上
  asset_id: SC101_clue_02
  purpose: 强化Rosa母爱主题，提供密码线索
```

## 注意事项

1. **出现次数统计**：不需要在数据中记录，由网站动态计算
2. **关联循环**：通过ID中的循环位自动识别
3. **中英文名称**：`name_en`用于生成资源路径，建议使用驼峰命名
4. **解谜证据**：`has_puzzle`为true的证据，需在`puzzle_description`中描述玩法
5. **分析证据**：需要分析的证据，所有`analysis`字段必须完整填写（名称、动作、描述）
