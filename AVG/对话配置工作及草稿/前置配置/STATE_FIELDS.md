# Loop State 文件字段说明

本文档说明 `loop1_state.yaml` ~ `loop6_state.yaml` 中所有字段的含义和使用规则。

---

## 文件总体结构

```
文件头注释（循环概要）
├── player_context          — 玩家视角
├── opening                 — 开篇对话
│   ├── emma_00X            — Emma 对话（保持 knows/does_not_know）
│   └── 其他开篇 NPC        — 如 rose_002（L5）
├── scenes                  — 自由探索场景列表
│   ├── evidence            — 场景内证据
│   └── npcs                — 场景内 NPC
├── expose                  — 指证系统
│   ├── target NPC          — 被指证者
│   ├── round_1 ~ round_N   — 各轮指证
│   └── 特殊机制            — 如 vinnie_false_confession、inducement_system
└── doubts                  — 疑点列表
```

---

## 一、player_context（玩家视角）

每个循环文件顶部，描述玩家进入该循环时的认知状态和调查方向。

| 字段 | 类型 | 说明 |
|------|------|------|
| `goals.primary` | string | 本循环的核心调查问题 |
| `goals.secondary` | list | 次要调查问题 |
| `known_facts` | list | 进入本循环时玩家已确认的事实（来自前序 Expose） |
| `new_directions` | list | 新的调查方向 |
| `new_directions[].direction` | string | 方向名称 |
| `new_directions[].trigger` | string | 触发该方向的信息来源 |
| `post_expose_knowledge` | list | 本循环 Expose 结束后玩家获得的新知识 |

**规则：**
- `known_facts` = 上一循环的 `post_expose_knowledge` + 之前累积
- L1 的 `known_facts` 为空（`[]`），因为玩家什么都不知道
- 每个循环的 `post_expose_knowledge` 应出现在下一循环的 `known_facts` 中

---

## 二、NPC 条目结构

每个 NPC 条目由 **基本信息 + 4 个区块** 组成：

```
NPC 条目
├── 基本信息               — talk, is_liar, motive, mindset
├── 1. NPC 已知信息        — knowledge_pool / awareness + active/withheld_topics
├── 2. 玩家询问意图        — player_inquiry
├── 3. 可提取证词          — testimony_ids
└── 4. 鉴赏力              — connoisseur
```

### 2.1 基本信息

| 字段 | 类型 | 说明 |
|------|------|------|
| `talk` | string | 对应的对话文件 ID |
| `is_liar` | bool | 是否为本循环的说谎者（Expose 对象） |
| `motive` | string | NPC 参与对话的动机 |
| `mindset` | string | NPC 当前的心理状态 |

### 2.2 区块 1：NPC 已知信息

NPC 的知识根据出场模式分为四种写法：

#### 模式 A：首次出场（引用知识池）

知识池（`knowledge_pool` + `blind_spots`）已提取到独立文件 `npc_knowledge_pools.yaml`，不再内联写在 state 文件中。

在 NPC 条目的"区块 1"处写引用注释 `# 知识池见 npc_knowledge_pools.yaml → {npc_name}`，然后：

| 字段 | 类型 | 说明 |
|------|------|------|
| `active_topics` | list | 本循环**会展示**的知识池主题 |
| `withheld_topics` | list | 本循环**刻意不展示**的知识池主题 |

#### 模式 B：后续出场（引用知识池 + awareness）

同样写注释 `# 知识池见 npc_knowledge_pools.yaml → {npc_name}`，然后：

| 字段 | 类型 | 说明 |
|------|------|------|
| `awareness` | list | **实时认知变化**——因游戏事件获得的新知识 |
| `blind_spots_L{N}` | list | 该循环特有的信息盲区（可选，仅在关键时使用） |
| `active_topics` | list | 本循环**会展示**的知识池主题 |
| `withheld_topics` | list | 本循环**刻意不展示**的知识池主题 |

#### 模式 C：Emma（特殊，保持原结构）

| 字段 | 类型 | 说明 |
|------|------|------|
| `knows` | list | Emma 本循环知道的信息（每循环不同，全部动态） |
| `does_not_know` | list | Emma 本循环不知道的信息 |
| `lie` | null | 始终为 null（Emma 不撒谎） |

Emma 不使用 knowledge_pool / active_topics / withheld_topics。

#### 模式 D：一次性 NPC（如 emma_foster）

保留 `knows` / `does_not_know`，因为只出场一次，不需要知识池。

### 2.3 知识池详细规则

**`knowledge_pool` + `blind_spots`** — 已提取到独立文件

所有 8 个 NPC 的知识池和盲区已集中维护在 `npc_knowledge_pools.yaml` 中：

```yaml
# npc_knowledge_pools.yaml 结构示例
ohara:
  knowledge_pool:
    frank:
      - 快十年的老邻居
      - 腿不好，1912年港口事故伤的
    loan:
      - 和Frank都向湖滨信托借了钱
  blind_spots:
    - Frank贷款具体利率
    - Leonard和Vinnie的指挥关系
```

- 内容是该 NPC 始终知道的事实，不因循环推进而改变
- 按主题（topic）分类，方便后续引用和控制展示范围
- `blind_spots` 标注该 NPC 在整个游戏中**永远不会知道**的信息
- state 文件中通过 `# 知识池见 npc_knowledge_pools.yaml → {npc_name}` 引用

**`awareness`** — 实时认知变化

```yaml
awareness:
  - content: 新获得的认知
    trigger: 触发该认知的游戏事件
```

- 仅用于**动态 NPC 的非首次出场**
- 标注因游戏进程（如前序 Expose、NPC 被捕等）而获得的新知识
- 每条必须有明确的 `trigger`
- 适用于：Leonard、Moore、Morrison、Tony
- 不适用于：O'Hara、Danny、Rose、Vinnie（纯固定知识）

### 2.4 区块 2：玩家询问意图

量化玩家对该 NPC 各话题的提问意愿，每次出场都要写。

```yaml
player_inquiry:
  - "场景道具催款单"  # 7
  - "Emma说O'Hara被威胁不开门"  # 9
```

每条为一个字符串（驱动提问的信息来源），`#` 后为提问意愿强度（0-10 分）。

**评分标准：**

| 分数 | 含义 | 典型场景 |
|------|------|---------|
| 10 | 必问 | 核心悬念直接相关，如遗嘱曝光后问 Rose 身份 |
| 8-9 | 强动机 | 前序 Expose 揭示的线索直接指向该话题 |
| 6-7 | 中等 | 有线索暗示但非核心焦点 |
| 4-5 | 弱动机 | NPC 主动提及引发好奇，但无硬线索驱动 |
| 2-3 | 几乎不会问 | 无触发信息，纯背景探索 |
| 0 | 被动触发 | 不是玩家主动提问，而是在 Expose/鉴赏力中被逼出 |

**规则：**
- Expose 对象的 `player_inquiry` 设为 `null`（指证中被动回应，非主动提问）

### 2.5 区块 3：可提取证词

```yaml
testimony_ids:
  - 2091001  # 证词描述
  - 2091002  # ⚠谎言: 谎言证词描述
  - 2071001  # ⚠偏见: 偏见证词描述
```

- 只列 7 位证词 ID + 简短注释
- 谎言证词用 `⚠谎言:` 标注
- 偏见/错误证词用 `⚠偏见:` 标注
- 证词 ID 格式: `{loop}{npc}{sequence}`（如 2091001 = Loop2 的 09 号 NPC 的第 001 条）
- ID 与对话草稿中的 `get` 标记保持一致

### 2.6 区块 4：鉴赏力

统一使用 `connoisseur` 字段，用 `type` 区分素材和考题：

```yaml
connoisseur:
  # 素材（为后续考题提供信息）
  - type: source
    content: 信息内容
    note: "后面要考——XXX"

  # 考题（本 NPC 出的题）
  - type: quiz
    node: "#XXX"                    # 对话节点编号（可选）
    question: "问题"
    answer: "正确答案（含来源标注）"
    note: "设计备注（可选）"
```

| type | 说明 |
|------|------|
| `source` | 鉴赏力素材——本次对话中出现的信息，后续某个 NPC 会据此出考题 |
| `quiz` | 鉴赏力考题——考查玩家是否记住了之前某次对话中的信息 |

### 2.7 各 NPC 知识池位置速查

| NPC | 首次出场（知识池所在文件） | 后续出场 | 知识类型 |
|-----|------------------------|---------|---------|
| Emma | — | L1-L6 | 全动态（knows/does_not_know） |
| emma_foster | L1（一次性） | — | 保留 knows/does_not_know |
| Morrison | L1 expose | L6 | 混合（L6 加 awareness） |
| O'Hara | L2 | L3, L4 | 纯固定 |
| Tony | L2 | L5*, L6 | 固定为主（L5/L6 加 awareness） |
| Vinnie | L2 | L5 | 纯固定 |
| Moore | L2 | L3, L6 | 混合（L3/L6 加 awareness） |
| Leonard | L2 | L3, L4, L6 | 混合（最复杂，每次加 awareness） |
| Danny | L3 | L4(expose) | 纯固定（含错误认知） |
| Rose | L4 | L5 | 纯固定 |

---

## 三、active_topics / withheld_topics（展示范围控制）

控制本循环中 knowledge_pool 的哪些子集对玩家可见。

```yaml
active_topics: [frank(基础背景), loan(连号钞票+借贷经过)]
withheld_topics: [rose, frank(举报部分), neighborhood]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `active_topics` | list | 本循环对话中**会展示**的知识池主题（或子集） |
| `withheld_topics` | list | 本循环**刻意不展示**的知识池主题（留给后续循环） |

**规则：**
- `active_topics` + `withheld_topics` 应覆盖 knowledge_pool 的全部主题
- 括号内注明子集范围，如 `vinnie(部分：不含踢门)` 表示只展示 Vinnie 相关知识的一部分
- 每个 `withheld_topics` 中的主题必须在后续循环的 `active_topics` 中被释放
- 最终循环（L6）的 `withheld_topics` 应为 `[]`（全部释放）

**释放链示例（O'Hara）：**
```
L2: withheld [rose, frank(举报部分), neighborhood]
  → L3: active [frank(完整含举报)], withheld [rose]
    → L4: active [rose, neighborhood], withheld []
```

---

## 四、Expose 相关字段

### 4.1 Expose 目标 NPC 的谎言

谎言（`lie`）只写在 expose 段落中，NPC 条目不再保留 lie 字段。

| 字段 | 类型 | 说明 |
|------|------|------|
| `lie.content` | string | 谎言内容（多轮时按 Round 分列） |
| `lie.truth` | string | 谎言背后的真相 |
| `lie.break_condition` | string | 击破条件（需要哪些证据） |
| `lie.post_break` | string | 击破后的结果（NPC 反应 + 获得的新信息/证据） |

非 Expose NPC 如果在对话中说了谎言，在 `testimony_ids` 上用 `⚠谎言:` 标注。

### 4.2 Expose 轮次

```yaml
round_N:
  lie: "该轮的谎言内容"
  lie_source: "谎言来源（证词 ID 或'NPC的新谎言'）"
  usable_evidence:
    - id: 证据ID
      name: 证据名称
      用途: 该证据如何反驳谎言
  result: "该轮结果（NPC 的反应 + 是否转入新谎言）"
```

**规则：**
- 第一轮的 `lie_source` 必须对应 Talk 中已收集的证词
- 后续轮的 `lie_source` 为 NPC 在 Expose 中被逼出的新谎言
- `usable_evidence` 中的证据 ID 必须是玩家在自由探索阶段可获取的

---

## 五、其他字段

### 5.1 doubts（疑点）

```yaml
doubts:
  - id: 4位数字
    text: "疑点问题"
    unlock_condition: "解锁条件（至少两种不同来源交叉验证）"
```

### 5.2 evidence（证据）

```yaml
evidence:
  - id: 4位数字
    name: 证据名称
    note: "设计备注"
```

### 5.3 scenes（场景）

```yaml
scenes:
  - id: 4位数字
    name: 场景名称
    evidence: [...]        # 该场景可获取的证据
    npcs: {...}            # 该场景的 NPC
```

---

## 六、字段变更历史

### 第一次重构（知识池引入）

| 操作 | 旧字段 | 新字段 | 适用范围 |
|------|--------|--------|---------|
| 替换 | `knows` | `knowledge_pool` | 首次出场的非 Emma NPC |
| 替换 | `does_not_know` | `blind_spots` | 首次出场的非 Emma NPC |
| 新增 | — | `awareness` | 动态 NPC 的非首次出场 |
| 新增 | — | `player_inquiry` | 所有 NPC 每次出场 |
| 新增 | — | `active_topics` | 所有非 Emma NPC 每次出场 |
| 新增 | — | `withheld_topics` | 所有非 Emma NPC 每次出场 |
| 新增 | — | `player_context` | 文件顶部，每循环一个 |

### 第二次重构（知识池提取）

| 操作 | 说明 |
|------|------|
| **提取** | `knowledge_pool` + `blind_spots` 从 6 个 state 文件中提取到 `npc_knowledge_pools.yaml` |
| **替换** | state 文件中原 knowledge_pool/blind_spots 块改为引用注释 `# 知识池见 npc_knowledge_pools.yaml → {npc}` |
| **校准** | 知识池内容逐条对照 Unit2 设计文档，删除无文档支撑的条目，修正事实错误 |
| **统一** | 后续出场 NPC 引用格式从 `# 知识池见 LX npc_001（固定，未变化）` 改为 `# 知识池见 npc_knowledge_pools.yaml → npc` |

### 第三次重构（结构精简）

| 操作 | 字段 | 说明 |
|------|------|------|
| **删除** | `branch_design` | player_inquiry 已覆盖话题结构 |
| **删除** | `maps_to_branch` | 从 player_inquiry 中移除 |
| **删除** | `background_flavor` | 演出细节不属于 state 文件职责 |
| **删除** | `critical_for_loop6` | 移到 expose 段落注释 |
| **合并** | `connoisseur_source` + `connoisseur_check` → `connoisseur` | 统一用 `type: source/quiz` 区分 |
| **简化** | `testimony` → `testimony_ids` | 只列 ID + 注释，不含完整结构 |
| **移除** | NPC 条目中的 `lie` | 谎言只保留在 expose 段落；非 Expose NPC 的谎言在 testimony_ids 标注 |
| **删除** | `player_inquiry` 中的 `topic` | 话题名称属于对话设计阶段，state 文件只保留 score + trigger |

---

## 七、NPC 条目示例

### 首次出场 NPC

```yaml
ohara_001:
  # ── 基本信息 ──
  talk: ohara_001
  is_liar: false
  motive: 没有主动动机，但内心渴望有人帮忙
  mindset: 恐惧但渴望倾诉

  # ── 1. NPC 已知信息 ──
  # 知识池见 npc_knowledge_pools.yaml → ohara

  active_topics: [frank(基础背景), loan(连号钞票+借贷经过)]
  withheld_topics: [rose, frank(举报部分), neighborhood]

  # ── 2. 玩家询问意图 ──
  player_inquiry:
    - "Emma说O'Hara被威胁不开门"  # 9

  # ── 3. 可提取证词 ──
  testimony_ids:
    - 2091001  # O'Hara确认Vinnie上门催收

  # ── 4. 鉴赏力 ──
  connoisseur:
    - type: source
      content: O'Hara的钞票是崭新连号20美元
      note: "崭新连号钞票（与Vinnie的钞票序号对比是L2指证关键）"
```

### 后续出场 NPC（有 awareness）

```yaml
leonard_002:
  # ── 基本信息 ──
  talk: leonard_002
  is_liar: false
  motive: 甩锅Moore
  mindset: 示好策略
  # 知识池见 npc_knowledge_pools.yaml → leonard

  # ── 1. NPC 已知信息 ──
  awareness:
    - content: L2被Zack拆穿身份
      trigger: L2 Expose结果
  active_topics: [identity(完整), crime_network(完整)]
  withheld_topics: [murder]

  # ── 2. 玩家询问意图 ──
  player_inquiry:
    - "L2被拆穿后想深挖"  # 7

  # ── 3. 可提取证词 ──
  testimony_ids:
    - 2041003  # Leonard声称在Moore银行工作十年
    - 2041007  # ⚠谎言: Leonard声称Vinnie催收是Moore指派的

  # ── 4. 鉴赏力 ──
  connoisseur: []
```

### Emma（保持原结构）

```yaml
emma_003:
  is_liar: false
  motive: 推进调查
  mindset: 务实、急迫

  knows:
    - Mickey已经递交了新的传票申请
  does_not_know:
    - 银行档案室里的具体内容
  lie: null

  connoisseur:
    - type: quiz
      node: "#006"
      question: "O'Hara怎么描述Vinnie的催收方式？"
      answer: "一言不发站在门口（来源：L2 ohara_001）"
```

---

## 八、核心设计理念

1. **NPC 知识是固定的，变的是玩家的提问方向。** O'Hara 一直知道 Rose 在这条街住了四五年，但玩家只有在 L4 遗嘱曝光后才有动机去问她。

2. **knowledge_pool 写一次，后续引用。** 避免每循环重复写相同的 `knows`，减少维护成本和不一致风险。

3. **awareness 只用于真正的实时变化。** 仅当 NPC 因游戏事件（被 Expose、目睹逮捕等）获得了新认知时才使用。

4. **player_inquiry 量化提问优先级。** 帮助对话设计师理解"玩家这时候最想问什么"，指导分支选项的排列顺序和 NPC 对话的重点分配。

5. **active/withheld 控制信息节奏。** 确保同一个 NPC 在不同循环释放不同层次的信息，支撑"每循环只揭示一层真相"的设计原则。

6. **每个 NPC 条目只有 4 个区块。** 已知信息、询问意图、证词、鉴赏力——结构统一，一目了然。
