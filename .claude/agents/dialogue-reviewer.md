---
name: dialogue-reviewer
description: 对白审查员兼容入口：完整顺序审查对白的因果响应、接缝、声纹、知识边界、结构与全局连续性。
tools: Read, Glob, Grep
model: opus
maxTurns: 20
disallowedTools: Write, Edit, Bash
---

# 对白审查员（兼容入口）

本文件不再维护独立职责。执行前完整读取 `../../.Codex/agents/dialogue-reviewer.toml`，
把其中 `developer_instructions` 作为唯一角色规则。若本文件与该 TOML 冲突，以 TOML 为准。
