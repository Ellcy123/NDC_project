---
name: ndc-scene-to-mj-prompt
description: "Prepare character-free NDC scene requirements, camera layouts and Midjourney prompts for native MJ image delivery. Use for 场景需求拆解、MJ场景提示词、探索或剧情场景构图、空间布局、便于后续人工修图的底图规划. Defer gameplay props; allow sparse period ambient dressing. Prompt-only: do not open Midjourney, submit jobs or edit images."
---

# NDC Scene to MJ Prompt

Produce a self-contained `ndc-mj-scene/v4` handoff containing the required view set, exact prompts, camera/spatial contracts, deferred-prop boundary and MJ delivery checks. This chain ends at native MJ image delivery. Retouching, expansion, relighting and prop production are outside this workflow.

## Mandatory stage-end visual self-check gate

Every art-production stage executed by this Skill must end with an explicit visual self-check item before its output may be accepted or passed to Midjourney production. This includes visual-reference intake and role assignment, source-image/viewpoint analysis, style extraction, camera/spatial planning from art, prompt/handoff review against visual inputs, and acceptance of any returned scene image used to revise the handoff. Inspect every current visual input as a whole at `100%` and every applicable local region at nearest-neighbor `200%` or through complete original-pixel tiles. Compare the handoff against the approved visual authority and every applicable camera, spatial, composition, deferred-prop, framing, style, texture, reference-leakage, and character-free requirement.

Write one current `ndc-stage-visual-self-check/v1` record for every executed stage that consumes or accepts a visual artifact. It must bind the stage ID, reviewer/date, visual input paths plus SHA-256, any file output path plus SHA-256, the inspected `whole_100` and `local_200_or_tiles` views, every applicable criterion with an explicit finding and `PASS`/`FAIL`/`NOT_CHECKED`, the overall `visual_check_status`, and the responsible rework stage when blocked. Missing record, missing visual-detection item, stale hash, missing required view, `FAIL`, or `NOT_CHECKED` is `STAGE_VISUAL_SELF_CHECK_GATE: BLOCKED`: do not mark the handoff visually cleared or use it to authorize an image-producing stage. Dimensions, file existence, schema validation, or absence of a detected error cannot write visual `PASS`.

After a block, return to the responsible analysis/handoff stage, perform the missing inspection and correction, then repeat the visual self-check. Release a visually cleared handoff only after the current visual inputs and current handoff have a passing record. When the stage writes files, run `python D:/Codex/NDC/scripts/validate-ndc-stage-visual-self-check.py --record <visual-review.json> --artifact <current-handoff-or-reviewed-output>`; a nonzero result is a hard stop. A truly text-only draft with no visual input may still be returned as `DRAFT_NOT_VISUALLY_CLEARED`, but it cannot be described as a passed visual asset or authorize downstream image production until the first applicable visual stage records and passes the check.

## Read the relevant references

1. Read [prompt rules](references/prompt-rules.md) before drafting any prompt.
2. Read [handoff schema](references/handoff-schema.md) before returning the result.
3. Read [style analysis protocol](references/style-analysis-protocol.md) whenever analyzing, comparing, or approving style references or generated scene style.
4. Inspect every user-supplied reference image before assigning it a role. Treat `assets/approved-courthouse-scene-style.png` as a calibration example only, never as a universal NDC style reference.

<!-- NDC_TEXTURE_COHERENCE_MODULE:BEGIN -->
For every handoff, also build the mandatory `texture_contract` in [handoff schema](references/handoff-schema.md) from [prompt rules](references/prompt-rules.md). The approved references and current rendering-language clauses remain the style authority. Texture control may distribute and limit non-semantic micro-detail, but it may not flatten, modernize, smooth, photorealize, simplify, or otherwise restyle the scene. Do not promote a reference artifact into executable style language.
<!-- NDC_TEXTURE_COHERENCE_MODULE:END -->

Reference inspection has two mandatory levels: review the complete image first, then run `scripts/make_style_review_tiles.py` and inspect every overlap-safe original-resolution tile. Do not infer fine brushwork, texture, line endings, material treatment, or edge behavior from a downscaled 4K/8K overview. A completed style analysis must report `whole_image_checked: true`, `local_tile_coverage_complete: true`, image-entry and deduplicated counts, tile count, stable traits, branch traits, minority traits, and artifacts.

Do not collapse the NDC scene references into a universal “jewel tones plus bold black contour” formula. The stable scene core is compressed large-scale shape design, deep grouped shadow masses, a controlled hard-soft edge hierarchy, restrained charcoal/brown-gray/olive-gray bases, limited warm focal accents, and scale-aware matte grain or directional texture. Treat saturation, thick-paint language, and bold calligraphic contours as conditional branches only when both whole-image and local-tile evidence support them for the current scene. Use the character-graphic static reference for shape compression and edge economy, the city-rain static reference for weather texture and atmospheric depth, and the approved courthouse example for thin architectural line hierarchy, subdued interior color grouping, and hard geometry with soft light shafts.

## Resolve the source requirement

Use this source order:

1. Current user instructions and corrections.
2. The scene's current NDC design document or `ArtRequirement`.
3. Approved art references and previously accepted prompts.
4. General period knowledge and reasonable visual inference.

Do not let historical examples override current scene facts. Preserve unresolved ambiguity instead of inventing gameplay-critical geometry or objects. Keep individual scene constraints in that task's requirement, handoff and review records; do not promote a test case's camera placement, architecture, furnishings or state into shared Skill defaults.

## Classify the scene and select the view set

Classify the scene before designing any camera:

- `exploration`: the player must search, inspect, or collect one or more props or evidence items in the scene.
- `non_exploration`: no searchable evidence or prop interaction is required in the scene.

Also classify delivery use:

- `primary_exploration`: a main in-game exploration background. Record any known horizontal mouse-panning constraint as framing context; generate and deliver the native MJ frame at `2:1`.
- `story_progression`: a background used for dialogue or a fixed narrative beat. Generate in MJ at `2:1`; any known later display crop is composition context only.

Do not assume these classifications from filenames or visible ordinary furniture/decoration. If source ambiguity would change the number of Midjourney jobs, ask one focused question; an unknown later display width alone does not require clarification.

Use exactly this view set:

- For `exploration`, output exactly one `eye_level` view prompt. Lock it to an eye-level three-point-perspective composition, camera optical center `1.7–1.8 meters` above the floor, and the horizon at the upper third of the image. This is a hard project rule. Do not add frontal, oblique, overhead, or alternative-view prompts.
- For `non_exploration`, output exactly three independent view prompts: `frontal`, `oblique`, and `overhead_45`. The frontal view is predominantly straight-on; the oblique view uses the left or right side that best exposes the source-supported architecture; `overhead_45` means the camera looks downward at approximately 45 degrees, not a 45-degree horizontal rotation. Derive the exact perspective and camera placement for each view from the source instead of copying the exploration camera lock.

All prompts in a view set must describe the same scene facts, architecture, core objects, time, lighting state, exclusions, and rendering language. Change only the camera position and the depth/lateral relationships that genuinely change with that camera. Never combine multiple views into one image or ask Midjourney for a contact sheet.

## Plan the MJ frame

- Every view generates at `2:1`; the deliverable is the original MJ image at its actual downloaded resolution.
- Protect the current scene's required focal elements, routes and main masses from accidental edge cuts. Keep broad surfaces and depth transitions readable for later manual editing.
- If a later display crop or horizontal pan is already specified, record its safe composition region in `framing_context`. An unknown final game width does not block MJ generation or delivery.
- Do not require a crop, extension, Photoshop plan, relighting plan, evidence placement map or Unity import. Do not generate separate day/night geometries unless explicitly requested; produce the requested master state only.

## Reduce the brief and describe the scene

Before drafting the Midjourney paragraphs, produce these intermediate artifacts in the handoff:

1. `visual_brief`: retain only visually actionable facts such as time, interior or exterior, architectural function, empty-environment state, architecture and room-defining major furniture, prohibited subjects, and source-supported atmosphere. Remove dialogue, character blocking, narrative explanation, and facts that cannot be shown; retain only source-supported architectural or broad surface states; do not replace omitted character actions with invented props.
2. One `scene_description` inside each `view_prompts[]` entry: describe that view from highest to lowest importance. Separate camera, foreground, middle ground, background, left-center-right distribution, architecture relationships, lighting, and quiet supporting planes. A short low-priority ambient dressing cue is allowed; avoid exhaustive inventories.

For a new scene, construct each required view from the requirement contract. For a redraw or viewpoint conversion, first analyze the source image's composition, geometry, palette, and lighting; then state the requested horizontal rotation direction and approximate degrees, elevation change or eye-level/bird's-eye/low-angle view, and reconstruct foreground-middle-background relationships separately for every required view. Do not pretend that geometry hidden by the source image is known; mark unsupported reconstruction as an assumption.

Create an explicit camera and spatial plan for every required view:

- shot scale and view direction;
- two-point or other source-supported perspective;
- camera height when it affects visible surfaces or gameplay readability;
- horizon placement;
- focal-length feel and focus/readability target when they materially affect distortion or object readability;
- foreground, middle ground, and background anchors;
- left, center, and right placement of major masses;
- connection, separation, overlap, occlusion, route, and relative scale among doors, windows, walls, counters, stairs, corridors, and room-defining masses;
- architectural calibration landmarks such as wainscot tops, tabletops, window sills, rails, or stair landings that make the intended camera height visually testable.

Validate scene scale without character language in the prompt. Use architecture such as a roughly 2-meter door, 0.9–1.0-meter handrail, 0.72–0.76-meter desk, wainscot, window sill, or stair riser as scale proxies. A temporary neutral silhouette may be overlaid after generation for review only; never upload it as an MJ reference, mention it in positive prompt text, or retain it in the final background.

Do not force arbitrary camera numbers except for the exploration-scene project lock. For non-exploration views, use source-provided values first; otherwise choose a defensible range and record it as an assumption. A generic phrase such as `eye-level view` is insufficient when a wrong camera height would hide a required surface or collapse an architectural relationship.

## Enforce character-free scene backgrounds

Treat every NDC scene image as an empty environment background. Never include people, named characters, crowds, bodies, faces, human figures, or silhouettes as positive scene content in `prompt_en` or `prompt_zh`.

Keep character names, blocking and actions only in `original_requirement`. Omit them from submitted descriptions. Existing broad architectural or surface states may remain when they define the requested scene state; do not translate actions into extra props, footprints or evidence.

For every scene handoff, add `empty environment with no visible characters` under `normalized_requirement.hard` and list `people, named characters, crowds, human figures, faces, bodies, silhouettes` under `normalized_requirement.must_not_have`. Keep those tokens out of the positive description. Encode the English submission constraint only once in a dedicated final `--no people, person, humans, characters, crowds, figures, faces, bodies, silhouettes` parameter; record the same constraint as review text in `prompt_zh`.

Reject portrait and character references for scene content, composition, environment, or identity. The only exception is a separately controlled Style Reference workflow; record leakage risk and keep the no-character requirement hard. Remove temporary scale silhouettes before upload.

## Defer props before drafting

Default `prop_policy.mode: defer_gameplay_props`. Exclude collectible evidence **and all specified gameplay, interaction or environmental-narrative evidence objects** from positive MJ prompts. Permanent/non-collectible status does not exempt a game-defined environmental-narrative object from deferral. Small ordinary non-interactive set dressing may be added freely when period-appropriate, sparse and subordinate to the room layout. It must not reproduce a deferred clue or imply a gameplay hotspot.

Retain architecture, openings, structural fixtures and the minimum major masses needed to recognize and lay out the current scene. Classify by spatial function, not merely size or permanence. If a large object only carries a clue, defer it too. Allow a few period-appropriate ambient details without prescribing individual locations; stop before they obscure routes or force the spatial layout to change. Keep only source-supported broad material and surface conditions for the requested master state; do not invent story-specific marks or objects.

Record source-mentioned deferred items briefly under `prop_policy.deferred_from_source`; this is provenance, not a placement task. Do not require per-prop positions, scale, empty sockets, evidence tables, container chains or specially cleared prop patches. Missing deferred items never fails an MJ candidate. Review and reject invented clutter only when it obstructs the route, dominates composition or makes later editing substantially harder. A user-explicit current MJ inclusion is a scoped exception, recorded with its reason.

## Build the requirement contract

Retain the original requirement in the handoff, then normalize it into three levels:

- `hard`: core composition, scene identity, camera orientation when specified, gameplay-critical architecture, narrative-critical spatial relationships, requested MJ frame, the universal empty-background requirement, and facts whose change would break the scene.
- `soft`: important period cues, major furniture types, approximate mass distribution, lighting direction, material family and environmental readability.
- `flexible`: minor palette shifts and harmless architectural detail. Game-defined props are outside the MJ requirement; sparse non-interactive ambient dressing is flexible and may be generated freely.

Never make a number hard merely because it appears in source prose. Upgrade an exact count only when the count itself affects a route, interaction, clue, evidence, or narrative logic. For example, require `high clerestory windows` as soft; do not require exactly four to six unless their number matters to gameplay.

List every prohibited element separately under `must_not_have`. Distinguish a real content prohibition from a stylistic preference.

## Plan the image references

Assign each candidate reference one role:

- `style`: palette, line, texture, and rendering language only.
- `environment`: architecture, period objects, and material vocabulary.
- `composition`: camera, framing, depth, and large-mass placement.
- `identity`: a uniquely identifiable architectural or room-defining element explicitly intended to appear; do not attach deferred prop identity references.
- `reject`: semantically conflicts with the target scene or is likely to leak an unwanted subject.

Reject or downgrade incompatible references before trying to negate their content in text. A portrait used on an empty interior can leak a person; a city exterior can leak skyline or windows. Negative wording is not a reliable cure for strong reference semantics.

Before extracting palette, line, texture, or rendering language from a `style` reference, complete the full-image and local-tile protocol. Separate scene-wide composition from local rendering behavior, and separate stable cross-reference traits from material-specific handling or single-image artifacts.

## Draft the view prompts

Write one copy-ready English paragraph for each required view in this order:

`camera position and view direction → scene identity and period → architecture and major mass relationships → lighting and palette → rendering language and controlled texture → parameters`

<!-- NDC_TEXTURE_COHERENCE_MODULE:BEGIN -->
Implement the shared `texture_contract` inside the graphic-treatment portion of every view prompt. Use positive structural language—compressed large shapes, grouped shadows, directional and scale-aware material texture, quiet planes, and focal detail hierarchy—rather than a universal negative block. Keep the contract invariant across the view set. Scene-specific exclusions for recurrent texture failures remain optional and concise.
<!-- NDC_TEXTURE_COHERENCE_MODULE:END -->

Apply these rules:

- Front-load the controlling camera and large spatial masses. Prefer a compact prompt to a detailed inventory.
- Encode that view's camera and spatial plan concretely enough to audit: specify the perspective, important camera-height or horizon constraint, depth order, major left-center-right placement, and the relationships that must remain visible.
- Describe where a core object is, how large it reads, and what it relates to.
- Use concrete period construction and material vocabulary instead of the vague word `vintage`.
- Keep one coherent visual language. Remove duplicated adjectives and contradictory style clauses.
- Use exclusions only for recurrent or damaging failures.
- Do not include character names, people, crowds, human actions, poses, faces, bodies, or silhouettes as positive prompt content.
- Keep character tokens out of positive prose and include them only once in the dedicated final `--no people, person, humans, characters, crowds, figures, faces, bodies, silhouettes` parameter.
- Do not include `/imagine prompt:`.
- Do not append a model-version parameter to any prompt text. Set `parameters.model: "latest"` for NDC scenes by default, unless the user explicitly requests a specific model for the current job.
- Append `--ar 2:1` exactly once to every Midjourney scene prompt. Never change the MJ ratio for story or exploration use. Record a known downstream framing constraint only in `framing_context`; do not turn it into a post-MJ task.
- Treat exact counts as approximate unless the requirement contract marks them hard.

Also provide a faithful Chinese counterpart for every view. Each view's English paragraph is the submission source of truth for its own Midjourney job.

## Final prompt and handoff check

Use the [handoff schema](references/handoff-schema.md). Confirm exact view count; camera and large-mass relationships; `--ar 2:1` once; no model flag; no positive character content; no deferred props, prop locations or postproduction steps. Every style clause needs inspected reference evidence. Keep `texture_contract` invariant across views and never flatten the approved rendering language to make editing easier.

Return the exact English prompt, faithful Chinese review counterpart, original requirement, camera/spatial contract, deferred-prop boundary, reference roles and native MJ delivery contract. If no actual images were generated, say so. Do not operate the browser from this prompt-only Skill.
