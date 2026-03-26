---
paths:
  - "**/state/**"
  - "**/前置配置/**"
  - "**/loop*_state*"
---

# State 文件规则

## 三阶段分离
State 文件中的内容严格分为三个阶段，不可混合：
1. **Opening**（硬切/脚本）：Zack 观察，无玩家选择
2. **Scenes**（🔓自由探索）：玩家自由探索、收集证据、与 NPC 对话
3. **Expose**（直接对决）：线性递进的指证

## NPC 条目必填
每个 NPC 必须包含 4 个块：
1. **已知信息**：active_topics（可谈话题）/ withheld_topics（保留话题）
2. **玩家询问意图**：player_inquiry，格式 `"{驱动信息来源}" # {分数 0-10}`
3. **可提取证词**：testimony_ids，标注 ⚠谎言 / ⚠偏见
4. **鉴赏力**：source / quiz 节点引用

## 格式规范
- Testimony ID：7 位数字 `{loop}{npc_code}{sequence}`
- Player inquiry：`"{驱动信息来源}" # {分数 0-10}`
- Expose 对象：`is_liar: true`, `player_inquiry: null`
- Evidence note：`关键——{用途}` / `场景道具` / 空

## 信息控制
- NPC 可说个人经历，不可说 Expose 结论
- NPC 不可泄露 blind_spot 信息
- active_topics 只包含本 Loop 应揭示的信息
- withheld_topics 覆盖后续 Loop 才揭示的内容
- validation_status 必须为 PASS 才可进入对话生成
