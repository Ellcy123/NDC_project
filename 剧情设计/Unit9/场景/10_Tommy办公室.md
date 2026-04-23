# 10 Tommy 办公室

**state ID**：`9010`（90xx = 场景命名空间；全 6 Loop 共用此 ID）

**位置**：2F（酒吧经理值班处）
**戏剧作用**：L2 指证 Tommy 场所（账本 + 排班表）；L4 Rita 间谍指认 + Whale 身份确认；L5 完整节目单 + Vivian 修改申请

---

## Loop 1

**状态**：未出现
**说明**：L1 玩家活动集中在 Webb 会客室。Tommy 办公室未解锁。

---

## Loop 2

**状态**：出现（搜证 + ⚔️ 指证 Tommy）
**场景类型**：🔓 自由探索 + ⚔️ Expose
**解锁条件**：L2 自由探索阶段自动解锁

### 场景描述
Tommy 是酒吧经理兼账房，在自己办公室接受 Zack 的问话。他表面承认酒吧有私酒生意，但隐瞒了勒索业务和收入差额。Tommy 的酒吧账本和 Vivian 排班表存放在此。⚔️ **指证场所**：Tommy 是本 Loop 的 Expose 对象。

### NPC 列表
| NPC | is_liar | 关键证词 |
|---|:---:|---|
| Tommy（tommy_l2） | true（L2 Expose 对象；三层退守：只有私酒 → 账目清白 → 古董卖出） | 2050201（⚠谎言：只有私酒 — R1 指证目标）/ 2050202（Vivian 23:30 送酒）/ 2050203（身份） |

### 可获取证据
| ID | 名称 | 类型 | 可拾取 | note |
|---|---|---|:---:|---|
| 9204 | Tommy 酒吧账本 / Tommy's Bar Ledger | item | ✅ | 关键——疑点 9202 condition；L2 R2 击穿件（配 9203 收入差额） |
| 9208_vivian_schedule | Vivian 排班表 / Vivian's Work Schedule | item | ❌ | 场景道具——确认 Vivian 23:30 送酒惯例 |

---

## Loop 3

**状态**：未出现
**说明**：L3 Tommy 未驻场（焦点在 Rosa 指证 + 会客室深度搜证）。Tommy 办公室此 Loop 不开放。

---

## Loop 4

**状态**：出现（Rita 间谍指认 + Whale 身份确认）
**场景类型**：🔓 自由探索
**解锁条件**：L3 post_expose Rosa 交出 .45 弹壳（9401）后，持弹壳追问 Tommy 触发

### 场景描述
Tommy 在自己的办公室。Zack 带着 .45 弹壳（9401）前来追问。

**核心叙事（主线）**：Zack 出示 .45 弹壳并追问 Webb 惹上的大人物——Tommy 在 Zack 强调"这对 Vivian 脱罪十分关键"后松口指认：大人物就是 Whale；Whale 甚至在酒吧里派了人渗透（Rita）。Tommy 正式指认："这个酒吧里知道 Whale 的，除了 Webb，只有前勒索人和现勒索人。"

**弹壳背景（次线）**：Tommy 认出 9401 弹壳，给出他见过这类枪的亲身经历（被枪击大腿）；之后那份工作由另一个人接手（不点名，L5 才揭示是 James）。

### NPC 列表
| NPC | is_liar | 关键证词 |
|---|:---:|---|
| Tommy（tommy_L4_001） | false | 4050401（Rita 是 Whale 派来的间谍；疑点 9401 condition）/ 4050402（知道 Whale 的只有前/现勒索人；L5 疑点 9504 condition） |

### 携带证据（carried_evidence）
| ID | 来源 Loop | 用途 |
|---|:---:|---|
| 9401 | L3 post_expose | 出示给 Tommy，触发 Rita 间谍指认 + Whale 身份确认对话链 |

### 可获取证据
无（本场景无可拾取新物证，核心是证词）

---

## Loop 5

**状态**：出现（完整节目单 + Vivian 修改申请）
**场景类型**：🔓 自由探索（玩家搜证 → Tommy 回应交代）
**解锁条件**：L5 自由探索阶段自动解锁

### 场景描述
Tommy 在自己的办公室里。他没有主动拿出任何东西——完整节目单（9501）和 Vivian 的节目修改申请（9502）静静地放在他办公桌的文件堆里，等玩家自己搜证发现。Zack 翻出这两件后，Tommy 并不阻拦，只是平静地解释："本来也是想给你的。"他对 Morrison 把 Vivian 强押回警局这件事深感同情。他追加了一条关键证言：知道 Whale 存在的人，在这家酒吧只有前勒索人和现勒索人——然后郑重对 Zack 说：希望你能查明真相，还 Vivian 清白。

### NPC 列表
| NPC | is_liar | 关键证词 |
|---|:---:|---|
| Tommy（tommy_003） | false | 5050501（追加：知道 Whale 的只有前/现勒索人——与 4050402 同内容，独立 ID）/ 5050502（情感托付：恳请 Zack 查明真相） |

### 可获取证据
| ID | 名称 | 类型 | 可拾取 | note |
|---|---|---|:---:|---|
| 9501 | 完整节目单 / Complete Program List | item | ✅ | 关键——疑点 9503 condition；L5 R1 击穿件；23:00 鼓点高潮掩盖真实枪声 |
| 9502 | 节目修改申请 / Program Modification Request | item | ✅ | 关键——疑点 9503 condition；L5 R1 击穿件；Vivian 亲笔申请调至最高音量（证明 23:00 鼓点被刻意安排） |

---

## Loop 6

**状态**：未出现
**说明**：L6 聚焦 Morrison 家 + 警局。Tommy 办公室不开放。
