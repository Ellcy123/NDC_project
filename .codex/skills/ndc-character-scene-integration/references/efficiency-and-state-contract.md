# 人物入景效率与状态合同

本页是四个入景 Skill 共用的运行约束。它缩短主 `SKILL.md`，但不削弱身份、剧情、可见结构、来源、真实 Alpha、实际 UI 或工程重建门禁。

## 1. 状态与修订

场景只有在冻结 scope、参考交接校验和流水 `guard` 都指向同一 `scene_id + revision` 时才是 `READY`。参考阶段用 `validate_reference_handoff.py` 产生最近 15 分钟内的 `ndc-character-scene-ready-revision-gate/v1`；正式提交包必须绑定该文件。新 revision 发布后，旧浏览器工作区立即执行 `supersede`：未提交的 `PREPARED/UPLOAD_CONFIRMED` 自动取消，已提交或未知结果只回原对话核实并隔离，不得继续提交旧引用。

`READY` 是允许开始网页副作用的硬门禁；缺少重复截图、报告排版或非关键 metadata 不影响参考准备，但不能伪造 `READY`。流水数据库继续负责唯一领取与 revision fence，浏览器工作区负责单场景防串包；两者均须通过。

## 2. 人体覆盖分类

每个 actor/pose 只取一种：

| 模式 | 硬要求 |
|---|---|
| `FULL_IN_FRAME` | 保留并审核完整头到脚母层 |
| `SCENE_OCCLUDED` | 即使腿脚被家具或人物遮挡，也保留并审核完整头到脚母层，再用原场景遮挡 |
| `FRAME_CROPPED_FOREGROUND` | 不要求永远在画外的腿脚；必须完整生成并审核头部至自然出框边界的全部可见解剖，且保存画外尺度、重心和承托证据 |

镜头出框不能用于掩盖缺手、缺肘、断头、关键道具截断或错误支撑。白模和终结清单都记录模式；模式变化属于实质修订，会使相关缓存与旧 gate 失效。

## 3. 三引用原子提交

每次真实尝试都重新上传三份独立图片，固定顺序：

1. `local-whitebox-crop`；
2. `untouched-full-scene`；
3. `approved-character-card`；
4. 随后粘贴完整提示词。

不得合并成拼图、沿用上一对话附件、少传、换序或用文本替代。一个浏览器原子操作段完成：认领精确 URL → 逐项上传 → 等三项完成 → 核对三个独立缩略图及本地 SHA-256 → 粘贴提示词 → `confirm-uploads` → 点击一次提交 → 页面明确接收后 `mark-submitted`。中途失去工作区身份、健康、READY 或 attachment 证据时，在点击前取消 packet；点击后未知则只核实，不重发。

固定风格原始字节、`(shirt, jacket, skirt, tie)` 等关键语义和三引用职责属于提交硬门禁；网页仅改变空格、换行或显示排版时按规范化回显记录，不把 UI 格式变化误判成文本语义漂移。

## 4. 逻辑场景工作区与浏览器健康

“场景专用窗口”是逻辑隔离：一个 `scene_id + revision`、一个浏览器/session 身份和多个专用对话 URL。无需强制每场占一个物理 OS 窗口；只要标签页归属、URL、账户别名、scene/revision 和本地 state 可追溯即可。

开始 fan-out 前只运行一次真实轻量 canary，证明标签枚举、DOM/附件入口和动作通道可用；先记录 `HEALTHY`，再记录 canary `PASS`，工作区才变为 `READY`。canary 不提交图片、不计模型 attempt。一次 canary 失败把该载体设为 `QUARANTINED`；缩小诊断、重绑或切换受支持且已授权载体后重新健康检查。不要让所有单元重复相同探测。

默认 `max_open_submissions=3`，网页限流或传输不稳时主动降到 1–2；任何时候都不能超过 state 中的 WIP 上限。同一对话只允许一个未决 attempt，同一 actor/pose 不得跨对话重复占用。

## 5. 提交硬门禁、正式硬门禁与软审阅

提交前只阻断：修订或单元错误；actor/pose/剧情范围错误；三引用缺失、错序或哈希漂移；身份源错误；白模动作、主朝向、尺度或承托有实质冲突；原版风格字节或关键否定词丢失；同 actor/pose 有未决提交；来源已 superseded；浏览器工作区不 `READY`。

正式候选只因会导致实际错误或不可用的问题阻断：身份/服装/状态、人数、关键动作/视线/道具、严重可见解剖、明显漂浮/穿插/比例、无真实 Alpha 或大块背景、关键 UI 遮挡、文件/尺寸、XY/图层不可重建、正式来源不可追溯、提交归属不明。

H1–H3 软问题包括：非交互角色轻微视线、动作含义不变的小姿态偏差、容差内比例、少量发丝/白边/残色、低重点纹理、无漂浮的轻微阴影不足、低可见度软承托、永久画外腿脚、已有真实检查但重复证据字段不完整、网页回显空白格式变化。它们记录后停止低价值润色；不得改写为 H0。

## 6. 尝试止损与最低场景产出

同一缺陷连续两次仍存在，下一次必须换方法或封装，不得继续堆同类提示词。第 4–6 次模型尝试只允许处理 H0 身份、关键动作或严重结构问题；H1/H2/H3 不得消耗这些次数。

- 10 active 分钟内形成带真实 UI 的 Layout Preview；
- 首个 H0 可用 RGBA 到达后 15 active 分钟内形成 Pixel Proof Preview；
- 30 active 分钟仍无 Pixel Proof：强制换已授权路线；
- 60 active 分钟：停止低价值润色，用场景级 finalizer 一次封装为 `FORMAL_CANDIDATE`、`PROVISIONAL_SCENE_PACKAGE` 或有真实 H0 证据的 `H0_BLOCKED_PACKAGE`。

外部网页生成、登录、验证码、网络和传输等待单列，不吞进 active time。`probe` 只用于快速像素证明，不冒充上述正式/待审包。

## 7. Photoshop 所有权与路线缓存

首次 PS 操作仍完整读取当前手册并保存手册 SHA-256 与实时能力快照。相同手册哈希、同一会话能力目录和同一主机连接状态下可复用能力矩阵；命令目录、Bridge、手册或会话变化立即失效。一个按钮失败只终止该路线；正式 RGBA 通过即短路剩余路线，否则继续所有适用且 `supported` 的独立非生成路线。

跨任务交棒及场景封装使用真实 `docs0/queue0` 握手：可恢复 PSD 和审阅快照已保存，Photoshop 实测打开文档数为 0，本任务在途命令数为 0、未知命令数为 0，ownership 标为 `RELEASED`。这不是旧 queue/lease 服务，也不授权 Computer Use 补位；任何在途/未知命令都禁止交棒。

## 8. 恢复、缓存与事件驱动

每次恢复只读 `manage_scene_web_window.py resume` 的一条紧凑记录，再按其中的精确 URL/未决单元/下一动作继续；不重演整段历史。像素与视觉审核缓存以源场景、UI、scope、人体覆盖模式、RGBA、审阅证据及验证合同哈希为键；metadata-only 改动不重审，用户否定或任何实质依赖改变立即失效。

生产任务完成或封装当前场景后调用 `claim-next` 一次；有 `READY` 单元就接续，没有就结束当前轮。上游发布新 READY revision 时再唤醒同一生产任务。不得常驻 heartbeat 轮询、重复查无变化状态或为“保持运行”新建后台服务。

场景终结器写一个确定性的 `package-index.json`，按稳定 layer ID 排序并只绑定内容哈希、XY、质量与输出哈希；时间戳和显示备注不进入该索引。一个 scene/revision 只维护一个当前场景包，后续真实修订产生新 revision，不在同一目录反复制造角色级“最终包”。

## 9. 交付候选、审计与进度

凡当前任务已明确选定、准备作为交付目标的图片，均须在 `{DELIVERY_ROOT}/<类别>/Unit<n>/<资产或场景>/交付候选/<candidate-id>` 登记；这包括明确选定用于交付的参考图。只有 `selectedForDelivery: true` 的图片进入，不能把全部生成结果、普通参考、PSD、提示词、审核截图或完整过程证据批量复制进来。源文件和完整证据继续留在 `{WORK_ROOT}`，候选区只保留字节一致的候选图、`candidate-status.json` 与醒目的状态说明。

用 `delivery_candidate_registry.py register` 登记，角色图/整场图使用 `artifactRole: delivery_candidate`，明确用于交付的参考图使用 `artifactRole: selected_reference`。登记状态从 `DELIVERY_CANDIDATE_PENDING_REVIEW` 开始；它明确不是正式 PASS，`formalApproval` 与 `engineSyncAllowed` 均为 false。同一 `requirementId` 只允许一个 `current` 候选；换图必须显式写 `supersedesCandidateId`，旧候选保留可追溯状态，不覆盖。

审计和制作进度先运行 registry 的 `inventory`，枚举候选区的清单与当前字节，再同冻结 scope 和工作过程台账核对。候选覆盖、复核 PASS、复核 FAIL、正式交付就绪分别统计；有候选只证明该必需产物已有明确交付目标，不证明质量、来源、Alpha、XY 或正式验收通过。

复核不合格先用 registry 的 `review --result fail` 原位记录 `DELIVERY_CANDIDATE_REVIEW_FAILED_MOVE_ELIGIBLE`、原因和证据；失败前不得预先移出，失败后也不自动删除。若后续决定移出，必须保留迁移目标、迁移前后 SHA-256、替代候选链和审计索引。候选不得作为批准身份源、正式资产或工程镜像同步输入。
