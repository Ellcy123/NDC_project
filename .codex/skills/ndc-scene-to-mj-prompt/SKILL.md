---
name: ndc-scene-to-mj-prompt
description: "Convert NDC game-scene requirements, narrative context, approved art examples, and local references into character-free Midjourney background prompts plus a structured production handoff. Use when the user asks to整理场景美术需求、写或修改 MJ 场景提示词、生成主要探索场景、生成剧情推进场景、规划 16:10 或横向探索画幅、分析人物比例或参考图、拆分底图与证据图层、规划昼夜版本，或为后续 Midjourney 与 Photoshop/Firefly 制作准备 Prompt＋需求。 This skill is prompt-only: do not open Midjourney, upload files, submit jobs, or edit images."
---

# NDC Scene to MJ Prompt

Produce a self-contained `ndc-mj-scene/v3` handoff containing the required view set, one exact prompt per view, the empty-background and layer contract, canvas/postprocess plan, and shared audit requirements. Keep prompting, Midjourney operation, and Photoshop finishing separate.

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

Also classify delivery use:

- `primary_exploration`: a main in-game exploration background that must support horizontal mouse panning and therefore needs additional width.
- `story_progression`: a background used only to advance dialogue, exposition, or a fixed narrative beat; generate in MJ at `2:1`, then finish at `16:10` after generation.

Do not assume these classifications from filenames. If gameplay use is unclear and changes the canvas plan, ask one focused question.

If the source is ambiguous and the classification would change the number of Midjourney jobs, ask one focused question. Do not infer `exploration` merely because ordinary furniture or decoration is visible.

Use exactly this view set:

- For `exploration`, output exactly one `eye_level` view prompt. Lock it to an eye-level three-point-perspective composition, camera optical center `1.7–1.8 meters` above the floor, and the horizon at the upper third of the image. This is a hard project rule. Do not add frontal, oblique, overhead, or alternative-view prompts.
- For `non_exploration`, output exactly three independent view prompts: `frontal`, `oblique`, and `overhead_45`. The frontal view is predominantly straight-on; the oblique view uses the left or right side that best exposes the source-supported architecture; `overhead_45` means the camera looks downward at approximately 45 degrees, not a 45-degree horizontal rotation. Derive the exact perspective and camera placement for each view from the source instead of copying the exploration camera lock.

All prompts in a view set must describe the same scene facts, architecture, core objects, time, lighting state, exclusions, and rendering language. Change only the camera position and the depth/lateral relationships that genuinely change with that camera. Never combine multiple views into one image or ask Midjourney for a contact sheet.

## Plan canvas and Photoshop finishing

- For every scene and every view, fix Midjourney generation at `2:1`. Scene purpose never changes the MJ generation ratio.
- For `story_progression`, set `canvas_plan.post_mj_operation: crop_or_reframe_to_16_10` and plan a post-MJ crop/reframe from the `2:1` base to the standard `16:10` delivery frame. Protect all required content inside `canvas_plan.crop_safe_area`.
- For `primary_exploration`, keep the MJ base at `2:1`, protect the central gameplay-safe area, and plan any additional left/right continuation with Photoshop Firefly Generative Fill after generation. Record the final delivery width as unresolved until the game UI or delivery specification supplies it.
- Do not use Midjourney to create separate day/night geometry by default. Lock composition and space, then hand the accepted master background to Photoshop for manual relighting and color changes.

## Reduce the brief and describe the scene

Before drafting the Midjourney paragraphs, produce these intermediate artifacts in the handoff:

1. `visual_brief`: retain only visually actionable facts such as time, interior or exterior, architectural function, empty-environment state, required objects, prohibited subjects, and source-supported atmosphere. Remove dialogue, character blocking, narrative explanation, and facts that cannot be shown; convert relevant character activity into environmental traces under the character-free rules below.
2. One `scene_description` inside each `view_prompts[]` entry: describe that view from highest to lowest importance. Separate camera, foreground, middle ground, background, left-center-right distribution, architecture relationships, lighting, and optional decoration.

For a new scene, construct each required view from the requirement contract. For a redraw or viewpoint conversion, first analyze the source image's composition, geometry, palette, and lighting; then state the requested horizontal rotation direction and approximate degrees, elevation change or eye-level/bird's-eye/low-angle view, and reconstruct foreground-middle-background relationships separately for every required view. Do not pretend that geometry hidden by the source image is known; mark unsupported reconstruction as an assumption.

Create an explicit camera and spatial plan for every required view:

- shot scale and view direction;
- two-point or other source-supported perspective;
- camera height when it affects visible surfaces or gameplay readability;
- horizon placement;
- focal-length feel and focus/readability target when they materially affect distortion or object readability;
- foreground, middle ground, and background anchors;
- left, center, and right placement of major masses;
- connection, separation, overlap, occlusion, route, and relative scale among doors, windows, walls, counters, stairs, corridors, and core objects;
- architectural calibration landmarks such as wainscot tops, tabletops, window sills, rails, or stair landings that make the intended camera height visually testable.

Validate scene scale without character language in the prompt. Use architecture such as a roughly 2-meter door, 0.9–1.0-meter handrail, 0.72–0.76-meter desk, wainscot, window sill, or stair riser as scale proxies. A temporary neutral silhouette may be overlaid after generation for review only; never upload it as an MJ reference, mention it in positive prompt text, or retain it in the final background.

Do not force arbitrary camera numbers except for the exploration-scene project lock. For non-exploration views, use source-provided values first; otherwise choose a defensible range and record it as an assumption. A generic phrase such as `eye-level view` is insufficient when a wrong camera height would hide a required surface or collapse an architectural relationship.

## Enforce character-free scene backgrounds

Treat every NDC scene image as an empty environment background. Never include people, named characters, crowds, bodies, faces, human figures, or silhouettes as positive scene content in `prompt_en` or `prompt_zh`.

When a source document describes character positions or actions, retain that wording only in `original_requirement`. Translate it into environmental traces and spatial readability for the normalized requirements and prompts. For example, turn a guarded doorway into physical barricades and rope stanchions, a clerk moving files into unattended archive carts and stacked document boxes, and characters waiting by a side door into a clearly visible secondary entrance and an unobstructed route. Never copy character names, occupations, poses, blocking, or actions into the generated prompt.

For every scene handoff, add `empty environment with no visible characters` under `normalized_requirement.hard` and list `people, named characters, crowds, human figures, faces, bodies, silhouettes` under `normalized_requirement.must_not_have`. Keep those tokens out of the positive description. Encode the English submission constraint only once in a dedicated final `--no people, person, humans, characters, crowds, figures, faces, bodies, silhouettes` parameter; record the same constraint as review text in `prompt_zh`.

Reject portrait and character references for scene content, composition, environment, or identity. The only exception is a separately controlled Style Reference workflow; record leakage risk and keep the no-character requirement hard. Remove temporary scale silhouettes before upload.

## Separate the background from mutable layers

Only permanent environmental storytelling may be baked into the base background. Classify every requested object into:

- `base_environment_narrative`: permanent architecture, wear, fixed furnishings, and lasting environmental storytelling allowed in the background;
- `interaction_closeup`: evidence revealed in a close-up;
- `scan_overlay`: oil, imprint, residue, or analysis visualization;
- `collectible_layer`: any item the player can pick up;
- `transient_story_layer`: characters, bodies, temporary props, Loop-specific objects, fire/state effects that may disappear, and other removable content.

Never place the last four categories in the generated base prompt. Preserve their required location and scale in the handoff so later layers can align with the background.

## Build the requirement contract

Retain the original requirement in the handoff, then normalize it into three levels:

- `hard`: core composition, scene identity, camera orientation when specified, gameplay-critical architecture, narrative-critical spatial relationships, canvas use, the universal empty-background requirement, and facts whose change would break the scene.
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
- Keep character tokens out of positive prose and include them only once in the dedicated final `--no people, person, humans, characters, crowds, figures, faces, bodies, silhouettes` parameter.
- Do not include `/imagine prompt:`.
- Do not append a model-version parameter to any prompt text. Set `parameters.model: "latest"` for NDC scenes by default, unless the user explicitly requests a specific model for the current job.
- Append `--ar 2:1` exactly once to every Midjourney scene prompt. Never change the MJ ratio for story or exploration use. Record post-MJ `16:10` cropping or Photoshop Firefly horizontal extension only in `canvas_plan`.
- Treat exact counts as approximate unless the requirement contract marks them hard.

Also provide a faithful Chinese counterpart for every view. Each view's English paragraph is the submission source of truth for its own Midjourney job.

## Self-review before handoff

Verify that:

1. `scene.mode` is explicit and the view count is exactly one for `exploration` or exactly three for `non_exploration`.
2. Every hard requirement has a corresponding clause in every view prompt where it remains visible.
3. No prompt clause contradicts the original requirement.
4. Core objects are earlier and more concrete than decorative details.
5. Every exploration prompt states eye-level three-point perspective, camera optical center `1.7–1.8 meters` above the floor, and a horizon at the upper third; no alternative view is present.
6. Every non-exploration handoff contains `frontal`, `oblique`, and `overhead_45`, and the overhead prompt clearly describes an approximately 45-degree downward view.
7. Camera height, horizon, perspective, focal-length feel, and focus/readability choices are source-supported, project-locked, or recorded as assumptions.
8. Foreground-middle-background and left-center-right relations are rebuilt for every view and explicit for every architecture-defining mass.
9. Architectural calibration landmarks make any critical camera-height requirement visually testable.
10. Soft and flexible details are not phrased with unnecessary exactness.
11. The reference plan does not introduce unwanted subjects.
12. Every `prompt_en` and `prompt_zh` contains no character name, human action, pose, crowd, figure, face, body, or silhouette as positive content.
13. `normalized_requirement.hard`, `must_not_have`, and every prompt counterpart enforce an empty environment with no visible characters; `prompt_en` carries character tokens only in its final dedicated `--no` parameter.
14. Only `base_environment_narrative` content is baked into the background; collectible, transient, close-up, and scan content is kept in separate layers.
15. Scale is validated through architecture or a non-submitted review overlay, never through positive character language or an uploaded silhouette.
16. Every prompt uses fixed `--ar 2:1`; `story_progression` includes a post-MJ `16:10` crop-safe plan, while `primary_exploration` includes a central safe area and any post-MJ Photoshop Firefly left/right extension plan.
17. Day/night variants share one geometry-locked master and default to Photoshop manual relighting.
18. Shared scene facts do not drift between view prompts.
19. `must_not_have` is concise and scene-specific beyond the mandatory no-character exclusions.
20. Parameters are separate from requirements, default `model` to `latest`, and keep model-version syntax out of every prompt text.

If a hard ambiguity would materially change the image, ask one focused question. Otherwise state the assumption and continue.

## Return the handoff

Return the exact field structure in [handoff schema](references/handoff-schema.md). The primary payloads are:

1. `scene.mode` plus `view_prompts[]`: how many independent Midjourney jobs are required and what each must generate.
2. `original_requirement` plus `normalized_requirement`: what the operator must audit.
3. `visual_brief` plus each view's `scene_description` and `camera_contract`: how the visual facts, camera, depth layers, and architecture relationships were derived and how they must be reviewed.

Reference roles, parameters, and review priorities are supporting execution data. Do not operate a browser or claim that an image was generated.
