---
name: ndc-prop-master-production
description: 制作 NDC 独立道具透明母版、指定状态和普通 Big，按重要度执行双图选优或单图先行、有限重试及透明整备。用于道具母版生成和返修；不制作场景放入、容器菜单或点击热区。
---
# NDC 道具母版制作

先读取[重要度、容差与候选策略](../ndc-prop-requirements/references/importance-and-tolerance.md)。含 H1 的 master job 使用 `paired` 两图选优；全部为 H2/H3 时使用 `single_first`，首图通过硬门禁且处于 20%/30% 容差内即停止，只有实际失败才提交第二张。六次上限仍是故障/返修上限，不是默认必须用满的产量。

## Photoshop MCP 强制前置

本 Skill 第一次实际调用 Photoshop MCP 前，必须完整读取当前环境的《PS MCP 操作参考手册》：维护工作区从项目根解析 `PS_MCP_操作参考手册.md`，工程镜像从仓库根解析 `production/art_pipeline/PS_MCP_操作参考手册.md`。在当前母版作业记录中保存实际手册路径、版本、SHA-256 和当前会话能力快照；两处均不存在或哈希不一致时不得以历史记忆继续操作。手册负责候选分流、原生 Alpha、自动主体/移除背景、软硬边、路径优化、单引擎、超时回退和视觉/技术验收；本 Skill 的道具语义、分级候选策略、一次隔离和阶段门禁继续优先。实时目录只允许执行 supported 能力，手册本身不增加操作授权。

执行前读[对话任务独立额度](../ndc-prop-requirements/references/task-budget.md)：新对话完整新额度，资产在其他对话中的历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于引用中的旧预算说明。

这是第二阶段。输入为第一阶段内容档案和批次状态；缺失时先交给[需求整理](../ndc-prop-requirements/SKILL.md)。读[共用批次协议](../ndc-prop-requirements/references/batch-contract.md)和[母版专业细则](references/production-details.md)；需要最终框幅或Icon时才读[详情图规格](../ndc-scene-evidence-placement/references/detail-icon-production.md)。

## 制作边界

- 独立物品母版锁定身份、完整物体、关键内容、指定状态及风格，透明背景。普通Big满足最终规格时保留为已完成角色，不在场景阶段重画。Icon及其专用母版统一交第三阶段末制作，本阶段只记录可用来源和依赖。
- 依赖真实桌面、推车或房间语境的线索近景和照片式Big，在第三阶段承载体确定后制作。环境痕迹先锁定可见状态和原场景来源，不为了透明背景凭空拆成独立物件。
- 原生Alpha可用时优先检查和保留，不能先转RGB再重新抠图。可读文字只能来自生成或美术提供的完整母版；不得用PS、代码、OCR替换层补写。
- A类逐项准确；B类只按事先允许的差异验收；C类不追求旧化像素复刻。身份、风格、结构、透明边缘和技术规格仍需通过。
- **道具候选的返工路由：** 先核对道具本体的身份、结构、必要信息、指定状态与可读文字。角色/手部、背景、承托物、场景残留、外部构图边界、透明背景和其他非道具本体问题，先做一次 Photoshop MCP 抠取/移除并实际视觉检查；当前命令确实不支持所需操作时，记录能力边界后允许一次不改写道具像素的确定性 Alpha 提取。若这一次实际隔离结果不完整、视觉失败或置信度不足，保留提取前原图和尝试件，标记 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW`，按下文继续 provisional 下游与待用户审核交付；它不计正式 PASS 覆盖，不可正式发布。随后可在剩余额度内生成空背景/原生透明背景的独立道具图，但不得围绕同一失败源反复尝试 Alpha 阈值或描边。道具本体语义错误同样直接回到生成且不适用 provisional 提取例外；确定性蒙版、裁切和变换只能提取或整理既有像素，不能改写道具本体、必要信息或文字。

## 提取不完整仍推进

Photoshop MCP 已实际产出可打开的非生成 RGBA 后，不得因边缘不完整、残留／误删或把握不足而留空。保留提取前原图的精确字节、尺寸和 SHA-256；另存尝试 RGBA、可恢复 PSD、蒙版／路径／动作证据、Alpha 多底预览、置信度和逐区缺陷。旧 provisional 不覆盖，后续尝试新建版本。

该结果可作为**明确标记的 provisional 来源**继续场景布局、Big/Icon 派生、状态预览、Map／XY 与整包联组检查；全部后继继承 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW` 和源哈希。把原图、尝试件、恢复件、缺陷记录和派生件放入 `工作过程文件` 下独立“待用户审核交付包”。不得把它写成 scene-readiness／正式覆盖 PASS，也不得进入 `最终交付`。用户审核、修正或新提取通过后，从保留原图或明确选定版本建立新修订，重跑受影响 Alpha、身份、场景、热区、XY、重建及发布门禁。若没有任何合规 RGBA 输出，则只保存能力阻断并继续其它独立资产，不伪造 provisional 文件。

## 生成和选优

1. 先处理本阶段可执行缺失项，之后再复检已有问题和修复／重制。当前缺失项有有效来源就复用，必要依赖只做针对性核对；“先复用”是单项方案选择，不是全批旧图先审先修。纯框幅、摆放、透明边缘问题优先使用可用PS MCP修复。
2. 编写输入前按需调用现有 imagegen 与 ndc-visual-description；细节控制针对当前参考和错误，不把减少纹理当成改变画风。
3. 同一物品状态母版总上限6张，首张计入。含 H1 的 `paired` job 按最多3轮、每轮2张比较选优；全部 H2/H3 的 `single_first` job 每轮只生成1张，首张通过硬门禁且处于容差内即停止，只有实际失败才进入下一轮。已有通过版本不为了用完额度继续生成。
4. 必须在生图前通过 attempt 命令登记，prompt指向实际提交的提示文件。`paired` 同轮两张可用同一锁定提示作不同候选；下一轮须按失败原因实质修改。`single_first` 每次都是新一轮，第二张及以后均须记录首张的硬失败或超容差原因并修改提示。只有选定版进入透明整备。
5. PS MCP一次只操作当前目标；占用、保存交接、检查等待及切换遵循共享PS协议。当前图必须先完成实际检查并保存 PASS、FAIL 或 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW` 的当前哈希记录，不能批量修改后补审；其中 provisional 只允许进入上文明确标记的下游和审核包，正式依赖及发布仍阻断。安全交接后其他任务可使用PS。恢复已有路径修局部，不反复描整圈。
   透明整备前按需读[身份与Alpha检查](../ndc-scene-evidence-placement/references/asset-identity-and-alpha-review.md)及[PS操作](../ndc-scene-evidence-placement/references/photoshop-mcp-repair-and-framing.md)，保留完整语义母版及正确原生Alpha。
6. 使用现有 evidence_art.py 完成允许的确定性框幅与Alpha整备。检查整图、局部和最终显示效果，写同一份阶段审核记录，禁止技术脚本自写视觉PASS。
7. 运行scene-readiness逐场景检查：该场景全部道具及完整关联前置均有效通过、无未知外部关联时即可交接第三阶段正式分支；同物全部所需状态、普通Big及跨场景共享母版不能漏查。无关场景未完成不阻塞，不缩小总scope、不按百分比放行。无场景索引的旧批先按合同迁移，否则仍等整批母版。`PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW` 可绕过正式 scene-readiness 仅进入明确标记的 provisional 布局、热区、XY 和审核包分支；不得改写批次 PASS、生成正式热区或发布。

## 输出

完整语义母版、透明选定版、已完成的普通Big、供后续Icon参考的来源索引、当前审核和总尝试记录。立体Icon的独立呈现来源也在第三阶段末制作；不能把整张Big机械缩成Icon。
