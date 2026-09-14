# 既有资产检索、阶段人工节点与可选回流支线

本合同覆盖角色入景与道具五阶段。它增加的是按原任务初始要求设置的阶段人工节点，以及用户需要时可走的人工处理／回流支线；不取代、不合并、不提升 PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW、交付候选或正式 PASS，也不删除原生产流程。角色初始节点交完整人体白模母层与实际 Image 1；道具初始节点交实际母图、Big 等原始要求内容。没有额外节点要求时，Icon、场景态、热区、菜单、提取、合成、验收与正式发布仍按冻结主线正常推进，不需要提前全部塞进节点。

## 1. Discovery receipt

任何新的生成、修复或复用前，建立 ndc-asset-discovery-receipt/v1。收据精确绑定 domain、scene_id、revision、actor_id 或 item_id、pose_or_state、artifact_role；记录 official_runtime、approved_archive、formal_delivery 三类实际配置根的精确编号／别名查询、完成状态与候选文件 SHA-256／尺寸。

复制 assets/asset-discovery-receipt.template.json 填写后运行：

    python scripts/asset_discovery.py verify --receipt <receipt.json> --action <GENERATE|REPAIR|REUSE|PACKAGE>

CONFIRMED_ABSENT 只有完整检索全部三根且无候选时才可用于 GENERATE。FOUND_USABLE 必须复用，FOUND_REPAIRABLE 必须修复，FOUND_UNBOUND／NOT_SEARCHED／SEARCH_INCOMPLETE／BLOCKED 都阻止新生成。收据的 asset-index 或 scope revision 哈希变化自动失效；需要显式保留失效链时运行 invalidate 生成新 NOT_SEARCHED 记录，绝不覆盖旧收据。旧批必须新建收据，不能把 checked_roots 迁为合格证据。

## 2. 节点创建与审批

复制 assets/manual-review-node.template.json 及对应领域模板。

角色节点须先按[角色白模节点交付合同](../../ndc-character-scene-reference/references/node-delivery-contract.md)生成场景包，再由 node manifest 绑定包内实际字节。固定路径是 `{DELIVERY_ROOT}/角色融入场景/Unit<n>/节点交付/<scene-id>/`；根层只平铺全部逐 actor/pose 透明 `complete_anatomy_master`、确实会作为网页 Image 1 的 `final_submission_whitebox`、联合白模、真实 UI 预览及现有 PSD/PSB，JSON、候选状态和审核证据只进 `_节点资料` 并按交付文件同 stem 归组。每场 scope、pack、manifest 与 manual node 必须绑定同一 `scene_label`，同时写可读地点和时间，不能只把 SC 代号交给用户。多场批次逐场建包，并用冻结 `expected_scene_ids` 运行 `node_delivery.py audit-batch`；其 CSV／Markdown／JSON 逐场、逐 actor/pose 列出已验证项和待人工补齐项。不得只交一个场景、混入一个日期根、错放 `{DELIVERY_ROOT}/角色` 或建立角色／类型资产子目录。联合预览只是多人关系视图，不能冒充任一 actor/pose 的最终生产白模。木棍、关节点、程序几何块、扁平色剪影、技术量尺和仅文件名／JSON 声明的白模均拒绝；reference handoff 必须逐字节复用节点这两个权威文件。

用户明确要求查看／分拣旧批冗余生成结果时，可在角色 pack 显式开启 `legacy_migration_backfill` 并绑定当次完整历史来源清单；旧 RGB 候选与已有透明 RGBA 以非正式审阅副本进入场景根，后者文件名须携带匹配的 `__XY_x<int>_y<int>`。以后遇到同类明确要求可再次启用，但普通节点默认关闭；这不把历史候选提升为生产白模／当前交付候选／PASS。

道具节点按[道具节点交付阶段资产合同](../../ndc-prop-delivery-review/references/node-delivery-contract.md)生成场景阶段包。冻结矩阵逐 subject 对 16 类角色声明 `REQUIRED`／`MAINLINE_AFTER_NODE`／`NOT_APPLICABLE`：原任务最初要求的实际母图、Big 等必须收齐；后续仍属冻结主线但本节点暂不交的内容必须标 `MAINLINE_AFTER_NODE`，不能借节点缩小完整生产分母。只有用户额外要求从旧冗余资产分拣时，才把已核验的 Icon、场景态、Map／XY、Type6／Type7、菜单、PSD、环境叙事和线索追加为节点 `REQUIRED`；可选 `reconcile-hotspots` 用当前 batch 精确反查“已通过但漏包”的 Stage4 实物。实际资产平铺到场景根，场景就绪 PNG 带精确 `__XY_x<int>_y<int>`。每场携带可读地点和时间；`audit-batch` 只统计当前节点范围，JSON 与证据只进 `_节点资料`。只含 JSON、按类型拆资产目录、缺本节点 `REQUIRED` 或只报 SC 代号都不能创建节点。

    python scripts/manual_review_node.py create --node-manifest <node.json>

向用户呈现 NODE_DELIVERABLE_READY。默认把人工处理／回流记录为 `PARALLEL_NONBLOCKING`：原冻结生产主线继续推进，不等待用户回流。只有用户明确要求“等我处理／审核后再继续”时，才设为 `USER_HOLD` 并执行：

    python scripts/manual_review_node.py approve --node-manifest <node.json> --out <approval.json> --approved-at <ISO-8601> --user-statement <用户明确通过原话>
    python scripts/manual_review_node.py verify --node-manifest <node.json> --approval <approval.json>

角色下游必须使用节点精确绑定的生产白模；`PARALLEL_NONBLOCKING` 下节点本身的哈希即为主线输入权威，不要求 approval。`USER_HOLD` 下 approval 的 node manifest 路径和 SHA-256 是上游权威。道具附加分拣资产只约束对应支线字节，不阻断未依赖它们的主线阶段。不能回头静默换来源或覆盖节点前判断；节点或回流支线都不等于任务完成。

## 3. 可选人工回流支线

角色使用 ndc-character-scene-production/assets/manual-render-return-workspace.template.json；道具使用 ndc-scene-evidence-placement/assets/manual-finished-package-workspace.template.json。每个 workspace 必须在审批前预先列出 slot、角色和相对路径，并写入 node_id／domain／scene_id／revision；节点反向以 SHA-256 绑定该 workspace，所以 workspace 不内嵌 approval（否则会形成自引用哈希循环）。

人工回流不是默认主线的替代品。只有用户明确说“已经生成好了”或同义表达后，读取 workspace 当前内容并运行：

    python scripts/manual_review_node.py return --workspace-manifest <workspace.json> --approval <approved-node-approval.json> --workspace <folder> --out <accepted-return.json> --returned-at <ISO-8601> --user-statement <用户明确交回原话>

它写 USER_RETURN_ACCEPTED_FOR_PACKAGING，保留全体当前文件及 slot SHA-256。文件的新增或变更是用户主动新 revision，不以旧哈希退回；此前节点／返回和并行主线版本均保留。缺独立层但只有扁平预览时写 INPUT_GAP，继续其余 present slots，不生图补洞。回流只建立受影响支线的新 revision 并重跑相应技术、视觉、关系和正式发布门禁；不得覆盖已经推进的主线，也不得把主线本应完成的范围默认转交用户。

## 4. 失效条件

只有用户明确否定、需求实质变化、节点 revision 改变、用户交回新 revision，或可验证的冻结 scope／资产索引变更会使受影响部分失效。无关场景、无关节点、时间戳或展示备注不回滚其它节点。PROVISIONAL 的专属用户审核仍按其原合同，不能代替本节点审批。
