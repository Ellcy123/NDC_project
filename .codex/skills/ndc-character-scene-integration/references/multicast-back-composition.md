# 三人及以上同场背影构图门禁

同一剧情快照内同时出现三名或更多角色时，默认必须指定至少一名当前真实 cast 中的支持性角色，位于相对靠近镜头的 `foreground` 或 `near-midground`，以背对镜头的可见上半身／背部参与构图。不能把所有角色都安排成正面或侧面对镜头，也不能临时增加无需求角色凑门禁。

承担背影构图的角色必须是非 active 状态。若 active 角色需要按点击后视线规则回应镜头，应改由同场非 active 支持角色承担背影；当前快照没有可用非 active 角色时，不得让 active 角色违背视线规则，只能取得用户对该具体 `scene_id + snapshot_id` 的明确构图改写后使用例外。

## 三阶段执行

1. `whitebox`：参考任务锁定 `actor_id`、深度层级、`facing: back`、可见背部区域和真实 UI 侧；在联合白模与真实 UI 叠加图中实际检查背部可读、前后层次成立且不遮挡 UI。
2. `formal`：生产任务保持同一指定角色、深度和背向关系；完整角色先生成，再按真实遮挡制作派生层。不能因模型更容易画正脸而把背影改成正面／侧面。
3. `final-composite`：全场验收再次检查背部可见性、前后层次、真实 UI、主体关系和遮挡。技术门禁通过不代替整场艺术判断。

每阶段建立 `ndc-multicast-back-composition/v1` 合同并运行：

```text
python scripts/validate_multicast_back_composition.py --contract <contract.json> --output <gate.json>
```

合同至少包含：`scene_id`、`snapshot_id`、`stage`、当前整场 `artifact`、当前真实 UI 检查 `ui_report`，以及完整 `actors`。每个 actor 记录 `actor_id`、`active`、`depth_band`、`facing`；承担背影的 actor 还必须记录正面积的 `visible_back_region_bbox`。三人以下返回适用性 false 的 PASS，不能把它当三人门禁证据。

三人及以上时，验证器会继续打开 `ui_report.contract` 并复核当前字节与 `contractSha256`。multicast `actors[].actor_id`、UI contract `actors[].actorId`、UI report `actors[].actorId` 三个集合必须完全一致且各自无重复；任何漏掉的实际在场角色、额外角色、重复角色、旧合同或旧报告都直接失败。只写 `status: pass` 的摘要不是 UI 证据。用户构图例外只影响背影候选要求，不豁免全员 UI 覆盖。

用户例外只对准确的 `scene_id + snapshot_id` 生效，必须保存 `exception: {source_kind: user_instruction, scene_id, snapshot_id, instruction}`；旧案例、作者偏好、生成困难或浏览器故障都不是例外。阶段文件或角色状态变化后重新运行，旧哈希门禁失效。
