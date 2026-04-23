# 13 Morrison 家

**state ID**：`9013`（90xx = 场景命名空间；全 6 Loop 共用此 ID）

**位置**：酒吧外（Morrison 私宅）
**戏剧作用**：L6 赌债欠条 + 借 Whale 钱记录 + 藏起来的弹壳 + 马票存根；Whale 调查电话唯一登场

---

## Loop 1

**状态**：未出现
**说明**：L1 Morrison 尚未被怀疑。Morrison 家未解锁。

---

## Loop 2

**状态**：未出现
**说明**：L2 Morrison 保持"嫌麻烦秉公"人设，不暴露被收买暗示。Morrison 家未解锁。

---

## Loop 3

**状态**：未出现
**说明**：L3 Morrison 仍在"姑且秉公"人设内。Morrison 家未解锁。

---

## Loop 4

**状态**：未出现
**说明**：L4 Morrison 看到 .45 弹壳变脸（turn_cutscene）、强押 Vivian——暗示其被收买，但尚未揭露 Whale 关联。Morrison 家未解锁。

---

## Loop 5

**状态**：未出现
**说明**：L5 聚焦 James 线 + 蓝月亮后门 arrest。Morrison 家未解锁。

---

## Loop 6

**状态**：出现（搜证 + 🎬 Whale 电话突发事件 + ⚡ 转场警局）
**场景类型**：🎬 硬切（Zack+Emma 采访为由进入）→ 🔓 自由探索（Morrison 本人不在）
**解锁条件**：L6 剧情推进自动解锁（Morrison 在警局值班，搜查窗口）

### 场景描述
Zack 和 Emma 来到 Morrison 的住所。Morrison 本人不在（在警局值班）——这是搜查的窗口。房间陈设简朴却藏着 Morrison 不能让人看到的东西：一叠赌债欠条（9603）、一份向 Whale 借款的记录（9604）、Morrison 自己藏起来的另一枚 .45 弹壳（9605，场景道具）、以及一叠厚厚的华盛顿公园赛场马票存根（9606，环境叙事）。搜查进行到中段，Morrison 家的电话突然响起。

### 🎬 Whale 调查电话（phone_call_event）[U9-L6-INT-01]

Morrison 家的电话响起。Zack 接了。电话另一端的声音低沉、不疾不徐，带着一种俯视一切的从容。他知道 Zack 和 Emma 在查案，知道 James 已经死了，也知道他们接下来要做什么。Zack 问他是谁。对方说：他就是 Whale。Zack 没有开口。Whale 只说了一句话，随后挂断，不等 Zack 回答：

> **"我在看你们能走多远。"**

叙事意义：Whale 首次以声音形式直接登场——此前他只是"影子"，现在有了声音。七个字、平静、犬儒——不威胁，不阻止，但态度居高临下。挂断电话不等 Zack 回答——Whale 不与 Zack 平等对话，他只是"宣告"。Unit9 结束后 Whale 的形象依然是"空头像"。

**产出证词**：6111001 — Whale（电话）："我在看你们能走多远"（不作为任何疑点 condition，仅插入剧情证言）

### NPC 列表
无（Morrison 本人不在；Whale 仅以声音形式登场，不设 NPC 条目）

### 可获取证据
| ID | 名称 | 类型 | 可拾取 | note |
|---|---|---|:---:|---|
| 9603 | Morrison 欠疤面煞星 5000 美元赌债欠条 | item | ✅ | 关键——疑点 9601 condition；L6 R2 击穿件（两件必须同时出示） |
| 9604 | Morrison 借 Whale 钱的记录 | item | ✅ | 关键——疑点 9601 condition；L6 R2 击穿件（W 先生借 $6,000，Webb 案前三周） |
| 9605 | Morrison 藏起来的弹壳 | item | ✅ | 场景道具——不进疑点 condition（裁决 8）；加固藏证行为；弹底 MILLER ARMS |
| 9606 | 华盛顿公园赛马场整赛季马票存根 | envir | ❌ | 场景道具——环境叙事；辅助说明 Morrison 赌博成瘾深度 |

### 后续场景
搜证完成 + 电话事件结束后，Zack 和 Emma 带着五件证据（9401、9601、9503、9603、9604）前往**警局 Morrison 办公室**（9014 transition_cutscene）进入 Expose Morrison 三轮谎言。
