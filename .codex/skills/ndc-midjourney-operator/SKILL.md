---
name: ndc-midjourney-operator
description: "Generate and deliver native character-free NDC scene images in Midjourney from an ndc-mj-scene/v4 handoff. Use for MJ实际出图、双Style Reference、场景构图和空间布局审核、有限轮次Vary与提示词修订、原始MJ图片下载交付. Defer gameplay props; allow sparse period ambient dressing. No retouching, expansion, relighting or prop-production phase. Do not use for prompt-only requests."
---

# NDC Midjourney Operator

## 画面描述辅助检查

编写或修改生图/编辑输入时，协作使用 [ndc-visual-description](../ndc-visual-description/SKILL.md)：需求与参考明确后，在布局/姿态方案定稿前确定本帧可见意图；最终提示、参考及裁切组装后检查实际提交内容，防止下游重新引入剧情/视角冲突。沿用已有检查，实质变化只复核受影响项；候选偏差复用本 Skill 的视觉审阅进行原因诊断。

该辅助 Skill 只负责可见描述与冲突检查。本 Skill 的来源权威、逐字提示锁定、专门技术/视觉门禁、工具权限和重试预算继续有效；不得以描述检查通过代替图片验收。纯复用与文件复制不重做创作分析。


Run the required scene view set through submission, bounded iteration, visual review and native MJ image delivery. The workflow ends there. Later user retouching is supported by readable layout, separated major shapes, quiet planes and coherent lighting in the MJ image itself.

For a packet released by another task, use the [scene pipeline handoff](../ndc-art-stage-pipeline/references/scene-pipeline.md): claim the whole scene with all required views, retain its original production journal and exact source/prompt locks, and check the current packet/lease before external actions. The producer can prepare another independent scene concurrently. Never create a separate unaware task per view or restart a view's three-round budget. `execution_mode: validation` only checks the received contract and returns `VALIDATION_COMPLETE`; it never opens/submits MJ or claims image approval. Production without an existing explicit user image-generation grant stays waiting; approving Skill maintenance is not that grant.

## Review scope and evidence reuse

Read [production record and continuation](references/production-record.md) before accepting or resuming a job. Separate a grid's coarse rejection record from a shortlisted native file's formal visual record:

- Inspect all four grid candidates for hard camera/layout, architecture/routes and figure leakage first. A clear veto ends that candidate's review with a concrete reason; uninspected fine style/texture stays `NOT_CHECKED`, not `PASS`. Rejected candidates need no complete tile inspection, and their historical failures do not block a different current accepted candidate.
- A shortlisted original file must pass whole-image `100%`, complete original-pixel local coverage (or the required `200%` views), and all applicable camera, spatial, state, framing, style, texture and reference-leakage criteria. Browser completion, thumbnails, dimensions and hashes do not prove artistic success.
- Write a current `ndc-stage-visual-self-check/v1` record binding the reviewer/date, input/output identity and hashes, actual inspected views, each applicable criterion/finding, status and rework owner. Missing evidence, stale bindings, `FAIL` or applicable `NOT_CHECKED` blocks formal selection/delivery. When a local file exists, run `python D:/Codex/NDC/scripts/validate-ndc-stage-visual-self-check.py --record <visual-review.json> --artifact <current-output>`; a nonzero result blocks that artifact.
- Selection, byte-preserving copy and publication may reference the same passing review after the production-record protocol checks current bytes, sources/parents, role, requirements and rejection status. New pixels or a changed requirement/role trigger only the affected review plus required whole-image/context checks. Style and texture retain distinct conclusions but share the actual inspection evidence.

Every attempt remains recorded, including rejected and uncertain results. Final delivery requires the current accepted dependency chain to pass; it never requires rejected grids to become passing stages. Budget exhaustion leaves an unresolved candidate and does not relax any formal gate.

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

Verify the upstream existing-asset lookup and its current approval/requirement bindings. Do not repeat inventory unless those inputs changed. Track exactly one exploration `eye_level`, or three non-exploration `frontal`, `oblique`, `overhead_45` required views, while submitting independent jobs only for missing or explicitly requested redraws. Exploration retains the project lock: eye-level three-point perspective, camera optical center 1.7–1.8 meters and upper-third horizon. Overhead means 45 degrees downward, not horizontal yaw. Require `--ar 2:1` once and no model flag; shared room facts and master state remain invariant.

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

Follow [operation loop](references/operation-loop.md). Use `https://alpha.midjourney.com/imagine`, inspect the live page, verify the latest exposed model and HD selection, both saved Style References and `2:1`. Preserve unrelated settings. Before each image-producing action, reserve it in the persistent scene/view/state job under the production-record protocol, then submit each exact first-round prompt once and record its new job identity before further actions. Preserve the cumulative three-round budget across prompt revisions, tab recovery, changed output directories and task handoffs. An uncertain response requires checking the gallery, not immediate resubmission. Follow the bounded browser-recovery procedure when observation fails; tab metadata alone cannot verify the account, settings or job result.

Review all four candidates against the current handoff's camera and spatial contract first. Derive scene-specific checks from that contract; do not inherit another task's camera placement, architecture, furnishings or state. Use visible scale and perspective cues, not prompt labels, to judge camera height. Preserve passing views and iterate only failed ones within budget. For every later shortlisted view, compare source-supported landmark identities, wall/opening connections and master state with the shared contract and current accepted views. Visibility may change with camera; room facts may not. If a shared source fact changes, invalidate only affected view plans/reviews; never silently replace the authority with generated geometry or reset budgets.

After a candidate clears the hard composition/architecture/empty-background vetoes, download its native file to the work-process directory. Inspect the whole image and complete overlapping original-resolution tiles. Review style and texture separately; `FAIL` or `NOT_CHECKED` blocks formal selection. Use the existing tile helper and record coverage, original dimensions, current hashes, stage visual checks and `ndc-texture-coherence/v1`; validate using `D:/Codex/NDC/scripts/validate-ndc-texture-gate.py` and the shared stage validator.

Choose among hard-passing images by later editing convenience: legible depth, separated silhouettes, unobstructed routes, continuous supporting surfaces, coherent light and restrained incidental clutter. Do not smooth away the approved painterly style. Do not reject a sound MJ base because later props or final game-canvas operations remain absent.

## Complete delivery

For every required view, provide the native MJ file, actual format/dimensions/hash, job URL or ID, exact submitted prompt and actual model/HD/reference settings, candidate audit and final gate records. Decode the downloaded file to check integrity and measured aspect ratio; a thumbnail, filename or HD toggle is not proof of native resolution. A mismatched download returns to file retrieval and QA. Keep original downloaded bytes; any QA overview or tiles are separate process artifacts. Deliver a passing MJ source image, without a Photoshop task list or pending-retouch status.

If no candidate passes within budget, retain the best candidate in `工作过程文件`, state the unmet camera/layout/style requirement and actual attempts, and do not mark it formal or conceal the failure with later manual-edit promises. Required non-exploration views remain individually tracked until all pass or are explicitly reported unresolved.
