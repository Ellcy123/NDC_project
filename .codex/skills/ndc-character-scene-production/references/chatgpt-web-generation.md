# 网页版 ChatGPT 生图

本页只用于人物入景第二阶段的正式像素生成。Terra/xhigh 仍是生产编排、判断与验收任务；像素生成后端固定为已登录的 `chatgpt.com` 网页版 ChatGPT。浏览器载体可为 Codex 内置 `iab`，或 Computer Use 当前支持且用户已指定/授权的外置 Chrome、Edge；不得改用 Codex 图片生成工具、`imagegen`、图片 API、其它站点或其它生图后端来“临时顶替”。

## 会话和输入

- 使用 Computer Use 当前文档支持的可见浏览器入口。用户指定 `iab`、Chrome 或 Edge 时优先使用该浏览器；未指定时选择当前健康、已登录且可追溯的受支持浏览器。只接受 `https://chatgpt.com/` 域名；不要输入、索取、记录或保存账号密码、验证码、Cookie 或令牌。登录、验证码、地区限制或账号门禁需要人工处理时，记录 `WAITING_MANUAL`，只阻断依赖该网页提交的分支。
- 提交前浏览器不可用时，可切换到另一受支持浏览器并打开同一专用对话 URL；这不是模型 attempt。网页已经收到消息或状态未知时，换浏览器只能用于核实同一对话，不能重发。上传仍按 Computer Use 当前确认规则在操作前处理，浏览器授权不等于文件上传授权。
- 每个完整 `scene_id + revision` 建立一个专用 ChatGPT 对话，同场角色、状态和返修都在该对话内保持整场上下文。不同 revision 新建对话，旧对话只读保留。不得把不同场景混在同一对话，也不得按角色拆成彼此不知情的网页对话。
- 每次提交都重新上传实际三引用，顺序固定为：1 `local-whitebox-crop`，2 `untouched-full-scene`，3 `approved-character-card`。等每个附件在网页上显示完成后再提交。粘贴当前 `PROMPT_STYLE_BINDING_GATE: PASS` 对应的完整提示词原文；不得依赖“同上”“按上一张”或网页历史自动补足缺失约束。角色卡和固定风格块共同承担风格锁定，任何一个都不能因网页已有上下文而省略。
- 提交前核对对话 URL、scene/revision、pose、三引用顺序及 SHA-256、提示词 SHA-256、网页附件状态和目标工作目录。浏览器页面中的文件名、缩略图或成功提示不能代替本地哈希。

## 记账、提交和回收

先运行重要度与提示词风格门禁，再用 `python scripts/build_chatgpt_web_submission_packet.py --contract <source.json> --out-dir <scene_revision_attempt_dir> --browser <iab|chrome|edge>` 生成不可覆盖的提交包。包中包含按序重命名的三引用、完整提示词、重要度配置、两份门禁及 `submission-manifest.json`/`receipt-draft.json`。操作者逐项对照该目录上传，不能临时从别处选图或重新拼提示词。

随后运行流水 `guard`，再在原 journal 的对应 formal job 写入 `attempt`。新提交的 `submission.tool` 固定为 `chatgpt_web_browser`，`submission.operation` 固定为 `generate_image`；`arguments` 至少保存 `scene_id`、`revision`、`pose_ids`、`conversation_url`、`browser: iab|chrome|edge`、submission manifest 路径/哈希、prompt/importance profile 哈希、按上传顺序排列的引用 role/path/sha256，以及 `backend: chatgpt_web`。历史 `chatgpt_web_iab` 记录继续兼容审计。写入 pending 后只提交一次。

网页明确收到消息即视为已经提交并消耗一次真实 model attempt。生成失败、拒绝或无图也按真实结果 resolve；页面仍在生成、断线或工具回执不清楚时记 `unknown`，回到同一标签页和同一对话核实，禁止刷新后重发、另开对话或改用 Codex 生图。一个场景对话同一时刻只允许一个未决提交。

生成完成后：

1. 在网页中打开对应生成结果，使用网页提供的下载动作取得原始图像；不使用屏幕截图、浏览器缩略图、复制粘贴的预览或系统重采样版本作为生产源。
2. 保存到 packet 分配的 `work_directory` 内，文件名包含 scene、revision、pose、attempt 和 candidate 序号；不直接进入 `最终交付`。
3. 计算下载文件 SHA-256，实际打开检查可读性、尺寸和候选对应关系，再补全提交包中的 `ndc-chatgpt-web-generation-receipt/v2` 回执。回执除 task/thread ID、scene/revision、pose、submission ID、ChatGPT conversation URL、提交/完成时间、candidate 序号、下载路径/哈希和固定 backend 字段外，必须逐字匹配 submission manifest 中的 prompt、importance profile 与三引用路径/哈希。旧 v1 仅可用 `--allow-legacy-v1` 审计历史记录，不得用于新提交。
4. 运行 `python scripts/validate_chatgpt_web_receipt.py --receipt <receipt.json> --output <gate.json>`；只有 `CHATGPT_WEB_GENERATION_GATE: PASS` 才能用回执绝对路径作为 journal `resolve` 的 evidence。随后先按 H0/H1/H2/H3 对上下文结果作一次分流，再决定提取、局部修复或重试；同一真实观察可引用到多个相容门禁，不能重复截图充当重复审核。网页“已生成”或回执验证只证明来源与文件身份，不构成艺术 PASS。

## 停止与恢复

网页限流、上传/下载故障、会话失效或生图能力不可用时，同一原样操作最多重试一次；再次失败须缩小诊断、切换受支持浏览器或等待恢复。提交前切换浏览器不计模型 attempt；提交已发生或结果未知时，只在同一专用对话核实。不得切回 Codex 图片生成或图片 API。保存当前 URL、browser、submission ID、pending/unknown 状态和已下载候选，继续不依赖该结果的场景记录、离线审阅或其它独立工作。确认原对话没有结果后，才按 journal 规则进入下一次尝试。
