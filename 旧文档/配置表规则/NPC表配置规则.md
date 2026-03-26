# NPC表配置规则文档

## 第一部分：配置表字段说明

### 1.1 字段列表

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | NPC唯一ID，格式：NPC + 章节 + 序号(2位) |
| cnName | string | 是 | 中文名字 |
| enName | string | 是 | 英文名字 |
| role | string | 否 | 角色类型（protagonist/partner/suspect/witness/victim/killer） |
| path1 | string | 否 | 美术资源路径1（头像等） |
| path2 | string | 否 | 美术资源路径2 |
| path3 | string | 否 | 美术资源路径3 |
| TestimonyCount | int | 否 | 证词数量 |
| cnTestimony | string | 否 | 中文证词（多条用 `/` 分隔） |
| enTestimony | string | 否 | 英文证词（多条用 `/` 分隔） |
| cnDescribe | string | 是 | 中文描述（仅1条，角色简介） |
| enDescribe | string | 是 | 英文描述（仅1条，角色简介） |
| infoCount | int | 是 | 信息数量（1-6） |
| info1 | string | 否 | 人物信息1，格式：`中文/英文` |
| info2 | string | 否 | 人物信息2，格式：`中文/英文` |
| info3 | string | 否 | 人物信息3，格式：`中文/英文` |
| info4 | string | 否 | 人物信息4，格式：`中文/英文` |
| info5 | string | 否 | 人物信息5，格式：`中文/英文` |
| info6 | string | 否 | 人物信息6，格式：`中文/英文` |
| ifExposeInfo1 | int | 否 | 第1个可被指证的info编号（1-6） |
| cnNewInfo1 | string | 否 | 第1条指证后的中文信息，格式：`原文/新文` |
| enNewInfo1 | string | 否 | 第1条指证后的英文信息，格式：`原文/新文` |
| ifExposeInfo2 | int | 否 | 第2个可被指证的info编号（1-6） |
| cnNewInfo2 | string | 否 | 第2条指证后的中文信息，格式：`原文/新文` |
| enNewInfo2 | string | 否 | 第2条指证后的英文信息，格式：`原文/新文` |
| npcPosX | float | 否 | NPC在关系图中的X坐标（中心点） |
| npcPosY | float | 否 | NPC在关系图中的Y坐标（中心点） |
| npcRelation | string | 否 | 关联的NPC ID，多个用 `/` 分隔 |
| npcRelationParaCn | string | 否 | 关系描述（中文），多个用 `/` 分隔 |
| npcRelationParaEn | string | 否 | 关系描述（英文），多个用 `/` 分隔 |

---

### 1.2 ID命名规则

**格式：`NPC` + `章节(1位)` + `序号(2位)`**

| 位置 | 含义 | 说明 |
|------|------|------|
| NPC | 固定前缀 | Non-Player Character |
| 第1位 | 章节 | 1=第1章 |
| 第2-3位 | 序号 | 01-99，该章节内的NPC序号 |

**示例：**
- `NPC101` = 第1章 第01个NPC（Zack）
- `NPC102` = 第1章 第02个NPC（Emma）
- `NPC103` = 第1章 第03个NPC（Rosa）

---

### 1.3 证词规则（cnTestimony/enTestimony）

证词用于指证系统，NPC在不同循环中会有不同的证词。

**格式**：多条证词用 `/` 分隔

```yaml
cnTestimony: 证词1/证词2/证词3
```

**示例：**
```yaml
- id: NPC103
  cnName: 罗莎
  TestimonyCount: 3
  cnTestimony: 我一直在地下室酒窖工作,什么都没看到/我当时在后台走廊清洁,但很专心工作/是Morrison警官迷晕了Zack先生,我被威胁不能说出真相
```

---

### 1.4 描述规则（cnDescribe/enDescribe）

描述用于展示NPC的基础简介，**仅1条**。

| 字段 | 类型 | 说明 |
|------|------|------|
| cnDescribe | string | 中文角色简介（仅1条） |
| enDescribe | string | 英文角色简介（仅1条） |

**示例：**
```yaml
cnDescribe: 蓝月亮歌舞厅的清洁女工
enDescribe: Cleaning lady at Blue Moon Ballroom
```

---

### 1.5 信息规则（info1~info6）

人物详细信息，独立字段存储，最多6条。

| 字段 | 类型 | 格式 | 说明 |
|------|------|------|------|
| infoCount | int | 1-6 | 信息条数 |
| info1~info6 | string | `中文/英文` | 人物详细信息 |

**格式说明：**
- 每条info用 `/` 分隔中英文
- 格式：`中文内容/英文内容`

**示例：**
```yaml
infoCount: 4
info1: 50岁的清洁工，夜班23:00-01:00/50-year-old janitor, night shift 23:00-01:00
info2: 我一直在地下室酒窖工作/I was working in the basement wine cellar
info3: 单身母亲，儿子Miguel患病/Single mother, son Miguel is sick
info4: 是Morrison警官迷晕了Zack先生/Officer Morrison drugged Mr. Zack
```

---

### 1.6 指证规则（ifExposeInfo + NewInfo）

指证系统用于揭穿NPC的谎言，**最多支持2条可被指证的信息**。

| 字段 | 类型 | 格式 | 说明 |
|------|------|------|------|
| ifExposeInfo1 | int | 1-6 | 第1个可被指证的info编号 |
| cnNewInfo1 | string | `原文/新文` | 第1条指证后的中文信息 |
| enNewInfo1 | string | `原文/新文` | 第1条指证后的英文信息 |
| ifExposeInfo2 | int | 1-6 | 第2个可被指证的info编号 |
| cnNewInfo2 | string | `原文/新文` | 第2条指证后的中文信息 |
| enNewInfo2 | string | `原文/新文` | 第2条指证后的英文信息 |

**格式说明：**
- NewInfo 用 `/` 分隔原文和新文
- 格式：`原文/新文`
- 原文 = 被指证前显示的内容（谎言）
- 新文 = 指证成功后显示的内容（真相）

**示例：**
```yaml
# 指证1：针对info2（地下室酒窖的谎言）
ifExposeInfo1: 2
cnNewInfo1: 我一直在地下室酒窖工作/工作记录卡显示她在后台走廊工作
enNewInfo1: I was in the basement wine cellar/Work record shows backstage corridor

# 指证2：针对info4（Morrison的指控）
ifExposeInfo2: 4
cnNewInfo2: 是Morrison警官迷晕了Zack先生/Rosa确认Morrison威胁她配合栽赃
enNewInfo2: Officer Morrison drugged Mr. Zack/Rosa confirms Morrison threatened her
```

**指证流程：**
```
玩家选择证据 → 指证 info2 的内容
    ↓
原显示：我一直在地下室酒窖工作
    ↓ 指证成功
新显示：工作记录卡显示她在后台走廊工作
```

---

### 1.7 人物关系规则（npcRelation）

用于 **INVESTIGATE 面板的 RELATIONSHIP 人物关系网图**。

| 字段 | 类型 | 格式 | 说明 |
|------|------|------|------|
| npcPosX | float | 数值 | NPC在关系图中的X坐标（中心点） |
| npcPosY | float | 数值 | NPC在关系图中的Y坐标（中心点） |
| npcRelation | string | `NPC_ID` 或 `ID1/ID2` | 关联的NPC ID |
| npcRelationParaCn | string | `关系1` 或 `关系1/关系2` | 关系描述（中文） |
| npcRelationParaEn | string | `relation1` 或 `rel1/rel2` | 关系描述（英文） |

**填写规则：**
1. **每条关系线只填写一次**：A↔B 的关系只需要在 A 或 B 其中一个NPC配置
2. **尽量避免多关系**：如 Rosa-Webb 写在 Rosa，Tommy-Rosa 写在 Tommy
3. **多个关系用 `/` 分隔**：如必须配置多个，ID和描述用 `/` 分隔且一一对应

**关系图示意：**
```
┌─────────────────────────────────────┐
│  INVESTIGATE - RELATIONSHIP 面板    │
├─────────────────────────────────────┤
│                                     │
│           [Webb]  ← 死者中心         │
│          /   |   \                  │
│     [Rosa] [Tommy] [Morrison]       │
│        ↑      ↑        ↑            │
│   npcPosX/Y 决定头像位置             │
│   npcRelation 决定连线对象           │
│   npcRelationPara 显示关系文字       │
│                                     │
└─────────────────────────────────────┘
```

**示例：**
```yaml
# Rosa 配置与 Webb 的关系
- id: NPC103
  cnName: 罗莎
  npcPosX: 100.0
  npcPosY: 200.0
  npcRelation: NPC101           # 与Webb有关系
  npcRelationParaCn: 清洁工      # 关系是"清洁工"
  npcRelationParaEn: Cleaner

# Tommy 配置与 Rosa 的关系（每条线只填一次）
- id: NPC105
  cnName: 汤米
  npcPosX: 300.0
  npcPosY: 200.0
  npcRelation: NPC103           # 与Rosa有关系
  npcRelationParaCn: 上下级      # 关系是"上下级"
  npcRelationParaEn: Supervisor
```

---

### 1.8 完整配置示例

```yaml
- id: NPC103
  cnName: 罗莎
  enName: Rosa Martinez
  role: suspect
  path1: Art/UI/NPC/Rosa
  path2: Art/UI/NPC/Rosa_Portrait

  # 证词
  TestimonyCount: 3
  cnTestimony: 我一直在地下室酒窖工作,什么都没看到/我当时在后台走廊清洁/是Morrison警官迷晕了Zack先生
  enTestimony: I was working in the basement wine cellar/I was cleaning the backstage corridor/It was Officer Morrison who drugged Mr. Zack

  # 描述（仅1条基础简介）
  cnDescribe: 蓝月亮歌舞厅的清洁女工
  enDescribe: Cleaning lady at Blue Moon Ballroom

  # 信息（独立字段，中文/英文格式）
  infoCount: 4
  info1: 50岁的清洁工，夜班23:00-01:00/50-year-old janitor, night shift 23:00-01:00
  info2: 我一直在地下室酒窖工作/I was working in the basement wine cellar
  info3: 单身母亲，儿子Miguel患病/Single mother, son Miguel is sick
  info4: 是Morrison警官迷晕了Zack先生/Officer Morrison drugged Mr. Zack

  # 指证1：针对info2
  ifExposeInfo1: 2
  cnNewInfo1: 我一直在地下室酒窖工作/工作记录卡显示她在后台走廊工作
  enNewInfo1: I was in the basement wine cellar/Work record shows backstage corridor

  # 指证2：针对info4
  ifExposeInfo2: 4
  cnNewInfo2: 是Morrison警官迷晕了Zack先生/Rosa确认Morrison威胁她配合栽赃
  enNewInfo2: Officer Morrison drugged Mr. Zack/Rosa confirms Morrison threatened her

  # 人物关系（用于RELATIONSHIP关系图）
  npcPosX: 100.0
  npcPosY: 200.0
  npcRelation: NPC101
  npcRelationParaCn: 清洁工
  npcRelationParaEn: Cleaner
```

---

## 第二部分：与 npcs.yaml 的对应关系

### 2.1 文件说明

| 文件 | 位置 | 用途 |
|------|------|------|
| NPCStaticData.yaml | D:\NDC_project\story\ | 配置表（Excel转换） |
| npcs.yaml | D:\NDC_project\Preview\data\master\ | Preview网站使用的数据 |

---

### 2.2 字段对应关系

| NPCStaticData（配置表） | npcs.yaml（Preview） | 说明 |
|------------------------|---------------------|------|
| id | 键名（如 NPC103） | ID格式相同 |
| cnName | name_cn | 中文名 |
| enName | name | 英文名 |
| cnDescribe | description | 基础描述 |
| info1~info6 | info.loopX | 各循环的详细信息 |
| ifExposeInfo1/2 | （逻辑处理） | 指证系统使用 |
| cnNewInfo1/2 | （逻辑处理） | 指证后替换信息 |
| cnTestimony | （需手动整理） | 证词需要根据循环拆分 |
| role | role | 角色类型 |

---

### 2.3 role字段说明

| role | 说明 |
|------|------|
| protagonist | 主角（Zack） |
| partner | 搭档（Emma） |
| suspect | 嫌疑人 |
| witness | 证人 |
| victim | 受害者（Webb） |
| killer | 凶手（Jimmy） |

---

### 2.4 info字段结构（npcs.yaml特有）

npcs.yaml 中的 `info` 按循环组织NPC信息：

```yaml
NPC103:
  name: Rosa Martinez
  name_cn: 罗莎·马丁内斯
  role: suspect
  description: 蓝月亮歌舞厅的清洁女工
  info:
    loop1:
      - 50岁的清洁工，夜班23:00-01:00
      - 我一直在地下室酒窖工作（可被指证）
      - 单身母亲，儿子Miguel患病
    loop2:
      - 是Morrison警官迷晕了Zack先生（可被指证）
      - 被Morrison威胁配合栽赃
```

---

### 2.5 转换对照示例

**配置表（NPCStaticData.yaml）：**
```yaml
- id: NPC103
  cnName: 罗莎
  enName: Rosa Martinez
  cnDescribe: 蓝月亮歌舞厅的清洁女工
  enDescribe: Cleaning lady at Blue Moon Ballroom
  infoCount: 4
  info1: 50岁的清洁工，夜班23:00-01:00/50-year-old janitor
  info2: 我一直在地下室酒窖工作/I was in the basement
  info3: 单身母亲，儿子Miguel患病/Single mother
  info4: 是Morrison警官迷晕了Zack先生/Morrison drugged Zack
  ifExposeInfo1: 2
  cnNewInfo1: 我一直在地下室酒窖工作/工作记录卡显示她在后台走廊工作
  enNewInfo1: I was in the basement/Work record shows backstage corridor
  ifExposeInfo2: 4
  cnNewInfo2: 是Morrison警官迷晕了Zack先生/Rosa确认Morrison威胁她
  enNewInfo2: Morrison drugged Zack/Rosa confirms Morrison threatened her
```

**对应到 npcs.yaml：**
```yaml
NPC103:
  name: Rosa Martinez
  name_cn: 罗莎·马丁内斯
  role: suspect
  description: 蓝月亮歌舞厅的清洁女工
  info:
    loop1:
      - 50岁的清洁工，夜班23:00-01:00
      - 我一直在地下室酒窖工作（可被指证 → 工作记录卡显示她在后台走廊工作）
      - 单身母亲，儿子Miguel患病
    loop2:
      - 是Morrison警官迷晕了Zack先生（可被指证 → Rosa确认Morrison威胁她）
```

---

## 3. 注意事项

1. **ID必须唯一**：同一张表中不能有重复ID
2. **中英文都要填**：cnName/enName、cnDescribe/enDescribe 必须填写
3. **证词分隔符**：多条证词用 `/` 分隔
4. **info格式**：每条info格式为 `中文/英文`
5. **NewInfo格式**：格式为 `原文/新文`
6. **指证上限**：最多2条可被指证的信息（ifExposeInfo1 和 ifExposeInfo2）
7. **role字段**：可选值为 protagonist/partner/suspect/witness/victim/killer
8. **关系线唯一**：每条关系线只在一个NPC处配置，避免重复（如 Rosa-Webb 写在 Rosa，Tommy-Rosa 写在 Tommy）
9. **关系对应**：npcRelation 和 npcRelationParaCn/En 的数量必须一一对应

---

## 4. 更新日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v2.1 | 2025-12-07 | 新增人物关系字段：npcPosX/Y（关系图位置）、npcRelation（关联NPC）、npcRelationParaCn/En（关系描述） |
| v2.0 | 2025-12-07 | 重构info和指证系统：describe简化为1条；新增info1~info6独立字段；指证改为两组字段（ifExposeInfo1/2 + cnNewInfo1/2 + enNewInfo1/2）；NewInfo格式改为`原文/新文` |
| v1.0 | 2025-11-29 | 初始版本，基于 NPCStaticData 表和 npcs.yaml 整理 |
