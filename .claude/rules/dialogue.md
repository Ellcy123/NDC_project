---
paths:
  - "AVG/**"
  - "**/对话草稿*"
---

# 对话规则

## 两阶段流程
- **Phase 1**：只修改 MD 草稿，不碰 JSON
- **Phase 2**：Unit1 仅在用户明确指示后执行 `AVG/Tools/sync_unit1_script_to_json.py --write`，且只回写本地 EPI01 的 Words；其他 Unit 使用各自专用同步器
- 绝不凭记忆编写剧情细节——先读设计文档

## 分支规则
- 普通问答分支只用于 `scenes[].npcs` 自由探索 Talk；Opening、场景级强制 Event、post-expose、`ending_sequence` 禁止普通分支，其中的证词沿固定剧情线性获取
- 自由探索 Talk 只有一个有效信息方向时可使用线性 Talk，不得制造单选项假分支
- 使用 `@branch` 时必须有 2-3 个有效选项
- 每组分支选项必须指向不同信息维度（身份/关系、时间线、事件/线索、情绪/态度、背景/环境）
- 自由探索证词既可在线性主干获取，也可在不同分支路径内获取
- 自由探索分支不是内容层面的永久互斥选择；玩家在完整探索/回访中可以走到全部路径，不得因 get 位于某条路径就判定永久漏取
- 态度分支：核心信息（keyInfoType/keyInfoContent）相同，NPC 反应/语气不同
- 所有分支最终汇合到同一节点，禁止永久分叉
- Repeat 对话中的分支应指回首次对话的未走路径，负责完整探索中的后续可达性

## 信息获取
- 证据有直接获取（对话 get / 场景点击）和派生获取（分析/合成）两层
- 每个场景/NPC 承载 1-3 个核心信息点，不超过 3 个
- keyInfoType 标记必须准确：timeline（时间线）/ statement（陈述）/ identity（身份关系）
- 两次 `get` 之间至少间隔 3-5 句普通对话

## ID 格式
- 对话 ID：9 位数字 `{loop}{scene}{sequence}`
- 证词 ID：7 位数字 `{loop}{npc_code}{sequence}`

## 指证相关
- Expose 第一个 Lie 必须对应 Talk 中已收集的证词
- 后续 Lie 是嫌疑人被逼出的新谎言（止损式），不是 Zack 喂话
- 谎言由嫌疑人主动说出，不是被动否认

## 视频路径
- videoEpisode = 章节标识（EPI01/EPI02/EPI03）
- videoLoop = 循环标识（loop1-loop6）
- videoScene = 对话文件名（不含 .json）
- videoId = 对话 ID
