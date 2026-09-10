# Photoshop MCP 高效高质量操作参考手册

> 版本：v2.6
>
> 更新日期：2026-09-11（Asia/Shanghai）
>
> 适用范围：NDC 道具、人物、场景、UI、热区、透明提取、局部修图、构图变换、规格整理和一般 Photoshop MCP 图像任务。

## 0. 手册目标与最高原则

本手册解决两个问题：

1. 在操控 Photoshop MCP 时尽量减少无效往返、重复预览和低价值手工描边；
2. 在提高效率的同时，保证输出仍通过任务对应的技术检查、视觉检查和项目门禁。

执行优先级固定为：

1. 先确认任务目标、来源、保护区域和允许改变的内容；
2. 先判断是否真的需要 Photoshop；
3. 优先原生 Alpha、语义选择、安装动作和非破坏蒙版；
4. 路径只处理硬边局部、权威钢笔轮廓或正式热区；
5. 机械尺寸、框幅、坐标和模板工作尽量交给已批准的确定性脚本；
6. 每次修改都必须能回退，输出必须经过真实视觉检查；
7. 技术成功、命令成功、出现透明像素、棋盘格或哈希一致都不能单独证明图片质量通过。

严禁把以下结果称为精确抠图：

- 用矩形或粗略多边形包住主体；
- 从错误选区直接生成工作路径；
- 由模型根据缩略图猜出大量坐标；
- 用上百个没有控制柄的直角锚点描整圈；
- 仅检查选择区包围框；
- 仅看到透明背景或 Alpha 非零；
- 仅收到 Photoshop 动作成功返回。

## 1. 权威顺序与适用边界

### 1.1 权威顺序

发生冲突时按以下顺序执行：

1. 用户对当前任务的明确要求；
2. NDC 项目底层规则和当前任务适用 Skill；
3. Photoshop MCP 实时 host、state、capability、command describe 结果；
4. 本手册；
5. 历史快照和旧操作记录。

本手册不能把实时目录中 unavailable、unverified、experimental 或 requires_user 的能力改成自动可用。

用户默认是需求与结果的决策者、审核者，不是 Photoshop 生产操作员。`requires_user` 只描述命令的自动化状态，不等于用户已经同意承担该步骤；除非用户对当前资产主动明确选择亲自操作，或明确指定人工制作人员，否则不得把抠图、Select and Mask、色彩范围、通道、蒙版、笔刷修边、保存导出等生产劳动交给用户，也不得等待用户完成后才继续其它独立工作。

### 1.2 原生 MCP 单引擎规则

- 旧 ndc-photoshop-queue 已退役，不再调用 queue、proxy、broker、lease 或 watchdog。
- 本机所有客户端共享一个原生 Photoshop 执行引擎；同一时刻只允许一个任务修改 Photoshop。
- 并发修改通常返回 NATIVE_COMMAND_BUSY。遇到忙碌时不抢占、不循环重试。
- 人工正在操作 Photoshop 时不得接管。
- 新任务准备使用 Photoshop MCP 时，必须先执行第 3.1.1 节的陈旧自动文档检查；只释放来源可证明为自动任务且已异常遗留的文档，人工打开或来源不明的文档一律保护。
- 交棒前保存可恢复 PSD 或审阅快照，并确认没有在途、未知或未核实命令。
- 修改命令在超时、断线或返回未知状态后不得自动重发；先读取 host、state、history 和已产生文件判断命令是否已经执行。

### 1.3 不允许的替代

- 未经用户对当前任务明确授权，不得用鼠标、键盘、Computer Use 或屏幕坐标点击替代 Photoshop MCP。
- 不得用生成式图片工具伪装成抠图、Alpha、确定性变换或像素修复。
- 不得用 Photoshop、代码、OCR 或文字图层补写 NDC 道具的标题、日期、数字、签名、印章或正文。
- 不得覆盖唯一原文件；任何破坏性操作必须在可恢复副本上执行。

## 2. 当前本机能力快照

以下是 2026-09-10 的本机快照；每个新任务仍以实时查询为准。

- Photoshop：Adobe Photoshop (Beta) 27.11.0
- Photoshop MCP：2.0.1
- Bridge 协议：ps-mcp-bridge/3
- 命令总数：104
- supported：89
- experimental：2
- requires_user：11
- unavailable：2
- 能力分类：supported 22、experimental 3、requires_user 10、unavailable 19

当前关键事实：

- document.open_allowed 已是 supported，可在配置允许根目录内使用绝对路径打开文件。
- document.close 已是 supported，但关闭本身不等于保存；只有完成第 3.1.1 节的所有权、恢复副本与未知状态检查后才可自动调用。
- document.save 仍是 requires_user；自动留档优先导出 PSD/PNG 副本。
- selection.select_subject 没有独立目录命令。
- Photoshop 已安装动作集“主体和背景”，其中“选择主体”和“移除背景”可由 supported 的 action.play 执行。
- Select and Mask 与 Color Range 仍是 requires_user。
- 当前目录不能创建、删除或绘制图层蒙版内容；只能读取或设置已有蒙版的密度和羽化。
- 当前目录没有 selection-to-new-layer 或 layer-via-cut。
- `layer.place_file` 已是 supported：可把允许根内的 Photoshop 兼容文件置入当前文档，生成嵌入式智能对象层，并保留源 RGBA；它不是蒙版创建或跨文档剪贴板。
- 智能对象现支持上述嵌入式置入；仍不支持重链接、内容编辑、替换或把选区自动拆成新图层。
- `photoshop_advanced_execute` 仅白名单允许无参数 deselect 与 invert，不能绕行执行 paste、place、make mask 或其它未公开动作。
- `exportFolderConfigured=false` 只表示面板未指定导出文件夹；它不影响已认证导出，也不会补出蒙版内容能力。
- layer.translate、layer.scale、layer.rotate 均为 supported。
- generative.fill unavailable；generative.upscale experimental，不进入常规正式链路。

### 2.1 已安装且与图像处理相关的动作

当前已确认：

- 动作集：主体和背景
  - 选择主体
  - 移除背景
  - 模糊背景
  - 生成自定义背景
  - 协调当前图层

正式抠图只优先考虑“选择主体”和“移除背景”。其它动作是否适合当前任务，必须另行检查其实际像素结果。

### 2.2 一次性性能设置

Adobe Photoshop 可在“首选项 → 图像处理”中选择 Select Subject 和 Remove Background 的处理方式。

- Device：优先用于速度，通常也是默认设置；
- Cloud：只在设备处理的边缘结果明显失败、且用户愿意等待时试用。

该设置属于可选的用户辅助操作，仅在用户对当前任务主动明确同意时进行；未授权时保持现有设置并继续其它合规路线，不得要求用户为生产切换。一个任务只检查一次，不在每张图前反复切换。

## 3. 标准运行卡

### 3.1 任务级预检：每个任务或运行时变化后执行一次

1. 读取本手册当前版本，并记录文件修改时间或 SHA-256。
2. 明确输入绝对路径、输入 SHA-256、目标输出、允许改变内容、保护区域和是否允许人工辅助。没有当前资产的明确授权时，人工辅助默认为否；一般任务授权、历史协作、Photoshop 已打开或命令标记 `requires_user` 均不能推定为允许。
3. 调用 photoshop_host_describe：
   - paired 必须为 true；
   - connected 必须为 true；
   - queuedCommands 必须为 0；
   - Photoshop 和插件版本必须与预期一致。
4. 调用 photoshop_state_get 并按第 3.1.1 节检查是否存在陈旧的自动任务文档；人工或来源不明文档不得关闭。
5. 调用 photoshop_capability_list，保存当前命令统计。
6. 调用 action.list，记录本任务拟用动作的动作集名和动作名。
7. 对本任务第一次使用的命令执行 command_search 和 command_describe，保存：
   - command_id；
   - status；
   - input schema；
   - risk；
   - prerequisites；
   - verification；
   - rollback。
8. 检查允许打开根目录和导出目录。exportFolderConfigured 为 false 时，先解决导出位置，不开始正式生产。

当 host、pluginInstanceId、Photoshop 版本、MCP 版本和命令目录没有变化时，可在同一任务内复用已保存的命令说明，不必对每张图重新读取完整目录。

### 3.1.1 陈旧自动文档的安全保存与释放

本节中的“窗口”指 Photoshop 中已打开的文档，不包含应用主窗口、面板或原生对话框。每个准备修改 Photoshop 的新任务只检查一次；host、插件实例、任务占用者或文档列表变化后重新检查。

#### A. 先建立文档所有权，来源不明即保护

对 `photoshop_state_get` 返回的每个已打开文档，尝试与当前任务及历史自动操作记录中的 `task_id`、`document_id`、源路径、打开时间、最后一次自动命令和输出目录匹配：

- `AUTOMATION_OWNED`：有 MCP 的 `document.open_allowed`、`document.create`、`document.duplicate` 或其它受支持命令回执，且文档 ID／路径与任务记录一致；
- `HUMAN_OR_UNKNOWN_PROTECTED`：没有完整自动来源链、由用户明确标记为人工窗口，或所有权存在冲突；
- `ACTIVE_TASK_PROTECTED`：虽由自动任务打开，但所属任务仍为 active／inProgress，或仍有在途、排队、超时未知及未核实命令。

只有 `AUTOMATION_OWNED` 可以进入后续陈旧判定。无法证明“是自动任务打开”时，不得通过标题、文件名、打开时长、是否未保存或当前是否位于前台进行猜测；一律按人工或来源不明窗口保护。人工窗口即使打开很久、未保存或占用文档数量，也不得自动保存、关闭或切换其活动图层。

#### B. 陈旧异常的判定

自动文档必须同时满足以下条件，才标记为 `STALE_AUTOMATION_DOCUMENT`：

1. 所属自动任务已经 completed、failed、interrupted，或已有明确交棒记录证明不再使用该文档；
2. host 显示 `queuedCommands=0`，且没有 in-flight、unknown、timeout-unverified 或等待人工步骤的命令；
3. 距该文档最后一次已确认的自动命令至少 30 分钟；具体 Skill 可以要求更长，不得擅自缩短；
4. 当前没有人工正在使用 Photoshop，也没有其它任务声明占用；
5. 文档不属于当前准备执行的任务。

仅“打开超过 30 分钟”不构成异常。任务仍活跃、所有权未知或命令结果未知时，无论时长都不得释放。

#### C. 安全保存与关闭顺序

对每个 `STALE_AUTOMATION_DOCUMENT` 一次只处理一份，并执行：

1. 保存释放前快照：`task_id`、原所属任务、文档 ID、标题、源路径、尺寸、活动图层、dirty/unsaved 状态、最后自动命令时间、host 状态及判定证据。
2. 若文档有未保存改动，先用实时目录中 `supported` 的 PSD 导出能力写入唯一、不可覆盖的恢复副本：
   `D:\Codex\NDC\工作过程文件\PS_MCP\orphan-recovery\<yyyy-MM-dd_HHmmss>\<document-id>_<safe-title>.psd`。
   `document.save` 仍为 requires_user，不得借关闭流程覆盖原文件。
3. 对恢复 PSD 做文件层验证：文件存在、非零字节、可读，记录绝对路径和 SHA-256；重要构图文档同时导出或保留审阅 PNG。验证失败则保持文档打开并登记 `STALE_RELEASE_SAVE_FAILED`。
4. 文档无未保存改动也要确认其原文件或最近恢复副本仍存在；证据不足则不关闭。
5. 在调用 `document.close` 前读取实时 command describe，按其当前 schema 选择不会再次覆盖原文件的关闭方式；使用唯一 idempotency_key。
6. 关闭后重新调用 state，确认目标文档 ID 已消失、活动文档符合预期、文档数量准确减少且 `queuedCommands=0`，登记 `STALE_RELEASE_PASS`。
7. 若关闭超时、断线或结果为 unknown，不得重发。先读 host、state、history 和恢复文件判断文档是否已关闭；仍无法确定则登记 `STALE_RELEASE_UNKNOWN` 并停止自动清理。

清理多份陈旧文档时必须逐份完成“保存—文件验证—关闭—状态验证”，不能批量关闭后再补回执。任何一步发现人工活动、其它任务占用或来源链不完整，立即停止清理并保留剩余窗口。

#### D. 明确不允许

- 不关闭人工打开、用户明确保留或来源不明的文档；
- 不以文档标题相似、文件位于过程目录或窗口长期未置顶作为自动所有权证据；
- 不关闭仍由 active／inProgress 任务使用的文档；
- 不在保存失败、文件未校验或命令状态未知时强制关闭；
- 不用鼠标、键盘、Computer Use 或系统进程结束操作绕过原生 MCP；
- 不把关闭 Photoshop 应用进程当作文档释放；
- 不为释放窗口覆盖唯一原文件、正式资产或人工工作文件。

### 3.2 资产级预检：每张图执行

1. 确认 Photoshop 未被人工或其它任务使用。
2. 调用 photoshop_state_get，核对：
   - 活动文档 ID 和标题；
   - 宽、高、色彩模式；
   - 活动图层 ID、名称、类型和锁定状态；
   - 当前选区、路径和通道；
   - 是否存在未保存改动。
3. 检查源图是否已有 Alpha；先看原图 Alpha、黑底、白底和棋盘格，不得先转 RGB。
4. 创建工作副本。动作、滤镜、删除、路径替换和其它破坏性操作不得直接作用于唯一源图。
5. 对照任务 Skill 决定当前图是否真的应该进入 Photoshop。

### 3.3 执行与验证

- 每次修改使用唯一 idempotency_key。
- 只执行解决当前缺陷所需的最少命令。
- 对 `主体和背景 / 选择主体` 与 `主体和背景 / 移除背景`，`action.play` 必须返回动作前后文档、活动图层与选区快照；动作返回本身不构成选区、蒙版或 Alpha 通过结论。
- 读操作和未改变像素的元数据操作不需要生成全图预览。
- 修改像素、选区、路径、变换、滤镜或 Alpha 后必须做相应 state 或 preview 验证。
- 不连续盲调多个参数；如果需要移动，就不要顺便缩放和旋转。
- 操作不合格时优先撤销到已知状态，而不是叠加反向修补。

### 3.4 三检查点策略

默认只在三个节点取主要视觉证据：

1. 输入或选定候选；
2. Photoshop 修改后候选；
3. 最终 RGBA、运行尺寸或合成结果。

局部预览只覆盖高风险位置：发丝、细绳、针尖、透明玻璃、手指、鞋、纸张边缘、孔洞、阴影末端、接触点和高对比边。

## 4. 先分流，再操作

这是效率提升最大的步骤。

| 缺陷类别 | 处理路线 | Photoshop 是否应介入 |
|---|---|---|
| 身份、结构、状态、材质或时代错误 | 返回生成或美术源 | 否 |
| 必要文字错误、缺失或乱码 | 返回完整生成或美术源 | 否 |
| 原生 Alpha 已正确 | 保留 Alpha，直接整备和验收 | 通常否 |
| 人手、背景、承托物、场景残片等外部缺陷 | 对选定版做一次隔离 | 是 |
| 位置、统一缩放、旋转、透明边距、轻微裁切 | 最小变换后交确定性最终器 | 是 |
| 发丝、毛绒、玻璃、烟雾、半透明薄纱 | 灰度 Alpha 或人工 Select and Mask | 仅适合蒙版链 |
| 硬质外轮廓的少量局部错误 | 局部贝塞尔路径 | 是 |
| Type 6、Map、热区 | 定稿父图上的语义路径 | 后续阶段 |
| 大范围新场景状态或缺失像素 | 返回对应生成或场景状态流程 | 不用 PS 假修 |

### 4.1 候选进入 PS 的门槛

- 同批两张候选先在 Photoshop 外完成选优。
- 只有选定版进入透明整备。
- 不同时对两张候选做完整抠图。
- 已证明语义失败的图不进入 Photoshop。
- 一次隔离输出实际视觉失败后，不在同一源上继续做第二、第三套阈值或描边实验；按第 4.2 节保留并交付待审核版本，同时可在剩余额度内另行生成空背景或原生透明源。

### 4.2 不完整或低置信度提取的持续推进

当 Photoshop MCP 已实际执行合规非生成提取并产出可打开的 RGBA，但视觉检查发现边缘不完整、残留、误删、软边不确定，或操作者对结果把握不足时，不得把该资产留空或停在没有可审核文件的状态：

1. 保留提取前原图的精确字节、绝对路径、尺寸和 SHA-256；原图只读，不被尝试结果覆盖。
2. 保存本次实际尝试的 RGBA、可恢复 PSD，以及存在时的蒙版、路径、选区／动作回执、Alpha 四底预览和真实缺陷说明；不得用空白占位、假 Alpha 或只有报告没有图片来代替。
3. 将结果标记为 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW`，记录置信度、已知缺陷、未核实区域、实际方法和当前手册／能力快照。旧 provisional 版本不覆盖，后续尝试建立新版本。
4. 允许该结果进入**明确标记的 provisional 下游链**，继续完成可执行的合成、框幅、状态预览、Map／XY、双 Profile、重建和整包检查；所有派生件继承同一 provisional 状态及源哈希，不能把技术成功写成视觉 PASS。
5. 将原图、尝试结果、恢复件、预览、缺陷记录和派生件放入 `工作过程文件` 下独立的“待用户审核交付包”。这属于可交付审核材料，不进入 `最终交付`，不覆盖已批准资产，也不满足正式发布验证器的 PASS 条件。
6. 用户审核、人工修正或后续自动提取真正通过后，从保留原图或明确选定版本建立新修订，重新执行受影响的 Alpha、边缘、XY、重建、合成和正式发布门禁；不得把旧 provisional 记录回写成历史上已经通过。

只有完全没有合规提取输出（例如 Bridge 断开、源图无法受控进入 Photoshop、导出不可用或命令结果未知）时，才按能力阻断处理；此时仍保留原图和检查点并继续其它独立工作，但不得伪造 provisional RGBA。语义、身份、结构或必需文字错误也不因本节获得放行；本节只处理提取完整度和置信度。

## 5. 高效高质量抠图总流程

### 5.1 第一步：原生 Alpha 优先

打开源图后先记录：

- Alpha absent：没有 Alpha；
- Alpha opaque：全不透明；
- Alpha binary：只有 0 和 255；
- Alpha partial：包含半透明覆盖。

如果原生 Alpha 可用：

- 保留它作为起点；
- 不进行 RGB 扁平化；
- 不从白底或黑底重新色键抠图；
- Alpha 0 下的隐藏 RGB 可在最终清理时归零，但不能借此改变可见像素；
- 局部缺陷只修对应区域，不重建整张 Alpha。

### 5.2 第二步：定义像素所有权

抠图前写清以下区域：

- BODY_MUST_KEEP：本体材料、可见厚度、细线、针、反光、标记和小零件；
- OWN_SHADOW_KEEP：当前资产角色需要保留的归属阴影；
- REAL_GAPS_REMOVE：真实孔洞和组件间空隙；
- BACKGROUND_REMOVE：外部背景、承托物和无关残片；
- FOREGROUND_EXCLUDE：确实遮挡在主体前方的像素。

颜色浅、亮度高或接近背景，不等于背景。连续玻璃中的透射颜色也不等于孔洞。

### 5.3 路线 A：不透明、边界清晰的主体

适用于：

- 木、金属、石、厚纸板等不透明道具；
- 人物服装和皮肤的大部分硬轮廓；
- 背景与主体对比明确；
- 软毛、透明材质和复杂阴影不是主要边缘。

推荐命令链：

1. document.open_allowed；
2. document.duplicate；
3. 按材质选择一条动作链，且只在工作副本上执行：
   - 先看主体范围：`action.play`，set_name：主体和背景，action_name：选择主体；
   - 直接隔离清晰硬边主体：`action.play`，set_name：主体和背景，action_name：移除背景。
4. 读取动作回执的 before/after 文档、活动图层与选区快照；“选择主体”必须看到实际选区，不能只相信动作成功。
5. state 验证；
6. preview 检查全图和高风险局部；
7. 通过后 document.export 输出 PSD 与 PNG。

动作返回成功只说明动作执行完成。以下任一项仍为失败：

- 残留背景、桌面、椅背、手或场景像素；
- 切掉组件、细线、边缘厚度或阴影；
- 产生错误透明孔洞；
- 改变主体内部 RGB；
- 没有真实 Alpha；
- 未检查实际输出。

### 5.4 路线 B：自动主体初选加已授权人工精修

适用于：

- 人物头发、眼镜、手指和鞋；
- 毛绒、流苏、细绳；
- 主体和背景对比不足；
- 自动移除背景已经接近成功但软边不可靠。

推荐：

1. 在未保存副本上 action.play“主体和背景 → 选择主体”；
2. 查看完整选区，不只看 bounds；
3. 由用户为当前资产明确指定的人工制作人员在原生 Select and Mask 中精修；只有用户主动明确选择亲自操作时，操作者才可以是用户本人；
4. 输出到图层蒙版或带 Alpha 的新层；
5. MCP 恢复后重新读取 state、preview，并导出 PSD/PNG；
6. 登记人工交接、实际保存文件和视觉证据。

当前 selection.select_and_mask_dialog 为 requires_user。MCP 只能记录和衔接，不能自动完成原生工作区；这不构成要求用户操作的授权。当前资产没有已授权人工制作人员时，不建立路线 B，继续路线 C、其它实时 supported 路线，或按第 16 节登记能力缺失。

### 5.5 路线 C：通道或计算派生 Alpha

适用于：

- 背景与主体在某一亮度或色彩通道上明显分离；
- 烟雾、玻璃、薄纱、反射或软阴影需要灰度 Alpha；
- 自动主体不能保持部分透明。

当前可用：

- channel.list；
- channel.create；
- channel.duplicate；
- channel.calculations_new；
- layer.apply_image。

限制：

- 当前 Calculations 命令能力有限，不等同完整 Photoshop 通道工作流；
- Color Range 是 requires_user；
- 当前不能自动绘制或直接写图层蒙版像素；
- 通道统计不能替代黑、白、对比底上的实际视觉检查。

### 5.6 路线 D：局部硬边贝塞尔路径

路径只适合：

- 金属、木器、纸板、鞋底、衣服硬边；
- 少量自动选区明显偏移的局部；
- 用户或美术已经绘制的权威钢笔路径；
- Type 6、Map 和热区轮廓。

路径不适合：

- 发丝、毛发、烟雾、玻璃、薄纱和软阴影；
- 整个人物或复杂道具的自动坐标猜测；
- 从缩略图生成数百个折线点。

## 6. 钢笔和路径的优化规范

### 6.1 核心原则

- 先获得可靠选区或 Alpha，再决定是否需要路径。
- 能用蒙版解决的软边不转路径。
- 用尽量少的锚点表达曲线；锚点多不等于准确。
- 曲线使用 smoothPoint 和真实左右控制柄。
- 只在轮廓拐角、曲率极值、切线变化或拓扑变化处放点。
- 直线段使用 cornerPoint；圆弧、肩线、鞋面和器物曲面使用 smoothPoint。
- 外轮廓、真实孔洞和多个独立岛分别建 subpath。

Adobe 的官方建议同样是避免不必要的锚点；点越少越容易编辑、显示和维护。

### 6.2 禁止的路径形态

- 整圈全部是 cornerPoint；
- leftDirection 和 rightDirection 全部等于 anchor；
- 每隔固定像素机械放一个点；
- 用选择区包围框代替轮廓；
- 把纹理、明暗、印刷内容或照片中的人物脸当成物理边界；
- 用凸包填掉真实凹槽或组件间空隙；
- 把主体阴影、承载体阴影和背景混成一个路径。

### 6.3 路径生成方式

优先级：

1. 用户或美术在同尺寸文档中绘制的权威钢笔路径；
2. 从已经通过的二值硬边选区创建路径；
3. 从真实像素轮廓自动拟合三次贝塞尔曲线；
4. 仅对少量局部手工建立新路径。

不允许模型仅凭视觉缩略图直接猜完整路径坐标。

### 6.4 create_from_selection 的容差

path.create_from_selection 的 tolerance 范围为 0.5 至 10，默认 2。

使用建议：

- 1K 至 2K 硬边资产可先从 2 至 4 试起；
- 细针、尖角、小孔等细节可降低容差；
- 热区或不要求贴像素的交互轮廓可适当提高容差；
- 容差不是质量结论，必须在原像素或最近邻 200% 检查。

如果生成了大量角点、锯齿或拓扑错误，不继续降低容差堆点；返回选区或 Alpha 修正。

### 6.5 自动曲线拟合建议

如果未来用代码从硬边 Mask 构造 path.create 输入，应执行：

1. 从原始尺寸 Alpha 提取轮廓，不使用截图；
2. 保留外轮廓、孔洞和多个岛的拓扑；
3. 对轮廓做误差受控的简化；
4. 在角点保留 cornerPoint；
5. 对连续曲线拟合三次贝塞尔；
6. 控制柄沿局部切线设置，长度仅作初始估计；
7. 对尖角、细小零件和凹槽单独降低拟合误差；
8. path.create 后回转选区并在 200% 检查。

不能把 Ramer-Douglas-Peucker 简化后的折线直接当成最终平滑路径；折线简化之后还需要曲线拟合。

### 6.6 当前 MCP 的路径限制

- 可创建、读取、复制、选择、删除路径；
- 可在选区与路径之间转换；
- 已有 PathPoint 几何为只读，不能逐点修改；
- 需要修正时创建带版本名的新路径，保留旧路径；
- 不为普通母版抠图读取完整路径几何，除非确实要复核权威路径或热区。

## 7. 不同材质的抠图策略

| 材质或边缘 | 优先方法 | 重点检查 |
|---|---|---|
| 金属、木、石、厚纸 | Remove Background 初选，局部贝塞尔硬边 | 边缘厚度、缺口、投影 |
| 普通服装和皮肤 | Select Subject，局部硬边修正 | 手指、袖口、鞋 |
| 发丝、毛绒、流苏 | Select Subject + Select and Mask | 断丝、背景色边、半透明 |
| 玻璃、液体、薄纱 | 原生 Alpha 或灰度通道 | 材料连续性、反光、部分透明 |
| 针、细线、链条 | 高分辨率初选加局部精修 | 断裂、消失、错误增粗 |
| 纸张、照片 | 保留完整纸面、厚度和全部可见角 | 不把图内内容当边界 |
| 软接触阴影 | 灰度 Alpha | 方向、范围、归属、渐变 |
| 硬轮廓热区 | 权威钢笔路径 | 凹槽、孔洞、多岛、相邻物排除 |

## 8. 道具母版生产专用路线

适用 ndc-prop-master-production。

### 8.1 进入 Photoshop 前

1. 两图先选优；
2. 检查道具身份、结构、组件、指定状态、材质和必要文字；
3. 语义错误直接回生成；
4. 只有外部背景、手、承托物、构图和 Alpha 问题才进入 PS。

### 8.2 原生 Alpha 可用

- 保留；
- 使用现有确定性工具完成允许的透明安全缩放和最终框幅；
- 不重新抠图。

### 8.3 简单不透明道具

- 副本上执行“移除背景”动作；
- 只做一次实际隔离；
- 检查所有组件、细线、孔洞和当前角色所需阴影；
- 通过后再进入最终尺寸整理；
- 失败后不继续阈值或描整圈；先按第 4.2 节保存并交付 provisional 提取包，再按剩余额度决定是否重生空背景或原生透明版本。

### 8.4 框幅和普通 Big

- 语义完整但位置、占比、旋转或透明边距错误时，只做最小一次 Photoshop 修正；
- 最终标准化框幅、透明安全重采样、模板和报告交给 evidence_art.py finalize-big；
- 不为尺寸问题重新生图；
- 不用 Photoshop 或代码补写文字。

### 8.5 多部件 Big

- 只有当前目录暴露 selection-to-new-layer 或 layer-via-cut 时，才在单文档中逐部件拆层；
- 当前本机尚无该命令，应记录 PS_MCP_SELECTION_TO_LAYER_UNAVAILABLE；
- 使用已授权的 Alpha 安全确定性变换；
- 不拆多个文档反复导入；
- 保留每个组件原有阴影，不强制添加统一图层样式阴影。

### 8.6 跨文档合成边界

- `layer.place_file` 是当前唯一已实机验证的受控跨文件置入入口：输入允许根内的绝对路径，在活动文档中新建嵌入式智能对象层。2026-09-10 的 Photoshop 27.11.0 隔离测试证明 RGBA 逐像素一致、Alpha 一致、历史回滚和临时导入清理可用。
- 置入前先打开目标场景，再逐个置入已选定的角色、道具或阴影文件；同场景保持一个文档连续完成，置入时直接命名图层。每次置入核对图层数、名称、`kind=smartObject`、`embedded=true`，整批置入和变换后再取一次全场预览，避免每层重复导出。
- 有原生 Alpha 的源图直接置入，不先转 RGB、不重新抠图。没有 Alpha 的源图仍须先按语义选择路线完成隔离；`layer.place_file` 只负责传入与合成，不会自动生成精确边界。
- 智能对象置入后优先用 supported 的 translate、scale、rotate 做最小变换；不要通过反复打开独立文档、复制粘贴或鼠标拖放绕行。需要像素级改边时，在可恢复副本上处理并重新置入通过审核的结果。
- 不得把 `document.open_allowed`、`exportFolderConfigured`、Smart Object 识别或 `photoshop_advanced_execute` 误当成蒙版创建、智能对象内容编辑、重链接或替换能力。当前仍不能自动创建/绘制蒙版，也没有 selection-to-new-layer。
- 命令状态以实时 search/describe 为准；若 `layer.place_file` 不再是 supported，保存检查点并按任务 Skill 的确定性回退或人工分支处理，不恢复旧 queue，也不伪造合成。

## 9. 人物透明提取路线

1. 候选先通过身份、姿势、服装、完整性和风格检查；
2. 在副本上执行“选择主体”或“移除背景”动作；
3. 自动结果只作为起点；
4. 必查发丝、眼镜、耳朵、手指、鞋、半透明衣料和高对比边；
5. 发丝和软边使用 Select and Mask 或灰度 Alpha；
6. 服装、皮肤和鞋的少量硬边可用贝塞尔修正；
7. 不用整圈全角点路径；
8. 导出 PSD 与 PNG RGBA，实测 Alpha；
9. 在黑、白、饱和红和棋盘格上检查。
10. 若不完整或低置信度，仍按第 4.2 节保存原图和尝试件并继续 provisional 下游，不将其称为正式人物层。

## 10. 场景局部修图和证物入景

### 10.1 坐标锁定局部修复

- 明确允许修改 Mask；
- Mask 外像素必须保持；
- 先在副本和独立层工作；
- 只执行当前目录 supported 的修复；
- 当前没有修复画笔、仿制图章、内容识别填充或生成式填充的可靠自动命令；
- 不得用选择后删除冒充背景修复；
- 完成后对最初源图做授权 Mask 外零漂移检查。

### 10.2 近成功入景修正

仅在身份、内容、材质、光照、透视和承托已经正确时：

1. 保留冻结场景和候选；
2. 只执行必要的 translate、scale 或 rotate；
3. 道具与其归属接触／投影一起变换；
4. 检查比例、透视、接触、遮挡、光向、阴影和全场协调；
5. 不能解决时回对应生成任务，不连续盲调。

### 10.3 Type 7 内景重框

- 只处理已批准的无边框内部；
- 均匀放大和移动完整内景；
- 不包含 12px 白框参与变换；
- 不扭曲容器、不改变机位、不裁掉必要部件和阴影；
- 通过后再添加精确白框。

## 11. Type 6、Map 与热区路径

路径必须表达语义所有权，而不是颜色或对比。

### 11.1 描边前清单

- 目标身份；
- 全部物理组件；
- 可见平面和厚度；
- 目标归属阴影；
- 真实负空间；
- 前景遮挡；
- 相邻可交互物。

### 11.2 路径要求

- 外轮廓完整；
- 孔洞用 subtract；
- 多个独立组件可用多个 add subpath；
- 不用外接矩形或凸包；
- 不把相邻柜门、把手、纸张或容器面并入；
- 照片 Map 包含完整物理相纸，不把照片内容当边缘；
- 用户或美术明确认定的最终钢笔路径是权威路径，不再简化或重描。

### 11.3 直接拾取与阴影

直接地图拾取需要分别管理：

- original_scene；
- carrier_without_prop；
- pickup_layer；
- scene_before_pickup。

pickup_layer 的 Alpha 必须覆盖道具及其归属阴影，排除承载体和承载体自身阴影。组合必须重建拾取前场景；拾取后不得留下道具、道具阴影、残片或修补缝。

## 12. 变换、尺寸和导出

### 12.1 选择正确命令

- image.resize：重采样整张图；
- document.resize_canvas：改变画布边界；
- document.rotate：旋转整张画布；
- layer.translate：移动活动层；
- layer.scale：缩放活动层；
- layer.rotate：旋转活动层。

不要把画布裁切、图像缩放和图层缩放混称为同一操作。

### 12.2 变换效率

- 只调用解决问题所需的命令；
- 参数在执行前计算并记录；
- 能用一次 scale 解决时不先 translate 再 scale 再 translate；
- 固定运行时框幅交确定性最终器；
- 视觉构图判断留在 Photoshop；
- 每个变换结果都检查透明边、接触和重采样软化。

### 12.3 导出

- document.export 支持 PNG、JPEG、PSD；
- 导出副本不等于保存当前工作文档；
- PSD 用于可恢复图层、蒙版和路径；
- PNG 用于真实 RGBA 交付；
- 导出后必须在文件层检查存在性、宽高、模式、Alpha 和 SHA-256；
- 需要原生 Save 时按 requires_user 流程处理。

## 13. 滤镜、颜色与文本

### 13.1 滤镜

当前 supported 的滤镜包括模糊、锐化、噪点和多种形态滤镜。正式 NDC 资产只在明确任务需要时使用。

- 先复制；
- 只作用于正确图层或选区；
- 记录参数；
- 视觉检查是否改变风格、材质、文字或身份；
- 不用滤镜替代重绘或语义修复。

### 13.2 颜色、模式与配置文件

document.color_mode_set、document.bits_per_channel_set 和 document.profile_convert 为 supported，但属于高风险转换。

- 转换前复制；
- 记录源和目标模式、位深、ICC；
- 检查透明、图层兼容和颜色漂移；
- 不在没有交付要求时主动转换。

### 13.3 文本

Photoshop MCP 通用目录支持创建和编辑文本层，但 NDC 道具规则优先：

- 正式道具文字必须来自已接受的完整生成或美术母版；
- Photoshop、代码和 OCR 不得补写、替换或校正文案；
- 文字错误是语义失败，不是技术修图问题。

## 14. 视觉与技术验收

### 14.1 通用技术检查

- 文件存在；
- 路径正确；
- 宽、高和比例正确；
- 色彩模式和位深正确；
- Alpha 实际存在且与角色相符；
- 输出 SHA-256 已记录；
- 输入、输出和当前文档版本可追溯；
- PSD 可恢复；
- 没有未知命令或未完成保存。

### 14.2 通用视觉检查

- 100% 整图：内容、构图、整体轮廓和风格；
- 原像素或最近邻 200%：边缘、孔洞、细部、残片和锯齿；
- 400% 仅用于发丝、细线、针尖、局部 Alpha 或像素级接缝；
- 最终运行尺寸：缩小后是否丢失细节或产生脏边。

### 14.3 Alpha 四底检查

至少使用：

- 黑底：发现白色 matte、浅色残留和半透明断层；
- 白底：发现黑边、脏边和暗色背景残留；
- 饱和红底：发现轮廓孔洞和综合色边；
- 棋盘格：检查透明范围和错误岛。

同时查看 Alpha-only 灰度图。

### 14.4 正式抠图 PASS 的失败条件

任一项失败即不能进入正式交付或标记 PASS；仍应按第 4.2 节形成可审核的 provisional 交付包：

- 主体材料缺失；
- 背景残留；
- 错误透明孔洞；
- 真实孔洞被填死；
- 半透明材料变成全透明或全不透明；
- 归属阴影丢失或带入错误阴影；
- RGB 身份被改写；
- 细线、发丝、针、链条或纸张厚度断裂；
- 运行尺寸出现明显白边、黑边或锯齿；
- 只存在技术报告，没有真实视觉审查。

## 15. 速度优化清单

### 15.1 应当缓存

- 同一任务内未变化的 host 和命令目录；
- 已 describe 的命令 schema；
- 已确认的动作集和动作名；
- 允许根目录和导出规则；
- 固定的输出模板和验收表。

### 15.2 不应重复

- 每张图重新读取完整命令目录；
- 两张候选都完整抠图；
- 每个读操作都导出预览；
- 为普通母版读取完整路径几何；
- 在同一失败源上反复阈值、收缩、扩张和描边；
- 用多个反向变换抵消错误参数；
- 为纯尺寸问题重新生成图片；
- 为软边建立大量硬路径点。

### 15.3 应当合并

- 使用安装动作把 Photoshop 内部多步骤放进一个受控历史范围；
- 选定候选后一次完成隔离；
- 最终机械框幅和尺寸交确定性工具一次完成；
- 同一次审阅同时覆盖整图、关键局部和运行尺寸，但每个产物仍保留自己的结论。

## 16. 失败、超时与回退

### 16.1 NATIVE_COMMAND_BUSY

- 不重试风暴；
- 检查是否有人或其它任务正在使用 Photoshop；
- 等待引擎空闲；
- 重新读取 state 后继续。

### 16.2 修改命令超时或连接中断

- 不自动重发；
- 调用 host_describe；
- 调用 state_get；
- 查看 history 状态；
- 检查输出文件和哈希；
- 明确命令未执行后，才能以新的 idempotency_key 重新提交。

### 16.3 动作执行失败

- 保留动作名、文档 ID、活动图层和原始返回；
- 检查是否作用于错误层、锁定层或不支持文档；
- 回到副本初始状态；
- 同一原样命令最多重试一次；
- 再失败则换路线或记录能力缺失。

### 16.4 requires_user

- `requires_user` 表示当前命令不能由 MCP 自动完成，不是把生产步骤分配给用户的授权；
- 先保存当前状态，并核验其它实时 `supported` 的非生成路线和已授权确定性处理；一次失败不得直接升级为人工交接；
- 默认不要求用户执行 Select and Mask、色彩范围、通道、蒙版、笔刷修边、保存导出或其它图片生产劳动，也不得以“完成后回复已完成”作为继续条件；
- 只有用户对当前资产主动明确选择亲自操作，或明确指定人工制作人员时，才说明准确原生步骤并建立 `manual_handoff`；不得从一般性继续指令或历史人工协作推定授权；
- 未获当前资产人工授权且不存在合规自动路线时，记录准确能力缺项和可恢复检查点，继续不依赖该步骤的独立工作；不得用界面自动化越权补位，也不得把未完成资产登记为通过；
- 已实际得到不完整或低置信度 RGBA 时，不把它丢弃或留空；按第 4.2 节保存原图、尝试件与证据，继续明确标记的 provisional 下游和待用户审核交付；
- 经明确授权的人工结果回收后重新读取 state 和 preview，验证实际文件、Alpha 和边缘，不把用户或人工制作人员的完成声明本身当作结果证据。

### 16.5 unsupported

- 记录准确 command_id、status 和缺项；
- 不声称执行；
- 按当前 Skill 使用确定性回退、返回生成或登记人工处理；
- 继续不依赖该能力的独立工作。

## 17. 当前命令速查

### 文档

- supported：document.create、close、export、open_default、open_allowed、duplicate、resize_canvas、rotate、artboard_list
- requires_user：document.save

### 图像与变换

- supported：image.resize、layer.translate、layer.scale、layer.rotate
- unavailable：自由变换网格、透视、斜切、扭曲、操控变形的自动正式路线

### 图层

- supported：layer.create、rename、delete、group_create、visibility_set、opacity_set、clipping_set、blend_mode_set、fill_opacity_set、locked_set、kind_inspect、place_file（嵌入式智能对象，保留源 RGBA）
- 当前无 selection-to-new-layer 或 layer-via-cut

### 选择

- supported：select_all、deselect、invert、rectangle、ellipse、expand、contract、feather、border、polygon、grow、smooth
- requires_user：color_range_dialog、select_and_mask_dialog
- 直接 selection.select_subject 当前无目录命令，但可通过安装动作执行

### 路径

- supported：path.list、create、geometry_get、select、duplicate、delete、create_from_selection、make_selection

### 蒙版

- supported：mask.properties_get、mask.properties_set
- 当前不能通过正式目录命令创建、删除或绘制图层蒙版内容

### 通道

- supported：channel.list、create、duplicate、delete、calculations_new、layer.apply_image

### 动作

- supported：action.list、action.play
- requires_user：action.record_dialog、automation.batch_dialog

### 历史

- supported：history.undo、redo、state_list、state_activate

### 颜色

- supported：document.color_mode_set、bits_per_channel_set、profile_convert

### 生成与神经能力

- unavailable：generative.fill、neural.skin_smoothing
- experimental：generative.upscale

## 18. 最小操作记录模板

每个 Photoshop 连续段至少记录：

    task_id:
    asset_id:
    input_path:
    input_sha256:
    manual_version:
    host_version:
    mcp_version:
    plugin_instance_id:
    preflight_documents:
      - document_id:
        ownership: AUTOMATION_OWNED | HUMAN_OR_UNKNOWN_PROTECTED | ACTIVE_TASK_PROTECTED
        owner_task_id:
        last_automated_activity_at:
        stale_result:
    stale_release:
      document_id:
      recovery_psd:
      recovery_sha256:
      close_idempotency_key:
      final_status: NOT_NEEDED | STALE_RELEASE_PASS | STALE_RELEASE_SAVE_FAILED | STALE_RELEASE_UNKNOWN
    document_id:
    active_layer_id:
    capability_snapshot:
    commands:
      - command_id:
        idempotency_key:
        arguments:
        result_status:
        verification:
    output_psd:
    output_png:
    output_sha256:
    visual_review:
      whole_100:
      local_200:
      risk_local_400:
      runtime_size:
      black_white_red_checker:
      alpha_only:
    final_status: PASS | FAIL | WAITING_REVIEW | PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW

## 19. 必须关联本手册的美术生产 Skill

以下 Skill 只要实际进入 Photoshop MCP，就必须执行第 3 节前置并记录手册路径、版本与 SHA-256：

- ndc-art-stage-pipeline
- ndc-character-asset-derivation
- ndc-character-identity-production
- ndc-character-scene-integration
- ndc-character-scene-production
- ndc-coordinate-image-edit
- ndc-generate-characters
- ndc-generate-expressions（仅用户明确授权的 Photoshop MCP 模式）
- ndc-generate-ui-portraits
- ndc-prop-delivery-review（仅有限返修分支）
- ndc-prop-hotspot-export
- ndc-prop-master-production
- ndc-scene-evidence-placement
- ndc-scene-state-variation

仅做文字审查、提示词准备或明确禁止 Photoshop 的 Skill 不因为出现“Photoshop”字样而加载本手册。

维护工作区手册位于项目根；工程镜像位于 `production/art_pipeline/PS_MCP_操作参考手册.md`。同步后必须逐字节校验 SHA-256 一致。

## 20. 正式资料入口

- Adobe Photoshop Desktop Help：
  https://helpx.adobe.com/photoshop/desktop.html
- Detect subject using Select Subject：
  https://helpx.adobe.com/photoshop/desktop/make-selections/automatic-color-based-selections/detect-subject-using-select-subject.html
- Improve Select Subject and Remove Background：
  https://helpx.adobe.com/photoshop/desktop/make-selections/automatic-color-based-selections/improved-select-subject-and-remove-background-results.html
- Remove background：
  https://helpx.adobe.com/photoshop/desktop/repair-retouch/remove-objects-fill-space/remove-background-in-your-images.html
- Draw paths with the Pen tool：
  https://helpx.adobe.com/photoshop/desktop/draw-shapes-paths/draw-lines-curves/draw-paths-with-the-pen-tool.html
- Edit paths：
  https://helpx.adobe.com/photoshop/using/editing-paths.html
- Save selections and Alpha channel masks：
  https://helpx.adobe.com/photoshop/using/saving-selections-alpha-channel-masks.html
- Channel calculations：
  https://helpx.adobe.com/photoshop/using/channel-calculations.html

## 21. 维护规则

- Photoshop、MCP、UXP、插件或命令目录变化后，刷新第 2 节。
- 更新维护工作区手册后，同步工程镜像并验证 SHA-256 一致。
- 新增会实际操作 Photoshop MCP 的美术生产 Skill 时，必须把它加入第 19 节并在该 Skill 入口加入“Photoshop MCP 强制前置”。
- 每次新增正式可用动作，记录动作集名、动作名、适用输入、输出形态、失败案例和真实审核结论。
- 新增命令必须先通过实时 search、describe 和测试副本验证，再写入 supported。
- 手册中的通用能力不覆盖 NDC Skill 的更严格限制。
- 任何抠图路线都要保留一次失败回退，不允许无限微调同一源。
- 路径规范发生变化时，用测试资产验证：平滑点、控制柄、孔洞、多岛、回转选区和 200% 边缘。
- 更新本手册后运行内容一致性检查，至少核对：
  - 命令状态与实时目录；
  - 自动主体动作；
  - 原生 Alpha 优先；
  - 软硬边分流；
  - 路径禁用和优化条件；
  - 超时不重发；
  - 单引擎交接；
  - 陈旧自动文档的所有权证据、30 分钟阈值、人工窗口保护、安全保存、逐份关闭与未知状态回退；
  - `layer.place_file` 的实时状态、允许根、嵌入式智能对象结果、Alpha 一致性与回滚；
  - 技术与视觉双门禁。
