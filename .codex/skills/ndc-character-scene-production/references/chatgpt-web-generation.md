# 网页版 ChatGPT 生图

本页只用于人物入景第二阶段的正式像素生成。Terra/xhigh 仍是生产编排、判断与验收任务；像素生成后端固定为已登录的 `chatgpt.com` 网页版 ChatGPT。浏览器载体可为 Codex 内置 `iab`，或 Computer Use 当前支持且用户已指定/授权的外置 Chrome、Edge；不得改用 Codex 图片生成工具、`imagegen`、图片 API、其它站点或其它生图后端来“临时顶替”。

## 逻辑场景工作区、并发对话和输入

- 使用 Computer Use 当前文档支持的可见浏览器入口。用户指定 `iab`、Chrome 或 Edge 时优先使用该浏览器；未指定时选择当前健康、已登录且可追溯的受支持浏览器。只接受 `https://chatgpt.com/` 域名；不要输入、索取、记录或保存账号密码、验证码、Cookie 或令牌。登录、验证码、地区限制或账号门禁需要人工处理时，记录 `WAITING_MANUAL`，只阻断依赖该网页提交的分支。
- 浏览器载体没有固定先后顺序：按用户指定，以及当时的健康、登录和可追溯状态动态选择；不同已登录 ChatGPT 账户均可继续任务。提交前当前载体不可用时，可切换受支持浏览器或账户；未发生提交时不计模型 attempt。若当前账户仍能访问原生成单元的专用对话或结果，切换只用于接续该 URL、验收和下载，不新建对话、不重新提交。若新账户因账户隔离确实没有原对话、历史消息或结果，则按“账户切换与记录缺失”封存旧状态后，在同一场景窗口登记后继对话重新生成。登录／验证码仍按 `WAITING_MANUAL` 处理，不输入、搬运或保存凭据。用户已授权实际人物入景生产时，冻结 submission packet 内的三引用上传及对应提示词提交属于已交办流程，不再逐角色、逐次或逐文件向用户请求“发送”确认；该授权不包含包外文件、其它场景或其它外部操作。
- 每个完整 `scene_id + revision` 建立一个逻辑场景工作区：一个浏览器/session 身份加一组可追溯标签页即可，不强制独占物理 OS 窗口。每个角色或不可分割状态组作为一个 `generation_unit_id`，使用自己的 ChatGPT 对话。不同 revision 新建工作区并 `supersede` 旧工作区；旧对话只用于核实已提交结果，不再提交旧引用。
- fan-out 前只做一次真实轻量 canary。先记录浏览器 `HEALTHY`，再记录 canary `PASS`，工作区才成为 `READY`；失败载体进入 `QUARANTINED`。默认 `max_open_submissions=3`，限流时降至 1–2。不同角色或同一角色不同 pose 可以并发；同一对话只允许一个未决 packet/submission，同一 actor/pose 不得跨对话重复占用。
- 每次提交都重新上传实际三引用，顺序固定为：1 `local-whitebox-crop`，2 `untouched-full-scene`，3 `approved-character-card`。三项都必须是本地哈希绑定的真实 PNG、JPEG 或 WebP 图片，不能以文本、快捷方式、截图外壳或仅文件扩展名代替。等每个附件在网页上显示完成后再提交。粘贴当前 `PROMPT_STYLE_BINDING_GATE: PASS` 对应的完整提示词原文；不得依赖“同上”“按上一张”或其它标签页的历史自动补足缺失约束。角色卡和用户原版固定风格块共同承担风格锁定，任何一个都不能因同窗已有其它对话而省略。
- 提交前核对工作区 ID、当前标签页的 `generation_unit_id`／actor／pose、完整 URL、三引用顺序及 SHA-256、提示词 SHA-256、网页附件状态和单元工作目录。在一个原子操作段内完成三项上传、等待、三个独立缩略图核对、提示词粘贴和 `confirm-uploads`；任一项缺失都不点击发送。浏览器文件名或成功提示不能代替本地哈希。

## 网页模型档位与自动提交

- 场景窗口初始化时先检查网页当前模型选择器；每个新对话首次正式提交前，以及页面重载、账号状态变化或模型选择可能改变后再次核对。默认选择页面显示的“极高”档位；没有“极高”或该档位不可选时，选择当前账号实际可用的最高档位。若选择器锁定但当前档位已经是“极高”或实际最高可用档位，直接继续；不得等待解锁、修改账号设置、绕过限制或切换生图后端。
- 在 submission 记录或同目录工作记录中保存页面实际显示的档位名称；使用回退时同时记录“未提供／不可选极高”和最终最高可用档位。模型档位文字与 Terra 的 `thinking: xhigh` 是两个不同字段，不得互相冒充。
- 模型选择、冻结包上传和一次正式提交均是已授权生产的自动步骤。只要当前 scene/revision、身份来源、白模、提示词和全部前置门禁已确定，就直接执行，不输出“请回复发送某角色”之类的确认门槛。只有登录／验证码必须人工处理、用户明确暂停、或出现会改变授权范围的真实未决选择时才等待；一般偏好问题和逐角色发送不构成等待理由。

## 浏览器窗口／标签绑定与原图下载恢复

- 每次接管已经打开的场景窗口时，先按当前 Computer Use 浏览器文档取得精确浏览器／session 句柄，核对 `scene-window-identity.json` 的 window ID、scene/revision 和 browser，再枚举窗口内标签页，以完整 `conversation_url` 逐一认领对应生成单元。能够读取标签页快照、但动作返回“标签页不属于当前 browser session”或同义错误时，判定为**会话绑定失效**，重新枚举并认领；不得把它误记为浏览器无响应，也不得因此另开窗口、新建对话或重发。
- 浏览器清单、标签页枚举或控制传输第一次超时／连接失败时，只对同一轻量检查重试一次；仍失败则重置 Computer Use 控制会话、重新读取当前文档并再检查一次。重置后仍失败，登记 `BROWSER_CONTROL_TRANSPORT_UNAVAILABLE`。内置与外置浏览器若共用同一失效的控制服务，不得在两者之间循环切换并重复超时；保留原对话 URL、已生成结果证据和恢复检查点，继续离线工作，待控制服务恢复后从同一结果接续。
- 若全量清单或会自动附带可访问性快照的便捷调用超时，但当前文档提供的浏览器句柄、`browser.tabs.list()`、`browser.tabs.get()` 或 `tab.playwright.domSnapshot()` 仍能返回，判定为**包装层或普通侧栏标签绑定故障**，不能登记为整个控制传输失效。内置浏览器应创建或复用当前任务的 `browser-use` 标签页，再通过底层标签页句柄打开精确 `conversation_url`；普通侧栏浏览标签即使可枚举，也不得因无法附加调试器而反复接管。外置浏览器存在多个配置时，必须选择目标 profile／extension instance 的精确句柄，再按当前文档枚举并认领原标签，不能用模糊的浏览器名称代替。只有这些底层页面调用按有限重试仍失败，才登记 `BROWSER_CONTROL_TRANSPORT_UNAVAILABLE`。
- 同一台机器／同一实际下载目录同一时刻只允许一个任务认领浏览器下载。点击前记录候选序号、结果可访问性标签、完整 `conversation_url`、原图元素固有尺寸，以及页面能提供的 resource／asset 标识；然后运行 `python scripts/download_receipt.py begin --directory <actual-download-dir> --snapshot <packet-work-dir>/download-snapshot.json --owner <task-scene-unit>`。成功取得目录锁并冻结前快照后才允许点击。目录锁只协调 Codex 任务，不允许把人工同时下载产生的文件猜成当前结果。
- 先启动 `tab.playwright.waitForEvent("download", { timeoutMs: 15000 })`，再点击网页“保存”**一次**。事件成功时只调用 `await download.path({ timeoutMs: 15000 })`；当前 Codex Browser 的 `PlaywrightDownload` 合同不提供 `suggestedFilename()`，不得调用，也不得从人类可读文件名推导归属。把 `path()` 的真实返回值交给 `download_receipt.py complete-event`，复制到 packet 的不可覆盖规范文件名并记录回执。`path()` 为空或文件不可读仍不二次点击，转入同一次动作的目录核实。
- 下载事件监听超时只表示**事件回执缺失**，不等于网页下载失败。对同一 snapshot 运行 `python scripts/download_receipt.py settle --snapshot <snapshot> --receipt <receipt> --destination <packet-work-dir>/<scene-revision-pose-attempt-candidate>.png`；脚本仅接受点击后新建或真实改变、稳定且唯一的 PNG／JPEG／WebP，并记录 aware UTC、本地时区、文件 ID、字节数、格式、固有尺寸与 SHA-256。`NO_NEW_FILE_OBSERVED`、`AMBIGUOUS_DIRECTORY_DELTA`、尺寸／哈希不符均不得认领；绝不使用“最近文件”、旧文件名或未换算的 UTC／本地时间近似匹配。终态回执会释放目录锁；流程中断时只用 `release` 释放同 token 锁。
- 无论事件路径还是目录 delta，运行 `download_receipt.py verify` 并把文件 SHA／尺寸同页面候选、asset／resource 标识及视觉身份逐项核对；回执只证明文件取得与字节身份，不替代人物、姿态、场景或风格审核。网页图片完整显示、缓存命中或按钮状态改变，都不能单独证明已持久化下载。
- 事件与目录核实都失败、但当前结果仍完整显示时，可用 `pageAssets.list()` 锁定当前 inventory 中与页面候选／asset 标识相符的唯一 image，再用窄范围 `pageAssets.bundle({ inventoryId, assetIds })` 保存原始资源字节。该方法不是截图或重采样，但必须登记为 `NON_FORMAL_PAGE_ASSET_RECOVERY_CANDIDATE`，保存 inventory ID、asset ID、资源 URL、bundle manifest、对话 URL、尺寸与 SHA-256；不能填写正式 v4 回执的 `download` 字段，也不能宣称网页 Save 回执成功。正式门禁要求网页下载时，仍需在同一对话恢复 Save；不得因此重发生图。
- 若控制传输在原图已经完整加载后失效，可将已确认属于该结果的完整浏览器缓存对象复制到当前过程目录的 `recovery-candidates` 下，记录来源缓存路径、复制时间、字节数、SHA-256、图片类型、固有尺寸、对话 URL 和 asset 标识，并明确标为 `NON_FORMAL_CACHE_RECOVERY_CANDIDATE`。该候选只用于防止缓存淘汰和后续字节比对；不能填入正式 v3 回执的 `download` 字段，不能作为网页原始下载、视觉批准或 journal resolve 证据。
- 控制服务恢复后回到同一对话、认领精确标签页并使用网页提供的下载动作取得原始文件。原始文件落入 packet 的 `work_directory` 后，计算 SHA-256；若存在缓存恢复候选，同时记录两者是否字节一致。无论是否一致，正式回执只绑定本次网页下载得到且已实际打开核验的原始文件；不一致时保留两份并登记异常，不覆盖或静默替换。

## 记账、提交和回收

先为 scene/revision 建立一次场景窗口记录，并为各角色／状态生成单元登记不同对话 URL：

```powershell
python scripts/manage_scene_web_window.py init --directory <scene-window-dir> --scene-id <scene> --revision <n> --browser <iab|chrome|edge> --window-id <actual-or-stable-window-id> --window-label <scene-label> --created-at <ISO-8601>
python scripts/manage_scene_web_window.py record-health --state <state> --result healthy --checked-at <ISO-8601> --evidence <real-browser-check>
python scripts/manage_scene_web_window.py record-canary --state <state> --result pass --checked-at <ISO-8601> --evidence <tabs-dom-attachment-entry-check>
python scripts/manage_scene_web_window.py register --state <scene-window-state.json> --unit-id <unit> --actor-id <actor> --pose-id <pose> --conversation-url <https://chatgpt.com/c/...> --registered-at <ISO-8601>
```

对 READY 单元先运行重要度与 v2 提示词风格门禁，并保存最近 15 分钟内的流水 CURRENT revision gate，再用 `python scripts/build_chatgpt_web_submission_packet.py --contract <source-v3.json> --out-dir <unit_attempt_dir> --browser <iab|chrome|edge>` 生成不可覆盖的提交包。包中包含逻辑工作区身份、按序重命名的三引用、完整提示词、用户原版风格文本、重要度配置、revision/retry 控制及 v3 manifest/v4 receipt draft。操作者只能从该目录上传。

新 source 使用 `ndc-chatgpt-web-submission-source/v3`，其场景／角色字段必须与已登记单元完全相同；以下路径值在运行时从 `{WORK_ROOT}` 解析成真实绝对路径：

```json
{
  "schema": "ndc-chatgpt-web-submission-source/v3",
  "scene_window_state_path": "{WORK_ROOT}/.../scene-window-state.json",
  "scene_id": "SCxxxx",
  "revision": 1,
  "generation_unit_id": "actor-a__pose-a",
  "actor_id": "actor-a",
  "pose_ids": ["pose-a"],
  "prepared_at": "2026-09-11T23:00:00+08:00",
  "revision_gate": {"path": "absolute CURRENT gate", "sha256": "..."},
  "retry_control": {"attempt_number": 1, "defect_tier": "INITIAL", "consecutive_same_defect_count": 0, "method_changed": false},
  "uploaded_inputs": ["three bound file objects in fixed role order"],
  "prompt": {"path": "absolute packet source", "sha256": "..."},
  "prompt_binding_gate": {"path": "absolute v2 PASS gate", "sha256": "..."},
  "importance_profile": {"path": "absolute profile", "sha256": "..."},
  "importance_gate": {"path": "absolute PASS gate", "sha256": "..."}
}
```

随后对各单元运行流水 `guard`，再在原 journal 的对应 formal job 写入 `attempt`。新提交的 `submission.tool` 固定为 `chatgpt_web_browser`，`submission.operation` 固定为 `generate_image`；`arguments` 至少保存 `scene_id`、`revision`、`scene_window_id`、`generation_unit_id`、`actor_id`、`pose_ids`、`conversation_url`、`browser: iab|chrome|edge`、submission manifest 路径/哈希、用户原版 style-lock 哈希、prompt/importance profile 哈希、按上传顺序排列的引用 role/path/sha256，以及 `backend: chatgpt_web`。历史 `chatgpt_web_iab` 记录只作兼容审计。网页明确收到该单元消息后，立即运行 `manage_scene_web_window.py mark-submitted ...`；然后可切换到下一 READY 标签提交，不等待本单元生成完成。

三张附件和提示词已在网页实见后先运行 `confirm-uploads`；只有它成功，才点击一次发送。网页明确收到消息后运行 `mark-submitted` 并消耗一次真实 model attempt。生成失败、拒绝或无图也用 `resolve` 记录终态；页面仍在生成、断线或工具回执不清楚时先记录一次 `unknown`，随后必须核实成终态，不重复写 UNKNOWN、不重发。其它不同单元可继续并发、回收或离线准备。

若 packet 已 `PREPARED` 或已确认上传为 `UPLOAD_CONFIRMED`、但网页尚未收到任何提交，可用 `cancel-prepared` 保存原因并释放该对话；这不计真实 model attempt，也不得用于撤销已点击发送或结果不明的提交。场景全部单元均已终态且相关原始回执已冻结后，用 `close` 关闭 state；只读保留逻辑工作区身份、对话 URL、packet 与事件。存在任一 `PREPARED/UPLOAD_CONFIRMED/PENDING/UNKNOWN` 时禁止关闭。

```powershell
python scripts/manage_scene_web_window.py confirm-uploads --state <scene-window-state.json> --unit-id <unit> --confirmed-at <ISO-8601> --evidence <three-independent-thumbnails-and-prompt>
python scripts/manage_scene_web_window.py mark-submitted --state <scene-window-state.json> --unit-id <unit> --submission-id <submission> --submitted-at <ISO-8601>
python scripts/manage_scene_web_window.py resolve --state <scene-window-state.json> --unit-id <unit> --result <unknown|produced|failed|refused|account_record_unavailable> --resolved-at <ISO-8601> --evidence <evidence>
python scripts/manage_scene_web_window.py cancel-prepared --state <scene-window-state.json> --unit-id <unit> --cancelled-at <ISO-8601> --evidence <pre-submit-reason>
python scripts/manage_scene_web_window.py close --state <scene-window-state.json> --closed-at <ISO-8601>
python scripts/manage_scene_web_window.py supersede --state <old-state> --replacement-revision <n+1> --superseded-at <ISO-8601> --evidence <new-revision>
python scripts/manage_scene_web_window.py resume --state <scene-window-state.json>
```

## 账户切换与记录缺失

- 账户不同本身不是阻断条件。记录不含凭据的 `account_profile_label`（例如用户可辨识的浏览器配置／账号别名）、browser、切换原因和时间；禁止记录邮箱全称、密码、验证码、Cookie、令牌或其它认证数据。
- 原生成单元专用对话／结果可访问时，继续沿用原 URL、submission ID、attempt 与回执，不能因为换了账户再发一次。
- 只有当前新账户确因账户隔离看不到原专用对话、历史消息或生成结果，且已保存最后可知状态和核实证据时，才把原 pending/unknown resolve 为 `account_record_unavailable`。该终态保留原 submission、URL 和一次真实 model attempt，不记为 `no_output`，也不计作工具错误。
- 随后在当前场景窗口 state 中以 `--supersedes-unit-id` 登记同 actor/pose 的后继对话，再以当前冻结输入、完整提示词、用户原版 style-lock 和重要度配置的相同哈希建立不可覆盖的后继 submission packet。因为新对话 URL 不同，后继包须保留旧 manifest 路径／SHA-256、旧 submission ID、旧 URL、`account_record_unavailable` 证据、新账户非敏感标签和新 URL。若又一次发生经核实的账户隔离，可继续建立多级后继，但必须形成单一可追溯链；不得从任一旧单元分叉出两个后继，也不得跳过当前链尾。重新提交是新的真实 model attempt，受原 journal 剩余额度约束。若旧记录后来恢复可访问，只用于审计与回收，不覆盖新记录、不补发，也不把两个结果冒充同一次尝试。

生成完成后：

1. 在网页中打开对应生成结果，按上述加锁 snapshot → 单次 Save → event `path()`／唯一目录 delta 协议取得原始图像；不使用屏幕截图、浏览器缩略图、复制粘贴的预览或系统重采样版本作为生产源。
2. 保存到 packet 分配的 `work_directory` 内，文件名包含 scene、revision、pose、attempt 和 candidate 序号，并保留 download snapshot／receipt；不直接进入 `最终交付`。
3. 计算下载文件 SHA-256，实际打开检查可读性、尺寸和候选对应关系，再补全提交包中的 `ndc-chatgpt-web-generation-receipt/v4` 回执。回执必须逐字匹配 v3 manifest 中的工作区、revision gate、retry control、原版 style-lock、prompt、importance profile 与三引用路径/哈希。验证器会再次读取 prompt 并复核门禁；旧 v3/v2/v1 只可用对应 `--allow-legacy-v*` 开关审计历史，不得用于新提交。
4. 运行 `python scripts/validate_chatgpt_web_receipt.py --receipt <receipt.json> --output <gate.json>`；只有 `CHATGPT_WEB_GENERATION_GATE: PASS` 才能用回执绝对路径作为 journal `resolve` 的 evidence。随后按 H0/H1/H2/H3 对上下文结果完成提取前分流：失败则在原生成阶段有限返修，通过则冻结原始文件／回执／审核结论／SHA-256，并默认继续本场下一未完成角色或状态。冻结 scope 全部生成／复用项齐备后整体转入提取阶段是优先顺序，不是硬门禁；网页生成、回收或浏览器传输真实等待／受阻，或其它具体调度理由已记录时，可先提取已经就绪的角色。无论顺序如何，同一真实观察可引用到多个相容门禁，不能重复截图充当重复审核；缺项不能从整场 scope 删除或被局部完成掩盖。网页“已生成”或回执验证只证明来源与文件身份，不构成艺术 PASS。

## 停止与恢复

网页限流、上传故障、会话失效或生图能力不可用时，同一原样操作最多重试一次；再次失败须缩小并发、缩小诊断、切换受支持浏览器／已登录账户或等待恢复。收图恢复依据当前载体的实际故障动态处理，不预设固定核验顺序。提交前切换浏览器或账户不计模型 attempt；提交已发生或结果未知时，原记录可访问则只在对应单元的原对话核实，不得重发，也不关闭仍健康的同场并发对话。只有账户隔离导致原记录确实不可访问时，才按上一节以 `account_record_unavailable` 封存并在新账户发起新的计数尝试。不得切回 Codex 图片生成或图片 API。保存场景窗口 state、各 URL、browser、账户非敏感标签、submission ID、pending/unknown 状态和已下载候选，继续其它同场对话回收、场景记录、离线审阅或独立工作。
