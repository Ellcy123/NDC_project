# UI 母图到双规格裁切的交接

只在批次已启用 [公共流水线](../SKILL.md) 时读取本页。边界为单角色已接收的 U0 来源与 U1 母图 → 同一来源的 U2 裁切、U3 真实审核。上游可继续其他独立角色；未接收人工补肩、待审母图及失效来源仍阻断本角色。多任务不增加生图授权、预算或 Photoshop 权限，实际 PS 操作仍走 [共用队列](../../ndc-photoshop-queue/SKILL.md)。

## 发布前

先完成 [UI Skill](../../ndc-generate-ui-portraits/SKILL.md) 的历史资产检索与复用。两版均已存在者直接复用，不创建裁切交接；只缺一版只发布该版。通用肖像允许截肩，若本次 UI 来源确实缺肩胸结构，必须由人工接手，原 U0 进入等待；收到合格人工源并真实复查接收后才能发布。不自动补肩，不因下游空闲绕过人工交接。

使用原 `production-journal.jsonl` 的实际 job，遵循 [生产记录](../../ndc-generate-ui-portraits/references/production-record.md)。U0 的 `requirements.purpose` 为 `ui-source`，U1 为 `ui-master`，规格 job 为 `ui-big` / `ui-small`；每项 `requirements.identity_id` 是同一角色正式 ID。U1 必须依赖 U0，待裁切规格必须依赖本 U1。原 journal 的 `task_id` 保持母生产任务 ID；下游任务 ID 只用于流水线领取，不能改写资产历史。

旧记录不足以证明来源时，在原流程补当前可核对的依据和适用审核，保留历史、累计尝试与限额；不得另起 journal、伪造历史批准或为了满足字段重画已批准字节。缺少有效来源或当前接收时发布会阻断。

## Packet 契约

公共 `schema`、`pipeline_kind=ui_portrait`、`unit_id`、正整数 `revision`、`producer_task_id`、`execution_mode`、`files`、`authority` 由公共流水线核验。`execution_mode` 来自计划，不由下游改变。所有引用必须是实际文件路径和当前 SHA-256。`authority.journal` 是原 journal 绝对路径；其 `upstream_jobs` 含 U0、U1 及所有保留规格；`downstream_jobs` 含本次实际规格 job。

UI 专属 `payload` 示例（标识和 hash 均需替换为真实值）：

```json
{
  "character_id": "正式角色ID",
  "stem": "正式文件stem",
  "mode": "missing_profiles",
  "u0_job_id": "角色-U0",
  "master_job_id": "角色-U1",
  "master_role": "ui_master",
  "source_roles": {
    "card": "approved_card",
    "portrait": "approved_portrait",
    "approval": "source_approval"
  },
  "manual_completion": "received",
  "requested_profiles": ["small"],
  "profile_jobs": {"small": "角色-small"},
  "preserved_profiles": {
    "big": {"file_role": "preserved_big", "job_id": "原big实际job"}
  },
  "acceptance_bindings": {
    "角色-U0": "实际绑定摘要",
    "角色-U1": "实际绑定摘要",
    "原big实际job": "实际绑定摘要"
  }
}
```

新制双版使用 `mode=new_pair`、`requested_profiles=["big","small"]`、对应两个 `profile_jobs`，`preserved_profiles={}`。两集合互斥且合计覆盖 big/small。保留规格直接绑定原已接收 job，不要求新建 reuse job；不得重做、重命名覆盖原文件或改动旧 receipt。新裁切两版均须直接来自同一 U1；历史版未知的母图关系如实保留未知，不伪造“同母图”历史。

`files` 至少声明母图、批准角色卡、合格通用肖像、来源批准证据，及本次保留的历史规格。U1 `current_acceptance` 的 `ui_master` 输出必须与所交母图路径及 hash 完全一致，母图须 3:4、RGB 或完全不透明 RGBA。角色卡和肖像必须是 U1 实际输入，来源三项必须属于已接收 U0 的输入或输出。跨任务不以同名文件或最近修改时间替代这些关联。

来源批准证据为 `source_roles.approval` 所指 JSON，内容来自实际批准与人工交接依据，并且绑定 U0 当前审核：

```json
{
  "schema": "ndc-ui-source-approval/v1",
  "character_id": "正式角色ID",
  "approved": true,
  "approval_basis": "实际批准来源及身份核对依据",
  "card_sha256": "角色卡实际hash",
  "portrait_sha256": "本次合格肖像实际hash",
  "manual_completion": {
    "required": true,
    "status": "received",
    "confirmation": "人工完成返还的实际指令或回执位置",
    "original_portrait": {
      "path": "原截肩肖像绝对路径",
      "sha256": "原文件实际hash"
    }
  }
}
```

无需人工补全时 `required=false`、`status=not_required`，packet 同样填 `manual_completion=not_required`。需要人工补全时 U0 必须记录 `source_decision.mode=manual_input`，原截肩肖像也须绑定 U0 来源。此 JSON 是证据索引，不因填写 `approved=true` 或计算 hash 就产生艺术批准；真实来源及视觉审核仍由原流程核验。

对所有声明的 `upstream_jobs` 调用 `scripts/ui_adapter.py` 的 `accepted_binding(journal_path, job_id)` 填写 `acceptance_bindings`。摘要只绑定该 job 的当前接收 context 和输出，不散列整个会追加的 journal；其他独立角色进展不会让本单失效。领取和回收再次检查每个相关 job 的当前有效接收。父图被拒收、来源或相关需求变更、依赖字节变化时，旧交接失效；保留旧候选，按公共流程发布新 revision，预算不重置。

## 下游执行与回收

先按公共入口领取、核对 lease 与 packet，工作前执行 `guard`。实际命令和派发恢复以公共入口为准，不能跳过领取直接写他人的候选目录。母图引用原绝对路径；新标注、回执、审核图和候选全部放进领取分配的 `work_directory`，`compose` 用其尚不存在的子目录。原始来源和旧回执不写入下游目录冒充新结果。

在 UI Skill 根按实际来源执行：

```text
python -B scripts/ui_portrait.py compose --input <原U1母图> --landmarks <独占目录/landmarks.json> --stem <正式stem> --profile small --output-dir <独占目录/crop-small-新目录>
python -B scripts/ui_portrait.py audit --receipt <独占目录/crop-small-新目录/composition.json>
```

本次为双版时省略 `--profile`，两版直接同母图裁切。单版修订只用对应参数，保持另一版字节和有效审核；失败不得把预算重设为初始值。调用 Photoshop 前另外领取 PS 队列，离线裁切和视觉审核本身不占 PS。

技术 `audit` 会重读母图、标注并重建实际裁切，仍只产出 `TECHNICAL_PASS` / `NOT_CHECKED`。按原 UI U3 做真实整图、局部、原尺寸可读性和配对审核，使用原 journal 的下游实际 job 生成 request、绑定记录并取得当前有效接收。不能只回传“已看过”或将技术成功改写为视觉 PASS。

成功结果的公共 `unit_id` / `revision` 必须匹配领取版本；`files` 声明实际 composition receipt、其使用的标注 JSON、及本次输出 PNG 的 role/path/hash。例：

```json
{
  "status": "PASS",
  "files": ["此处替换为实际引用对象，不是字符串"],
  "payload": {
    "receipts": ["composition"],
    "profile_roles": {"small": "ui_small"}
  }
}
```

每份 receipt 的母图必须匹配同一冻结 U1，标注须在 packet 或 result 声明且 hash 有效；receipt 所含规格并集恰好为 requested_profiles，不允许顺手重做保留版。适配器调用现有 `ui_portrait.audit`，核对实际 PNG、正式 stem、原 journal 下游 `current_acceptance`，公共核心再核对独占目录和实际操作无 pending/unknown，才回收生产 PASS。最终完整 big/small 清单和用户验收口径仍按原 UI Skill。

真实失败或人工等待回传 `status=FAIL|WAITING_MANUAL`，`payload.reason` 写实际问题，`payload.return_stage` 指 U0/U1/U2/U3，并保留实际过程文件。无需捏造 PASS 才释放下游任务；只阻断本单依赖，其他独立角色可继续。旧来源已失效时由核心隔离为 STALE。恢复先核对实际任务与工具状态、候选及原累计次数，再接续原阶段，不能因超时自动重试或新起预算。

## 仅验证模式

维护测试不会生成真实角色、调用生图或 PS。隔离的 `tests/ui_fixtures.py` 提供 `create_fixture(new_workroot, unit_id, producer_task_id, missing_profiles=..., manual_required=...)`，返回 packet、base、原合成 journal、landmarks；所有来源、记录及 review 明标 synthetic，生产发布会拒绝它们。生产 `ui_adapter.py` 不提供初始化或制造合成接收的工具。

测试下游可调用 `complete_fixture(claimed_packet, base)`：在领取的独占目录内实际执行现有 compose/audit，结果为 `VALIDATION_COMPLETE` 且 `payload.validation_only=true`，不写下游艺术接收、不改原 journal。核心只能在计划 execution_mode=validation 接收此状态，不能计作正式 PASS。合成像素裁切证明协议与技术门禁可运行，不证明真实角色视觉质量或用户批准。
