---
name: ndc-character-asset-derivation
description: 从 NDC 已批准角色身份源派生通用角色卡、肖像、单次全身状态与明确请求的模块拼版，并完成技术整备和交付检查。用于已有身份的资产生产或局部返修；不重新设计身份、不制作表情库或人物入景。
metadata:
  category: art/character/derivation
---

# NDC 角色资产派生

执行前读[对话任务独立额度](references/task-budget.md)：新对话完整新额度，其他对话的资产历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于旧预算说明。

实际使用原生 Photoshop MCP 前，确认 Bridge 已连接及所需命令可用，并协调本机同一时刻只有一个任务操作 Photoshop；不再调用排队或租约接口。同任务当前图须保存、完成技术及真实视觉检查并核对当前hash；未审完不得推进下一张。PASS可推进相应依赖；FAIL缺陷已记录且预算耗尽或用户要求封存时，保留候选和累计次数，仅继续独立资产；安全保存可恢复文件和固定审阅快照后，可安全交棒给其他独立任务。释放不是PASS，不解除原图及依赖的阻断、不重置预算；命令在途或结果未知时不得自行交棒。纯准备、生图等待和离线审阅不长期占用桥接，未授权的PS操作不会因连接可用而获得授权。

从已批准身份源制作真正缺少的请求资产；原角色入口保存共享提示、素材及脚本，本 Skill 负责实际派生、技术整备与交付。

## D0 进入条件

- 读 [持久生产记录](references/production-record.md)、共享 [角色合同](../ndc-generate-characters/references/character-contract.md) 及 [预算与依赖](../ndc-generate-characters/references/production-budgets-and-dependencies.md)，沿用需求入口的盘点、批准源和同一job。无盘点先补查，无身份源交 [身份生产](../ndc-character-identity-production/SKILL.md)，不得文本重建同一角色。
- 用户明确选定资产时停止该资产艺术搜索，只执行已有授权内的必要技术整备。新图仅在已获Codex执行／批量授权后制作；规划与维护不授权生图。
- 非复用任务在可见意图确定及提交组装后使用 [画面描述](../ndc-visual-description/SKILL.md)，变化只检查受影响项。

## D1 按请求进入一个分支

| 分支 | 只读取所需资源（共享根 `../ndc-generate-characters/`） |
|---|---|
| 普通整卡 | `references/prompt-library.md` 6.2、`scripts/verify_locked_prompt.py`；逐字导出 `character-card-default`，不得擅加规格词 |
| 通用肖像 | `references/prompt-library.md` 7及7.1；默认 `portrait`，已有身份污染证据时使用独立锁定 `portrait-single-reference`；执行细则见下方链接 |
| 单次全身状态 | 提示库1.1既有状态及1.2；从批准通用角色卡只改明确状态，表情库交专门Skill |
| 明确4K或明确独立模块／拼版 | `references/modular-character-card.md`；先锁本次请求的模块子集。单模块只生产该项；整卡拼版才要求整卡所需模块齐备 |

分支执行和肖像参考合同见 [派生细则](references/asset-derivation.md)。普通卡默认一次整卡，失败在同一有界预算中返修；“正式／高清”不自动触发模块化。4K整卡固定3840×2160，单独模块按当前约定或已有同组模块规格交付，不强制套用2K/4K整卡画布。黑白红资源保留于共享库，只在另有明确动画资产请求时使用，不主动进入静态交付。

## D2–D3 艺术、技术与交付

1. 先查身份、必需视图／内容、结构、风格、纹理和当前状态；读共享 `references/style-self-check.md`、`references/style-analysis-protocol.md`。适用证据可继承，新增／变化风险仍真实查看。背面模块的正脸五官在本图不可见，绑定批准身份源并检查实际可见的后脑、耳位、后领、体型和服装背部；不要求回头、露正脸或编造本图五官PASS。
2. 艺术通过后冻结，按共享 `references/post-generation-normalization.md` 做必须的背景处理、等比缩放、画布位置与边缘检查。同任务PS当前图完整保存、完成真实自检并核对hash；未审完不推进下一张，PASS才推进相应依赖，FAIL按全局队列有据封存后仅继续独立资产；跨任务安全挂起释放按上方队列协议执行，技术失败仍只返责任技术阶段。
3. 整卡或肖像输出读取共享 `references/execution-gates.md` 的对应交付合同，并使用原 `scripts/audit_character_delivery.py`、`validate_delivery_receipt.py`。单模块或单次状态输出不伪装为card/portrait：按本次输出规格实测尺寸、模式、完整主体/边缘、缩放及当前背景要求，用真实阶段视觉记录、适用风格/纹理检查和持久记录 `check --job <当前job>` 核验请求子集及其依赖。只有请求整卡拼版才检查三视图对齐、整卡版式和全套模块；未请求的头部/鞋/细节不构成缺项。机械PASS不代表视觉PASS；需求及父源变更必须使受影响派生证据失效。
4. 需要表情集时，交合格肖像与当前适用裁切范围。原生截肩仍是合法通用肖像；表情裁切不适用交人工完成一次适配，收到合格人工源才继续，详见共享角色合同。禁止自动补肩。

输出实际资产路径、源和版本、技术／视觉状态、消耗与缺项。只完成卡不能称肖像或表情已完成；候选留作过程历史，正式文件按项目规则归档。
