# 非生成提取能力门禁

在一个上下文角色候选已经通过当前候选级视觉检查、但尚未从该图提取透明角色层时执行本门禁。它检查的不是“Photoshop 是否连接”，而是当前代理会话能否在 Photoshop 内真实完成非生成选区、透明像素层或蒙版、以及 RGBA 导出。它不替代候选视觉检查、最终 Alpha 检查、坐标登记或整场验收。

## 通过条件

在占用共享 PS 队列前，建立 `ndc-non-generative-extraction-capability/v1` 合同与来自当前会话的 `ndc-photoshop-execution-capabilities/v1` 能力快照。合同必须绑定：

- 当前上下文候选的绝对路径和 SHA-256；
- `route: photoshop_non_generative`；
- 只可使用 `selection_to_layer_mask`：Photoshop 真实主体/边缘选区、选区转图层蒙版、PNG RGBA 导出；
- `output_requirements` 中的 `format: png`、`alpha: true`、`no_generated_pixels: true`。

能力快照必须引用当前运行时的原始命令目录（绝对路径及 SHA-256），并为主体选区、选区转蒙版和导出逐项记录 `status: supported` 与原始说明。验证器会把快照与该目录的真实 `id/status/description` 逐项比对。主体选区必须由 Photoshop 的真实边缘识别产生，随后实际生成图层蒙版，并以发丝、半透明边缘和高对比衣物边缘的局部审阅作为完成证据；坐标多边形、手绘轮廓、像素复制和图层可见性不构成识别。`requires_user`、`unavailable`、`unverified`、`experimental`、连接状态、预期的人工作业或“之后再处理”都不能证明能力存在。

## 已安装动作的候选试验

`action.play` 运行的 Photoshop 内置动作（包括名称为“选择主体”“移除背景”或其本地化版本的动作）不是门禁操作本身。它们可在**源图的未保存副本**上验证实际行为，但不得对原图或正式候选直接运行。每次试验必须记录动作集/动作名、源图 SHA-256、临时文档 ID、导出的 PSD/PNG 和全图/发丝/手/鞋局部审阅。

以下任一项为 `FAIL`，并以“提取能力/边缘质量”回退：动作仅返回成功；仅出现透明像素；仍留场景像素、椅背、窗框或其它背景残片；切掉发丝、手、鞋或服装边缘；动作破坏 RGB 身份；或结果不能转换为可复核的图层蒙版。动作候选失败不得消耗正式角色生产额度、不得作为下一角色或接触合成的输入。`action.play` 也不能填入 `subject_selection` 或 `selection_to_mask` 的门禁合同操作；它没有证明这两个效果。

运行：

```powershell
python scripts/validate_extraction_capability.py --contract <extraction-contract.json> --output <extraction-capability-gate.json>
```

只有 `EXTRACTION_CAPABILITY_GATE: PASS` 才能占用 PS 队列并开始提取。随后仍须实际导出 PSD 与 PNG、检查 Alpha 像素、边缘、尺寸、坐标和全场回放；预检通过不等于透明资产通过。

## 失败处理

若当前会话缺少所选路径任一能力，写入 `EXTRACTION_CAPABILITY_GATE: FAIL` 与实际缺项，保留原始上下文候选及 SHA-256，且只允许进行不改变该资产的诊断或等待外部能力恢复。不得：

- 调用任何生成式图像工具来“补一张透明图”；
- 用生成或重绘背景替代抠图；
- 将不透明上下文图、棋盘格背景图或未验证文件称为 RGBA；
- 跳过该角色直接生产或登记下一角色、接触合成、XY 或最终场景 PASS。

## 合同和快照最小结构

```json
{
  "schema": "ndc-non-generative-extraction-capability/v1",
  "source_candidate_path": "absolute path to contextual candidate",
  "source_candidate_sha256": "64 lowercase hex",
  "route": "photoshop_non_generative",
  "method": "selection_to_layer_mask",
  "capability_snapshot_path": "absolute path to current-session snapshot",
  "operations": {
    "subject_selection": {"command_id": "selection.select_subject", "effect": "subject_selection"},
    "selection_to_mask": {"command_id": "layer.mask_from_selection", "effect": "selection_to_layer_mask"},
    "rgba_export": {"command_id": "document.export", "effect": "rgba_export"}
  },
  "output_requirements": {"format": "png", "alpha": true, "no_generated_pixels": true}
}
```

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
