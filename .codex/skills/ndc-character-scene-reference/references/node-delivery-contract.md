# 角色入景白模节点交付合同

角色人工节点不是 JSON 审批表，而是用户可以直接打开、比较和继续修改的真实文件包。每个场景 revision 在正式人物网页生图前，先从 `assets/character-node-delivery-pack.template.json` 建立 v3 pack spec；旧 v1/v2 包仅保持历史可验证，不作为新节点模板。再运行：

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
- 每场唯一的可编辑表演 PSD：`SC<scene>_scene_<revision>_performance-editable_source.psd`。

可编辑表演 PSD 是新节点必交资产，不是“有就附带”的可选源文件。它参考 `SC2206__ref-20260911__scene__whitebox-recovery__source.psd` 的使用方式：画布保持原场景尺寸；原场景为独立层；真实 UI 为独立可开关层；冻结 scope 中每个 actor/pose 都有可独立开关、移动和等比调整的命名层或组，并保留节点当前的位置与比例。若同一场景含多个快照，在同一 PSD 内以清晰快照组隔离，不另建多个互不关联的 PSD。不得只放扁平联合预览、链接失效的外部对象或无法单独修改各表演的合并层。

PSD 内每个 actor/pose 必须来自已经视觉通过的 `complete_anatomy_master`：人物具有连续三维体积与明暗，头、颈、肩胸、躯干、骨盆、双臂／手、双腿／脚及重心／承托关系可读。颜色不是判定项；彩色三维白模可以优于灰色方案，扁平轮廓即使带渐变、抗锯齿、混合 Alpha 或丰富色彩仍是代理。每对母层／Image 1 复制 `assets/whitebox-visual-review.template.json`，绑定两者精确 SHA-256、100% 整体与不低于 200% 局部视觉检查以及全部三维／解剖／代理排除项。程序色彩、亮度或 Alpha 检查只能淘汰明显坏件，不能写出视觉 PASS。

整场 PSD 复制 `assets/performance-editable-psd-review.template.json` 建立结构收据：绑定 PSD 精确 SHA-256、当前画布与原场景画布尺寸、背景／真实 UI／逐 actor-pose 图层结构，并逐项绑定已通过母层的 SHA-256。冻结 scope 有任一 actor/pose 未通过、缺层或夹带联合预览／扁平代理时，整场 PSD 失败；不能把一项通过拆成整场节点，也不能用 Photoshop 分层包装改变源白模质量。

部分返修不从空白整场重建。先把用户当前认可的联合白模及其独立角色层冻结为 revision baseline，再区分 `preserve` 与 `replace`：只替换用户当前明确列出的 actor/pose，未列入者保留原来源字节、位置、比例、主朝向和叙事关系。用户纠正返修名单时以最新完整名单为准；合并后重新检查整场关系和真实 UI，但不得借复核扩大返修范围。案例上，已认可的彩色三维整场白模应作为构图权威，即使另一个灰色方案的单人结构也像三维人物，若它改变镜头、动作、相互关系或未经要求重做保留角色，仍不能取代 baseline。

完整人体母层与 Image 1 必须逐 actor/pose 成对齐全，并覆盖冻结 scope 的全部 actor/pose；每场还必须有且只有一个上述可编辑表演 PSD。只收一场中的部分角色、只收一个场景而遗漏批次清单中的其它场景、只收联合预览、只收 JSON 或只有 PSB／扁平图而没有 PSD 都失败。跨场景批次逐场生成上述目录和 manifest，再用批次索引链接每场；不得把八个场景混入一个无场景层级的日期目录。历史可用白模可以复制精确字节进入对应场景，但其当前 scope／H0 状态必须如实记录，不能因为进入节点包就写成 READY 或 PASS。旧 v1/v2 节点保持历史可验证；本要求约束新建的 v3 节点。

这份节点的默认必需范围到白模参考阶段为止。正式网页生图、结果回收、抠图、合成和整场验收仍属于原冻结生产主线，不能因为节点只含白模而删除或改成不适用。人工处理与回流默认是与主线并行的 `PARALLEL_NONBLOCKING` 支线；只有用户明确要求暂停等待人工审核／修改时，才使用 `USER_HOLD` 并把 approval 作为后续门禁。

只有用户明确要求把旧批冗余生成结果拿来判断可复用性时，才启用 pack 中的 `legacy_migration_backfill.enabled=true`。每次启用都必须绑定当次完整历史来源清单，把已按当前白模生成的旧 RGB 候选登记为 `legacy_render_candidate`，把已抠除背景且有可靠位置的旧 RGBA 登记为 `legacy_scene_ready_rgba`；每项都保留来源、SHA-256、技术／视觉状态和 provenance。后者文件名必须以 `__XY_x<int>_y<int>` 收尾并与记录坐标一致。它们作为根层真实图像供用户直接审阅，但不计作生产白模，不自动变成当前候选或 PASS。以后遇到同类明确分拣要求可再次启用；普通新节点保持关闭，也不得因此固定交付全部生成历史。

多场任务完成或汇报前，复制 `assets/character-node-delivery-batch-audit.template.json`，列出冻结批次的准确 `expected_scene_ids`、每场可读 `scene_label` 和 scope 绑定，再运行 `audit-batch`。它逐场验证唯一 manifest，输出 UTF-8 CSV、Markdown 和 JSON；逐场列地点、时间、每个 actor/pose 的母层与 Image 1、联合预览、UI 预览和可编辑表演 PSD，并把缺失场景或文件逐项标为 `NEEDS_MANUAL_SUPPLY_OR_REPACKAGING`。任何遗漏、多余场景目录或失效包都使批次为 `INCOMPLETE`，不得用当前已有文件数冒充全量。

`joint_whitebox_preview` 只审核多人关系，`actual_ui_clearance_preview` 只审核 UI 避让。二者不得改名、裁切或用状态字段冒充 `complete_anatomy_master` / `final_submission_whitebox`。木棍、关节点、程序几何块、扁平色剪影、带渐变的扁平人形和技术量尺不属于生产白模；自动 `dimensional`／颜色统计通过也不改变其身份。

## `_节点资料` 隔离

所有 JSON、候选状态、来源路径、SHA-256、冻结 scope、来源索引、交接文档、命名表、网页提示词、技术／视觉审核、discovery／provenance receipt、HTML 总览和人读清单都只放进 `_节点资料`。每个根层文件有 `_节点资料/<同名 stem>/<同名 stem>_节点候选.json`，其审核证据同组；节点级资料位于 `_节点资料/_节点/<node-id>/`。迁移模式的完整历史来源清单也只放节点资料。根层出现 JSON／说明文件，或出现 actor／类型／revision 资产子目录，均为失败。

节点 manifest 的 `formal_pass` 必须为 false，状态只能是 `NODE_DELIVERY_READY_PENDING_USER_REVIEW`。它是按用户要求放在 `{DELIVERY_ROOT}` 下的隔离审核包，不是交付候选 registry、批准身份源、正式资产或工程同步来源。reference handoff 和网页提交必须逐字节复用节点冻结的 master 与 Image 1；默认 `PARALLEL_NONBLOCKING` 不等待人工回流。用户交回人工修改后的 PSD 时改用独立 `ndc-character-scene-manual-return`；该 Skill 只处理角色入景，不适用于道具。
