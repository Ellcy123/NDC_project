# 角色入景白模节点交付合同

角色人工节点不是 JSON 审批表，而是用户可以直接打开、比较和继续修改的真实文件包。每个场景 revision 在正式人物网页生图前，先从 `assets/character-node-delivery-pack.template.json` 建立完整 pack spec，再运行：

    python scripts/node_delivery.py pack --pack-spec <character-node-delivery-pack.json> --delivery-root <resolved-{DELIVERY_ROOT}/角色融入场景>
    python scripts/node_delivery.py verify --manifest <节点交付清单.json> --delivery-root <resolved-{DELIVERY_ROOT}/角色融入场景>
    python scripts/node_delivery.py audit-batch --batch-spec <character-node-delivery-batch-audit.json> --delivery-root <resolved-{DELIVERY_ROOT}/角色融入场景> --output-dir <resolved-{WORK_ROOT}/节点交付统计>

必须先通过 `ndc_art.py paths` 解析根；命令中的占位符不是实际路径。包的固定位置为：

```text
{DELIVERY_ROOT}/角色融入场景/Unit<n>/节点交付/<scene-id>/
```

目录代号用于机器绑定，但所有 scope、pack、manifest、人工节点及批次清单还必须携带相同的 `scene_label = {display_name, location, time}`。`display_name` 要把地点与时间写成用户可理解的场景概括，例如“圣心医院病房（白天）”，不能只重复 `SC2206`。HTML、Markdown 和批次统计均优先显示该名称，同时保留代号。

## 根层是真实资产

场景根层只平铺当前节点实际资产，不建立 actor、pose、type 或 revision 子目录：

- 每个 actor/pose 的透明、完整 3D 解剖人体母层：`SC<scene>_<actor>_<pose>_whitebox-master.png`；
- 同一 actor/pose 真正会原样上传为网页版 ChatGPT Image 1 的局部场景白模：`SC<scene>_<actor>_<pose>_image1-whitebox.png`；
- 本场全员联合站位预览：`SC<scene>_scene_<revision>_joint-whitebox.png`；
- 使用真实 UI 的避让预览：`SC<scene>_scene_<revision>_ui-whitebox.png`；
- 已存在的可恢复源文件：`SC<scene>_[subject_]_<revision>_source.psd|psb`。

完整人体母层与 Image 1 必须逐 actor/pose 成对齐全，并覆盖冻结 scope 的全部 actor/pose；只收一场中的部分角色、只收一个场景而遗漏批次清单中的其它场景、只收联合预览或只收 JSON 都失败。跨场景批次逐场生成上述目录和 manifest，再用批次索引链接每场；不得把八个场景混入一个无场景层级的日期目录。历史可用白模可以复制精确字节进入对应场景，但其当前 scope／H0 状态必须如实记录，不能因为进入节点包就写成 READY 或 PASS。

这份节点的默认必需范围到白模参考阶段为止。正式网页生图、结果回收、抠图、合成和整场验收仍属于原冻结生产主线，不能因为节点只含白模而删除或改成不适用。人工处理与回流默认是与主线并行的 `PARALLEL_NONBLOCKING` 支线；只有用户明确要求暂停等待人工审核／修改时，才使用 `USER_HOLD` 并把 approval 作为后续门禁。

只有用户明确要求把旧批冗余生成结果拿来判断可复用性时，才启用 pack 中的 `legacy_migration_backfill.enabled=true`。每次启用都必须绑定当次完整历史来源清单，把已按当前白模生成的旧 RGB 候选登记为 `legacy_render_candidate`，把已抠除背景且有可靠位置的旧 RGBA 登记为 `legacy_scene_ready_rgba`；每项都保留来源、SHA-256、技术／视觉状态和 provenance。后者文件名必须以 `__XY_x<int>_y<int>` 收尾并与记录坐标一致。它们作为根层真实图像供用户直接审阅，但不计作生产白模，不自动变成当前候选或 PASS。以后遇到同类明确分拣要求可再次启用；普通新节点保持关闭，也不得因此固定交付全部生成历史。

多场任务完成或汇报前，复制 `assets/character-node-delivery-batch-audit.template.json`，列出冻结批次的准确 `expected_scene_ids`、每场可读 `scene_label` 和 scope 绑定，再运行 `audit-batch`。它逐场验证唯一 manifest，输出 UTF-8 CSV、Markdown 和 JSON；逐场列地点、时间、每个 actor/pose 的母层与 Image 1、联合预览、UI 预览，并把缺失场景或文件逐项标为 `NEEDS_MANUAL_SUPPLY_OR_REPACKAGING`。任何遗漏、多余场景目录或失效包都使批次为 `INCOMPLETE`，不得用当前已有文件数冒充全量。

`joint_whitebox_preview` 只审核多人关系，`actual_ui_clearance_preview` 只审核 UI 避让。二者不得改名、裁切或用状态字段冒充 `complete_anatomy_master` / `final_submission_whitebox`。木棍、关节点、程序几何块、扁平色剪影和技术量尺不属于生产白模。

## `_节点资料` 隔离

所有 JSON、候选状态、来源路径、SHA-256、冻结 scope、来源索引、交接文档、命名表、网页提示词、技术／视觉审核、discovery／provenance receipt、HTML 总览和人读清单都只放进 `_节点资料`。每个根层文件有 `_节点资料/<同名 stem>/<同名 stem>_节点候选.json`，其审核证据同组；节点级资料位于 `_节点资料/_节点/<node-id>/`。迁移模式的完整历史来源清单也只放节点资料。根层出现 JSON／说明文件，或出现 actor／类型／revision 资产子目录，均为失败。

节点 manifest 的 `formal_pass` 必须为 false，状态只能是 `NODE_DELIVERY_READY_PENDING_USER_REVIEW`。它是按用户要求放在 `{DELIVERY_ROOT}` 下的隔离审核包，不是交付候选 registry、批准身份源、正式资产或工程同步来源。reference handoff 和网页提交必须逐字节复用节点冻结的 master 与 Image 1；默认 `PARALLEL_NONBLOCKING` 不等待人工回流，用户明确要求暂停时才由 `manual_review_node.py` 建立 approval 并转为 `USER_HOLD`。
