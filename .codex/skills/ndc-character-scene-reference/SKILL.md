---
name: ndc-character-scene-reference
description: 用 Astra 中级智能为 NDC 人物入景制作整场方案、景深图、完整单人和联合白模，并按完整场景交给 Terra 极高任务通过受支持的内置或外置浏览器在网页版 ChatGPT 生产。用于入景参考准备、参考缺陷返修和跨场景重叠协调；不生成正式角色资产。
metadata:
  category: art/character/scene-reference
---

# 人物入景：整场参考与协调

自然交互按镜头实际看到的头、肩、躯干和脚判断，不凭“朝向某人”的提示词放行。结合交流对象位置判断是否应只见后脑勺；点击后优先一脚微移、躯干部分转向并侧对镜头、头眼回应镜头，不默认整个人转成正面。具体参照共享规则的 [状态动作连续性](../ndc-character-scene-integration/references/state-variant-assembly.md)。用户纠正后先修正当前画面，再沉淀可迁移判断，不能把单场姿势硬套所有场景。

点击后交互状态必须看向镜头、回应玩家。整场白模明确 active 的头部朝向和朝镜头视线目标；保留合理的身体方向、工作位、支撑及手部动作。不能把“抬眼”或“看向画外人物”当作符合要求；该约束不套用于未点击 idle 或纯剧情人物间交流。

同一快照三人及以上同时在场时，读取并执行[三人及以上同场背影构图门禁](../ndc-character-scene-integration/references/multicast-back-composition.md)：默认锁定至少一名非 active 支持角色位于前景或近中景并背对镜头，以可见上半身／背部形成前后层次，且不得遮挡当前真实 UI。联合白模阶段必须运行 `MULTICAST_BACK_COMPOSITION_GATE` 的 `whitebox` 合同；所有人正面／侧面对镜头不能放行。若没有可用非 active 角色，只接受用户对该具体 scene/snapshot 的明确例外，不得牺牲 active 看镜头规则。

阶段责任以整场白模交接为界：本阶段确定完整场景各角色/状态、头身比、动作大类、主朝向、承托类型、粗略景深、完整母版范围和遮挡关系，冻结并交给下一阶段后即完成该场景参考职责。精确 XY、精确最终尺寸、halo、matte edge、服装/手指/面部精修不属于返回白模生成的理由。正式角色与白模的对齐、生成后技术/视觉自检、提取合成、返修及最终交付均由生产任务全权负责。交接成功后继续下一场参考；全部交接后结束参考轮次，不持续轮询、监控生产，不代做正式角色修复或重复验收。只有下游明确提交动作前提、主朝向、承托类型、粗略深度或解剖/完整母版范围等白模核心错误时，才处理对应参考返修；生产结果偏离正确白模由下游自行对齐。

人体覆盖按[效率与状态合同](../ndc-character-scene-integration/references/efficiency-and-state-contract.md)分为 `FULL_IN_FRAME`、`SCENE_OCCLUDED`、`FRAME_CROPPED_FOREGROUND`。前两类保留并审核完整头到脚母层；镜头构图自然出框的前景角色只需完整到画面边界，并保留画外尺度、重心和承托证据，不能为永远不可见的腿脚额外消耗生成与抠图时间。可见手、肘、头、关键道具或自然出框连续性缺失仍是硬失败。

执行前读[对话任务独立额度](references/task-budget.md)：新对话完整新额度，其他对话的资产历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于旧预算说明。

执行模型固定为 `gpt-6-astra`，`thinking: medium`。这是用户明确指定的生产配置；调用任务工具时实际填写，不用文字自称已切换。当前任务配置不符时按 [模型启动与交接](../ndc-art-stage-pipeline/references/integration-pipeline.md) 启动参考协调任务；已有正确配置则直接继续，避免再开一层协调任务。

启动时只读 [入景共享规则](../ndc-character-scene-integration/SKILL.md)、[效率与状态合同](../ndc-character-scene-integration/references/efficiency-and-state-contract.md)和[制作节奏](../ndc-character-scene-integration/references/production-cadence.md)的参考阶段；具体尺度、UI、多人或承托问题出现时再按共享 Skill 的索引读取对应参考，不在每次恢复重载完整生产细节。

1. 锁定当前需求全部场景、出场状态、角色与姿势映射；盘点批准原图、身份来源和历史有效组件。先完成一场，再推进另一独立场景，不先批量制作所有角色局部白模。
2. 完成表演、支撑、场景尺度证据、景深、逐 actor/pose 最终生产白模和全体联合快照。按[白模放行规则](../ndc-character-scene-integration/references/whitebox-acceptance.md)重点检查角色/状态、头身比、动作大类、主朝向、承托类型、粗略景深和完整母版范围；不影响判断的小型遮挡、局部缺失及小细节可放行，交接正式生图补全，不强制先修白模。每个 actor/pose 必须保留透明 `complete_anatomy_master`，并从它与原场景制作实际将作为网页 Image 1 的 `final_submission_whitebox`；整场彩色 `joint_whitebox_preview` 只审核多人关系，禁止把木棍、关节点、程序块面、扁平剪影、量尺或该联合预览改名冒充最终生产白模。可在正确承托锚点上统一平移、等比缩放和必要旋转；不为精确 XY/尺寸或边缘精修再生图。按[重要度与容差合同](../ndc-character-scene-integration/references/importance-and-tolerance.md)为“区域 × 验收项”登记 H0/H1/H2/H3，运行校验并随场景冻结；不得按整张图笼统标成“不重要”。各状态使用相同来源及变换，所有 NPC 场景均选用真实 UI，不能推断无 UI；多人关系联合审阅，三人及以上快照还必须保存 `whitebox` 背影构图门禁 PASS。尺度允许原门禁认可的 metric 或 bounded 模式，不能编造相机度量。原场景、现行白模和既有竖向尺度仍有效时，旧 v1 报告缺少 v2 字段或横纵 `directionTransfer` 不是重做白模的理由；按兼容校验复用，横向量尺只作占地诊断，当前人物尺寸由现行 placement、头部、支撑和整场审阅决定。
3. 组装实际局部生图输入、原图映射、身份图及提示词；检查引用职责和可见动作。让原 `production_gate.py` 对当前 pre-generation ledger 验证通过，并保留真实技术/视觉检查。直接从当前联合白模叠加实际 UI 生成 Layout Preview，目标 active time 不超过 10 分钟，不为预览额外生图。`probe` 档 finalizer 要到生产任务取得首个 H0 可用 RGBA 后运行；文件存在或旧 PASS 不代替艺术审核。
4. 先按[角色白模节点交付合同](references/node-delivery-contract.md)从 `assets/character-node-delivery-pack.template.json` 建立真实文件包，并用 `scripts/node_delivery.py pack|verify` 生成 `{DELIVERY_ROOT}/角色融入场景/Unit<n>/节点交付/<scene-id>/`：场景根平铺最初要求的逐 actor/pose 完整母层、实际 Image 1、联合白模与真实 UI 预览；JSON、候选状态和审核证据只进 `_节点资料`。每场 scope、pack、manifest 与人工节点必须绑定同一 `scene_label`，同时写用户可理解的地点和时间，不能只报 SC 代号。仅在用户明确要求从旧批冗余资产分拣更多节点内容时，开启 `legacy_migration_backfill`：绑定完整历史来源清单，把旧 RGB 候选和已有抠背景 RGBA 作为非正式审阅副本一并平铺；RGBA 名称末尾写匹配坐标的 `__XY_x<int>_y<int>`。该分拣可在以后同类明确要求中再次启用，但普通新节点保持关闭。多场批次必须逐场建包，再用 `assets/character-node-delivery-batch-audit.template.json` 与 `node_delivery.py audit-batch` 枚举当前节点清单。随后从 `assets/scene-reference-handoff.template.json` 建立当前整场交接，每个 generation unit 只绑定一个 actor/pose、人体覆盖模式和三份独立引用；Image 1 与 `complete_master` 必须逐字节复用节点中的权威白模。人工处理／回流默认是 `PARALLEL_NONBLOCKING` 支线：节点就绪后原角色正式生产主线继续完成冻结 scene scope，不等待用户回流，也不删减后续生成、提取、合成和验收。只有用户明确要求“等我处理／审核后再继续”时，才设 `USER_HOLD` 并要求 approval。运行 `scripts/validate_reference_handoff.py --handoff <handoff.json> --output <ready-revision-gate.json> --checked-at <ISO-8601>`；任何用联合预览或另制替代图换掉节点白模的交接直接失败。只有 `CURRENT` gate 与流水 `guard` 均绑定同一 scene/revision 才发布 `character_scene` 包。任何新 revision 都明确 supersede 旧工作区。白模、景深或其它参考通常仍是过程／交接材料；只有当前任务明确决定“该参考图本身也用于交付”时，才登记为 `selected_reference`。
5. 生产回传参考错误时，保留实际次数与候选，暂停相关场景后修正姿势、尺度、承托或多人关系，重核受影响证据并追加交接版本；不要求独立已通过场景重做。

原始参考的模型/PS预算及已明确授权的独立测试计数都必须保留。交接继续引用原生产ID；真实新对话任务自动获得完整新额度，旧参考记录只追溯，不扣减新任务；同对话接续不清零。人工节点依原流程处理，等待时释放PS且可继续无依赖场景。所有需求场景都未到交接条件时如实报告缺口，不删减总清单。

共用执行机制与包字段见 [入景阶段交接](../ndc-art-stage-pipeline/references/integration-pipeline.md)。本任务负责全批参考和跨任务协调；Terra接手后的同场角色生产和最终场景验收由Terra统一负责。

## 发布前节点门禁

读[检索、人工节点与回流合同](../ndc-art-stage-pipeline/references/discovery-and-manual-node.md)及[角色白模节点交付合同](references/node-delivery-contract.md)。先为每个 actor/pose 的白模建立精确 discovery receipt；只有当前 scope 的 `CONFIRMED_ABSENT` 才能生成白模，FOUND_USABLE／FOUND_REPAIRABLE 分别复用／修复。第 3 步白模包齐备后，先以 `node_delivery.py pack|verify` 建立每场可直接使用的平铺文件包，再创建每个 scene/revision 唯一的角色人工节点；节点的 `node_delivery_manifest` 必须绑定该包及其可读 `scene_label`。逐 actor/pose 直接附实际 PNG `complete_anatomy_master`、最终会上传的 `final_submission_whitebox`、两类检查和 discovery receipt，另附联合白模与实际 UI 避让预览。只交 JSON、只交联合预览、漏场景、仅报 SC 代号或把几何块人形冒充最终白模均不能创建节点。多场汇报前运行 `node_delivery.py audit-batch`。默认 `PARALLEL_NONBLOCKING` handoff 只需绑定就绪节点，原生产主线继续；只有用户明确设置 `USER_HOLD` 才要求 `USER_NODE_APPROVED` approval。人工回流建立新支线 revision 并重跑受影响门禁，不覆盖或取消已经推进的主线。
