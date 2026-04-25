# 审计维度速查表

7 维 + 1 兜底，覆盖一致性审计的所有面向。每个维度独立 sub-agent，结果汇入同一报告。

## 维度代码 → 名称 → 执行者

| 代码 | 名称 | 执行者 | 输出文件 |
|---|---|---|---|
| **A** | 人物档案 | character-fact-auditor | `issues/A-character.jsonl` |
| **B** | 称谓 | addressing-auditor | `issues/B-addressing.jsonl` |
| **C** | 时间线/跨Loop泄露 | timeline-auditor | `issues/C-timeline.jsonl` |
| **D** | 物证物理属性 | consistency-checker | `issues/D-items.jsonl` |
| **E** | 年代用语 | narrative-designer（专项调用） | `issues/E-era.jsonl` |
| **F** | 声纹 | voice-print-auditor（每 NPC 一次） | `issues/F-voice-{npc}.jsonl` |
| **G** | 多视角 | multi-perspective-auditor | `issues/G-perspective.jsonl` |
| **X** | 对话 12 项兜底 | dialogue-reviewer | `issues/X-dialogue12.jsonl` |

## 维度边界（避免重复审计）

| 容易混淆的两维 | 边界 |
|---|---|
| A 人物档案 vs F 声纹 | A 查"事实陈述与档案是否对账"，F 查"说话方式是否像本人"。同一句话两者都可触发是正常的——A 报"年龄不对"，F 报"AI 腔"。 |
| A 人物档案 vs G 多视角 | A 查"单一 NPC 自身陈述"，G 查"跨 NPC 同事件描述"。A 看 1 句，G 看 N 句。 |
| B 称谓 vs C 时间线 | 称谓的"早改口"是隐含信息泄露——表面归 B，但如果改口涉及 NPC 知道未发生事件，C 也会报。两边都报是正常的，最终会在报告中并列展示。 |
| D 物证 vs A 人物档案 | D 查物理属性（尺寸/颜色/品牌），A 查"人物持有物声明"。"我的银烟盒"——A 查档案是否记载"Vivian 持银烟盒"，D 查烟盒物理描述跨场景是否一致。 |
| E 年代 vs F 声纹 | E 查"1920s 不该出现的词"，F 查"该 NPC 不该用的词"。年代词同时也是声纹偏离时，两边都报。 |
| X 对话 12 项 vs 其他维度 | X 是兜底——它的 12 项里有很多在专维度里更专业地审了。X 仍要跑，专门捕捉对话链断裂、平行场景隔离、Lie 主动性这些**结构问题**。事实/称谓/声纹问题以专维度结果为准。 |

## 严重度公约

所有维度统一三档：

| 等级 | 含义 | 处理 |
|---|---|---|
| **P0** | 推理体验破坏（信息泄露、核心事实矛盾、玩家会立即出戏） | 必须修复，进 Phase 3 复核 |
| **P1** | 设计质量损失（声纹偏离、未到改口时间已改口、年代词混入） | 应该修复，进 Phase 3 复核 |
| **P2** | 风格与雕琢（用词雷同、轻度风格漂移） | 建议修复，跳过 Phase 3 直接归 verified |

特殊状态：

| 状态 | 含义 |
|---|---|
| `needs_human` | Phase 3 复核 agent 无法判定（context 不足、设计意图不明） |
| `meta_fact_conflict` | 事实表自身有冲突（不归任何维度，单列展示） |
| `unverified` | --skip-verify 模式下所有 issue 的状态 |

## Issue jsonl 公共字段

每条 issue（不论维度）必须包含：

```json
{
  "_dim": "A | B | C | D | E | F | G | X",
  "file": "源文件路径",
  "line_id": "对话 9 位 ID（无对话 ID 时填 N/A）",
  "speaker": "发言 NPC（如适用）",
  "loop": "L1–L6",
  "type": "维度内枚举的具体类型",
  "severity": "P0 | P1 | P2",
  "suggestion": "修复建议（≤80 字）"
}
```

每个维度的 type 枚举见对应 agent 定义。

## 维度优先级（出报告时的展示顺序）

按**对玩家推理体验的破坏力**降序排列：

1. **C** 时间线（信息泄露最致命）
2. **G** 多视角（核心事实矛盾会让玩家无所适从）
3. **A** 人物档案（NPC 自相矛盾立刻出戏）
4. **B** 称谓（暗含关系/信息泄露）
5. **D** 物证（错的证据描述会引导错的推理）
6. **F** 声纹（影响沉浸感但不破坏推理）
7. **E** 年代用语（影响沉浸感）
8. **X** 对话 12 项兜底（结构性问题各异）

报告里筛选/排序按严重度优先，但同严重度内按上述维度顺序排。
