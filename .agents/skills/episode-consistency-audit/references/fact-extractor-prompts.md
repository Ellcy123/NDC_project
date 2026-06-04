# Fact Extractor Prompts

Phase 1 的 5 张事实表抽取提示词。主 orchestrator 启动 general-purpose Agent 时**直接复制对应章节作为 prompt**（替换其中的 `{Unit}` / `{EPI_NN}` 占位符）。

每个 agent 必须自行 Read 源文件，自行 Write 输出 JSON。**不要**让主 orchestrator 代读再传 context——浪费 token。

---

## §1 characters.json

**Prompt：**

```
任务：抽取 {Unit} 的人物档案事实表。

读取以下文件：
1. 剧情设计/{Unit}/Characters/*.md（每个 NPC 一个 MD，含弧光、立场、说话方式）
2. 剧情设计/{Unit}/state/loop*_state.yaml（NPC 段：active_topics / withheld_topics / blind_spots）
3. 剧情设计/{Unit}/{Unit}_大纲.md（NPC 关键事件）
4. 剧情设计/{Unit}/案发时间线与动线.md

为每个 NPC 输出以下结构（合并到一个 JSON 对象）：

{
  "<NPC 姓名>": {
    "age": <数字 | null>,
    "occupation": "<职业字符串>",
    "family": {"父亲": "...", "母亲": "...", "兄弟": "...", "妻子": "...", "孩子": "..."},
    "key_events": [
      {"loop": <数字>, "event": "<简述>", "stance_in_dialog": "truthful | deceptive | partial"}
    ],
    "items_owned": ["<物品名/ID>", ...],
    "relationships": {
      "<对方 NPC>": {
        "current": "<当前关系：情人/朋友/敌对/中立>",
        "history": [{"loop": <数字>, "change": "<变化描述>"}]
      }
    },
    "stance_per_event": {"<event_id>": "truthful | deceptive | partial"},
    "voice_register": "<声纹特征：克制/外放、市井/文雅、情感色彩、口头禅>",
    "blind_spots": ["<不知道的事 1>", ...]
  },
  ...
}

输出落盘：.audit/{Unit}/facts/characters.json

注意：
- 不"修复"档案中的矛盾——保留矛盾并在该字段加 _conflict 数组
- 不编造档案中没说的字段，不知道就 null
- voice_register 要从档案"说话方式"段精炼，≤30 字
- 每个 NPC 都要有条目，连临时配角也要列（除非该 NPC 在该 Unit 没有任何台词）
```

---

## §2 events.json

**Prompt：**

```
任务：抽取 {Unit} 的事件事实表（ground truth）。

读取以下文件：
1. 剧情设计/{Unit}/案发时间线与动线.md（核心来源）
2. 剧情设计/{Unit}/{Unit}_大纲.md（事件背景）
3. 剧情设计/{Unit}/state/loop*_state.yaml（事件细节、参与者）
4. 剧情设计/{Unit}/Characters/*.md（事件的多角度补充信息）

输出结构：

{
  "<event_id（如 E001_案发当晚）>": {
    "time": "<具体时间，含日期/时段>",
    "location": "<具体地点>",
    "participants": ["<NPC>", ...],
    "core_facts": [
      "<事实 1：必须是物理可观察的客观陈述>",
      "<事实 2>"
    ],
    "outcome": "<事件结果>",
    "physical_evidence": ["<证据 ID>", ...],
    "loop_revealed": <数字，本事件最早在哪个 Loop 完整揭示>,
    "before_loop_state": "<在该 Loop 之前玩家对该事件的认知>"
  },
  ...
}

事件 ID 命名：E + 三位数字 + _ + 简短中文名（如 E001_案发当晚 / E002_码头交易 / E003_失踪夜）。

输出落盘：.audit/{Unit}/facts/events.json

注意：
- core_facts 只放"客观可观察的物理事实"——天气、情绪、心理活动不算
- 同一事件被不同 NPC 描述时，以最权威来源（设计文档原文 > state > 角色档案）为准
- 设计文档中存在矛盾时，保留矛盾并加 _conflict
- 跨 Unit 引用的事件不抽（只抽本 Unit 内发生的）
```

---

## §3 items.json

**Prompt：**

```
任务：抽取 {Unit} 的物品/证据物理属性表。

读取以下文件：
1. 剧情设计/{Unit}/Unit{N}_证据美术需求分类.md
2. 剧情设计/{Unit}/state/loop*_state.yaml（evidence 段）
3. preview_new2/data/table/ItemStaticData.json（按 ID 索引的官方描述）
4. 剧情设计/{Unit}/{Unit}_大纲.md

输出结构：

{
  "<item_id（如 I0901_银烟盒）>": {
    "name": "<物品名>",
    "loop_first_appear": <数字>,
    "first_holder": "<最初持有者 NPC | null>",
    "physical": {
      "material": "<材质>",
      "color": "<颜色>",
      "size": "<尺寸>",
      "brand": "<品牌，如适用>",
      "marks": "<刻字/磨损/血迹等特征>",
      "count": <数量>
    },
    "current_location_per_loop": {
      "L1": "<位置或 NPC>",
      "L2": "...",
      ...
    },
    "narrative_role": "<叙事作用：直接证据/派生证据/合成证据/陷阱>",
    "referenced_in": "<在哪些场景/对话中出现的简要提示，不需要 line_id 全列>"
  },
  ...
}

输出落盘：.audit/{Unit}/facts/items.json

注意：
- 物理属性以 ItemStaticData.json 的 description 字段为最高权威
- 设计文档与 ItemStaticData 矛盾时，保留矛盾并加 _conflict
- 不抽通用道具（家具/路边树等无叙事作用之物）
- 派生证据要标注其来源 item ID
```

---

## §4 addressing.json

**Prompt：**

```
任务：抽取 {Unit} 内角色之间的称谓表与改口条件。

读取以下文件：
1. 剧情设计/{Unit}/Characters/*.md（关系段、对话样例）
2. 剧情设计/{Unit}/state/loop*_state.yaml（关系演变事件）
3. 剧情设计/{Unit}/{Unit}_大纲.md
4. （可选采样）AVG/EPI{NN}/Talk/loop*/*.json 用于校准已有称谓

输出结构（每对 speaker→target 一条）：

{
  "<speaker>-><target>": {
    "default_form": "<日常称谓，如 '汤米' / 'Mr. Salvatore' / '老吉米'>",
    "formal_form": "<正式场合形式，如全名+敬称>",
    "intimate_form": "<亲密形式，如昵称、爱称>",
    "third_party_form": "<向其他人提到 target 时的称呼>",
    "change_conditions": [
      {
        "loop": <数字>,
        "event": "<触发事件，如 '关系破裂' / 'L4 揭穿撒谎'>",
        "new_form": "<改口后的形式>",
        "reversible": <true/false>
      }
    ],
    "context_rules": "<场合规则简述，如 '玩家在场用 default_form，单独时可用 intimate_form'>"
  }
}

输出落盘：.audit/{Unit}/facts/addressing.json

注意：
- 只抽出现在该 Unit 中的角色对——不要全排列组合
- 自指（speaker = target）不抽
- 主角 Zack 也是有效 speaker / target——若 Zack 用了私人称谓变化要标
- 设计文档没明说的称谓变化不要编——保留 change_conditions 为空数组
- 玩家选项分支可能让某些改口条件依赖玩家选择——若是，在 event 字段标 "玩家选 X 时"
```

---

## §5 event_perspectives.json

**Prompt：**

```
任务：抽取 {Unit} 的"事件×视角"二维表——每个事件每个知情人各自的"真实知情"和"对外呈现"。

前置依赖：必须先读
1. .audit/{Unit}/facts/events.json（已抽出的事件列表）
2. .audit/{Unit}/facts/characters.json（已抽出的 NPC stance 字段）

补充阅读：
3. 剧情设计/{Unit}/Characters/*.md（NPC 各自的立场）
4. 剧情设计/{Unit}/state/loop*_state.yaml（active_topics / withheld_topics / blind_spots）
5. 剧情设计/{Unit}/案发时间线与动线.md

输出结构：

{
  "<event_id>": {
    "<NPC 名>": {
      "presence": "在场 | 门外 | 缺席 | 事后听说",
      "true_knowledge": "<该 NPC 真实知道的内容简述>",
      "presented_version": {
        "L1": "<L1 时该 NPC 对外讲的版本>",
        "L2": "...",
        ...
      },
      "stance": "truthful | deceptive | partial | evolving",
      "stance_evolution": "<若 evolving，描述跨 Loop 演变，如 'L1-L3:deceptive, L4+:truthful'>",
      "permitted_lies": ["<允许撒的谎 1>", ...],
      "withheld_in_loop": {"L1": ["不应透露的事 1"], "L2": ...}
    },
    ...
  }
}

输出落盘：.audit/{Unit}/facts/event_perspectives.json

注意：
- 只对 events.json 中存在的事件做映射
- 只对 characters.json 中存在的 NPC 做记录
- presence != "缺席" 的 NPC 才需要详细字段；"缺席"的 NPC 简化为 {presence: "缺席"}
- permitted_lies 要具体（如 "否认在场" / "声称当晚在别处" / "推说没看见枪"），不要泛泛
- stance 与 characters.json 中的 stance_per_event 字段必须一致——如果不一致保留矛盾并加 _conflict
- "事后听说"类 NPC 的 true_knowledge 是听说的版本，不是 ground truth——这个区分很重要
```

---

## 全局抽取约定

所有 5 个 fact-extractor 必须遵守：

1. **保留矛盾**：源文档中存在矛盾时，**不要**自作主张选一方为 ground truth——保留并标 `_conflict: ["<矛盾描述>", ...]`
2. **不要补全**：源文档没说的字段填 `null` / 空数组，不要根据"常识"或"剧情合理性"补
3. **逐 NPC / 逐事件枚举**：每个 NPC、每个事件、每对 speaker→target 都要有条目（即使是空记录）
4. **输出严格 JSON**：可被 `json.loads()` 解析；不要写 JS 注释、不要尾随逗号
5. **路径硬约定**：输出必须落 `.audit/{Unit}/facts/<对应文件名>.json`，目录不存在的话自行 mkdir
6. **token 不省**：本 phase 的输出会被后续 7 个审计 agent 反复读——抽得越完整后续越省

完成后向调用方简短回报：抽取完成，输出在哪、有多少条目、是否有 _conflict 标记。
