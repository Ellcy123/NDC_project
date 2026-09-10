# ndc-photoshop-queue 安全删除与跨设备迁移记录

后续多客户端端口冲突及原生HTTP接入注意事项见[原生多客户端接入补充](2026-09-10_native-http-followup.md)。此补充不恢复旧队列，且不把监测端成功当作所有任务恢复。

日期：2026-09-10（Asia/Shanghai）

## 结论与状态

本机已移除可调用的源 Skill 和工程镜像 Skill，注销注册并清除活动调用依赖。原生 Photoshop MCP 已通过实际文档操作与重启后自动重连测试。

- Skill 退役状态：REMOVED。
- 原生运行时功能：NATIVE_MCP_SMOKE_PASS。
- 旧 Codex 会话：TRANSPORT_RELOAD_REQUIRED；当前监测对话缓存的旧工具返回 Transport closed。这不是原生测试失败，也不等于旧生产任务已经恢复。
- 工程发布：本记录随退役变更提交；提交编号及远端发布结果以 Git 历史和实际推送回执为准。
- 不把本机的通过复制成其他设备的通过。

用户明确要求删除排队/租约 Skill、保留原生 PS MCP，并将安全删除流程留在工程以供其他设备执行。不是卸载 Photoshop、原生 MCP 或 UXP 插件。

## 已移除与保留

已从可调用位置移除：

- 工作区 .agents/skills/ndc-photoshop-queue。
- 工程 .codex/skills/ndc-photoshop-queue（17 个 Git 跟踪文件；本机完整目录另有缓存文件）。
- production/art_pipeline/skill_sources.json 中相应注册。
- 11 个相关 Skill 的 29 个引用文件中的旧队列调用要求，以及共享 production-record 模板中的旧 broker/watchdog 要求。
- 工作区 AGENTS.md、底层规则中的强制排队、租约、心跳及自动占位回收要求。
- 本机旧队列恢复启动器已移出原启动位置，保留在恢复备份。

保留：

- 每台设备独立安装的 Photoshop Full MCP 运行时和 Photoshop UXP 插件。
- 本机配对数据、队列历史数据库、历史审计、原有导出目录、PSD/PNG 和长期 Skill 备份。
- 图像来源、像素保护、艺术/技术审核、失败依赖与原任务预算规则。
- 原始源目录和工程目录完整快照位于非 Skill 发现目录，可恢复；不是不可恢复的物理销毁。

## 每台设备必须执行的安全顺序

1. **先迁移，再应用删除提交。** 备份本机 Codex MCP 配置、旧 Skill 源/镜像、需要更新的规则和调用方。已拉取而入口失效时，从 Git 历史或自己的备份提取旧文件到非发现目录，只用于审计/迁移；不要重新启动旧队列作为正式通道。
2. 协调本机所有 Photoshop 使用任务停止新请求；核验没有 owner、等待票、人工占用、在途或未知命令。已有文档由原负责者保存可恢复 PSD 和固定审阅 PNG。不能以进程存在、超时或旧空闲截图替代现场状态。
3. 查明本机原生运行时入口、真实 Windows 用户、可访问的 Bridge 数据目录、允许根和导出目录。密钥属于其他用户/旧沙箱且当前身份不可访问时，使用原生配对流程；不修改 ACL、复制他人凭据或伪造身份来绕过认证。
4. 备份后修改本机 photoshop_full_mcp 配置，让 command 指向真实 Node、args 指向原生运行时 dist/src/index.js；删除对旧 Skill 的 mcp-proxy.mjs 依赖。保留有意选择的允许根和导出目录。不要把本机用户名、磁盘、端口或凭据复制到其他电脑。
5. 空闲迁移期可以启动仅用于配对/诊断的原生实例；旧队列不得再提交编辑。完成原生配对，确认旧 Bridge 不再是当前控制者后，核对并停止旧 broker 和代理，不停止 Photoshop。不要启动第二个编辑者。
6. 验证原生 MCP 初始化、工具目录不含 queue 工具、Bridge 已配对且连接、真实宿主和文档状态。只用新建的非交付测试文档验证创建/修改、PSD/PNG 导出、文件实际存在与哈希、重开 PSD 和安全关闭；不得修改生产资产做测试。连接成功不等于抠图、Alpha、生成式填充等所有能力均支持。
7. 原生测试通过后，将本机两个旧 Skill 目录移至非发现的备份目录，再删除活动注册与调用引用。没有安装某一副本则记录不存在，不递归删除其父目录。清理旧启动器，防止后续恢复旧 broker。
8. 修改其他 Skill 时，先备份源与镜像两侧、保留已有较新改动，再验证、同步镜像并备份完整更新包，逐文件 SHA-256 校验。不得用旧源覆盖其他任务的较新工程改动。
9. 重启/重连原生运行时后再次确认自动配对和空文档状态。已运行的 Codex 对话可能仍缓存旧工具；需重载 MCP 连接，必要时重新打开 Codex（不关闭 Photoshop）。只有新会话实际调用成功，才能将该会话标记为已恢复。
10. 将本机结果记录在本机过程目录；工程只保存可移植步骤和无秘密的结果摘要。不要提交 Bridge secret、token、queue.sqlite、客户端 session 或整份机器 config.toml。

## 原生配置映射

配置字段依据本次检查的 Photoshop Full MCP 2.0.1-ndc2；其他版本需核对自身实现。

| 项目 | 每台设备的值 |
| --- | --- |
| MCP command | 本机 Node 可执行文件 |
| MCP args | 原生运行时 dist/src/index.js，不能引用已删 Skill |
| PS_MCP_DATA_DIR | 当前运行身份可访问的本机 Bridge 数据目录 |
| PS_MCP_EXPORT_DIR | 保留本机已采用、可写且受控的导出位置 |
| PS_MCP_ALLOWED_ROOTS | 本机实际允许的资产根；不改变只读源授权 |
| PS_MCP_PORT_START / END | 本机可用端口，属于机器配置，不复制维护机值 |

本机沿用了既有 exports 子目录。虽然其父目录历史名称带 queue-state，它仍被原生导出配置引用，**不得连同整个状态目录作为缓存删除**。

原生 stdio 服务通常按客户端启动；删除租约后没有自动多任务调度。**同一时刻只让一个任务连接并操作本机 Photoshop；交接时先保存并释放该连接，再让另一任务连接。** 不保证多个常驻 stdio 客户端自然共享一个 Bridge，也不以“不同文档”允许并发写入。不要在新名字下重建队列来冒充删除完成。

## 本机验证摘要

- 14:08：旧队列 IDLE，无 owner/waiting/external/handler；Bridge 命令数为 0。两个生产任务已收到停止新增 PS 请求的迁移通知，消息发送工具返回了成功回执。
- 14:11：源与工程旧队列各 18/18 个文件完成 SHA-256 备份核验；Codex MCP args 已切换原生入口。
- 14:16：用户在 Photoshop 面板完成原生 Bridge 配对；服务器身份与本机原生运行时一致。
- 14:17：原生读取 Photoshop 27.11.0 状态，paired=true、connected=true、documentCount=0。
- 14:18：核对后停止旧 broker 和 3 个旧代理；未停止 Photoshop。原生创建 64×64 的独立测试文档，并创建第二个像素图层。
- 14:18–14:20：实际导出 PSD/PNG、核验 SHA-256、关闭测试文档、从允许路径重开 PSD（仍为 64×64、2 层）、安全关闭并确认 documentCount=0。
- 源/工程两个可调用旧 Skill 目录已移出；活动 Skill 中旧 Skill 名、queue CLI、proxy 与 queue 工具引用扫描无命中。
- 11 个更新 Skill 通过 quick_validate；源、工程镜像和完整更新后备份共 220 个文件逐一 SHA-256 匹配。
- 14:27：退出临时验证会话，再从原生入口启动；无需再次输入配对码，Bridge 自动连接成功，状态仍为零文档，工具数为 21、queue 工具数为 0。
- TOML 解析、原生入口存在性、配置无旧 Skill 路径及 Git diff --check 均通过。
- 旧监测会话缓存工具调用仍返回 Transport closed；不将其或 Unit2/Unit4 生产状态记为已重连。

测试导出哈希：

- PSD：387df7eba39aca0baf04cc9c4270fa383e236ea9c6ba9efae3fb20044fbd08f7
- PNG：1320f5ff73b84ff177b1bdf8fdf3f0c18dc19b25f6c5086c6884464f989cdfd6

## 原生配对窗口的本机兼容修正

迁移中复现了“配对接口返回 displayed=true，实际没有窗口”的独立问题。Windows PowerShell 子进程以 -Command - 接收 stdin，但未指定 -NonInteractive，触发 PSReadLine 初始化失败并以 0 退出，传入的显示脚本未执行。使用无秘密的 Write-Output 夹具验证：原参数输出为空；增加 -NonInteractive 后正确输出。

本机仅对原生 dist/src/bridge.js 的 showPairingDialog 做窄修正：

- 启动参数增加 -NonInteractive（不禁用 WPF 对话框，只禁用命令行交互组件）。
- 脚本加 ErrorActionPreference=Stop，stdin 末尾补换行。
- 保留 trusted local dialog、短时端口绑定配对码和用户面板确认；配对码不返回 MCP 客户端，也不写入记录。
- 修改前文件单独备份；实际验证窗口进程存在且用户完成配对。未放宽认证、命令能力或允许根。

其他设备不必无条件打补丁。仅在同版本、同症状且最小夹具复现时对自身运行时修正；运行时是每机外部安装，不随此次 Skill 删除提交分发。

## 提交与回滚注意事项

本次工程提交包含队列文件删除、11 个调用方 Skill 修订、注册删除和本记录。旧版 ZIP 归档受仓库忽略规则管理，保留在本机，不强制加入 Git；跨设备可从 Git 历史取回已跟踪的旧版本。现有其他任务未提交变更不属于本次，应分开选择，不能整仓库盲目提交。工作区 AGENTS/底层规则不在工程提交内；其他设备按本记录同步自己的规则。

回滚须协调所有 PS 使用者停止操作，再从本机备份恢复配置与同一版本的源/镜像；重新验证运行时、配对与入口。不要恢复旧 broker 却保留新原生连接并行运行。跨用户旧配对和已变更运行时哈希需要分别验证，备份存在并不保证旧队列可直接启动。
