# 发布、领取与结果回收

脚本不直接调用模型、浏览器或Codex应用。活动协调任务按本协议驱动原生产Skill；应用实际派发按[任务派发](task-dispatch.md)进行。

## 固定范围与原历史

每个已授权批次使用独立过程目录；数据库固定为该目录的 `pipeline.sqlite`。`init` 只创建一次，拒绝覆盖；续作直接使用原库。`project_root`为当前工程工作区根，本机为 `D:/Codex/NDC`；`work_root`必须位于其 `工作过程文件` 内。上游和下游使用同一共享数据库绝对路径；Git worktree不会复制外部过程资产。

计划最小结构：

```json
{
  "schema": "ndc-art-stage-pipeline/v1",
  "pipeline_id": "本批次稳定编号",
  "pipeline_kind": "ui_portrait",
  "execution_mode": "production",
  "project_root": "D:/Codex/NDC",
  "work_root": "D:/Codex/NDC/工作过程文件/本批次流水",
  "controller_task_id": "真实协调任务ID",
  "units": [
    {
      "unit_id": "CHARACTER_A",
      "producer_task_id": "真实母生产任务ID",
      "authority": {
        "journal": "D:/Codex/NDC/工作过程文件/本批次/production-journal.jsonl",
        "upstream_jobs": ["A-U0", "A-U1"],
        "downstream_jobs": ["A-big", "A-small"]
      }
    }
  ]
}
```

把示例替换为完整实际范围。`unit_id`使用稳定ASCII身份或场景编号，允许字母、数字、点、下划线和连字符。场景kind为 `scene_mj`，其上游是经核对的提示合同而非图片审核，`upstream_jobs`可空；下游job覆盖全部必需视角。两种kind分别建流水，不能把不同流程塞进同一工作者而重新判断职责。

执行模式固定：`production`用于已有实际生产授权；`validation`只做合成夹具、合同接收与技术机制测试，不提交艺术生成，不产生生产PASS。切换模式不能重开同一库洗掉历史。

```powershell
$pipelinePython = 'C:\Users\EDY\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$pipelineCli = 'D:\Codex\NDC\.agents\skills\ndc-art-stage-pipeline\scripts\pipeline.py'
& $pipelinePython -X utf8 -B $pipelineCli --db $pipelineDb init --plan $pipelinePlan
```

后续所有调用保留同一个 `--db`。JSON和真实输出都放过程目录；不向正式交付目录写临时包或夹具。

## 就绪发布

包使用 `ndc-art-stage-packet/v1`，包含 `pipeline_kind`、`unit_id`、正整数 `revision`、`producer_task_id`、`authority`、`files`及相应adapter的 `payload`。每个文件引用为 `{role,path,sha256}`，路径绝对、角色唯一，哈希对应实际文件。

参考 [UI专属字段](ui-pipeline.md) 或 [场景专属字段](scene-pipeline.md)，不能凭通用字段猜测批准、母图或提示。`authority`须与完整计划中的原journal/job一致。专门adapter核对相关accepted上下文、当前源与必需结果；源变更或人工前置缺失不产生READY。

```powershell
& $pipelinePython -X utf8 -B $pipelineCli --db $pipelineDb publish --task $producerTaskId --packet $packetPath
```

该调用先验证专门条件，再把不可变JSON写入 `handoffs` 并原子发布，返回包路径、哈希及READY。重复相同版本只返回已发布；同版本不同内容拒绝。实质修改必须用下一连续版本。脚本自动分配每单位／版本的独占输出目录，不能修改其他任务源文件。

只把当前被引用文件纳入包；原journal持续追加，引用其绝对位置与相关job接受绑定，不能把全journal摘要当本单位版本。上游B追加记录不应使A失效；A源像素、身份、共享空间或真正前置变化才使其后继失效。

原journal正在短暂追加或读取过程中变化时，CLI返回可重试 `BUSY`（退出码3），不持久标记STALE；待写入结束后重做本次读取。不得删除写锁或改建日志。只有稳定读取后仍不满足来源和审核条件才撤销就绪。

## 协调与下游执行

每次READY后协调者立即 `reserve-dispatch --task <controller>`，随后按派发文档执行，不等所有单位READY。一个流水只有一个下游；派发保留、提交中、回执未知、setup未完成或已领取时，重复reserve不会再创建任务。

```powershell
& $pipelinePython -X utf8 -B $pipelineCli --db $pipelineDb claim --task $workerTaskId --dispatch $dispatchId
& $pipelinePython -X utf8 -B $pipelineCli --db $pipelineDb guard --task $workerTaskId
```

任务ID使用实际下游ID；包中的 `producer_task_id`保持原生产历史归属，不改成新任务ID。CLI为本worker保存租约上下文，不打印token；不得借用其他任务上下文。guard成功只说明交接版本仍有效，不能替代原Skill各阶段的来源、权限和视觉检查。

按原Skill调用UI裁切或MJ操作。实际生成前先在原生产journal的相同job登记attempt，再提交一次；未知结果继续查原工具/任务，不新建job重试。长步骤之间更新 `heartbeat`，其作用是诊断，不授予超时抢占。人工等待不得占PS，PS操作仅走已有共用入口。

## 回收与连续消费

结果JSON包含 `unit_id`、`revision`、`status`、实际 `files` 和adapter的 `payload`。所有新增结果放领取时分配的目录；只读的历史保留版继续在packet引用，不伪称下游新输出。

```powershell
& $pipelinePython -X utf8 -B $pipelineCli --db $pipelineDb result --task $workerTaskId --result $resultPath
& $pipelinePython -X utf8 -B $pipelineCli --db $pipelineDb claim-next --task $workerTaskId
```

- `PASS`：仅production模式，实际专门校验和原下游job当前审核均有效。不是用户最终批准。
- `FAIL`：记录实际缺陷、原次数和返修责任；依原预算修复或封存，独立单位仍可继续。
- `WAITING_MANUAL`：记录原流程明确的人工节点和可交接材料，暂停此单位；工作者可接其他READY单位。
- `VALIDATION_COMPLETE`：仅validation模式，记录实际验证动作，不计生产PASS。
- `STALE`：来源或版本已变；保留旧结果及原因，不提升为当前交付。

pending/unknown的真实提交须先在原journal核实，不允许用结果回收或换任务绕过。下游完成当前单位后自动尝试claim-next；已有READY即在当前任务继续。返回WAITING_UPSTREAM时结束当前轮，让协调者以后通过send唤醒；不后台永久轮询。

`status`保留全清单、每单位状态、派发与占用，仅当全范围达到对应完成状态才报告整批完成。生产范围不能用验证结果补齐。上游只在最终汇总时统一整理交付清单，过程交接不再重扫整章。

完成数量会重新核对当前来源、原审核、实际结果文件与固定回执哈希；历史PASS不永久有效。后来修改的回执或输出会退出当前完成统计，短暂日志写入则显示BUSY并保留原存储状态。

## 人工返回、输入修订与失联

人工返回先走原Skill接收来源与审核，再追加新packet版本，或在原包仍完全有效时 `resume --task <controller> --unit <id> --evidence <真实返回说明.json>`。说明需含unit_id及实际reason；缺授权或来源未通过仍拒绝，不把说明本身当艺术批准。

包新版本不会杀掉旧任务或抹去未知操作。旧worker在下一guard或result时停止发布，记录STALE并保留实际文件；单一租约解除后才可领取当前版本。已在执行的外部命令不能靠修改数据库撤回。

失联只触发核实：用实际任务状态、原生成job和PS队列状态检查是否仍有操作。只有确认原worker没有活动回合、外部操作已核实，才 `recover-worker --task <controller> --evidence <核实.json>`。证据包含worker_task_id、no_active_turn:true、external_operations_settled:true和具体observation。原journal存在pending/unknown仍拒绝恢复。恢复隔离旧租约并暂停该分支供保存结果复核，其他独立READY可继续，不重放、不重置次数。

应用创建/消息投递的未知结果按任务派发文档单独处理；不要用worker恢复去清除创建回执不明。长期后台触发不在此Skill内，当前主任务结束后若要继续定时派发，应使用用户另行指定的调度方式。

已BOUND但尚未claim的旧交接也不能直接抹去。确认目标任务无活动回合、未领取且外部操作已核实后，可用 `cancel-dispatch` 交回入口；证据含dispatch_id、target_task_id、no_active_turn:true、confirmed_not_claimed:true、external_operations_settled:true及observation。此证据说明交接已停止，不谎称任务从未创建。已经领取则使用上述结果回收或失联恢复。
