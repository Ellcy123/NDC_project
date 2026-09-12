# 提示词风格绑定门禁

在正式人物入景的每一次提示词编辑后、模型提交前执行本门禁。它补充而不替代候选图的 `STYLE_LOCK_GATE` 与 `TEXTURE_COHERENCE_GATE`：前者检查提示词仍忠实绑定既定生产风格，后两者检查实际生成像素。

## 唯一原版与可变范围

- 唯一可用于新人物入景网页提交的风格描述是本 Skill 的 `assets/original-user-style-description.txt`。它直接保存用户 2026-08-22 提供的原文，UTF-8 SHA-256 固定为 `b1208685aa0dfdde5da5fca44dfde6f94d815c720bc55612a998d2e53859bf79`。不得从旧 prompt、旧 style-lock、聊天摘要或本页转录；工作包只可逐字节复制该 asset。
- 原文包含 `(shirt, jacket, skirt, tie)`，末尾为 `straight perspective,` 后接 U+00A0 NO-BREAK SPACE 和 LF。不得 trim、Unicode／空白归一化、改行尾、翻译、缩写、同义替换、删括号内容或按角色改变。`assets/original-user-style-description.manifest.json` 保存来源与终止码点说明。
- 渲染提示词必须恰好包含该 asset 的完整原始字节一次。原版块之外不得出现第二份完整或改写的原版风格描述；其它动作、构图、支撑和像素保护约束不能改写这段风格文本。
- Image 1/2/3 必须依次为 `local-whitebox-crop`、`untouched-full-scene`、`approved-character-card`。
- 动态字段仅包括角色/身份、当前白模和哈希、相机可见方向、可见动作、支撑接触、可见脸手细节和已登记的几何范围；动态字段不得含 `style`、`texture`、`brushwork`、`line_language`、`lighting_style` 或反向风格词。

在记录模型 attempt 之前执行：

```powershell
python scripts/validate_prompt_style_binding.py --contract <prompt-binding.json> --output <prompt-binding-gate.json>
```

`prompt-binding.json` 使用 schema `ndc-prompt-style-binding/v2`，至少提供：

```json
{
  "style_lock_path": "work copy byte-identical to assets/original-user-style-description.txt",
  "fixed_style_sha256": "b1208685aa0dfdde5da5fca44dfde6f94d815c720bc55612a998d2e53859bf79",
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

验证器从自身 Skill 根解析 canonical asset，先核验 asset、manifest 和内置 hash，再逐字节比较工作副本，并检查完整 prompt 中出现次数、引用角色和动态字段。工作副本即使自带一个内部一致的新 hash，只要与原版字节不同也会 `FAIL`。该门禁只能证明提交文本绑定，不能批准候选像素。
