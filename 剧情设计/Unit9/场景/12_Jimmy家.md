# 12 Jimmy 家

**state ID**：`9012`（90xx = 场景命名空间；全 6 Loop 共用此 ID）

**位置**：酒吧外（Jimmy 和 Anna 的住处）
**戏剧作用**：L5 Anna 证言、Jimmy 给 Whale 回信、英语练习书（倒写 J 三物闭环）、撕碎申请表（爱尔兰裔身份）

---

## Loop 1

**状态**：未出现
**说明**：L1 Jimmy 尚未被聚焦为重点怀疑对象。Jimmy 家未解锁。

---

## Loop 2

**状态**：未出现
**说明**：L2 Jimmy 是背景噪音，不作为重点追踪对象。Jimmy 家未解锁。

---

## Loop 3

**状态**：未出现
**说明**：L3 聚焦酒吧内 Rosa 时间线 + Jimmy 销毁节目单插入剧情。Jimmy 家未解锁。

---

## Loop 4

**状态**：未出现
**说明**：L4 聚焦酒吧内 Vivian 救人线。Jimmy 家未解锁。

---

## Loop 5

**状态**：出现（Anna 首次出场 + 三件关键证据）
**场景类型**：🔓 自由探索（新开放）
**解锁条件**：L5 剧情推进自动解锁

⚠ **ID 命名说明**：本场景 state ID = `9012`（90xx 段为场景命名空间，与物品/疑点段 91xx–96xx 分离）。

### 场景描述
Zack 和 Emma 来到 Jimmy 的家。Anna 是 Jimmy 的妻子，L5 首次出场。Anna 不知道 Jimmy 是凶手——她只知道丈夫接了一件"重要的差事"，说能解决经济困难。三件关键证据在此处发现：
- **9503** Jimmy 给 Whale 的回信（可拾取）
- **9504** Berlitz 英语练习书（envir，不拾取；Zack 观察到倒写 J，与 9302 纸条、9402 合同一致）
- **9505** 撕碎的移民申请表（可拾取；确认爱尔兰裔身份 James O'Sullivan）

### NPC 列表
| NPC | is_liar | 关键证词 |
|---|:---:|---|
| Anna（anna_001） | false | 5080501（怀孕 + 家里急需大笔钱）/ 5080502（身份：Jimmy 的妻子） |

**Anna blind_spots**：Jimmy 是凶手 / Whale 是谁 / Jimmy 本 Loop 末会自杀。

### 可获取证据
| ID | 名称 | 类型 | 可拾取 | note |
|---|---|---|:---:|---|
| 9503 | Jimmy 给 Whale 的回信 / Jimmy's Reply Letter to Whale | item | ✅ | 关键——疑点 9504 condition；L5 R3 击穿件；L6 R3 复用；倒写 J 与 9302/9402 一致；末尾暗示"交接后归还那件东西" |
| 9504 | Berlitz 英语练习书 / Berlitz English Practice Book | envir | ❌ | 场景道具——L5 R4 叙事收尾引用（倒写 J 闭环）；post_expose 点名；不作手持物证出示 |
| 9505 | 撕碎的移民申请表 / Torn Immigration Application | item | ✅ | 关键——疑点 9501 condition；L5 R2 击穿件（配合口音证词 5070501）；James O'Sullivan，科克郡 |

---

## Loop 6

**状态**：未出现
**说明**：L6 Jimmy 已自杀，Anna 不再作为调查对象。L6 聚焦 Morrison 家 + 警局。
