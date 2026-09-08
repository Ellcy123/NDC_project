# 道具入景适配：仅在当前作业插入道具时读取

道具需求、透明母版、场景放入、容器菜单、Map/Big/Icon 和正式打包由相应道具 Skill 持有。本工具只做已授权场景像素编辑，不自行新增这些交付物或把普通修图改成道具批次。

带 `ndc-prop-batch/v1` 时先读 [共用批次协议](../../ndc-prop-requirements/references/batch-contract.md)，沿用原入景 job ID、同一追加尝试日志及总计最多 3 次；换位置、换阶段、最终复查和 PS 修正都不赠送生成额度。不要同时开第二份独立可消费预算。保留失败候选/历史，当前接受依赖链通过即可交付；废弃候选不必变成 PASS。

若物体在篮子、抽屉、箱包等容器内部或由容器承托/露出，交回父流程 Type 6 → Type 7 容器链；不能用直接拾取绕过容器。普通场景修图不加载这条业务规则。

## 授权工作区和最终合成蒙版

新插入证物的父授权区是合法承载面的创作工作区，不是轮廓抠图。优先完整可用桌面、托盘、抽屉内部或地面区；除受保护边界不允许外，包围框两轴至少为计划物体的 3 倍，每个无遮挡侧至少留 128 原图像素，取要求较大者。不可擅自突破受保护边界；空间不足时调整当前授权内方案或报告冲突，不静默缩小安全边距。

候选出来后，另建最终合成蒙版，覆盖完整物体、必要承托面、阴影/反射及细小部件；它必须属于父授权区，任一无遮挡语义边缘/阴影距离硬边界至少 64 原图像素。不得回缩为贴轮廓蒙版。所有硬边界外像素继续零漂移。

For collectible evidence placement, first make a tight intent mask that records the proposed object envelope, then expand it deterministically into the broad authorization workspace. The intent mask is a planning artifact, not the final hard mask. Use `expand-mask`; the command fails rather than silently clipping the required `3x` workspace or `128px` side margins:

```powershell
& $ndcImagePython $ndcCoordinateScript expand-mask `
  --input "$ndcWorkRoot/intent_mask.png" `
  --output "$ndcWorkRoot/authorization_mask.png" `
  --scale 3 `
  --min-margin 128 `
  --limit-rect 1024 384 2048 1408 `
  --report "$ndcWorkRoot/authorization_mask_report.json"
```

Inspect both masks over the full scene. A rectangular broad workspace is acceptable when the prompt and protected-element list keep unrelated content unchanged; it is not required to hug the object contour.

After a candidate exists, create the final composition mask from the candidate's actual object, shadow, and necessary support-surface patch. Prepare a second manifest with the same source and crop, use this composition mask, and compose from the already persisted `generated.png`; this deterministic recomposition does not authorize or require another generation. In final verification, pass the parent authorization mask as the legal union and the composition manifest as the executed job.


## 场景图的信息预算

When the job inserts an NDC evidence prop into an exploration scene, extend the prompt with a map-view contract. Do not paste the full detail-art requirement into this prompt. Use this structure:

```text
Use case: NDC in-scene evidence anchor
Primary request: add a discoverable scene prop that communicates only its object class, silhouette, material, broad color, and current state.
Map-view information budget: this is not the detail sprite. Do not expose exact titles, dates, numbers, signatures, or body text. At gameplay scale it only needs to read as a folder, ledger, envelope, pen, tool, or other named object class.
Perspective contract: infer ordinary physical scale, visible face, foreshortening, and orientation from the source camera, nearby furniture, support surface, and vanishing lines. A document may show only its edge, spine, thickness, folded corner, or an unreadable cover fragment.
Placement contract: keep the entire object, contact shadow, reflection, and required occlusion inside the authorized edit region.
Hard invariants: do not enlarge, stand up, tilt, rotate, or turn the prop toward the viewer for legibility; do not create a close-up, evidence card, product display, signboard, or readable document; return the full edited crop with unchanged framing and camera.
```

The matching `*_big` detail asset owns close-reading information. Generate it separately from the scene insertion so exact text requirements cannot force the map prop into an oversized frontal presentation.


## 附加视觉验收

For in-scene evidence insertion, also reject the job when the prop is oversized relative to nearby objects, turned toward the viewer for legibility, readable like a detail card, inconsistent with the support-surface perspective, or semantically clipped by the hard mask. Run this review on the full scene at expected gameplay display size. Passing containment and boundary reports alone is not acceptance.

For every newly inserted freestanding object, inspect both the parent-authorization overlay and final-composition overlay together with the close crop and gameplay-size full scene. Reject it if any unoccluded semantic edge, tag, loose part, reflection, or shadow comes within `64 source pixels` of the composition hard-mask boundary, if either boundary reads as part of the object, or if a required base/contact shadow merges into the background so that the object appears visually incomplete. A zero outside-mask pixel diff does not waive this completeness check.

If a source-colored fragment remains because the mask was too tight, rebuild the evidence workspace from the intent mask with larger `--scale` or `--min-margin` values and recompose from the persisted generated crop when it already contains the complete object. Regenerate only if the crop itself lacks the complete object or usable replacement texture.


检查接触、遮挡、投影方向、透视、相对尺度、光照/材质/边缘和通行冲突。漂浮/半漂浮即 FAIL，即使像素包含与接缝检测通过。重复失败应诊断承载面、遮挡和真实输入；同一资产换承载面只可使用剩余额度，第三次失败即停止生成，不能另起位置 job。
