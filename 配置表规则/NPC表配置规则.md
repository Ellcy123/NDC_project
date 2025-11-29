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
| cnDescribe | string | 是 | 中文描述（多条用 `/` 分隔） |
| enDescribe | string | 是 | 英文描述（多条用 `/` 分隔） |
| ifExpose | string | 否 | 可被指证的描述编号（如 `2/4`） |
| cnNewDescribe | string | 否 | 指证后的新描述信息 |
| enNewDescribe | string | 否 | 指证后的新描述信息（英文） |

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

描述用于展示NPC的信息（info），多条描述用 `/` 分隔。

| 字段 | 类型 | 说明 |
|------|------|------|
| cnDescribe | string | 中文描述，多条用 `/` 分隔 |
| enDescribe | string | 英文描述，多条用 `/` 分隔 |
| ifExpose | string | 可被指证的描述编号，多个用 `/` 分隔 |
| cnNewDescribe | string | 指证后的新描述信息 |
| enNewDescribe | string | 指证后的新描述信息（英文） |

**描述格式示例：**
```yaml
cnDescribe: 描述1/描述2/描述3/描述4
```

**ifExpose 格式：**
- `2/4` = 第2条和第4条描述可以被指证

**cnNewDescribe 格式：**
- `原信息<link="key_describe">指证后新信息</link>`
- 原信息 = 被指证前显示的内容
- 指证后新信息 = 指证成功后替换显示的内容

**完整示例：**
```yaml
- id: NPC103
  cnName: 罗莎
  cnDescribe: 蓝月亮歌舞厅的清洁女工/我一直在地下室酒窖工作,什么都没看到/我当时在后台走廊清洁,但很专心工作/是Morrison警官迷晕了Zack先生,我被威胁不能说出真相
  enDescribe: Cleaning lady at Blue Moon/I was working in the basement wine cellar/I was cleaning the backstage corridor/Officer Morrison drugged Mr. Zack
  ifExpose: 2/4
  cnNewDescribe: 我一直在地下室酒窖工作,什么都没看到<link="key_describe">工作记录卡显示她23:00-01:00在后台走廊工作,不是地下室</link>/是Morrison警官迷晕了Zack先生,我被威胁不能说出真相<link="key_describe">Rosa确认是Morrison威胁她配合栽赃</link>
```

**说明：**
- cnDescribe 有4条描述（用 `/` 分隔）
- ifExpose: `2/4` 表示第2条和第4条可以被指证
- cnNewDescribe:
  - 第2条原信息：`我一直在地下室酒窖工作,什么都没看到`
  - 第2条指证后：`工作记录卡显示她23:00-01:00在后台走廊工作,不是地下室`
  - 第4条原信息：`是Morrison警官迷晕了Zack先生,我被威胁不能说出真相`
  - 第4条指证后：`Rosa确认是Morrison威胁她配合栽赃`

---

### 1.5 完整配置示例

```yaml
- id: NPC103
  cnName: 罗莎
  enName: Rosa Martinez
  role: suspect
  path1: Art/UI/NPC/Rosa
  path2: Art/UI/NPC/Rosa_Portrait
  TestimonyCount: 3
  cnTestimony: 我一直在地下室酒窖工作,什么都没看到/我当时在后台走廊清洁/是Morrison警官迷晕了Zack先生
  enTestimony: I was working in the basement wine cellar/I was cleaning the backstage corridor/It was Officer Morrison who drugged Mr. Zack
  cnDescribe: 蓝月亮歌舞厅的清洁女工/我一直在地下室酒窖工作,什么都没看到/我当时在后台走廊清洁,但很专心工作/是Morrison警官迷晕了Zack先生
  enDescribe: Cleaning lady at Blue Moon/I was working in the basement wine cellar/I was cleaning the backstage corridor/It was Officer Morrison who drugged Mr. Zack
  ifExpose: 2/4
  cnNewDescribe: 我一直在地下室酒窖工作,什么都没看到<link="key_describe">工作记录卡显示她23:00-01:00在后台走廊工作,不是地下室</link>/是Morrison警官迷晕了Zack先生,我被威胁不能说出真相<link="key_describe">Rosa确认是Morrison威胁她配合栽赃</link>
  enNewDescribe: I was working in the basement wine cellar<link="key_describe">Work record shows she was in backstage corridor 23:00-01:00, not basement</link>/Officer Morrison drugged Mr. Zack<link="key_describe">Rosa confirms Morrison threatened her to cooperate in framing</link>
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
| cnDescribe（第1条） | description | 基础描述 |
| cnDescribe（其他条） | info.loopX | 各循环的详细信息 |
| ifExpose | （逻辑处理） | 指证系统使用 |
| cnNewDescribe | （逻辑处理） | 指证后替换信息 |
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
  description: 蓝月亮歌舞厅的清洁女工...
  info:
    loop1:
      - 蓝月亮歌舞厅清洁工，夜班23:00-01:00
      - 单身母亲，儿子Miguel患病需要昂贵药物
      - 声称在地下室酒窖工作（实际在后台走廊）
    loop2:
      - 被Morrison威胁配合栽赃，内心充满恐惧和愧疚
      - 在Zack的劝说下说出真相
```

---

### 2.5 转换对照示例

**配置表（NPCStaticData.yaml）：**
```yaml
- id: NPC103
  cnName: 罗莎
  enName: Rosa Martinez
  cnDescribe: 蓝月亮歌舞厅的清洁女工/我一直在地下室酒窖工作/我当时在后台走廊清洁/是Morrison警官迷晕了Zack先生
  enDescribe: Cleaning lady at Blue Moon/I was in basement/I was in backstage corridor/Officer Morrison drugged Zack
  ifExpose: 2/4
  cnNewDescribe: 我一直在地下室酒窖工作<link="key_describe">工作记录卡显示她在后台走廊工作</link>/是Morrison警官迷晕了Zack先生<link="key_describe">Rosa确认Morrison威胁她配合栽赃</link>
  cnTestimony: 证词1/证词2/证词3
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
      - 我一直在地下室酒窖工作（可被指证）
      - 声称在地下室酒窖工作（实际在后台走廊）
    loop2:
      - 我当时在后台走廊清洁
      - 是Morrison警官迷晕了Zack先生（可被指证）
```

---

## 3. 注意事项

1. **ID必须唯一**：同一张表中不能有重复ID
2. **中英文都要填**：cnName/enName、cnDescribe1/enDescribe1 必须填写
3. **证词分隔符**：多条证词用 `/` 分隔
4. **描述可扩展**：cnDescribe 可以继续扩展 4/5/6...
5. **role字段**：可选值为 protagonist/partner/suspect/witness/victim/killer

---

## 4. 更新日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2025-11-29 | 初始版本，基于 NPCStaticData 表和 npcs.yaml 整理 |
