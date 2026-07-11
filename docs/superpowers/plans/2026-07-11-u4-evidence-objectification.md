# Unit4 Evidence Objectification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 Unit4 主准大纲中约三分之一的报告、纸条和零散文件改成可观察、分析或组合的实物证据，同时保持原有指证结论与信息边界。

**Architecture:** 只修改一份主准大纲。按 Loop 分批替换证据名称、获取交互、指证表和后续引用；现有正式文书继续承担法律与组织证明，实物承担物理事实。

**Tech Stack:** Markdown、`rg` 文本一致性检查、Git diff。

## Global Constraints

- 主准文件：`剧情设计/Unit4/Unit4_大纲0710_逻辑重构版_v2.md`。
- 设计规范：`docs/superpowers/specs/2026-07-11-u4-evidence-objectification-design.md`。
- 不修改 state、table、AVG 或既有 Item ID。
- 不改变五个 Loop、指证对象、谎言维度和 U4→U5 边界。
- 不自动提交 Git；仓库已有用户确认的 Unit4 备份移动。

---

### Task 1: 修改 Loop 1–2 的报告型证据

**Files:**
- Modify: `剧情设计/Unit4/Unit4_大纲0710_逻辑重构版_v2.md:122`

**Interfaces:**
- Consumes: L1 Harrison 调查链、L2 Whitfield 三轮指证。
- Produces: 现场弹道实物、自首证物箱、红线注射器、分析药瓶、问题药剂和封签组。

- [ ] **Step 1:** 把 `弹道初步`改为现场弹道实物与分析结论。
- [ ] **Step 2:** 用`Harrison 未完成的自首证物箱`替换`最后工作顺序表`，保留箱内正式文书名称。
- [ ] **Step 3:** 把 L2 剂量卡、剩余量鉴定、化验报告、封签对照替换为红线注射器与十三日封签药盒、分析药瓶、问题药剂和实体封签组，并补齐两只死亡病例空瓶的取得节点。
- [ ] **Step 4:** 同步修改 Whitfield R1–R3 指证表和上下文引用。
- [ ] **Step 5:** 运行 `rg -n '弹道初步|最后工作顺序表|每日剂量卡|剩余量鉴定|药剂化验报告|批次封签对照' 剧情设计/Unit4/Unit4_大纲0710_逻辑重构版_v2.md`；预期不再出现作为现行证据的旧名称。

### Task 2: 修改 Loop 3 的现场物证

**Files:**
- Modify: `剧情设计/Unit4/Unit4_大纲0710_逻辑重构版_v2.md:383`

**Interfaces:**
- Consumes: Morrison 当夜时间线、Doris R3、爆炸前搜证。
- Produces: 磨号手枪与余弹、黄铜寄存柜钥匙、伪造铅封与定时引燃器。

- [ ] **Step 1:** 把配枪初检改成玩家直接分析枪与未击发余弹。
- [ ] **Step 2:** 把领取凭条改成 Doris 缝纫盒里的 214 号黄铜钥匙观察，补车站值班行李员核实证词，并同步当夜时间线、R3、指证后授权带走钥匙和 L3 结尾。
- [ ] **Step 3:** 把检修卡证据改成爆炸前拍摄的伪造市政煤气铅封与异常时钟接线、爆炸后回收的耐火接点，保留 18:12 Doris 证词且不赋予玩家可拆弹能力。
- [ ] **Step 4:** 运行 `rg -n '配枪与弹药初检|领取凭条|伪造煤气检修卡' 剧情设计/Unit4/Unit4_大纲0710_逻辑重构版_v2.md`；预期无旧证据残留。

### Task 3: 回收 Patrick 遗物匣并修改 Loop 5 书写者证明

**Files:**
- Modify: `剧情设计/Unit4/Unit4_大纲0710_逻辑重构版_v2.md:702`

**Interfaces:**
- Consumes: 现有 EPI02 物件 2107、L4 Margaret R3、L5 密码与操作簿书写者链。
- Produces: Patrick 遗物匣主题物件、密码 `FTMWPTF`、Mickey 定制钢笔证明链。

- [ ] **Step 1:** 用 Patrick 遗物匣归并遗物封袋、童年练习本和残页；明确刻句在 U2 只作环境信息、L4 才进入推理链，并保留清场补充记录的独立证明责任。
- [ ] **Step 2:** 把匣身刻句统一为 `FOR THE MANY WE PAY THE FEW`，同步 L4 复审触发、L5 动机、密码说明、Mickey 进场反应及后续引用。
- [ ] **Step 3:** 把 Mickey 日常工作笔记改成定制钢笔与法人卷宗已知批注，更新书写者一致性组合。
- [ ] **Step 4:** 运行 `rg -n 'FTMTFMP|few must pay|童年练习本|残页|遗物封袋|Mickey 日常工作笔记' 剧情设计/Unit4/Unit4_大纲0710_逻辑重构版_v2.md`；预期旧版本引用为零。

### Task 4: 全章逻辑与格式验证

**Files:**
- Verify: `剧情设计/Unit4/Unit4_大纲0710_逻辑重构版_v2.md`

**Interfaces:**
- Consumes: Tasks 1–3 的全部修改。
- Produces: 无残留旧名称、无时序倒挂、无 U5 破梗的最终大纲。

- [ ] **Step 1:** 逐项核对 L2、L3、L4 指证表中的材料均在指证前出现。
- [ ] **Step 2:** 运行 `rg -n 'FTMWPTF|Patrick 遗物匣|红线刻度注射器|黄铜寄存柜钥匙|定时引燃器|Mickey 定制钢笔' 剧情设计/Unit4/Unit4_大纲0710_逻辑重构版_v2.md`，确认新证据的首次出现和后续回收。
- [ ] **Step 3:** 运行 `git diff --check`；预期无空白错误。
- [ ] **Step 4:** 运行 `git diff -- 剧情设计/Unit4/Unit4_大纲0710_逻辑重构版_v2.md`，确认没有修改 Loop 数量、指证对象、人物责任或 U4→U5 结论。
