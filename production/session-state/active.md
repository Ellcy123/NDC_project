# Active Session

## 当前任务
工作流架构升级 — agents/rules/skills/hooks 体系建设

## 进度
- [x] Step 1: 创建 10 个 agent 定义文件
- [x] Step 2: 创建 6 个 path-scoped rules 文件
- [x] Step 3: 创建 3 个 team skill 文件
- [x] Step 4: CLAUDE.md 瘦身
- [x] Step 5: 创建 hooks 脚本
- [x] Step 6: 创建 session state 机制

## 关键决策
- Agent 架构采用三层结构：Director (Opus) → Designers (Sonnet) → Reviewers (Opus/Sonnet)
- 对话17条规则外移到 .claude/rules/dialogue.md，CLAUDE.md 只保留引用
- Agent Team 编排规则由 agent 定义 + team skill 替代
