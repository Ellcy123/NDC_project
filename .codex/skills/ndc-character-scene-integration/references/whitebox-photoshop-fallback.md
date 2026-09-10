# Photoshop MCP fallback for whitebox repair

白模顺序：初次生成时包括隐藏部位的完整人体，保留未裁剪母层；随后按真实遮挡关系裁剪派生层或制作蒙版，审核裁剪后的场景参考。正常裁剪不算缺失，不要求补回场景中本应被遮住的像素；小瑕疵容错不取消初始完整生成。正式角色同样先生成完整母层再应用遮挡。

白模阶段以 [白模放行与正式完整性](whitebox-acceptance.md) 为准：位置、比例、头身比、动作和演绎可准确判断时，小型遮挡、局部缺失和细节可放行，不为此强制补全、PS返修或再生成。下文完整母层要求在正式生产仍适用；白模只须提供足以判断核心目标的独立及联合参考。

Use native Photoshop MCP with one active operator per host; verify the bridge and required capabilities, then save recoverable checkpoints before handing over. This permits safe suspension for another independent task, not a whitebox PASS, a new repair budget or another task taking over actors inside the same scene.

Use as soon as a useful whitebox has a position, proportion, extraction or local assembly defect that verified Photoshop MCP operations can repair. Read [ps-first-repair.md](ps-first-repair.md); three generated attempts are a ceiling, not a prerequisite for PS. Choose the closest useful candidate by defect severity and completeness of separable actor components. A whitebox need not be produced correctly in one generative pass: PS-repaired anatomical mannequin imagery is a valid structural authority after the same complete acceptance gates.

## Budget and entry

For the user-approved layered workflow, the declared generation unit is a planned depth/occlusion batch; follow [layered-character-batches.md](layered-character-batches.md). Keep batch and whole-task counts, preserve passed lower layers, and never rename a failed batch to restart its budget. A batch may contain several complete separable actors. Full isolated actor layers are produced before occlusion, so PS can adjust them without inventing hidden anatomy. Fine gaze not resolvable in whitebox material belongs to later character review, not these repair rounds.

- Record generation attempts and completed PS repair/review rounds separately. The whitebox allowance is at most three generated attempts and up to three PS repair rounds, with PS allowed before the model ceiling. Do not call the model merely to consume unused attempts. One coherent repair with saved output and full review counts as a round; each tool command does not.
- For a resumed legacy candidate, preserve actual model and completed PS counts and use only its remaining authorized repair allowance; do not grant three fresh PS rounds on every resume. A user-explicit independent production/test follows the separate-count rule in production-cadence.md. Keep historical handoffs intact and record actual new work without rewriting old counters to fit a validator.
- Query the host, command inventory and specific schemas before editing. Use only supported, verified MCP operations. A command that merely tracks manual completion is not an automated capability. If an essential operation is unavailable, identify that exact operation and keep the candidate; do not substitute mouse/keyboard automation.

## Repair components and transforms

1. Before touching pixels, bind the candidate hash, original scene, canonical heights, measured head/body ratios, support anchors and intended pose. List each defect and the MCP operation intended to fix it.
2. Component separation needed for repair is allowed before the combined whitebox passes. It creates process-only layers, not approved generation inputs. Preserve complete visible silhouettes. Reveal or obtain missing anatomy only when it prevents judging the core whitebox criteria; acceptable small omissions are deferred to formal generation.
3. Move/scale the actual volumetric mannequin around the appropriate foot, pelvis or lying support anchors. Proportion correction, including head/body correction, is allowed at this whitebox stage when it produces coherent human anatomy and an unbroken neck/joint chain. Use only transformations the MCP actually exposes; do not stretch a person merely to fill a rectangle. Unsupported perspective/warp is not available by implication.
4. Keep fixed furniture and room geometry at original registration. Transform only the actor and its authorized associated components, then rebuild support response and occlusion as needed. Correcting one actor must not silently move another. If the required pose cannot be obtained while retaining sound anatomy, that defect is not solved by a transform.
5. For bounded omissions or assembly seams, reuse compatible existing pillow/bedding/actor components through verified selection and independent layers. Preserve the complete actor; do not permanently delete hidden anatomy or cut a final pillow to a different generated body silhouette. Whole-scene acceptance is still required after repair.
6. Work on one image/document at a time. Consecutive operations within that coherent repair may share one end-of-operation save, technical check, whole/local inspection and current-hash validation; this task resolves failure before advancing to its next image. After a recoverable save and frozen review snapshots, safely suspend through the shared queue for another independent task; unresolved or in-flight commands must follow queue recovery first. Retain source layers, failed status and existing counts. Follow [production-cadence.md](production-cadence.md) rather than restarting full reviews for every micro-operation.

## Reacceptance

Update affected pose/placement coordinates, transform records and artifact hashes. Rebuild isolated and combined references from the same current actor components. Recheck fixed-scene absolute scale, cast-scale v2 head-first, core body proportions and action under whitebox-acceptance.md, named support contacts and soft-material response, performance, gaze, actual UI, scene/cast occlusion, and preservation of camera/furniture. Existing validators and tolerances remain in force; do not alter source measurements to make a repaired picture pass.

Record an `ndc-stage-visual-self-check/v1` and exact-pose-whitebox visual review for the repaired artifact, then rerun the production ledger. Only the passing current whitebox may be isolated onto the original-color scene for the local three-reference handoff. No character generation may precede that acceptance.

This branch prepares anatomical whiteboxes. Formal-layer transforms and local pixel repairs follow [production-cadence.md](production-cadence.md) and [ps-first-repair.md](ps-first-repair.md); neither branch permits arbitrary transforms to rescue incorrect performance or treats missing anatomy/contact/scale evidence as passed. After exhausted repair rounds, retain a marked work candidate with unresolved findings.
