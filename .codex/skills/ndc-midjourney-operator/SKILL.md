---
name: ndc-midjourney-operator
description: "Operate Midjourney for NDC scene generation from an ndc-mj-scene/v2 handoff containing shared source requirements and the required view prompts. Use when the user asks to在 Midjourney 网页提交或生成 NDC 探索场景单一平视搜证镜头、为非探索场景生成正面/斜侧/45度俯视三个独立任务、上传并设置参考图、检查各视角四宫格、按构图和核心物品审核结果、做 Vary 或最小提示词修订并继续有限轮次迭代。 Use browser:control-in-app-browser for the web UI. Do not use for prompt-only requests; use ndc-scene-to-mj-prompt instead."
---

# NDC Midjourney Operator

Submit, inspect, and iterate the complete required NDC view set while treating every per-view prompt and the shared source requirements as separate primary inputs. Audit generated images against the requirements and each view's camera contract, not merely against whether they resemble the prompt.

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

Require `visual_brief` and a `scene_description` plus `camera_contract` inside every view entry. Treat the per-view camera, depth layers, lateral layout, architecture relationships, and camera-calibration landmarks as audit inputs rather than optional prose. Do not submit an older `ndc-mj-scene/v1` packet directly; use `ndc-scene-to-mj-prompt` to migrate it to `v2` so the required view count is explicit.

Accept the full `ndc-mj-scene/v2` fields described in [handoff contract](references/handoff-contract.md). If any required view prompt is absent or structurally conflicts with a hard requirement, use `ndc-scene-to-mj-prompt` to repair the handoff before operating Midjourney. Do not infer a missing audit contract from prompts alone.

Validate the view set exactly:

- `exploration`: exactly one `eye_level` entry. Its camera contract and prompt must specify an eye-level three-point-perspective composition aligned with a standing eye line, camera height `1.7–1.8 meters`, and horizon at the upper third. Reject additional viewpoints.
- `non_exploration`: exactly three entries in order: `frontal`, `oblique`, `overhead_45`. The overhead entry must mean an approximately 45-degree downward camera angle, not a horizontal rotation.
- Every view is an independent job. Reject prompts that request multiple views, split panels, contact sheets, or collages in one image.
- Compare shared scene identity, architecture, core objects, lighting state, exclusions, and rendering language across all entries. Repair unexplained content drift before submission.

Before opening the page:

- Confirm every `status: use` local file exists.
- Exclude every `status: reject` reference.
- Compare every view prompt with all shared hard requirements and its own camera contract.
- Preserve harmless soft or flexible imprecision.
- Require `parameters.model: "8.1"` by default. Select Midjourney V8.1 in the live UI before submission; never add `--v 8.1` to the prompt text. Honor another version only when the user explicitly requested it for the current job. If the declared version is unavailable, stop and report the blocker instead of silently falling back.
- Confirm the requested aspect ratio is represented once in every view prompt, normally as `--ar 2:1` for an NDC background.
- Treat HD/high-quality output as a live-UI preflight check. If the current Midjourney UI exposes an HD or equivalent high-quality control, enable it and verify its selected state. If it does not exist, do not invent an obsolete parameter; report the unavailable control and preserve the current quality setting.

## Mandatory static style references

For every NDC Midjourney view submission, upload and apply both bundled assets as Midjourney Style References:

- `assets/ndc-static-style-city-rain.jpg`
- `assets/ndc-static-style-character-graphic.png`

Treat both assets as mandatory `style` references even when the handoff contains `references: []`. Use them only through Midjourney's Style Reference role, never as image, composition, environment, character, or identity references.

Do not inherit the city skyline, rain, nighttime setting, orange street, male character, facial identity, pose, or costume from these images. If the Midjourney UI cannot assign both files specifically as Style References, stop instead of silently submitting without them or degrading them to image prompts.

Add handoff-provided `status: use` references only after these two static style references. Keep the handoff roles unchanged; the static references do not replace scene-specific environment, composition, or identity references.

## Operate Midjourney

Use the Midjourney Imagine page at `https://www.midjourney.com/imagine` through the selected browser surface.

1. Reuse an existing suitable Midjourney tab when available; otherwise open the Imagine page.
2. Inspect the current page before clicking or typing. Do not rely on remembered coordinates or stale controls.
3. If authentication blocks the task, ask the user to sign in on that browser surface and continue only after they report it ready. Never inspect or retrieve cookies, passwords, or session stores.
4. Read the browser's current file-upload documentation before any upload. Show the two bundled static style assets plus the exact handoff `status: use` local files, the Midjourney destination, and obtain any upload confirmation required by the browser skill.
5. Upload the two bundled assets first and assign both specifically as Style References. Then upload only handoff `status: use` references and assign each declared role. Do not turn handoff references into style references unless the handoff declares that role.
6. Select the handoff's declared model version, normally V8.1, and verify the selected state. Preserve personalization and unrelated settings. Do not silently substitute the page's current version.
7. Inspect the live settings for an HD or equivalent high-quality control and apply the preflight rule above; HD selection is separate from the V8.1 model selection.
8. Process `view_prompts[]` in declared order. Enter that entry's `prompt_en` exactly for its first round and apply the shared handoff parameters without duplicating them.
9. Submit one independent job per required view, verify that each new job appears, and wait for every complete result grid before declaring the initial view set complete.
10. Never stop after only one non-exploration view has been submitted. The required output is three separately auditable jobs, not one preferred angle.

## Audit the result grid

Review every candidate in every required view against the original and normalized requirements plus that view's camera contract in this order:

1. Core composition and camera.
2. Core gameplay or narrative objects.
3. Scene identity, period, and required/forbidden subjects.
4. Reference-image leakage.
5. Lighting, material, and graphic finish.
6. Soft and flexible details.

Use `pass`, `partial`, or `fail` for each category. Do not reject an image only because a flexible count differs. For example, the presence and type of high clerestory windows can matter while their exact count remains irrelevant.

For composition and camera, explicitly compare the image with that view entry's scene description and camera contract:

- perspective type, view direction, camera height, and horizon;
- foreground-middle-background and left-center-right anchors;
- connection, separation, overlap, visibility, route, and relative scale among architecture-defining masses;
- lens distortion and depth-of-field readability when specified;
- visible calibration landmarks such as wainscot tops, tabletops, window sills, rails, or stair landings. A camera-height label in the prompt does not pass if the observable geometry contradicts it.

For an exploration view, fail any candidate that does not visibly satisfy the eye-level three-point perspective, `1.7–1.8 meter` standing camera, and upper-third horizon lock. For non-exploration, judge frontal, oblique, and 45-degree downward views independently; one passing view never substitutes for a missing or failed required view.

Keep aesthetic appeal separate from requirement fidelity. A beautiful image with a wrong layout or missing core object fails. A faithful image may proceed even if decorative details drift.

## Choose the next action

- `stop-view`: at least one candidate in the current view passes every hard requirement and has no damaging leakage. Record the candidate index and continue to any unresolved required views.
- `stop-set`: every required view has one passing candidate. Only then report the view set complete.
- `vary-subtle`: a candidate passes composition and core objects but has a small local rendering or detail issue. Use this first for a localized defect.
- `vary-strong`: use on the same useful candidate when a subtle variation fails to resolve the localized defect, or when the initial defect already requires a meaningful visual reinterpretation without changing the scene contract.
- `repair-and-resubmit`: the whole grid repeats a structural problem, misses a core object, uses the wrong scene identity, or shows reference leakage that variation is unlikely to solve.

For `repair-and-resubmit`, preserve every accepted clause in that view and change only its failure delta:

- Wrong composition: shorten and front-load the camera and large spatial masses.
- Missing core object: move it earlier and state its position, scale, and relationship.
- Reference leakage: remove or downgrade the conflicting reference before lengthening exclusions.
- Period drift: add concrete period construction or props; avoid generic `vintage` padding.
- Unwanted people: first remove portrait or identity references that do not belong in the scene.

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

Then report whether the complete required view set passed. For `non_exploration`, list the selected candidates for `frontal`, `oblique`, and `overhead_45` separately.

Do not claim a result passed before visually inspecting the complete image. Do not hide requirement drift merely because the image is attractive.
