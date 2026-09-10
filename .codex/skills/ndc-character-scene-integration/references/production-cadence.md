# Production cadence and evidence reuse

白模顺序：初次生成时包括隐藏部位的完整人体，保留未裁剪母层；随后按真实遮挡关系裁剪派生层或制作蒙版，审核裁剪后的场景参考。正常裁剪不算缺失，不要求补回场景中本应被遮住的像素；小瑕疵容错不取消初始完整生成。正式角色同样先生成完整母层再应用遮挡。

白模阶段以 [白模放行与正式完整性](whitebox-acceptance.md) 为准：位置、比例、头身比、动作和演绎可准确判断时，小型遮挡、局部缺失和细节可放行，不为此强制补全、PS返修或再生成。下文完整母层要求在正式生产仍适用；白模只须提供足以判断核心目标的独立及联合参考。

Use whole-scene rehearsal, layered production, whole-scene acceptance and one final package. Technical schemas are evidence interfaces inside these milestones, not a demand for a new picture or report for every command.

The Astra/medium reference coordinator owns complete scene direction and whiteboxes until a whole-scene handoff; the Terra/xhigh worker then owns all actors, interactions and final acceptance in that scene. See [phase handoff](../../ndc-art-stage-pipeline/references/integration-pipeline.md). Only different complete scenes overlap across these phases; reference defects return ownership after the old production claim ends. Do not split actors into separate tasks that advance different production stages of the same scene. Independent scenes may overlap non-PS preparation, generation waits and offline review only when their sources, working documents, outputs and scene records are isolated and shared masters are read-only. All actual PS use goes through native MCP with one active operator per host and a saved checkpoint before handover.

## Start and resume

- Read the latest user instruction and rejection/pause note before old PASS records. Inventory current layers, unresolved defects, actual counts and verified tool capabilities once. Preserve valid components instead of restarting the cast.
- Separate authorized asset work from formal Skill maintenance. Record uninstalled proposals; do not silently apply an unapproved exception or block unrelated authorized work on maintenance approval.
- Keep one concise work record: current source/output identity, useful artifact, transforms/contact dependencies, unresolved defect, next action, generation/repair counts and elapsed time. Native reports and one ledger carry detailed evidence; do not duplicate measurements by hand.
- For a test comparable to four actors in a fixed room, target a useful full-scene preview within about 30 minutes and a method review at about 90 minutes. These are planning targets, not delivery guarantees or universal time limits. Record tool/model waiting separately and report total elapsed time too. At the checkpoint identify the bottleneck and switch to a permitted workable method or report the exact blocker; do not extend polish/paperwork by default. Do not duplicate an in-flight model submission.

## Rehearsal before polish

Reuse available candidates/masters for a cheap full-shot read. With none available, the first anatomical whitebox assembly supplies the preview; do not require an extra generation just for rehearsal. Provisional evidence does not pass the pre-generation gate.

Read intended relationships and body language first; then support/depth/scale, soft contact, UI and overlap. Known failure stops dependent refinement, not independent passed work. Use the same actor layers for unobstructed and final-occluded views. Whole-shot judgment precedes fine head/edge measurement.

## PS before avoidable regeneration

Before another model call, classify the defect using [ps-first-repair.md](ps-first-repair.md). Prefer re-extraction, layer-order/occlusion correction, support-calibrated transforms or compatible donor patches when correct content already exists. Do not consume generation attempts to reach a PS entry threshold. An unavailable advanced command is not proof that verified selection/layer operations cannot solve the defect. Compare the full repair/review time with generation, extraction, registration and renewed review, not model latency alone.

## One coherent image operation

Same-document extraction cleanup, documented uniform registration and save may form one operation. Intermediate files are unaccepted work states. Within the same task, save, run relevant technical checks, inspect whole/local views, write and validate the current-hash review before advancing to another image. Never batch-edit several PS documents before reviewing. Bridge occupancy is separate: after saving a recoverable checkpoint and frozen review snapshots with no in-flight or unknown command, suspend and release to other independent tasks under the global queue. Offline review need not hold PS. Keep unfinished/failed acceptance, dependency blocks and existing counts; recheck document identity, source version and current hashes when the task reacquires PS. A timeout alone cannot prove safe release. Tell the user whether PS is editing, saved awaiting review, or safely released; record a user-confirmed manual close as such, not as an inferred bridge failure.

Inspect contextual RGB before extraction; extraction cannot certify an unaccepted face, pose or contact. Prefer verified non-generative extraction/native alpha that preserves the accepted pixels and contextual workflow. Do not assume a PS selection command exists. Model-based removal is a new generative attempt: compare it to the accepted parent for identity, silhouette, scale and contact.

Review normalized actors on the actual scene as well as neutral backgrounds. Permitted PS correction includes support-anchored uniform scale/translation/rotation of an anatomically and semantically suitable layer, plus bounded extraction, occlusion and compatible-pixel repairs under ps-first-repair.md; update affected whitebox/placement evidence and interaction layers, then revalidate. Respect explicit user-locked coordinates. Do not warp a wrong pose, fit an alpha box or alter fixed furniture. Preserve the untouched high-resolution source and apply the composed transform once to avoid repeated destructive resampling.

## Evidence reuse

- Reuse actual prior review for byte-identical copies only when authority, requirements, pose/support/occlusion/UI context, scope and acceptance state are unchanged. Verify destination hash and path. User rejection invalidates reuse even when bytes match.
- Metadata/manifest writes do not require another visual inspection. Pose/support/UI/authority edits change interpretation and do require affected review. Filenames cannot rehabilitate a failed result.
- New pixels require actual current whole-frame review plus local inspection of changed regions and affected boundaries, contacts, identity or occlusion. Earlier local coverage survives only for proven unchanged regions under unchanged interpretation. Preserve complete current coverage and label inherited observations honestly.
- Share genuinely inspected views/findings across applicable visual, texture and physical checks. Schema-specific reports may reference the same inspection but must bind their actual artifact, scope, reviewer/time and provenance. Do not claim that a regenerated board was independently reviewed.
- Retain the five required ledger stage IDs as real review scopes. One inspection can cover actual extracted output and its registered scene preview after a coherent operation, yielding the corresponding compatibility reports. Each required output/view must actually exist and have been seen; simply filling stage names is invalid. The contextual result still needs its own acceptance before extraction.
- An original unchanged report can be referenced directly at its original path. For a copied output, if the validator requires destination binding, derive a copy-bound record with the original observations/reviewer/time and source-record reference, plus the new path/hash and explicit copy check. This is provenance adaptation, not a fabricated fresh visual review.

Neutral-edge detectors are diagnostic. When flags indicate intentional white hair, collars, highlights or bedding, inspect the flagged material regions once against the parent and black/white/scene-tone views. Preserve raw findings and an evidence-bound material classification. Do not raise thresholds, remove light design pixels or write exhaustive per-pixel prose where one reviewed material region explains the issue.

## Budget and routing

- Keep counts per planned batch/actor and for the whole scene. Whiteboxes retain three generated attempts plus up to three coherent PS repair/review rounds per batch.
- For each formal actor or planned interaction unit, the six-attempt model ceiling includes initial context, revisions and generative background removal. A multi-actor call counts once globally and against each affected unit. Folders and stage labels do not grant new budgets. Additional PS correction has a finite declared allowance, normally up to three coherent rounds, and remains subject to the time checkpoint.
- For continuation within the same Codex conversation, carry forward its actual counts; a failed unit at its ceiling receives no extra model calls through renaming, reopening or this Skill revision. Every actual new Codex conversation automatically receives fresh counters, including work on reused candidates; no additional declaration or answer is required. Record the real conversation ID and provenance relation once; retain old files and old counts as history, but do not deduct them from or synchronize them into the new test. A folder/date/model change inside the same conversation does not create a new budget. Still-valid approved components may be reused; old failures do not become approved.
- Wrong intent/stiff silhouette returns to action/whitebox design; invalid support/scale to geometry; soft-contact failure to the coupled interaction; extraction drift to the accepted parent; packaging mistakes to packaging only.
- Validate pre-generation readiness when inputs change and post-generation readiness when finished layers change. Do not rerun an identical ledger merely because another command or metadata write occurred.
- At exhaustion preserve the candidate and exact unresolved failures. Do not manufacture six attempts to satisfy a legacy handoff checker; if its exact-six schema cannot represent a time/capability stop, keep a clearly marked work candidate with actual counts and do not claim that checker passed.

## Package once

Freeze pixels after scene acceptance. Produce source paths/hashes, layer/XY mapping and reconstruction from those outputs once, referencing valid existing reports. Formal folders contain passed assets; prompts, candidates and evidence remain in the work directory. Copy/reconstruction success cannot override withdrawn or failed visual acceptance.

## Repair rounds and scoped reuse

A PS repair round begins with an actual candidate pixel/layer-combination change. Opening, read-only measuring, queueing, preparing a selection plan, or exporting an unchanged source does not consume a repair round. One coherent same-document repair/save/review sequence is one round. A changed but unfinished sequence remains in-progress and reserves that round; a failed or discarded actual repair remains used, rather than disappearing because review was not completed. Keep model, PS and technical operations separate in the original counters.

Use the same scene-scale register as geometry authority. Review dependencies distinguish geometry, actor:<id>, interaction:<id> and composite:<snapshot>. An occlusion/soft-layer repair invalidates related actors/interactions and composite snapshots, not unrelated unchanged complete masters or source measurements. Existing native report hashes and actual artifact scopes remain authoritative; reuse their valid observations. Every changed composite still gets current whole-frame and relevant local inspection. Do not clone all reports or add a parallel ledger just to describe the dependency graph.
