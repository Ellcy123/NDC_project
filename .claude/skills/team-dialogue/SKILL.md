---
name: team-dialogue
description: "对白撰写 skill：从 Manifest 指定的大纲、定稿 State 与既有成稿建立剧情因果和连续性合同，按连续场景包生成并审查正式中文对白 MD 草稿。"
argument-hint: "[state 文件或目录路径]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# 对白撰写 Skill（兼容入口）

本文件不再维护一套独立规则。执行前必须完整读取并严格遵守：

`../../../.agents/skills/team-dialogue/SKILL.md`

该文件是唯一权威，包含剧情因果—人物选择卡、信息响应、连续场景包、Talk
分支、Zack 知识边界、逐场成稿审查和内容总监闸门。若本入口与权威文件冲突，
一律以 `.agents/skills/team-dialogue/SKILL.md` 为准。
