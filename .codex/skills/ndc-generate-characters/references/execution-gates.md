# NDC 角色资产可执行门禁

## 目的

本文件把角色生产从“模型记得规则即可”改为“没有证据就不能通过”。它适用于所有推理模型，尤其用于降低较轻量模型在长流程中跳步、混用参考图或把技术规格误判为正式质量的风险。

## 一、生成前参考角色清单

在调用任何生图、修图或拼版工具前，先输出或保存以下清单。每个条目必须包含绝对路径、用途和批准状态。

```yaml
asset: <character and asset type>
identity_sources:
  - path: <same-character approved source>
    locks: [face, hair, body, costume, palette]
style_sources:
  - path: <style library or style-only asset>
    controls: [line, brush, value, material]
landed_peer_comparisons:
  - path: <approved same-branch peer asset>
    compare_only: [layout or portrait style]
rejected_examples:
  - path: <rejected image>
    demonstrates: <known defect>
    forbidden_as: [identity source, approval source]
frozen_user_approved_features:
  - <feature that may not change>
required_output:
  type: <card or portrait>
  size: <width x height>
  background: <white or transparent>
```

硬规则：

1. 身份只能由同一角色的批准素材控制。
2. 风格参考只控制画法，不得覆盖身份。
3. 已落地同分支资产用于横向核对，不得偷换为当前角色身份。
4. 被用户否定的图只能证明错误，除非用户明确保留其中某一局部，否则不能成为批准源。
5. 清单缺路径、用途或批准状态时，正式链状态为 `NOT_CHECKED`，不得进入正式生成或正式交付。
6. 正式角色卡或肖像的 `style_sources` 必须同时列出对应自检库目录和该分支的 style-only 参考文件；只列一张便利样本不能通过回执验证。
7. 用户提供的原始提示词与用户明确选定的图是最高艺术依据。清单必须记录 `user_prompt_authority` 与 `explicit_user_selection`；一旦用户明确选图，该图的艺术搜索停止，除非用户明确要求再做艺术修改。
8. 表情和便携故事道具只有在当前用户提示词明确要求时才是阶段硬门槛。其余均记录为 `DEFER_TO_IMAGE2`，不得阻断 MJ 选图或触发概念重开。

## 二、阶段化执行

严格按依赖关系推进，每一阶段只处理一个可验收对象。正式交付链必须逐阶段通过；用户明确要求完整流程、探索或候选集时，可在失败项留痕后继续生成下游候选，但候选链不构成正式资产。

```text
参考清单
→ 身份/设计源确认
→ 生产路由确认与提示词逐字锁定
→ 默认整卡、单个 4K 模块或单张肖像艺术候选
→ 身份与结构检查
→ 对应自检库整图横向检查
→ 原像素无遗漏局部检查
→ 冻结艺术候选
→ 抠图/等比例缩放/画布定位/边缘清理；仅非肖像必需结构缺边时局部扩图或补全
→ 最终机械检查
→ 阶段回执
→ 冻结通过项或返回失败阶段
```

- 用户未明确要求 `4K` 时，角色卡默认使用 `prompt-library.md` 的锁定整卡提示词一次生成；不得自动拆分模块。
- 只有用户明确要求 `4K` 时才进入模块化角色卡流程，并在回执记录该触发原文。
- 肖像与默认角色卡生成提示词必须逐字匹配源代码块。技术规格不得附加到生成提示词。
- 明确 4K 的模块化角色卡每次只生成一个模块；前一模块未通过时不得生成下一模块。
- 4K 路线中已通过模块冻结。单个模块失败时不得整卡重生，也不得改变已通过模块。
- 4K 路线中所有模块通过后才允许确定性拼版。
- 肖像必须作为独立肖像分支生成；不得用角色卡裁切放大替代。
- 锁定角色卡/肖像提示词要求中性或面无表情时，角色设定中的笑容、和善感或威胁感不构成艺术门禁。MJ 缺少可后补故事道具也不构成 MJ 门禁。
- 艺术候选通过后，比例、尺寸、透明、人物占比和画布位置返回技术整备，不返回生成提示词。非肖像资产的必需结构缺边可在技术整备中局部补全；肖像缺肩或截肩不补全，也不阻断。
- 背景透明化必须晚于艺术候选确认与冻结。原生纸张底不阻断艺术通过；最终透明要求只在末端技术整备与边缘检查中执行，失败时不得改写提示词或重生人物。
- 重要角色的 MJ 全身和可选头部候选选择遵循 `123` 原则：固定提示词的一组依次为初始四宫格（Batch 1）→ 从 Batch 1 最接近图执行一次 `Vary Subtle`（Batch 2）→ 从 Batches 1–2 合计八张最接近图执行一次 `Vary Strong`（Batch 3）。仅在 Batch 3 仍无通过项后，才能根据 Batch 1 的共同偏差改写提示词并开始下一组；最多三组、九批、三十六张。第三组结束仍无通过项时，选择全局最接近图为 `FALLBACK_SELECTED`，并只允许进入有阻断项记录的修复/候选链。不得把该状态写成身份锁、`FORMAL_PASS` 或正式 `identity_source`。
- 每个 MJ 候选阶段回执必须包含：`group_number`、`batch_number`、`prompt_version`、`job_id_or_url`、`selection_action: INITIAL|VARY_SUBTLE|VARY_STRONG`、`selected_source_candidate`（初始批可为 `null`）、四张审查结论、当前阶段门禁、`prompt_delta_from_batch_1`（仅新组）和 `fallback_defects`（仅 `FALLBACK_SELECTED`）。保留每一批及被选源图的可复核链接或本地证据。
- 本规则只替代 MJ 候选选择阶段原有的“两次失败即停止”做法；模块、肖像、技术整备与其他非 MJ 选择阶段继续按照各自的有限重试和阻断要求执行。

## 三、统一状态与阻断条件

每项门禁只允许三个状态：

- `PASS`：已检查并附有证据；
- `FAIL`：发现明确违反项；
- `NOT_CHECKED`：未检查、证据缺失、无法读取或结论不可靠。

正式资产只有在全部必需项为 `PASS` 时才能标记 `FORMAL_PASS`。任何 `FAIL` 或 `NOT_CHECKED` 都必须使 `formal_status` 为 `BLOCKED`，并阻断正式拼版、正式技术整备和正式交付。

用户明确要求完整流程、探索或候选集时，允许继续生成下游候选。每个此类文件和回执必须写明 `candidate_status: CANDIDATE_ONLY`、`chain_mode: EXPLORATORY` 与 `upstream_blockers`；不得把它写入正式 `identity_sources`，不得标为 `FORMAL_PASS`，也不得以“候选已完成”替代正式验收。

禁止使用“基本通过”“大致可用”“待美术确认但先交付”等词绕过阻断。需要用户主观决定时写 `NOT_CHECKED: USER_DECISION_REQUIRED`。

## 四、角色卡回执

角色卡回执必须包含：

```yaml
card_receipt:
  output_path: <absolute path>
  dimensions: <measured width x height>
  ratio: PASS|FAIL
  provenance:
    production_route: DEFAULT_LOCKED_ONE_PASS|EXPLICIT_4K_MODULAR
    explicit_4k_requested: true|false
    explicit_4k_evidence: <user wording or null>
    modules_independently_generated: PASS|FAIL|NOT_REQUIRED
    low_resolution_crop_enlarged: PASS|FAIL|NOT_CHECKED
    generative_redraw_during_assembly: PASS|FAIL|NOT_CHECKED
    fullbody_head_detail_anchors:
      front: {source_module: <path>, native_crop_pixels: [w, h], usage: DIRECT_UNSCALED_CROP|CLARITY_SUPPLEMENT|NOT_USED, no_interpolation: PASS|FAIL, identity_match: PASS|FAIL|NOT_CHECKED}
      left: {source_module: <path>, native_crop_pixels: [w, h], usage: DIRECT_UNSCALED_CROP|CLARITY_SUPPLEMENT|NOT_USED, no_interpolation: PASS|FAIL, identity_match: PASS|FAIL|NOT_CHECKED}
      back: {source_module: <path>, native_crop_pixels: [w, h], usage: DIRECT_UNSCALED_CROP|CLARITY_SUPPLEMENT|NOT_USED, no_interpolation: PASS|FAIL, identity_match: PASS|FAIL|NOT_CHECKED}
  prompt_lock:
    source_path: <absolute prompt-library.md path>
    source_section: <6.2 or 6.1>
    submitted_prompt_path: <absolute verbatim prompt snapshot path>
    exact_text_match: PASS|FAIL
  technical_normalization:
    frozen_art_candidate: <absolute path>
    operations: [BACKGROUND_REMOVAL|LOCAL_OUTPAINT|EDGE_COMPLETION|PROPORTIONAL_SCALE|CANVAS_PLACEMENT|EDGE_CLEANUP|NONE]
    face_hair_costume_interior_frozen: PASS|FAIL|NOT_CHECKED
    scale_factor: <number or null>
    final_subject_bbox: [x0, y0, x1, y1]
    historical_bbox_max_not_exceeded: PASS|FAIL|NOT_CHECKED
    head_ratio_and_position_exception: <evidence or null>
  layout:
    fullbody_region_left_two_thirds: PASS|FAIL
    head_region_right_upper_half: PASS|FAIL
    detail_region_right_remainder: PASS|FAIL
    borderless_white_canvas: PASS|FAIL
  fullbody_measurements:
    front_bbox: [x0, y0, x1, y1]
    left_bbox: [x0, y0, x1, y1]
    back_bbox: [x0, y0, x1, y1]
    common_subject_height: <pixels or null>
    head_top_aligned: PASS|FAIL
    heel_aligned: PASS|FAIL
    shoulder_waist_knee_reviewed: PASS|FAIL|NOT_CHECKED
  required_views: PASS|FAIL
  empty_hands_and_anatomy: PASS|FAIL|NOT_CHECKED
  identity: PASS|FAIL|NOT_CHECKED
  whole_image_checked: true|false
  local_tile_coverage_complete: true|false
  style: PASS|FAIL|NOT_CHECKED
  formal_status: FORMAL_PASS|BLOCKED
  candidate_status: FORMAL_CANDIDATE|CANDIDATE_ONLY
  chain_mode: FORMAL|EXPLORATORY
  upstream_blockers: [<failed or unchecked upstream gate and evidence path>]
```

版式采用用户确认的结构：全身三视图占画面左侧三分之二；头部正面、严格右侧面、背面三视图占右侧区域的上半部；穿鞋结构和其他批准细节占右侧余下区域。最终卡为无边框纯白画布。格子坐标正确但人物实际过小、比例不一致或存在大块无用途空白，仍判布局失败。

`low_resolution_crop_enlarged` 的通过含义是“未发生低清裁片放大”。如发生放大，该项必须为 `FAIL`。最终文件达到 4K 不能抵消该失败。

## 五、肖像回执

肖像回执必须包含：

```yaml
portrait_receipt:
  output_path: <absolute path>
  dimensions: <measured width x height>
  ratio: PASS|FAIL
  provenance:
    newly_rendered_portrait_branch: PASS|FAIL|NOT_CHECKED
    crop_or_upscale_substitute: PASS|FAIL|NOT_CHECKED
  prompt_lock:
    source_path: <absolute prompt-library.md path>
    source_section: 7
    submitted_prompt_path: <absolute verbatim prompt snapshot path>
    exact_text_match: PASS|FAIL
  technical_normalization:
    frozen_art_candidate: <absolute path>
    operations: [BACKGROUND_REMOVAL|PROPORTIONAL_SCALE|CANVAS_PLACEMENT|EDGE_CLEANUP|NONE]
    face_hair_costume_interior_frozen: PASS|FAIL|NOT_CHECKED
    scale_factor: <number or null>
    final_subject_bbox: [x0, y0, x1, y1]
    final_head_bbox: [x0, y0, x1, y1]
    historical_bbox_max_not_exceeded: PASS|FAIL|NOT_CHECKED
    head_ratio_and_position_exception: <evidence or null>
  identity_source_paths: [<paths>]
  style_source_paths: [<paths>]
  peer_comparison_paths: [<paths>]
  identity: PASS|FAIL|NOT_CHECKED
  hair_shape_and_color: PASS|FAIL|NOT_CHECKED
  portrait_style: PASS|FAIL|NOT_CHECKED
  required_background: TRANSPARENT|OPAQUE_PAPER|OPAQUE_WHITE
  background_conformance: PASS|FAIL|NOT_CHECKED
  transparent_silhouette_checks:
    required: true|false
    black: PASS|FAIL|NOT_CHECKED
    white: PASS|FAIL|NOT_CHECKED
    red: PASS|FAIL|NOT_CHECKED
  whole_image_checked: true|false
  local_tile_coverage_complete: true|false
  formal_status: FORMAL_PASS|BLOCKED
  candidate_status: FORMAL_CANDIDATE|CANDIDATE_ONLY
  chain_mode: FORMAL|EXPLORATORY
  upstream_blockers: [<failed or unchecked upstream gate and evidence path>]
```

`crop_or_upscale_substitute` 的通过含义是“肖像不是角色卡裁切或插值放大的替代品”。透明角落、正确比例和保住身份都不能替代肖像风格检查。背景要求来自最终交付规范，而不是生成提示词：透明时 `transparent_silhouette_checks.required` 为 `true` 且三种底色检查必须为 `PASS`；明确不透明交付时该对象只记录 `required: false`，三项非必需门禁不进入回执，由 `background_conformance` 验证背景完整性。

## 六、机械检查与视觉检查边界

先完成原生艺术候选的身份、结构与画风检查并冻结，再按 `post-generation-normalization.md` 做必要技术整备。之后对技术整备后的最终候选运行 `scripts/audit_character_delivery.py`。它负责尺寸、比例、文件模式、透明范围、基础人物区域、版式辅助线和透明底对比图；它不判断人物是否同一人，也不判断画风是否合格。

再运行 `scripts/make_style_review_tiles.py`，并查看全部整图页和局部检查页。只有实际检查全部输出后，才可填写：

```text
whole_image_checked: true
local_tile_coverage_complete: true
```

脚本成功不等于视觉检查完成。哈希一致只证明文件字节一致，不证明身份、版式或画风正确。

全部人工检查完成后，将回执保存为 JSON，并运行：

```text
python scripts/validate_delivery_receipt.py --receipt <delivery-receipt.json>
```

回执中的 `gates` 每项使用对象结构：

```json
{
  "status": "PASS",
  "evidence": ["绝对路径、测量值或具体视觉观察"]
}
```

参考清单的每项使用 `path`、`role`、`approval_status`；其中 `approval_status` 只允许 `APPROVED`、`REJECTED`、`REFERENCE_ONLY`。只有验证器输出 `RECEIPT_VALID: FORMAL_PASS` 才能正式交付。

## 七、交付前反证检查

在写 `FORMAL_PASS` 前，必须主动回答：

1. 当前结论是否只来自尺寸、透明角或文件名？若是，阻断。
2. 是否把角色身份参考与风格参考混为一谈？若是，阻断。
3. 是否只挑了一张最相似的参考，而没有检查对应自检库整体？若是，阻断。
4. 是否把角色卡或全身裁片冒充新生成肖像，是否把普通整卡直接插值放大冒充 4K，或在 4K 拼版时重绘？若是，阻断。对已通过的新生成艺术候选执行有记录的抠图、等比例缩放与画布定位不属于冒充；非肖像资产按规则执行的局部边缘补全也不属于冒充。
5. 是否有用户已指出但当前回执未逐项复查的问题？若是，阻断。
6. 是否能为每个 `PASS` 指向测量值、文件路径或完整视觉检查记录？若否，改为 `NOT_CHECKED`。
7. 默认整卡或肖像的实际提交提示词是否与锁定源代码块逐字一致？若否，阻断并返回生成前。
8. 用户是否明确要求 4K？若否却采用模块化 4K 路线，阻断并返回生产路由。
9. 是否因角色设定中的笑容、威胁感或可后补道具，否定了锁定提示词要求的中性角色卡/肖像，或重开了已由用户选定的艺术候选？若是，阻断并恢复用户选图。
