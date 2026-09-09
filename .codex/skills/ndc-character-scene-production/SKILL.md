---
name: ndc-character-scene-production
description: 用 Terra 极高智能接收已通过的 NDC 整场景深与白模方案，完成正式角色生成、提取、接触合成、全场验收和图层交付。用于 Astra 参考阶段交接后的生产及有限返修；不重新设计整场参考，不按角色拆任务。
metadata:
  category: art/character/scene-production
---

# 人物入景：正式资产生产

接收已确定的整场白模后，本阶段全权承担后续生产与交付：自行生成完整角色，按冻结白模校正位置、整体大小、头身比、动作和遮挡，自行完成技术/视觉自检、提取合成及必要返修。比例对齐属于本阶段职责，不要求参考任务持续监控、复核或代修；按白模纠正生成偏差不属于重设参考。仅在白模自身核心关系错误且必须改变已确定方案时，附明确证据回传参考返修。下游自行登记结果并接续已就绪场景，不等待上游逐步批准。

白模顺序：初次生成时包括隐藏部位的完整人体，保留未裁剪母层；随后按真实遮挡关系裁剪派生层或制作蒙版，审核裁剪后的场景参考。正常裁剪不算缺失，不要求补回场景中本应被遮住的像素；小瑕疵容错不取消初始完整生成。正式角色同样先生成完整母层再应用遮挡。

执行前读[对话任务独立额度](references/task-budget.md)：新对话完整新额度，其他对话的资产历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于旧预算说明。

执行模型固定为 `gpt-5.6-terra`，`thinking: xhigh`。由 [参考协调任务](../ndc-character-scene-reference/SKILL.md) 通过实际任务工具指定。引用 [入景共享规则](../ndc-character-scene-integration/SKILL.md) 和 [入景阶段交接](../ndc-art-stage-pipeline/references/integration-pipeline.md)，先claim唯一场景，检查原来源、完整范围、pre-generation ledger和剩余次数。旧任务或重复消息不得重复领取或重开生产。

读取 [制作节奏](../ndc-character-scene-integration/references/production-cadence.md) 及 [完整流程](../ndc-character-scene-integration/references/full-workflow.md) 从“Actual generation handoff”到最终交付；不要从需求盘点重跑参考阶段。

- 全场按原远近层次、完整角色和交互单元生产，始终回到同一完整场景判断。保持各状态角色联动，不能拆成互不知情的角色任务。
- 遵守[白模放行与正式完整性](../ndc-character-scene-integration/references/whitebox-acceptance.md)：已放行的小型遮挡/缺失不退回参考。实际提示词要求同姿势、位置、比例和头身比下生成完整角色，补全列出的缺失，结果逐项实查，不能照抄白模缺损或把提示词要求当作完整性通过。
- 实际生图前guard并在原成本journal同一job登记attempt，结束或结果未知立即记实；多人调用按原规则在相关单元计入，统一提交标识用于全场去重统计。不得另建一份零计数日志。
- 每次编辑正式生图提示词后、写入模型 `attempt` 前，必须运行[提示词风格绑定门禁](references/prompt-style-binding-gate.md)，保存当前提示词、固定风格块、三引用角色和动态字段的检查回执。仅 `PROMPT_STYLE_BINDING_GATE: PASS` 可提交；任何固定风格块哈希不符、缺失/改写、引用顺序漂移，或动态字段含反向风格要求均为 `FAIL`，不得用后续出图审美检查补救。
- contextual结果先真实检查，再提取、接触/软物处理和合成。非生成抠图、图层顺序和已有像素修复优先。所有PS连续段走共享队列，安全保存审阅快照后及时释放。
- 像素修复只恢复已批准姿势和几何目标；若必须更改姿势、落点、尺度依据或多人关系，回传 `FAIL`、`return_stage: reference`，由Astra修订相关参考。不能靠任意扭曲、改家具或降低门禁继续。
- 每个实际修改图像完成保存、技术和全图/相关局部审阅再推进。局部遮挡修改复用未变的独立母层和尺度依据，只重查受影响角色、交互与整场快照；新的合成图仍须查看。
- 原post-generation ledger、身份/风格/纹理、完整图层、真实UI、Alpha、XY及原尺寸重建全部通过后才回传PASS并按原规则归档。技术和合同测试不作艺术批准。

每次结果回收后claim-next已READY完整场景；没有就绪场景就结束本轮，由Astra以后唤醒同一任务。人工节点与未知外部操作遵循原阻断规则，不占PS等待；不自行建立后台服务。
