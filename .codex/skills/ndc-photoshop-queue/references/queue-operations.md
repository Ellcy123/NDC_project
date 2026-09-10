# Photoshop 队列操作与恢复

按需阅读：客户端与入口 → 正常交棒 → 离线审核；只有发生人工操作或异常时才读取对应部分。下列接口来自本 Skill 的 `broker.mjs`、`queue-client.mjs` 与 `queue-core.mjs`，具体图像制作仍由原生产 Skill 决定。

## 客户端与入口

共用 stdio 代理提供 `photoshop_queue_*` 和原生 `photoshop_*` 工具，底层统一经过同一 broker。已迁移客户端使用这些工具；旧任务仍缓存旧直连时，使用以下 CLI 调用同一个 MCP 接口，或重新连接到共用代理。仅更新 Skill 文档不能拦截旧直连客户端；不要同时保留两条生产执行通道。

从当前实际 `SKILL.md` 所在目录运行 PowerShell 公共入口；它自行寻找系统或 Codex 内置 Node，不依赖固定用户名、盘符或可用的 `python` 命令：

```powershell
$psTaskId = '当前真实任务ID'
$psSkillRoot = Split-Path -Parent '<当前实际 ndc-photoshop-queue/SKILL.md 路径>'
& (Join-Path $psSkillRoot 'scripts\queue-client.ps1') -Task $psTaskId -Action health
```

正式入队前先运行 `--action health`。`ok:true` 表示受审运行时哈希、允许根、队列数据库、导出目录、磁盘及 Bridge 的静态检查通过；`ready_for_new_lease:true` 才表示当前可尝试取得新租约。acquire 还会实时确认 Photoshop 响应且当前为零文档；已有文档返回 `UNMANAGED_DOCUMENT_OPEN` 并续期原等待票。出现阻断时执行返回的唯一 `next_action`，不得用重启 broker 代替文档、人工或未知命令恢复。

跨轮次恢复、上下文压缩、任务被唤醒或收到继续指令时，先运行：

```powershell
& (Join-Path $psSkillRoot 'scripts\queue-client.ps1') -Task $psTaskId -Action resume-check
```

它在同一当前 broker 上重新读取 health 和 status，并返回带时间的 `ndc-ps-resume-check/v1`、`photoshop_operational`、`current_blockers` 与 `resume_action`。旧轮次的 Bridge 断联、旧文档 ID、旧错误码、截图、摘要或 `PREPARED_NOT_ENQUEUED` 一律失效，不能直接转成“等待用户修复”；若 `photoshop_operational:true`，立即按 `resume_action` 使用已有票、重新绑定原 owner，或为已准备工作 enqueue/acquire。若为 false，仅记录本次 `checked_at` 和当前 blocker，继续独立分支；任务下次恢复时再运行一次，不把历史失败永久缓存。

把 `$psTaskId` 换为当前任务／会话的真实 ID，不能使用通用示例 ID。Node 必须支持 `node:sqlite`；公共入口优先使用 `NDC_NODE_EXE`，其次使用 PATH 和当前用户的 Codex 内置 Node。不得把 Windows Store `python.exe` 的无输出或退出码 9009 记成 PS MCP 故障；需要 `ndc_art.py` 时必须先解析到真实 Python，或直接使用上述不依赖 Python 的队列入口。`scripts/runtime-binding.json` 只记录可提交的相对约定与受审哈希；PS MCP 外部运行时默认从 `%LOCALAPPDATA%` 解析，非标准安装设置 `NDC_PS_MCP_RUNTIME`。允许目录来自 `NDC_PS_ALLOWED_ROOTS` 或当前机器 NDC 配置，队列状态默认在当前用户 `%LOCALAPPDATA%/NDC/photoshop-queue`。

state dir、client session、client-key 和 Bridge secret 必须设备隔离；另一台电脑不得复制这些状态或并发打开同一个 `queue.sqlite`。端口仅在设备本地通过 `NDC_PS_QUEUE_PORT` 覆盖。

CLI 的请求文件是 UTF-8 JSON：顶层固定为 `name` 和 `arguments`，每次只调用一个接口。请求、日志及审核证据放入本任务的 `工作过程文件` 目录。执行方式：

```powershell
& (Join-Path $psSkillRoot 'scripts\queue-client.ps1') -Task $psTaskId -Request $psRequestPath
```

`$psRequestPath` 必须指向已写好的本次 JSON 文件。CLI 以命令行 `--task` 为权威身份，覆盖 enqueue/acquire/recover/cancel/review/external 请求中残留的旧 `task_id`，并自动填写 `acquire/cancel` 的 ticket；这避免 handoff 后审核查到另一个任务键。私有租约上下文采用临时文件原子替换，损坏文件会隔离为 `.corrupt-*` 后走同任务 rebind。不要手写 token、读取并打印 client-key，或复用其他任务的会话文件。每次检查返回内容及退出码，退出码 2 表示调用失败。

同一轮 `enqueue` 到 `release` 使用同一客户端类型。stdio 代理的上下文与 CLI 的本地会话文件不自动互通，不要在 stdio 取得租约后直接改用 CLI 操作。stdio 重连或 CLI 上下文丢失不表示 PS 已释放，按异常恢复处理。

同一任务上下文丢失但 broker 仍记录其所有权时，再次 `acquire` 会隔离旧 token、重新发放租约并自动执行串行 probe；只有返回 `acquired:true` 且 `production_resumed` 不为 false 才继续修改。probe 暂时失败时保留返回的新租约，仅重试 `photoshop_queue_probe`，不重新入队。

`status`、命令检索／说明和能力目录属于不接触当前文档的元数据；`photoshop_state_get`、`photoshop_preview_get` 等实际宿主读取也要先 acquire。`status` 的队列空闲、bridge 计数及已配对信息都不等于完成一次实时宿主核对。

## 正常交棒

### 异常占位自动接续（2026-09-09）

本节覆盖后文旧“活跃心跳绝不回收”和“等待者必须取消票再恢复”的人工恢复步骤，仅针对自动acquire路径。用户已授权等待任务自行处理异常占位，不再请求例行确认。队首acquire会在owner失联180秒或无有效进展300秒后自动回收；原生handler/in_flight仍运行时先等待，不以耗时关闭。恢复保持原等待票、原资产及次数，旧epoch立即失效。随后执行实时probe：未绑定文档才可直接释放；队列打开且仍干净的源图须先关闭再释放；出现未保存变化时先转为脏状态并救存。脏文档必须匹配原document_id，实际导出唯一PSD/PNG并checkpoint后关闭释放，原任务记录WAITING_REVIEW。实证文档已经丢失则按原lost_document流程记录FAIL，不能当已保存。

返回acquired:true表示恢复完成且已领取自己的生产资产；acquired:false且有recovery表示自动恢复未结束，约30秒后用同一task和ticket继续acquire，不另开任务、不删除队列数据库、不调用审批窗口。已配置路径不可用、救存失败等先检查并采用已有授权的静默能力修复；不能声称此机制可绕过宿主权限或任意销毁未保存文档。明确人工占用保持其原协议。后文recover/probe仍用于已有手动恢复租约的诊断，不是自动接续的额外审批关卡。

### 1. 输入准备后排队

先完成来源、提示、坐标／选区方案和必要文件准备，记录本任务当前资产的累计尝试，不占着 PS 等生图。写入请求：

```json
{
  "name": "photoshop_queue_enqueue",
  "arguments": {
    "asset_id": "当前资产的稳定ID",
    "description": "当前图要执行的已授权操作及本轮安全保存点",
    "ready": true
  }
}
```

CLI 自动填任务 ID；stdio 直接调用时需填写 `task_id`。一个任务最多有一个待处理请求，同资产重复 enqueue 返回原 ticket，不获得额外排队位置。当前资产尚未完成审核时不能换资产；已完成真实检查的 FAIL 按下文“离线审核及重新进入”决定有限返修或有据封存，不借新 ID 绕过未审门禁。

```powershell
& (Join-Path $psSkillRoot 'scripts\queue-client.ps1') -Task $psTaskId -Action acquire
```

仅返回 `acquired: true` 才可开始原生操作。`WAIT_TURN`、`BUSY`、`MANUAL_PENDING`、`EXTERNAL_USE` 均表示等待；`ALREADY_HELD` 不重新给出租约，沿用本客户端已保存上下文。仍准备好立即接手的在线任务约每30秒再次调用 `acquire`，等待期间可做短时独立工作，不高频轮询或重复 enqueue。尚在等待且已不需要 PS 时，用 `photoshop_queue_cancel` 的空 arguments 请求取消自己的 ticket，持有者不能用 cancel 代替安全 release。

未持有PS的等待票默认5分钟不调用 acquire 续期即过期移除，审计原因为 `UNACQUIRED_WAITING_TICKET_EXPIRED`；watchdog每5秒以及 enqueue/acquire 入口会清理过期待处理票，避免失联等待者长期占据队首。`status` 是只读观察，不延长等待票；返回 `TICKET_NOT_WAITING` 且 `reenqueue_required` 时，先确认仍有准备好的需求，再以原真实任务和资产重新 enqueue，到队尾取得新票。不要让常驻代理替所有任务永久续期，否则死任务也会被保活。该时限仅移除尚未取得PS的等待请求，不使自动owner、在途／未知命令或人工reservation自动过期、释放或转正。

### 2. 原生 MCP 操作

获得使用权后先读取实际状态，核对目标文档及输入。使用已暴露工具或 `photoshop_command_search`／`photoshop_command_describe` 核实的原生命令，所有权限与前后置检查继续有效。CLI 原生调用仍写同样的请求结构，例如导出当前文档：

打开 NDC 已允许根内的现有源图时，先确认 `photoshop_queue_health.runtime.production_commands` 中 `document.open_allowed` 为 `supported`；然后使用 `document.open_allowed` 与真实绝对路径。broker 在原生命令入账前验证能力状态以及文件真实存在、非空、可读且规范路径仍在本机 `ndc.local.json`／`NDC_PS_ALLOWED_ROOTS` 定义的现存根内，再映射为请求绑定的一次性认证导入。能力仍为 `experimental`／`unverified`／`requires_user` 时返回 `CAPABILITY_NOT_PRODUCTION_READY`；不得用一次成功调用代替正式能力晋级。`document.open_default` 在生产队列内直接返回 `OPEN_ALLOWED_REQUIRED`，不要把源图预复制到队列导出目录。打开本身只绑定当前租约、源文件证据与文档，不算图像修改；若尚未执行任何实际修改且宿主仍报告文档已保存，可以 `document.close`（`save:false`）后以 `NO_IMAGE_CHANGE` 释放，不制造 PSD/PNG 检查点。若文档变为未保存，返回 `UNTRACKED_DOCUMENT_CHANGES`，必须救存。一个租约只能绑定一个打开的文档，且文档总数必须始终为一；换图必须先关闭并释放后重新入队。

```json
{
  "name": "photoshop_command_execute",
  "arguments": {
    "command_id": "document.open_allowed",
    "idempotency_key": "本资产本轮打开源图的唯一操作ID",
    "args": { "path": "当前设备允许根内的真实绝对源图路径" }
  }
}
```

`exportFolderConfigured:false` 仅表示 UXP 中没有用户持久选择的外部导出文件夹；队列经认证 Bridge 导入／导出的能力与此状态分开判断。不得仅凭该字段推断一次性导入必然不可用。`document.open_allowed` 的失败必须保留底层错误：本地路径或允许根验证失败应在提交 Photoshop 前返回；提交后的 `HOST_ERROR`／超时仍按唯一恢复流程处理，不能换幂等键重放。

```json
{
  "name": "photoshop_command_execute",
  "arguments": {
    "command_id": "document.export",
    "idempotency_key": "本资产本轮保存PSD的唯一操作ID",
    "args": { "format": "psd", "file_name": "本任务_本资产_本轮唯一名称.psd" }
  }
}
```

本机 `document.export` 使用 `format`、`file_name`，没有任意目标路径参数；实际文件落在已有受控导出位置，以返回的真实绝对路径为准。导出 PNG 时改成 `format: png` 和另一唯一文件名。不要传入猜测的 `path` 参数或自动修改用户选中的 UXP 导出目录。若既有导出位置不能形成允许目录内的可验证文件，记录保存能力阻断，不凭空填写导出证据。

每个 `photoshop_command_execute` 都必须提供稳定 `idempotency_key`，按本资产本轮具体操作记录；无键请求返回 `IDEMPOTENCY_KEY_REQUIRED`，无键的 typed convenience 工具不再暴露并返回 `DURABLE_COMMAND_REQUIRED`。同一次提交的查询／重试沿用原 key，新的操作使用新 key；PSD 与 PNG 两次导出也分别使用各自 key。broker 将 key 按真实任务及资产隔离：已完成的相同请求返回原结果，`running/unknown` 拒绝重放，同 key 改参数返回 `IDEMPOTENCY_PAYLOAD_MISMATCH`。缓存结果不是当前图再次验收或再次执行的证据；结果未知时不能改 key 来强行重做。

同一张图中已授权、相互连续的操作可以组成一个安全段；不把每个小命令当作一次新艺术尝试。最后一次修改后依次经 MCP 导出 PSD 与审阅 PNG，之后不要再改像素／文档；后续实际修改会使旧导出证据和检查点失效。输出使用新路径，保留以前接受的快照和真实审核记录。

原生 `photoshop_job_*`、用户辅助作业、显示式对话框和重新配对不属于自动队列生产路径；这些接口不能通过换名字绕过限制。只有用户已有明确授权的人工步骤才进入人工交接。所有 Photoshop 内操作仍走已批准 MCP 通道，不调用原始宿主执行后门。

### 3. 检查点与释放

正常生产优先使用原子交棒请求，避免任务在两次导出、checkpoint、关闭和 release 之间停顿。handoff 必须关闭队列文档；`close:false` 返回 `HANDOFF_CLOSE_REQUIRED`，不能留下孤儿文档再释放：

```json
{
  "name": "photoshop_queue_handoff",
  "arguments": {
    "file_prefix": "当前资产_本轮唯一安全交棒名",
    "resume": "目标设备或下次租约从该PSD恢复并先核对审阅PNG与来源哈希",
    "close": true
  }
}
```

`file_prefix` 只作为文件名，broker 会移除路径和非法字符。修改过的文档必须连续生成本轮 PSD/PNG；任一步失败时不得另开任务或重启 broker，使用同一租约和幂等记录继续核对。未修改文档直接释放，不为了关闭而制造假导出。

使用 MCP 返回的实际 PSD／PNG 路径和文档 ID 构造检查点；`document_id` 必须保持实际返回类型，不能把数字 ID 擅自转成字符串。

```json
{
  "name": "photoshop_queue_checkpoint",
  "arguments": {
    "document_id": 123,
    "files": [
      { "path": "D:/Codex/NDC/工作过程文件/本次已实际导出的文件.psd", "role": "working" },
      { "path": "D:/Codex/NDC/工作过程文件/本次已实际导出的审阅.png", "role": "review" }
    ],
    "resume": "从已保存PSD核对来源哈希和文档，再继续当前资产指定步骤；当前PNG等待技术与整图局部真实审核"
  }
}
```

示例路径、文档 ID 和恢复步骤必须替换为本轮真实值。checkpoint 会重新计算文件哈希，要求文件匹配当前文档在最后修改之后的实际 MCP export 记录；手工写哈希、仅复制旧文件或传入其他文档 PSD 均不能证明本轮已保存。`view` 可作为附加文件角色，但修改后的检查点内每一个文件都必须满足同一导出证据条件；离线制作的局部审阅图放在后续审核记录里，不伪称为 MCP export。

```powershell
& (Join-Path $psSkillRoot 'scripts\queue-client.ps1') -Task $psTaskId -Action release
```

release 成功后，该图进入 `WAITING_REVIEW`，下一个独立任务可以取得 PS。文件被改动、缺少当前检查点、命令在途或结果未知都会阻断释放；先解决所报问题，不删除队列文件。未改图且无未解决命令可直接释放，返回 `NO_IMAGE_CHANGE`，不生成艺术通过记录。客户端退出仅会尝试同样的安全释放，不能保证脏文档已经交棒。

只要本租约绑定过文档，release 前就必须关闭。修改过的文档只有在实际导出的 PSD／PNG 已建立当前有效 checkpoint、实时活动文档确为本租约文档时，才可通过原生 `document.close` 执行，再 release；只打开且未改动的已保存源图也须关闭。安全关闭用于释放本任务文档资源，不关闭用户或其他任务的文档；不得先关闭再补保存证明，也不把关闭作为图像PASS。未绑定过文档的纯检查租约才可直接 release。

## 离线审核及重新进入

释放后检查固定 PNG 的技术指标、整图 100% 和局部至少 200%，并完成原生产 Skill 的适用视觉项。审核必须由真实查看形成，队列、SHA-256 和文件存在性均不能判断艺术质量。

登记使用现有 `ndc-stage-visual-self-check/v1` JSON 记录：包含真实 `stage_id`、`reviewer`、`reviewed_at`，当前输出与输入路径／SHA-256，`whole_100` 和 `local_200_or_tiles` 审阅视图，适用 `criteria` 的明确发现及 `visual_check_status`。失败记录保留 FAIL 和 `rework_stage`；Type 7、热区等仍需满足原专项记录要求。不得为了队列登记改变资产角色以避开专项检查。不同角色／场景的专业审核继续由原 Skill 执行。

```json
{
  "name": "photoshop_queue_review",
  "arguments": {
    "asset_id": "当前资产的稳定ID",
    "record": "D:/Codex/NDC/工作过程文件/本轮真实视觉记录.json"
  }
}
```

CLI 强制使用当前 `--task` 绑定 `task_id`，无需占有 PS；请求文件中的旧任务 ID 不再影响快照查找。队列调用绑定的 `validate-queue-review.py` 与现有 NDC 校验器，只核验记录及当前快照关系，不生成视觉判定。登记被拒绝时检查记录结构、实际文件和当前快照关系，保留真实失败结论；不能把子项或总状态改成 PASS 来换取登记成功。

当前图技术和真实视觉检查完成、当前哈希核对一致后，PASS 可进入相应后续依赖。FAIL 须记录明确缺陷：仍有原预算且需修复时继续原资产责任阶段；预算已耗尽或用户明确指示封存时，保留候选、失败审核、原始次数及停止依据，封存该分支后可 enqueue 其他独立资产。FAIL／NOT_CHECKED 都不能成为后代的通过输入，不能把失败候选写入正式交付；同场人物入景的联合前置仍未通过时，也不能把同场其他角色伪称为无依赖资产。

队列 `review` 可登记真实 PASS 或 FAIL；`WAITING_REVIEW` 仍阻止同任务换图，FAIL 登记后允许排队不代表生产门禁或预算自动批准。执行者按原生产记录保存封存依据及依赖阻断，不得假造 PASS 或重新开次数。原图需再次进入 PS 时按原 `task_id`、`asset_id` 重新 enqueue，从队尾取得新租约，核对不可变来源、已保存 PSD 及恢复起点后继续。保存、挂起和恢复不重新计算艺术预算；失败、拒收及来源变化只影响实际依赖项。

## 人工占用

人工正在使用或即将接手同一 PS 时，用当前负责交接的真实任务 ID 请求：

```json
{
  "name": "photoshop_queue_external",
  "arguments": { "active": true, "note": "人工接手的具体范围及已知交接状态" }
}
```

存在自动持有者时返回 `REQUESTED`：新任务不能 acquire，当前持有者不再提交修改，只在已有命令结束后核对、导出保存、checkpoint 并 release；释放后转为 `ACTIVE`。没有自动持有者时直接进入 `ACTIVE`。REQUESTED 表示等待安全交棒，不能告知人工已经可以与自动任务同时编辑。

人工已经开始操作时立即登记并停止新增自动修改；核对是否改变活动文档和未保存状态。人工打开其他文档也会影响同一 PS 的全局状态，不能视为可并行。若在途命令尚未结束或结果未知，保留阻断，先按异常恢复核实，不以人工请求强行中断、覆盖或丢弃未保存工作。

人工明确结束后，原登记任务可提交 `photoshop_queue_external`，arguments 使用 `active: false` 及实际交接说明。原登记任务失联或由另一在线任务代办时，代办者仍使用自己的真实任务 ID，并附用户当前明确“用好了／已结束”的指令来源：

```json
{
  "name": "photoshop_queue_external",
  "arguments": {
    "active": false,
    "user_confirmed_finished": true,
    "confirmation_note": "用户明确结束人工PS操作的实际任务、时间及原指令来源",
    "note": "原登记者失联，由本任务按用户已结束指令代办解除"
  }
}
```

以真实来源替换示例说明，不能只填“10分钟已过”。队列返回并审计 `manual_release` 的原声明者 `declarer_task_id`、代办者 `released_by` 及确认依据；不能冒用原 task_id、凭超时自动清除或把沉默当结束。解除人工占用不自动解除仍存在的自动 owner、在途命令或未知结果，后者继续按自身恢复门禁处理。

自动任务重新排队并核对实时文档，不能直接续用旧活动文档假设。仅等待人工从别处回传补肩／去底文件不占用本机 PS，不应无限维持 external。人工接手不扩大自动补肩或其他图像修改权限。

## 异常恢复

先用 `--action status` 读取 `diagnosis`、owner、in_flight、unknown、external、handler_running 和 bridge；不要仅看计时或 queuedCommands。

| 状态／证据 | 处理 |
| --- | --- |
| `IDLE_HELD`：默认 120 秒无有用进展 | 提醒当前任务交出安全段；心跳只表示活着，不代表进展或无限续占许可。 |
| `STALE_SAFE`／`STALE_UNSAVED`：默认 180 秒无心跳 | 仅为疑似失联，核实持有者和宿主；不能由时间直接让第二个写入者开始。 |
| `COMMAND_RUNNING`／`COMMAND_OVERDUE` 或 handler_running | 仍有执行中请求，等待明确结果；最长占用或请求预算到期不等于宿主已停。 |
| `UNKNOWN_COMMAND`、网络／客户端超时、重启后的未知提交 | 不重放命令、不释放、不直接重新 acquire；执行唯一恢复流程。 |
| `ACTIVE_DOCUMENT_CHANGED` | 原资产与活动文档关系不可信，停止修改，核对人工或旧直连是否改变状态；不得导出另一文档冒充原资产。 |
| `BRIDGE_SESSION_CHANGED` | 插件实例已更换；用当前租约执行 `probe`。文档 ID 匹配时自动恢复生产，否则进入保存型恢复。 |
| `BROKER_INSTANCE_CHANGED`／客户端上下文丢失 | 同任务重新 `acquire` 触发 fencing 与重绑；有在途／未知命令时仍进入唯一恢复流程。 |
| `HOST_PREFLIGHT_FAILED` | 尚未授予 owner，原等待票已续期；恢复 Bridge／PS 响应后用同一票重试 acquire。 |
| `DEVICE_HANDOFF_REQUIRED`／`FOREIGN_DEVICE_LEASE` | 停止使用旧 token；只能从源设备原子交棒形成的 PSD/PNG 检查点在目标设备重新入队。 |

恢复请求：

```json
{ "name": "photoshop_queue_recover", "arguments": {} }
```

CLI 自动填当前真实任务 ID，并保存成功返回的新租约。若本恢复任务还有排队中的生产 ticket，先取消自己的等待票；`RECOVERY_TASK_QUEUED` 不能通过换假任务 ID 绕开。broker 只允许一个恢复操作者；仍有原生命令 handler 或记录中的 in_flight 时拒绝接管，其他持有者仍响应时也不能夺取。恢复成功会隔离旧租约，**尚未证明宿主空闲或原图合格**。接着执行：

```powershell
& (Join-Path $psSkillRoot 'scripts\queue-client.ps1') -Task $psTaskId -Action probe
```

probe 通过同一个桥接串行请求实际 PS 状态，成功只证明执行顺序已核对，不证明超时操作没执行、图像已保存或视觉合格。观察真实结果，不盲目重放原命令。恢复租约只用于允许的状态查看、救存导出及检查点验证后的本租约文档安全关闭；仍有正确文档时核对并导出 PSD／PNG、checkpoint、安全关闭、release，再重新排队进入正常制作。若文档身份不符或无法救存，保留恢复阻断，不擅自关闭文档或覆盖已有资产。

只有确实没有打开文档、未保存结果已经丢失时，才请求：

```json
{ "name": "photoshop_queue_lost_document", "arguments": {} }
```

该接口会再执行一次新鲜实时 probe，只有 `hasDocument: false` 且 `documentCount: 0` 才把原任务未保存工作标为 `FAIL / UNSAVED_DOCUMENT_LOST` 并释放。旧截图、旧状态、断联、单独 missing activeDocument 或猜测“PS 应该关了”均不构成证明；不得主动关掉文档来满足该条件。返回 FAIL 是数据丢失处置，不是艺术审核完成或原资产可交付。

后台监测可对已保存／未变的 `STALE_SAFE` 分支取得唯一恢复租约，在实时 probe 成功且检查点仍有效后释放；不会依据超时盲抢未保存或未知结果。自动恢复失败查看 `recovery-needed.json` 并按上述单一恢复流程处理，不能启动第二个 broker 来绕过。

不得由普通生产任务调用 `Stop-Process`、删除 `broker.json`、删除 WAL/SQLite 或直接启动第二个 broker。broker 进程变化会立刻进入 `RECOVERY_REQUIRED`；原任务重绑或队首任务驱动恢复，不再等待普通陈旧计时。维护重启仅在 health/status 同时证明无 owner、无 waiting、无 external、无 handler 时进行一次，并在重启后重新 health。

## 设备切换

只支持可证明的冷切换：源设备完成 `photoshop_queue_handoff`，保存检查点中的 `device_id`、文件路径和 SHA-256；目标设备取得全新的本地租约，核对文件哈希后打开 PSD，并接受新的 Photoshop 文档 ID。旧 ticket、epoch、token、broker/Bridge 实例和文档 ID 全部失效。

源设备突然掉线且最后修改没有有效 checkpoint 时，目标设备不得自动接管、关闭或重放。将状态记为 `SOURCE_DEVICE_UNREACHABLE`，从最后一个有效 checkpoint 恢复；checkpoint 之后的结果保持未知。若未来需要两台电脑同时在线调度，必须另建中央协调服务，不能把 SQLite 放到同步盘或网络共享目录冒充分布式锁。

## 运行时边界

`scripts/runtime-binding.json` 当前适配原生 Photoshop MCP `2.0.1-ndc2`，其中 `document.open_allowed` 仅在真实 NDC 允许根导入、状态核验和无修改关闭均通过后晋级为 `supported`。绑定文件只保存可移植的相对约定与受审哈希；当前机器的运行时、Python、允许目录、验证器和 `state_dir` 由 `runtime-config.mjs` 解析。原生 server/config/bridge/policy/catalog 的指定哈希均须匹配，并且 `document.open_allowed`、`document.export`、`document.close` 三项生产必需能力都必须为 `supported`；变化返回 `RUNTIME_CHANGED` 或 `CAPABILITY_NOT_PRODUCTION_READY`，先安装/复核完整运行时及门禁，不能只更新哈希或复制 catalog 跳过检查。CLI 会连接本机已有 broker 或以隐藏方式启动，不能重复直接启动原生 server。

原有已配对关系、允许目录、用户选定导出位置及原生权限保持原意。`PAIRING_NOT_A_QUEUE_OPERATION`、`MANUAL_RESERVATION_REQUIRED`、`UNADAPTED_NATIVE_TOOL`、`CAPABILITY_NOT_PRODUCTION_READY` 等错误要求停止对应操作、说明实际能力边界；不得通过重新配对、改目录、原始脚本注入、界面自动化或关闭用户文档来使队列“成功”。真实验证只证明记录中的运行时、宿主和命令契约；切换电脑仍需安装相同受审运行时并重新通过 health。
