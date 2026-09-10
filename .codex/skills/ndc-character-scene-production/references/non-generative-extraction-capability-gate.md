# 非生成提取能力门禁

对通过候选级视觉检查、准备提取透明角色层的每个角色执行本门禁。默认优先等待同一 scene/revision 的完整生成清单齐备后统一执行；若网页生成／回收真实等待或其它具体调度理由已记录，也可对清单中已就绪角色提前执行。本门禁检查的不是“Photoshop 是否连接”，而是当前代理会话能否在 Photoshop 内真实完成非生成选区、透明像素层或蒙版、以及 RGBA 导出。它不替代整场生成进度记录、候选视觉检查、最终 Alpha 检查、坐标登记或整场验收；提前提取不能使尚缺角色从 scope 消失。

## 通过条件

在使用本机已配对的原生 Photoshop MCP 前，建立 `ndc-non-generative-extraction-capability/v2` 合同与来自当前会话的 `ndc-photoshop-execution-capabilities/v1` 能力快照。合同必须绑定：

- 当前上下文候选的绝对路径和 SHA-256；
- 自动路线的 `source_open`：当前原生 MCP 命令目录中 `supported` 且真实适用于该源的受控打开、置入或导入命令。不得因命令名看似可用就列入合同，也不得把候选复制到导出目录后冒充导出；`experimental`、`requires_user` 或预期的人工操作均为 FAIL。未来其它受支持的置入／导入命令可以登记，不固定某一个入口；
- `route: photoshop_non_generative`；
- `method` 是如实记录当前提取路线的审计标签，不是封闭枚举，也不指定或偏好某一个 Photoshop 按钮。只要当前运行时将所需原生命令标为 `supported`、该路线全程非生成式且能留存真实操作、PSD/PNG 与 Alpha/蒙版证据，就可采用任何能可靠达到边缘识别与透明提取目的的 Photoshop 方法；例如 `selection_to_layer_mask`、`action_result_to_rgba`、`channel_derived_rgba`、色彩范围、计算/应用图像、路径/矢量蒙版、混合条件，或它们在同一未保存源副本中的组合。人工 Photoshop 路线只可由用户为当前资产明确指定的人工制作人员执行，或由用户对当前资产主动明确选择亲自执行；必须登记人工交接，并以同等的实际保存和审阅证据复核。用户默认不是人工制作人员，不能从一般任务授权、历史协作、已打开 Photoshop 或 `requires_user` 状态推定其承担生产操作；
- `output_requirements` 中的 `format: png`、`alpha: true`、`no_generated_pixels: true`。

能力快照必须引用当前运行时的原始命令目录（绝对路径及 SHA-256），并为 `source_open`、当前路线所需操作和导出逐项记录 `status: supported` 与原始说明。验证器会把快照与该目录的真实 `id/status/description` 逐项比对。主体/对象选择、通道 Alpha、已安装非生成动作和人工蒙版修整都可成为路线的一部分，但它们的名称、成功返回、棋盘格或透明像素统计均不能替代实际输出审阅。坐标多边形、自动手绘轮廓、像素复制和图层可见性不构成边缘识别或结果证据。`requires_user`、`unavailable`、`unverified`、`experimental`、连接状态、预期的人工作业或“之后再处理”都不能证明能力存在。

## 用户职责与人工节点边界

- `requires_user` 只是当前命令不能由自动接口直接完成的能力状态，不是把该步骤分配给用户的授权。
- 用户默认只负责需求决策、结果审核及登录／验证码等平台强制身份节点；不得要求用户执行 Select and Mask、色彩范围、通道、蒙版、笔刷修边、保存导出或其它图片生产劳动，也不得等待用户回复“已完成”后才继续。
- 只有用户对当前资产主动明确选择亲自操作，或明确指定了人工制作人员，才可建立 `manual_handoff`。记录必须包含操作者来源、当前资产、允许操作、预期输出和回收证据；不得把一般性“继续”“执行到完成”或 Photoshop 已打开解释为人工参与授权。
- 某个候选或路线失败后，必须建立并继续填写 `route_exhaustion_log`，核验其它实时 `supported` 的非生成路线和任务已授权的确定性处理；一次自动动作失败不能直接升级为人工交接或整体能力失败。日志必须区分端到端独立路线与同一路线参数重试，逐条记录材质适用性、所需命令实时状态、是否执行、输入／输出哈希、真实结果和精确失败点。获得正式通过的 RGBA 后可以停止；否则只有所有适用路线均有实测或 `NOT_APPLICABLE`／`UNSUPPORTED` 证据时，才能记录 `EXTRACTION_CAPABILITY_GATE: FAIL` 和准确缺项。

“选择主体”已得到选区但没有任何当前 `supported` 的方式落实为 Alpha，只证明 `selection_to_rgba` 路线在落实环节受阻，不影响直接透明动作、通道／计算或其它适用路线。“移除背景”已导出真实 RGBA 但仍保留矩形场景背景，必须记录为 `PROVISIONAL` 或质量失败、保留其文件并继续其它路线；不得把它改述为“没有输出”。同一原样命令最多重试一次。Computer Use 或界面操作不属于默认路线，只有当前任务另有明确授权时才可纳入。

## 已安装动作的候选试验

`action.play` 运行的 Photoshop 内置动作（包括名称为“选择主体”“移除背景”或其本地化版本的动作）可以是 `action_result_to_rgba` 正式路线的一步，但必须在**源图的未保存副本**上运行，不得对原图直接运行。每次试验必须记录动作集/动作名、源图 SHA-256、临时文档 ID、导出的 PSD/PNG 和全图/发丝/手/鞋/高对比衣物边缘的局部审阅。

以下任一项为正式提取 `FAIL`，并以“提取能力/边缘质量”回退：动作仅返回成功；仅出现透明像素；仍留场景像素、椅背、窗框或其它背景残片；切掉发丝、手、鞋或服装边缘；动作破坏 RGB 身份；没有可核验的真实 Alpha；或未完成规定的局部审阅。动作候选失败不得消耗正式角色生产额度、不得作为正式角色层或正式接触合成的输入；若已经导出可打开的真实 RGBA，则必须按下文 provisional 分支保留、派生和交付审核。`action.play` 不可冒充为 `subject_selection` 或 `selection_to_mask`；它必须以 `extraction_action: installed_action_play` 如实记录，并接受实际输出门禁。

运行：

```powershell
python scripts/validate_extraction_capability.py --contract <extraction-contract.json> --output <extraction-capability-gate.json>
```

只有 `EXTRACTION_CAPABILITY_GATE: PASS` 才能占用 PS 队列并开始提取。随后仍须实际导出 PSD 与 PNG、检查 Alpha 像素、边缘、尺寸、坐标和全场回放；预检通过不等于透明资产通过。

## 不完整结果的 provisional 流转

能力门禁已通过并实际导出可打开的非生成 RGBA 后，如果结果因边缘、残留、误删、软边或置信度不足而未达到正式 Alpha 门禁，不得留空或只保存失败文字。保留提取前原图及 SHA-256，另存尝试 RGBA、PSD、蒙版／路径／动作证据、Alpha 多底预览和逐区缺陷，状态固定为 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW`。允许继续 provisional 注册、遮挡、接触、阴影、整场合成、XY、重建和全场检查；所有派生结果继承该状态和源哈希，并进入 `工作过程文件` 下独立的“待用户审核交付包”。

该流转只提供可审核资产，不是正式放行：不得写入正式目录、不得满足正式发布验证器、不得把失败项改记 PASS。用户审核、人工修正或后续自动提取通过后，从保留原图或明确选定版本建立新修订并重跑受影响门禁；旧 provisional 版本继续作为历史，不被覆盖。若根本没有合规 RGBA 输出，则不适用本分支，按下节能力失败处理。

## 失败处理

若当前会话缺少受支持源图入口，或完成 `route_exhaustion_log` 后证明所有适用路线均在端到端能力上受阻，且确实没有任何合规 RGBA 输出，才写入 `EXTRACTION_CAPABILITY_GATE: FAIL` 与实际缺项，保留原始上下文候选及 SHA-256。暂停依赖该角色透明层的合成与最终放行，但继续同一整场内不依赖该透明层的已授权工作，例如其它冻结角色的网页生产、来源回执、候选审核和独立准备；涉及该角色精确遮挡、接触或最终合成的步骤继续等待能力恢复。已有可打开但不完整／低置信度 RGBA 时改走上一节，不得误报为“没有输出”。不得：

- 调用任何生成式图像工具来“补一张透明图”；
- 用生成或重绘背景替代抠图；
- 将不透明上下文图、棋盘格背景图或未验证文件称为 RGBA；
- 省略该角色、把未完成透明提取登记为完成，或继续其接触合成、XY 和最终场景 PASS。

## 合同和快照最小结构

```json
{
  "schema": "ndc-non-generative-extraction-capability/v2",
  "source_candidate_path": "absolute path to contextual candidate",
  "source_candidate_sha256": "64 lowercase hex",
  "route": "photoshop_non_generative",
  "method": "selection_to_layer_mask",
  "capability_snapshot_path": "absolute path to current-session snapshot",
  "operations": {
    "source_open": {"command_id": "<current supported open/place/import command>", "effect": "source_open", "source_path": "same absolute path as source_candidate_path"},
    "subject_selection": {"command_id": "selection.select_subject", "effect": "subject_selection"},
    "selection_to_mask": {"command_id": "layer.mask_from_selection", "effect": "selection_to_layer_mask"},
    "rgba_export": {"command_id": "document.export", "effect": "rgba_export"}
  },
  "output_requirements": {"format": "png", "alpha": true, "no_generated_pixels": true}
}
```

`action_result_to_rgba` 的最小操作为上述 `source_open`、`extraction_action: {"command_id":"action.play","effect":"installed_action_play"}` 和同样的 `rgba_export`；`channel_derived_rgba` 的最小操作为上述 `source_open`、`alpha_channel: {"command_id":"<current supported channel command>","effect":"alpha_channel_construction"}` 和同样的 `rgba_export`。其它方法可按实际调用补充一个或多个具名 `operations` 字段；验证的是其当前 `supported` 状态、来源和输出证据，不是字段名是否属于预设名单。这只是能力合同：正式通过仍需在当前冻结输出上实查 Alpha、边缘和背景残片。

```json
{
  "schema": "ndc-photoshop-execution-capabilities/v1",
  "session_id": "current task id",
  "captured_at": "ISO-8601 timestamp",
  "catalog_path": "absolute path to current Photoshop command catalog JSON",
  "catalog_sha256": "64 lowercase hex",
  "commands": [
    {"id": "selection.select_subject", "status": "supported", "description": "Create a subject selection"},
    {"id": "layer.mask_from_selection", "status": "supported", "description": "Create a layer mask from the active selection"},
    {"id": "document.export", "status": "supported", "description": "Export the active document as PNG RGBA"}
  ]
}
```

记录工具调用的原始输出路径或哈希，以便在复核时证明快照不是历史能力或人工推测。
