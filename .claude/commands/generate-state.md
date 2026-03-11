# 设计文档 → State 文件生成工作流

根据指证设计、证据设计、场景表、剧情设计、NPC 知识池和人设，为指定循环生成完整的 `loop{N}_state.yaml`。

---

## 使用方式

用户调用时指定循环编号，例如：`/generate-state 3`（生成 Loop 3 的 state 文件）。

如果用户未指定循环编号，询问要生成哪个循环（1-6）。

---

## 输入文件

执行前**必须**读取以下文件（按优先级排列）。**绝不凭记忆编写任何事实细节。**

### 1. 指证设计（最高优先级 — 决定整个循环的证据需求和信息流向）

路径模式：`剧情设计/Unit2/循环指证设计/Unit2*循环{N}*指证设计*.md`

包含：
- 被指证者身份、核心目标
- 每轮 Lie + 所需证据 + 击破逻辑 + 结果
- 后续循环衔接线索
- Expose 后玩家获得的新知识

### 2. 证据设计

路径模式：`剧情设计/Unit2/证据设计/Unit2_循环{N}_证据美术资产.md`

包含：
- 每个证据的 ID、名称、物品描述、发现位置
- 美术资产描述（在 state 中引用证据时名称必须与此一致）

### 3. 场景状态表

路径：`剧情设计/Unit2/场景/Unit2_全场景循环状态表.md`

包含：
- 每个场景在 6 个循环中的状态（🎬开篇/🔓自由探索/🔒封锁/⏸️无新线索/⚔️指证/⚡突发/🎭结尾）
- 据此确定本循环有哪些场景可进入、哪些是新解锁的

### 4. 剧情大纲

路径：`剧情设计/Unit2/剧情/新的剧情设计.md`

包含：
- 每循环的核心目标、搜证阶段、指证阶段概述
- 人物关系、案情背景、六循环递进结构

### 5. NPC 知识池

路径：`AVG/对话配置工作及草稿/前置配置/npc_knowledge_pools.yaml`

包含：
- 每个 NPC 的固定知识（knowledge_pool）和永久盲区（blind_spots）
- 按主题（topic）分类

### 6. NPC 人设

两个来源：
- `AVG/对话配置工作及草稿/前置配置/characters/{npc_name}.md` — 说话方式、核心性格
- `剧情设计/Unit2/人物设定/{npc_name}.md` — 背景故事、人物关系

### 7. 前序循环 State 文件（L2 及以后）

路径：`AVG/对话配置工作及草稿/前置配置/loop{N-1}_state.yaml`

必须读取上一循环的：
- `post_expose_knowledge` → 填入本循环的 `known_facts`
- 各 NPC 的 `withheld_topics` → 确认本循环哪些话题该释放
- 鉴赏力 `source` 条目 → 确认本循环是否需要配对的 `quiz`

如果是 L3+，还需要往前追溯更多循环的 `post_expose_knowledge` 以累积 `known_facts`。

### 8. 格式规则

路径：`AVG/对话配置工作及草稿/前置配置/STATE_FIELDS.md`

**必须在生成前读取**，确保字段结构、命名、注释格式完全一致。

### 9. 主角人设（参考）

路径：`剧情设计/00_世界观与角色/主角设计/`

- `Zack_Brennan.md` — Zack 的行为逻辑影响 `player_inquiry` 的提问方向
- `Emma_OMalley.md` — Emma 的 knows/does_not_know 逻辑

---

## 生成流程

### Phase 0：信息收集与理解

读取上述所有文件后，在心中建立以下认知模型：

1. **本循环的 Expose 需要哪些证据？** — 列出所有轮次所需的证据 ID
2. **这些证据分别在哪个场景获取？** — 对照证据设计和场景状态表
3. **哪些证据来自前序循环？** — 对照前序 state 文件的 evidence 段落
4. **本循环有哪些 NPC 出场？首次还是再次？** — 对照场景状态表 + NPC 出场历史
5. **本循环的核心叙事弧线是什么？** — 从剧情大纲理解"玩家从哪里来、到哪里去"

### 核心架构：三阶段分离

每个循环严格分为三个游戏阶段，必须作为**独立段落**书写：

| 阶段 | State 段落 | 性质 | 说明 |
|------|-----------|------|------|
| 开篇 | `opening` | 硬切（脚本） | 玩家观看剧情，无自由操作 |
| 自由探索 | `scenes` | 自由进出 | 玩家自行选择场景、收集证据、对话 NPC |
| 指证 | `expose` | 直接对决 | 选定目标后进入指证流程 |

**分离原则：**
- 同一场景可能跨阶段（如医院既是🎬开篇也是🔓自由探索），但在 state 文件中必须分开写：`opening` 段落 + `scenes` 段落
- 每个段落只描述对应阶段的内容，不混合
- 开篇 NPC 如在自由探索阶段也可对话，需在 `scenes` 中另设独立条目

### Phase 1：生成 player_context

```yaml
player_context:
  goals:
    primary: "..."    # 从剧情大纲该循环的核心目标
    secondary:        # 从剧情大纲的次要问题
      - "..."
  known_facts:        # = 前序所有循环的 post_expose_knowledge 累积
    - "..."
  new_directions:     # 本循环新开启的调查方向
    - direction: "..."
      trigger: "..."  # 具体触发信息
  post_expose_knowledge:  # 从指证设计的最终结果
    - "..."
```

**规则：**
- L1 的 `known_facts` 为 `[]`
- `post_expose_knowledge` 严格从指证设计的 `result` 段落提取
- `goals.primary` 必须是一个**问句**，代表玩家的核心困惑
- `new_directions` 的 `trigger` 必须是具体的信息事件，不能是抽象描述

### Phase 2：生成 opening

```yaml
opening:
  scene_id: XXXX     # 从场景状态表中标记为🎬的场景
  characters: [...]
  purpose: "..."      # 用一句话说清开篇的功能
  talk: emma_00X

  emma_00X:
    is_liar: false
    motive: "..."     # Emma 为什么在这里、要做什么
    mindset: "..."    # Emma 此刻的心理状态

    knows:            # Emma 在本循环开始时已知的信息
      - "..."
    does_not_know:    # Emma 明确不知道的关键信息
      - "..."
    lie: null

    connoisseur: []   # 或有 source/quiz
```

**规则：**
- `emma.knows` 包含：上一循环 Expose 的结论 + 本循环开篇之前发生的事件
- `emma.does_not_know` 包含：本循环将要发现的关键信息（这些是调查的目标）
- 如果开篇有其他 NPC（如 L5 的 Rose），也在 opening 下列出，使用标准 NPC 条目格式

**开篇阶段限制（硬切/脚本场景）：**
- 开篇是硬切场景，玩家无法自由选择——不存在主动提取证词或自由提问
- `testimony_ids`: **禁止**（证词提取在自由探索阶段完成）
- `player_inquiry`: **禁止**（玩家在开篇没有主动提问选择）
- 鉴赏力 `connoisseur`: **只允许 quiz**（不允许 source）——source 放到自由探索场景中
- 如果开篇 NPC 在自由探索阶段也可对话（如 Margaret 在医院），需在 `scenes` 中另设独立 NPC 条目

### Phase 3：生成 scenes

#### 3.1 确定场景列表

从场景状态表中提取本循环所有**非🎬非⚔️**的场景，包括：
- 🔓 自由探索（新解锁 + 已有场景新内容）
- ⏸️ 无新线索（只列 ID 和名称，不加 evidence/npcs）

#### 3.2 分配证据到场景

对照证据设计，将每个证据放入其 `发现位置` 对应的场景中：

```yaml
scenes:
  - id: XXXX
    name: "场景名称"
    evidence:
      - id: XXXX
        name: "证据名称"    # 必须与证据设计中的名称完全一致
        note: "设计备注"    # 标注关键/场景道具/对Expose的用途
```

**证据 note 标注规则：**
- `关键——{用途}` — Expose 直接使用的核心证据
- `场景道具` — 环境信息，不直接用于指证
- 不标注 — 普通证据

#### 3.3 分配 NPC 到场景

从场景状态表 + 剧情大纲确定哪些场景有 NPC 对话，然后按 Phase 4 的规则生成 NPC 条目。

### Phase 4：生成 NPC 条目（核心 — 最复杂的部分）

**每个 NPC 条目必须包含 4 个区块。生成前对照以下检查清单：**

#### 4.0 前置判断

| 判断项 | 依据 | 影响 |
|--------|------|------|
| 首次出场 or 再次出场？ | 场景状态表 + 前序 state | 决定知识结构用模式 A/B/C |
| 是否为本循环 Expose 对象？ | 指证设计 | is_liar=true, player_inquiry=null |
| 本循环的 goals.primary 与该 NPC 的知识池有什么交集？ | 知识池 + goals | 决定 player_inquiry 的方向 |

#### 4.1 基本信息

```yaml
npc_00X:
  talk: npc_00X
  is_liar: false/true
  motive: "..."     # NPC 参与这段对话的动机（不是性格描述，是"为什么现在要说话"）
  mindset: "..."    # NPC 此刻的心理状态
```

**motive 生成规则：**
- 必须回答"这个 NPC 为什么愿意（或被迫）跟 Zack 说话？"
- 参考 NPC 人设中的核心动机 + 当前循环的情境变化
- 首次见面：可能是被动的（被 Zack 找上门）
- 再次见面：通常有变化——信任度/局势/新信息触发

**mindset 生成规则：**
- 对比前序循环中该 NPC 的 mindset，体现**变化**
- 首次出场：从人设推导初始心理状态
- 再次出场：承接前序循环的结果（如被 Expose 拆穿 → 防守 or 示好 or 报复）

#### 4.2 区块 1：NPC 已知信息

**模式判断：**
- Emma → 模式 C（knows/does_not_know/lie:null）
- 一次性 NPC → 模式 D（knows/does_not_know）
- 首次出场的常规 NPC → 模式 A
- 再次出场的常规 NPC → 模式 B

**模式 A（首次出场）：**
```yaml
        # ── 1. NPC 已知信息 ──
        # 知识池见 npc_knowledge_pools.yaml → {npc_name}

        active_topics: [...]
        withheld_topics: [...]
```

**模式 B（再次出场）：**
```yaml
        # ── 1. NPC 已知信息 ──
        awareness:  # 以下为L{N}新获知信息，基础知识见 npc_knowledge_pools.yaml → {npc_name}
          - content: "新认知内容"
            trigger: "触发事件"
        active_topics: [...]
        withheld_topics: [...]
```

**active/withheld_topics 生成规则（最关键的信息节奏控制）：**

1. 从 `npc_knowledge_pools.yaml` 列出该 NPC 的所有 topic
2. 判断每个 topic 与**本循环 goals.primary** 的相关性：
   - 直接相关 → active（但注意透露度控制，见下方）
   - 与后续循环相关 → withheld
   - 与本循环无关但不会剧透 → 可选 active（作为背景/性格展示）
3. 检查前序循环的 `withheld_topics` 中是否有应在本循环释放的话题
4. 括号标注子集范围：`frank(基础背景)` vs `frank(完整含举报)`

**透露度控制原则——NPC 能说什么，不能说什么：**

| NPC 知道的 | 能说 | 不能说 |
|-----------|------|--------|
| 与 Expose 答案直接相关的**细节数字/结论** | ✗ | 这是玩家自己发现的 |
| 受害者视角的**感受和现象** | ✓ | — |
| 自己亲身经历的**具体事件** | ✓ | — |
| 对其他 NPC 的**印象和传闻** | ✓ | — |
| 本循环 Expose 的**最终结论** | ✗ | 这是 Expose 才揭示的 |
| 后续循环才揭示的信息 | ✗ | withheld_topics |
| blind_spots 中的信息 | ✗ | NPC 永远不知道 |

**示例——L3 O'Hara 的透露度控制：**
- O'Hara 知道"借200扣50管理费" → ✓ 可以说（自身经历的现象）
- O'Hara 知道"Frank在算超额收费" → ✓ 可以说（她观察到的事实）
- O'Hara 不知道"月利率12%=年化289%" → 自然不会说（blind_spot）
- O'Hara 不知道"空壳投资公司" → 自然不会说（blind_spot）
- 结果：玩家从 O'Hara 处得到"银行在多收钱"的方向，但具体数字需要自己去档案室找

#### 4.3 区块 2：玩家询问意图

```yaml
        # ── 2. 玩家询问意图 ──
        player_inquiry:
          - "驱动提问的信息来源"  # 分数(0-10)
```

**生成步骤：**

1. 列出本循环 `goals.primary` 和 `goals.secondary`
2. 对该 NPC 的 `active_topics` 逐一检查：与哪个 goal 相关？
3. 考虑**玩家此刻已知的信息**（known_facts + 本循环前面场景可能获得的信息）
4. 每条 inquiry 格式：`"{信息来源或驱动原因}"  # {分数}`
5. Expose 对象的 player_inquiry 设为 `null`

**分数评判标准：**
- 10: 核心悬念直接相关
- 8-9: 前序 Expose/证据直接指向
- 6-7: 有线索暗示但非核心
- 4-5: NPC 主动提及引发好奇
- 2-3: 无触发信息
- 0: 被动触发（Expose/鉴赏力中）

**核心检查：player_inquiry 是否服务于 goals.primary？**
- 如果某条 inquiry 与 goals.primary/secondary 完全无关，重新评估是否需要
- inquiry 不是"NPC 想说什么"，而是"**玩家想问什么**"

#### 4.4 区块 3：可提取证词

```yaml
        # ── 3. 可提取证词 ──
        testimony_ids:
          - {7位ID}  # 证词简述
          - {7位ID}  # ⚠谎言: 谎言证词简述
          - {7位ID}  # ⚠偏见: 偏见证词简述
```

**证词设计规则：**

**首次见面 NPC 必须包含的证词类型：**
1. **身份/职业证词** — 确认"这个人是谁"（例：Danny 是 Frank 唯一的侄子）
2. **时间线证词** — 案发当晚的行踪（例：Danny 11/6 晚在赌场到快九点）

**再次见面 NPC 的证词：**
- 基于本循环进展的**新信息**（不是重复上次的内容）
- 可能包含对其他 NPC/事件的新评价

**Expose 对象的证词（在 Talk 中收集，Expose 中使用）：**
- 至少一条将成为 Expose Round 1 的 `lie_source`
- 用 `⚠谎言:` 标注
- 谎言证词在 Talk 对话中应该听起来**合理**，不能一听就假

**证词 ID 格式：`{loop}{npc_code}{sequence}`**
- loop: 2位数字（如 20 = L2 of Unit2）
- npc_code: 2位数字（参照已有编码）
- sequence: 3位数字（001, 002, ...）

**偏见证词：**
- NPC 真诚地相信但客观上有误的陈述
- 用 `⚠偏见:` 标注
- 常见于有强烈情绪或立场的 NPC（如 Danny 对 Rose 的偏见）

#### 4.5 区块 4：鉴赏力

```yaml
        # ── 4. 鉴赏力 ──
        connoisseur:
          - type: source
            content: "信息内容"
            note: "L{X} {npc} quiz#{XXX} 考这个"
          - type: quiz
            node: "#{XXX}"
            question: "NPC 提出的问题"
            answer: "正确答案（来源：L{X} {场景/NPC} {证据/对话}）"
```

**鉴赏力设计规则：**

**Source（信息种子）：**
- 出现在本次对话中的一条信息
- 必须在后续某个循环/某个 NPC 的 quiz 中被考到
- `note` 明确标注配对的 quiz 编号和所在位置
- 信息可以来自：NPC 台词、场景道具描述、证据内容

**Quiz（考验）：**
- 由 NPC 自然地向 Zack 提出（NPC 考 Zack，不是 Zack 考 NPC）
- 必须有配对的 source 存在于前序循环或本循环其他场景
- `answer` 中必须标注来源

**Source ↔ Quiz 严格 1:1 配对**
- 每个 source 必须有且仅有一个 quiz
- 每个 quiz 必须有且仅有一个 source
- 不允许孤儿 source 或无 source 的 quiz

**叙事动机——NPC 为什么要考 Zack？**

| 场景 | 动机类型 | 示例 |
|------|---------|------|
| NPC 不信任 Zack | 验证 | "你说你检查了现场…那个烛台是什么做的？" |
| NPC 要冒险帮忙 | 确认值得冒险 | "Frank 到底调查了多少个受害者？" |
| NPC 在试探 Zack 知道多少 | 刺探 | "你去了银行？说说那个利率是多少？" |
| NPC 对某事很在意 | 个人原因 | Tony 的侄子也是受害者之一 |

**禁止：**
- 同 NPC 同循环自考自（source 和 quiz 不能出自同一个 NPC 的同一次对话）
- NPC 问自己刚说过的信息（信息距离不足）
- 为了考而考，无叙事理由

**每个 NPC 的 Talk 最多包含：**
- 2 条 source + 1 条 quiz（上限）
- 大多数 NPC 条目的 connoisseur 为 `[]`

**全循环鉴赏力预算：**
- 建议每循环 source + quiz 合计不超过 5 条
- 分布要合理，不集中在一个 NPC 身上

### Phase 5：生成 expose

```yaml
expose:
  target: "{NPC名} ({NPC_code})"
  total_rounds: N

  round_1:
    lie: "谎言内容"
    lie_source: "证词 {testimony_id}"
    usable_evidence:
      - id: XXXX
        name: "证据名称"
        用途: "如何反驳谎言"
    result: "结果描述"

  round_2:
    lie: "新谎言内容"
    lie_source: "NPC的新谎言（Round 1后退守）"
    usable_evidence: [...]
    result: "..."
```

**规则：**
- 直接从指证设计文档转录，保持一致
- `round_1.lie_source` 必须对应 NPC 条目 testimony_ids 中标注 `⚠谎言:` 的证词
- `usable_evidence` 中的每个证据 ID 必须出现在本文件的 scenes.evidence 中（或前序循环已获取）
- 如果指证设计中有特殊机制（如 L5 的 vinnie_false_confession），也要完整转录

**Expose 对象的 Talk/NPC 分离（重要）：**
- Expose 对象的完整 NPC 条目（4 个区块：已知信息、询问意图、证词、鉴赏力）写在 **`scenes`** 段落中对应场景下
- `expose` 段落**只包含**：`target`、`total_rounds`、各 `round_N`、以及一条注释指向 scenes 中的 NPC 条目
- 原因：证词收集（Talk）发生在自由探索阶段，指证（Expose）是独立的第三阶段
- 格式示例：
```yaml
expose:
  target: "NPC名 (code)"
  total_rounds: N
  # {NPC}的Talk/证词见上方 scenes → SC{XXXX} → {npc_00X}

  round_1:
    lie: "..."
    ...
```

### Phase 5.5：标注突发事件（如有）

如果场景状态表中本循环存在 ⚡突发 标记的场景，必须在 state 文件中添加 `events` 段落（放在 expose 之后、doubts 之前）：

```yaml
events:
  - type: sudden          # 突发事件（硬切，玩家不可控）
    scene_id: XXXX
    name: "事件名称"
    trigger: "触发条件"   # 什么时候触发（如"Expose结束后"、"opening结束后"）
    characters: [...]
    purpose: "事件功能"   # 对剧情推进的作用
    result: "事件结果"    # 事件结束后玩家获得什么（信息/证据/NPC 状态变化）
```

**规则：**
- 从场景状态表中识别所有 ⚡突发 场景
- `trigger` 必须明确标注触发时机，因为突发事件是硬切（玩家无法选择何时进入）
- 如果突发事件发生在 Expose 期间（如 L5 Mickey 打断 Vinnie 认罪），写在 expose 段落内部而非独立 events
- 如果突发事件独立于 Expose（如 L3 市政厅 Mickey 登场发生在开篇），写在 events 段落
- `result` 中标注事件对后续流程的影响（如获得新证据、NPC 解锁、场景状态变化）

**已知突发事件参考：**
- L3 市政厅：Mickey 登场，法院调取令被拒 → Mickey 以律师身份递交传票
- L5 码头：Mickey 救出 Margaret，Vinnie 喊出"Leo"

### Phase 6：生成 doubts

```yaml
doubts:
  - id: XXXX
    text: "疑点问题"
    unlock_condition: "item:XXXX + testimony:XXXXXXX"
```

**规则：**
- 每个 doubt 的解锁条件至少需要**两种不同来源**的信息（证词×物证、物证×物证、多方证词）
- doubt 的 text 应该是玩家在收集到部分信息后自然产生的疑问
- 从指证设计的"逻辑矛盾"段落推导

---

## 生成后自检清单

### A. 结构完整性

- [ ] 文件头注释包含：循环主题、说谎者、核心揭示、前序事件、时间
- [ ] player_context 五个字段齐全
- [ ] opening 包含 Emma 条目
- [ ] scenes 覆盖场景状态表中所有本循环可进入的场景
- [ ] expose 轮次与指证设计一致
- [ ] doubts 不为空

### B. 证据覆盖

- [ ] Expose 每轮 `usable_evidence` 中的证据 ID 都能在 scenes.evidence 中找到（或来自前序循环）
- [ ] 证据名称与证据设计文档**完全一致**
- [ ] 没有遗漏指证设计中提到的证据

### C. NPC 条目

- [ ] 每个 NPC 条目包含 4 个区块（已知信息 + 询问意图 + 证词 + 鉴赏力）
- [ ] 首次出场 NPC 有身份/职业证词 + 时间线证词
- [ ] Expose 对象 `is_liar: true`，`player_inquiry: null`
- [ ] Emma 使用 knows/does_not_know 格式，不使用 knowledge_pool

### D. 目标对齐

- [ ] 每个 NPC 的 `player_inquiry` 最高分项与 `goals.primary` 相关
- [ ] `active_topics` 展示的内容服务于玩家的调查方向
- [ ] NPC 不透露 Expose 的具体结论（数字、机制、身份），只提供方向性暗示

### E. 信息节奏

- [ ] `known_facts` = 前序所有循环的 `post_expose_knowledge` 累积
- [ ] `withheld_topics` 中的话题在后续循环有释放计划
- [ ] 前序循环 `withheld_topics` 中标注为本循环释放的话题已移入 `active_topics`
- [ ] 不同 NPC 之间无重复信息分配（同一条信息只有一个"信息所有者"）

### F. 鉴赏力

- [ ] source : quiz = 1:1 配对
- [ ] 0 个孤儿 source
- [ ] 每个 quiz 有叙事动机（NPC 为什么要问这个问题）
- [ ] 无同 NPC 同循环自考自
- [ ] quiz 答案来自游戏内信息，不考验现实知识
- [ ] `note` 标注清晰标明配对关系

### G. 指证

- [ ] round_1.lie_source 对应 testimony_ids 中的 `⚠谎言:` 条目
- [ ] 每轮 result 与指证设计文档一致
- [ ] 后续 round 的 lie_source 标注为"NPC的新谎言"

---

## 验证状态更新

完成自检清单后，在 state 文件末尾更新 `validation_status` 段落。对每个自检部分（A-G），根据检查结果记录 PASS 或 FAIL：

```yaml
validation_status:
  cross_check: "PENDING"               # 由 cross_check.py 自动更新，不要手动修改
  structure_completeness: "YYYY-MM-DD PASS"   # Section A
  evidence_coverage: "YYYY-MM-DD PASS"       # Section B
  npc_entries: "YYYY-MM-DD PASS"             # Section C
  goal_alignment: "YYYY-MM-DD PASS"          # Section D
  info_pacing: "YYYY-MM-DD PASS"             # Section E
  connoisseur: "YYYY-MM-DD PASS"             # Section F
  expose: "YYYY-MM-DD PASS"                  # Section G
```

值格式：`"PENDING"` / `"YYYY-MM-DD PASS"` / `"YYYY-MM-DD FAIL: N issues"`

如果某项检查发现问题，标记为 FAIL 并注明问题数量。日期使用当天日期。

---

## 输出

输出到：`AVG/对话配置工作及草稿/前置配置/loop{N}_state.yaml`

如果文件已存在，**先读取**现有文件，然后对比差异向用户确认后再覆盖。

---

## 附录：NPC 编码速查

| NPC | code | 首次出场 | 备注 |
|-----|------|---------|------|
| Foster | 02 | L1 | 一次性（emma_foster） |
| Morrison | 03 | L1 expose | L6 再次出场 |
| O'Hara | 09 | L2 | L3, L4 |
| Tony | 11 | L2 | L5, L6 |
| Vinnie | 05 | L2 | L5 expose |
| Moore | 06 | L2 | L3 expose, L6 |
| Leonard | 04 | L2 | L3, L4, L6 expose |
| Danny | 07 | L3 | L4 expose |
| Rose | 08 | L4 | L5 |
| Margaret | — | L6 | 特殊（医院） |

## 附录：Talk ID 命名规则

| 类型 | 格式 | 示例 |
|------|------|------|
| 首次对话 | `{npc}_{出场序号}` | `ohara_001`, `danny_001` |
| 再次对话 | `{npc}_{出场序号}` | `ohara_002`（L3再次）, `leonard_003`（L4） |
| Emma 开篇 | `emma_{循环序号}` | `emma_003`（L3开篇） |
| Expose | 不在 NPC 条目中设 talk，写在 expose 段落 | — |
