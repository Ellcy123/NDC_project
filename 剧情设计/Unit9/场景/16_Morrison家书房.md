# 16 Morrison 家书房

**state ID**：`9016`（90xx = 场景命名空间；全 6 Loop 共用此 ID）

**位置**：酒吧外（Morrison 私宅——书房）
**戏剧作用**：L6 赌债欠条 + 借 Whale 钱记录 + 9401 弹壳找回（L4 被 Morrison 夺走、藏于书桌抽屉深处）+ 9605 藏起来的弹壳（场景道具加固藏证行为）

**美术资源**：复用 EPI01 `SC006_bg_MorrisonHomeStudy`（原 Morrison 家书房）

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
**说明**：L4 Morrison 看到 .45 弹壳变脸（turn_cutscene）、强押 Vivian——暗示其被收买。9401 弹壳此时被 Morrison 当场夺走、带回自家藏匿。Morrison 家未解锁。

---

## Loop 5

**状态**：未出现
**说明**：L5 聚焦 James 线 + 蓝月亮后门 arrest。Morrison 家未解锁。

---

## Loop 6

**状态**：出现（核心搜证场景）
**场景类型**：🔓 自由探索（Morrison 本人不在；与 9013 客厅同步开放）
**解锁条件**：L6 剧情推进自动解锁（Morrison 在警局值班，搜查窗口）

### 场景描述
Morrison 的私人书房。书桌抽屉最深处藏着他最不想让人看到的东西：赌债欠条（9603）、向 Whale 借款的记录（9604）、以及 L4 末从 Zack 手中夺走后藏匿于此的那枚 .45 弹壳（9401）——用一本过期台历压着。桌面上另一枚弹壳（9605）作为藏证行为的补充叙事道具。房间整体陈设冷峻、公事公办，但抽屉深处的藏品却与主人表面的"秉公警察"形象彻底冲突。

### NPC 列表
无（Morrison 在警局值班；搜查窗口期）

### 可获取证据
| ID | 名称 | 类型 | 可拾取 | note |
|---|---|---|:---:|---|
| 9603 | Morrison 欠疤面煞星 5000 美元赌债欠条 | item | ✅ | 关键——疑点 9601 condition；L6 R2 击穿件（两件必须同时出示） |
| 9604 | Morrison 借 Whale 钱的记录 | item | ✅ | 关键——疑点 9601 condition；L6 R2 击穿件（W 先生借 $6,000，Webb 案前三周） |
| 9401 | .45 警用弹壳（找回）/ .45 ACP Police-Issue Casing (Retrieved) | item | ✅ | 关键——L6 Expose R1 击穿件（与 9601 配对）；L4 被 Morrison 夺走后藏于书桌抽屉最深处；状态从 confiscated_by_morrison → retrieved_from_confiscation |
| 9605 | Morrison 藏起来的弹壳 | item | ✅ | 场景道具——不进疑点 condition（裁决 8）；加固藏证行为；弹底 MILLER ARMS |

### 与 9013 客厅的关系
9013 客厅是 Whale 电话事件发生地 + 9606 马票环境叙事；9016 书房承载所有核心取证。两个场景属同一栋房子的两间相邻房间，玩家在搜查过程中可自由切换。

### 后续场景
搜证完成 + 9013 电话事件结束后，Zack 和 Emma 带着五件证据（9401、9601、9503、9603、9604）前往**警局 Morrison 办公室**（9014 transition_cutscene）进入 Expose Morrison 三轮谎言。
