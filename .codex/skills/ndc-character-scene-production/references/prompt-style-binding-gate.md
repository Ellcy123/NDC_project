# 提示词风格绑定门禁

在正式人物入景的每一次提示词编辑后、模型提交前执行本门禁。它补充而不替代候选图的 `STYLE_LOCK_GATE` 与 `TEXTURE_COHERENCE_GATE`：前者检查提示词仍忠实绑定既定生产风格，后两者检查实际生成像素。

## 不可变与可变范围

- 将当前已批准生产风格完整存为一个 `style_lock` 纯文本文件；不在角色提示词中重写、缩写、同义替换或按角色改变。
- 渲染提示词必须恰好包含该文件一次，且其 SHA-256 与提交合同相符。
- Image 1/2/3 必须依次为 `local-whitebox-crop`、`untouched-full-scene`、`approved-character-card`。
- 动态字段仅包括角色/身份、当前白模和哈希、相机可见方向、可见动作、支撑接触、可见脸手细节和已登记的几何范围；动态字段不得含 `style`、`texture`、`brushwork`、`line_language`、`lighting_style` 或反向风格词。

在记录模型 attempt 之前执行：

```powershell
python scripts/validate_prompt_style_binding.py --contract <prompt-binding.json> --output <prompt-binding-gate.json>
```

`prompt-binding.json` 使用 schema `ndc-prompt-style-binding/v1`，至少提供：

```json
{
  "style_lock_path": "absolute path to immutable style_lock text",
  "fixed_style_sha256": "sha256 of that exact text file",
  "rendered_prompt_path": "absolute path to the prompt to submit",
  "reference_roles": ["local-whitebox-crop", "untouched-full-scene", "approved-character-card"],
  "dynamic_fields": {
    "character": "...",
    "whitebox_id": "...",
    "camera_orientation": "...",
    "visible_action": "...",
    "support_contact": "...",
    "geometry": "..."
  }
}
```

The validator writes `PASS` or `FAIL` with the prompt/style hashes, role checks,
dynamic-field validation and specific failure reasons. A prompt gate cannot
declare a candidate artistically accepted; it is a required pre-submission
receipt only.
