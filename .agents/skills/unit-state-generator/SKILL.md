---
name: unit-state-generator
description: "Use when generating, regenerating, or auditing a complete Unit State file set from an active outline registered in canon_manifest.json, especially when scene openings, event order, narrative handoffs, or Unity runtime mappings may drift from the outline."
---

# Unit State 文件生成流水线

从 `canon_manifest.json` 登记的 active outline 出发，经 agent team 讨论式协作，输出讨论结论、Manifest 声明数量的 Loop State 文件、风险点清单和时间线。

核心原则：先逐事件忠实转译大纲，再做系统设计。讨论结论只能解释或裁决大纲，
不能在未获用户批准时覆盖大纲、补写现实调度、改换事件顺序或移动玩家控制边界。

## Step 0：Canon 预检（必须）

开始讨论前先读取仓库根目录的 `canon_manifest.json`，按 `canonicalUnit` 找到目标章节，并锁定：

- `planningDirectory`：所有讨论结论、State、风险点和时间线的输出根目录。
- `sources.outline`：唯一允许作为本轮 State 输入的 active outline。
- `sources.statePattern`：已有 State 时使用的登记路径；`state.status=reserved` 时允许为 `null`，此时输出目录按 `{planningDirectory}/state/` 推导，State 真正生成后再更新 Manifest。
- `maturity.state.expectedLoops`：本章应生成的 Loop 数量，记为 `{L}`。
- `maturity.structure`：是否存在 non-Loop finale 等特殊结构。
- `idSpaces[]`：本章实际使用的 Episode 与 ID 命名空间；不得仅凭 Unit 号推导。

如果用户传入的大纲路径与 `sources.outline` 不一致，停止生成并显式报告 Canon 冲突；不能自行选择较新的文件。

Loop 范围始终是 `loop1` 至 `loop{L}`，不得默认补足到 6。若 `maturity.structure` 包含 non-Loop finale，该终幕写入最后一份 `loop{L}_state.yaml` 的 `ending_sequence`，不得虚构额外 Loop。

### 内容权威顺序

1. Manifest 指定的 active outline。
2. 用户明确批准、且可追溯到记录的变更。
3. 仅针对 active outline 歧义或 `[?]` 项的讨论裁决。
4. State。
5. 对白与配置表。

《讨论结论》是 active outline 的派生设计合同，不是独立 Canon。它只能整理明确
内容、裁决真实歧义、登记待确认事项。凡新增 NPC、地点、阻拦、互动门槛、事件、
事件改序、事件移动或玩家控制阶段变化，必须进入“偏差审批表”，经用户批准后才
能继续生成 State。

### Unity 运行时预检

生成前必须完整读取
[`references/unity-opening-runtime-contract.md`](references/unity-opening-runtime-contract.md)。
若 `D:\NDC` 可访问，再核对其 `AGENTS.md`、`res/xml/ChapterConfig.xml`、
`res/xml/SceneConfig.xml`、`res/xml/NPCLoopInfo.xml`、`res/xml/Talk.xml`
及相关运行时代码。Unity 只决定“怎么落地”，不能反向创造剧情。

若目标 Unit 已有 `state_contract.yaml` 或 validator，先检查它是否把大纲未批准
的临时方案锁成正式合同。合同与 active outline、用户批准记录或 Unity 当前行为
冲突时，停止 State 生成并报告上游合同冲突；不得为了让旧 validator 通过而保留
错误设计。

---

## 使用方法

将下方 Prompt 模板中的 `{变量}` 替换为实际值后，作为一条消息发给 Codex。

---

## Prompt 模板

```
用 agent team 模式来完成这个任务。你来规划需要几个 teammates、各自承担什么角色、如何分工。

要求（两种协作形态，分场景用，不要混成圆桌闲聊）：
- 【分工产出】各管一摊的工作（系统策划查 ID 冲突、推理策划设证据链、叙事策划设角色声音）——各 teammate 并行独立产出自己维度，互相看不见。
- 【盲产对比】遇到大纲里真有分歧/多解的关键决策（时间线矛盾裁决、Loop 映射、关键线索归属、疑点 condition 取舍）——指定两个 teammate 在【互相看不见对方答案】的前提下各自盲产一版完整处理方案，产出后再摆一起对比分歧。
- 严禁"同一角色先说 A、再扮另一角色反驳 A"式的自导自演辩论——分歧靠两份独立盲产方案的对比来暴露，不靠演双簧。
- 你作为 lead：分配工作、收齐盲产方案后做对比，把分歧点交内容总监裁决。
- 内容总监只能裁决 active outline 边界内的设计分歧；不能批准新增、删除、
  改序或控制权变化。
- 所有 teammates 完成后再给我最终结果；只有偏差审批表或 `[?]` 待定项非空时，
  先集中请求一次用户批准。

任务：
基于 `canon_manifest.json` 中 Unit{N} 的 active outline，生成 Unit{N} 的完整 state 文件体系。先完成 Canon 预检，并在讨论结论顶部记录实际使用的 `planningDirectory`、`sources.outline`、`expectedLoops` 和 `structure`。

内容事实权威顺序固定为：active outline → 用户明确批准的变更 → 仅针对大纲歧义的
讨论裁决 → State。讨论结论不得自行覆盖大纲。生成前完整读取
`.agents/skills/unit-state-generator/references/unity-opening-runtime-contract.md`，
并建立逐事件大纲覆盖矩阵、Opening 场景流和跨场连续性合同。

## 期望产出

| 文件 | 路径 | 说明 |
|------|------|------|
| 讨论结论 | `{planningDirectory}/讨论结论.md` | active outline 的派生设计合同，含覆盖矩阵、偏差审批表与运行时映射 |
| State × `{L}` | `{planningDirectory}/state/loop{1-L}_state.yaml` | 每个 Loop 的完整蓝图；实际逐个展开为 loop1 至 loop{L} |
| 风险点清单 | `{planningDirectory}/风险点清单.md` | P0/P1/P2 分级 |
| 时间线与动线 | `{planningDirectory}/案发时间线与动线.md` | 完整时间线 + 人物动线 |

## Team 角色建议（你可根据情况调整）

### Phase 1：讨论（→ 讨论结论.md）

| 角色 | agent 类型 | 职责 | 关注点 |
|------|-----------|------|--------|
| 叙事策划 | narrative-designer | 角色声音、时代质感、情绪节奏、场景构成 | 人物动机真实性、情绪弧连贯性、时代细节 |
| 推理策划 | puzzle-designer | 证据链、指证逻辑、线索分布、难度曲线 | 三大原则、谎言维度、正确证据闭环、推理路径唯一性 |
| 系统策划 | system-designer | 配置表、ID 编码、系统可行性、Unity 入口映射 | ID 冲突、非标准机制支持、ChapterConfig/SceneConfig/Talk 入口边界 |
| 内容总监 | content-director | 三大原则守护、分歧仲裁、跨 Loop 节奏 | 只裁决大纲边界内的设计分歧；无权批准偏差 |

### Phase 2：State 生成（→ `{L}` × state.yaml）

基于 active outline、已批准的讨论结论、逐事件覆盖矩阵、场景与控制权流、
叙事连续性链和 Unity runtime contract，由 state-architect 类型的 teammate
生成。可以按实际 `{L}` 个 Loop 分工，但每名生成者必须收到本 Unit 的完整覆盖
矩阵和前后 Loop handoff，不能只拿自己的局部摘要。生成后必须互相交叉验证，
特别检查大纲事件落点、Opening/自由探索边界、跨 Loop 证据 ID、known_facts
链式传递和 continuity handoff。如存在 non-Loop finale，由最后一轮负责人将其
写入 `ending_sequence`。

### Phase 3：收尾（→ 风险点 + 时间线）

你作为 lead 综合所有产出，生成风险点清单和时间线文档。

## 参考资料知识库（`参考资料/` 目录）

每个 agent 在讨论前**必须先读取**对应的参考资料。这些资料提供 1920s 芝加哥的历史准确性基础、叙事设计理论和语言风格规范。

### 按角色分配的必读资料

**叙事策划 必读：**
| 文件 | 用途 |
|------|------|
| `参考资料/对白语言风格资料/00_中文对白落地总则.md` | governing 文档，先读：中文载体、五条铁律、英文语域→中文转换原则。6 份史料当字典查，不直译 |
| `参考资料/对白语言风格资料/场合与语域切换.md` | 每个 NPC 在不同场景的语言调整基准（最全面，813行） |
| `参考资料/对白语言风格资料/族裔与移民语言特征.md` | 爱尔兰裔、意大利裔等角色的语言特征（如 Jimmy 的爱尔兰口音） |
| `参考资料/对白语言风格资料/职业语言特征.md` | 警察、律师、工人、厨师等职业的语言模式 |
| `参考资料/对白语言风格资料/阶级与身份语言差异.md` | 上层 NPC vs 下层工人的对白质感差异 |
| `参考资料/对白语言风格资料/性别与语言.md` | 1920s 性别规范、Flapper 女性、情感表达差异 |
| `参考资料/叙事结构参考/01_叙事结构理论.md` | 起承转合（Kishotenketsu）四段式结构 |
| `参考资料/叙事结构参考/04_角色驱动的悬疑节奏.md` | 情感真相先于事实真相、节制感设计 |

**推理策划 必读：**
| 文件 | 用途 |
|------|------|
| `docs/游戏系统/核心玩法/疑点系统.md` | **疑点/碎片两态生命周期、一对一挂载、时序硬约束**——疑点 condition 设计的机制级规则 |
| `docs/游戏系统/核心玩法/指证系统.md` | 指证 Expose 机制——与疑点联动的击穿逻辑 |
| `参考资料/04_1920年代法医学与刑侦技术.md` | 弹道学、验尸程序、技术能力边界——**证据设计的科学性约束** |
| `参考资料/02_1920年代指纹识别技术.md` | 指纹比对需 8-12 匹配点，不能"快速"确认 |
| `参考资料/06_1920年代毒物与化学物质.md` | 某些毒物在 1925 年根本无法追踪——谋杀手段参考 |
| `参考资料/叙事结构参考/03_证据链与线索布局理论.md` | **三线索法则**：每个关键结论需 3 条独立线索支撑 |
| `参考资料/叙事结构参考/02_红鲱鱼与假凶手设计.md` | 好红鲱鱼三要素：内在逻辑、推进情节、事后意义 |
| `参考资料/叙事结构参考/05_循环叙事设计.md` | **知识银河战士**模型：知识门控链设计框架 |

**系统策划 必读：**
| 文件 | 用途 |
|------|------|
| `参考资料/叙事结构参考/06_NDC项目具体应用.md` | **直接可用的 Loop 设计检查清单** |
| `参考资料/叙事结构参考/05_循环叙事设计.md` | 知识门控的系统支持需求 |

**内容总监 必读：**
| 文件 | 用途 |
|------|------|
| `docs/游戏系统/核心玩法/疑点系统.md` | **疑点一对一 + 时序硬约束**——内容总监审核时必须交叉验证 |
| `参考资料/叙事结构参考/06_NDC项目具体应用.md` | Unit 验证清单——用于最终审核 |
| `参考资料/叙事结构参考/01_叙事结构理论.md` | 起承转合框架——验证 Manifest 声明的 `{L}` 个 Loop 弧线完整性 |
| `参考资料/05_1920年代芝加哥警察系统与腐败.md` | 角色冲突根源、腐败机制——验证 Morrison 等角色设计 |

**所有角色 共读（世界观框架）：**
| 文件 | 用途 |
|------|------|
| `参考资料/00_资料总览与使用指南.md` | 资料库导航，571行完整指南 |
| `参考资料/03_禁酒令时期犯罪手法与黑帮活动.md` | 走私网络、黑帮组织结构——世界观框架 |
| `参考资料/05_1920年代芝加哥警察系统与腐败.md` | CPD 腐败规模、贿赂机制——角色动机与冲突根源 |
| `参考资料/01_1920年代著名悬疑案件.md` | 真实案件参考——案件设计的历史锚点 |

### 参考资料在讨论中的应用要求

1. **证据设计必须尊重技术边界**：1925 年的法医学和指纹技术有明确局限（见 02/04 文件），证据设计不能超越当时的检测能力
2. **角色语言必须匹配身份**：每个 NPC 的语言风格应按职业/阶级/族裔差异化（见对白语言风格资料），在 state 文件的 NPC mindset/motive 中体现
3. **犯罪手法必须合理**：黑帮运作方式、走私网络、腐败机制需符合禁酒令时期的真实模式（见 03/05 文件）
4. **红鲱鱼需通过三要素验证**：假凶手/假线索设计必须满足"内在逻辑+推进情节+事后意义"（见叙事结构参考 02）
5. **每个 Loop 通过检查清单验证**：使用 `叙事结构参考/06_NDC项目具体应用.md` 中的清单逐项检查

## Phase 1 前置产物：大纲忠实转译包

team 讨论前，lead 必须先把 active outline 转成以下四份可审计材料，并把原文
锚点传给所有 teammate。缺一项不得开始设计：

1. **逐事件大纲覆盖矩阵**

   | beat_id | source_anchor | 大纲原事件 | 人物/地点/顺序 | 计划落点 | mapping | deviation |
   |---|---|---|---|---|---|---|
   | U4-L3-O02 | Loop3/开篇/抵达宅邸 | Zack 与 Emma 在门口撞见 Mickey | 三人同场，先于探索 | opening.sequence[mansion_arrival] | exact | none |

   `mapping` 只允许 `exact / merged / deferred / omitted / added / reordered`。
   `merged` 必须证明没有丢失事件顺序和责任；`deferred` 必须指出合法后续落点；
   `omitted / added / reordered` 必须进入偏差审批表。

   active outline 在自由探索段落中显式标出的每一处 `👤 NPC：角色名` 都是
   `dialogue_required` 事件，必须按出现位置单独进入覆盖矩阵，并落到对应
   `scenes[].npcs.*.talk`。同名 NPC 在不同场景或事件阶段重复出现时按多条
   marker 计算，不能用另一场 Talk、Opening Talk 或 Event Talk 抵消。

   active outline 中每一处 `⚪` 都是 `testimony_required` 证言来源，不是普通
   `active_topics` 提示。逐条保存 `⚪` 证言块的正文，并在覆盖矩阵登记
   `testimony_id`、`source_text` 与对应获取位置的内联 `testimony_ids` 落点。
   若 `⚪` 后直接是完整证言句，`content` 必须逐字一致；若 `⚪` 是证言标题且
   下有明细 bullet，`content` 由该标题下的明细组成，不得添加大纲之外的事实。
   默认一处 `⚪` 对应一个证言语义单元；只有大纲明确说明“正式摘要、不新增另
   一套事实”或用户批准时才允许 `merged`。不得自行拆成多个 ID，也不得只留下
   ID、名称或概括。

2. **偏差审批表**：列出所有新增、删除、移动、改序、改变人物在场状态或玩家
   控制边界的计划。表为空才能自动继续；非空时集中向用户请求一次批准，不得让
   team 内部自行批准。
3. **场景与控制权流**：逐 Loop 标明强制 Opening、转场、玩家恢复控制、
   自由探索、Expose、post_expose 和 ending_sequence 的先后关系。
4. **叙事连续性链**：逐个关键单元记录进入状态、消费的前文压力、必须发生的
   剧情拍、退出状态和下一单元 handoff。

覆盖矩阵必须达到：漏项 0、无来源新增 0、重复映射 0，才允许进入 State 生成。

## 讨论必须覆盖的议题

Phase 1 的 team 讨论必须逐一讨论并达成结论：

1. **整体概述**：故事核心、新旧变更（如适用）、保留的设计
2. **权威时间线**：统一所有时间点，裁决大纲中的矛盾
3. **Loop 映射总表**：`{L}` 个 Loop 的标题、指证对象、情绪弧、节奏功能
4. **各 Loop 详细设计**（L1-L{L} 逐个讨论）：
   - 根级 Opening 场景流（一个根流程 + 一个或多个场景/事件 Talk + 玩家控制恢复点）
   - 场景列表（类型 + NPC + 内容）及 Opening / 自由探索职责边界
   - 关键证据及 ID 分配
   - **疑点 / 碎片设计**（ID + 观察式文本 + condition 两件 + Loop 归属）；若 active outline 明确批准某 Loop 使用独立门控玩法替代常规疑点，则改为完整记录该门控的输入、输出、完成条件与 Expose 解锁关系
     - 本 Loop 新增疑点清单
     - 本 Loop 新增碎片清单（独立 / 立即合并）
     - 跨 Loop 碎片的首现 Loop、合并 Loop、父疑点 ID
     - 进度条分母 = 本 Loop 新增疑点数 + 本 Loop 独立碎片数（合并到旧碎片的新碎片不计）
   - 指证设计（谎言层级 + 证据需求 + 击穿逻辑；每件指证证据都必须映射回某个疑点/碎片 ID，或 active outline 明确批准的独立门控链）
   - 本 Loop 揭示的真相层
   - 设计要点与风险
5. **关键设计问题与裁决**：大纲中的歧义、矛盾、[?] 标注逐一裁决
6. **原则二风险清单**：信息严密性检查
7. **遗留待确认事项**：需与策划核实的问题
8. **NPC 出场总表**
9. **场景复用参考**
10. **逐事件大纲覆盖矩阵与偏差审批结果**
11. **叙事连续性链与 Unity 运行时入口映射**

## 讨论结论.md 输出格式

```markdown
# Unit{N} 大纲讨论结论

> 讨论日期：{date}
> 参与者：内容总监、叙事策划、推理策划、系统策划
> 数据来源：`{sources.outline}`
> Canon：`planningDirectory={planningDirectory}` / `expectedLoops={L}` / `structure={structure}`
> 状态：定稿——可作为 state 文件生成的权威依据

---

## 一、整体变更概述
## 二、权威时间线
## 三、Loop 映射总表
## 四、各 Loop 详细设计
### Loop 1：{标题}
...
### Loop {L}：{标题}
## 五、关键设计问题与裁决
## 六、原则二风险清单
## 七、遗留待确认事项
## 八、NPC 出场总表
## 九、场景复用参考
## 十、逐事件大纲覆盖矩阵与偏差审批结果
## 十一、叙事连续性链与 Unity 运行时入口映射
```

## Team 讨论的关键约束

1. **证据 ID 全局分配**：先读取 Manifest 的 `idSpaces[]`，在讨论阶段锁定实际 Episode、ID 范围与各 Loop 分段，避免后续 state 各自为政。Unit 号不能替代 Manifest；例如 Unit1 同时存在策划 9xxx 与 Unity 1xxx 命名空间。
2. **跨 Loop 证据追踪**：明确标注每件跨 Loop 证据的完整流转路径
3. **每个 Loop 只揭示一层真相**：严格遵守原则一
4. **疑点一对一挂载**：每件证据/证言**只能**挂在唯一一个疑点或碎片的 condition 里。如果某件证据"好像哪个疑点都能挂"，必须在证言/物证层面拆成多条独立条目。设计时 team 内部交叉验证，一旦发现一证多挂立刻拆
5. **疑点时序硬约束**：疑点/碎片的出现 Loop ≤ 它 condition 里任何证据的**最早指证使用 Loop**。违例会导致玩家在指证 Loop 缺证据但无法回头——流程卡死。讨论阶段就要把每件指证证据和它所属疑点的 Loop 逐条比对
6. **疑点 condition 件数**：每个疑点 condition 优先 2 件（推荐双来源交叉）；1 件仅在"单件即可定案"的特殊情况用；严格禁止 3 件及以上——超过要拆成多个疑点
7. **裁决格式**：每个裁决包含 争议点 → 判断依据（引用三大原则/疑点系统规则）→ 裁决结果 → 下一步
8. **大纲 [?] 标注**：不擅自决定，收集到"遗留待确认事项"
9. **事实改写审批**：team 可以发现问题和提出候选方案，但不能批准
   `omitted / added / reordered`。偏差必须引用原文、说明影响并集中交用户批准。
10. **事件落点唯一**：每个 mandatory beat 只能有一个主落点；同一剧情拍不得
    同时挂在 Opening 和自由探索 NPC Talk。需要后续回响时另标 `callback`，不能
    复制事件本身。
11. **顺序与责任不压缩**：可以合并相邻描述，但不能把“拒绝后再指证”写成
    “指证后拒绝”，不能把强制到场声明移成玩家可跳过的询问，也不能用新增 NPC
    替原事件提供便利。

## State 文件生成规则

- 当前仓库没有独立 `STATE_FIELDS.md`；不得引用或等待一个不存在的 schema 文件。
- 结构权威：active outline + 用户批准记录 + 目标 Unit 已批准且未冲突的
  `state_contract.yaml` + 本 skill 的 Unity runtime contract。已有 State 只能作为
  工作样本，不能作为事实或结构权威；特别不得照搬 Unit3 中按人物嵌套 Opening
  的历史写法。可参考 Unit2 的场景级 Opening，但仍须按本节合同生成。
- player_context.known_facts = 前序 Loop 的 post_expose_knowledge 累积
- NPC 条目 4 必填区块：已知信息、玩家询问意图、可提取证词
- **显式 NPC 标记不得丢失**：active outline 自由探索段落中的每个
  `👤 NPC：` 必须生成对应场景的自由 NPC Talk。若同一角色在 Opening 后继续
  留场，Opening 只承担强制事件，恢复控制后仍须另有 `scenes[].npcs` Talk
  承担询问、证词或对话交付；两者内容不得重复。
- **对话取得必须双向绑定**：大纲写明“对话获取｜NPC”的证据，State 必须同时
  在证据 `acquisition.talk` 和 NPC `grants_evidence` 中登记，并指向同一个
  `scenes[].npcs.*.talk`。只把证据列在 scene 中视为漏配。
- **证言正文必须在获取位置内联**：NPC 普通 Talk 可取得的证言必须直接写在该
  NPC 的 `testimony_ids` 下，每项至少包含 `id / kind / content /
  acquisition_talk / source_anchor`。指证后取得的证言写在对应
  `expose.post_expose.testimony_ids` 下。禁止另建根级 `testimony_registry`，
  也禁止只写裸 ID。内联证言禁止自创 `name`；若后续配置需要玩家界面的短标题，
  使用 TestimonyItem 正式字段 `shortDesc`。`content` 是对白与 TestimonyItem
  摘要的事实真源；`active_topics` 只限定谈话范围，不能替代 `content`。
- **`⚪` 原文必须可追溯**：每条由大纲 `⚪` 产生的内联证言必须带
  `source_anchor`。完整句式的 `⚪` 必须逐字进入 `content`；标题式 `⚪` 则按
  其直属明细 bullet 形成 `content`。对白可以按角色声纹自然展开，但不能删除
  时间、地点、人数、身份、否定词、不确定性等限定，也不能膨胀出大纲没有的结论。
- **证言拆并规则**：默认 `一处 ⚪ → 一个 testimony_id`。同一 `⚪` 内多个
  相互依赖的分句仍是一条证言；若确需拆分，必须有大纲明确结构或用户批准记录。
  多处 `⚪` 合并到同一 ID 时，覆盖矩阵必须逐处登记并标记 `merged`，且只允许
  大纲明确声明“不新增另一套事实”的别名或正式摘要。
- **Expose 谎言分层**：R1 `lie_source` 必须先在普通 Talk 中取得，登记为
  `collectible_lie_anchor` 并以内联对象保留在 NPC `testimony_ids`；R2 及以后
  是指证现场才产生的退守谎言，正文直接写在对应 Expose 轮次的 `lie`，ID 只放
  `expose_lie_ids` 与对应轮次 `lie_source`，禁止混入 `testimony_ids` 让对白
  提前 `@get`。
- Expose 对象：is_liar: true, player_inquiry: null
- 每轮指证用不同维度的证据
- 不泄露后续 Loop 的信息
- **事实标签必须拆分**：同一 NPC 同时有真话和谎言时，不得用单一错误的
  `is_liar: false` 覆盖；每项 active topic 应标明 `truth_status` 或在 NPC 块中
  明确列出 `truthful_claims / false_claims / unknown_claims`。
- **执行顺序必须可读**：角色选择、拒绝、交付、离场、态度转弯等决定人物意义
  的动作必须落在正确的 pre-expose / opening / scene / post_expose 时段，不能只
  保留结果摘要。

### Opening 合同

每个 Loop 只有一个根级 `opening`。其中 `sequence[]` 可以包含一个或多个
场景级/事件级 Talk；地点、时间或独立事件切点可以拆分，说话人变化本身不能拆分：

```yaml
opening:
  type: cutscene_sequence
  runtime_root:
    table: ChapterConfig
    init_scene: 4021
    init_talk: L3_opening_broken_call
  sequence:
    - event_id: broken_call
      source_anchor: "active outline / Loop3 / 开篇来电"
      talk: L3_opening_broken_call
      scene_id: 4021
      location: "Zack 侦探事务所"
      cast: [Zack, Emma, Harold]
      required_beats:
        - "人工接线员转入 Harold 的电话"
        - "Harold 只说出 Brennan 后断线"
        - "Zack 与 Emma 立即前往宅邸"
      runtime_exit:
        action: change_scene
        target_scene_id: 4022
        continuation: next_talk
        next_talk: L3_opening_mansion_arrival
    - event_id: mansion_arrival
      source_anchor: "active outline / Loop3 / 抵达宅邸"
      talk: L3_opening_mansion_arrival
      scene_id: 4022
      location: "Morrison 宅邸门口"
      cast: [Zack, Emma, Mickey]
      required_beats:
        - "Zack 与 Emma 在门口撞见 Mickey"
        - "Mickey 强制声称自己也刚到"
      runtime_exit:
        action: release_to_exploration
  player_control_restored_after: mansion_arrival
```

Opening 约束：

- `sequence[].talk` 按场景或事件命名，如 `L3_opening_broken_call`；禁止
  `L3_opening_emma` 等按人物命名。
- `cast` 表示强制演出出场者，不等于可点击 NPC。
- `scenes[].npcs` 只登记玩家恢复控制后主动点击的 NPC Talk。
- Opening 的 `cast` 不能满足自由探索段落的 `👤 NPC` marker；同一角色先参与
  Opening、后作为自由 NPC 时必须分别映射，且信息职责不重复。
- 同一人物可以在两处出现，但必须有不同职责和内容，不能复制问句、进场动作或
  同一事实交代。
- `player_control_restored_after` 必须指向最后一个强制段；此前不得进入普通
  Talk 分支。
- 跨场强制续接默认使用 `change_scene + next_talk`。不得让目标场景的
  `firstEnterTalk` 同时承载同一剧情拍。
- 运行时细节以
  `references/unity-opening-runtime-contract.md` 为准。

### 叙事连续性合同

新增顶层设计字段 `narrative_continuity`。它不进入 Unity 正式表：

```yaml
narrative_continuity:
  units:
    - id: L2_harold_followup
      source_anchor: "active outline / Loop2 / 散庭后"
      entry_state:
        - "Whitfield 已被击穿"
      consumes:
        - "Harold 仍未公开 Harrison 材料"
      required_callbacks:
        - "Harold 要求 Zack 今晚守着事务所电话"
      required_beats:
        - "Emma 要求私下谈话必须包括自己"
      exit_state:
        facts:
          - "Harold 准备再次联系 Zack"
        relationship_changes:
          - "Harold 首次把 Zack 与 Pierce 区分开"
        unresolved_pressure:
          - "密封材料尚未交出"
      hands_off_to: L3_opening
```

每个 Opening、关键 Talk、Expose、post_expose 和 ending_sequence 至少对应一个
continuity unit。相邻单元必须形成 `hands_off_to` 链；每个单元都要说明消费了
什么既有压力、产生了什么状态变化、把什么交给下一场。

如果目标 Unit 的 `state_contract.yaml` 尚未允许
`outline_coverage`、`opening.runtime_root`、
`opening.sequence[].source_anchor`、`opening.sequence[].required_beats`、
`narrative_continuity` 等设计期字段，先报告合同升级需求，
不得静默省略，也不得未经批准直接改合同或 validator。
- **独立门控例外**：只有 active outline 明确写明“该 Loop 可不配置常规疑点”时，才能省略该 Loop 的 DoubtConfig。State 必须新增 `special_mechanics` 设计区块，逐条登记门控链输入材料、产出结论、完成条件、失败反馈待定项和 Expose 解锁条件；所有指证材料仍必须能反查到某条门控链，不能成为游离证据。
- **独立门控字段模板**：

  ```yaml
  special_mechanics:
    identity_lock:
      status: provisional
      replaces_standard_doubts: true
      open_questions:
        - ui_layout
        - submission_method
        - failure_feedback
      chains:
        - id: chain_1
          name: "证明链名称"
          inputs:
            - {type: item, id: 4501, name: "正式证据名"}
          output:
            type: derived_conclusion
            id: 4571
            name: "派生结论名"
          proof_boundary: "本链能证明什么、不能证明什么"
      completion_condition: all_chains_completed
      unlocks: expose
  ```

  `status: provisional` 表示交互表现仍可讨论，不表示输入、输出和剧情结论可以由 State 生成者自行改写。
- **DoubtConfig 规则**：
  - 每条目必填 `isFragment`（`false` 为疑点 / `true` 为碎片）
  - 疑点 condition 优先 2 件，允许 1 件；禁止 ≥ 3 件
  - 碎片 condition 必须单件
  - 跨 Loop 碎片：condition 里引用的证据 ID 必须来自首现 Loop；父疑点的 condition 是所有子碎片 condition 的并集（子集匹配触发合并）
  - 疑点/碎片文本采用**观察式提问**（如"这些照片上的人似乎在哪里见过一样？"），避免结论式（如"酒吧在做勒索"）
- 生成完成后执行 A-J 十段自检：
  - A 结构完整性：player_context / opening / scenes / expose / doubts 或获批 special_mechanics / evidence_registry 齐全
  - B 证据覆盖：大纲正式证据均有获取位置、流转与用途
  - C NPC 完整性：已知信息、玩家询问意图、可提取证词等必填区块齐全
    ；active outline 每一处 `👤 NPC` marker 均有同场自由 Talk，重复出场按
    出现次数逐一覆盖；对话取得证据与 Talk 双向绑定；每一处 `⚪` 均有
    `testimony_required` 覆盖行和唯一内联 ID 落点；所有普通
    `testimony_ids` 均有非空 `content`，所有 R2+ `lie_source` 均有同轮 `lie`
  - D 目标对齐：本轮 primary goal、核心揭示与大纲一致
  - E 信息节奏：后续 Loop 信息与 NPC 未知事实没有提前泄露
  - F 特殊结构：独立门控与 `ending_sequence` 等非标准结构完整、边界清楚
  - G Expose 逻辑：每轮谎言、材料、击穿维度与前置门控闭环
  - H 大纲覆盖：逐事件覆盖矩阵漏项 0、无来源新增 0、重复映射 0；所有偏差有用户批准记录
  - I Opening：一个根流程、场景/事件命名、强制段顺序正确、玩家控制恢复点明确、未与自由 NPC Talk 重复
  - J 连续性与运行时：continuity handoff 无断链；`initTalk / change_scene + next / firstEnterTalk / NPC TalkInfo` 职责无冲突
- 若本章存在 non-Loop finale：最后一份 State 必须含 `ending_sequence`，其中只写终幕事件，不把它登记为新的 Loop。

## 跨 Loop 一致性校验清单（Phase 2 完成后）

### 基础一致性
- [ ] 证据 ID 无冲突（实际 `{L}` 个文件间不重复）
- [ ] known_facts 链式传递正确
- [ ] 跨 Loop 证据流转一致
- [ ] NPC 知识边界在其认知范围内自洽
- [ ] active outline 自由探索中的每一处 `👤 NPC` 均落到同场
  `scenes[].npcs.*.talk`；同名多次出现未被错误合并
- [ ] 所有“对话获取”证据的 `acquisition.talk` 与 NPC
  `grants_evidence` 双向一致
- [ ] active outline 每一处 `⚪` 均进入覆盖矩阵，`source_text` 与原文逐字一致
- [ ] 所有普通 `testimony_ids` 都是 `id + content` 内联对象，不存在裸 ID，
  不含冗余 `name`，根级不存在 `testimony_registry`
- [ ] R1 `lie_source` 能反查普通 Talk 的内联证言；R2+ `lie_source` 在对应
  Expose 轮次有非空 `lie`
- [ ] `active_topics` 没有被当作证言正文替代品
- [ ] 一处 `⚪` 未被无批准拆成多个 ID；多处合并时有大纲明确说明并标记
  `merged`
- [ ] R1 谎言锚在普通 Talk 可取得；R2+ 动态退守只在 `expose_lie_ids`，
  未混入 NPC `testimony_ids`
- [ ] 指证证据在对应 Loop 的 scenes 中可获取
- [ ] 疑点解锁条件中引用的 ID 存在
- [ ] 使用独立门控替代疑点的 Loop 已在 `special_mechanics` 中覆盖全部指证材料，并明确完成门控后才解锁 Expose
- [ ] 每个 Loop 只有一个根级 `opening`，所有强制段均在 `opening.sequence[]`
- [ ] Opening Talk 以场景/事件命名，不以人物命名
- [ ] `player_control_restored_after` 指向最后一个强制段
- [ ] 同一剧情拍未同时出现在 Opening 与 `scenes[].npcs`
- [ ] `narrative_continuity.units[].hands_off_to` 目标存在且全链无断点
- [ ] 每个大纲 mandatory beat 有唯一 State 落点，所有新增/省略/改序均有用户批准
- [ ] Unity 映射遵守一个 `ChapterConfig.initTalk` 根入口；跨场续接未与目标 `firstEnterTalk` 重复

### 疑点系统专项（对照 `docs/游戏系统/核心玩法/疑点系统.md`）
- 以下项目只检查使用常规疑点的 Loop；active outline 明确批准的独立门控 Loop 改查 `special_mechanics` 材料覆盖与解锁关系。
- [ ] **一对一挂载**：跨实际 `{L}` 个 state 文件扫描所有 DoubtConfig.condition，同一证据/证言 ID **只能**在一处被引用——发现多处立即拆
- [ ] **时序硬约束**：对每件在指证 ExposeData 里被使用的证据，定位它所属的疑点/碎片——该疑点/碎片的 Loop ≤ 该证据最早指证的 Loop
- [ ] **condition 件数**：疑点 1–2 件，碎片严格 1 件，禁止 ≥ 3 件
- [ ] **进度条分母**：每个 Loop 新增疑点 + 新增独立碎片（合并到旧碎片的新碎片不计）；总表与各 Loop 分母对得上
- [ ] **碎片合并正确性**：父疑点 condition 是子碎片 condition 并集；合并 Loop ≥ 所有子碎片首现 Loop
- [ ] **疑点文本为观察式**：每条疑点/碎片文本是玩家视角的提问，不是结论式复述

## 全程自主

- 日常分析、ID 分配和无争议结构不要逐步询问；team 内部完成后统一交付
- 大纲中明确标注 `[?]` 的待确认项，以及任何 `omitted / added / reordered`
  偏差，集中成一次审批请求；未获批准不得写入 State
- 讨论结论必须逐条追溯到 active outline 或用户批准记录，不能成为覆盖大纲的独立权威
- 发现现有讨论结论、state_contract、validator 或历史 State 与 active outline
  冲突时，先报告上游缺陷，不能为了复用旧产物继续生成
- 除必须先批准的偏差/待定项外，所有产出完成后一次性交付给我
```

---

## 变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `{N}` | Unit 编号 | 1 |
| `{planningDirectory}` | 从 Manifest 读取的当前策划目录 | `剧情设计/Unit4` |
| `{sources.outline}` | 从 Manifest 读取的 active outline | `剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md` |
| `{L}` | 从 `maturity.state.expectedLoops` 读取的 Loop 数 | `5` |
| `{structure}` | 从 `maturity.structure` 读取的章节结构 | `5_loops_plus_non_loop_finale` |
| `{date}` | 讨论日期 | 2026-04-15 |

---

## 使用示例

```
用 agent team 模式来完成这个任务。你来规划需要几个 teammates、各自承担什么角色、如何分工。

要求（两种协作形态，分场景用，不要混成圆桌闲聊）：
- 【分工产出】各管一摊的工作（系统查 ID、推理设证据链、叙事设声音）——各 teammate 并行独立产出自己维度，互相看不见。
- 【盲产对比】遇到真有分歧/多解的关键决策——两个 teammate 互相看不见各盲产一版完整方案，再对比分歧。
- 严禁同一角色自导自演式辩论；分歧靠两份独立盲产方案对比暴露。
- 你作为 lead：分配工作、收齐盲产方案做对比、把分歧交内容总监裁决。
- 所有 teammates 完成后再给我最终结果

任务：
读取 `canon_manifest.json`，基于 Unit1 的 active outline 生成完整 state 文件体系。Loop 数量、输出目录和特殊终幕结构全部以 Manifest 为准。

[此处粘贴上方"期望产出"到"全程自主"之间的全部内容]
```

---

## 与其他 Skill 的关系

| 阶段 | 后续可用 Skill |
|------|---------------|
| State 文件完成后 | `/team-expose` — 基于 state 设计完整指证 |
| 指证完成后 | `/team-loop` — 生成对话草稿 |
| 全部完成后 | `/playthrough-audit` — AI 模拟玩家走完整个 Unit |
