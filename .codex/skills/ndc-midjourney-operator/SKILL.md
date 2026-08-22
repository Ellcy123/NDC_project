---
name: ndc-midjourney-operator
description: "Operate Midjourney for character-free NDC scene-background generation from an ndc-mj-scene/v3 handoff, then report the Photoshop/Firefly finishing plan. Use when the user asks to在 Midjourney 网页提交或生成 NDC 主要探索场景或剧情推进场景、上传双风格参考图、检查四宫格、按镜头/空间/空底图/证据分层审核、做有限轮次 Vary 或最小提示词修订，并交接 16:10、横向拓图或昼夜手动改光。 Use browser:control-in-app-browser for the web UI. Do not use for prompt-only requests or directly operate Photoshop."
---

# NDC Midjourney Operator

Submit, inspect, and iterate the complete required NDC base-background view set. Audit every result against the source, camera contract, empty-background rule, layer plan, canvas plan, and Photoshop finishing handoff.

## Read the relevant references

1. Read [handoff contract](references/handoff-contract.md) before accepting a job.
2. Read [review rubric](references/review-rubric.md) before judging a generated grid.
3. Read [operation loop](references/operation-loop.md) before opening or controlling Midjourney.
4. Use the `browser:control-in-app-browser` skill and follow its browser-selection, authentication, upload, and interaction rules exactly.

## Establish authorization and scope

- Treat an explicit request to `submit`, `generate`, `run`, `出图`, or `帮我在 MJ 做` as authorization for one complete initial view set using the supplied handoff: one Midjourney job for `exploration`, or three independent jobs for `non_exploration`.
- Do not submit when the user asks only to prepare, inspect, or revise a prompt.
- Ask before submission only when the prompt, references, or paid action materially differs from what the user authorized.
- Default to at most three generation rounds per required view including that view's initial grid. Ask before exceeding a view's handoff budget or starting an unrelated variation branch.
- Do not upscale, download, delete, publish, like, or make another unrelated job unless requested or explicitly included in the handoff.

## Validate the handoff

Require all of the following:

1. `scene.mode`, which determines the required job count.
2. `view_prompts[]`, containing the exact text and camera contract for every required first submission.
3. `original_requirement` plus `normalized_requirement`, the shared audit contract.

Require `visual_brief`, `layer_plan`, `canvas_plan`, `time_variant_plan`, and a `scene_description` plus `camera_contract` inside every view entry. Treat camera, spatial relations, scale landmarks, removable layers, and edge-extension constraints as audit inputs. Do not submit `ndc-mj-scene/v1` or `v2` directly; migrate it through `ndc-scene-to-mj-prompt` to `v3`.

Accept the full `ndc-mj-scene/v3` fields described in [handoff contract](references/handoff-contract.md). If any required view prompt is absent or structurally conflicts with a hard requirement, use `ndc-scene-to-mj-prompt` to repair the handoff before operating Midjourney. Do not infer a missing audit contract from prompts alone.

Validate the view set exactly:

- `exploration`: exactly one `eye_level` entry. Its camera contract and prompt must specify an eye-level three-point-perspective composition, camera optical center `1.7–1.8 meters` above the floor, and horizon at the upper third. Reject additional viewpoints.
- `non_exploration`: exactly three entries in order: `frontal`, `oblique`, `overhead_45`. The overhead entry must mean an approximately 45-degree downward camera angle, not a horizontal rotation.
- Every view is an independent job. Reject prompts that request multiple views, split panels, contact sheets, or collages in one image.
- Compare shared scene identity, architecture, core objects, lighting state, exclusions, and rendering language across all entries. Repair unexplained content drift before submission.
- Require fixed MJ generation at `2:1` for both scene uses. Require `story_progression` to include `post_mj_operation: crop_or_reframe_to_16_10` plus a `16:10` crop-safe plan. Require `primary_exploration` to include a central safe area, left/right continuity, mouse-pan readability, and any post-MJ Photoshop Firefly extension plan.
- Require `time_variant_plan.geometry_lock: true`. Submit only the declared geometry master unless the user explicitly asks to regenerate a separate time variant.
- Require every collectible, disappearing object, character, body, Loop-specific prop, close-up clue, and scan visualization to remain outside the base prompt.
- Keep every person- or character-related token out of positive prompt prose. Permit such tokens only once in the final dedicated `--no people, person, humans, characters, crowds, figures, faces, bodies, silhouettes` parameter.

Before opening the page:

- Confirm every `status: use` local file exists.
- Exclude every `status: reject` reference.
- Compare every view prompt with all shared hard requirements and its own camera contract.
- Preserve harmless soft or flexible imprecision.
- Require `parameters.model: "latest"` by default. Select the current latest Midjourney model shown in the live UI before submission; never add a model-version parameter to the prompt text. Honor a specific model only when the user explicitly requested it for the current job. If the requested model is unavailable, stop and report the blocker instead of silently falling back.
- Confirm fixed `--ar 2:1` appears exactly once in every Midjourney prompt. Never replace it with `16:10` or another final-delivery ratio.
- Treat HD/high-quality output as a live-UI preflight check. If the current Midjourney UI exposes an HD or equivalent high-quality control, enable it and verify its selected state. If it does not exist, do not invent an obsolete parameter; report the unavailable control and preserve the current quality setting.

## Mandatory static style references

For every NDC Midjourney view submission, apply both static style references from the images already saved in the Midjourney account:

- `assets/ndc-static-style-city-rain.jpg`
- `assets/ndc-static-style-character-graphic.png`

Treat both assets as mandatory `style` references even when the handoff contains `references: []`. Use them only through Midjourney's Style Reference role, never as image, composition, environment, character, or identity references. On the Alpha Imagine page, click `Images` in the upper-right, select the two matching saved images from the panel below, and assign both specifically as Style References. Do not upload the bundled local copies during normal operation; use them only to identify the matching saved images.

Do not inherit the city skyline, rain, nighttime setting, orange street, male character, facial identity, pose, or costume from these images. If the Midjourney UI cannot assign both files specifically as Style References, stop instead of silently submitting without them or degrading them to image prompts. If repeated figure leakage can be traced to the character-based style asset, stop and request an approved character-free environment style proxy; do not compensate by adding character descriptions to positive prose or by silently dropping a mandatory reference.

Add handoff-provided `status: use` references only after these two static style references. Keep the handoff roles unchanged; the static references do not replace scene-specific environment, composition, or identity references.

## Operate Midjourney

Use the Midjourney Alpha Imagine page at `https://alpha.midjourney.com/imagine` through the selected browser surface. Navigate directly to this exact URL; do not infer the Alpha version from an upper-left logo or screenshot, and do not substitute the non-Alpha `www.midjourney.com` page.

1. Reuse an existing suitable Midjourney tab when available; otherwise open the Imagine page.
2. Inspect the current page before clicking or typing. Do not rely on remembered coordinates or stale controls.
3. If authentication blocks the task, ask the user to sign in on that browser surface and continue only after they report it ready. Never inspect or retrieve cookies, passwords, or session stores.
4. Open `Images` in the upper-right and select the two saved static style images first, assigning both specifically as Style References. Do not re-upload their bundled local copies.
5. Only when the handoff contains additional `status: use` local references, read the browser's current file-upload documentation, show those exact files and the Midjourney destination, obtain any required upload confirmation, then upload and assign each declared role. Do not turn handoff references into style references unless the handoff declares that role.
6. Select the handoff's declared model. When it is `latest`, choose the current latest model shown in the live UI and verify the selected state. Preserve personalization and unrelated settings. Do not silently use an older model when `latest` is declared.
7. Inspect the live settings for an HD or equivalent high-quality control and apply the preflight rule above; quality selection is separate from model selection.
8. Process `view_prompts[]` in declared order. Enter that entry's `prompt_en` exactly for its first round and apply the shared handoff parameters without duplicating them.
9. Submit one independent job per required view, verify that each new job appears, and wait for every complete result grid before declaring the initial view set complete.
10. Never stop after only one non-exploration view has been submitted. The required output is three separately auditable jobs, not one preferred angle.
11. Do not generate separate day/night versions by default. The selected master goes to Photoshop for geometry-locked manual relighting.
12. Do not perform Photoshop expansion or relighting in this Skill; report the exact Firefly/Photoshop handoff after the MJ base passes.

## Audit the result grid

Review every candidate in every required view against the original and normalized requirements plus that view's camera contract in this order:

1. Core composition and camera.
2. Empty-background and layer-contract compliance.
3. Gameplay architecture, routes, interaction areas, and permanent environmental storytelling.
4. Canvas use, central safe area, and extendable edges.
5. Scene identity, period, and reference-image leakage.
6. Lighting, material, and graphic finish.
7. Soft and flexible details.

Use `pass`, `partial`, or `fail` for each category. Do not reject an image only because a flexible count differs. For example, the presence and type of high clerestory windows can matter while their exact count remains irrelevant.

For composition and camera, explicitly compare the image with that view entry's scene description and camera contract:

- perspective type, view direction, camera height, and horizon;
- foreground-middle-background and left-center-right anchors;
- connection, separation, overlap, visibility, route, and relative scale among architecture-defining masses;
- lens distortion and focus/readability when specified;
- visible calibration landmarks such as wainscot tops, tabletops, window sills, rails, or stair landings. A camera-height label in the prompt does not pass if the observable geometry contradicts it.

Fail any candidate containing a person, named character, crowd, face, body, or silhouette. Fail a base background that bakes in a collectible, disappearing object, Loop-specific prop, close-up clue, or scan effect. A temporary scale silhouette may be overlaid only after generation for review and must be removed before selection/export.

For `primary_exploration`, inspect both side edges of the `2:1` MJ base for continuous walls, floors, ceilings, streets, skyline, and lighting that Photoshop Firefly can extend. Confirm the central gameplay-safe area remains complete before any expansion. For `story_progression`, confirm all required content in the `2:1` MJ base survives the planned post-MJ crop to `16:10`.

For an exploration view, fail any candidate that does not visibly satisfy the eye-level three-point perspective, an optical center about `1.7–1.8 meters` above the floor, and the upper-third horizon lock. For non-exploration, judge frontal, oblique, and 45-degree downward views independently; one passing view never substitutes for a missing or failed required view.

Keep aesthetic appeal separate from requirement fidelity. A beautiful image with a wrong layout or missing core object fails. A faithful image may proceed even if decorative details drift.

## Choose the next action

- `stop-view`: at least one candidate in the current view passes every hard requirement and has no damaging leakage. Record the candidate index and continue to any unresolved required views.
- `stop-set`: every required view has one passing candidate. Only then report the view set complete.
- `vary-subtle`: a candidate passes composition and core objects but has a small local rendering or detail issue. Use this first for a localized defect.
- `vary-strong`: use on the same useful candidate when a subtle variation fails to resolve the localized defect, or when the initial defect already requires a meaningful visual reinterpretation without changing the scene contract.
- `repair-and-resubmit`: the whole grid repeats a structural problem, misses a core object, uses the wrong scene identity, or shows reference leakage that variation is unlikely to solve.
- `handoff-to-photoshop`: the MJ base passes; report Firefly left/right extension, manual day/night relighting, and removable-layer placement without trying to bake those changes into another MJ job.

For `repair-and-resubmit`, preserve every accepted clause in that view and change only its failure delta:

- Wrong composition: shorten and front-load the camera and large spatial masses.
- Missing core object: move it earlier and state its position, scale, and relationship.
- Reference leakage: remove or downgrade the conflicting reference before lengthening exclusions.
- Period drift: add concrete period construction or props; avoid generic `vintage` padding.
- Unwanted people: first remove portrait or identity references that do not belong in the scene.
- Mutable evidence or transient props baked into the base: remove their positive prompt clauses and reserve only an empty alignment area.
- Poor exploration extension edges: simplify side structures and lighting so Photoshop Firefly has coherent continuation targets without changing the central safe area.

Use `ndc-scene-to-mj-prompt` for structural rewrites. Supply it with the previous handoff, the failed view id, and a factual failure report, not a vague request to “make it better.” Preserve already passing views and continue only within the failed view's authorized iteration budget.

Default escalation for one otherwise valid candidate is `vary-subtle` first, inspect the returned grid, then `vary-strong` only if the defect persists. Skip directly to `repair-and-resubmit` when the camera, depth structure, entrance relationship, major route, or another hard architectural relation is wrong across the grid.

## Report each round

Return for each required view:

- view id, round number, and job identity or URL when visible;
- exact prompt and references used for that view;
- candidate-by-candidate audit summary;
- selected action and its requirement-based reason;
- remaining iteration budget for that view;
- final passing candidate or the unresolved blocker.
- canvas status: `MJ 2:1 base passed, 16:10 post-crop pending` or `MJ 2:1 base passed, Photoshop Firefly horizontal extension pending`;
- geometry-locked day/night Photoshop handoff when a time variant is required;
- separate-layer list for collectibles, transient story content, close-ups, and scan overlays.

Then report whether the complete required view set passed. For `non_exploration`, list the selected candidates for `frontal`, `oblique`, and `overhead_45` separately.

Do not claim a result passed before visually inspecting the complete image. Do not hide requirement drift merely because the image is attractive.
