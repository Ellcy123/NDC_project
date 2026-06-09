# Unit 内容设计工作流程规范

适用于 NDC 项目单个 Unit（章节）从大纲到预览落地的全流程。
基于 Unit9 实战路径整理，作为后续 Unit 的标准操作流程。

---

## 总览

```
阶段 1  大纲              → Unit{N}_大纲.md
         ↓
阶段 2  state + 角色 + 场景空间（三轨并行）
         ↓
阶段 3  对白草稿（Loop 顺序推进，MD 草稿）
         ↓
阶段 4  润色 + 人设/state 反向迭代
         ↓
阶段 5  证据稳定 → 小玩法 → 证据/场景美术清单
         ↓
阶段 6  JSON 落地（对白+配置表）+ 预览部署
         ↓
阶段 7  一致性审计 + 全流程体验审计
```

**关键认知**：
- 阶段 2-5 不是严格瀑布，是螺旋——写对白时回头改 state 是常态。
- 小玩法**必须**等证据 ID 稳定后再做，否则反复重写。
- 美术对接清单是**最末**才整合的，不要早做。
- 预览不是最后一步——配置表在 `avg_editor_v2` 上边写边验证，只是最终整合落在阶段 6。

---

## 阶段 1：大纲

**目标**：产出 `剧情设计/Unit{N}/Unit{N}_大纲.md`，确立 6 个 Loop 的起承转合骨架。

**产出**：
- `Unit{N}_大纲.md`（核心剧情、Loop 划分、关键转折、谁是凶手、各 Loop 揭示哪一层真相）
- `Unit{N}_时代细节补充.md`（如 1920s 芝加哥背景，可选）
- `案发时间线与动线.md`（凶案当晚物理时间线）

**可用 skill**：
- `narrative-guide` — 叙事引导师，基于专业叙事理论逐步审视情节框架
- `episode-outline-generator` — 大纲生成器
- `episode-story-extractor` — 故事提取器（已有材料时反向整理）

**注意事项**：
- 大纲数次迭代是正常的（Unit9 经历 5 轮）。
- **疑点不写独立文档**——直接合并进后续 state（Unit9 早期有独立 `疑点设计.md`，后来 `3c27db3` 整体删除）。
- 大纲写作风格（用户反馈）：**结构第一**，对白只写关键的（指证击穿/反转锚点/情感爆点），普通过场用一两句概括。

**举例**（Unit9 实际路径）：
```
fe2d3bd  大纲更新
c013a9f  1920s 时代细节补充
bada565  时代质感细节落地
339a81e  补回隐藏线索章节
```

---

## 阶段 2：state + 角色 + 场景空间（并行三轨）

**目标**：把大纲转化为可执行的数据骨架——每个 Loop 有完整 state、每个角色有档案、每个场景有空间布局。

**产出**：

| 轨道 | 路径 | 文件 |
|------|------|------|
| state | `剧情设计/Unit{N}/state/` | `loop1_state.yaml` ~ `loop6_state.yaml` |
| 角色 | `剧情设计/Unit{N}/Characters/` | 每个 NPC 一个 `.md`（Unit9 共 10 个） |
| 场景 | `剧情设计/Unit{N}/场景/` | 每个调查场景一个 `.md`（Unit9 共 18 个） |

**可用 skill**：
- `unit-state-generator` — **首选**。大纲 → 4-agent 团队讨论 → 6 个 state 文件 + 风险点清单。
- `team-loop` — 整 Loop 端到端编排（证据→指证→state→对话→审查），适合从零做整个 Loop。
- `team-design` — 单场景/单 NPC 中等复杂度任务。
- 直接调 agent：`state-architect`（场景编排+证据分配+知识边界）、`evidence-designer`（证据链+ID 编码）、`expose-designer`（指证谜题）。

**注意事项**：
- **角色档案聚焦人设**（用户反馈）：只写弧光/立场/作用，不复述剧情事件。
- **疑点解决是二元的**（用户反馈）：描述疑点状态只用"已解决/未解决"，不写"部分解决"。
- 空间布局可能要重构（Unit9 `ae84903` 整体重构过一次）。
- 证据 ID 编码：EPI09 = 9xxx，loop1=91xx，loop2=92xx……派生证据 97xx。

**举例**：
```
adc0de3  state-to-table skill 引入
06d20f3  大纲疑点逻辑修正 + state-to-table 三段式重构
ae84903  空间布局重构
6db6c46  角色文档初版
f2a1a09  角色文档重写 + 9506 生锈弹壳 + 基础设计文件入库
```

---

## 阶段 3：对白草稿（Loop 顺序推进）

**目标**：state 定稿后逐 Loop 写对白 MD 草稿。**严格 MD 优先**，不碰 JSON。

**产出**：
- `AVG/对话配置工作及草稿/Loop{1-6}_对话草稿.md`
- 或新格式：直接在 `AVG/EPI{NN}/Talk/loop{X}/` 下分文件起草（Unit9 后期改用此结构）

**可用 skill**：
- `team-dialogue` — **首选**。State 已定稿，整 Loop 补对白：两策划讨论 → dialogue-writer 执笔 → 审查 → 内容总监拍板。
- `team-expose` — 完整指证设计流程（谜题方案→state 写入→对话生成→全面审查）。
- 直接调 agent：`dialogue-writer`（执笔）、`dialogue-reviewer`（12 项审查清单）、`voice-print-auditor`（单角色声纹一致性）。

**注意事项**：
- **Phase 1（MD）和 Phase 2（JSON）严格分开**。本阶段只产 MD，绝不动 JSON。
- 修改对白前必读对应章节设计文档，绝不凭记忆编。
- 17 条对话设计规则见 `.claude/rules/dialogue.md`（编辑对应路径文件时自动加载）。
- 一开始可能只做 1 个 Loop 试水（Unit9 从 `778dfb0` Loop1 草稿起步）。

**举例**：
```
778dfb0  Loop1 对话草稿 + AVG 目录重构
fdf3255  state 证词清理（13 处）+ Loop1 对话草稿
6e2f566  Loop1-4 对话/state、Loop5-6 润色版
```

---

## 阶段 4：润色 + 人设/state 反向迭代

**目标**：写对白时发现的人设/逻辑问题，反推回 state 和角色档案做同步修正。**这一阶段是螺旋的，不要试图一次性写完阶段 3 再开始**。

**典型反向修正**：
- 大设定转向（Unit9 `2f015e7`：Webb 从"保镖+继承"改为"遗嘱执行人+slayer rule"）
- 全局重命名（Unit9 `a5b46ac`：Jimmy → James）
- 配角加回/加戏（Unit9 `f28c386`：Mrs.Morrison 加回 + Whale 多句台词）
- 单 Loop 重构（Unit9 `7817171`：Loop3 加 Vivian 共情 + Loop5 §1 重构为纯情绪戏）

**可用 skill**：
- `episode-consistency-audit` — 全集一致性审计，事实抽取 → 7 维并行审计 → HTML 报告。
- 直接调 agent：`character-fact-auditor`（人物档案对账）、`multi-perspective-auditor`（同事件跨 NPC 一致性）、`addressing-auditor`（称谓审计）、`timeline-auditor`（时序+跨 Loop 信息泄露）。

**注意事项**：
- 修改 state 后，**相关 Loop 的对白要回头扫一遍**（用 grep 搜旧设定关键词）。
- 人设细节调整后，已落地的 NPC 文档要同步（Unit9 `7462fa0` "对话润色版落地 + state/证据/角色文档同步更新"是一次性整理的典范）。

**举例**：
```
2f015e7  设计转向：Webb 委托从"保镖+继承"改为"遗嘱执行人+slayer rule"
a5b46ac  全局重命名：Jimmy → James / 吉米 → 詹姆斯
7462fa0  对话润色版落地：Loop1-6 原版替换为润色版 + state/证据/角色文档同步更新
```

---

## 阶段 5：证据稳定 → 小玩法 → 美术清单

**目标**：证据 ID 不再大改后，做小玩法和美术对接清单。

**产出**：

| 内容 | 路径 | 说明 |
|------|------|------|
| 小玩法 | `剧情设计/Unit{N}/小玩法/` | 每个分析/合成证据一个 MD（Unit9 L1-L4 各 1 个） |
| 证据美术分类 | `剧情设计/Unit{N}/Unit{N}_证据美术需求分类.md` | 按类型分组 |
| 场景美术分类 | `剧情设计/Unit{N}/Unit{N}_场景美术需求分类.md` | 按场景分组 |
| 动态漫画需求 | `剧情设计/Unit{N}/Unit{N}_证物出示动态漫画美术需求.md` | 指证回放/关键镜头 |
| 美术对接整合 | `剧情设计/Unit{N}/Unit{N}_AVG美术对接整合清单.md` | **最终交付给美术**的合并清单 |
| 人物调度清单 | `剧情设计/Unit{N}/Unit{N}_AVG人物调度美术清单.md` | 每场每个角色立绘需求 |
| 美术资源复用 | `剧情设计/Unit{N}/Unit{N}_美术资源复用与补画清单.md` | 跨 Unit 复用统计 |

**可用 skill**：
- 暂无专门 skill，按文档模板手工产出。
- 可调用 `narrative-designer` agent 辅助构图描述。

**注意事项**：
- **小玩法必须等证据 ID 稳定**——Unit9 L1-L4 有小玩法文件（`6e2f566` 落地），L5-L6 没做（需要确认是否补）。
- **动态漫画构图建议**（用户反馈）：必须写明构图机位/画面内/画面外/视觉重点，**不能用全景对比描述**——动态漫画只展示一个局部。
- 美术对接清单是**最末整合**，不要在阶段 3 就做——Unit9 `ba02a57`（最近一次 commit）才整合。

**举例**：
```
6e2f566  Loop1-4 对话/state、Loop5-6 润色版、证据美术分类、小玩法设计（首次出现）
ba02a57  对白与 state 整合 + 美术对接清单
```

---

## 阶段 6：JSON 落地 + 预览部署

**目标**：把 MD/YAML 转成 Unity 工程可读的 JSON，并在 `avg_editor_v2/` 网页验证。

**两条独立数据流**：

### 6.1 对白：MD → JSON

```
AVG/对话配置工作及草稿/Loop{X}_对话草稿.md
  → AVG/EPI{NN}/Talk/loop{X}/*.json
  → AVG/EPI{NN}/Expose/Loop{X}_{npc}.json
```

**可用 skill**：
- `dialogue-id-reorder` — 对话 ID 连续化、拆长句、修分支/陷阱段。
- `dialogue-md-to-json` — 三段式：LLM 跨表预检 → py dry-run → 用户确认后写入。

**命令**：
```bash
cd AVG/对话配置工作及草稿
python sync_to_json.py Loop{X}_对话草稿.md --dry-run  # 预览
python sync_to_json.py Loop{X}_对话草稿.md            # 执行
python sync_to_json.py --all                          # 全量
python extract_to_md.py                               # 反向验证往返一致性
```

### 6.2 配置表：在 avg_editor_v2 上维护

```
avg_editor_v2/data/table/{表名}.json（编辑器副本，真相源；初始从 Unity seed）
  → 用 /config-edit skill 精改（单条 / 字段级）
  → 手动 copy 到 D:\NDC\Assets\table\
```

配置表不再从 state YAML 批量生成（旧 `state-to-table` 已退役）。state YAML 是设计层源，配置表改动直接在 avg_editor_v2 上做。

**可用 skill**：
- `config-edit` — 改 avg_editor_v2/data/table 的配置表：定位表/字段、连带改关联表、改前阐述、改后基线自校验。

### 6.3 预览部署

```bash
cd avg_editor_v2 && python server.py   # 本地预览 / 编辑器
```

线上部署到 Vercel（`vercel.json` 根路由 → `avg_editor_v2/index.html`）。

**注意事项**：
- **ID 重编排在生成 JSON 前做**（Unit9 `b6e1ad7` "全章对话 ID 重编排 + JSON 生成 + 预览部署"是一次完成的）。
- JSON 落地后发现的问题，**修改 MD 后重新 sync**，不要直接改 JSON。
- 同步到 D:\NDC：`copy /Y "D:\NDC_project\avg_editor_v2\data\table\*.json" "D:\NDC\Assets\table\"`

**举例**：
```
1abe679  EPI09 起步（开始写 JSON）
b6e1ad7  全章对话 ID 重编排 + JSON 生成 + 预览系统部署
89b3e02  L1-L4 分析派生证据落地 + 配置表/对话同步
4fa02ab  全章对白同步
```

---

## 阶段 7：审计

**目标**：JSON 落地后做整体校验，发现遗漏的逻辑/一致性/体验问题。

**可用 skill**：
- `episode-consistency-audit` — 全集一致性审计。事实抽取 → 7 维并行扇出 → 复核 → HTML 报告。
- `playthrough-audit Unit{N}` — 全流程体验审计。AI 模拟玩家走完整流程，~15 分钟，输出包含证据链路图、玩家风险点、问题明细的交互式 HTML 报告。

**典型问题类型**：
- 跨 Loop 信息泄露（`timeline-auditor`）
- 同事件跨 NPC 描述不一致（`multi-perspective-auditor`）
- 玩家无法触达某证据（`player-simulator` / `player-advocate`）
- 单角色声纹漂移（`voice-print-auditor`）
- 称谓不符合关系状态（`addressing-auditor`）

**注意事项**：
- 审计 agent 缺乏游戏机制理解（feedback memory 记录），需要在 prompt 里附加系统文档，并加 pre-HTML 验证阶段。

---

## 附录 A：什么时候用整体编排 skill，什么时候用单 agent

| 任务规模 | 推荐方式 |
|---------|---------|
| 单场景/单 NPC 设计 | `team-design` |
| State 已定稿，整 Loop 补对白 | `team-dialogue` |
| 完整指证设计 | `team-expose` |
| 整个 Loop 从零规划（证据→指证→state→对话→审查） | `team-loop` |
| Unit 大纲 → 6 个 state 文件 | `unit-state-generator` |
| 改配置表（非 Talk/Expose） | `config-edit` |
| 对白 MD → JSON | `dialogue-md-to-json` |
| 全流程体验审计 | `playthrough-audit Unit{N}` |
| 简单改文案/小修 | 不开 team，直接做 |

## 附录 B：核心数据约束

- **证据 ID**：EPI{NN} = N×1000 起，loop{X} = NX×100 起，派生证据 N7xx
- **对话 ID**：9 位 `{loop}{scene}{sequence}`，例：105001005
- **证词 ID**：7 位 `{loop}{npc}{sequence}`，例：1031002
- **每场景/NPC 承载 1-3 个核心信息点，不超过 3 个**
- **每 Loop 只揭示一层真相**
- **疑点解锁推荐**两种不同来源交叉验证，但单件强证据也允许（2026-04-22 规则放宽）

## 附录 C：三大原则（高于一切具体规则）

1. **悬疑感优先**——绝不提前破梗。藏梗 > 明示。
2. **信息严密性**——零矛盾、零漏洞。物理属性前后一致，证词与摘要信息密度对等。
3. **逻辑闭环**——每个谜题严密指向 + 多方暗示。谎言措辞精确匹配证据维度。

详见 `CLAUDE.md` "游戏设计三大原则" 章节。
