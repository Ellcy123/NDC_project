---
name: episode-consistency-audit
description: "全集一致性审计：事实抽取 → 7 维并行扇出 → 复核 → HTML 报告。一次扫一个 Unit 的全部 Loop，对话/state/角色档案三向对账。token 重投入换准确率。"
argument-hint: "[Unit 号，如 'Unit9'；可选 '--skip-verify' 跳过 Phase 3 复核]"
user-invocable: true
---

# Episode Consistency Audit — 全集一致性审计

把整个 Unit 的对话、state、角色档案做四层对账，输出按严重度排序、可筛选的 HTML 报告。一次跑通常 10–30 分钟、token 重投入换准确率。

**核心理念**：准确率不来自更长的 context，而来自**同一份内容被多个独立视角反复看**——每个 sub-agent 的 context 高度收敛，再用复核 phase 剔除假阳性。

---

## 参数解析

接收：
- `Unit{N}`（必填）—— 如 `Unit9`
- `--skip-verify`（可选）—— 跳过 Phase 3 复核（更快、但假阳性多）

推断 EPI 号：`Unit9 → EPI09`，`Unit3 → EPI03`，依次类推。

---

## Phase 0 — 准备

1. 解析 Unit 号 → EPI 号
2. 创建工作目录：`.audit/{Unit}/{facts,issues,verified}/`
3. 用 Glob 列出对话与设计文件清单（不读内容、只列路径）：
   ```
   AVG/EPI{NN}/Talk/loop*/*.json
   AVG/EPI{NN}/Expose/*.json
   剧情设计/{Unit}/state/loop*_state.yaml
   剧情设计/{Unit}/Characters/*.md
   剧情设计/{Unit}/{Unit}_*.md
   剧情设计/{Unit}/案发时间线与动线.md
   ```
4. 落 `.audit/{Unit}/scope.json`（文件清单 + 时间戳 + Unit/EPI 号）

如果当前 Unit 主要工作还在 MD 草稿阶段（`AVG/对话配置工作及草稿/Unit{N}/Loop*_生成草稿.md`），同时把草稿路径加入清单——大多数审计 agent 应优先读最新版本。

---

## Phase 1 — 事实抽取（5 个 fact-extractor 并行）

事实表是后续所有 phase 的 ground truth。抽取本身就会暴露设计自相矛盾的地方——这些 metadata 也写入最终报告。

并行启动 **5 个通用 Agent（subagent_type: general-purpose）**，使用 `references/fact-extractor-prompts.md` 中对应章节的 prompt。

| 抽取目标 | 输入文件 | 输出 JSON | Prompt 章节 |
|---|---|---|---|
| characters.json | 角色档案 + state 中的 NPC 段 | `.audit/{Unit}/facts/characters.json` | §1 |
| events.json | 案发时间线与动线.md + state 中的事件段 | `.audit/{Unit}/facts/events.json` | §2 |
| items.json | 证据美术需求分类.md + state 中证据段 + ItemStaticData.json | `.audit/{Unit}/facts/items.json` | §3 |
| addressing.json | 角色档案中关系段 + state 中关系演变 | `.audit/{Unit}/facts/addressing.json` | §4 |
| event_perspectives.json | events.json + 每个 NPC 档案的"知情程度" | `.audit/{Unit}/facts/event_perspectives.json` | §5 |

**注意**：event_perspectives.json 的抽取需要先读 events.json，所以**严格说**它依赖于其他抽取的输出。**实际操作**：

- 第一波并行：characters / events / items / addressing（4 个并行）
- 第二波单发：event_perspectives（依赖 events + characters）

抽取出现自相矛盾时**不要"修复"**——保留矛盾并在该字段加 `_conflict` 注释，让审计完整跑完。

---

## Phase 2 — 7 维并行扇出

通过 Agent tool 在**单条消息内**并行启动以下任务（独立 context、互不可见）。每个任务的 prompt 都明确告知 Unit 号 + 输出 jsonl 路径。

### 并行批 A（6 个 agent 同时启动）

| 维度 | subagent_type | 输出 |
|---|---|---|
| D 物证物理属性 | `consistency-checker` | `.audit/{Unit}/issues/D-items.jsonl` |
| C 时间线/跨Loop泄露 | `timeline-auditor` | `.audit/{Unit}/issues/C-timeline.jsonl` |
| X 对话 12 项兜底 | `dialogue-reviewer` | `.audit/{Unit}/issues/X-dialogue12.jsonl` |
| A 人物档案 | `character-fact-auditor` | `.audit/{Unit}/issues/A-character.jsonl` |
| B 称谓 | `addressing-auditor` | `.audit/{Unit}/issues/B-addressing.jsonl` |
| G 多视角 | `multi-perspective-auditor` | `.audit/{Unit}/issues/G-perspective.jsonl` |

每个 agent 的输入 prompt 模板：

```
unit = {Unit}
auditor = {agent name}

工作目录与事实表：
  .audit/{Unit}/facts/

对话文件范围（自行 Glob）：
  AVG/EPI{NN}/Talk/loop*/*.json
  AVG/EPI{NN}/Expose/*.json

State 文件：
  剧情设计/{Unit}/state/loop*_state.yaml

输出（必须落盘）：
  .audit/{Unit}/issues/{对应文件}.jsonl

每行一个 issue，格式见 agent 定义中的"输出"段。
不要修改任何源文件。
```

### 串行批 B：声纹（每 NPC 单跑）

获取该 Unit 的**核心 NPC 列表**（从 characters.json 取所有 NPC 名）。**串行**启动 `voice-print-auditor`，每次 prompt 包含：
- `target_npc = <NPC 姓名>`
- `unit = {Unit}`
- 输出 → `.audit/{Unit}/issues/F-voice-{npc}.jsonl`

为什么串行？每个 voice-print 任务要把该 NPC 全部台词放进单一 context——并行启动会导致每个 sub-agent 重复读取整套对话文件，token 浪费比并发收益高。

### 一次性专项：年代用语审计

启动一次 `narrative-designer`（不新建 agent），prompt：
```
任务：1920s 芝加哥背景对话的年代用语审计
输入：AVG/EPI{NN}/Talk/loop*/*.json + AVG/EPI{NN}/Expose/*.json
重点找：
  - 现代词（"OK"、"压力大"、"信息差"、"反馈"、"沟通"作动词）
  - 技术词（出现 1920s 不存在的科技/概念）
  - 翻译腔（不像 1920s 美国英语翻译过来的中文）
不要评判对话质量、节奏、声纹。
输出 jsonl 到 .audit/{Unit}/issues/E-era.jsonl，格式：
  {"_dim":"E", "file":..., "line_id":..., "speaker":..., "text":..., "type":"modern_word|tech_anachronism|translation_smell", "severity":"P1|P2", "suggestion":...}
```

---

## Phase 3 — 复核（默认开启，--skip-verify 可关）

聚合 `.audit/{Unit}/issues/*.jsonl`，对其中 severity ∈ {P0, P1} 的每条 issue：

1. 读 issue 中的 file + line_id，定位上下文 ±10 句
2. 读相关 fact 条目（按 issue 中引用的 fact 字段）
3. 起一个**新的 general-purpose Agent**，**minimal context**：仅
   - 原 issue（不带其他 issues）
   - 上下文 ±10 句
   - 相关 fact 条目
   - 一句问话："这真矛盾吗？给出 verdict: confirmed | dismissed | needs_human + reason（≤80 字）"
4. 收集 verdict：

| Verdict | 落盘 |
|---|---|
| `confirmed` | `.audit/{Unit}/verified.jsonl`（追加原 issue + verdict 字段） |
| `dismissed` | `.audit/{Unit}/dismissed.jsonl`（保留原 issue + dismissal reason） |
| `needs_human` | `.audit/{Unit}/needs_human.jsonl` |

P2 issue **不进 Phase 3**，直接归入 verified（成本/收益不划算，假阳性也不致命）。

`--skip-verify` 模式下：直接把所有 issue 拷到 verified.jsonl，每条标 `verdict: "unverified"`。

---

## Phase 4 — 聚合 HTML 报告

调用：
```bash
python .claude/skills/episode-consistency-audit/references/build_report.py {Unit}
```

脚本读：
- `.audit/{Unit}/verified.jsonl`
- `.audit/{Unit}/needs_human.jsonl`
- `.audit/{Unit}/dismissed.jsonl`（计入 summary，但默认折叠）
- `.audit/{Unit}/facts/*.json`（用于 issue 详情中展开"违反的事实"）
- `.audit/{Unit}/scope.json`

输出：
- `audit-reports/{Unit}_consistency_{YYYYMMDD}/index.html`
- `audit-reports/{Unit}_consistency_{YYYYMMDD}/styles.css`

报告结构：
- 顶部：扫描范围摘要（多少文件、issue 分级数、事实表清单）
- 一级筛选：严重度（P0 / P1 / P2 / needs_human）
- 二级筛选：维度（A 人物 / B 称谓 / C 时间线 / D 物证 / E 年代 / F 声纹 / G 多视角 / X 对话兜底）
- 三级筛选：Loop（L1–L6）
- 每条 issue 卡片：原台词 + 高亮违规字段 + 违反的 fact 引用 + 修复建议 + dismissal reason（如有）

报告完成后向用户输出 HTML 路径。

---

## 关键原则（写给运行时的自己）

- **每个 Phase 2 agent 的 context 要干净**：只装它需要的事实表 + 全台词，不要塞其他维度的 issue
- **Phase 3 复核 context 要更干净**：只放上下文 ±10 句 + 相关 fact，不带原 issue 的姊妹条目
- **Phase 1 事实表自相矛盾时**：保留矛盾并标记，**不要修复**——这本身就是审计发现
- **不要在 Phase 2 之前提前过滤**：哪怕看起来"明显是误报"，让审计完整跑完，留 Phase 3 决定
- **不要并行 voice-print**：6 个 NPC × 单 context 串行 ≈ 6 次调用，并行的 prompt 重复成本超过并发收益
- **不要伪造完整性**：任一 phase 失败要在报告里明示"此维度未运行/事实表缺失"，不要假装全跑通

---

## 失败兜底

- 任一 Phase 1 抽取失败 → 主 orchestrator 标记该事实表 `missing`，对应 Phase 2 agent 跳过并在报告中标"缺事实表"
- 任一 Phase 2 agent 失败 → 报告中该维度标"未运行"，**不阻塞其他维度**
- Phase 3 复核失败 → 该 issue 留在 needs_human
- build_report.py 失败 → 退而输出 `.audit/{Unit}/MERGED_ISSUES.md`（纯文本汇总）

---

## 不要做的事

- 不要在 Phase 1/2 之间帮 agent "整理" 输出格式——固定 jsonl 协议
- 不要把 fact 表写到 `剧情设计/` 下污染设计目录——一律落 `.audit/`
- 不要修改原对话/state/档案文件
- 不要跑完写一句"基本没问题"就收工——必须出 HTML 报告
- 不要把 dismissed.jsonl 直接丢掉——默认折叠展示，让用户能复审 Phase 3 是否过度宽容

---

## 调用示例

```
/episode-consistency-audit Unit9
/episode-consistency-audit Unit9 --skip-verify
```

---

## 与既有 skill 的边界

- 与 `/playthrough-audit` 不重叠：playthrough 关心**玩家体验**（推理路径、信息获取节奏、谜题手感），本 skill 关心**事实/称谓/声纹的内部一致性**——是底层工艺审计
- 与 `/team-dialogue` / `/team-loop` 不重叠：那些是生产流水线，本 skill 是 QA 流水线
- 与 `consistency-checker` / `timeline-auditor` / `dialogue-reviewer` 单 agent 调用不重叠：本 skill 是**编排**这些 agent + 加 4 个新维度 + 加复核 + 出 HTML，单 agent 调用仍可独立使用
