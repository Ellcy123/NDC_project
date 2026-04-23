# 14 警局 Morrison 办公室

**state ID**：`9014`（90xx = 场景命名空间；全 6 Loop 共用此 ID）

**位置**：芝加哥警察局（酒吧外 / 警局内）
**戏剧作用**：L6 Expose Morrison 的指证场所——Morrison 官僚得意+主动屏退下属即最强自证

---

## Loop 1

**状态**：未出现
**说明**：L1 聚焦 Webb 会客室开场指证 Rosa。警局未出现。

---

## Loop 2

**状态**：未出现
**说明**：L2 聚焦 2F 办公室线（勒索生意）+ 指证 Tommy。警局未出现。

---

## Loop 3

**状态**：未出现
**说明**：L3 聚焦酒吧内时间线推理（Rosa 指证）。警局未出现。

---

## Loop 4

**状态**：未出现
**说明**：L4 聚焦酒吧内救 Vivian 线 + turn_cutscene（Morrison 强押 Vivian 至警局关押发生，但事件在酒吧大厅触发，警局本身未作为场景登场）。警局未出现。

---

## Loop 5

**状态**：未出现
**说明**：L5 聚焦 James 线 + 蓝月亮酒吧后门 arrest_cutscene。警局未出现。

---

## Loop 6

**状态**：出现（🎭 转折过场 → ⚔️ Expose Morrison 入口）
**场景类型**：🎭 Transition cutscene（到达后自动进入指证）
**解锁条件**：L6 在 Morrison 家搜证 + 🎬 Whale 电话事件结束 → Zack 和 Emma 带五件证据（9401、9601、9503、9603、9604）前往警局

### 场景描述
Zack 和 Emma 带着五件证据（9401、9601、9503、9603、9604）来到警察局。Morrison 在自己的办公室里——Zack 选择单独面对他，不公开对质。Emma 站在 Zack 身侧，两人推门进去。

Morrison 正在向一个下属吹嘘 Vivian 案办得如何神速、手脚如何干净——官僚的得意感令人不适。随后他主动赶走下属，要求私下谈判。**这个动作本身就是最强的自证。**

### 叙事要求（scene_note）
- Morrison 吹嘘语言要有官僚得意感（讨论结论风险 A）
- 主动赶走下属是自证行为（讨论结论风险 B）

### NPC 列表
| NPC | is_liar | 备注 |
|---|:---:|---|
| Morrison | true（L6 Expose 对象，三轮谎言） | target_npc_id = 104；target_talk = morrison_expose_loop6；过场结束直接进 Expose，不在本场景抽取对话证词 |
| （下属 — 一闪而过） | - | 无台词细节；Morrison 主动屏退他 |

### 可获取证据
无（过场 + Expose 入口；本场景不新增物证，使用 Morrison 家 9613 取得的五件证据进入三轮指证）

### 携带证据（carried_evidence — 用于 Expose）
| ID | 来源 | 用途 |
|---|---|---|
| 9401 | L3 Rosa post_expose 继承 | .45 弹壳（Morrison R1 / R2 线索） |
| 9601 | L5 James 自杀现场继承 | 米勒集团特制手枪（R3 凶器闭环） |
| 9503 | L5 James 家 | James 给 Whale 的回信（R3 Whale 关联维度） |
| 9603 | L6 Morrison 家 | 赌债欠条（R2 同时出示） |
| 9604 | L6 Morrison 家 | 借 Whale 钱记录（R2 同时出示） |

### 后续
过场结束 → 进入 ⚔️ **Expose Morrison**（三轮谎言：官僚说辞 → 我没收钱 → 我不认识 Whale）。
