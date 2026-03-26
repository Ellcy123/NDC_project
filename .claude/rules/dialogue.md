---
paths:
  - "AVG/**"
  - "**/对话草稿*"
---

# 对话规则

## 两阶段流程
- **Phase 1**：只修改 MD 草稿，不碰 JSON
- **Phase 2**：用户明确指示后才执行 sync_to_json.py 同步到 JSON
- 绝不凭记忆编写剧情细节——先读设计文档

## 分支规则
- 每组分支选项必须指向不同信息维度（身份/关系、时间线、事件/线索、情绪/态度、背景/环境）
- 不同分支路径允许独占 get 获取（证据/证词/时间线标记）
- 态度分支：核心信息（keyInfoType/keyInfoContent）相同，NPC 反应/语气不同
- 所有分支最终汇合到同一节点，禁止永久分叉
- Repeat 对话中的分支应指回首次对话的分支路径

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
