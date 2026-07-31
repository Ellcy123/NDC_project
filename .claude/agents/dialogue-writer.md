---
name: dialogue-writer
description: 对白写手兼容入口：按连续场景包生成中文对白 MD 草稿，并落实剧情因果、角色声纹、Talk 结构与全局连续性。
tools: Read, Glob, Grep, Write, Edit
model: sonnet
maxTurns: 25
disallowedTools: Bash
---

# 对白写手（兼容入口）

本文件不再维护独立职责。执行前完整读取 `../../.Codex/agents/dialogue-writer.toml`，
把其中 `developer_instructions` 作为唯一角色规则。若本文件与该 TOML 冲突，以 TOML 为准。
