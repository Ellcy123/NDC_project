# 道具节点交付阶段资产合同

## 定位

`节点交付` 是按场景组织、交给用户直接浏览和使用的阶段性人工审核包；不是只传 JSON 的状态回执，也不是单项 `交付候选` 的同义词。默认节点只交原任务最初要求推进到的阶段成果：道具通常至少是实际母图与 Big，角色入景参考则是逐角色完整白模母层及最终 Image 1。它不自动提前要求后续 Icon、场景态、热区、菜单或正式发布资产。

节点是冻结生产主线旁的审核接口，不是替代主线的新流程。没有额外节点要求时，任务仍须继续完成冻结范围内全部资产；节点通过、用户回流或旧资产分拣都不能缩小生产分母、删除原阶段或把未到节点的主线资产改成不适用。

机器 JSON 负责同时冻结完整主线来源与本次节点子范围、哈希和完整性校验。场景根必须直接平铺本次节点 `REQUIRED` 的真实 PNG／JPG、PSD、XY/TXT；用户无需进入 `big`、`icon`、`master`、`map`、`prop`、`psd` 等分类文件夹才能取用。`请先打开_节点交付总览.html`、`节点交付资产清单.md`、JSON、交付候选记录和审核证据统一隔离到 `_节点资料`。目录只含 JSON、只含候选登记表或只含报告链接，一律不是可提交节点；但不能拿“场景根没有后续主线资产”反推那些资产已从冻结范围取消。

## 固定目录

道具类别根由 `ndc_art.py paths` 的 `{DELIVERY_ROOT}` 解析，实际节点固定为：

    {DELIVERY_ROOT}/道具/Unit<n>/节点交付/<scene-id>/

`<scene-id>` 是机器代号；scope、pack、manifest、人工节点和批次清单还必须携带一致的 `scene_label = {display_name, location, time}`。`display_name` 必须同时包含用户可理解的地点与时间，例如“圣心医院病房（白天）”，不能只写 `SC4027`。HTML、Markdown 与批次统计优先显示该概括名称并同时保留代号。

场景根是用户直接取用层；打包器不会在已有场景根上覆盖。目录结构固定为：

- `<scene-id>/SC<scene>_<item-or-scene>_[state_]map|big|icon|master|prop|psd.<ext>`：全部实际交付图片、PSD 源文件和 XY/TXT 直接平铺在场景根；`prop` 专指二级菜单图，扩展状态角色使用合同定义的 `original`、`final`、`preview`、`carrier`、`pickup`、`before_pickup`、`xy`、`container`、`prop_preview` 尾缀。任何已抠除背景、可直接按坐标融回场景的 PNG（`pickup_layer`、`map_hotspot`、`type6_container`）必须在角色尾缀之后、扩展名前追加精确 `__XY_x<int>_y<int>`，例如 `SC4027_4314_map__XY_x1186_y708.png`；清单 `placement_xy` 必须一致。不可直接入景的图片不得冒用该尾缀。
- `<scene-id>/_节点资料/<与交付资产完全相同的文件 stem>/`：该资产的 `*_交付候选.json` 与 `审核证据/`。JSON、交付候选、技术／视觉证据不得出现在场景根。
- `<scene-id>/_节点资料/_节点/<node-id>/`：scope、pack、`节点交付清单.json`、HTML 总览、Markdown 清单和非正式警示。

不得建立 `4112.big`、`01_母图`、`02_Big` 或 `可用源文件/原始图` 这类逐类型／逐资产取用树。每个角色必须在节点矩阵中明确写 `REQUIRED`、`MAINLINE_AFTER_NODE` 或 `NOT_APPLICABLE`，不能把“本节点暂不交”写成“不适用”。

## 节点子范围与完整生产主线

复制 `assets/prop-node-delivery-scope.template.json`，并用 `source_scope` 绑定完整冻结生产范围。对本节点涉及的场景、item／container／shared subject，把以下 16 种角色分别声明为：

- `REQUIRED`：原任务要求本次节点必须看到的阶段资产；默认初始道具节点至少包含实际母图与 Big。
- `MAINLINE_AFTER_NODE`：仍属于冻结生产范围、但按原阶段顺序在本节点之后继续制作或交付的资产；必须保留 artifact ID 和原因。
- `NOT_APPLICABLE`：对该对象确实不存在该角色；不得用于隐藏后续主线工作。

`source_master`、`state_master`、`psd_source`、`big`、`icon`、`scene_original`、`scene_final`、`scene_preview`、`carrier_without_prop`、`pickup_layer`、`scene_before_pickup`、`map_hotspot`、`xy`、`type6_container`、`type7_menu`、`menu_preview`。

节点子范围不是从当前目录反推；它由用户最初要求到达的阶段和后续明确追加的节点要求决定。完整主线仍由 active delivery scope、取得方式、SceneConfig、ItemStaticData、容器链、环境叙事／线索语义和场景依赖推导，并通过 `source_scope` 的 SHA-256 保持冻结。`semantic_class=clue` 和 `semantic_class=environment_narrative` 只记录语义，不改变平铺位置。

两个既有任务中从旧冗余资产分拣出的 Icon、场景态、热区、菜单、PSD 等属于例外支线。用户明确要求时，可在核对当前来源、真实字节、审核和坐标后把它们提升为该节点的附加 `REQUIRED`；以后遇到同类明确分拣要求也可采用相同方式。普通新节点不自动扫描、强制补齐或提前生产这些后续资产。

硬关系：

- 每个非场景 subject 至少需要 `source_master` 或 `state_master`；母图不能被 Big、Icon 或 Map 代替。
- `map_hotspot` 必须同时需要 `xy`。
- `pickup_layer` 与 `type6_container` 进入节点时必须同时需要 `xy`；正式主线中的直接拾取四态、Type 7 菜单预览及重建关系仍由原阶段门禁完整执行，不能因节点只交局部文件而删除。
- 共享母图仍要把字节一致副本收进每个使用它的场景节点；不能让用户跳到“共享资产”树自行拼包。

## 打包与验证

复制 `assets/prop-node-delivery-pack.template.json`，只为节点 scope 中的每个 `REQUIRED` artifact 指定实际源文件、标准交付文件名、状态、选用依据和真实审核文件；`MAINLINE_AFTER_NODE` 只进入清单的主线续作区，不要求提前复制。文件名必须以场景与 subject 开头并以角色结尾，例如 `SC4002_4112_big.png`、`SC4002_4112_master.png`；用户追加的场景可放置 Map 示例为 `SC4002_4112_map__XY_x320_y180.png`。同一道具多状态可在 item 与角色之间增加状态段。所有图片必须同时有 `technical_review` 与 `visual_review`；PSD/XY 等非图片至少有 `technical_review`。节点允许清晰标记的 PASS、provisional 或可见失败件供用户判断，但不得缺少当前 `REQUIRED` 或把失败写成 PASS。

从当前 Skill 根运行：

    python scripts/node_delivery.py pack --scope <prop-node-scope.json> --pack-spec <pack.json> --delivery-root <resolved-delivery-root>/道具
    python scripts/node_delivery.py verify --manifest <节点交付清单.json> --delivery-root <resolved-delivery-root>/道具
    python scripts/node_delivery.py audit-batch --batch-spec <prop-node-delivery-batch-audit.json> --delivery-root <resolved-delivery-root>/道具 --output-dir <resolved-{WORK_ROOT}/节点交付统计>

只有在用户明确要求从前序／旧冗余资产分拣附加节点内容时，才额外运行：

    python scripts/node_delivery.py reconcile-hotspots --batch <current-batch.json> --unit Unit<n> --delivery-root <resolved-delivery-root>/道具 --output-dir <resolved-{WORK_ROOT}/节点交付统计>

该命令逐项反查当前批次 Stage4 PASS 热区的源 PNG、审核绑定、正确场景节点副本和 XY 文件名，用于发现“已通过但漏包”的旧资产；它不是普通节点默认门禁，也不启动或替代 Stage4 生产。

打包器执行字节一致复制，自动生成平铺交付层和隔离的 `_节点资料`。其清单设计参考公开打包工作流中“payload 与元数据／逐文件哈希分层”的做法，但 NDC 路径和命名完全以本合同为准。它拒绝：

- scope 角色矩阵不全、`MAINLINE_AFTER_NODE` 缺 artifact ID／原因，或 `NOT_APPLICABLE` 没有理由；
- 任一 required artifact 缺失、重复、越界或多出未绑定文件；
- 只有 JSON 而没有实际资产；
- 图片缺技术或视觉审核证据；
- 交付资产未平铺在场景根、文件名缺少 `SC<scene>_<subject>` 或没有以已声明角色尾缀收束；
- JSON、候选记录、总览或审核证据混入场景根，或资产资料没有放进与交付文件同 stem 的目录；
- 节点 `REQUIRED` 的 Map、pickup layer 或 Type6 无 XY；正式主线四态与菜单关系仍由原阶段门禁处理；
- 可直接入景 PNG 缺 `__XY_x<int>_y<int>`、尾缀与 `placement_xy` 不一致，或非入景文件冒用 XY 尾缀；
- 文件哈希变化、错误场景目录、错误 node-id 或在已有场景根上覆盖。

打包后的 `NODE_DELIVERY_READY_PENDING_USER_REVIEW` 仅表示“当前节点 `REQUIRED` 齐全、目录可用、哈希一致并可提交审核”。manifest 必须同时列出 `MAINLINE_AFTER_NODE`，提醒后续冻结主线照常继续。用户批准仍由 `manual_review_node.py` 精确绑定该清单；正式视觉、技术、父图、重建、运行时和发布门禁继续执行。

多场任务完成或汇报前，复制 `assets/prop-node-delivery-batch-audit.template.json`，列出冻结批次的准确 `expected_scene_ids`、每场 `scene_label` 和 scope 绑定，再运行 `audit-batch`。其 UTF-8 CSV、Markdown 和 JSON 必须逐场显示代号、地点、时间并逐 artifact 列出已验证或 `NEEDS_MANUAL_SUPPLY_OR_REPACKAGING`；漏场景、无唯一 manifest、多余场景目录或任一 required artifact 失效，整批都是 `INCOMPLETE`。

## 与其它隔离层的关系

- `交付候选`：单个当前目标的状态登记，不是场景节点包。节点打包可以从多个当前候选或已通过资产收集精确字节，但只要求当前节点明确圈定的 `REQUIRED` 齐全。
- `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW`：质量状态；可以在节点中清楚展示，不能冒充 PASS。
- 正式资产：节点通过不结束主线；只有冻结范围全部生产与正式门禁通过后才能转正，节点目录永远被正式发布扫描排除。
- 过程证据：完整历史仍留 `{WORK_ROOT}`；节点只复制本场当前版本所需的审核和交接证据。
