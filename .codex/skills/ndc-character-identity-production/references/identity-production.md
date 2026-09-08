# 身份母版生产细则

以下 `assets/` 指共享 `../../ndc-generate-characters/assets/`；提示、用户选择、预算和角色合同以入口指定的现行合同为准。本文件仅用于身份路线。

## 重要角色MJ全身


Use the current Midjourney default model. Never add `--v`, `--V 8.1`, or another model-version flag.

Open or reuse the Alpha Imagine page at `https://alpha.midjourney.com/imagine`. Do not identify the Alpha site from the upper-left logo or a screenshot and do not substitute the non-Alpha `www.midjourney.com` page.

The two core MJ style references are already saved in the Midjourney account. Click `Images` in the upper-right of the Imagine page, select the matching two saved images from the panel below, and assign both to `Use style`. Do not upload the local copies during normal operation. Use the bundled assets only to visually identify the correct saved images:

- `assets/mj-style-reference-1.png`
- `assets/mj-style-reference-2.jpg`

Use 1:2. Require a complete head-to-toe character, natural standing pose, shoulder-height/eye-level camera, and a minimal pure-white background. Keep both reference files and the aspect ratio fixed while changing the character-description variable.

### 2.1 Apply the MJ `123` candidate-selection loop

Apply the same loop to the full-body grid and to every optional MJ head-material grid. A pass means the current stage's applicable hard gates are met, not merely that an image is the least flawed. Expression and portable story props are excluded from MJ hard gates unless the active user prompt or an explicit instruction marks them `HARD_NOW`. Do not revise the prompt before completing the current group's `Subtle` then `Strong` route. At every decision, save the group number, batch number, job URL/ID, selected source candidate, variation action, review result, and—when starting a new group—the exact prompt delta derived from its Batch-1 evidence. The detailed sequence, maximum budget, and `FALLBACK_SELECTED` handling are defined in `../../ndc-generate-characters/references/character-rules.md` and the stage-receipt requirements in `../../ndc-generate-characters/references/execution-gates.md`.

### 3. Apply the head-quality gate

After selecting a viable full body, inspect the head at useful zoom.

- Treat facial legibility as a hard gate, not a preference. Both eyes, the brow/eye spacing, the nose bridge and tip, the mouth or mustache shape, the jaw/cheek contour, and the hairline must be simultaneously readable at useful zoom. Dramatic chiaroscuro is allowed only when it sculpts these landmarks rather than erasing them.
- If the head is clear, structurally reasonable, identity-distinctive, and fits the role description, skip separate head generation.
- If the head is too small, blurred, malformed, cropped, generic, insufficiently descriptive, or has a large shadow mass that hides an eye or other identity landmarks, do not pass the gate. Generate separate head material with the same two MJ style references and 9:16, or explicitly route the face through local repair before identity lock.

Do not require the separate head to look like the face in the full-body image. Midjourney text generation cannot reliably reproduce the same person. Judge the head by role-description fit, structural quality, hairstyle silhouette, age, period, and usability as refinement material. Do not fail it for lacking an inferred smile, menace, kindness, or other temporary expression unless that expression is explicitly required in the current MJ prompt.

Never confuse the MJ head material with the later general-style portrait deliverable.

### 4. Plan MJ-stage refinement and lock identity

Use the full-body image as the source of body type, pose, outfit layers, shoes, accessories, color scheme, and silhouette. When a separate head is stronger, use it as a replacement or redraw reference without demanding raw-image facial consistency.

Route defects explicitly:

- Regenerate full body for major body, pose, costume, role, or style failure.
- Generate or regenerate head material for an otherwise good full body with an unusable head.
- Refine locally for background debris, fake text/signatures, unwanted objects, silhouette joins, hands, feet, shoes, clothing borders, and excessive fragmented details.
- Treat local repeated marks, broken texture continuity, or isolated decorative micro-detail as a bounded repair from the frozen approved source. Treat whole-image micro-detail inflation as a regeneration from the original stage authority; never chain from the failed candidate or use sharpening, texture overlays, AI upscaling, or repeated resizing as a texture fix.
- Defer a missing portable story prop or non-identity expression to Image 2 unless the active user prompt explicitly makes it a current-stage hard requirement. Their absence alone must not restart MJ concept generation.
- Treat a hand hidden behind the back as a pose defect. Prefer an otherwise comparable candidate with both arms and hands visible. Accept the hidden-hand candidate only when its body type, head-to-body proportion, face, or role fit is materially stronger; in that case, repair the pose with Image 2 before producing the character card.
- Accept directly when the full body and head are already clear and usable.

Do not declare identity lock while the face is still ambiguous. If the raw full-body face fails the legibility gate, combine the chosen body with approved head material or locally repair/re-light the face until the resulting MJ-stage refined full body has a readable, distinctive face.

Treat that refined full body as the first identity lock. Preserve an identity-anchor crop of its final face when the full-body scale is too small for reliable comparison. The crop must come from the same locked image or the exact face composited into it; an unrelated raw MJ head is not a valid downstream identity anchor. Downstream identity consistency begins here, not between the two raw MJ generations.


## 通用风格身份母版

参考顺序：已锁定MJ全身 → 需要时其同源面部锚点 → 通用全身风格参考（style-only）。逐项比较脸型、额头、眉眼距离、鼻形、口／胡须、颧颌、耳朵、发际线和不对称特征；只保留“同年龄、胡须、发型”不足以通过。转绘身份漂移返回转绘，不能重开已选MJ设计。进入角色卡前双臂自然下垂、双手可见；严格侧视允许远侧手自然重叠。

次要新角色直接按共享提示库1.1的通用风格生产母版，不走MJ；其标准下游为角色卡，不自动补肖像。每个真实生成／精修／转绘阶段沿用共享预算及当前hash绑定的视觉记录，任何候选失败不重置计数。
