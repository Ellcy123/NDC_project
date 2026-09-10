# 网页版 ChatGPT 生图

本页只用于人物入景第二阶段的正式像素生成。Terra/xhigh 仍是生产编排、判断与验收任务；像素生成后端固定为已登录的 `chatgpt.com` 网页版 ChatGPT。浏览器载体可为 Codex 内置 `iab`，或 Computer Use 当前支持且用户已指定/授权的外置 Chrome、Edge；不得改用 Codex 图片生成工具、`imagegen`、图片 API、其它站点或其它生图后端来“临时顶替”。

## 会话和输入

- 使用 Computer Use 当前文档支持的可见浏览器入口。用户指定 `iab`、Chrome 或 Edge 时优先使用该浏览器；未指定时选择当前健康、已登录且可追溯的受支持浏览器。只接受 `https://chatgpt.com/` 域名；不要输入、索取、记录或保存账号密码、验证码、Cookie 或令牌。登录、验证码、地区限制或账号门禁需要人工处理时，记录 `WAITING_MANUAL`，只阻断依赖该网页提交的分支。
- 浏览器载体没有固定先后顺序：按用户指定，以及当时的健康、登录和可追溯状态动态选择。提交前当前载体不可用时，可切换到另一受支持浏览器并打开同一专用对话 URL；这不是模型 attempt。只有当前载体恰为内置 `iab` 且首次明确确认它无法回收已生成结果时，才不继续在该载体重复等待，立即转到已登录**同一 ChatGPT 账户**的健康外置浏览器，打开同一专用对话 URL 验收并执行网页原始下载；不得把这一故障分支扩写成每次任务都要“先内置核验、再外置核验”。该切换只接续原对话，不新建对话、不重新提交，也不新增模型 attempt；外置浏览器未登录同一账户或触发登录／验证码时按 `WAITING_MANUAL` 处理，不输入或搬运凭据。网页已经收到消息或状态未知时，换浏览器只能用于核实同一对话，不能重发。用户已授权实际人物入景生产时，冻结 submission packet 内的三引用上传及对应提示词提交属于已交办流程，不再逐角色、逐次或逐文件向用户请求“发送”确认；该授权不包含包外文件、其它场景或其它外部操作。
- 每个完整 `scene_id + revision` 建立一个专用 ChatGPT 对话，同场角色、状态和返修都在该对话内保持整场上下文。不同 revision 新建对话，旧对话只读保留。不得把不同场景混在同一对话，也不得按角色拆成彼此不知情的网页对话。
- 每次提交都重新上传实际三引用，顺序固定为：1 `local-whitebox-crop`，2 `untouched-full-scene`，3 `approved-character-card`。等每个附件在网页上显示完成后再提交。粘贴当前 `PROMPT_STYLE_BINDING_GATE: PASS` 对应的完整提示词原文；不得依赖“同上”“按上一张”或网页历史自动补足缺失约束。角色卡和固定风格块共同承担风格锁定，任何一个都不能因网页已有上下文而省略。
- 提交前核对对话 URL、scene/revision、pose、三引用顺序及 SHA-256、提示词 SHA-256、网页附件状态和目标工作目录。浏览器页面中的文件名、缩略图或成功提示不能代替本地哈希。

## 网页模型档位与自动提交

- 每个专用对话首次正式提交前，以及页面重载、账号状态变化或模型选择可能改变后，读取网页当前模型选择器。默认选择页面显示的“极高”档位；没有“极高”或该档位不可选时，选择当前账号实际可用的最高档位。若选择器锁定但当前档位已经是“极高”或实际最高可用档位，直接继续；不得等待解锁、修改账号设置、绕过限制或切换生图后端。
- 在 submission 记录或同目录工作记录中保存页面实际显示的档位名称；使用回退时同时记录“未提供／不可选极高”和最终最高可用档位。模型档位文字与 Terra 的 `thinking: xhigh` 是两个不同字段，不得互相冒充。
- 模型选择、冻结包上传和一次正式提交均是已授权生产的自动步骤。只要当前 scene/revision、身份来源、白模、提示词和全部前置门禁已确定，就直接执行，不输出“请回复发送某角色”之类的确认门槛。只有登录／验证码必须人工处理、用户明确暂停、或出现会改变授权范围的真实未决选择时才等待；一般偏好问题和逐角色发送不构成等待理由。

## 记账、提交和回收

先运行重要度与提示词风格门禁，再用 `python scripts/build_chatgpt_web_submission_packet.py --contract <source.json> --out-dir <scene_revision_attempt_dir> --browser <iab|chrome|edge>` 生成不可覆盖的提交包。包中包含按序重命名的三引用、完整提示词、重要度配置、两份门禁及 `submission-manifest.json`/`receipt-draft.json`。操作者逐项对照该目录上传，不能临时从别处选图或重新拼提示词；符合上述授权和门禁后立即完成上传与提交，不另设用户口令。

随后运行流水 `guard`，再在原 journal 的对应 formal job 写入 `attempt`。新提交的 `submission.tool` 固定为 `chatgpt_web_browser`，`submission.operation` 固定为 `generate_image`；`arguments` 至少保存 `scene_id`、`revision`、`pose_ids`、`conversation_url`、`browser: iab|chrome|edge`、submission manifest 路径/哈希、prompt/importance profile 哈希、按上传顺序排列的引用 role/path/sha256，以及 `backend: chatgpt_web`。历史 `chatgpt_web_iab` 记录继续兼容审计。写入 pending 后只提交一次。

网页明确收到消息即视为已经提交并消耗一次真实 model attempt。生成失败、拒绝或无图也按真实结果 resolve；页面仍在生成、断线或工具回执不清楚时记 `unknown`，回到同一标签页和同一对话核实，禁止刷新后重发、另开对话或改用 Codex 生图。一个场景对话同一时刻只允许一个未决提交。

生成完成后：

1. 在网页中打开对应生成结果，使用网页提供的下载动作取得原始图像；不使用屏幕截图、浏览器缩略图、复制粘贴的预览或系统重采样版本作为生产源。
2. 保存到 packet 分配的 `work_directory` 内，文件名包含 scene、revision、pose、attempt 和 candidate 序号；不直接进入 `最终交付`。
3. 计算下载文件 SHA-256，实际打开检查可读性、尺寸和候选对应关系，再补全提交包中的 `ndc-chatgpt-web-generation-receipt/v2` 回执。回执除 task/thread ID、scene/revision、pose、submission ID、ChatGPT conversation URL、提交/完成时间、candidate 序号、下载路径/哈希和固定 backend 字段外，必须逐字匹配 submission manifest 中的 prompt、importance profile 与三引用路径/哈希。旧 v1 仅可用 `--allow-legacy-v1` 审计历史记录，不得用于新提交。
4. 运行 `python scripts/validate_chatgpt_web_receipt.py --receipt <receipt.json> --output <gate.json>`；只有 `CHATGPT_WEB_GENERATION_GATE: PASS` 才能用回执绝对路径作为 journal `resolve` 的 evidence。随后先按 H0/H1/H2/H3 对上下文结果作一次分流，再决定提取、局部修复或重试；同一真实观察可引用到多个相容门禁，不能重复截图充当重复审核。网页“已生成”或回执验证只证明来源与文件身份，不构成艺术 PASS。

## 停止与恢复

网页限流、上传故障、会话失效或生图能力不可用时，同一原样操作最多重试一次；再次失败须缩小诊断、切换受支持浏览器或等待恢复。收图恢复依据当前载体的实际故障动态处理，不预设固定核验顺序；当前载体为内置 `iab` 且首次明确无法收图时，直接切换到同一账户的健康外置浏览器，不消耗第二轮重复等待。提交前切换浏览器不计模型 attempt；提交已发生或结果未知时，只在同一专用对话核实。不得切回 Codex 图片生成或图片 API。保存当前 URL、browser、submission ID、pending/unknown 状态和已下载候选，继续不依赖该结果的场景记录、离线审阅或其它独立工作。确认原对话没有结果后，才按 journal 规则进入下一次尝试。
