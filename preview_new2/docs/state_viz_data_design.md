# State Visualizer 数据架构设计文档

> 服务于 `state_visualizer.html`，将 state YAML 文件转换为可视化图表。
> 读取路径：`剧情设计/Unit{1,2,3}/state/loop{1-6}_state.yaml`

---

## 1. YAML 结构分析与差异汇总

### 1.1 三个 Unit 的结构差异

在设计统一数据模型之前，需要明确各 Unit state 文件的实际差异：

| 字段/特性 | Unit1 | Unit2 | Unit3 |
|-----------|-------|-------|-------|
| `player_context.goals` | primary + secondary | primary + secondary | chapter_goal + primary + secondary |
| `opening.characters` | 直接列表 | 直接列表 | 直接列表 |
| NPC `connoisseur` 字段 | 总是空数组 `[]` | 有 source/quiz 节点 | 有 source/quiz 节点，含 trigger_mode |
| NPC `awareness` 字段 | 不存在 | 存在（L3+） | 存在 |
| `sudden_event` 字段 | 不存在 | 存在（如 L3 Mickey 登场） | 不存在 |
| `events` 字段（过渡事件） | 不存在 | 不存在 | 存在 |
| 场景证据 `analyzed_id` | 存在 | 存在（以 `2701` 等派生 ID 形式） | 用「派生证据说明」章节描述 |
| expose 字段 `trap_evidence` | 不存在 | 不存在 | 存在 |
| expose 字段 `auto_followup_evidence` | 不存在 | 不存在 | 存在（Unit3 L5 R2 双阶段） |
| `doubts.clear` 字段 | 存在（布尔） | 不存在 | 不存在 |

### 1.2 共同结构骨架

所有 Unit 的 state 文件都包含以下顶层键：

```
player_context    → 玩家视角（本循环目标、已知事实、新方向）
opening           → 开篇场景 + 开篇 NPC 状态
scenes[]          → 自由探索场景列表（每场景可含证据和 NPC）
expose            → 指证设计（target + total_rounds + round_N）
doubts[]          → 本循环疑点列表
validation_status → 校验状态（供策划内部使用，可视化忽略）
```

Unit3 额外包含：
```
events[]          → 过渡事件（closing 类型，指证结束后）
derived_evidence  → 派生证据说明章节（YAML 注释，非结构化数据）
```

---

## 2. JS 标准化数据模型

以下是将 YAML 解析为 JS 对象后的目标数据结构，使用 TypeScript 接口风格描述。
**抹平 Unit 差异是这个模型的核心职责。**

### 2.1 顶层容器

```typescript
interface StateData {
  // 元信息（从文件名和文件头注释解析）
  meta: LoopMeta;

  // 玩家视角
  playerContext: PlayerContext;

  // 开篇场景
  opening: OpeningScene;

  // 自由探索场景（含证据和 NPC）
  scenes: Scene[];

  // 指证设计
  expose: ExposeDesign;

  // 疑点列表
  doubts: Doubt[];

  // 特殊事件（突发事件 + 过渡事件，合并处理）
  specialEvents: SpecialEvent[];

  // 派生证据映射（从 analyzed_id 和「派生证据说明」章节提取）
  derivedEvidenceMap: DerivedEvidenceMap;
}
```

### 2.2 元信息

```typescript
interface LoopMeta {
  unit: 1 | 2 | 3;           // 从文件路径解析
  loop: 1 | 2 | 3 | 4 | 5 | 6; // 从文件路径解析
  title: string;               // YAML 第 2 行注释，如"目击者的沉默"
  liar: string;                // "本循环说谎者:" 后的值，如 "Rosa"
  coreReveal: string;          // "核心揭示:" 后的值
  precedingEvents: string;     // "前序事件:" 后的值
  timeLabel: string;           // "时间:" 后的值，如 "1925年11月7日 约14:00"
}

// 解析规则：读取 YAML 头部注释（# 开头的行），按行匹配关键词提取
// Unit1 注释在 # ============= 块内，Unit2/3 相同格式，可统一正则匹配
```

### 2.3 玩家视角

```typescript
interface PlayerContext {
  chapterGoal: string | null;  // Unit3 才有，Unit1/2 补 null
  goals: {
    primary: string;
    secondary: string[];
  };
  knownFacts: string[];        // known_facts 数组，L1 可能为空
  newDirections: NewDirection[]; // 本循环新发现的调查方向
  postExposeKnowledge: string[]; // 指证后玩家获得的结论
}

interface NewDirection {
  direction: string;   // 方向名称，如 "贷款申请笔迹造假"
  trigger: string;     // 触发条件文字说明
}
```

### 2.4 开篇场景

```typescript
interface OpeningScene {
  sceneId: number;              // opening.scene_id
  characters: string[];         // opening.characters
  purpose: string;              // 开篇目的说明
  talkRef: string | number;     // opening.talk（字符串 key 或数字 ID）

  // 开篇 NPC（可能有多个，如 Unit3 L5 同时有 emma 和 mickey）
  npcs: OpeningNpc[];

  // 突发事件（Unit2 L3 的 Mickey 登场等）
  suddenEvent: SuddenEvent | null;
}

interface OpeningNpc {
  key: string;           // YAML 中的 key，如 "emma_003", "mickey_001"
  isLiar: boolean;
  motive: string;
  mindset: string;
  knows: string[];
  doesNotKnow: string[];
  lie: NpcLie | null;
  connoisseur: ConnoisseurNode[]; // Unit1 始终为 []
}

interface SuddenEvent {
  name: string;
  trigger: string;
  characters: string[];
  purpose: string;
  result: string;
}
```

### 2.5 场景

```typescript
interface Scene {
  id: number;
  name: string;
  note: string | null;

  // 场景状态标记（从 note 和 YAML 注释中解析）
  sceneType: SceneType;

  // 证据列表
  evidence: EvidenceItem[];

  // NPC 列表（一个场景可能有多个 NPC，但通常只有一个）
  npcs: SceneNpc[];

  // 场景级鉴赏力节点（Unit2 Leonard办公室 的 connoisseur 挂在场景而非 NPC 上）
  connoisseur: ConnoisseurNode[];
}

type SceneType =
  | 'opening'      // 🎬 开篇场景
  | 'explore'      // 🔓 可探索（有新证据或 NPC）
  | 'locked'       // 🔒 本循环锁定
  | 'idle'         // ⏸️ 本循环无新线索
  | 'expose'       // ⚔️ 指证场所
  | 'event'        // ⚡ 突发事件触发点
  | 'ending';      // 🎭 结尾场景

// SceneType 解析规则：
// 1. 优先读取 YAML 注释中的 emoji 标记（🔓🔒⏸️⚔️⚡🎭🎬）
// 2. 若没有 emoji，根据字段存在性推断：
//    - evidence 非空 → explore
//    - npcs 非空且 npc.isLiar → expose（如果场景 ID 与 expose.target 一致）
//    - evidence 为空、npcs 为空 → idle
```

### 2.6 证据条目

```typescript
interface EvidenceItem {
  id: number;
  name: string;
  note: string;         // 原始 note 字段

  // 从 note 字段解析的结构化信息
  category: EvidenceCategory;
  usage: string | null;         // note 中 "关键——" 后的用途说明
  analyzedId: number | null;    // analyzed_id 字段（原始证据）

  // 从 expose rounds 反向关联（解析阶段填充）
  usedInExposeRounds: number[]; // 被哪几轮 expose 引用
  isTrap: boolean;              // 是否出现在 trap_evidence 中
  isDerived: boolean;           // ID 为 x7xx 格式 → 派生证据
}

type EvidenceCategory =
  | 'key'         // note 以 "关键" 开头
  | 'narrative'   // note 为 "环境叙事"
  | 'prop'        // note 为 "场景道具"
  | 'derived'     // 派生证据（analyzed_id 指向的目标）
  | 'trap';       // 出现在 expose.round_N.trap_evidence 中

// note 解析规则：
// "关键——{用途}" → category: 'key', usage: {用途}
// "关键——raw状态，分析后变为{ID}({描述})" → category: 'key', analyzedId 解析
// "环境叙事" 开头 → category: 'narrative'
// "场景道具" 开头 → category: 'prop'
// "非指证Item" 开头 → category: 'prop'
```

### 2.7 NPC（场景内）

```typescript
interface SceneNpc {
  key: string;           // YAML 中的 NPC key，如 "tommy", "rosa", "moore_001"
  talkRef: string;       // talk 字段值
  isLiar: boolean;
  motive: string;
  mindset: string;

  // 知识状态
  knows: string[];
  doesNotKnow: string[];

  // 本循环新认知（Unit2/3 的 awareness 字段，Unit1 补空数组）
  awareness: AwarenessItem[];

  // 谎言（非 Expose 对象的 NPC 也可能有谎言，如 Danny）
  lie: NpcLie | null;

  // 可提取证词
  testimonyIds: number[];

  // 鉴赏力节点
  connoisseur: ConnoisseurNode[];
}

interface NpcLie {
  content: string;    // 谎言内容
  truth: string;      // 真相
}

interface AwarenessItem {
  content: string;    // NPC 新获知的信息
  trigger: string;    // 触发来源（如 "L2 Expose结果"）
}
```

### 2.8 指证设计

```typescript
interface ExposeDesign {
  target: string;          // 如 "Rosa (103)", "Moore (06)"
  totalRounds: number;

  // NPC 状态（在 expose 下重复声明，与 scenes 中的 NPC 信息可能有延伸）
  npcState: SceneNpc | null;

  rounds: ExposeRound[];
}

interface ExposeRound {
  id: number;               // 轮次编号（1-based）
  lie: string;              // 本轮谎言文本
  lieSource: string;        // 来源证词 ID 或说明

  // 可用证据（需出示才能击穿）
  usableEvidence: ExposeEvidence[];

  // 陷阱证据（Unit3 才有）
  trapEvidence: ExposeEvidence[];

  // 自动跟进证据（Unit3 L5 R2 双阶段，不需要玩家选择）
  autoFollowupEvidence: ExposeEvidence[];

  // 击穿后的结果说明
  result: string;
}

interface ExposeEvidence {
  id: number;
  name: string;
  usage: string;  // YAML 中的 "用途:" 字段
}
```

### 2.9 疑点

```typescript
interface Doubt {
  id: number;
  text: string;

  // 解锁条件（原始字符串，如 "testimony:1031002 + item:1115"）
  unlockConditionRaw: string;

  // 解析后的解锁条件
  unlockCondition: UnlockCondition[];

  // 本循环是否解决（Unit1 有 clear 字段，Unit2/3 无此字段，补 null）
  clear: boolean | null;
}

interface UnlockCondition {
  type: 'testimony' | 'item';
  id: number;
}

// unlock_condition 解析规则：
// "testimony:1031002 + item:1115" → 按 " + " 分割，再按 ":" 分割类型和 ID
```

### 2.10 特殊事件

```typescript
// 统一容器，合并 sudden_event 和 events[]
interface SpecialEvent {
  type: 'sudden' | 'closing';   // sudden_event → 'sudden'，events[] → 按 type 字段
  name: string;
  sceneId: number | null;        // closing 事件有 scene_id，sudden 没有
  trigger: string;
  characters: string[];
  purpose: string;
  result: string | null;         // sudden 事件有 result，closing 一般没有
}
```

### 2.11 鉴赏力节点

```typescript
interface ConnoisseurNode {
  type: 'source' | 'quiz';
  nodeId: string | null;    // quiz 才有 node 字段，如 "#006", "#104"
  triggerMode: string | null; // Unit3 才有 trigger_mode 字段

  // source 节点
  content: string | null;   // source 的知识内容
  noteForFuture: string | null; // note 字段（说明该 source 在未来哪个 loop 被考察）

  // quiz 节点
  question: string | null;
  answer: string | null;    // 包含正确答案的完整来源说明
  reward: string | null;    // Unit3 有此字段，Unit1/2 没有
}
```

### 2.12 派生证据映射

```typescript
interface DerivedEvidenceMap {
  // key: 原始证据 ID，value: 派生证据 ID
  // 来源1：证据条目的 analyzed_id 字段
  // 来源2：Unit3 的「派生证据说明」章节（YAML 注释，需要正则解析）
  [originalId: number]: number;
}
```

---

## 3. 情绪弧线算法

情绪弧线（Tension Curve）= 一个 Loop 从 opening 到 expose 最终轮的张力变化曲线。
横轴是时间轴节点，纵轴是 0-100 的张力值。

### 3.1 张力基准：Opening

```
opening_tension = BASE_TENSION

BASE_TENSION = 30（默认值）

调整规则：
  + 15  →  opening NPC 的 isLiar = true
  + 10  →  opening 后立刻有 sudden_event
  + 10  →  player_context.knownFacts 数量 >= 5（玩家已积累大量背景知识，期待感强）
  - 5   →  player_context.knownFacts 为空（L1，玩家从零开始，张力较低）

上限：60（开篇不宜超过中游）
下限：20
```

### 3.2 场景张力贡献

每个 Scene 作为一个张力节点，贡献值叠加到当前累积张力：

```
scene_tension_contribution(scene) =
    evidence_score(scene)
  + npc_score(scene)
  + doubt_proximity_bonus(scene)

其中：

evidence_score(scene) =
    count(category='key') × 15
  + count(category='narrative') × 3
  + count(category='prop') × 2
  + count(isDerived=true) × 10   // 派生证据说明玩家有深度分析动作，张力更高

npc_score(scene) =
    (scene.npcs 非空 ? 5 : 0)
  + (any npc.isLiar ? 15 : 0)
  + (any npc.testimonyIds 非空 ? 8 : 0)
  + (any npc.connoisseur 非空 ? 4 : 0)  // 鉴赏力有额外互动空间

doubt_proximity_bonus(scene) =
    count(doubts 中 unlockCondition 引用本场景证据) × 10
    // 疑点解锁集中在该场景 → 张力峰值
```

### 3.3 Expose 各轮张力

```
expose_round_tension(round) =
    EXPOSE_BASE
  + round.id × ROUND_INCREMENT
  + lie_severity(round)
  + evidence_density(round)

其中：

EXPOSE_BASE = 60        // 所有 expose 轮次从 60 起步
ROUND_INCREMENT = 12    // 每轮递增 12

lie_severity(round) =
    判断 round.result 的文字：
      包含"彻底崩溃"或"防线崩溃"  → +15
      包含"被迫承认"              → +8
      包含"部分承认"              → +5
      包含"辩解"                 → +3
      其余                       → 0

evidence_density(round) =
    count(round.usableEvidence) × 5
  + count(round.autoFollowupEvidence) × 8  // 自动跟进不需要玩家选择，节奏更紧
  + (round.trapEvidence 非空 ? -3 : 0)     // 有陷阱证据 → 轻微降低（需要玩家甄别，节奏稍缓）

上限：100
```

### 3.4 Closing Events 张力

```
closing_event_tension =
    前一个节点张力值 - 15   // closing 事件通常是情绪消化时刻，张力短暂下降
    最低不低于 40           // 但 closing 结尾往往埋新悬念，不会完全平静
```

### 3.5 完整弧线计算流程

```
nodes = []

// 1. Opening 节点
nodes.push({
  label: "Opening",
  tension: opening_tension,
  sceneId: opening.sceneId,
  type: 'opening'
})

// 2. Sudden Event（如果存在）
if (suddenEvent != null) {
  nodes.push({
    label: suddenEvent.name,
    tension: nodes.last().tension + 20,
    type: 'sudden_event'
  })
}

// 3. 各自由探索场景（按 YAML 顺序，idle 场景不独立计算，折叠）
for scene in scenes:
  if scene.sceneType == 'idle':
    continue   // idle 场景不作为独立张力节点
  contrib = scene_tension_contribution(scene)
  tension = clamp(nodes.last().tension + contrib, 0, 85)
  nodes.push({
    label: scene.name,
    tension: tension,
    sceneId: scene.id,
    type: scene.sceneType
  })

// 4. Expose 各轮（作为独立节点）
for round in expose.rounds:
  tension = expose_round_tension(round)
  nodes.push({
    label: `Expose R${round.id}: ${round.lie[:20]}...`,
    tension: tension,
    sceneId: expose_scene_id,  // 从 scenes 中找 expose 场景的 ID
    type: 'expose'
  })

// 5. Closing Events（如果存在）
for event in specialEvents where type='closing':
  tension = nodes.last().tension - 15
  nodes.push({
    label: event.name,
    tension: max(tension, 40),
    type: 'closing'
  })

return nodes
```

### 3.6 关键节点标记规则

只在以下条件满足时加注解，不要到处都是标注：

| 条件 | 注解文本 |
|------|---------|
| 节点 tension 是整条弧线的最高点 | "峰值：{tension}" |
| expose 最终轮（round.id == expose.totalRounds） | "Expose 终轮" |
| 节点 tension 比前一节点高 >= 20 | "张力跃升 +{delta}" |
| 节点 tension 比前一节点低 >= 15（非 closing 类型） | "张力骤降 -{delta}"（可能是 idle 场景插入过多） |
| doubts 中有 3 个以上疑点都指向同一场景的证据 | "疑点密集区" |
| suddenEvent 节点 | "突发事件" |
| post_expose_knowledge 数量 >= 5 | 在 expose 终轮注解加 "重大揭示" |

---

## 4. 证据关联图数据结构

使用标准 nodes + edges 结构，兼容 D3.js / vis.js / ECharts graph 组件。

### 4.1 节点类型

```typescript
type NodeType =
  | 'evidence'    // 证据/道具节点
  | 'scene'       // 场景节点
  | 'doubt'       // 疑点节点
  | 'expose_round' // 指证轮次节点
  | 'npc';        // NPC 节点（可选，默认不显示，按需展开）

interface GraphNode {
  id: string;           // 唯一标识，格式："{type}_{id}"，如 "evidence_1115"
  type: NodeType;
  label: string;        // 显示文本

  // 视觉样式（供渲染层使用）
  color: string;        // 见下方颜色规则
  shape: NodeShape;     // 见下方形状规则
  size: number;         // 节点大小，关键证据 > 环境叙事

  // 原始数据引用
  sourceData: EvidenceItem | Scene | Doubt | ExposeRound;
}

type NodeShape = 'circle' | 'diamond' | 'rect' | 'triangle';

// 颜色规则：
// evidence (key)      → #E8A838（琥珀色，关键证据）
// evidence (narrative) → #6B8F9E（蓝灰，环境叙事）
// evidence (prop)      → #8E8E8E（灰色，场景道具）
// evidence (derived)   → #C67C3E（深琥珀，派生证据）
// evidence (trap)      → #CC4444（红色，陷阱）
// scene               → #4A7C59（深绿，场景）
// doubt               → #7A5C9E（紫色，疑点）
// expose_round        → #C44444（深红，指证轮次）
// npc                 → #5C7AA8（蓝色，NPC）

// 大小规则：
// evidence (key)      → size: 18
// evidence (derived)  → size: 15
// evidence (narrative/prop) → size: 10
// scene               → size: 22
// doubt               → size: 16
// expose_round        → size: 20
```

### 4.2 边类型

```typescript
type EdgeType =
  | 'located_in'      // 证据 → 场景（证据在该场景发现）
  | 'unlocks_doubt'   // 证据 → 疑点（证据是疑点解锁条件之一）
  | 'used_in_expose'  // 证据 → 指证轮次（证据用于该轮指证）
  | 'derived_from'    // 派生证据 → 原始证据（analyzed_id 关系）
  | 'testimony_for'   // NPC → 疑点（NPC 证词是疑点解锁条件）
  | 'trap_in';        // 证据 → 指证轮次（以陷阱身份存在）

interface GraphEdge {
  id: string;           // "{source_id}_{target_id}_{type}"
  source: string;       // 源节点 ID
  target: string;       // 目标节点 ID
  type: EdgeType;

  // 视觉样式
  color: string;
  dashed: boolean;      // 虚线 = 次要关系
  label: string | null; // 边标签（通常为 null，只在特殊情况加）
  width: number;        // 线宽
}

// 边颜色规则：
// located_in       → #888（灰色虚线）
// unlocks_doubt    → #7A5C9E（紫色实线）
// used_in_expose   → #C44444（红色实线）
// derived_from     → #C67C3E（深琥珀虚线，方向：派生证据指向原始证据）
// testimony_for    → #5C7AA8（蓝色虚线）
// trap_in          → #CC4444（红色虚线，注意 dashed: true）

// 线宽规则：
// unlocks_doubt, used_in_expose → width: 2（主要推理链，加粗）
// 其余                         → width: 1
```

### 4.3 图构建流程

```
function buildGraph(stateData: StateData): { nodes: GraphNode[], edges: GraphEdge[] }

// Step 1: 构建场景节点
for scene in stateData.scenes where sceneType != 'idle':
  nodes.add(SceneNode(scene))

// Step 2: 构建证据节点 + located_in 边
for scene in stateData.scenes:
  for ev in scene.evidence:
    nodes.add(EvidenceNode(ev))
    edges.add(located_in(ev.id → scene.id))

    // 如果有 analyzed_id，同时构建派生证据节点和 derived_from 边
    if ev.analyzedId != null:
      nodes.add(EvidenceNode(derived, ev.analyzedId))
      edges.add(derived_from(ev.analyzedId → ev.id))

// Step 3: 构建疑点节点 + unlocks_doubt 边
for doubt in stateData.doubts:
  nodes.add(DoubtNode(doubt))
  for condition in doubt.unlockCondition:
    if condition.type == 'item':
      // 可能引用派生证据 ID，确保节点已存在
      edges.add(unlocks_doubt(condition.id → doubt.id))
    if condition.type == 'testimony':
      edges.add(testimony_for(condition.id → doubt.id))

// Step 4: 构建 Expose 轮次节点 + used_in_expose 边
for round in stateData.expose.rounds:
  nodes.add(ExposeRoundNode(round))
  for ev in round.usableEvidence:
    edges.add(used_in_expose(ev.id → round.id))
  for ev in round.autoFollowupEvidence:
    edges.add(used_in_expose(ev.id → round.id))  // 自动跟进和普通可用证据同样处理
  for ev in round.trapEvidence:
    edges.add(trap_in(ev.id → round.id))

return { nodes, edges }
```

### 4.4 布局建议

证据关联图不适合纯力导向布局（边太多会打乱），建议分层布局：

```
层次结构（从左到右）：
  Layer 0（最左）: 场景节点
  Layer 1:          证据节点（含派生证据）
  Layer 2:          疑点节点
  Layer 3（最右）: Expose 轮次节点

垂直分组：按场景 ID 分组，同场景证据纵向排列
```

---

## 5. 信息密度计算公式

信息密度（Information Load）= 策划者向玩家塞入信息的总量，用于提示"某场景是否过载"。

### 5.1 场景级信息密度

```
InfoLoad(scene) =
    key_evidence_count × 3.0
  + derived_evidence_count × 2.5
  + narrative_evidence_count × 0.5
  + prop_evidence_count × 0.3
  + npc_is_liar_count × 4.0
  + npc_testimony_count × 2.0
  + npc_connoisseur_count × 1.5
  + known_facts_referenced × 1.0
    // known_facts_referenced = 本场景的 newDirections 中引用了多少已知事实

// 解读阈值：
// 0.0 – 3.0  → 轻量（idle 场景，浏览即可）
// 3.1 – 6.0  → 适中（正常调查场景）
// 6.1 – 9.0  → 较重（注意对话设计要给玩家消化时间）
// 9.1 +      → 过载警告（建议拆分或降低证据密度）
```

### 5.2 循环级信息密度

```
InfoLoad(loop) =
    sum(InfoLoad(scene) for scene in scenes)
  + expose_complexity(loop)

expose_complexity(loop) =
    expose.totalRounds × 5.0
  + sum(len(round.usableEvidence) for round in expose.rounds) × 2.0
  + len(post_expose_knowledge) × 1.5

// 循环级阈值：
// 0 – 25   → 轻量循环（L1 通常如此）
// 26 – 50  → 标准循环
// 51 – 70  → 信息较重（确保每场景节奏有缓冲）
// 71 +     → 过载警告（可视化时以红色高亮显示）
```

### 5.3 每循环场景间信息密度分布

**这是信息密度计算最重要的输出**，用于发现"前重后轻"或"中间堆砌"问题：

```
distribution_score(loop) =
    max(InfoLoad(scenes)) / sum(InfoLoad(scenes))

// distribution_score 解读：
// < 0.4  → 分布均匀（理想状态）
// 0.4–0.6 → 轻微集中，可接受
// > 0.6  → 严重集中（某场景承载了大部分信息）
//          → 触发注解："信息集中在 {scene.name}，建议分散"
```

### 5.4 公式使用的可视化输出

- 每个 Scene 节点旁显示密度数值（小字），颜色从绿到红渐变
- Loop 右上角显示循环总密度 + distribution_score
- 超过阈值的场景，在情绪弧线图中加底色高亮（浅红背景）
- 在注解列表中输出文字："SC{id} {name} 信息密度 {value}，建议检查"

---

## 6. 注解（Annotation）触发规则汇总

注解是出现在可视化图表上的文字标签，用来提醒策划注意特定设计问题或亮点。
**原则：宁少勿多，只在确实需要策划关注时才触发。**

### 6.1 触发规则完整列表

| 编号 | 触发条件 | 注解文本 | 触发位置 |
|------|---------|---------|---------|
| A01 | tension 是整条弧线最高点 | "全Loop峰值 {value}" | 弧线节点 |
| A02 | tension 比前一节点高 >= 20 | "张力跃升 +{delta}" | 弧线节点 |
| A03 | tension 比前一节点低 >= 15（非 closing 节点） | "张力骤降 -{delta}，检查场景空白是否合理" | 弧线节点 |
| A04 | expose 最终轮 | "最终指证" | 弧线节点 |
| A05 | post_expose_knowledge 数量 >= 5 | "重大揭示（{n}条）" | expose 终轮节点 |
| A06 | InfoLoad(scene) > 9.0 | "信息过载 {value}，建议拆分" | 场景节点（密度图） |
| A07 | distribution_score(loop) > 0.6 | "信息集中在 {scene.name}" | 循环摘要区 |
| A08 | 某疑点有 3+ 条解锁条件指向同一场景 | "疑点解锁集中区" | 证据关联图中场景节点 |
| A09 | expose.round 中有 trap_evidence | "含陷阱证据，注意玩家误选率" | 指证轮次节点 |
| A10 | expose.round 中有 auto_followup_evidence | "双阶段指证" | 指证轮次节点 |
| A11 | doubt.clear == false（Unit1 特有） | "遗留疑点，转至后续Loop" | 疑点节点 |
| A12 | sudden_event 存在 | "突发事件：{name}" | 开篇区域 |
| A13 | NPC 的 isLiar=true 且 connoisseur 非空 | "说谎者含鉴赏力节点，注意不要泄露谎言" | 证据关联图 NPC 节点 |
| A14 | 某证据出现在多个 expose 轮（usedInExposeRounds.length >= 2） | "跨轮复用证据" | 证据节点 |
| A15 | 某关键证据（category='key'）未出现在任何 expose 轮 usable_evidence 中 | "未用于指证的关键证据，检查是否遗漏" | 证据节点 |

### 6.2 注解显隐控制

可视化器应提供过滤器，允许策划按需显隐各类注解：

```
- [ ] 系统性警告（A06, A07, A15）
- [ ] 张力曲线注解（A01, A02, A03, A04, A05）
- [ ] 指证设计注解（A09, A10, A14）
- [ ] 疑点注解（A08, A11）
- [ ] 叙事事件注解（A12, A13）
```

---

## 7. YAML 解析器实现备注

### 7.1 已知解析难点

1. **YAML 头部注释不是标准 YAML 数据**
   解析器（如 js-yaml）会忽略注释。需要先用正则提取头部注释行，再交给 YAML 解析器处理剩余内容。

   ```javascript
   // 提取 meta 信息的正则（适用于三个 Unit）
   const LIAR_REGEX = /# 本循环说谎者[：:]\s*(.+)/;
   const REVEAL_REGEX = /# 核心揭示[：:]\s*(.+)/;
   const TIME_REGEX = /# 时间[：:]\s*(.+)/;
   ```

2. **Unit3 派生证据说明章节是 YAML 注释块**
   整段「派生证据说明」使用 `# 分析N：` 格式的注释，不是 YAML 结构。
   需要正则解析如：`# 3501(标注报纸) → 系统层分析 → 3502(笔迹比对报告)`
   提取格式：`{sourceId}(\w+) → .+ → {derivedId}(\w+)`

3. **`result` 字段是多行字符串（YAML `|` 块）**
   js-yaml 可正确解析 `|` 块，但渲染时需要保留换行，显示为 `<pre>` 或 `white-space: pre-line` 的 div。

4. **opening 下有多个 NPC key（如 Unit3 L5 同时有 emma_008 和 mickey_001）**
   开篇 NPC 的 key 名称不固定，需要遍历 opening 的所有子键，判断是否包含 `is_liar` 字段来识别 NPC 条目（而非 scene_id、characters 等非 NPC 字段）。

5. **场景 ID 在 YAML 中定义为整数，但字符串比较时需注意类型**
   `scene.id: 1122` 在 YAML 中是整数，与 `opening.scene_id: 1122` 做匹配时要统一转 number。

### 7.2 推荐的文件加载顺序

```javascript
// 加载单个 Loop 的完整数据
async function loadLoopState(unit, loop) {
  const url = `剧情设计/Unit${unit}/state/loop${loop}_state.yaml`;
  const raw = await fetch(url).then(r => r.text());

  // Step 1: 正则提取注释中的 meta 信息
  const meta = extractMeta(raw, unit, loop);

  // Step 2: 用 js-yaml 解析结构化数据
  const yaml = jsyaml.load(raw);

  // Step 3: 标准化为 StateData 结构
  const stateData = normalize(yaml, meta);

  // Step 4: 构建派生关系（从 analyzed_id 和注释中的派生说明）
  stateData.derivedEvidenceMap = buildDerivedMap(raw, yaml);

  // Step 5: 反向填充 evidence 的 usedInExposeRounds 和 isTrap
  enrichEvidenceWithExposeInfo(stateData);

  return stateData;
}
```

---

*本文档版本：2026-04-08*
*服务于：`preview_new2/state_visualizer.html`（待开发）*
*数据来源：三个 Unit 共 18 个 state YAML 文件的结构分析*
