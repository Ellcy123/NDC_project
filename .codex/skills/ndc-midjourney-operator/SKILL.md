---
name: ndc-midjourney-operator
description: "Generate and deliver native character-free NDC scene images in Midjourney from an ndc-mj-scene/v4 handoff. Use for MJ实际出图、双Style Reference、场景构图和空间布局审核、有限轮次Vary与提示词修订、原始MJ图片下载交付. Defer gameplay props; allow sparse period ambient dressing. No retouching, expansion, relighting or prop-production phase. Do not use for prompt-only requests."
---

# NDC Midjourney Operator

Run the required scene view set through submission, bounded iteration, visual review and native MJ image delivery. The workflow ends there. Later user retouching is supported by readable layout, separated major shapes, quiet planes and coherent lighting in the MJ image itself.

## Mandatory stage-end visual self-check gate

Every art-production stage executed by this Skill must end with an actual visual self-check before its output may be accepted, passed to a later formal stage, selected as passed or released. This includes reference-role acceptance, each initial grid, each variation or resubmission round, candidate selection, local-file acceptance, and native MJ image delivery. Inspect the current whole image at `100%` and every applicable local region at nearest-neighbor `200%` or through complete original-pixel tiles. Compare against the current handoff, camera/spatial contract, empty-background/prop-deferral rules, framing context, approved style authority, texture contract, reference-leakage risks, and every other applicable visual requirement.

Write one current `ndc-stage-visual-self-check/v1` JSON record per executed stage. It must bind the stage ID, reviewer/date, input and output paths plus SHA-256 when a local file exists, the inspected `whole_100` and `local_200_or_tiles` views, every applicable criterion with an explicit finding and `PASS`/`FAIL`/`NOT_CHECKED`, the overall `visual_check_status`, and the responsible rework stage when blocked. Missing record, missing visual-detection item, missing required view, stale local hash, `FAIL`, or `NOT_CHECKED` is `STAGE_VISUAL_SELF_CHECK_GATE: BLOCKED`: do not select, advance, or call the result passed. Browser completion, job status, grid existence, dimensions, URLs, or absence of a detected error cannot write visual `PASS`.

After a block, return to the responsible round or handoff-repair stage, perform the missing inspection and authorized variation/resubmission, then repeat the visual self-check on the new current output. Release only after the current candidate has a passing record. When a local file exists, run `python D:/Codex/NDC/scripts/validate-ndc-stage-visual-self-check.py --record <visual-review.json> --artifact <current-output>`; a nonzero result is a hard stop. When browser-only evidence has not yet produced a local file, save the same record with page/job identity and review-view evidence, but treat formal file delivery as incomplete until a downloaded current file is hash-bound and validated. Existing per-view generation budgets still apply, and exhausting one leaves an unresolved candidate rather than weakening this gate.

## References and browser capability

Read [handoff contract](references/handoff-contract.md), [operation loop](references/operation-loop.md) and [review rubric](references/review-rubric.md) before operating. Read [style analysis protocol](references/style-analysis-protocol.md) before style approval. Use the available browser-control tools and their current documentation; do not depend on an unavailable historical browser skill name.

## Authorization and scope

- An explicit request to generate/run/出图 authorizes the required initial view set, necessary inspection, up to three generation rounds per view including the first, and downloading native results for QA and delivery. A prompt-only request does not authorize submission.
- When changing browser or profile, preserve the user's intended MJ account. Match the specific connected browser/profile and verify the account identity in visible UI before entering a prompt, attaching references or submitting. A generic browser name, successful login or familiar saved images does not prove account identity. Reuse a currently verified identity without asking again; if the target is unknown or mismatched, resolve that identity first. Do not inspect credentials or silently log out/switch accounts. Record the verified account/profile with the job settings.
- Prefer native HD using the exposed UI. No automatic creative upscale or external image editing. Exceeding the declared generation budget or a materially different scene/reference needs user authorization; routine corrections inside the budget do not.
- A download for QA is allowed before visual approval; it is a work-process candidate. Formal acceptance requires the current local-file visual checks. This avoids a download/inspection dependency deadlock.
- Do not publish, delete unrelated jobs, alter personalization/speed or start unrelated variants.

## Accept the handoff

Require `ndc-mj-scene/v4` with `workflow_end_stage: mj_image_delivery`, exact prompts, source and normalized requirements, camera/spatial contracts, `prop_policy`, `texture_contract`, references and native delivery contract. Migrate old versions through the prompt Skill; remove old operational postproduction and prop-placement requirements.

Validate exactly one exploration `eye_level`, or three non-exploration `frontal`, `oblique`, `overhead_45` independent jobs. Exploration retains the project lock: eye-level three-point perspective, camera optical center 1.7–1.8 meters and upper-third horizon. Overhead means 45 degrees downward, not horizontal yaw. Require `--ar 2:1` once and no model flag; shared room facts and master state remain invariant.

Default to deferred gameplay props: specified gameplay props, collectibles/evidence and game-defined environmental-narrative objects are excluded from positive prompts. Sparse period-appropriate non-interactive ambient dressing is allowed and may be chosen freely; keep it subordinate to composition and never duplicate deferred clue identities. Prioritize architecture, source-supported room-defining major furniture and the requested broad surface state; optional ambient dressing stays flexible. Do not require future prop positions, evidence surfaces, containers or layer maps. Missing deferred items never fails a result. A current user-explicit MJ inclusion must be recorded separately.

Keep character tokens only in one final `--no` parameter. Check every `status: use` file exists and has been inspected; never apply rejected references. Unknown final game width, unperformed cropping, expansion, relighting or prop work cannot block MJ generation or delivery.

## Mandatory static style references

For every NDC Midjourney view submission, apply both static style references from the images already saved in the Midjourney account:

- `assets/ndc-static-style-city-rain.jpg`
- `assets/ndc-static-style-character-graphic.png`

Treat both assets as mandatory `style` references even when the handoff contains `references: []`. Use them only through Midjourney's Style Reference role, never as image, composition, environment, character, or identity references. On the Alpha Imagine page, click `Images` in the upper-right, select the two matching saved images from the panel below, and assign both specifically as Style References. Do not upload the bundled local copies during normal operation; use them only to identify the matching saved images.

Do not inherit the city skyline, rain, nighttime setting, orange street, male character, facial identity, pose, or costume from these images. If the Midjourney UI cannot assign both files specifically as Style References, stop instead of silently submitting without them or degrading them to image prompts. If repeated figure leakage can be traced to the character-based style asset, stop and request an approved character-free environment style proxy; do not compensate by adding character descriptions to positive prose or by silently dropping a mandatory reference.

Treat the two static references as complementary controls, not proof of one universal surface style. The character-graphic asset controls compressed large shapes, hard massing, edge economy, and limited warm emphasis only. The city-rain asset controls matte weather texture, vertical atmospheric depth, charcoal/brown-gray grouping, and restrained orange light only. Do not require jewel-tone saturation or bold calligraphic contours unless the current handoff's approved scene reference independently supports them. For architectural interiors, expect thinner stable construction lines at doors, panels, and moldings, with hard geometry and softer light/atmosphere transitions.

Add handoff-provided `status: use` references only after these two static style references. Keep the handoff roles unchanged; the static references do not replace scene-specific environment, composition, or identity references.

## Submit and review

Follow [operation loop](references/operation-loop.md). Use `https://alpha.midjourney.com/imagine`, inspect the live page, verify the latest exposed model and HD selection, both saved Style References and `2:1`. Preserve unrelated settings. Submit each exact first-round prompt once; confirm its new job identity before further actions. An uncertain response requires checking the gallery, not immediate resubmission. Follow the bounded browser-recovery procedure when observation fails; tab metadata alone cannot verify the account, settings or job result.

Review all four candidates against the current handoff's camera and spatial contract first. Derive scene-specific checks from that contract; do not inherit another task's camera placement, architecture, furnishings or state. Use visible scale and perspective cues, not prompt labels, to judge camera height. Preserve passing views and iterate only failed ones within budget.

After a candidate clears the hard composition/architecture/empty-background vetoes, download its native file to the work-process directory. Inspect the whole image and complete overlapping original-resolution tiles. Review style and texture separately; `FAIL` or `NOT_CHECKED` blocks formal selection. Use the existing tile helper and record coverage, original dimensions, current hashes, stage visual checks and `ndc-texture-coherence/v1`; validate using `D:/Codex/NDC/scripts/validate-ndc-texture-gate.py` and the shared stage validator.

Choose among hard-passing images by later editing convenience: legible depth, separated silhouettes, unobstructed routes, continuous supporting surfaces, coherent light and restrained incidental clutter. Do not smooth away the approved painterly style. Do not reject a sound MJ base because later props or final game-canvas operations remain absent.

## Complete delivery

For every required view, provide the native MJ file, actual format/dimensions/hash, job URL or ID, exact submitted prompt and actual model/HD/reference settings, candidate audit and final gate records. Decode the downloaded file to check integrity and measured aspect ratio; a thumbnail, filename or HD toggle is not proof of native resolution. A mismatched download returns to file retrieval and QA. Keep original downloaded bytes; any QA overview or tiles are separate process artifacts. Deliver a passing MJ source image, without a Photoshop task list or pending-retouch status.

If no candidate passes within budget, retain the best candidate in `工作过程文件`, state the unmet camera/layout/style requirement and actual attempts, and do not mark it formal or conceal the failure with later manual-edit promises. Required non-exploration views remain individually tracked until all pass or are explicitly reported unresolved.
