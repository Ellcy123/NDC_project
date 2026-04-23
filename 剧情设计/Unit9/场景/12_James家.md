# 12 James 家

**state ID**：`9012`（90xx = 场景命名空间；全 6 Loop 共用此 ID）

**位置**：酒吧外（James 和 Anna 的住处）
**戏剧作用**：L5 Anna 证言、James 给 Whale 回信、英语练习书（倒写 J 三物闭环）、Anna 的合法移民通过通知（附 James 配偶资格书——坐实爱尔兰裔身份 + 揭露 James 仍是非法身份、正靠 Anna 通过走配偶豁免的动机底色）

---

## Loop 1

**状态**：未出现
**说明**：L1 James 尚未被聚焦为重点怀疑对象。James 家未解锁。

---

## Loop 2

**状态**：未出现
**说明**：L2 James 是背景噪音，不作为重点追踪对象。James 家未解锁。

---

## Loop 3

**状态**：未出现
**说明**：L3 聚焦酒吧内 Rosa 时间线 + James 销毁节目单插入剧情。James 家未解锁。

---

## Loop 4

**状态**：未出现
**说明**：L4 聚焦酒吧内 Vivian 救人线。James 家未解锁。

---

## Loop 5

**状态**：出现（Anna 首次出场 + 三件关键证据）
**场景类型**：🔓 自由探索（新开放）
**解锁条件**：L5 剧情推进自动解锁

⚠ **ID 命名说明**：本场景 state ID = `9012`（90xx 段为场景命名空间，与物品/疑点段 91xx–96xx 分离）。

### 场景描述
Zack 和 Emma 来到 James 的家。Anna 是 James 的妻子，L5 首次出场。Anna 不知道 James 是凶手——她只知道丈夫接了一件"重要的差事"，说能解决经济困难。三件关键证据在此处发现：
- **9503** James 给 Whale 的回信（可拾取）
- **9504** Berlitz 英语练习书（envir，不拾取；Zack 观察到倒写 J，与 9302 纸条、9402 合同一致）
- **9505** Anna 的合法移民申请通过通知（可拾取；卧室梳妆抽屉妥善收存；附 James 作为 Anna 配偶的非配额移民申请资格书——坐实 James O'Sullivan 爱尔兰科克郡出身 + 揭露 James 仍是非法身份）

### NPC 列表
| NPC | is_liar | 关键证词 |
|---|:---:|---|
| Anna（anna_001） | false | 5080501（怀孕 + 家里急需大笔钱）/ 5080502（身份：James 的妻子） |

**Anna blind_spots**：James 是凶手 / Whale 是谁 / James 本 Loop 末会自杀。

### 可获取证据
| ID | 名称 | 类型 | 可拾取 | note |
|---|---|---|:---:|---|
| 9503 | James 给 Whale 的回信 / James's Reply Letter to Whale | item | ✅ | 关键——疑点 9504 condition；L5 R3 击穿件；L6 R3 复用；倒写 J 与 9302/9402 一致；末尾暗示"交接后归还那件东西" |
| 9504 | Berlitz 英语练习书 / Berlitz English Practice Book | envir | ❌ | 场景道具——L5 R4 叙事收尾引用（倒写 J 闭环）；post_expose 点名；不作手持物证出示 |
| 9505 | Anna 的合法移民申请通过通知 / Anna's Immigration Approval Notice | item | ✅ | 关键——疑点 9501 condition；L5 R2 击穿件（配合口音证词 9075001）；卧室梳妆抽屉妥善收存；附件《James 配偶非配额申请资格书》坐实 James O'Sullivan 科克郡身份 + 揭露 James 仍是非法身份 |

---

## Loop 6

**状态**：未出现
**说明**：L6 James 已自杀，Anna 不再作为调查对象。L6 聚焦 Morrison 家 + 警局。
