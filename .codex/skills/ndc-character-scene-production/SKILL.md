---
name: ndc-character-scene-production
description: 用 Terra 极高智能接收已通过的 NDC 整场景深与白模方案，并在受支持的内置或外置浏览器中通过网页版 ChatGPT 完成正式角色生图，再执行提取、接触合成、全场验收和图层交付。用于 Astra 参考阶段交接后的生产及有限返修；不重新设计整场参考，不按角色拆任务。
metadata:
  category: art/character/scene-production
---

# 人物入景：正式资产生产

本 Skill 只接收已经 `READY` 的整场参考。Terra `gpt-5.6-terra / xhigh` 是同一场景的唯一生产编排与验收者；正式像素只在受支持且已登录的 `chatgpt.com` 可见浏览器中生成，载体可为 `iab`、Chrome 或 Edge。禁止 Codex 图片生成工具、图片 API、其它站点和其它生图后端。用户手工在 ChatGPT 生图时，本 Skill 只输出提示词；已授权自动生产则不逐角色索要“发送”确认。

执行前读取：

1. [效率与状态合同](../ndc-character-scene-integration/references/efficiency-and-state-contract.md)；
2. [网页版 ChatGPT 生图](references/chatgpt-web-generation.md)；
3. [执行档位与单入口终结](../ndc-character-scene-integration/references/execution-profiles-and-finalizer.md)；
4. 只有进入提取时再读[非生成提取能力门禁](references/non-generative-extraction-capability-gate.md)与当前《PS MCP 操作参考手册》；
5. 执行前读[对话任务独立额度](references/task-budget.md)。

不要在启动时重读全部入景资料。需要动作连续性、三人背影、尺度、接触、阴影或交付细节时，再从[共享入景 Skill](../ndc-character-scene-integration/SKILL.md)的索引加载对应 reference。

## 生产边界

- 冻结 scope 中全部 `case / snapshot / actor_pose_id` 的并集是整场范围。默认先生成、回收、审核并冻结全部必需角色/状态或合法复用源，再统一提取；真实网页等待、回收受阻或有证据的调度原因允许先处理已就绪角色。例外记录已就绪、未就绪、执行范围与恢复顺序，不能删除缺项或把局部当整场完成。
- 按正确白模校正正式结果的整体尺度、落点、头身比和遮挡属于本阶段。只有白模本身的动作前提、主朝向、承托类型、粗略深度或解剖覆盖范围错误，才附证据 `return_stage: reference`。
- 用户是需求与结果审核者，不是默认 Photoshop 操作员。不得把抠图、蒙版、通道、修边、保存或导出劳动转交用户；登录、验证码等平台强制节点例外。Computer Use 补位需要当前任务另有明确授权。
- 点击后 active 状态必须头部自然转向镜头、双眼直视镜头；idle 与纯剧情人物交流按剧情。三人及以上快照继承已通过的非 active 前景/近中景背影构图，并在正式候选和最终合成重验。

## 人体覆盖

每个 actor/pose 继承 reference gate 的覆盖模式：

- `FULL_IN_FRAME`：正式独立母层完整头到脚；
- `SCENE_OCCLUDED`：先保留完整头到脚母层，再用原场景像素遮挡；
- `FRAME_CROPPED_FOREGROUND`：只需生成并审核头部到自然画框出口的完整可见解剖，同时绑定画外尺度、重心与承托证据；不为永远不可见的腿脚消耗生成与提取。

不得用出框掩盖缺手、缺肘、断头、关键道具截断或错误支撑。模式变化属于新 revision。

## 网页提交

1. 领取唯一场景后先运行流水 `guard`，保存当前 revision gate；旧任务或重复消息不得重复领取。
2. 为 `scene_id + revision` 建立一个逻辑场景工作区。它可以是一个物理窗口中的标签组，也可以是可追溯的浏览器/session 标签集合；不强制独占 OS 窗口。
3. 先做一次真实轻量 canary；健康与 canary 均通过后工作区才为 `READY`。失败载体进入 `QUARANTINED`，不让每个角色重复探测。默认 WIP 为 3，限流时降为 1–2。
4. 每个角色或不可分割状态组使用独立 ChatGPT 对话。不同角色及同角色不同 pose 可并发；同一对话只允许一个未决 attempt，同一 actor/pose 不得跨对话重复占用。
5. 每次尝试按固定顺序重新上传三份独立引用：`local-whitebox-crop → untouched-full-scene → approved-character-card`，再粘贴完整提示词。不得合并、少传、换序或依赖历史。用 `confirm-uploads` 留存三个独立缩略图和本地哈希核对后，只点击一次发送；网页明确接收后立即 `mark-submitted`。
6. 风格描述唯一权威是 `assets/original-user-style-description.txt` 的原始 UTF-8 字节。每次提示词编辑后运行[风格绑定门禁](references/prompt-style-binding-gate.md)；关键语义和原字节是硬门禁，网页空格/换行/显示格式正常化是软记录。
7. 页面收到提交即记一次真实 model attempt。提交未知只回原 URL 核实，不重发；账户隔离确实无法访问旧记录时，才按网页合同封存 `account_record_unavailable` 并建立单一后继链。
8. 新 revision 立即 `supersede` 旧工作区：取消未提交 packet；已提交/未知结果只回收与隔离，不再继续旧引用。恢复时只读 `manage_scene_web_window.py resume` 的紧凑条目。

第 4–6 次模型尝试只处理 H0 身份、关键动作或严重结构问题；同一缺陷连续两次仍存在，必须换方法或封装，不得继续加强同类提示词。

## 回收与提取

- 使用网页提供的下载动作取得原始图；点击前用 `scripts/download_receipt.py` 加锁并冻结目录快照，事件成功只读取 `PlaywrightDownload.path()`，事件超时则只认领点击后唯一稳定的目录 delta，禁止 `suggestedFilename()`、最近文件猜测和二次 Save。保存 URL、submission、候选序号、download snapshot／receipt、原始文件 SHA-256 和 v4 回执。`pageAssets.bundle()` 是可追溯的精确资源恢复候选但不是正式 Save 回执；截图、缩略图、缓存恢复件均不是正式下载源。每个结果先做 H0/H1/H2/H3 提取前视觉分流，再继续其它单元。
- 第一次实际 Photoshop MCP 前，完整读取当前手册并记录实际路径、版本、SHA-256、Bridge 与实时命令目录。相同手册/会话/目录可复用能力矩阵；任一变化立即重测。只执行实时 `supported` 能力，不调用已退役 queue、proxy、broker、lease 或 watchdog。
- 一个按钮失败只终止该路线。同一原样命令最多重试一次，随后继续其它适用且 supported 的非生成路线。第一份 H0 可用 RGBA 立即形成 Pixel Proof Preview；第一份正式 RGBA 立即停止该层其余路线。没有正式 RGBA 时，只有所有适用路线均有实测、`NOT_APPLICABLE` 或 `UNSUPPORTED` 证据，才可登记整体能力失败。
- 实际得到可打开的非生成 RGBA 但提取不完整或把握不足时，保留原图、尝试 RGBA、可恢复 PSD、蒙版/路径/动作证据、Alpha 多底预览与缺陷，标记 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW`，继续 provisional 合成、XY、重建和整包检查。源文件及完整证据留在 `{WORK_ROOT}`；若其中一张已被明确选为交付目标，可将其字节一致副本登记到 `{DELIVERY_ROOT}` 的 `交付候选` 隔离层，但不得覆盖旧版本或满足 PASS。
- 交棒或封装前保存可恢复 PSD 与审阅快照，实测 Photoshop `docs0`、本任务命令 `queue0`、未知命令 0，并记录 ownership `RELEASED`。这只是原生 MCP 所有权握手，不是恢复旧 queue 服务。

## 门禁与终结

提交硬门禁只覆盖修订、scope、身份、关键动作/朝向/尺度/承托、三引用、原版风格关键语义、未决去重和 superseded 来源。正式硬门禁覆盖会导致身份/剧情/结构/Alpha/UI/文件/XY/来源错误或不可重建的问题。容差内姿势、发丝/白边、低重点纹理、轻微阴影/软承托、永久画外腿脚和重复证据格式问题按 H1–H3 记录，不为润色追加模型尝试。

时间盒使用 active time，网页、登录、验证码、网络和传输等待单列：10 分钟 Layout Preview，首个可用 RGBA 后 15 分钟 Pixel Proof，30 分钟无 Pixel Proof 强制换方法，60 分钟停止低价值润色并运行场景级 finalizer。结果只可为：

- `FORMAL_CANDIDATE`：正式硬门禁全部通过，等待归档/用户审核语义；
- `PROVISIONAL_SCENE_PACKAGE`：核心身份、动作与结构可用，软缺陷或证据缺口明确；
- `H0_BLOCKED_PACKAGE`：只有真实 H0 阻断，保留最佳候选与单一根因。

`formal` 仍必须通过 post-generation ledger、真实 UI、身份/风格、Alpha、完整 scope、XY/图层和原尺寸逐像素重建。finalizer 只生成过程预览、确定性 `package-index.json` 和当前状态，不把技术通过写成艺术批准。工作证据及 provisional/H0 包留在 `{WORK_ROOT}`；每张由当前任务明确选定准备交付的图片随后用共享 `delivery_candidate_registry.py` 登记到 `{DELIVERY_ROOT}/.../交付候选/<candidate-id>`，其中包括明确作为交付件的参考图。候选覆盖是审计和制作进度首选，不是正式 PASS；复核失败先原位标记为可考虑移出，不自动删除。只有另行通过并转正的资产进入已批准正式资产区或允许工程同步。

当前场景结束后只调用一次 `claim-next`。有 READY 场景就继续；没有就结束本轮，等上游发布新 READY 后唤醒同一任务。不得常驻轮询或建立后台 heartbeat 服务。用户明确暂停时只做被要求的分析或 Skill 维护，不恢复资产生产。
