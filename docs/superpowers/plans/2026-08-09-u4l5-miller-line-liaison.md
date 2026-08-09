# U4L5 Miller Line Liaison Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 Miller 当夜专线联络人的最小人物档案，解除 U4L5 `team-dialogue` 的 speaking character 声纹门禁。

**Architecture:** 只新增一份功能型人物档案，沿用 Unit4 现有轻量人物档案结构。档案只约束当夜电话中的叙事功能、声音和知识边界，不修改 active outline、Loop5 State、场景文档或 AVG 草稿。

**Tech Stack:** Markdown、`rg`、Git diff 检查。

## Global Constraints

- 来电者匿名、仅声音、只服务 U4L5 本场。
- 不配置姓名、性别、年龄、立绘、私人经历或 Unit5 再出场承诺。
- 电话条件必须与 active outline 和 Loop5 State 一致。
- 不使用现代客服话术或黑帮式恐吓。
- 此次不修改 active outline、Loop5 State、场景文档或 AVG 对白草稿。

---

### Task 1: 新增 Miller 当夜专线联络人人物档案

**Files:**

- Create: `剧情设计/Unit4/人物设定/miller_line_liaison.md`
- Reference: `docs/superpowers/specs/2026-08-09-u4l5-miller-line-liaison-design.md`
- Reference: `剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md`
- Reference: `剧情设计/Unit4/state/loop5_state.yaml`

**Interfaces:**

- Consumes: active outline 中“Miller 的最后条件”、Loop5 State 的 `miller_final_condition`、已批准的声音样张。
- Produces: `team-dialogue` 可直接读取的身份、声纹、知识边界和设计禁区。

- [ ] **Step 1: 新增人物档案**

写入五部分：权威依据与适用边界、基本信息、声音风格与交互姿态、知识边界、设计边界。声音样张固定为：

```text
“楼下的车已经到了。把保险档案交给司机，您一个人上车。”
“Brennan 先生可以离开。档案不能带走。您的律师身份暂时保留。”
```

- [ ] **Step 2: 校验关键条件覆盖**

运行：

```bash
rg -n '楼下的车|保险档案|一个人上车|Brennan 先生|档案不能带走|律师身份暂时保留' 剧情设计/Unit4/人物设定/miller_line_liaison.md
```

预期：六项条件全部命中。

- [ ] **Step 3: 校验越界内容与格式**

运行：

```bash
rg -n 'Sean|水源|小 Charles|Unit5|客服|威胁|立绘' 剧情设计/Unit4/人物设定/miller_line_liaison.md
git diff --check
```

预期：相关词只出现在明确的禁止或否定边界中；`git diff --check` 无输出。

- [ ] **Step 4: 对照真源复核**

逐项确认档案没有改变以下既定事实：车辆已准备、档案交给楼下司机、Mickey 独自上车、暂时保留律师身份、Zack 可离开但不能带走档案。

- [ ] **Step 5: 提交人物档案**

```bash
git add 剧情设计/Unit4/人物设定/miller_line_liaison.md
git commit -m "docs: add U4L5 Miller line liaison profile"
```
