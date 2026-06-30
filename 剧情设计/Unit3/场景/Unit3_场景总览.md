# Unit3 场景总览

> **数据源**：`剧情设计/Unit3/state/loop{1-6}_state.yaml`
> **场景总数**：14 个（SC3001-SC3014）
> **旧 SC3015 三楼走廊**：新大纲未使用，已废弃
> **公寓总楼层**：6 层住宅 + 楼顶天台（案发现场）。住户分布——2 楼 Smith 家（Thomas/Mary/Emily）、2 楼 Seamus、3 楼 Helen；4–6 楼为无具名其他住户。Thomas 任天台管理员，持全楼唯一天台钥匙。

---

## 场景索引

| ID | 中文名 | 英文名 | 类型 | 主要 Loop |
|----|--------|--------|------|----------|
| SC3001 | Thomas 公寓楼下现场 | Apartment Ground Crime Scene | 🔓 自由探索 | L1（保留至全 Unit）|
| SC3002 | Thomas 公寓楼顶 | Apartment Rooftop | 🔓 / ⚔️ | L1（部分封锁）/ L3 二次搜证 / L4 门把手 |
| SC3003 | Smith 家客厅 | Smith Home Living Room | 🔓 自由探索 | L2 |
| SC3004 | 警局 | Police Station | 🔓 → ⚔️ | L1（指证 Morrison）|
| SC3005 | 法医办公室 | Forensic Office | 🔓 自由探索 | L1 / L4（仪器到位）/ L6（精确报告）|
| SC3006 | 公寓二楼走廊 | Apartment 2F Hallway | 🔓 自由探索 | L3 / L6（Seamus 润滑油）|
| SC3007 | St.Patrick 教堂 | St.Patrick's Church | 🔓 自由探索 | L2 |
| SC3008 | Helen 家 | Helen's Apartment | 🔓 → ⚔️ | L3 / L4（指证 Helen 补充）/ L5（判决后）|
| SC3009 | 湖滨信托银行公共区 | LakeShore Trust Bank Lobby | 🔓 自由探索 | L3 |
| SC3010 | Margaret 鞋坊 | Margaret's Shoe Shop | 🔓 自由探索 | L4（新解锁）|
| SC3011 | Mickey 办公室 | Mickey's Law Office | 🔓 → ⚔️ | L1 开篇 / L5 开篇 / L6（控辩对决）|
| SC3012 | Smith 家卧室 | Smith Home Bedroom | 🔓 自由探索 | L2 |
| SC3013 | Smith 公寓楼门口 | Smith Apartment Entrance | 🔓 → ⚔️ | L2（指证 Mary）|
| SC3014 | Bernard 办公室 | Bernard's Office | 🔓 → ⚔️ | L5（指证 Bernard，新解锁）|

---

## 场景 × Loop 解锁矩阵

| 场景 | L1 | L2 | L3 | L4 | L5 | L6 |
|------|----|----|----|----|----|----|
| SC3001 楼下现场 | 🔓 | 🔓 | 🔓 | 🔓 | 🔓 | 🔓 |
| SC3002 楼顶 | 🔓部分封锁 | 🔓 | 🔓二次 | 🔓门把手 | 🔓 | 🔓 |
| SC3003 客厅 | 🔒 | 🔓 | 🔓 | 🔓 | 🔓 | 🔓 |
| SC3004 警局 | ⚔️ | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 |
| SC3005 法医 | 🔓 | 🔓 | 🔓 | 🔓+🎮 | 🔓 | 🔓+报告 |
| SC3006 二楼走廊 | 🔒 | 🔒 | 🔓 | 🔓 | 🔓 | 🔓+Seamus 油 |
| SC3007 教堂 | 🔒 | 🔓 | 🔓 | 🔓 | 🔓 | 🔓 |
| SC3008 Helen 家 | 🔒 | 🔒 | 🔓⚔️ | 🔓⚔️ | 🔓判决后 | 🔓 |
| SC3009 银行公共区 | 🔒 | 🔒 | 🔓 | 🔓 | 🔓 | 🔓 |
| SC3010 Margaret 鞋坊 | 🔒 | 🔒 | 🔒 | 🔓 | 🔓 | 🔓 |
| SC3011 Mickey 办公室 | 🎬 开篇 | 🔒 | 🔒 | 🔒 | 🎬 开篇 | 🔓⚔️ |
| SC3012 卧室 | 🔒 | 🔓 | 🔓 | 🔓 | 🔓 | 🔓 |
| SC3013 公寓楼门口 | 🔒 | 🔓⚔️ | 🔓 | 🔓 | 🔓 | 🔓 |
| SC3014 Bernard 办公室 | 🔒 | 🔒 | 🔒 | 🔒 | 🔓⚔️ | 🔓 |

**图例**：🎬 硬切开篇 / 🔓 自由探索 / ⚔️ 指证 / 🔒 未解锁 / 🎮 小玩法

---

## 指证地点速查

| Loop | 指证对象 | 指证地点 |
|------|---------|---------|
| L1 | Morrison | SC3004 警局 |
| L2 | Mary | SC3013 Smith 公寓楼门口 |
| L3 | Helen | SC3008 Helen 家 |
| L4 | Helen 补充 | SC3008 Helen 家 |
| L5 | Bernard | SC3014 Bernard 办公室 |
| L6 | Mickey（控辩对决）| SC3011 Mickey 办公室 |

---

## 新增 / 废弃说明

**新大纲新增场景**：SC3014 Bernard 办公室（L5 解锁）
**新大纲废弃场景**：~~SC3015 三楼走廊~~（旧版残留，本 Unit3 重写后未使用）

**重大语义变化**：
- SC3009：旧版"Continental 银行"→ 新版统一"湖滨信托银行公共区"
- SC3011：旧版"街角"→ 新版"Mickey 律师事务所"（L1 开篇 + L5 开篇 + L6 控辩对决）

---

## 美术参考统一规范

- 时代：1928 年芝加哥
- 色调：阴郁、冷调（湖区雾气感）
- 室内：低瓦数白炽灯 + 煤气取暖
- 街道：石板路 + 偶尔的小汽车 + 黑烟蒸汽
- 服装：1920s 西装 / 长大衣 / Flapper 风格（女性）
