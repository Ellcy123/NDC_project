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
| **H** | 对话 ID 编排 | consistency-checker | `issues/H-dialogue-id.jsonl` |
| **X** | 对话 12 项兜底 | dialogue-reviewer | `issues/X-dialogue12.jsonl` |

## 维度边界（避免重复审计）

| 容易混淆的两维 | 边界 |
|---|---|
| A 人物档案 vs F 声纹 | A 查"事实陈述与档案是否对账"，F 查"说话方式是否像本人"。同一句话两者都可触发是正常的——A 报"年龄不对"，F 报"AI 腔"。 |
| A 人物档案 vs G 多视角 | A 查"单一 NPC 自身陈述"，G 查"跨 NPC 同事件描述"。A 看 1 句，G 看 N 句。 |
| B 称谓 vs C 时间线 | 称谓的"早改口"是隐含信息泄露——表面归 B，但如果改口涉及 NPC 知道未发生事件，C 也会报。两边都报是正常的，最终会在报告中并列展示。 |
| D 物证 vs A 人物档案 | D 查物理属性（尺寸/颜色/品牌），A 查"人物持有物声明"。"我的银烟盒"——A 查档案是否记载"Vivian 持银烟盒"，D 查烟盒物理描述跨场景是否一致。 |
| E 年代 vs F 声纹 | E 查"1920s 不该出现的词"，F 查"该 NPC 不该用的词"。年代词同时也是声纹偏离时，两边都报。 |
| H 对话 ID vs X 对话 12 项 | H 只查 ID 编排（格式、连续性、跨文件冲突、字数合规）。X 查对话**内容结构**（Lie 主动性、分支维度差异、信息密度等）。两者不重叠。 |
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

## H 维度 — 对话 ID 编排审计规则

### 检查项与 type 枚举

| type | severity | 说明 |
|------|----------|------|
| `id_format` | P0 | ID 非 9 位纯数字（含字母后缀 a/b/c/A/B、下划线等） |
| `id_gap` | P1 | 同一段内 ID 不连续（跳号） |
| `id_duplicate` | P0 | 同一文件内同一 ID 出现 2 次以上 |
| `id_cross_file` | P0 | 跨文件使用了错误前缀（如 morrison_001 中出现 901xxxxxx） |
| `conv_conflict` | P0 | 跨 Loop 的 conv 编号冲突（如 L3 和 L4 都用了 904003xxx） |
| `branch_start` | P1 | 分支路径未从 x01 起编（如从 x00 开始） |
| `merge_range` | P1 | 汇合点未使用 4xx 段（如用了 019/020 或 030） |
| `trap_return` | P1 | Expose 陷阱路径末尾缺少 `→ 回到` 指向正确 Lie/branches 节点 |
| `branch_ref` | P0 | branches/Lie 节点中的跳转目标 ID 不存在 |
| `char_over_35` | P1 | 台词行中文字符数（含中文标点）超过 35 |
| `section_mismatch` | P1 | `## Talk:` / `## Expose:` 后的文件名与 ID 段前缀不匹配 |
| `get_mismatch` | P0 | get 标记引用的证词 ID 与 state 文件不一致 |
| `lie_mismatch` | P0 | Lie 标记的 lie_source 与 state expose 段不一致 |
| `post_expose_not_split` | P1 | post_expose 内容仍在 Expose 文件内，未拆为独立 Talk |
| `state_missing_section` | P1 | State 声明的对话在 MD 中无对应 section |

### ID 编码规则（检查依据）

**Talk ID**：`9{npc=2}{conv=3}{seq=3}` — 9 位
- 9 = Unit9 固定前缀
- npc = NPC 编码（01=Emma, 02=Zack, 03=Rosa, 04=Morrison, 05=Tommy, 06=Vivian, 07=Jimmy/James, 08=Anna, 09=Whale）
- conv = NPC 在全 Unit 的第几次对话（001 起，跨 Loop 递增）
- seq = 句子序号

**Expose ID**：`9{npc=2}9{loop=2}{seq=3}` — 9 位
- 第 4 位固定为 9（区别 Talk）
- loop = Loop 编号（01-06）

**seq 编号规则**：
- 主线：`001` 起递增
- 分支路径 ❶/❷/❸：`1xx`/`2xx`/`3xx`（从 x01 起）
- 汇合点：`4xx`（从 401 起）
- 双分支文件：第二组分支 `5xx`/`6xx`，第二组汇合 `8xx`
- Expose 陷阱：R1 陷阱 `1xx`/`2xx`/`3xx`，R2 陷阱 `4xx`

**字数规则**：每句台词 ≤ 35 个中文字符（含中文标点；不含英文/数字/空格/[...]动作/<!-- -->注释/📋系统行）

### 跨 Loop conv 编号追踪表（Unit9）

审计时需构建此表，确认无冲突：

| NPC | L1 | L2 | L3 | L4 | L5 | L6 |
|-----|----|----|----|----|----|----|
| Emma(01) | 001 | 002 | 003 | 004 | 005 | 006,007 |
| Rosa(03) | 001 | — | 002,003 | — | — | 004 |
| Morrison(04) | 001,002 | — | 003 | 004,005 | — | 006+ |
| Tommy(05) | — | 001,002 | — | 003 | 004 | 005 |
| Vivian(06) | 001 | — | 002 | 003,004 | — | 005 |
| James(07) | — | 001 | 002 | — | 003 | 004 |
| Anna(08) | — | — | — | — | 001 | 002 |
| Whale(09) | — | — | — | — | — | 001 |

## 维度优先级（出报告时的展示顺序）

按**对玩家推理体验的破坏力**降序排列：

1. **C** 时间线（信息泄露最致命）
2. **G** 多视角（核心事实矛盾会让玩家无所适从）
3. **A** 人物档案（NPC 自相矛盾立刻出戏）
4. **B** 称谓（暗含关系/信息泄露）
5. **D** 物证（错的证据描述会引导错的推理）
6. **H** 对话 ID 编排（ID 错乱会导致 sync 失败、游戏引擎崩溃）
7. **F** 声纹（影响沉浸感但不破坏推理）
8. **E** 年代用语（影响沉浸感）
9. **X** 对话 12 项兜底（结构性问题各异）

报告里筛选/排序按严重度优先，但同严重度内按上述维度顺序排。
