# NPC数据规范（NPCs Schema）

## 文件位置

```
Preview/data/UnitX/master/npcs.yaml
```

---

## 一、基础字段

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `name` | string | ✓ | NPC英文名 | `Rosa Martinez` |
| `name_cn` | string | ✓ | NPC中文名 | `罗莎·马丁内斯` |
| `role` | string | ✓ | 角色类型 | `suspect` |
| `description` | string | ✓ | 中文角色简介 | `蓝月亮歌舞厅的清洁女工...` |
| `description_en` | string | ✓ | 英文角色简介 | `A cleaning lady at...` |

### 角色类型 (role)

| role值 | 说明 |
|--------|------|
| `protagonist` | 主角（玩家角色） |
| `partner` | 主角伙伴 |
| `suspect` | 嫌疑人（可指证对象） |
| `witness` | 证人（提供证词） |
| `victim` | 受害者 |
| `killer` | 凶手 |

---

## 二、info 字段（人物信息）

玩家可获取的 NPC 关键信息，最多 6 条。

### 结构

```yaml
info:
  - id: 1
    text: 中文内容
    text_en: 英文内容
    source: 信息来源说明
    expose_truth: 指证后的真相（可选）
    expose_truth_en: 指证后的真相英文（可选）
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | int | ✓ | 信息编号 (1-6) |
| `text` | string | ✓ | 中文内容（NPC声称的） |
| `text_en` | string | ✓ | 英文内容 |
| `source` | string | ✓ | 信息来源说明（Preview专用） |
| `expose_truth` | string | - | 指证后的真相（中文），有此字段表示是谎言 |
| `expose_truth_en` | string | - | 指证后的真相（英文） |

### source 格式说明

| 来源类型 | 格式示例 |
|---------|----------|
| NPC对话 | `循环1 Rosa对话` |
| 场景搜索 | `循环1 Rosa储藏室搜索(EV1113)` |
| 指证后坦白 | `循环1 指证后Rosa坦白` |
| 其他NPC证词 | `循环4 Tommy证词(EV1441)` |

### 示例

```yaml
info:
  - id: 1
    text: 案发当晚一直在地下室酒窖工作
    text_en: Was working in the basement wine cellar all night
    source: 循环1 Rosa对话
    expose_truth: 工作记录卡显示实际在后台走廊工作
    expose_truth_en: Work record shows she was actually in backstage corridor
  - id: 2
    text: 单身母亲，儿子Miguel患病需要昂贵药物
    text_en: Single mother, son Miguel is ill and needs expensive medication
    source: 循环1 Rosa储藏室搜索(EV1113)
```

---

## 三、关系图字段

用于 INVESTIGATE 面板的 RELATIONSHIP 人物关系网图。

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `npcPosX` | float | - | 关系图X坐标 | `30` |
| `npcPosY` | float | - | 关系图Y坐标 | `30` |
| `npcRelation` | string | - | 关联NPC ID | `NPC104` |
| `npcRelationParaCn` | string | - | 关系描述(中文) | `被威胁配合栽赃` |
| `npcRelationParaEn` | string | - | 关系描述(英文) | `Threatened to Frame Zack` |

**填写规则**：
- 每条关系线只在一个NPC处配置（A↔B 只需在 A 或 B 配置一次）
- 多个关系用 `/` 分隔

---

## 四、转表生成字段

以下字段**不在 YAML 中配置**，由转表工具自动生成：

| 配置表字段 | 生成规则 |
|-----------|----------|
| `path1` | `{name}_big` |
| `path2` | `{name}` |
| `path3` | 空 |
| `infoCount` | 实时计算 `len(info)` |
| `info1~info6` | `{text}/{text_en}` |
| `ifExposeInfo1` | 第1个有 `expose_truth` 的 info.id |
| `cnNewInfo1` | `{text}/{expose_truth}` |
| `enNewInfo1` | `{text_en}/{expose_truth_en}` |
| `ifExposeInfo2` | 第2个有 `expose_truth` 的 info.id（如有） |
| `TestimonyCount` | 从 evidences.yaml 统计 type:note 数量 |
| `cnTestimony` | 从 evidences.yaml 提取并用 `/` 连接 |
| `enTestimony` | 同上（英文版） |

---

## 五、ID命名规范

```
NPC + 章节(1位) + 序号(2位)
```

**示例**：
- `NPC101` = 第1章 第01个NPC
- `NPC215` = 第2章 第15个NPC

---

## 六、完整示例

```yaml
NPC103:
  name: Rosa Martinez
  name_cn: 罗莎·马丁内斯
  role: suspect
  description: 蓝月亮歌舞厅的清洁女工，有个8岁生病的儿子Miguel，因经济困境被Morrison威胁配合栽赃
  description_en: A cleaning lady at the Blue Moon Club with an 8-year-old sick son Miguel. Due to financial hardship, she was threatened by Morrison to cooperate in framing Zack.

  info:
    - id: 1
      text: 案发当晚一直在地下室酒窖工作
      text_en: Was working in the basement wine cellar all night
      source: 循环1 Rosa对话
      expose_truth: 工作记录卡显示实际在后台走廊工作
      expose_truth_en: Work record shows she was actually in backstage corridor
    - id: 2
      text: 单身母亲，儿子Miguel患病需要昂贵药物
      text_en: Single mother, son Miguel is ill and needs expensive medication
      source: 循环1 Rosa储藏室搜索(EV1113)
    - id: 3
      text: 被Morrison威胁配合栽赃Zack
      text_en: Threatened by Morrison to frame Zack
      source: 循环1 指证后Rosa坦白
    - id: 4
      text: 看到Jimmy用钥匙进入Webb会客室
      text_en: Saw Jimmy use a key to enter Webb's parlor
      source: 循环4 Rosa对话

  # 关系图配置
  npcPosX: 30
  npcPosY: 30
  npcRelation: NPC104
  npcRelationParaCn: 被威胁配合栽赃
  npcRelationParaEn: Threatened to Frame Zack
```

---

## 七、注意事项

1. **ID必须唯一**：同一张表中不能有重复ID
2. **中英文都要填**：name/name_cn、description/description_en 必须填写
3. **info 编号从1开始**：id 字段从 1 开始编号
4. **source 字段**：仅用于 Preview 展示，不导出到配置表
5. **expose_truth**：只有可被指证的谎言才需要填写
6. **关系线唯一**：每条关系线只在一个NPC处配置
7. **证词自动提取**：从 evidences.yaml 的 type:note 自动关联

---

## 八、转表命令

```bash
python scripts/npc_converter.py
```

输出文件：`story/NPCStaticData.xlsx`
