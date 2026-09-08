---
name: ndc-character-scene-integration
description: Direct and place approved NDC characters in fixed scenes using narrative timelines, natural performance, physical scale and contact, independent character layers, actual dialogue UI, and original-resolution RGBA delivery. Use for 人物入景、角色融图、剧情角色进退场、点击前后状态、人物表演与站位、人物投影及既有入景资产审核；do not design new characters or generate new empty backgrounds.
---

# NDC Character Scene Integration

实际使用 Photoshop MCP 前按需读取 [全局 PS 队列](../ndc-photoshop-queue/SKILL.md)。同任务当前图须保存、完成技术及真实视觉检查并核对当前hash；未审完不得推进下一张。PASS可推进相应依赖；FAIL缺陷已记录且预算耗尽或用户要求封存时，保留候选和累计次数，仅继续独立资产；安全保存可恢复文件和固定审阅快照后，可按队列协议挂起释放给其他独立任务。释放不是PASS，不解除原图及依赖的阻断、不重置预算；命令在途或结果未知时不得自行交棒。纯准备、生图等待和离线审阅不长期占用桥接，未授权的PS操作不会因排队而获得授权。

Use approved scenes and character cards as authority. Establish a believable complete shot early, then produce separable layers and verify the finished shot. Technical agreement never overrides visible floating, stiff acting, broken contact, incorrect identity or a user's rejection.

## Scope and authorization

- Read/copy only from `D:/PMH/工作` and `D:/PMH/ndc`; outputs belong under `D:/Codex/NDC`. Keep evidence under `工作过程文件/角色融入场景/Unit<n>` and passed assets under the corresponding `最终交付` category, inside the source scene basename.
- If the user plans to generate manually in ChatGPT, provide prompts only. Execute generation/file management only within the authorized task. Do not edit Unity code/configuration or original production assets without separate authorization.
- Photoshop uses verified MCP capabilities and the shared queue only. Within this task, save, technically check, visually inspect and validate the current image before advancing to the next image. A recoverable checkpoint and frozen review snapshots permit suspension for another independent task under the queue protocol; an unfinished or failed image remains blocked. Consecutive operations on the same image may form one coherent repair.
- Task continuation and formal Skill installation are separate. Do not block already-authorized work merely to request a workflow update; record proposals and continue under applicable approved rules. An instruction to update the discussed revision authorizes that update. Real missing permission/capability blocks dependent work only; disclose the exact reason.
- A user rejection invalidates affected formal status and dependent reviews. Preserve history and follow the current pause/repair instruction. Passing gates does not mean user approval.

## Read the relevant guidance

Start or resume with [production-cadence.md](references/production-cadence.md) and [full-workflow.md](references/full-workflow.md). Load other references when the decision requires them, not all at startup.

| Decision | Reference |
|---|---|
| Cast presence and natural, readable acting | [directing-and-timeline.md](references/directing-and-timeline.md) |
| Support location, depth and scale | [placement-decision-chain.md](references/placement-decision-chain.md); [continuous-floor-support.md](references/continuous-floor-support.md) for continuous floors |
| Far-to-near batches, full masters and soft interactions | [layered-character-batches.md](references/layered-character-batches.md) |
| Repairable defects before another generation | [ps-first-repair.md](references/ps-first-repair.md) |
| Whitebox-specific repair and reacceptance | [whitebox-photoshop-fallback.md](references/whitebox-photoshop-fallback.md) |
| Actual input and reference responsibilities | [prompt-modules.md](references/prompt-modules.md) |
| Runnable schemas and commands | [staging-tool-contracts.md](references/staging-tool-contracts.md), search the relevant command |
| Shadows, state variants, packaging | [shadow-construction.md](references/shadow-construction.md), [state-variant-assembly.md](references/state-variant-assembly.md), [delivery-contract.md](references/delivery-contract.md), only for the active operation |
| Repeated unexplained failure | Relevant entry in [case-studies.md](references/case-studies.md) |

Collaborate with [ndc-visual-description](../ndc-visual-description/SKILL.md) before locking visible action/layout and after assembling the actual prompt, reference roles and crop. Reuse its reasoning for candidate diagnosis. Back views do not request visible frontal expressions; identity cards do not override the intended view. Pure copies do not restart creative analysis.

## Four production milestones

同一场景由一个任务统筹整场预演、白模联动、分层生产与全场验收；不能把角色A的正式合成与角色B尚未稳定的白模／站位拆到不同任务跨阶段推进。分层批次仍是同一场景内的制作顺序，不是拆角色并行的授权。不同场景仅在来源、工作PSD、输出和场景记录互相独立，共享角色母版只读且无未冻结共同依赖时，允许准备、生图等待或离线审核重叠；实际PS始终使用同一全局队列。

1. **Whole-scene rehearsal.** Resolve authority, runtime branch and actual cast; translate the beat into visible relationships; establish support/depth and rough scale. Use available candidates for a clearly provisional whole-scene preview before polishing anyone. Read it without dialogue: intended activity, natural support, distinct body language and credible interaction must be visible. Until Codex's own pre-generation checks pass, the preview is diagnostic only; this is not a user approval checkpoint.
2. **Layered production.** Plan far-to-near batches with complete independent actors. Review empty-scene depth and anatomical 3D whiteboxes, including isolated masters and the same-layer combined view, then pass the pre-generation ledger. Generate identities in original-scene context. Preserve approved actor pixels during extraction where verified tools permit; register layers and solve minimal soft-response regions together with human contacts. Return each changed actor to the whole shot before fine polish.
3. **Whole-scene acceptance.** Inspect narrative relationships and natural acting first, then scene scale/support, soft contact, occlusion, selected real UI, identity/style, edges and shadows. Repair affected components and dependencies only. Technical reports collect evidence; they cannot author artistic PASS.
4. **Package once.** After visual acceptance and post-generation validation, generate reconstruction, XY/layer manifest and source hashes from frozen outputs. Copies reuse valid review under the cadence rules while destination paths/hashes/reconstruction are checked. Work evidence stays out of formal folders.

## Invariants

- Resolve `exploration-click-pair` versus `pure-narrative` from configuration, dialogue and approved requirements. Use chronological simultaneous-cast snapshots. Preserve uninterrupted presences across entrances; do not anticipate a future actor or claim entry through a visibly closed door.
- Select the actual left or right dialogue UI after blocking and test that mask only. Faces and critical hands/props remain readable; genuine transparent padding is not obstruction.
- A ground-region hit proves coverage only. Author support/depth from the scene independently of actors. Shared provisional perspective assumptions cannot certify each other. Review local furniture and a different depth band; resolve uncertainty that changes placement before fine measurements.
- Before whitebox approval use `validate-scene-absolute-scale` with three independent fixed-object groups spanning horizontal/vertical and local/cross-depth evidence, then `validate-cast-scale` v2 with `headScalePriority: true`. Approximately 80% head/body consistency means both `maxHeadDeviationRatio` and `maxPairwiseHeadDeviationRatio` are `0.20`, not 0.40. It does not relax scene scale, anatomy or contact. Measure tilted/lying heads along the reviewed anatomical axis rather than a rotated vertical box.
- Pair the depth image with complete anatomical 3D whiteboxes using stable distinct matte colors. Never use stick/joint/block figures or the 170cm technical ruler as pose-generation authority. Review visible body structure, support and action silhouette; tiny unresolved gaze/expression differences transfer to the formal character stage.
- Complete masters and occluded snapshots use the same layers/transforms. Inspect hidden feet and anatomy in the complete master, then restore exact-source occlusion and judge final support. Never relocate hidden feet just to pass a calculation.
- Treat head/neck/shoulders plus pillow, pelvis plus cushion, or body plus bedding as coupled contact. Retain the full actor master and a separate minimum soft-response layer; recheck both when their relation changes. An unchanged empty pillow is not evidence of a newly loaded pillow. Fixed furniture/architecture remains exact source at scale 1.
- Natural acting is distinct from correct intent. Check support–pelvis–torso continuity, appropriate relaxation and believable hands/rest positions. Quiet does not require rigidity; natural does not require every actor to twist, stagger, gesture or hold a new prop. Coordinates document a viable pose, not force one.

## Review and retry control

Follow the operation boundaries in [production-cadence.md](references/production-cadence.md). Each accepted image state needs actual whole-`100%` and applicable local-`200%`/original-pixel inspection bound to paths and SHA-256. Record `ndc-stage-visual-self-check/v1` with explicit findings and `PASS`, `FAIL` or `NOT_CHECKED`. Missing coverage, stale hashes or failed/unchecked applicable criteria block downstream acceptance. Validate with `D:/Codex/NDC/scripts/validate-ndc-stage-visual-self-check.py --record <record> --artifact <output>` at accepted image milestones. Internal commands and manifest writes are not separate art stages.

Retain ledger coverage for `exact-pose-whitebox`, `contextual-local-result`, `matte-extraction`, `pre-composite-registration` and `final-full-composite`. They identify genuinely reviewed outputs/scopes inside the milestones. Share real inspection evidence where applicable; never invent an unexecuted stage or write PASS over a new hash. Changed pixels, context, requirements or user rejection invalidate affected evidence.

Before another generation, use [ps-first-repair.md](references/ps-first-repair.md) to select a bounded repair from existing pixels when feasible. Whiteboxes have at most three generated attempts and three MCP repair/review rounds per declared batch; PS may start after the first useful candidate, without consuming all model attempts. Formal production follows the shared model-call ceiling in the cadence reference, including generative extraction. Track whole-scene cost/time and separate model/PS counts. Folders, stage names and resumptions never reset budgets; a user-explicit independent production test has its own counts under the cadence reference. Exhaustion leaves a candidate and does not lower quality requirements.

## Completion

Require current visual/semantic acceptance, actual UI, independent complete layers, coupled contact, source-preserving occlusion, scene/head scale, identity/style/texture, shadows, original-resolution RGBA and 100% XY reconstruction. Run final conformance and the post-generation ledger. Archive passed outputs within the authorized task without another routine approval stop; distinguish formal results from unresolved candidates. During a user pause, perform only the requested analysis or Skill maintenance.
