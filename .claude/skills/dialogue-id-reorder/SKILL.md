---
name: dialogue-id-reorder
description: "对话 ID 重编排：逐 Loop 逐文件清理对话 ID——连续化、拆长句、修分支/陷阱段、审查。适用于 MD 草稿 ID 混乱时的系统性整理。"
argument-hint: "[Unit 编号] [Loop 编号，可选；不填则逐 Loop 处理]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash
---

# 对话 ID 重编排 Skill

对话 MD 草稿经过多轮修改后，ID 常出现跳号、重复、乱序等问题。本 skill 逐 Loop、逐对话文件系统性重编 ID，同时拆分超长句子，最终输出干净、连续、可直接 sync 的 MD 草稿。

## 适用场景

- MD 草稿已存在但 ID 混乱（跳号 / 重复 / 乱序）
- 需要拆分超长句子（>35 中文字）后重新分配 ID
- Expose 内陷阱路径 ID 需要规范化
- 新增或删除了对话节点，需要重编后续 ID

## 不适用

- 草稿还没写（先走 `/team-dialogue`）
- 只改文案不改 ID（直接 Edit）
- State 还没定稿（先走 `/team-loop` 或 `/unit-state-generator`）

---

## 核心规则

### 规则 1：ID 编码格式

#### Talk 对话 ID（9 位）

格式：`9{npc}{conv}{seq}`

| 字段 | 位数 | 说明 |
|------|------|------|
| 9 | 1 | Unit9 固定前缀 |
| npc | 2 | NPC 编码（见下方编码表） |
| conv | 3 | NPC 在全 Unit 的第几次对话（001 起） |
| seq | 3 | 该次对话内句子序号 |

例：`901001011` = Unit9 / Emma(01) / 第 1 次对话 / 第 011 句

#### Expose 对话 ID（9 位）

格式：`9{npc}9{loop}{seq}`

| 字段 | 位数 | 说明 |
|------|------|------|
| 9 | 1 | Unit9 固定前缀 |
| npc | 2 | 被指证 NPC 编码 |
| 9 | 1 | Expose 标记位（固定 9，区别 Talk） |
| loop | 2 | Loop 编号（01-06） |
| seq | 3 | 句子序号 |

例：`903901004` = Rosa / Expose / Loop1 / 第 004 句

#### NPC 编码表（Unit9）

| 代码 | NPC | 代码 | NPC |
|------|-----|------|-----|
| 01 | Emma | 06 | Vivian |
| 02 | Zack | 07 | Jimmy |
| 03 | Rosa | 08 | Anna |
| 04 | Morrison | 09 | Whale |
| 05 | Tommy | | |

---

### 规则 2：主线 seq 编号

#### Talk 主线

```
001  开场第 1 句
002  开场第 2 句
...
0xx  branches 节点（本身占一个 ID）
...  继续主线（branches 之前的句子 + branches 节点 = 连续编号）

1xx  分支路径 ❶（从 101 起递增）
2xx  分支路径 ❷（从 201 起递增）
3xx  分支路径 ❸（从 301 起递增）

4xx  汇合点（从 401 起递增，直到 end）
```

- 主线（`001`-`0xx`）+ 汇合（`4xx`）= 玩家必经路径
- 分支路径（`1xx`/`2xx`/`3xx`）= 玩家选其一
- **branches 节点本身占一个主线 ID**（如 `007`），不跳过
- **所有分支最终汇合到 `4xx` 段**，禁止永久分叉

#### Expose 主线

```
001  R1 开场第 1 句
002  R1 开场第 2 句
...
0xx  R1 Lie 节点（证据选择界面，本身占一个 ID）
0xx  R1 正确路径 — 出示正确证据后的主线推进
...
0xx  R1→R2 过渡（Rosa 补出新谎言）
0xx  R2 Lie 节点
0xx  R2 失败 / 转向 post_expose 入口
...（如有 R3/R4 继续主线递增）

1xx  R1 陷阱① — 出示错误证据 A（→ 回到 R1 Lie 重选）
2xx  R1 陷阱② — 出示错误证据 B（→ 回到 R1 Lie 重选）
3xx  R1 陷阱③ — 出示错误证据 C（→ 回到 R1 Lie 重选）
4xx  R2 陷阱① — 出示错误证据 D（→ 回到 R2 Lie 重选）
5xx  R2 陷阱②（如有）
...（按 Round 顺序继续分配 xx 段）
```

- **主线（`001` 递增）= 玩家走正确路径时看到的完整流程**
- 陷阱路径用 `1xx`/`2xx`/`3xx`... 与 Talk 分支规则统一
- 每个陷阱路径末尾标注 `→ 回到 {Lie 节点 ID}`（重选）
- Lie 节点和 branches 节点一样，本身占一个主线 ID

---

### 规则 3：句子拆分

- **每句台词 <= 35 个中文字**（含中文标点，不含英文/数字/空格/方括号动作指令）
- 超过 35 字的台词必须拆成两句或多句，每句分配独立 ID
- MD 草稿中已经换行但共用一个 ID 的内容，拆成独立 ID
- 拆分时保持语义自然断句，不在词语中间截断

**字数计算规则**：
- 计入：中文字符、中文标点（，。！？——……、；：""''）
- 不计入：英文字母、数字、空格、方括号内的动作指令 `[...]`、HTML 注释 `<!-- -->`、`> ` 引用前缀、`📋 获取证词` 系统行

**拆分示例**：

改前（1 个 ID，超 35 字）：
```markdown
### 903001003
**罗莎·马丁内斯** [把拖把把儿攥得更紧]
> 我...月底了，Webb 先生要求彻底清洁。我一直在走廊那边打扫...然后...然后听到了枪声。
```

改后（2 个 ID）：
```markdown
### 903001003
**罗莎·马丁内斯** [把拖把把儿攥得更紧]
> 我...月底了，Webb 先生要求彻底清洁。

### 903001004
**罗莎·马丁内斯**
> 我一直在走廊那边打扫...然后...然后听到了枪声。
```

---

### 规则 4：纯画面/动作节点不分配 ID

如果一段内容仅是环境描写、动作转场、NPC 无台词的表情反应，**不给独立 ID**——用 HTML 注释 `<!-- -->` 或合并进相邻台词的 `[...]` 动作括号。

**例外**：承载机制标记的节点（`get` / `show` / `branches` / `end`）即使无台词也保留 ID。

---

### 规则 5：post_expose 插入剧情拆分

State 中的 `post_expose` / `interlude` 必须从 Expose 文件中拆出，作为**独立 Talk 文件**：

- 文件名按主要对话对象命名：`{npc}_{conv}.json`
- ID 段按该 NPC 的下一个 conv 编号分配
- 例：Loop1 的 post_expose 主要对象是 Morrison → `morrison_002.json` → ID 段 `904002xxx`

---

### 规则 6：禁止的 ID 操作

- 禁止跳号（如 017 → 019）
- 禁止重复 ID（同一文件内任何 ID 只能出现一次）
- 禁止跨文件使用同一 ID（如 morrison_001 中不能出现 `901001028`）
- 禁止分支路径 ID 与主线 ID 重叠
- Lie 节点 / branches 节点本身必须占主线 ID，不能没有 ID

---

## Pipeline

### Phase 0：前置读取

读取以下文件，建立当前状态的完整认知：

1. **State 文件**：`剧情设计/Unit{N}/state/loop{X}_state.yaml`
   - 提取：opening / scenes / expose / post_expose / interlude
   - 确认哪些对话文件应该存在
2. **现有 MD 草稿**：`AVG/对话配置工作及草稿/Unit{N}/Loop{X}_生成草稿.md`
   - 提取：所有 section 头（`## Talk:` / `## Expose:`）
   - 提取：所有现有 ID（`### {9位数字}`）
3. **对话规则**：`.claude/rules/dialogue.md`

输出**对话文件清单**给用户确认：

```
Loop{X} 对话文件清单：
1. emma_001.json — Opening 插入剧情 — 901001xxx
2. vivian_001.json — Talk — 906001xxx
3. rosa_001.json — Talk — 903001xxx
4. morrison_001.json — Talk — 904001xxx
5. Loop1_rosa.json — Expose — 903901xxx
6. morrison_002.json — Talk (post_expose 拆出) — 904002xxx
```

AskUserQuestion 确认后进入 Phase 1。

### Phase 1：逐文件 ID 重编

**按文件清单顺序**，每个文件执行以下步骤：

#### Step 1.1：逐句扫描

对当前文件的每一句台词：
1. 提取中文字数（按规则 3 的计算方式）
2. 标记超 35 字的句子（需拆分）
3. 标记 MD 中已换行但共用 ID 的句子（需拆分）
4. 标记无台词但占 ID 的纯画面节点（需移除 ID）
5. 标记跨文件引用的 ID（需修正）

#### Step 1.2：生成重编方案

输出**改前 → 改后**对照表给用户：

```
文件：emma_001.json
─────────────────────────────────
旧 ID        → 新 ID        备注
901001001    → 901001001    不变
901001002    → 901001002    不变
...
901001017    → 901001017    不变
（缺 018）   →              跳号修复
901001019    → 901001018    重编
901001020    → 901001019    重编 + 拆分（原文 42 字）
             → 901001020    拆分出的第 2 句
...
```

**AskUserQuestion**：确认方案后执行修改。

#### Step 1.3：执行修改

用 Edit 工具逐个替换 ID。同时：
- 拆分超长句子
- 移除纯画面节点的 ID（转为注释）
- 修正跨文件引用

#### Step 1.4：下一个文件

重复 Step 1.1–1.3，直到当前 Loop 所有文件完成。

---

### Phase 2：审查

所有文件修改完成后，执行以下 7 项审查：

#### 审查 A：ID 连续性

- 主线 `001`–`0xx` 无跳号、无重复
- 分支 `1xx`/`2xx`/`3xx` 各段内部连续
- 汇合 `4xx` 段内部连续
- Expose 陷阱 `1xx`–`Nxx` 各段内部连续

#### 审查 B：ID 唯一性

- 同一文件内无重复 ID
- 同一 Loop 跨文件无重复 ID
- 无跨文件引用（如 morrison_001 中不应出现 `901xxxxxx`）

#### 审查 C：字数合规

- 逐句重新计算中文字数
- 确认无超 35 字的台词
- 确认拆分后语义通顺

#### 审查 D：分支/陷阱结构完整

- 每个 `branches` 节点的选项都指向正确的分支 ID
- 每个分支路径末尾有 `→ 汇合至 {4xx ID}`
- 每个 Expose 陷阱路径末尾有 `→ 回到 {Lie 节点 ID}`
- Lie 节点的证据选项都指向正确的陷阱/正确路径 ID

#### 审查 E：get/证词 ID 一致性

- `get` 标记引用的证词 ID 与 state 文件一致
- `Lie` 标记引用的 lie_source 与 state 文件一致
- 证据 ID（正确/陷阱）与 state 文件一致

#### 审查 F：section 头 & 文件名

- 每个 `## Talk:` / `## Expose:` 的文件名与 ID 段匹配
- post_expose 已从 Expose 文件拆出为独立 Talk

#### 审查 G：与 State 对账

- State 中声明的每个 NPC Talk 都有对应的 MD section
- State 中的 expose 有对应的 Expose section
- State 中的 post_expose / interlude 有对应的拆出 Talk section
- 无遗漏、无多余

---

### Phase 2 输出格式

```markdown
## Loop{X} ID 重编审查报告

### 文件清单
| # | 文件 | ID 范围 | 主线句数 | 分支/陷阱句数 | 总句数 |
|---|------|---------|---------|-------------|--------|
| 1 | emma_001.json | 901001001–901001038 | 38 | 0 | 38 |
| ... | | | | | |

### 审查结果
| 项目 | 状态 | 备注 |
|------|------|------|
| A. ID 连续性 | PASS / FAIL | {具体问题} |
| B. ID 唯一性 | PASS / FAIL | |
| C. 字数合规 | PASS / FAIL | {超标句列表} |
| D. 分支结构 | PASS / FAIL | |
| E. get/证词一致 | PASS / FAIL | |
| F. section 头 | PASS / FAIL | |
| G. State 对账 | PASS / FAIL | |

### 变更统计
- 原始 ID 总数：{N}
- 重编后 ID 总数：{M}（+{新增} / -{删除}）
- 拆分句子数：{K}
- 移除纯画面 ID 数：{J}
```

全部 PASS 后，当前 Loop 完成。询问用户是否继续下一个 Loop。

---

## 跨 Loop 注意事项

- NPC 的 `conv` 编号跨 Loop 递增：如 Morrison 在 L1 有 `morrison_001`（Talk）+ `morrison_002`（post_expose），则 L2 的 Morrison Talk 应为 `morrison_003`
- Expose 的 loop 编号对应实际 Loop：L1 = `01`，L2 = `02`，...
- 处理下一个 Loop 前，先确认前一个 Loop 的 conv 编号终止值，避免冲突
