---
name: ndc-generate-characters
description: 盘点 NDC 角色现有资产、锁定需求与来源，并路由身份母版和角色卡、肖像或状态派生；通用风格母版、通用角色卡及明确触发的黑白红卡使用受支持的内置或外置浏览器访问网页版 ChatGPT。用于角色制作起步、批次规划与跨阶段续作。
metadata:
  category: art/character/requirements
---

# NDC 角色需求与制作入口

## Photoshop MCP 强制前置

本 Skill 或其实际下游在第一次调用 Photoshop MCP 前，必须完整读取当前环境的《PS MCP 操作参考手册》：维护工作区从项目根解析 `PS_MCP_操作参考手册.md`，工程镜像从仓库根解析 `production/art_pipeline/PS_MCP_操作参考手册.md`。在作业记录中保存实际手册路径、版本、SHA-256 和当前会话能力快照；两处均不存在或哈希不一致时不得以历史记忆继续操作。手册负责通用效率、抠图、Alpha、路径、单引擎、超时回退和视觉/技术验收；本 Skill 继续负责需求、来源和专门生产 Skill 路由。实时目录只允许执行 supported 能力，手册本身不增加操作授权。

执行前读[对话任务独立额度](references/task-budget.md)：新对话完整新额度，其他对话的资产历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于旧预算说明。

实际使用原生 Photoshop MCP 前，确认 Bridge 已连接及所需命令可用，并协调本机同一时刻只有一个任务操作 Photoshop；不再调用排队或租约接口。同任务当前图须保存、完成技术及真实视觉检查并核对当前hash；未审完不得推进下一张。PASS可推进相应依赖；FAIL缺陷已记录且预算耗尽或用户要求封存时，保留候选和累计次数，仅继续独立资产；安全保存可恢复文件和固定审阅快照后，可安全交棒给其他独立任务。释放不是PASS，不解除原图及依赖的阻断、不重置预算；命令在途或结果未知时不得自行交棒。纯准备、生图等待和离线审阅不长期占用桥接，未授权的PS操作不会因连接可用而获得授权。

先查现有资产，再决定真实生产缺项。本入口负责需求、来源权威、复用决策和交接，不承包所有出图操作。

跨设备执行先用 `python -B scripts/art_pipeline/ndc_art.py paths` 解析 `{PLANNING_ROOT}`、`{ENGINE_ROOT}`、`{WORK_ROOT}`、`{DELIVERY_ROOT}`，再用 `skill ndc-generate-characters` 解析当前 Skill 根。Skill 专属模板与脚本只从该根的 `assets/`、`references/`、`scripts/` 相对读取；角色、运行时和过程资产分别从项目索引及各配置根解析。占位符不是字面路径；配置缺失或漂移时停止并重配，不得猜盘符、用户名或相邻目录。

每台设备第一次执行角色风格分析、生成或最终风格自检前，运行 `python -B scripts/art_pipeline/ndc_art.py preflight style-check`。若返回 `missing_user_designation`，明确提醒用户当前设备缺少哪一类完整自检库，并要求用户指定通用角色卡、通用肖像和黑白红角色卡三个目录；在指定并保存前不得用 Skill 内单张参考图、另一台机器路径或相似资产替代完整自检库，也不得把该依赖降级为可选项。完成设备配置后，后续批次直接使用，不重复索要确认。

## C0 需求与资产盘点

1. 读当前项目规则和角色策划／索引，锁定角色身份、请求资产类型、视图或状态、交付规格、用途和现有授权。需求清单是执行锚点，核实后直接推进，不增加逐项用户确认。
2. 在写新提示或调用生成前，按项目配置的正式游戏资源、确认交付和本地正式资产顺序检索；记录路径、角色ID／别名映射、类型、状态／视图、版本、批准依据、SHA-256。文件名相同不等于同人，风格参考和临时占位不算身份源。根角色与检索顺序以项目规则和项目索引为准，Skill 不保存任何设备盘符。
3. 每项只选择一条路线：`REUSE_APPROVED_AS_IS`、`DERIVE_TECHNICAL`、`REPAIR_REQUESTED_SCOPE`、`GENERATE_MISSING`、`BLOCKED_SOURCE_AMBIGUITY`。缺一项不重做整套；存在候选不证明没有正式资产；用户明确重制优先。
4. 原样复用核对真实身份、文件可读性、规格与复制／引用正确性，保留字节、来源和当前证据；不补造历史母图或历史审核。仅在当前需求、来源或已知缺陷确实不兼容时，记录受影响项并转返修。

## C1 分责交接

| 请求 | 执行 Skill | 本次交接终点 |
|---|---|---|
| 缺少已批准身份的全新重要／次要角色 | [身份母版生产](../ndc-character-identity-production/SKILL.md) | 可复用的通用风格身份源及同源面部锚点 |
| 已有身份的角色卡、通用肖像、单次全身状态、指定模块拼版 | [角色资产派生](../ndc-character-asset-derivation/SKILL.md) | 仅请求的资产及技术／视觉证据 |
| 可复用胸像表情库 | [角色表情](../ndc-generate-expressions/SKILL.md) | 合格肖像、真实缺项和适用裁切范围 |
| 222×240／106×120 UI 肖像 | [UI 肖像](../ndc-generate-ui-portraits/SKILL.md) | 历史UI复用结果及新制所需身份来源 |
| 固定场景中的角色入景 | [角色融入场景](../ndc-character-scene-integration/SKILL.md) | 身份源、状态需求及场景引用 |

重要新角色先使用既有 MJ 路线，次要新角色保留跳过 MJ 的快速路线；两者的正式通用风格母版，以及后续普通角色卡和明确触发的黑白红卡，统一按[角色资产网页版生图](references/chatgpt-web-character-generation.md)在受支持的内置 `iab` 或外置 Chrome/Edge 中通过网页版 ChatGPT 生成。网页模型默认选“极高”，没有则选择当前账号实际可用的最高档；已授权生产在冻结包通过后直接上传提交，不逐角色询问。已有批准身份不重新设计。普通角色卡默认锁定整卡生成；用户明确要求4K或明确要求独立模块生成／拼版才走模块化，4K才强制3840×2160。视频及动画分支不在本轮静态生产中主动展开；黑白红资源保留供明确请求时使用。

## 执行、续作与交付

- 只规划或维护 Skill 不授权生图。用户已要求 Codex 执行、批量生产或工程衔接时沿用已有授权；不重复请求开始确认。
- 生产或跨阶段续作读取 [角色合同](references/character-contract.md)、[预算与依赖](references/production-budgets-and-dependencies.md) 和 [持久生产记录](references/production-record.md)。交接同一任务记录与剩余预算，不能另起阶段重置失败。
- 网页三类正式资产每次提交前运行 `scripts/build_chatgpt_web_character_packet.py`，回收网页原始下载后运行 `scripts/validate_chatgpt_web_character_receipt.py`。一个角色同一 production revision 使用专用网页对话；任何引用、完整提示词、上传顺序、对话 URL 或哈希缺失都不提交，网页故障不静默回退其它生图后端。门禁全部满足后自动选择最高可用网页档位并立即提交，不要求用户回复“发送角色名”或再次确认已经交办的单个角色。浏览器按用户指定及当前健康、登录和可追溯状态动态选择，不固定先内置后外置，不同已登录 ChatGPT 账户均可继续任务。原记录可访问时只接续原对话；账户隔离导致原记录确实不可访问时，以 `account_record_unavailable` 保留原 attempt，在新账户新建专用对话并以相同输入／提示词哈希重新生图。
- 肖像可保留原生截肩。表情目标裁切不适配时，用 [一次人工适配交接](references/character-contract.md#人工肖像适配) 交人工处理；接收合格人工完成源后继续，不增加自动补肩。
- 纯复用不重做创作分析。确需新图时由执行 Skill 在构思和实际提交前接入 `ndc-visual-description`，仅复核变化项。
- 旧 `assets/`、`scripts/` 和专业 `references/` 保留为两个执行 Skill 的共享权威资源，旧脚本路径仍有效。按当前阶段加载，不默认通读整个旧资料库。

输出需求覆盖、复用／生产缺项、来源权威、实际阶段、预算消耗与阻断项。技术检查或计划编制完成不表示实际图像已生成；通过自检不冒充用户已选择该字节版本。
