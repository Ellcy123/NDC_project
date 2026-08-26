---
name: ndc-generate-characters
description: Generate, plan, route, audit, and critique NDC stylized characters through either the full Midjourney workflow for important new characters or the ChatGPT Image 2 fast path for minor new characters and existing-character state variants. Use when the user mentions NDC or 摩登迷城 character design, asks for role or character prompts, wants MJ candidate review or refinement routing, needs a new state based on an existing character card, or needs NDC character cards, conditional portraits, or animation-only black-white-red assets.
---

# NDC Generate Characters

## Operating mode

Treat this skill as a standalone character-production skill. Do not merge its rules into a scene skill.

Default to preparing copy-ready prompts, reference order, parameter constraints, review decisions, and refinement checklists for the user to execute manually. Do not call image-generation or image-editing tools merely because the task concerns NDC characters. Only execute images in Codex when the user explicitly asks for Codex execution, batch processing, automatic file management, or engineering integration.

Read `references/character-rules.md` before planning or judging any character task. Read `references/prompt-library.md` when producing prompts. Read `references/evidence-and-gaps.md` when deriving a new preference, evaluating a borderline case, or explaining the confidence of a recommendation.

Read `references/style-self-check.md` before judging or delivering generated assets. Its file paths and hard gates are mandatory for NDC output QA. Read `references/modular-character-card.md` before producing a formal 2K/4K character card or any character card assembled from separately generated views.

Read `references/style-analysis-protocol.md` whenever the task asks for style analysis, style self-check, comparison with style references, or formal style approval. A complete-image review is only the first pass. Use `scripts/make_style_review_tiles.py` to cover every source pixel with overlapping original-resolution tiles, inspect every tile for line, brush, texture, edge, material, and micro-detail behavior, then return those observations to the whole image. Do not call a 4K/8K reference fully analyzed from its downscaled overview alone. A formal style pass requires both `whole_image_checked: true` and `local_tile_coverage_complete: true`.

Use the bundled files in `assets/` in the exact roles stated below. Do not substitute visually similar references without user approval.

## Required inputs

Obtain or identify:

1. The character brief or existing character image.
2. The requested stage: full body, optional head, MJ refinement, general-style full body, character card, conditional portrait, animation-only black-white-red card, or full workflow.
3. Role-specific visible constraints: age, gender, ethnicity when specified, profession, class, personality translated into visible traits, hairstyle, upper garment, lower garment, shoes, and required accessories.
4. The production route: important new character, minor new character, or state variant of an existing character.
5. For an existing-character state variant, the current approved general-style character card. Do not proceed from text alone when that card exists.

If the brief lacks a material identity or costume decision, retain a visible placeholder such as `【角色描述】` instead of inventing plot facts.

## Workflow

### 0. Choose the production route

- Use the full Midjourney workflow for important new characters that need a reusable design master.
- For a minor new character, skip Midjourney and generate directly with ChatGPT Image 2. Use `assets/general-fullbody-style-reference.png` as the style reference and reuse the same general-style wording used by the full-body conversion and character-card stages. Its standard deliverable is the general-style character card only; do not generate a portrait merely to complete a set.
- For an additional state of an existing character, skip Midjourney and use the current approved general-style character card as the primary identity and design reference. Generate the requested state from that card; do not recreate the character from text.
- Route by narrative importance, reuse frequency, identity risk, and production cost. Do not force the full workflow merely because the request concerns a character.
- The black-white-red card is not part of the standard workflow. Trigger it only when the user or project requirement explicitly says that the character is entering animation production.

### 1. Convert the brief into visual design

Extract only visible design conclusions. Separate face, hair, upper garment, lower garment, shoes, accessories, body type, posture, and period/profession cues. Do not turn abstract personality words directly into unsupported costume elements.

### 2. Prepare the Midjourney full-body generation

Use the current Midjourney default model. Never add `--v`, `--V 8.1`, or another model-version flag.

Open or reuse the Alpha Imagine page at `https://alpha.midjourney.com/imagine`. Do not identify the Alpha site from the upper-left logo or a screenshot and do not substitute the non-Alpha `www.midjourney.com` page.

The two core MJ style references are already saved in the Midjourney account. Click `Images` in the upper-right of the Imagine page, select the matching two saved images from the panel below, and assign both to `Use style`. Do not upload the local copies during normal operation. Use the bundled assets only to visually identify the correct saved images:

- `assets/mj-style-reference-1.png`
- `assets/mj-style-reference-2.jpg`

Use 1:2. Require a complete head-to-toe character, natural standing pose, shoulder-height/eye-level camera, and a minimal pure-white background. Keep both reference files and the aspect ratio fixed while changing the character-description variable.

### 3. Apply the head-quality gate

After selecting a viable full body, inspect the head at useful zoom.

- Treat facial legibility as a hard gate, not a preference. Both eyes, the brow/eye spacing, the nose bridge and tip, the mouth or mustache shape, the jaw/cheek contour, and the hairline must be simultaneously readable at useful zoom. Dramatic chiaroscuro is allowed only when it sculpts these landmarks rather than erasing them.
- If the head is clear, structurally reasonable, identity-distinctive, and fits the role description, skip separate head generation.
- If the head is too small, blurred, malformed, cropped, generic, insufficiently descriptive, or has a large shadow mass that hides an eye or other identity landmarks, do not pass the gate. Generate separate head material with the same two MJ style references and 9:16, or explicitly route the face through local repair before identity lock.

Do not require the separate head to look like the face in the full-body image. Midjourney text generation cannot reliably reproduce the same person. Judge the head by role-description fit, structural quality, hairstyle silhouette, age, temperament, period, and usability as refinement material.

Never confuse the MJ head material with the later general-style portrait deliverable.

### 4. Plan MJ-stage refinement and lock identity

Use the full-body image as the source of body type, pose, outfit layers, shoes, accessories, color scheme, and silhouette. When a separate head is stronger, use it as a replacement or redraw reference without demanding raw-image facial consistency.

Route defects explicitly:

- Regenerate full body for major body, pose, costume, role, or style failure.
- Generate or regenerate head material for an otherwise good full body with an unusable head.
- Refine locally for background debris, fake text/signatures, unwanted objects, silhouette joins, hands, feet, shoes, clothing borders, and excessive fragmented details.
- Treat a hand hidden behind the back as a pose defect. Prefer an otherwise comparable candidate with both arms and hands visible. Accept the hidden-hand candidate only when its body type, head-to-body proportion, face, or role fit is materially stronger; in that case, repair the pose with Image 2 before producing the character card.
- Accept directly when the full body and head are already clear and usable.

Do not declare identity lock while the face is still ambiguous. If the raw full-body face fails the legibility gate, combine the chosen body with approved head material or locally repair/re-light the face until the resulting MJ-stage refined full body has a readable, distinctive face.

Treat that refined full body as the first identity lock. Preserve an identity-anchor crop of its final face when the full-body scale is too small for reliable comparison. The crop must come from the same locked image or the exact face composited into it; an unrelated raw MJ head is not a valid downstream identity anchor. Downstream identity consistency begins here, not between the two raw MJ generations.

### 5. Produce downstream assets

Use `assets/general-fullbody-style-reference.png` only as the target style reference when converting the locked MJ-stage full body. Reference order for identity-sensitive conversion is: locked MJ full body first, its same-source face identity-anchor crop second when needed, and the general full-body style reference last. Explicitly treat the first two as identity/design sources and the last as style-only.

The conversion must preserve person-specific facial geometry, not merely demographic labels. Compare face shape and forehead, eye/brow spacing, nose silhouette, mouth/mustache shape, jaw/cheek contour, ears, hairline, and asymmetries between the MJ identity lock and the converted full body. If the conversion invents a cleaner or more generic face, changes apparent age, or retains only broad traits such as “older man with side-parted hair and mustache,” reject it and return to the conversion stage.

Before creating the character card, make sure the locked general-style full body shows both arms naturally lowered and both hands completely visible. A hand may not remain behind the back or hidden by the torso. Preserve the selected character's body type, head-to-body ratio, face, clothing, accessories, and palette while correcting only the arm/hand pose.

Then produce only the assets required by the selected route:

1. General-style character card, 16:9, for every role that needs an independent character asset.
2. General-style portrait, 4:5, only for important, recurring, UI-present, or explicit close-up roles. Minor roles do not receive a portrait by default. Use `assets/general-portrait-style-reference.png` only as the portrait style reference.
3. Black-white-red character card, 16:9, only for an explicitly animation-bound role. Use `assets/black-white-red-style-reference.jpg` only as the target style reference. Preserve the rules below for that conditional branch even though it is excluded from standard production.

Before accepting any final asset, verify its actual pixel ratio first, then apply the matching style library and structural gates from `references/style-self-check.md`. A wrong ratio is an automatic failure and must not proceed to subjective style review.

For a formal 2K/4K general-style character card, prefer the modular workflow in `references/modular-character-card.md`: generate and approve each required view as an independent image, preserve every approved module, then use `scripts/compose_character_card.py` for deterministic assembly on an exact 16:9 white canvas. Do not ask an image model to redraw the approved modules during final assembly. A one-pass character-card generation remains acceptable for drafts or when the user explicitly chooses speed over module-level control.

Require three complete and consistently scaled full-body modules: front, strict left side, and back. Normalize their trimmed subjects to one shared height so head tops and heel baselines match exactly, then visually verify shoulder, waist, knee, and coat/garment construction lines. Do not preserve unequal source-pixel sizes or bottom-align them with an unused blank strip above. Every full-body view is a prop-free design reference: both hands must be empty and naturally lowered, and no portable prop may touch, overlap, hang from, or be carried by any character body. Require three neutral head modules: front, strict right side, and back. Require one worn-shoe close-up showing the character's lower trouser legs, ankles, and both feet wearing the approved shoes, plus zero to three approved, identity-relevant accessory, portable-prop, or construction details. Reject missing required angles, inconsistent module identity or design, misaligned view scale, unexplained layout voids, meaningless fabric crops used as filler, any non-empty hand, and any prop attached to or overlapping a full-body view.

Treat clothing-fold language, edge hierarchy, material response, and ink rhythm as formal delivery gates, not optional polish. NDC general-style garments use a small number of decisive angular fold wedges at load points, hard structural turns, broad quiet dark masses, and short controlled tonal bridges inside larger planes. Reject long continuously blended or airbrushed cloth, rounded melted folds, decorative micro-wrinkles, or generic glossy 3D shading. Ink weight is selective rather than uniformly heavy: focal silhouette turns, occlusions, and load-bearing corners may be bold; long garment edges are medium or fine and tapered; internal folds may be finer, broken, or carried by adjacent value blocks. Require visible swell, taper, breaks, and decisive endings, but do not force every edge to the same comic-outline weight. Hair remains grouped into large directional masses with a few broad ribbon-like marks and no individual-strand rendering. Treat finish by material: cloth and most skin planes stay matte, while approved polished leather, metal, jewelry, and badges may use compact sharp highlights. When the user supplies a hue-adjusted approved composite, treat it as the color authority: style repair may change fold edges and ink treatment only, while preserving its hue, palette, identity, design, and all already approved modules.

For an explicitly triggered black-white-red card, keep black, white, and red unmistakably dominant. Do not restore normal or general-style skin color. Skin may carry only a barely perceptible near-grayscale warm gray-brown or muted sepia bias, substantially less saturated than the general-style card. Use that faint hue only within skin planes while retaining the graphic black-white structure. Avoid both extremes: broad pure-white skin highlights and visibly brown/orange natural skin.

Keep red as a small, spatially purposeful signal accent: favor an asymmetric shadow-side rim, local separation light, or an identity-bearing tie, emblem, eye, or accessory. Reject an automatic full red outline around every edge, large red background blocks, red page borders, broad red floor shapes, or large red garment panels unless the approved source character explicitly requires them or the user explicitly selects the minimalist poster branch. Preserve low-contrast internal facets inside near-black garments instead of flattening them into featureless silhouettes.

Use the general-style character card as the identity source for the portrait and black-white-red card. Do not use the raw MJ head as the official portrait identity source.

For portraits, treat the portrait-style reference as style-only. The portrait branch may use faceted values and short directional dry-brush marks to carry form, so an extremely heavy outer contour is not a universal pass condition. Keep hard structural turns and controlled short tonal bridges, reject smooth airbrushing, and reject horizontal extension bands, duplicated background strips, or cutout seams as generation artifacts. If the reference subject changes the character's sex, age, face, hairstyle, or costume identity, reject that result immediately and retry with the approved character card as the only image reference while reproducing the portrait style in text.

For existing-character state variants, keep the approved general-style character card as the identity source. Change only the requested state, expression, action, damage, prop, costume difference, or scene condition. Preserve unrequested facial, body, costume, palette, and style features.

## Review order

For MJ full-body candidates, review in this order:

1. Complete body, usable pose, and stable anatomy.
   Prefer two naturally lowered arms with visible hands; a hand behind the back is a repairable but meaningful pose penalty. In a strict orthographic side view, the far hand may overlap naturally, but the arm may not be posed behind the back.
2. Role, age, period, profession, and costume match.
3. NDC style formed by both MJ references.
4. Body proportion, silhouette, garment layers, shoes, and required accessories.
5. Head-quality gate.
6. Repairable local defects.

For downstream assets, verify the actual ratio, then the identity locked after MJ refinement, layout, anatomy, and target style. Use the matching self-check library as a group rather than choosing one convenient example. Do not retroactively reject a character because the two raw MJ faces differ.

For every style judgment, follow the full-image plus complete-local-coverage protocol. Sampling only the face, hands, folds, or another preferred region is insufficient; semantic crops may supplement but never replace the overlap-safe grid. Report stable group-wide traits separately from branch traits, minority tendencies, and artifacts.

Never mark an identity-sensitive asset as passed from category resemblance alone. “Same age, same hairstyle, same mustache, same coat” is insufficient if the person-specific eye, nose, mouth, cheek/jaw, ear, or hairline geometry has drifted.

## Output contract

When preparing a full workflow, return these sections in order:

1. `角色纯视觉设定`
2. `MJ 全身提示词` with Chinese and English versions
3. `MJ 参数与参考图清单`
4. `头部质量闸门`
5. `MJ 头部提示词` only when the gate fails, or mark it as skipped
6. `MJ 素材精修任务单`
7. `MJ 身份锁与同源面部锚点`
8. `通用风格全身转绘提示词`
9. `通用风格角色卡模块提示词与拼版清单`
10. `通用风格肖像提示词` only when the portrait branch is required; otherwise mark it as skipped with the route reason
11. `黑白红风格角色卡提示词` only when animation production explicitly triggers it; otherwise mark it as retained but not generated
12. `比例、身份、结构与风格自检`
13. `验收与返工路由`

For the Image 2 fast path, return instead:

1. `生产路由与理由`
2. `参考图顺序`
3. `Image 2 可复制提示词`
4. `身份与风格锁定项`
5. `验收与返工路由`

Put each user-copyable prompt in its own fenced block. Keep operator notes outside prompt blocks. State the reference-image order immediately before each prompt.

When critiquing supplied images, report each issue as:

`问题 | 严重度 | 是否重生 | 推荐处理阶段/工具 | 理由`

Distinguish user-confirmed rules from case-derived judgments whenever a new conclusion is involved.
