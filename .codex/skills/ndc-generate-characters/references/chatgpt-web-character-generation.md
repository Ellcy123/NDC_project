# 角色资产网页版 ChatGPT 生图

本页约束正式 `general-style-fullbody`、`general-character-card` 和 `black-white-red-character-card` 三类艺术生成。生成后端固定为已登录的 `chatgpt.com` 网页版 ChatGPT，以延续项目已确认的角色画风。浏览器载体可为 Codex 内置 `iab`，或 Computer Use 当前支持且用户已指定/授权的外置 Chrome、Edge；禁止改用 Codex 内置图片生成工具、`imagegen`、图片 API、其它站点或其它生图后端顶替。通用肖像、单次状态、表情和 UI 肖像不因本规则自动改换后端；黑白红卡仍只在动画或明确请求分支触发。

## 会话与三类合同

- 每个 `character_id + production_revision` 建立一个专用 ChatGPT 网页对话。该角色本轮的通用风格转绘、角色卡以及被明确触发的黑白红卡在同一对话顺序接续；不同角色或生产 revision 新建对话，旧对话只读保留。
- 用户指定 `iab`、Chrome 或 Edge 时优先使用该浏览器；未指定时选择当前健康、已登录且可追溯的受支持浏览器。提交前可切换浏览器并打开同一专用对话 URL，不计模型 attempt；网页已收到消息或状态未知时，换浏览器只用于核实同一对话，不能重发。用户已授权实际角色生产时，冻结提交包内引用上传及对应提示词提交属于已交办流程，不再逐角色、逐次或逐文件向用户请求“发送”确认；该授权不包含包外文件、其它角色范围或其它外部操作。
- 每次生成仍重新上传当前分支的全部实际引用并粘贴完整提示词，不依赖网页历史、“同上”或上一张图自动补齐。附件逐个显示上传完成后才提交。
- 正式上传顺序严格等于提交包 `submission_order`：
  - `general-style-fullbody / mj-conversion`：`approved-mj-stage-fullbody` → 可选但一旦合同声明就必传的 `same-source-face-anchor` → `general-fullbody-style-reference` → `full-prompt`。
  - `general-style-fullbody / secondary-direct`：`general-fullbody-style-reference` → `full-prompt`；完整角色视觉设定必须已经写入 full prompt。
  - `general-character-card / default-whole-card`：`approved-general-style-fullbody` → 可选同源 `same-source-face-anchor` → 锁定 `full-prompt`。
  - `general-character-card / modular-component`：前述身份源与可选面部锚点后，可追加实际需要的 `approved-same-group-front-module`，最后提交当前唯一模块的完整提示词。
  - `black-white-red-character-card / animation-card`：`approved-general-character-card` → `black-white-red-style-reference` → `full-prompt`。
- “可选”不表示操作者可在网页临时决定省略：引用合同生成后，其角色、路径、顺序和 SHA-256 均冻结；只有上游证据证明该锚点或同组模块不需要时，才使用不含它的合法合同。

## 网页模型档位与自动提交

- 每个专用对话首次正式提交前，以及页面重载、账号状态变化或模型选择可能改变后，读取网页当前模型选择器。默认选择页面显示的“极高”档位；没有“极高”或该档位不可选时，选择当前账号实际可用的最高档位。若选择器锁定但当前档位已经是“极高”或实际最高可用档位，直接继续；不得等待解锁、修改账号设置、绕过限制或切换生图后端。
- 在 submission 记录或同目录工作记录中保存页面实际显示的档位名称；使用回退时同时记录“未提供／不可选极高”和最终最高可用档位。网页档位不等于 Codex 编排任务的 model／thinking 字段，不能用任务配置代替实际网页选择。
- 模型选择、冻结包上传和一次正式提交均是已授权生产的自动步骤。只要当前角色／revision、身份来源、引用合同、提示词和全部前置门禁已确定，就直接执行，不输出“请回复发送某角色”之类的确认门槛。只有登录／验证码必须人工处理、用户明确暂停、或出现会改变授权范围的真实未决选择时才等待；一般偏好问题和逐角色发送不构成等待理由。

## 不可漏项提交包

1. 把当前完整提示词保存为 UTF-8 文本。默认整卡逐字使用锁定全文；通用风格转绘和黑白红卡先用 `verify_locked_prompt.py` 导出或逐字核验锁定基底，当前分支适用纹理模块时再逐字追加该模块，并把“基底 + 模块”的完整文本一次性写入提交包。模块分支保存已经填入唯一模块名称与视角的完整文本。任何组合都在进入网页前完成，禁止在网页临时增删。
2. 建立 `ndc-chatgpt-web-character-submission-source/v1` 合同，填写 `character_id`、`production_revision`、`asset_mode`、`branch`、正整数 `revision`、专用 `conversation_url`、有序 `uploaded_inputs` 以及 `prompt`；每个文件项都使用绝对路径和当前 SHA-256。
3. 运行 `python scripts/build_chatgpt_web_character_packet.py --contract <source.json> --out-dir <character_revision_attempt_dir> --browser <iab|chrome|edge>`。目标目录必须不存在或为空；脚本按提交顺序复制引用和完整提示词，生成不可覆盖的 `submission-manifest.json` 与 `receipt-draft.json`。网页操作者只从此包取文件，不能临时从其它目录挑图。
4. journal 在实际网页提交前记录一次 attempt，新提交固定 `tool: chatgpt_web_browser`、`operation: generate_image`，并保存 `browser: iab|chrome|edge`、manifest、对话 URL、mode/branch/revision、输入与提示词哈希；历史 `chatgpt_web_iab` 记录继续兼容审计。网页明确收到消息即消费一次真实模型尝试；同一对话同一时刻只允许一个未决提交。门禁通过后直接上传并提交，不再插入逐角色用户口令。

## 回收与恢复

生成完成后只使用网页提供的原始下载动作，不使用截图、缩略图、复制粘贴预览或系统重采样图。下载文件保存在当前不可变提交包目录，补全 `ndc-chatgpt-web-character-generation-receipt/v1`，再运行：

```text
python scripts/validate_chatgpt_web_character_receipt.py --receipt <receipt.json> --output <gate.json>
```

只有 `CHATGPT_WEB_CHARACTER_GENERATION_GATE: PASS` 才证明当前候选确实来自指定网页对话、使用了完整有序引用和提示词、且原始下载字节已绑定；它不代表身份、风格、结构、版式或技术验收通过。随后仍执行各阶段原有视觉与技术门禁。

网页限流、登录／验证码、上传下载故障或结果未知时，只阻断依赖该提交的分支。原样操作最多重试一次；再次失败后可在提交前切换受支持浏览器，或保存 browser、URL、submission ID、pending/unknown 状态和已有候选，继续不依赖该结果的工作。恢复时先回到原对话核实，确认没有结果才进入下一尝试；禁止刷新后盲目重发、另开对话或静默切回 Codex 生图／图片 API。
