# 活动控制任务的跨任务派发

`scripts/dispatch_plan.py` 只生成工具参数和核心命令，不发送消息、不创建任务、不操作应用私有接口，也不替代 SQLite 核心。任务工具必须由当前活动的 Codex 控制任务调用。任务结束后本适配器不会常驻或定时触发。

每个 pipeline 复用一个下游任务，默认总并发为上游 1 + 下游 1。同一场景的完整 views 由该任务统筹，不按 view 创建任务。发布是单元边界：一个已通过的单元 READY 后即可推进下游；控制任务无需等待全部上游完成，再继续处理后面的独立单元。

## 当前工具能力依据

本机已提供的工具契约包含 `mcp__codex_app__create_thread`、`send_message_to_thread`、`read_thread`、`wait_threads`、`list_threads`、`list_projects`。具体参数以当前工具声明为准，不调用未经公开提供的内部 app/API。

- `create_thread` 仅在已有明确新任务授权时调用。先用 `list_projects` 取得真实 `projectId` 和 `isGitRepository`；Git 项目默认 worktree，非 Git 项目使用 local。只有用户明确要求直接使用保存项目时才覆盖为 local。
- 创建非阻塞：实际返回 `threadId` 才能绑定；只有 `clientThreadId` 时是 `SETUP_PENDING`，不得把它填入 send/read/wait 的 `threadId`。
- 复用任务使用 `send_message_to_thread`；保留原模型设置，不自行填入 model/thinking。
- 已知真实任务的简短检查用 `wait_threads` 的 `timeoutMs: 0`，后续传原工具返回的 cursor。需要具体回执时再 `read_thread`；不反复轮询相同状态。

官方说明确认 worktree 用于隔离同一 Git 项目的并行文件工作；它不替本协议证明外部应用操作或美术生产速度。[OpenAI：Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)

## 输入与参数生成

先由核心执行 `pipeline.py --db <绝对数据库路径> reserve-dispatch --task <真实控制任务ID>`。只接受首次原子预登记返回的 `RESERVED`；已有未解决派发应由核心返回阻塞，不能另开同一 worker。

保留完整 reservation JSON，不自行拼接 dispatch_id。其字段为：

`dispatch_id`、`pipeline_id`、`action(create|send)`、`status`、`target_thread_id`、`packet_path`、`packet_sha256`、`unit_id`、`revision`、`execution_mode(validation|production)`、`database_path`、`downstream_skill`、`work_directory`。

另提供当前控制任务的上下文 JSON：

```json
{
  "controller_task_id": "使用当前真实task ID",
  "project": {"projectId": "使用list_projects实际返回值", "isGitRepository": false},
  "explicit_new_task_authorized": false,
  "existing_task_dispatch_authorized": false,
  "art_execution_authorized": false,
  "authorization_note": "引用用户已有的本次授权，不把维护Skill当作新艺术生产许可"
}
```

`project` 是从当前 `list_projects` 结果整理的最小字段，不是示例 ID。send 分支复用核心已绑定的 `target_thread_id`，无需再次选项目。已有用户授权持续有效，记录已有依据即可，不要求重复确认。使用保存项目的显式覆盖另填 `use_saved_project_directly:true` 与 `saved_project_request_note`。需要远程已绑定目标时从真实回执填 `target_host_id`，不能猜测。

运行：

```text
python dispatch_plan.py --reservation <reservation.json绝对路径> --project-context <context.json绝对路径> --out <plan.json绝对路径>
```

输出包括符合本机工具声明的 `proposed_tool_call`、真实调用前原子命令、完整回执保存位置、绑定和未知结果登记命令，以及允许的效果范围。`argv` 是原始参数；同时提供正确单引号转义的 PowerShell 表达式。不得使用未经 shell 转义的 JSON 字符串拼接执行命令。

没有任务授权时只保留参数预览，`tool_call` 为空。production 还要求当前批次美术生产授权。validation 始终禁止真实 MJ/ImageGen/Photoshop 出图，仅可读协议记录和处理明确的合成夹具；UI production 限于已审母图裁切，不增加生图或自动补肩权限。

## 一次发送的实际顺序

1. 每次 publish 后尝试 reserve；拿到 `RESERVED` 即生成计划。下游已存在则 action 为 send，继续同一任务，不按场景/view 增开 worker。
2. 当前控制任务先执行计划的 `before_tool_call`：`dispatch-sent --task ... --dispatch ...`。核心只能原子执行一次 `RESERVED → SUBMITTING`。没有这一步成功回执就不能调用应用工具。
3. 仅在前一步成功后，调用 `tool_call.name`，原样使用其 `arguments` 一次。重复打印同一计划不产生第二次发送权；适配器本身不证明外部恰好执行一次。
4. 将完整真实应用回执保存到计划的 `app_response_path`，再执行 `after_actual_response` 对应的 `bind-dispatch --response ...`。不得先手填或把 clientThreadId 改名为 threadId。
5. 工具报错、没有回执或结果未知时执行 `on_unknown_result`。`SUBMITTING/UNKNOWN/SETUP_PENDING` 不因时间流逝重新发送，也不释放新任务名额。计划对这些状态只输出核实步骤。
6. 创建有真实 threadId 且完成绑定后检查其进展。worker 可能先于 bind 启动；若它已停在 `WAITING_FOR_DISPATCH_BINDING`，控制任务确认 bind 后只向同一真实任务补充续作消息，不再创建任务，也不另记一份资产领取。

未知创建可先 `list_threads`，再根据真实派发标记和任务内容检查候选；相似标题不是创建成功证明。找到真实任务后把实际回执交核心绑定；确实未创建时，必须由控制任务保存可核实外部状态和人工说明再走核心取消流程，禁止按超时推断。未知 send 优先读已绑定的真实目标与该 dispatch 的领取记录，禁止盲目重发。

## worker 与回传

worker 使用自己的真实 task/thread ID 调用 `claim --task ... --dispatch ...`。控制任务 ID、dispatch_id、clientThreadId、子代理名字或随机测试 ID 都不能冒充实际应用任务身份。缺少真实 ID 就回报 `NEED_REAL_TASK_ID`；未绑定就停在领取前。核心负责唯一领取、租约、不可变包哈希、revision 与输入依赖的有效性；worker 在实际生产前 guard，之后通过核心 result 回传。

每次 result 回传后，已绑定 worker 立即调用 `claim-next --task <自己的真实任务ID>`。核心只允许本 pipeline 唯一登记的 worker 在没有活跃领取/派发时原子领取下一 READY 包，返回 `CLAIMED` 并记录 `local_continuation` 事件，不伪造 create/send 回执。有包就按原权限与门禁继续，避免等待上游再次腾出模型回合；没有包则返回 `WAITING_UPSTREAM`，worker 结束本轮，控制任务以后 publish 后再 reserve/send 唤醒同一任务。不要用长时间后台轮询代替这个空队列出口。

共同数据库保留在原绝对路径。Git worktree 可能改变默认目录，worker 必须先确认共享数据库和 package/work_directory 可访问；不得拷贝数据库或重建 pipeline 来绕开领取。输出写入包指定的独占目录。相同单元的全部 views 保持同 worker；更新只影响相关依赖和规格，不重画已通过兄弟项。

人工节点必须回传具体需要人工完成的内容、来源、当前版本和续作位置，保存后暂停该依赖链。人工肩膀补全与人工 Alpha 是两个独立回执，不相互替代。返还后从接收、来源和哈希核验继续，不能伪造人工处理过程。技术合格、任务结束和艺术 PASS 是不同事实。

## 验证能证明什么

| 验证 | 能证明 | 不能证明 |
|---|---|---|
| `tests/test_dispatch_plan.py` 参数与响应状态夹具 | create/send 参数、原子发送前置命令、未知状态不生成第二次发送、clientThreadId 不当作真实目标、授权与效果范围；worker 的 claim-next 续作要求 | 没有实际创建、发送或运行用户任务 |
| 两个真实子代理并发访问隔离 SQLite 与不可变夹具 | 唯一领取、版本失效、回传与并发记录的协议行为；身份应明确标为测试代理 | 不能冒充两个真实 Codex 用户任务的 task ID，也不能证明 app 派发成功 |
| UI 合成夹具的实际裁切 | 本机规格导出和文件证据链 | 不构成真实角色身份或艺术批准 |
| 经用户明确授权的实际 app 派发并绑定回执 | 本机真实任务创建/续作及绑定链 | 不自动证明 MJ 更快或全批生产提速 |

本轮 Skill 维护默认只做前三类验证。没有进行真实 MJ 批次时，报告“协议与夹具验证通过；真实 MJ 性能未测”，不把预期重叠收益写成实测速度。
