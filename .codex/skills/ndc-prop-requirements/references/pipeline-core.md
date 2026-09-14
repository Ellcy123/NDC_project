# NDC 道具五阶段执行核心

本文件只保存五阶段共用且会改变执行决策的规则。各阶段的专业判据仍由对应 Skill 和按需引用的专业细则负责。

## 范围与状态真源

- `scope.required_artifacts` 是不可缩小的审计全集；当前生产、汇报和发布使用一个带 SHA-256 的活动范围修订。所有队列、校验、进度和候选统计必须读取同一修订，排除项只留历史，不能重新进入当前队列。
- `content_archive.json` 保存事实，`batch.json` 保存依赖和当前指针，追加日志保存尝试与状态历史。不要把长篇历史追加到 `next_action`；它只保留最多三条当前动作。
- 生产状态与有效状态分开：文件存在或 `status=PASS` 不等于当前绑定仍有效。进度必须分别报告交付候选覆盖、候选复核通过、有效 PASS、拒收和 provisional。
- 修改状态只能使用带预期旧值的结构化命令。禁止用文本搜索或人工补丁修改大批次中的相邻 artifact。

## 交付候选优先区

只有已经明确选定、预备用于交付的图和它实际使用的选定参考图可以进入 `{DELIVERY_ROOT}/<类别>/<Unit>/<资产或场景>/交付候选/<candidate-id>/`。普通候选、未选图、失败尝试、提示词、PSD、遮罩和未被明确选作交付目标的 provisional 仍在 `{WORK_ROOT}`。

每个交付候选使用独立 revision 目录并带 `candidate_manifest.json`。候选图文件名含 `__DELIVERY_CANDIDATE`，选定参考图含 `__SELECTED_REFERENCE`。状态只使用：

- `DELIVERY_CANDIDATE_SELECTED`
- `DELIVERY_CANDIDATE_REVIEWING`
- `DELIVERY_CANDIDATE_PASS_READY`
- `PROMOTED_FORMAL`
- `REVIEW_FAILED_PENDING_MOVE`
- `MOVED_FROM_DELIVERY_CANDIDATES`

候选不是正式 PASS，不得进入工程接入或正式发布白名单。复核失败时先标 `REVIEW_FAILED_PENDING_MOVE` 并保留；只有明确执行移出动作后才可移动，禁止自动删除。选定参考图是审核目标和来源证据；除非它本身也是必需交付角色，否则不增加交付分子或分母。

审计和续作先读取当前交付候选索引，再查 batch 和工作过程证据。首要进度是“已有交付候选／当前必需交付角色”，其次是“候选复核通过／已有交付候选”，最终是“正式 PASS／当前必需交付角色”。

## 按场景节点交付

`交付候选` 是单个当前目标的状态登记；`节点交付` 是给用户直接审核的完整场景包，两者不得互换。道具节点只在一个 scene/revision 的全部适用阶段资产已经实际形成后建立，固定进入 `{DELIVERY_ROOT}/道具/Unit<n>/节点交付/<scene-id>/`。图片、PSD 源文件和 XY/TXT 必须以 `SC<scene>_<subject>_[state_]map|big|icon|master|prop|psd` 及合同扩展状态尾缀直接平铺在场景根，不得再按类型或 artifact 拆文件夹；JSON、交付候选、HTML／人读清单和审核证据统一隔离在 `_节点资料`，并按交付文件同 stem 归组。只有 JSON 的目录一律失败。

节点范围由 active delivery scope、取得方式、场景／容器关系和每个 subject 的完整角色矩阵推导。每个角色都显式 `REQUIRED` 或带理由的 `NOT_APPLICABLE`；适用母图、状态母图、PSD、Big、Icon、原／定稿场景、直接拾取四态、Map／XY、Type6／Type7、菜单预览、环境叙事和线索都要收齐。共享资产必须把当前精确字节复制进每个使用场景的节点，不能要求用户跨目录拼包。执行合同、模板与校验器见[道具节点交付完整资产合同](../../ndc-prop-delivery-review/references/node-delivery-contract.md)。节点仍是非正式待审层，正式发布扫描必须排除整棵 `节点交付`。

## 增量校验与审核复用

- 日常使用 artifact、scene 或 changed 范围校验；全批 Stage 5 和强制重新哈希只在正式发布边界运行。
- 同一次命令只读取一次 batch、档案、活动范围和场景索引；相同路径只计算一次哈希，相同 artifact 只计算一次审核结果，相同场景只计算一次依赖闭包。
- 审核复用键由当前输出、相关父图、相关事实、验收合同、审核 profile、活动范围和用户拒收版本组成。无关场景成员或无关关系变化不能使已有 Big/Icon 失效。
- 每次像素变化只检查新增风险。H1 使用运行时与 100%，只有风险标志要求时加 200%；H2 使用运行时与 100%，异常才升级；H3 以运行时为主，异常才升级。身份、必要文字、状态、Alpha 语义、阴影归属、Map/XY、直接拾取重建、用户拒收和正式字节仍是硬门禁。

## 调度与前置检查

- 每个场景生成一个紧凑 `scene_packet.json`，只含活动范围哈希、必需角色、就绪项、唯一阻塞、当前父图、当前动作和恢复点。原始审计日志不进入默认上下文。
- 道具流程的默认生图载体是 Codex 内置 `image_gen`，用于独立母版、指定状态、Big、Icon 来源及不新增场景物件的局部生成。唯一网页例外是：实际目标为在已锁定场景或其场景派生容器视图中生成新增物品，例如承载物、容器或环境叙事物品；此时使用已授权、已登录的 `chatgpt.com` 网页版图片生成。单独生成物品后再合成进场景、已有物品的确定性放置／变换、普通 Big／Icon，以及与新增场景物件无关的修图，都不属于网页例外。两条路线均须先实际查阅本地参考并绑定真实提交；提交结果未知或调用失败时保留回执和检查点，不跨路线盲目重发。
- 扣生成额度或修改父图前运行提交预检：artifact 在活动范围内，job/scene/role/取得方式匹配，输入和提示词哈希有效，目标尺寸有效，后端与当前授权一致，已提交或结果未知时不重发。每次新生成、修复或复用还要绑定当前 active scope SHA 的 `ndc-asset-discovery-receipt/v1`：精确 item/state/artifact role，并完整检索 official_runtime、approved_archive、formal_delivery；`CONFIRMED_ABSENT` 才能新生成，`FOUND_USABLE` 必须复用，`FOUND_REPAIRABLE` 必须先修复，未检索／未绑定／不完整／失效都阻断。旧批没有活动 scope revision 时，先显式迁移 receipt，不把历史 checked_roots 冒充为当前检索。
- Photoshop 使用原生 MCP 且本机同时只有一个任务操作。不得恢复旧 queue、broker、lease 或 watchdog。一次连续 PS 会话只做一次手册／能力前检，之后每个动作仍核对当前文档身份；交棒按项目规则保存可恢复 PSD、审阅快照并确认无在途命令。
- 热区先登记 `BODY`、`PROP_SHADOW`、`KEEP_CARRIER`、`EXCLUDE_FOREGROUND` 和四极，再进入路径制作；一次审核板承载运行图、Alpha、棋盘、父图叠加及适用的拾取前后重建，避免重复打开同一像素关系。

## 生产期 Skill 稳定性

批次记录当前五个 Skill 和共用合同哈希。普通改进进入维护清单，不在生产途中改 Skill；只有阻断整个授权范围的执行器缺陷才可在测试、镜像、备份和显式迁移记录完成后升级。数据或单资产错误只修 batch／artifact，不借机重写 Skill。
