---
name: ndc-prop-delivery-review
description: 复查并归档 NDC 道具图片包，核验内容覆盖、跨状态身份、热区坐标、有效审核及有限返修，汇总风险和工程接入待办。用于道具最终验收、候选转正及交付复核；不把技术通过当视觉批准。
---
# NDC 道具最终复查与交付

复核前读取[重要度、容差与候选策略](../ndc-prop-requirements/references/importance-and-tolerance.md)。硬合同不变；H1/H2/H3 分别最多容许 10%/20%/30% 的已定义可测偏差，不跨区域平均。H2/H3 在限内不得因为纯润色继续出图或放大审核；出现异常、身份/状态/文字/Alpha/Map/XY/阴影/重建问题时立即回到硬门禁和必要高倍率检查。

## Photoshop MCP 强制前置

本 Skill 触发 Photoshop MCP 有限返修时，第一次实际调用前必须完整读取当前环境的《PS MCP 操作参考手册》：维护工作区从项目根解析 `PS_MCP_操作参考手册.md`，工程镜像从仓库根解析 `production/art_pipeline/PS_MCP_操作参考手册.md`。在当前复查记录中保存实际手册路径、版本、SHA-256 和当前会话能力快照；两处均不存在或哈希不一致时不得以历史记忆继续操作。手册负责通用效率、抠图、Alpha、路径、单引擎、超时回退和视觉/技术验收；本 Skill 的责任阶段返回、候选转正和正式交付门禁继续优先。实时目录只允许执行 supported 能力，手册本身不增加返修权限。

执行前读[对话任务独立额度](../ndc-prop-requirements/references/task-budget.md)：新对话完整新额度，资产在其他对话中的历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于引用中的旧预算说明。

这是第五阶段。读[批次协议](../ndc-prop-requirements/references/batch-contract.md)、[审核与复用](references/review-contract.md)及[交付细则](references/production-details.md)。命名、角色和目录仍遵从[交付合同](../ndc-scene-evidence-placement/references/delivery-contract.md)。

跨设备路径先由 `ndc_art.py paths` 解析：项目批准资产与工程运行时分别从 `{PLANNING_ROOT}` / `{ENGINE_ROOT}` 的索引和相对路径读取，新复查与 provisional 包只写入 `{WORK_ROOT}` 的受管 job。Skill 自有脚本、规范和资源从当前 Skill 根相对解析。占位符不是字面路径，任何配置漂移或缺失都不得用维护机盘符补位。

本阶段同时收口 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW`，但不把它转为正式 PASS。只要上游 Photoshop MCP 已实际导出可打开的非生成 RGBA，即使提取不完整或低置信度，也必须汇总为 `工作过程文件` 下独立“待用户审核交付包”：包含提取前原图及 SHA-256、尝试 RGBA、可恢复 PSD、蒙版／路径／动作证据、Alpha 多底预览、置信度／逐区缺陷，以及继承该状态的场景、Big/Icon、Map、XY、重建和联组结果。缺少下游角色时先补做可执行 provisional 派生，不留空。旧 provisional 不覆盖；每次修正建立新版本。

该审核包是用户可审核的交付材料，不进入 `最终交付`，不满足 stage 5、formal-release 或最终视觉记录 PASS，也不得覆盖已批准资产。正式统计同时报告 `formal_pass` 与 `provisional_review_delivery`，不能把后者算作正式覆盖。用户审核、人工修正或后续自动提取通过后，从保留原图或明确选定版本建立新修订，重跑受影响 Alpha、场景、阴影、热区、XY、重建、联组和正式发布门禁。道具语义、身份、结构、文字、承托或取得逻辑失败不适用本例外。

## 完整复查

全量生产时，本阶段在可执行缺失交付补全后进行整体复检，问题返回责任阶段有限修复；不得把本入口提前当作补缺前的全量审核任务。用户当前仅要求统计／复检时按该范围执行，不自动生图。进度按共用协议同时报告完整总角色、各场景实际阶段与补缺基线，正式交付另计；某场景获准入景不代表整批Icon／热区或正式交付已放行。

1. 从锁定需求推导必需交付，不能从现有文件反推需求已齐全。分别报告母版、场景、热区、正式整项及阻塞数量。
2. A类事实全部通过；B类按原先明确允许的差异判断；C类不追求像素一致。风险表列尚未核实或超出允许范围的差异。关键错误与技术错误不能被平均分数抵消。
3. 同组比较Big/Icon/Map/菜单及必要状态，判断身份、组件和状态关系；真实角度、光线与合理遮挡可变。读取当前拒收，用户否定立即使相关复用失效。
4. 核对实际待交付字节及完整链。所有可拾取、线索和环境叙事道具都检查本体及全部归属接触／投射阴影，需热区时要求热区完整覆盖该联合轮廓。对地图直接拾取且拾取后消失的道具，必须联组检查原场景、无道具承载物状态、道具＋全部道具归属阴影独立层、Map、XY和拾取前重建结果：承载物及其自身阴影必须永久保留且不得进入道具 Map，合成 Map 必须还原拾取前画面，移除 Map 必须恢复承载物仍在而道具及其归属阴影均消失、无残影／接缝的拾取后画面。任一项缺失即退回责任阶段。Type 7 二级菜单子物品不套用这套承载物三层门禁。已有审核满足图像／父图／内容／要求／范围均未变化且无拒收时复用记录；同哈希不足以放行。最终整包联组复查仍执行。
5. 关键问题返回责任阶段，保留原job和累计次数。先区分道具本体的身份、结构、必要信息、状态和可读文字，与人物/手部、背景、承托、场景残留、构图边界和Alpha等外部问题；后者先做一次 Photoshop MCP 抠取或修复并复查。若已产出可打开 RGBA 但隔离结果不完整、视觉失败或低置信度，将其登记为 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW`，继续补齐 provisional 下游并汇入待审核包；不计正式候选／进度，不可正式发布。可在原剩余额度内返回生成阶段产出空背景／原生透明背景的新版本，但不在同一失败源上重复调 Alpha。道具本体语义门禁失败同样回到生成且不走此例外。额度用尽保留真实候选和 provisional 审核包；不得因最终审核再次启动三轮生成，也不得把生产劳动默认转交用户。
6. 每个正式PNG必须绑定通过的真实视觉记录。复用记录只证明旧观察仍适用，脚本不得生成新的艺术PASS。详情图通过不代表热区通过。
7. 图片范围和程序接入分开：交付图片及可供接入的坐标／说明，不擅自修改Unity，不将程序未绑定错误计为缺PNG。但地图直接拾取道具缺少独立道具层或无道具承载物状态，属于图片／状态合同未完成，不能降格为“仅待程序接入”。用户明确要求运行时完成时仍需单独验证。

## 校验和归档

新五阶段批次必须依次执行以下命令，路径从Skill目录解析为绝对路径，不依赖终端cwd：

- `python scripts/workflow_state.py validate --batch <batch.json> --stage 5`：全批次交接、内容版本、依赖、生成额度与审核有效性。
- `python ../ndc-scene-evidence-placement/scripts/validate_formal_release.py --folder <formal> --release-contract <contract> --batch <batch.json>`：原图像角色、XY、父图与旧副本检查，并核验批次。
- `python scripts/final_visual_check.py --formal-dir <formal> --record-root <process> --batch <batch.json>`：最终复制后核对每个正式文件有有效逐图审核绑定。

正式目录仅接受通过的PNG与一份XYposition.txt。报告、候选、PSD、遮罩、历史及 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW` 审核包放在工作过程目录。替换包先完整验证，保存旧版本后发布；不混入旧目录的未知文件。通过适用门槛即归档，不等待重复人工确认。每个正式 artifact 可记录published_path以支持最终副本核对，但它必须与已审核字节一致；provisional 只记录 review-package 路径，不得伪造 published_path。

## 可复用工具

scripts/workflow_state.py 管理批次门槛、追加尝试日志、缺失 job 的受证据增补和审核复用判定；scripts/scene_release.py计算有证据的场景关联前置闭包。若已锁定批次确有一个必需、PENDING 的第三阶段场景产物漏绑 job，先核对确切历史次数与来源，再按[场景放行合同](../ndc-prop-requirements/references/scene-release-contract.md#接入与续跑)追加一次 `append-job`；不得借此重置、替换或补写其他 job。
历史次数已确认后，其引用的来源文件发生变化并触发`history source bytes changed`时，读[历史来源复核](references/history-source-revalidation.md)。只有重新查明历史次数未变后才能追加来源复核；它不重开次数，也不恢复图像审核。
scripts/stage_visual_check.py、scripts/final_visual_check.py 是移入本Skill的共用审核实现；项目根旧命令保留兼容入口。
旧evidence_art、evidence_delivery、irregular_map、secondary_prop_border和validate_formal_release仍保留在原Skill脚本地址。不要搬动脚本破坏历史作业。
