---
name: ndc-scene-to-mj-prompt
description: "Convert NDC game-scene requirements, narrative context, approved art examples, and local reference images into the required Midjourney view prompts plus a structured requirements handoff. Use when the user asks to整理场景美术需求、写或修改 MJ 场景提示词、生成探索场景单一平视搜证镜头、生成非探索场景正面/斜侧/45度俯视多视角、分析参考图用途、把 NDC 场景文档转成出图需求，或为后续 Midjourney 自动化准备 Prompt＋需求。 This skill is prompt-only: do not open Midjourney, upload files, submit jobs, or review generated grids."
---

# NDC Scene to MJ Prompt

Produce a self-contained `ndc-mj-scene/v2` handoff containing the required view set, one exact prompt per view, and the shared requirements that a later operator must audit against. Keep prompting and browser operation separate.

## Read the relevant references

1. Read [prompt rules](references/prompt-rules.md) before drafting any prompt.
2. Read [handoff schema](references/handoff-schema.md) before returning the result.
3. Inspect every user-supplied reference image before assigning it a role. Treat `assets/approved-courthouse-scene-style.png` as a calibration example only, never as a universal NDC style reference.

## Resolve the source requirement

Use this source order:

1. Current user instructions and corrections.
2. The scene's current NDC design document or `ArtRequirement`.
3. Approved art references and previously accepted prompts.
4. General period knowledge and reasonable visual inference.

Do not let historical examples override current scene facts. Preserve unresolved ambiguity instead of inventing gameplay-critical geometry or objects.

## Classify the scene and select the view set

Classify the scene before designing any camera:

- `exploration`: the player must search, inspect, or collect one or more props or evidence items in the scene.
- `non_exploration`: no searchable evidence or prop interaction is required in the scene.

If the source is ambiguous and the classification would change the number of Midjourney jobs, ask one focused question. Do not infer `exploration` merely because ordinary furniture or decoration is visible.

Use exactly this view set:

- For `exploration`, output exactly one `eye_level` view prompt. Lock it to an eye-level three-point-perspective composition aligned with a standing eye line, camera height `1.7–1.8 meters`, and the horizon at the upper third of the image. This is a hard project rule. Do not add frontal, oblique, overhead, or alternative-view prompts.
- For `non_exploration`, output exactly three independent view prompts: `frontal`, `oblique`, and `overhead_45`. The frontal view is predominantly straight-on; the oblique view uses the left or right side that best exposes the source-supported architecture; `overhead_45` means the camera looks downward at approximately 45 degrees, not a 45-degree horizontal rotation. Derive the exact perspective and camera placement for each view from the source instead of copying the exploration camera lock.

All prompts in a view set must describe the same scene facts, architecture, core objects, time, lighting state, exclusions, and rendering language. Change only the camera position and the depth/lateral relationships that genuinely change with that camera. Never combine multiple views into one image or ask Midjourney for a contact sheet.

## Reduce the brief and describe the scene

Before drafting the Midjourney paragraphs, produce these intermediate artifacts in the handoff:

1. `visual_brief`: retain only visually actionable facts such as time, interior or exterior, architectural function, empty-environment state, required objects, prohibited subjects, and source-supported atmosphere. Remove dialogue, character blocking, narrative explanation, and facts that cannot be shown; convert relevant character activity into environmental traces under the character-free rules below.
2. One `scene_description` inside each `view_prompts[]` entry: describe that view from highest to lowest importance. Separate camera, foreground, middle ground, background, left-center-right distribution, architecture relationships, lighting, and optional decoration.

For a new scene, construct each required view from the requirement contract. For a redraw or viewpoint conversion, first analyze the source image's composition, geometry, palette, and lighting; then state the requested horizontal rotation direction and approximate degrees, elevation change or eye-level/bird's-eye/low-angle view, and reconstruct foreground-middle-background relationships separately for every required view. Do not pretend that geometry hidden by the source image is known; mark unsupported reconstruction as an assumption.

Create an explicit camera and spatial plan for every required view:

- shot scale and view direction;
- one-point, two-point, or other justified perspective;
- camera height when it affects visible surfaces or gameplay readability;
- horizon placement;
- focal-length feel and depth-of-field target when they materially affect distortion or object readability;
- foreground, middle ground, and background anchors;
- left, center, and right placement of major masses;
- connection, separation, overlap, occlusion, route, and relative scale among doors, windows, walls, counters, stairs, corridors, and core objects;
- architectural calibration landmarks such as wainscot tops, tabletops, window sills, rails, or stair landings that make the intended camera height visually testable.

Do not force arbitrary camera numbers except for the exploration-scene project lock. For non-exploration views, use source-provided values first; otherwise choose a defensible range and record it as an assumption. A generic phrase such as `eye-level view` is insufficient when a wrong camera height would hide a required surface or collapse an architectural relationship.

## Enforce character-free scene backgrounds

Treat every NDC scene image as an empty environment background. Never include people, named characters, crowds, bodies, faces, human figures, or silhouettes in `prompt_en` or `prompt_zh`.

When a source document describes character positions or actions, retain that wording only in `original_requirement`. Translate it into environmental traces and spatial readability for the normalized requirements and prompts. For example, turn a guarded doorway into physical barricades and rope stanchions, a clerk moving files into unattended archive carts and stacked document boxes, and characters waiting by a side door into a clearly visible secondary entrance and an unobstructed route. Never copy character names, occupations, poses, blocking, or actions into the generated prompt.

For every scene handoff, add `empty environment with no visible characters` under `normalized_requirement.hard` and list `people, named characters, crowds, human figures, faces, bodies, silhouettes` under `normalized_requirement.must_not_have`. End both prompt counterparts with concise matching exclusions.

Reject portrait and character references for scene generation. The only exception is a separate operator-enforced Style Reference workflow that extracts style without treating the pictured person as content; record the leakage risk and keep the no-character requirement hard.

## Build the requirement contract

Retain the original requirement in the handoff, then normalize it into three levels:

- `hard`: core composition, scene identity, camera orientation when specified, gameplay- or evidence-critical objects, narrative-critical spatial relationships, the universal empty-environment requirement, and facts whose change would break the scene.
- `soft`: important period cues, object types, approximate distribution, lighting direction, material family, environmental readability, and secondary objects that should appear but may vary in count or exact shape.
- `flexible`: ornament, exact count of non-gameplay props, minor palette shifts, decorative placement, and incidental clutter.

Never make a number hard merely because it appears in source prose. Upgrade an exact count only when the count itself affects a route, interaction, clue, evidence, or narrative logic. For example, require `high clerestory windows` as soft; do not require exactly four to six unless their number matters to gameplay.

List every prohibited element separately under `must_not_have`. Distinguish a real content prohibition from a stylistic preference.

## Plan the image references

Assign each candidate reference one role:

- `style`: palette, line, texture, and rendering language only.
- `environment`: architecture, period objects, and material vocabulary.
- `composition`: camera, framing, depth, and large-mass placement.
- `identity`: a uniquely identifiable non-character object intended to appear.
- `reject`: semantically conflicts with the target scene or is likely to leak an unwanted subject.

Reject or downgrade incompatible references before trying to negate their content in text. A portrait used on an empty interior can leak a person; a city exterior can leak skyline or windows. Negative wording is not a reliable cure for strong reference semantics.

## Draft the view prompts

Write one copy-ready English paragraph for each required view in this order:

`scene identity and period → core composition and camera → hard objects and spatial relations → soft architecture and props → lighting and palette → graphic treatment → concise exclusions → parameters`

Apply these rules:

- Front-load composition and core objects.
- Encode that view's camera and spatial plan concretely enough to audit: specify the perspective, important camera-height or horizon constraint, depth order, major left-center-right placement, and the relationships that must remain visible.
- Describe where a core object is, how large it reads, and what it relates to.
- Use concrete period construction and props instead of the vague word `vintage`.
- Keep one coherent visual language. Remove duplicated adjectives and contradictory style clauses.
- Use exclusions only for recurrent or damaging failures.
- Do not include character names, people, crowds, human actions, poses, faces, bodies, or silhouettes as positive prompt content.
- Always include a concise no-character exclusion covering people, characters, crowds, human figures, faces, bodies, and silhouettes.
- Do not include `/imagine prompt:`.
- Do not append a model-version parameter such as `--v 8.1` to any prompt text. Set `parameters.model: "8.1"` for NDC scenes by default, unless the user explicitly requests another version for the current job.
- Default scene backgrounds to `--ar 2:1` only when the user or project source supplies no different aspect ratio.
- Treat exact counts as approximate unless the requirement contract marks them hard.

Also provide a faithful Chinese counterpart for every view. Each view's English paragraph is the submission source of truth for its own Midjourney job.

## Self-review before handoff

Verify that:

1. `scene.mode` is explicit and the view count is exactly one for `exploration` or exactly three for `non_exploration`.
2. Every hard requirement has a corresponding clause in every view prompt where it remains visible.
3. No prompt clause contradicts the original requirement.
4. Core objects are earlier and more concrete than decorative details.
5. Every exploration prompt states eye-level three-point perspective, `1.7–1.8 meters`, and a horizon at the upper third; no alternative view is present.
6. Every non-exploration handoff contains `frontal`, `oblique`, and `overhead_45`, and the overhead prompt clearly describes an approximately 45-degree downward view.
7. Camera height, horizon, perspective, and focal-length/depth-of-field choices are source-supported, project-locked, or recorded as assumptions.
8. Foreground-middle-background and left-center-right relations are rebuilt for every view and explicit for every architecture-defining mass.
9. Architectural calibration landmarks make any critical camera-height requirement visually testable.
10. Soft and flexible details are not phrased with unnecessary exactness.
11. The reference plan does not introduce unwanted subjects.
12. Every `prompt_en` and `prompt_zh` contains no character name, human action, pose, crowd, figure, face, body, or silhouette as positive content.
13. `normalized_requirement.hard`, `must_not_have`, and every prompt counterpart enforce an empty environment with no visible characters.
14. Shared scene facts do not drift between view prompts.
15. `must_not_have` is concise and scene-specific beyond the mandatory no-character exclusions.
16. Parameters are separate from requirements, default `model` to `8.1`, and keep model-version syntax out of every prompt text.

If a hard ambiguity would materially change the image, ask one focused question. Otherwise state the assumption and continue.

## Return the handoff

Return the exact field structure in [handoff schema](references/handoff-schema.md). The primary payloads are:

1. `scene.mode` plus `view_prompts[]`: how many independent Midjourney jobs are required and what each must generate.
2. `original_requirement` plus `normalized_requirement`: what the operator must audit.
3. `visual_brief` plus each view's `scene_description` and `camera_contract`: how the visual facts, camera, depth layers, and architecture relationships were derived and how they must be reviewed.

Reference roles, parameters, and review priorities are supporting execution data. Do not operate a browser or claim that an image was generated.
