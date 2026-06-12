# 15 James 家客厅

**state ID**：`9015`（90xx = 场景命名空间；全 6 Loop 共用此 ID）

**位置**：酒吧外（James 和 Anna 的住处——客厅）
**戏剧作用**：L5 Anna 首次出场迎客 + James 给 Whale 的回信 + Berlitz 英语练习书（倒写 J 三物闭环）

**美术资源**：复用 EPI01 `SC013_bg_JamesHomeLivingRoom`（原 Jimmy 家客厅）

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

**状态**：出现（Anna 首次出场）
**场景类型**：🔓 自由探索（新开放）
**解锁条件**：L5 剧情推进自动解锁（与 9012 卧室同步开放）

### 场景描述
Zack 和 Emma 进入 James 家客厅——Anna 在这里迎接。客厅桌面上放着 James 最近写的回信草稿 + 一本摊开的 Berlitz 英语练习书。Anna 是 James 的妻子，L5 首次出场，她不知道 James 是凶手。

### NPC 列表
| NPC | is_liar | 关键证词 |
|---|:---:|---|
| Anna（anna_001） | false | 9085001（怀孕 + 家里急需大笔钱）/ 9085002（身份：James 的妻子） |

**Anna blind_spots**：James 是凶手 / Whale 是谁 / James 本 Loop 末会自杀。

### 可获取证据
| ID | 名称 | 类型 | 可拾取 | note |
|---|---|---|:---:|---|
| 9503 | James 给 Whale 的回信 / James's Reply Letter to Whale | item | ✅ | 关键——疑点 9504 condition；L5 R3 击穿件；L6 R3 复用；倒写 J 与 9302/9402 一致；末尾暗示"交接后归还那件东西" |
| 9504 | Berlitz 英语练习书 / Berlitz English Practice Book | envir | ❌ | 场景道具——L5 R4 叙事收尾引用（倒写 J 闭环）；post_expose 点名；不作手持物证出示 |

---

## Loop 6

**状态**：未出现
**说明**：L6 James 已自杀，Anna 不再作为调查对象。L6 聚焦 Morrison 家 + 警局。
