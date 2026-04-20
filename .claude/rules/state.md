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

## 历史格式兼容（EPI01 / Unit2）

EPI01 Unit2 state 文件是早于本规则定稿的历史产物，允许保留以下旧格式，**不强制回溯修改**：

| 字段 | EPI01(Unit2) 旧格式 | EPI02+ / Unit8+ 新格式（当前规则） |
|------|--------------------|----------------------------------|
| NPC 知识块 | `knows` / `does_not_know` / `lie` | `active_topics` / `withheld_topics` |
| `doubts.unlock_condition` | 字符串 `"item:xxx + testimony:yyy"` | 结构化数组 `[{type: 1/2/3, param: "xxx"}, ...]` |
| `opening` 子字段 | `scene_id` / `characters` / `purpose` | `type` / `description`（+ 可选 scene_id/characters） |
| `evidence` 子字段 | `id` / `name` / `note` | 增补 `type` / `pickup` / `analysis` / `description` |
| `evidence_registry` 顶层块 | 无 | 有（Loop 级证据汇总，可选） |

**处理原则**：
- **读 Unit2 旧格式**：agent 解析时自动识别——如果 NPC 块含 `knows`/`does_not_know`/`lie` 则按旧格式走；如果 `unlock_condition` 是字符串则按 `+` 分隔解析 `type:param` 对
- **写新 Unit（Unit8+）**：一律用新格式
- **Unit2 未来若新增 loop**：建议用新格式，但与旧 loop 混存可接受
- **配置表生成**：DoubtConfig 运行时就是结构化数组，Unit2 字符串格式需经转换脚本；Unit8+ 新格式零转换直接映射
