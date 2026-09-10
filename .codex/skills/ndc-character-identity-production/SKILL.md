---
name: ndc-character-identity-production
description: 制作 NDC 全新角色的身份母版，执行重要角色 MJ 选图与必要精修，再在受支持的内置或外置浏览器中通过网页版 ChatGPT 完成通用风格转绘；次要角色也在网页端快速制作通用风格母版。用于缺少批准身份源的新角色；不制作角色卡、通用肖像、表情或人物入景。
metadata:
  category: art/character/identity
---

# NDC 角色身份母版生产

## Photoshop MCP 强制前置

本 Skill 第一次实际调用 Photoshop MCP 前，必须完整读取当前环境的《PS MCP 操作参考手册》：维护工作区从项目根解析 `PS_MCP_操作参考手册.md`，工程镜像从仓库根解析 `production/art_pipeline/PS_MCP_操作参考手册.md`。在当前作业记录中保存实际手册路径、版本、SHA-256 和当前会话能力快照；两处均不存在或哈希不一致时不得以历史记忆继续操作。手册负责通用效率、抠图、Alpha、路径、单引擎、超时回退和视觉/技术验收；本 Skill 继续负责身份生产、来源和艺术门禁。实时目录只允许执行 supported 能力，手册本身不增加操作授权。

执行前读[对话任务独立额度](references/task-budget.md)：新对话完整新额度，其他对话的资产历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于旧预算说明。

实际使用原生 Photoshop MCP 前，确认 Bridge 已连接及所需命令可用，并协调本机同一时刻只有一个任务操作 Photoshop；不再调用排队或租约接口。同任务当前图须保存、完成技术及真实视觉检查并核对当前hash；未审完不得推进下一张。PASS可推进相应依赖；FAIL缺陷已记录且预算耗尽或用户要求封存时，保留候选和累计次数，仅继续独立资产；安全保存可恢复文件和固定审阅快照后，可安全交棒给其他独立任务。释放不是PASS，不解除原图及依赖的阻断、不重置预算；命令在途或结果未知时不得自行交棒。纯准备、生图等待和离线审阅不长期占用桥接，未授权的PS操作不会因连接可用而获得授权。

输入是已核实的新角色需求与历史资产盘点，输出是可复用的通用风格身份母版及同源面部锚点。已有批准同角色身份时返回需求入口并交派生，不重新设计。

## 开始与续作

- 先读 [持久生产记录](references/production-record.md) 及共享 [角色合同](../ndc-generate-characters/references/character-contract.md)、[预算与依赖](../ndc-generate-characters/references/production-budgets-and-dependencies.md)，沿用同一job及分对话计数的历史记录；缺少盘点先由 [角色入口](../ndc-generate-characters/SKILL.md) 补齐。
- 用户仅要提示词时只输出提示、顺序和判断；已授权Codex批量或实际生产则继续执行。重要新角色使用MJ，次要新角色跳过MJ；两者的正式通用风格母版均按共享[角色资产网页版生图](../ndc-generate-characters/references/chatgpt-web-character-generation.md)在受支持的内置 `iab` 或外置 Chrome/Edge 中通过网页版 ChatGPT 生成，不因浏览器故障切换到其它生图后端。
- 构思与实际提交前使用 [画面描述](../ndc-visual-description/SKILL.md)，仅复核变化项；用户原始提示与明确选图优先，候选不自动变成身份锁。

## I1–I4 身份链

1. 将brief转为可见设计，区分当前硬要求和可后补表情／道具；冻结来源角色与提示版本。
2. 读 [身份生产细则](references/identity-production.md)。重要角色执行MJ全身123与头部可读性门禁，只在需要时补MJ头部；次要角色直接制作通用风格全身母版。
3. 精修必须保留选定设计，必要时合成已选头部并从最终同一张全身裁面部锚点；未可辨认或未通过不能锁身份。完成必需区域修复后记录真实视觉证据。
4. 重要角色将锁定MJ全身按 `general-style-fullbody / mj-conversion` 网页合同转通用风格；次要角色按 `general-style-fullbody / secondary-direct` 网页合同直接生产。每次从不可覆盖提交包按序上传全部参考和完整提示词，下载网页原始结果并取得 `CHATGPT_WEB_CHARACTER_GENERATION_GATE: PASS` 后，再逐项核对具体五官几何、服装、体型和配色。通过后冻结输出与依赖，交 [资产派生](../ndc-character-asset-derivation/SKILL.md)。

## 按阶段读取共享资源

共享资源以 `../ndc-generate-characters/` 为根，保留单一提示和风格权威：只写MJ或转绘提示时读取 `references/prompt-library.md` 对应第2–5节，次要角色读1.1，非锁定提示读1.2纹理模块；MJ决策读 `references/character-rules.md` 第3–5节。需要实际风格审核时读取 `references/style-self-check.md` 和 `references/style-analysis-protocol.md`，使用原 `scripts/make_style_review_tiles.py`，有效同源证据按持久合同继承。

实际生成、编辑或身份交接还适用共享 `references/execution-gates.md` 的来源清单、身份及阶段证据要求；角色卡、肖像、模块拼版和动画专节不属于本阶段。资产引用：MJ两图为共享 `assets/mj-style-reference-1.png` 与 `mj-style-reference-2.jpg`；通用转绘风格为 `assets/general-fullbody-style-reference.png`。网页包使用共享 `scripts/build_chatgpt_web_character_packet.py`，回收后运行 `scripts/validate_chatgpt_web_character_receipt.py`；提示词与实际参考绑定后不得在网页临时修改。

报告已产出母版／候选、身份源与锚点、预算、通过范围和待处理项；不把完成身份母版说成整套角色交付完成。
