---
name: team-dialogue
description: "对白撰写 skill：两策划讨论 → dialogue-writer 执笔 → 审查 → 内容总监拍板。产出进游戏的对话 MD 草稿（非预览）。"
argument-hint: "[state 文件或目录路径]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# 对白撰写 Skill

本 skill 产出的对白 MD 经 `sync_to_json.py` 同步到 Unity 工程，是游戏**正式内容**，不是预览/测试稿。所以每一条对白的质量、格式、ID 都要达到出货标准。

## 适用场景

- state 文件已通过 `/team-loop` 或 `/unit-state-generator` 定稿
- 需要整 Loop 或整 Unit 的完整对话草稿（Talk + Expose + 🔵插入剧情）
- 只改单 NPC 或小改文案：用 `/team-design`，不用本 skill

## 输入约定

本 skill 由用户提供的路径驱动，不假设默认目录。

| 必需 | 说明 |
|------|------|
| state 路径 | 单个 `loop{N}_state.yaml` 或含多个 state 的目录 |
| 人物设计目录 | 含 `{npc}.md` 的目录，通常在 `剧情设计/Unit{N}/Characters/` |

**知识池**（`npc_knowledge_pools.yaml`）为可选——Unit8+ 采用 state 内嵌 `active_topics` / `withheld_topics` 格式，无需独立知识池。

**解析顺序**：
1. argument 直接给路径 → 按给的用
2. 仅给 state → 在 state 同级 / 上级找 `Characters/`
3. 都没找到 → 用 AskUserQuestion 问用户，**不假设默认路径**

---

## 核心硬规则（贯穿全流程）

以下规则在 Phase 2a / 2b / 4 / 5 的所有 agent prompt 中必须原样传递。违反者视为 FAIL。

### 规则 1：对白格式精简

- **单个句子 ≤ 35 个中文字**（含标点）
- 少旁白：**只在有真实动作发生时**才写旁白（`Morrison 推门而入`）
- **禁止**氛围填充旁白（如"舞台在唱歌，酒吧的气压和街面不一样"之类与剧情无关的渲染段）
- **禁止**Zack 的大段内心独白——短句触发，一句即可
- 每个场景 **1-3 个**核心信息点，超过视为超载

### 规则 1 附：纯画面/动作无台词节点不分配 ID

如果一段 MD 内容仅是环境描写、动作转场、NPC 无台词的表情反应，**不要给它独立的对话 ID 节点**——直接以 HTML 注释块 `<!-- ... -->` 嵌入到上下台词节点之间，或合并进相邻台词节点的动作括号 `[...]` 里。

**理由**：
- `sync_to_json.py` 按 ID 解析 JSON 条目，空台词节点会生成空气对白
- 占用 ID 空间，打乱后续编号
- 运行时期望"有 ID 就有台词（或 get/show/branches/end）"

**正确写法**（画面转场用注释，NPC 静默反应合并到相邻台词括号）：
```markdown
### 901001022
**扎克·布伦南** [推开门，视线扫过房间：Vivian 站在正中，手里握着一把小手枪，枪管朝下。Rosa 靠墙，双手绞在一起]
> 她手里有枪。

<!-- Morrison 的脚步声从走廊传来——他迟了半拍。走进门时帽檐压着，身上有酒气。 -->

### 901001023
**莫里森侦探** [掏出记事本]
> Webb 先生……死亡。
```

**错误写法**（无台词节点独占 ID）：
```markdown
### 901001022
**扎克·布伦南** [推开门，视线扫过房间]

### 901001023
**薇薇安·罗斯** [没有转身，枪在手里晃了一下]

### 901001024
**扎克·布伦南** [目光停在枪上]
> Vivian。
```

**例外**：如果节点承载机制（`get` / `show` / `branches` / `end`），即使没有 NPC 台词也必须保留 ID——ID 在这里标记机制触发点，不是台词条目。

### 规则 2：人物性格必须在对白中"可见"

不允许写"Jimmy 温吞地说"这种描述型处理。人物特征通过以下方式**落在台词/动作里**：

- **用词习惯**（称呼、自称、口头禅、俚语）
- **停顿节奏**（`……`、"慢半拍"、吞咽后开口）
- **动作细节**（看手、推眼镜、挪糖果、摸枪柄）
- **情绪颗粒**（不是"生气地说"，是"杯子轻微抖了一下"）

**硬性要求**：dialogue-writer 产出的每个 NPC 首句对白，必须能让读者在不看 `{npc}.md` 前提下也识别出这是谁。

### 规则 3：语言风格必读

`D:/NDC_project/参考资料/对白语言风格资料/` 下 6 份资料：

- `1920s美国俚语与黑话大全.md`
- `场合与语域切换.md`
- `性别与语言.md`
- `族裔与移民语言特征.md`
- `职业语言特征.md`
- `阶级与身份语言差异.md`

narrative-designer / puzzle-designer / dialogue-writer / dialogue-reviewer 都必读此目录。每个 NPC 的族裔 / 性别 / 职业 / 阶级特征必须在对白里有可识别痕迹（不必全部，至少 1-2 个维度立住）。

### 规则 4：state 细节不得压缩

**Unit9 教训**：写手接到高阶摘要后自行补细节，压缩掉了 state 里指定的关键场景节奏（如"酒保拒绝 Zack → Emma 用暗号救场"被压成一句话画面）。

- Phase 2a 讨论时必须逐段读 state 的 `description` / `opening.description` / `interlude.description` 原文
- Phase 2b writer prompt 必须**原文贴出** state 里指定的场景节奏，禁止复述/压缩
- 写手在 prompt 中明确："state 里写的每个戏剧节拍都要在对白里展开，不是一行画面带过"

### 规则 4 附：同场景多 NPC Talk 必须有场景连贯性

**Unit9 L1 教训**：Opening (scene 9004→9003) 结束时 Zack 已经进入 Webb 会客室，Vivian/Rosa/Morrison 三人都在场。但三个 Talk 由三个 writer 并行执笔，各自当"独立场景入口"处理——Vivian writer 写了"Zack 推开会客室的门"、Rosa writer 写了"我要说我看见的"（Opening 里她已喊过指控）、Morrison writer 写了"你是谁来着"（Opening 里已互认）。合并后三个 Talk 读起来像三次重新进场。

**根因**：writer 是并行 spawn 的，每个只看得到自己的 prompt，默认写成"第一次接触"。

**强制流程**：

1. **Phase 1 派发摘要**：lead 必须显式标出"同场景多 NPC"的共享关系。例如：
   ```
   §2/§3/§4 三个 Talk 共享 Scene 9003（Webb 会客室）：
   Opening 末 Zack 已进入房间，三人都在场
   Talk 之间是"Zack 挨个走向 NPC"的连续动线，不是独立场景入口
   ```

2. **Phase 2b writer prompt 必须包含**：
   - **场景连续性提示**（原样粘贴，不替换）：
     ```
     ⚠️ 场景连续性：本 Talk 发生在 Scene {id} 内部，接续 Opening（或上一个 Talk）。
     Zack 已通过 Opening 进入场景，本 NPC 在场景内站立等候。
     不要写 "Zack 推门进入" / "我是 Zack Brennan" 式的首次相遇开场——
     Zack 已在场，直接写"Zack 走向 {NPC}" 的动线衔接。
     Opening 中 NPC 已说过的话（如 Rosa 的当众指控、Morrison 的宣告）不得重复，
     本 Talk 的开场应是"Zack 过来核细节"或"Zack 正式做笔录"。
     ```
   - **兄弟 Talk 清单**：告诉 writer 同 scene 其他 NPC 写手正在写什么，避免各自开场
   - **Opening 锚点**：明确指出本 Talk 接 Opening 的哪个节拍末尾

3. **Phase 3 合并后 lead 做连贯性抽查**：读合并后的 §1→§2→§3→§4 首尾衔接，检查有没有"Zack 又推了一次门"/"NPC 又重新介绍自己"类重复。

4. **Phase 4 dialogue-reviewer 新增审查项**：跨 Talk 场景连贯性——同 scene 多个 Talk 是否共享一套"Zack 已在场"前提。

### 规则 5：ID 与文件名（产物进游戏，sync 能识别）

**Talk 对话 ID**：9 位 `9{npc=2}{conv_index=3}{seq=3}`

- 9 = Unit9 标识
- npc = NPC 编码（2 位）
- conv_index = NPC 在全 Unit 的第几次出场（3 位，001 起）
- seq = 该次对话内句子序号（3 位，001 起）

例：`901001001` = Unit9 / Emma(01) / 第 1 次对话 / 第 1 句

**Expose 对话 ID**：9 位 `9{npc=2}9{loop=2}{seq=3}`

- 9 = Unit 标识
- npc = 被指证对象（2 位）
- 9 = Expose 标记位（固定 9，与 Talk 区分）
- loop = Loop 编号（2 位）
- seq = 句子序号（3 位）

例：`903901001` = Rosa / Expose / Loop1 / 第 1 句
例：`907905001` = Jimmy / Expose / Loop5 / 第 1 句

**NPC 编码表**（Unit9 标准，其他 Unit 需各自定义）：

| 代码 | NPC | 代码 | NPC |
|------|-----|------|-----|
| 01 | Emma | 06 | Vivian |
| 02 | Zack | 07 | Jimmy |
| 03 | Rosa | 08 | Anna |
| 04 | Morrison | 09 | Whale |
| 05 | Tommy | | |

**JSON 目标文件名**（MD section 头显式写出，对应 `sync_to_json.py` 识别规则）：

- Talk：`{npc}_{conv_index}.json` → 例 `emma_001.json` / `rosa_001.json` / `jimmy_002.json`
- Expose：`Loop{N}_{npc}.json` → 例 `Loop1_rosa.json` / `Loop5_jimmy.json` / `Loop6_morrison.json`

**MD section 头格式**（sync 必须识别）：

```markdown
## §1. Opening — {描述}
## Talk: emma_001.json
## §2. Scene s{id} — {描述}
## Talk: rosa_001.json
## Talk: vivian_001.json
## §3. Expose — Rosa 指证
```

### 规则 6：本 skill 不做的事

- 不生成 Repeat 对话（`emma_001_repeat.json`）——另开 skill 处理
- 不跑 `sync_to_json.py`（Phase 2 用户手动触发）
- 不重写证据 / 指证 / state（冲突时让用户走上游流程）
- 不假设独立知识池存在（优先用 state 内嵌 topics）

---

## Pipeline

### Phase 0：前置读取（lead 自己做，不 spawn agent）

lead 读取以下文件，汇总成"上下文包"供后续 agent 使用：

- **state**（用户指定的文件或目录下全部 loop state）
- **Unit 大纲**（`剧情设计/Unit{N}/Unit{N}_大纲.md`）
- **人物设计**（`剧情设计/Unit{N}/Characters/` 下全部涉及 NPC 的 `{npc}.md`）
- **语言风格资料**（`参考资料/对白语言风格资料/` 全部 6 份）
- **对话规则**（`AVG/对话配置工作及草稿/AVG对话配置规则.md` + `.claude/rules/dialogue.md`）

若任一必需文件缺失，用 AskUserQuestion 停下来问。

### Phase 1：派发方案确认

读 state 后提取：
- 本 Loop/Unit 的 NPC 清单（Talk 场景）
- Expose 场景清单（对象 NPC、ExposeID、轮次数）
- 🔵 插入剧情清单（id、title、涉及 NPC、location）
- Opening 类型（cutscene / 过场对话）
- 平行场景隔离约束

输出派发摘要给用户确认：
- 计划并行的讨论单元（每 NPC + 每 Expose + 每 Interlude）
- 计划产出的 JSON 文件名清单（`emma_001.json`、`Loop1_rosa.json`、...）
- 对话 ID 段规划（哪些 NPC 占用哪些 ID 段）

AskUserQuestion：
- 方案 OK → 进入 Phase 2
- 调整分工 → 按用户意见改
- 取消

### Phase 2a：两策划并行讨论（每单元一对）

**讨论单元** = 每 NPC 一次 Talk 对话 + 每 Expose + 每 Interlude。每个单元并行 spawn 一对 narrative-designer + puzzle-designer。

**narrative-designer prompt 模板**：

```
你是叙事策划。任务：为 {Unit}/{Loop}/{NPC 或 Expose/Interlude ID} 这段对白产出"叙事要点方案"。
不要写完整对白，只写要点（每段目标、语气、关键台词风格、动作设计、情绪节拍）。

必读：
- state 对应段落（粘贴原文，不压缩）
- {npc}.md（人物设计）
- 参考资料/对白语言风格资料/ 全部 6 份

输出格式：
1. 每段（opening/branch1/branch2/汇合/...）的叙事目标
2. 人物声音设计（哪几个可识别特征必须在台词里落地）
3. 语言风格定位（族裔/阶级/职业/语域切换）
4. 情绪节拍推荐
5. 禁忌清单（哪些话不能说、哪些词不能用）
```

**puzzle-designer prompt 模板**：

```
你是推理策划。任务：为同一段对白产出"推理要点方案"。
不要写完整对白，只写要点（分支维度、信息点分布、证据获取时机、Expose 递进逻辑）。

必读：
- state 对应段落
- 跨 Loop 隔离约束（后续 Loop 信息在本 Loop 必须隐藏）
- AVG/对话配置工作及草稿/AVG对话配置规则.md

输出格式：
1. 分支设计（每个分支的信息维度）
2. 信息点分布（每场景 1-3 个，不超 3）
3. 证据/证词 get 时机建议（间隔 3-5 句）
4. Expose 轮次设计（每轮谎言对应什么维度证据）
5. 禁止破梗清单（本 Loop 必须隐藏什么）
```

两策划返回后，lead 自己做"讨论汇总"——把两份要点合并成"统一方案"，解决冲突时原则：

- **信息严密性 > 叙事质感 > 逻辑闭环**（三大原则优先级）
- 叙事风格和推理信息冲突时，以推理信息为准，让叙事策划找新表达
- 严重冲突无法调和 → 用 AskUserQuestion 把双方观点摆给用户选

### Phase 2b：dialogue-writer 按方案执笔

每个单元 spawn 一个 `dialogue-writer`，prompt 必须包含：

- Phase 2a 合并后的"统一方案"
- state 对应段落**原文**（不摘要）
- `{npc}.md` 路径
- `参考资料/对白语言风格资料/` 路径（必读）
- 核心硬规则 §规则1-5（原样粘贴到 prompt 里）
- 平行场景隔离清单
- ID 段 + 目标 JSON 文件名
- 产出路径：临时文件 `AVG/对话配置工作及草稿/{Unit}/.temp_{file_basename}.md`

多 writer 并发允许（不同 NPC 不同临时文件）。

### Phase 3：合并与格式化

lead 负责：

1. 按场景顺序把各临时文件拼入主文件 `AVG/对话配置工作及草稿/{Unit}/Loop{N}_生成草稿.md`
2. Section 头用标准格式（参见规则 5）
3. 场景分组头（人类可读）：`## §N. Scene {scene_id} — {描述}`
4. 🔵 插入剧情用分隔块包裹，嵌在最自然的 Talk 文件里（或独立 `## Talk: loop{N}_interlude_{id}.json`）
5. 清理 `.temp_*.md`
6. 全局 ID 唯一性校验
7. 把合并后的主文件路径呈现给用户

### Phase 4：并行审查

并发 spawn：
- `dialogue-reviewer` × 每 Loop 一份（12 项质量清单）
- `consistency-checker` × 1（跨 Loop 证据物理属性、NPC 陈述、ID 编码）
- `timeline-auditor` × 1（跨 Loop 信息泄露、证据时序、疑点解锁时序）

每审查员 prompt 必带：
- 草稿路径
- state 路径
- Unit 大纲路径
- 核心硬规则（审查清单包含规则 1-5 的所有条）

**player-simulator 不默认跑**——需要整 Unit 就绪后走 `/playthrough-audit`。

### Phase 5：内容总监拍板

spawn `content-director`，输入 3 份审查报告全文 + Phase 1 方案 + 用户原始要求。

输出：
- 综合评分表（每 Loop PASS / WARNING / FAIL）
- FAIL 必修清单（按优先级 P0 / P1）
- WARNING 建议改清单（P1 / P2）
- 架构决策问题（如需用户裁决）
- 质感质量定性评估
- 下一步行动建议

AskUserQuestion：
- 采纳全部 → 进入 Phase 6
- 采纳部分 → 用户指定
- 保持原稿 → 结束

### Phase 6：执行修改（可选）

按 NPC / 单元维度再 spawn `dialogue-writer`，只改涉及部分。改后可选再跑 Phase 4（用户决定）。

---

## 产出清单

| 文件 | 路径 | 说明 |
|------|------|------|
| 对话草稿 | `AVG/对话配置工作及草稿/{Unit}/Loop{N}_生成草稿.md` | 主产物，可直接喂 sync_to_json.py |
| 审查报告（可选） | `AVG/对话配置工作及草稿/{Unit}/Loop{N}_审查报告.md` | 用户要求才写 |

---

## 后续手动步骤（本 skill **不做**）

1. **sync 到 JSON**：`python sync_to_json.py {Unit}/Loop{N}_生成草稿.md`（Phase 2，用户触发）
2. **Repeat 对话生成**：另开 skill
3. **State → 配置表 JSON**：走 `/state-to-table`

---

## 禁止事项速查

- ❌ 自动运行 `sync_to_json.py`
- ❌ 写 Repeat 对话
- ❌ 压缩 state 里指定的戏剧节奏
- ❌ Zack 大段内心独白
- ❌ 单句超过 35 字
- ❌ 氛围填充旁白（和剧情无关的画面描写）
- ❌ 用"温吞地说/生气地说"描述代替台词/动作落地
- ❌ 给纯画面/动作描写（无台词、无 get/show/branches/end 机制）分配独立 ID 节点——用 `<!-- -->` 注释或合并到相邻台词的动作括号里
- ❌ 重写证据/指证/state（上游流程负责）
- ❌ 并行写同一主文件（用 `.temp_*` 隔离）
- ❌ 假设独立知识池存在（Unit8+ 用 state 内嵌）
