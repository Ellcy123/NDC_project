# 已确认历史次数的来源更新

用于`legacy_resolution`已经追加、其引用的来源文件后来更新而触发`history source bytes changed`的批次。原`resolve-history`仍只确认一次历史次数。本命令只登记来源的新版本，不能更改历史次数或`new`／`known_historical`判断，不能恢复被拒绝或失效的图像审核。

## 实际复核与证据

先查旧历史证据、当前所有来源和本批追加的真实attempt。分别确认“接入前次数”和“本批真实次数”；不能把已有attempt重新计为历史次数，也不能由文件缺失推断零次。来源更新若证明原次数错误或无法核实，保持阻塞并记录矛盾，不使用本命令。需求事实变更另按批次失效传播复核受影响资产。

准备一份`ndc-prop-history-source-revalidation/v1` JSON，包含：

- `batch_id`、`reviewer`、`reason`；
- 非空`reviews`数组，每项含`job_id`、原`legacy_resolution`事件的`resolution_hash`、`previous_evidence_sha256`、原值不变的`confirmed_count`和`determination`、实际复核结论`reason`；
- 每项`sources`完整保留该job原有来源路径。每个来源含`path`、`previous_sha256`和当前`sha256`。路径不可删减、替换或重复；未变来源也保留，至少一个来源哈希实际变化。

第一次复核的`previous_evidence_sha256`取原`legacy_resolution.evidence_sha256`；后续复核取最近一次覆盖该job的`history_source_revalidation.evidence_sha256`。`previous_sha256`相应取该job最近一次有效来源哈希。即使一次事件覆盖多个job，各job仍沿自己的前任证据链续接。

同一文件被多个历史确认引用时，将所有受影响job放入同一`reviews`。命令执行前会验证完整日志和全部当前有效来源；未覆盖的来源漂移仍阻止追加，不临时开放生图。脚本校验只证明记录、路径与字节一致，历史结论须来自执行者实际查阅。

## 追加与继续

```powershell
python scripts/workflow_state.py revalidate-history-source --batch <batch.json> --evidence <source-review.json>
python scripts/workflow_state.py validate --batch <batch.json> --stage 2
python scripts/workflow_state.py progress --batch <batch.json>
```

用Skill绝对脚本路径执行。命令在同一批次锁下保存不可覆盖的`history_source_revalidations`快照并追加哈希串联事件；只更新批次`attempt_head`。返回`counts_preserved`，应与修复前按原历史确认和真实attempt累计的值逐job一致。原scope、jobs、日志字节前缀、旧证据和提示快照必须保留。

旧快照本身被篡改、日志断链、头不一致、来源丢失、次数矛盾等不会被本命令放行。中断留下的快照也不自动覆盖或删除。恢复后再按当前场景前置、父图和真实审核执行后续生产，不把来源复核当成资产PASS。
