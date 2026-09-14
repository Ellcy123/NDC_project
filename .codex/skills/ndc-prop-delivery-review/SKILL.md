---
name: ndc-prop-delivery-review
description: 复查并归档 NDC 道具图片包，核验内容覆盖、跨状态身份、热区坐标、有效审核及有限返修，汇总风险和工程接入待办。用于道具最终验收、候选转正及交付复核；不把技术通过当视觉批准。
---
# NDC 道具最终复查与交付

先读[五阶段共用执行核心](../ndc-prop-requirements/references/pipeline-core.md)。最终复核从“交付候选”清单开始，再与冻结范围和过程台账对账；普通过程候选不得抢占首轮审核。

复核前读取[重要度、容差与候选策略](../ndc-prop-requirements/references/importance-and-tolerance.md)。硬合同不变；H1/H2/H3 分别最多容许 10%/20%/30% 的已定义可测偏差，不跨区域平均。H2/H3 在限内不得因为纯润色继续出图或放大审核；出现异常、身份/状态/文字/Alpha/Map/XY/阴影/重建问题时立即回到硬门禁和必要高倍率检查。

## Photoshop MCP 强制前置

本 Skill 触发 Photoshop MCP 有限返修时，第一次实际调用前必须完整读取当前环境的《PS MCP 操作参考手册》：维护工作区从项目根解析 `PS_MCP_操作参考手册.md`，工程镜像从仓库根解析 `production/art_pipeline/PS_MCP_操作参考手册.md`。在当前复查记录中保存实际手册路径、版本、SHA-256 和当前会话能力快照；两处均不存在或哈希不一致时不得以历史记忆继续操作。手册负责通用效率、抠图、Alpha、路径、单引擎、超时回退和视觉/技术验收；本 Skill 的责任阶段返回、候选转正和正式交付门禁继续优先。实时目录只允许执行 supported 能力，手册本身不增加返修权限。

执行前读[对话任务独立额度](../ndc-prop-requirements/references/task-budget.md)：新对话完整新额度，资产在其他对话中的历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于引用中的旧预算说明。

这是第五阶段。读[批次协议](../ndc-prop-requirements/references/batch-contract.md)、[审核与复用](references/review-contract.md)及[交付细则](references/production-details.md)。命名、角色和目录仍遵从[交付合同](../ndc-scene-evidence-placement/references/delivery-contract.md)。

跨设备路径先由 `ndc_art.py paths` 解析：项目批准资产与工程运行时分别从 `{PLANNING_ROOT}` / `{ENGINE_ROOT}` 的索引和相对路径读取，新复查与 provisional 包只写入 `{WORK_ROOT}` 的受管 job。Skill 自有脚本、规范和资源从当前 Skill 根相对解析。占位符不是字面路径，任何配置漂移或缺失都不得用维护机盘符补位。

本阶段同时收口 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW`，但不把它转为正式 PASS。只要上游 Photoshop MCP 已实际导出可打开的非生成 RGBA，即使提取不完整或低置信度，也必须汇总为 `工作过程文件` 下独立“待用户审核交付包”：包含提取前原图及 SHA-256、尝试 RGBA、可恢复 PSD、蒙版／路径／动作证据、Alpha 多底预览、置信度／逐区缺陷，以及继承该状态的场景、Big/Icon、Map、XY、重建和联组结果。缺少下游角色时先补做可执行 provisional 派生，不留空。旧 provisional 不覆盖；每次修正建立新版本。

该审核包是用户可审核的交付材料，不进入 `最终交付`，不满足 stage 5、formal-release 或最终视觉记录 PASS，也不得覆盖已批准资产。正式统计同时报告 `formal_pass` 与 `provisional_review_delivery`，不能把后者算作正式覆盖。用户审核、人工修正或后续自动提取通过后，从保留原图或明确选定版本建立新修订，重跑受影响 Alpha、场景、阴影、热区、XY、重建、联组和正式发布门禁。道具语义、身份、结构、文字、承托或取得逻辑失败不适用本例外。

## 完整复查

- `scripts/delivery_candidate.py register|set-status|audit|move-failed`：把明确选定的交付目标及其选定参考图登记到 `最终交付/<类别>/<Unit>/<资产或场景>/交付候选/<candidate-id>`，原位记录复核失败；失败后才允许保留式移出，且不自动删除。
- `scripts/node_delivery.py pack|verify|audit-batch`：按[道具节点交付阶段资产合同](references/node-delivery-contract.md)把当前人工节点明确要求的阶段资产平铺到 `最终交付/道具/Unit<n>/节点交付/<scene>/`。默认初始节点以原任务要求的母图、Big 等为必需内容；Icon、场景态、热区、菜单、PSD 等只有原任务节点本来要求、或用户额外要求把可复用旧资产也带入时才成为节点 `REQUIRED`。仍在冻结生产范围但位于节点之后的资产必须标 `MAINLINE_AFTER_NODE`，不能写成不适用或从主线取消。文件名统一为 `SC<scene>_<subject>_[state_]map|big|icon|master|prop|psd` 及合同内扩展状态尾缀；可直接融回场景的透明 PNG 必须追加 `__XY_x<int>_y<int>`。每场同时携带包括地点和时间的可读 `scene_label`；JSON、交付候选、HTML／人读清单和审核证据只进入 `_节点资料`。`audit-batch` 只审核当前节点冻结的 `REQUIRED`，不把后续主线资产误报成当前节点缺件。
- `scripts/node_delivery.py reconcile-hotspots`：仅在用户明确要求从前序／旧冗余资产分拣更多节点内容时，从当前冻结 `ndc-prop-batch/v1` 反查 Stage4 PASS 的实际 PNG、当前审核哈希、正确场景平铺副本和 XY 文件名，避免已有可用热区漏包。它是可选人工回流／旧资产分拣支线，不是普通新节点或整条生产主线的默认门禁。
- `scripts/batch_update.py artifact-transition|next-action`：以期望批次哈希和期望旧状态执行原子写入，自动绑定文件哈希、追加状态事件，并把 next_action 限制为最多三条／300 字；禁止手工编辑大批次 JSON 更新产物状态。

全量生产时，本阶段在可执行缺失交付补全后进行整体复检，问题返回责任阶段有限修复；不得把本入口提前当作补缺前的全量审核任务。用户当前仅要求统计／复检时按该范围执行，不自动生图。进度按共用协议同时报告完整总角色、各场景实际阶段与补缺基线，正式交付另计；某场景获准入景不代表整批Icon／热区或正式交付已放行。

1. 从锁定需求推导必需交付，不能从现有文件反推需求已齐全。分别报告母版、场景、热区、正式整项及阻塞数量。
2. A类事实全部通过；B类按原先明确允许的差异判断；C类不追求像素一致。风险表列尚未核实或超出允许范围的差异。关键错误与技术错误不能被平均分数抵消。
3. 同组比较Big/Icon/Map/菜单及必要状态，判断身份、组件和状态关系；真实角度、光线与合理遮挡可变。读取当前拒收，用户否定立即使相关复用失效。
4. 核对实际待交付字节及完整链。所有可拾取、线索和环境叙事道具都检查本体及全部归属接触／投射阴影，需热区时要求热区完整覆盖该联合轮廓。对地图直接拾取且拾取后消失的道具，必须联组检查原场景、无道具承载物状态、道具＋全部道具归属阴影独立层、Map、XY和拾取前重建结果：承载物及其自身阴影必须永久保留且不得进入道具 Map，合成 Map 必须还原拾取前画面，移除 Map 必须恢复承载物仍在而道具及其归属阴影均消失、无残影／接缝的拾取后画面。任一项缺失即退回责任阶段。Type 7 二级菜单子物品不套用这套承载物三层门禁。已有审核满足图像／父图／内容／要求／范围均未变化且无拒收时复用记录；同哈希不足以放行。最终整包联组复查仍执行。
5. 关键问题返回责任阶段，保留原job和累计次数。先区分道具本体的身份、结构、必要信息、状态和可读文字，与人物/手部、背景、承托、场景残留、构图边界和Alpha等外部问题；后者先做一次 Photoshop MCP 抠取或修复并复查。若已产出可打开 RGBA 但隔离结果不完整、视觉失败或低置信度，将其登记为 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW`，继续补齐 provisional 下游并汇入待审核包；不计正式候选／进度，不可正式发布。可在原剩余额度内返回生成阶段产出空背景／原生透明背景的新版本，但不在同一失败源上重复调 Alpha。道具本体语义门禁失败同样回到生成且不走此例外。额度用尽保留真实候选和 provisional 审核包；不得因最终审核再次启动三轮生成，也不得把生产劳动默认转交用户。
6. 每个正式PNG必须绑定通过的真实视觉记录。复用记录只证明旧观察仍适用，脚本不得生成新的艺术PASS。详情图通过不代表热区通过。
7. 图片范围和程序接入分开：交付图片及可供接入的坐标／说明，不擅自修改Unity，不将程序未绑定错误计为缺PNG。但地图直接拾取道具缺少独立道具层或无道具承载物状态，属于图片／状态合同未完成，不能降格为“仅待程序接入”。用户明确要求运行时完成时仍需单独验证。
8. 用户要求人工节点时，按场景建立阶段节点交付。节点 scope 逐 subject 对 16 类角色明确写 `REQUIRED`、`MAINLINE_AFTER_NODE` 或 `NOT_APPLICABLE`：初始要求中的母图、Big 等是节点必需；位于后续阶段且仍属于冻结生产范围的内容写 `MAINLINE_AFTER_NODE`，主线照常继续；只有确实不适用的角色才能写 `NOT_APPLICABLE`。用户额外要求整理旧冗余资产时，可把经当前来源、哈希和审核核对的 Icon、场景态、热区／XY、菜单、PSD、环境叙事和线索作为该节点的附加 `REQUIRED`，但这仍是人工回流支线。实际资产按标准名平铺在场景根；场景就绪透明 PNG 必须带精确 XY。JSON／交付候选／总览／证据隔离进 `_节点资料`。多场任务以当前节点清单运行 `audit-batch`；不得把节点范围当成整个生产分母，也不得因节点已通过而停止冻结主线。

## 校验和归档

新五阶段批次必须依次执行以下命令，路径从Skill目录解析为绝对路径，不依赖终端cwd：

- `python scripts/workflow_state.py validate --batch <batch.json> --stage 5`：全批次交接、内容版本、依赖、生成额度与审核有效性。
- `python ../ndc-scene-evidence-placement/scripts/validate_formal_release.py --folder <formal> --release-contract <contract> --batch <batch.json>`：原图像角色、XY、父图与旧副本检查，并核验批次。
- `python scripts/final_visual_check.py --formal-dir <formal> --record-root <process> --batch <batch.json>`：最终复制后核对每个正式文件有有效逐图审核绑定。

`最终交付` 中的正式资产子目录仅接受通过的PNG与一份XYposition.txt；隔离的“交付候选”子树只接受明确选定的单项交付候选及其选定参考图，隔离的“节点交付”子树只接受当前节点范围内完整的阶段审核包，三者职责不同。节点交付场景根必须含其 `REQUIRED` 的真实图片／适用 PSD／XY/TXT；`MAINLINE_AFTER_NODE` 只列在节点资料中并继续生产，不要求提前塞进节点。HTML、Markdown、JSON、交付候选记录和审核证据只能位于 `_节点资料`，不得混入场景根或正式资产子目录。除节点明确要求的当前 PSD 源副本外，历史 PSD、遮罩、报告及完整 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW` 审核包仍放工作过程目录。替换包先完整验证，保存旧版本后发布；不混入旧目录的未知文件。通过适用门槛即归档，不等待重复人工确认。每个正式 artifact 可记录published_path以支持最终副本核对，但它必须与已审核字节一致；provisional 候选不得伪造 published_path。

## 可复用工具

scripts/workflow_state.py 管理批次门槛、追加尝试日志、缺失 job 的受证据增补和审核复用判定；scripts/scene_release.py计算有证据的场景关联前置闭包。若已锁定批次确有一个必需、PENDING 的第三阶段场景产物漏绑 job，先核对确切历史次数与来源，再按[场景放行合同](../ndc-prop-requirements/references/scene-release-contract.md#接入与续跑)追加一次 `append-job`；不得借此重置、替换或补写其他 job。
历史次数已确认后，其引用的来源文件发生变化并触发`history source bytes changed`时，读[历史来源复核](references/history-source-revalidation.md)。只有重新查明历史次数未变后才能追加来源复核；它不重开次数，也不恢复图像审核。
scripts/stage_visual_check.py、scripts/final_visual_check.py 是移入本Skill的共用审核实现；项目根旧命令保留兼容入口。
旧evidence_art、evidence_delivery、irregular_map、secondary_prop_border和validate_formal_release仍保留在原Skill脚本地址。不要搬动脚本破坏历史作业。

## 节点与来源复核

读[检索、人工节点与回流合同](../ndc-art-stage-pipeline/references/discovery-and-manual-node.md)。最终复查同时枚举完整冻结 scope、现行 discovery receipt、阶段节点 manifest、可选 approval／人工回流快照与正式文件：先运行 `node_delivery.py verify`，再由 `manual_review_node.py` 绑定同一 scene/revision/node 字节。节点只审核当前 `REQUIRED`，不能覆盖 `MAINLINE_AFTER_NODE` 的生产、缺失父图、热区、复核或正式发布门禁；任何 scope／asset-index／父图实质变化都只撤销受影响项。`USER_RETURN_ACCEPTED_FOR_PACKAGING` 是并行人工支线的当前快照，`节点交付`、`交付候选` 与 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW` 仍需分列，均不得在报告或正式目录中冒充 PASS。
